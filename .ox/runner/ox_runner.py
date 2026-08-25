import argparse
import fnmatch
import json
import os
import random
import re
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml


ROOT = Path(__file__).resolve().parents[2]
OX_DIR = ROOT / ".ox"
TASKS_DIR = OX_DIR / "tasks"
REPORTS_DIR = OX_DIR / "reports"
CONFIG_PATH = OX_DIR / "config.yml"

TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".json", ".yaml", ".yml", ".toml", ".md", ".txt",
    ".html", ".css", ".scss", ".xml", ".svg", ".sh",
}

TEXT_FILENAMES = {
    "README", "README.md", "SKILL.md", "AGENTS.md", "CLAUDE.md",
    "Dockerfile", "Makefile", "package.json", "pyproject.toml",
    "requirements.txt", "setup.py", "setup.cfg", "tsconfig.json",
}

EXCLUDED_PARTS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache", "dist", "build", "coverage",
    ".next", "target", "vendor",
}

REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
RETRYABLE_HTTP = {408, 409, 425, 429, 500, 502, 503, 504}


class OxCallError(RuntimeError):
    def __init__(self, message, telemetry=None):
        super().__init__(message)
        self.telemetry = telemetry or {}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_config():
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def load_pending_tasks(task_id=None):
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    paths = [TASKS_DIR / f"{task_id}.json"] if task_id else sorted(TASKS_DIR.glob("*.json"))
    pending = []
    for path in paths:
        if not path.is_file():
            continue
        task = json.loads(path.read_text(encoding="utf-8"))
        if task.get("status") == "PENDING":
            pending.append((path, task))
    return pending


def run_git(args, cwd=None, check=True):
    result = subprocess.run(
        ["git", *args], cwd=cwd, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({result.returncode}): {result.stderr[-3000:]}"
        )
    return result


def prepare_repository(task, temp_root: Path):
    repository = task.get("repository", "current")
    if repository == "current":
        return ROOT, {
            "repository": "current",
            "ref": run_git(["rev-parse", "HEAD"], cwd=ROOT).stdout.strip(),
            "source": "current checkout",
        }

    if not REPO_RE.fullmatch(repository):
        raise ValueError(
            "repository must be 'current' or GitHub owner/repo form; "
            f"got {repository!r}"
        )

    dest = temp_root / "reference"
    clone_url = f"https://github.com/{repository}.git"
    ref = task.get("ref")
    clone_args = ["clone", "--depth", "1"]
    if ref:
        clone_args.extend(["--branch", str(ref)])
    clone_args.extend([clone_url, str(dest)])
    run_git(clone_args)

    commit = run_git(["rev-parse", "HEAD"], cwd=dest).stdout.strip()
    return dest, {"repository": repository, "ref": commit, "source": clone_url}


def is_text_file(path: Path):
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in TEXT_FILENAMES


def rel_path(path: Path, root: Path):
    return path.relative_to(root).as_posix()


def matches_any(path_str: str, patterns):
    if not patterns:
        return False
    p = Path(path_str)
    return any(fnmatch.fnmatch(path_str, pattern) or p.match(pattern) for pattern in patterns)


def allowed_path(path: Path, root: Path, include_paths, exclude_paths):
    rel = rel_path(path, root)
    if any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts):
        return False
    if exclude_paths and matches_any(rel, exclude_paths):
        return False
    if include_paths and not matches_any(rel, include_paths):
        return False
    return is_text_file(path)


def tracked_files(repo_root: Path):
    result = run_git(["ls-files"], cwd=repo_root)
    return [repo_root / line for line in result.stdout.splitlines() if (repo_root / line).is_file()]


def discover_focus_paths(repo_root: Path, focus_terms):
    found = set()
    for term in focus_terms:
        term = str(term).strip()
        if not term:
            continue
        result = run_git(["grep", "-Iil", "-e", term, "--"], cwd=repo_root, check=False)
        if result.returncode not in (0, 1):
            continue
        for line in result.stdout.splitlines():
            candidate = repo_root / line.strip()
            if candidate.is_file():
                found.add(candidate.resolve())
    return found


def build_inventory(repo_root: Path, files):
    return "\n".join(sorted(rel_path(p, repo_root) for p in files))


