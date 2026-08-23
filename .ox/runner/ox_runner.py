import fnmatch
import json
import os
import re
import shutil
import subprocess
import tempfile
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


def load_config():
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def load_pending_tasks():
    pending = []
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    for path in sorted(TASKS_DIR.glob("*.json")):
        task = json.loads(path.read_text(encoding="utf-8"))
        if task.get("status") == "PENDING":
            pending.append((path, task))

    return pending


def run_git(args, cwd=None, check=True):
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({result.returncode}): "
            f"{result.stderr[-3000:]}"
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
    return dest, {
        "repository": repository,
        "ref": commit,
        "source": clone_url,
    }


def is_text_file(path: Path):
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in TEXT_FILENAMES


def rel_path(path: Path, root: Path):
    return path.relative_to(root).as_posix()


def matches_any(path_str: str, patterns):
    if not patterns:
        return False
    p = Path(path_str)
    return any(
        fnmatch.fnmatch(path_str, pattern) or p.match(pattern)
        for pattern in patterns
    )


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
    files = []
    for line in result.stdout.splitlines():
        path = repo_root / line
        if path.is_file():
            files.append(path)
    return files


def discover_focus_paths(repo_root: Path, focus_terms):
    found = set()
    for term in focus_terms:
        term = str(term).strip()
        if not term:
            continue
        result = run_git(
            ["grep", "-Iil", "-e", term, "--"],
            cwd=repo_root,
            check=False,
        )
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

    if len(raw) > max_file_bytes:
        raw = raw[:max_file_bytes]
        truncated = True
    else:
        truncated = False

    if b"\x00" in raw:
        return None

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw.decode("utf-8", errors="replace")
        except Exception:
            return None

    if truncated:
        text += "\n\n[FILE TRUNCATED BY OX CONTEXT PACKAGER]\n"
    return text


def score_candidate(path: Path, repo_root: Path, focus_terms, focus_paths):
    rel = rel_path(path, repo_root)
    rel_lower = rel.lower()
    name_lower = path.name.lower()
    score = 0

    if path.resolve() in focus_paths:
        score += 100

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

    depth = len(path.relative_to(repo_root).parts)
    score += max(0, 8 - depth)

    return score


def add_neighbor_files(selected, all_allowed, repo_root, max_neighbors=20):
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


def collect_repo_context(repo_root: Path, task: dict, config: dict):
    worker_cfg = config.get("worker", {})
    max_files = int(task.get("max_files", worker_cfg.get("max_files", 60)))
    max_file_bytes = int(
        task.get("max_file_bytes", worker_cfg.get("max_file_bytes", 150000))
    )
    max_context_chars = int(
        task.get("max_context_chars", worker_cfg.get("max_context_chars", 600000))
    )

    include_paths = task.get("include_paths", [])
    exclude_paths = task.get("exclude_paths", [])
    focus_terms = task.get("focus_terms", [])

    tracked = tracked_files(repo_root)
    allowed = [
        p for p in tracked
        if allowed_path(p, repo_root, include_paths, exclude_paths)
    ]

    focus_paths = discover_focus_paths(repo_root, focus_terms) if focus_terms else set()
    focus_paths = {
        p for p in focus_paths
        if p.exists() and allowed_path(p, repo_root, include_paths, exclude_paths)
    }

    ranked = sorted(
        allowed,
        key=lambda p: (
            -score_candidate(p, repo_root, focus_terms, focus_paths),
            rel_path(p, repo_root),
        ),
    )

    seed_limit = max(1, min(max_files, max_files - min(20, max_files // 4)))
    selected = ranked[:seed_limit]
    selected = add_neighbor_files(
        selected,
        allowed,
        repo_root,
        max_neighbors=max(0, max_files - len(selected)),
    )[:max_files]

    sections = []
    included = []
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
                section = section[:remaining] + "\n[CONTEXT BUDGET TRUNCATED]\n"
                sections.append(section)
                included.append(rel)
            break

        sections.append(section)
        included.append(rel)
        chars_used += len(section)

    inventory = build_inventory(repo_root, allowed)

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

    return inventory, "".join(sections), metadata


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

Clearly distinguish:

- DIRECT EVIDENCE
- INFERENCE
- RECOMMENDATION
- UNKNOWN / NEEDS MORE SOURCE

If the supplied bounded context is insufficient for a claim, say so explicitly and identify the exact additional paths/symbols that should be fetched in a follow-up task. Do not pretend to have read files that were not supplied.
"""


def call_ox(config, system_prompt, user_prompt):
    api_key = os.environ["OPENROUTER_API_KEY"]
    url = config["openrouter"]["base_url"].rstrip("/") + "/chat/completions"

    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "reasoning_effort": config.get("reasoning", {}).get("effort", "max"),
        "temperature": 1,
    }

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=900,
    )

    if not response.ok:
        raise RuntimeError(
            f"OpenRouter request failed ({response.status_code}): {response.text[:3000]}"
        )

    data = response.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(
            f"Unexpected OpenRouter response shape: {json.dumps(data)[:4000]}"
        ) from exc

    if not content:
        raise RuntimeError("Ox Alpha returned an empty response.")

    return content


def process_task(task_path: Path, task: dict, config: dict, system_prompt: str):
    print(f"Running {task['id']} ({task.get('repository', 'current')})")

    with tempfile.TemporaryDirectory(prefix="ox-worker-") as temp_dir:
        repo_root, repo_info = prepare_repository(task, Path(temp_dir))
        inventory, repo_context, context_meta = collect_repo_context(
            repo_root, task, config
        )

        print(
            "Context package: "
            f"{context_meta['included_file_count']} files, "
            f"{context_meta['context_chars']} chars, "
            f"{context_meta['focus_match_count']} focus matches"
        )

        prompt = build_prompt(
            task,
            repo_info,
            inventory,
            repo_context,
            context_meta,
        )
        result = call_ox(config, system_prompt, prompt)

    output_path = ROOT / task["output"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")

    task["status"] = "COMPLETE"
    task["inspected_repository"] = repo_info
    task["context_package"] = context_meta
    task_path.write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")

    print(f"Completed {task['id']} -> {output_path}")


def main():
    config = load_config()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    pending = load_pending_tasks()
    if not pending:
        print("No pending Ox tasks.")
        return

    system_prompt = (OX_DIR / "OX_SYSTEM_PROMPT.md").read_text(encoding="utf-8")

    for task_path, task in pending:
        try:
            process_task(task_path, task, config, system_prompt)
        except Exception as exc:
            task["status"] = "FAILED"
            task["error"] = str(exc)[:4000]
            task_path.write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")
            raise


if __name__ == "__main__":
    main()