def read_text_limited(path: Path, max_file_bytes: int):
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    truncated = len(raw) > max_file_bytes
    if truncated:
        raw = raw[:max_file_bytes]
    if b"\x00" in raw:
        return None
    text = raw.decode("utf-8", errors="replace")
    if truncated:
        text += "\n\n[FILE TRUNCATED BY OX CONTEXT PACKAGER]\n"
    return text


def score_candidate(path: Path, repo_root: Path, focus_terms, focus_paths):
    rel = rel_path(path, repo_root)
    rel_lower = rel.lower()
    name_lower = path.name.lower()
    score = 100 if path.resolve() in focus_paths else 0
    for term in focus_terms:
        term_lower = str(term).lower().strip()
        if term_lower and term_lower in rel_lower:
            score += 25
    if path.name in TEXT_FILENAMES:
        score += 20
    if "test" in rel_lower or "spec" in rel_lower:
        score += 12
    if any(token in name_lower for token in ("schema", "render", "convert", "svg", "ppt", "ooxml", "drawing")):
        score += 15
    score += max(0, 8 - len(path.relative_to(repo_root).parts))
    return score


def add_neighbor_files(selected, all_allowed, max_neighbors=20):
    selected_set = {p.resolve() for p in selected}
    directories = []
    for path in selected[:20]:
        parent = path.parent.resolve()
        if parent not in directories:
            directories.append(parent)
    neighbors = []
    for candidate in all_allowed:
        if candidate.resolve() in selected_set:
            continue
        if candidate.parent.resolve() in directories:
            neighbors.append(candidate)
        if len(neighbors) >= max_neighbors:
            break
    return selected + neighbors


def bounded_int(task, worker_cfg, key, default, hard_key):
    requested = int(task.get(key, worker_cfg.get(key, default)))
    hard_limit = int(worker_cfg.get(hard_key, requested))
    if requested < 1:
        raise ValueError(f"{key} must be positive")
    return min(requested, hard_limit)


def collect_repo_context(repo_root: Path, task: dict, config: dict):
    worker_cfg = config.get("worker", {})
    max_files = bounded_int(task, worker_cfg, "max_files", 40, "hard_max_files")
    max_file_bytes = bounded_int(task, worker_cfg, "max_file_bytes", 120000, "hard_max_file_bytes")
    max_context_chars = bounded_int(task, worker_cfg, "max_context_chars", 250000, "hard_max_context_chars")

    include_paths = task.get("include_paths", [])
    exclude_paths = task.get("exclude_paths", [])
    focus_terms = task.get("focus_terms", [])

    tracked = tracked_files(repo_root)
    allowed = [p for p in tracked if allowed_path(p, repo_root, include_paths, exclude_paths)]
    focus_paths = discover_focus_paths(repo_root, focus_terms) if focus_terms else set()
    focus_paths = {
        p for p in focus_paths
        if p.exists() and allowed_path(p, repo_root, include_paths, exclude_paths)
    }

    ranked = sorted(
        allowed,
        key=lambda p: (-score_candidate(p, repo_root, focus_terms, focus_paths), rel_path(p, repo_root)),
    )
    seed_limit = max(1, min(max_files, max_files - min(20, max_files // 4)))
    selected = add_neighbor_files(
        ranked[:seed_limit], allowed, max_neighbors=max(0, max_files - seed_limit)
    )[:max_files]

    sections, included = [], []
    chars_used = 0
    for path in selected:
        content = read_text_limited(path, max_file_bytes)
        if content is None:
            continue
        rel = rel_path(path, repo_root)
        section = f"\n\n===== FILE: {rel} =====\n\n{content}"
        if chars_used + len(section) > max_context_chars:
            remaining = max_context_chars - chars_used
            if remaining > 1000:
                sections.append(section[:remaining] + "\n[CONTEXT BUDGET TRUNCATED]\n")
                included.append(rel)
            break
        sections.append(section)
        included.append(rel)
        chars_used += len(section)

    metadata = {
        "tracked_file_count": len(tracked),
        "eligible_text_file_count": len(allowed),
        "focus_match_count": len(focus_paths),
        "included_file_count": len(included),
        "included_files": included,
        "context_chars": min(max_context_chars, sum(len(s) for s in sections)),
        "max_files": max_files,
        "max_file_bytes": max_file_bytes,
        "max_context_chars": max_context_chars,
    }
    return build_inventory(repo_root, allowed), "".join(sections), metadata


def build_prompt(task, repo_info, inventory, repo_context, context_meta):
    questions = "\n".join(f"- {q}" for q in task.get("questions", []))
    expected = "\n".join(f"- {x}" for x in task.get("expected_output", []))
    return f"""
# DELEGATED TASK

Task ID: {task['id']}
Task type: {task['type']}
Repository: {repo_info['repository']}
Commit/ref inspected: {repo_info['ref']}

## Objective

{task['objective']}

## Questions

{questions}

## Expected output

{expected}

## Context-packaging metadata

{json.dumps(context_meta, indent=2)}

## Eligible repository inventory

{inventory}

## Actual repository source supplied below

{repo_context}

## Evidence requirement

Base important findings on the supplied source. Cite concrete file paths and symbols/functions/classes where visible.
Clearly distinguish DIRECT EVIDENCE, INFERENCE, RECOMMENDATION, and UNKNOWN / NEEDS MORE SOURCE.
If the supplied bounded context is insufficient for a claim, say so explicitly and identify the exact additional paths/symbols that should be fetched in a follow-up task. Do not pretend to have read files that were not supplied.
"""


def retry_delay(openrouter_cfg, attempt, response=None):
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return min(float(retry_after), float(openrouter_cfg.get("backoff_max_seconds", 60)))
            except ValueError:
                pass
    base = float(openrouter_cfg.get("backoff_base_seconds", 5))
    cap = float(openrouter_cfg.get("backoff_max_seconds", 60))
    return min(cap, base * (2 ** max(0, attempt - 1))) + random.uniform(0, 1.0)


def call_ox(config, task, system_prompt, user_prompt):
    api_key = os.environ["OPENROUTER_API_KEY"]
    openrouter_cfg = config.get("openrouter", {})
    url = openrouter_cfg["base_url"].rstrip("/") + "/chat/completions"
    effort = task.get("reasoning_effort", config.get("reasoning", {}).get("effort", "high"))
    max_attempts = int(task.get("max_attempts", openrouter_cfg.get("max_attempts", 4)))
    timeout = int(task.get("request_timeout_seconds", openrouter_cfg.get("request_timeout_seconds", 900)))

    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "reasoning_effort": effort,
        "temperature": task.get("temperature", 1),
    }

    attempts = []
    for attempt in range(1, max_attempts + 1):
        started = time.monotonic()
        response = None
        try:
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=timeout,
            )
            elapsed = round(time.monotonic() - started, 3)
            attempts.append({
                "attempt": attempt,
                "status_code": response.status_code,
                "elapsed_seconds": elapsed,
                "retry_after": response.headers.get("Retry-After"),
            })
        except requests.RequestException as exc:
            elapsed = round(time.monotonic() - started, 3)
            attempts.append({
                "attempt": attempt,
                "transport_error": type(exc).__name__,
                "message": str(exc)[:1000],
                "elapsed_seconds": elapsed,
            })
            if attempt >= max_attempts:
                raise OxCallError(f"OpenRouter transport failure after {attempt} attempts: {exc}", {
                    "model": config["model"], "reasoning_effort": effort, "attempts": attempts,
                }) from exc
            time.sleep(retry_delay(openrouter_cfg, attempt))
            continue

        if response.ok:
            try:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
            except (ValueError, KeyError, IndexError, TypeError) as exc:
                raise OxCallError(
                    f"Unexpected OpenRouter response shape: {response.text[:4000]}",
                    {"model": config["model"], "reasoning_effort": effort, "attempts": attempts},
                ) from exc
            if not content:
                raise OxCallError(
                    "Ox Alpha returned an empty response.",
                    {"model": config["model"], "reasoning_effort": effort, "attempts": attempts},
                )
            return content, {
                "model": config["model"],
                "reasoning_effort": effort,
                "attempts": attempts,
                "usage": data.get("usage"),
                "provider": data.get("provider"),
            }

        retryable = response.status_code in RETRYABLE_HTTP
        if not retryable or attempt >= max_attempts:
            raise OxCallError(
                f"OpenRouter request failed ({response.status_code}): {response.text[:3000]}",
                {"model": config["model"], "reasoning_effort": effort, "attempts": attempts},
            )
        time.sleep(retry_delay(openrouter_cfg, attempt, response))

    raise OxCallError("OpenRouter request exhausted retries", {"attempts": attempts})


def metrics_path_for(task_id):
    return REPORTS_DIR / f"{task_id}.metrics.json"


def write_metrics(task_id, payload):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics_path = metrics_path_for(task_id)
    metrics_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return metrics_path


def process_task(task_path: Path, task: dict, config: dict, system_prompt: str):
    task_started = time.monotonic()
    print(f"Running {task['id']} ({task.get('repository', 'current')})")
    task["status"] = "RUNNING"
    task["started_at"] = utc_now()
    task_path.write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="ox-worker-") as temp_dir:
        package_started = time.monotonic()
        repo_root, repo_info = prepare_repository(task, Path(temp_dir))
        inventory, repo_context, context_meta = collect_repo_context(repo_root, task, config)
        package_seconds = round(time.monotonic() - package_started, 3)

        print(
            "Context package: "
            f"{context_meta['included_file_count']} files, "
            f"{context_meta['context_chars']} chars, "
            f"{context_meta['focus_match_count']} focus matches"
        )
        prompt = build_prompt(task, repo_info, inventory, repo_context, context_meta)
        result, call_meta = call_ox(config, task, system_prompt, prompt)

    output_path = ROOT / task["output"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")

    task["status"] = "COMPLETE"
    task["completed_at"] = utc_now()
    task["inspected_repository"] = repo_info
    task["context_package"] = context_meta
    task["execution"] = {
        "metrics_path": metrics_path_for(task["id"]).relative_to(ROOT).as_posix(),
        "reasoning_effort": call_meta.get("reasoning_effort"),
        "attempt_count": len(call_meta.get("attempts", [])),
    }
    task_path.write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")

    write_metrics(task["id"], {
        "schema_version": "ox-execution-metrics-v1",
        "task_id": task["id"],
        "status": "COMPLETE",
        "generated_at": utc_now(),
        "context_package": context_meta,
        "context_packaging_seconds": package_seconds,
        "call": call_meta,
        "total_seconds": round(time.monotonic() - task_started, 3),
    })
    print(f"Completed {task['id']} -> {output_path}")


def mark_failed(task_path, task, exc, task_started):
    call_meta = exc.telemetry if isinstance(exc, OxCallError) else {}
    task["status"] = "FAILED"
    task["completed_at"] = utc_now()
    task["error"] = str(exc)[:4000]
    task["execution"] = {
        "metrics_path": metrics_path_for(task["id"]).relative_to(ROOT).as_posix(),
        "attempt_count": len(call_meta.get("attempts", [])),
    }
    task_path.write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")
    write_metrics(task["id"], {
        "schema_version": "ox-execution-metrics-v1",
        "task_id": task["id"],
        "status": "FAILED",
        "generated_at": utc_now(),
        "error_type": type(exc).__name__,
        "error": str(exc)[:4000],
        "call": call_meta,
        "total_seconds": round(time.monotonic() - task_started, 3),
    })


def parse_args():
    parser = argparse.ArgumentParser(description="Run bounded Ox Alpha delegated tasks")
    parser.add_argument("--task-id", help="Run exactly one PENDING task by id, e.g. task-009")
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    pending = load_pending_tasks(args.task_id)
    if not pending:
        print(f"No pending Ox tasks{f' for {args.task_id}' if args.task_id else ''}.")
        return

    if args.task_id and len(pending) != 1:
        raise RuntimeError(f"expected one pending task for {args.task_id}; got {len(pending)}")

    system_prompt = (OX_DIR / "OX_SYSTEM_PROMPT.md").read_text(encoding="utf-8")
    failures = []
    for task_path, task in pending:
        started = time.monotonic()
        try:
            process_task(task_path, task, config, system_prompt)
        except Exception as exc:
            mark_failed(task_path, task, exc, started)
            failures.append((task["id"], exc))
            if args.task_id:
                break

    if failures:
        summary = "; ".join(f"{task_id}: {exc}" for task_id, exc in failures)
        raise RuntimeError(f"Ox task failures: {summary}")


if __name__ == "__main__":
    main()
