#!/usr/bin/env python3
"""Bounded-parallel, retrying orchestration wrapper for the proven Ox worker.

Keeps ox_runner.py's context packaging and report semantics intact while adding:
- per-task selection
- bounded parallel execution (hard capped at 3)
- local RUNNING claim/lease metadata
- transient OpenRouter retry/backoff
- per-task timing/token observability

GitHub workflow-level branch concurrency remains the cross-run duplicate-work guard.
Workers never push independently; the workflow performs one aggregate commit after
all workers finish.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

import ox_runner as base

RETRYABLE_HTTP = {408, 409, 425, 429, 500, 502, 503, 504}
STATE_LOCK = threading.Lock()
LOCAL = threading.local()


def now():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.isoformat().replace("+00:00", "Z")


def write_task(path: Path, task: dict):
    with STATE_LOCK:
        path.write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")


def select_pending(task_ids):
    pending = base.load_pending_tasks()
    if not task_ids:
        return pending
    wanted = set(task_ids)
    return [
        (path, task) for path, task in pending
        if task.get("id") in wanted or path.stem in wanted
    ]


def claim(path: Path, task: dict, config: dict):
    lease_minutes = int(task.get("lease_minutes", config.get("worker", {}).get("lease_minutes", 45)))
    started = now()
    task["status"] = "RUNNING"
    task["worker_claim"] = {
        "worker_id": f"{os.environ.get('GITHUB_RUN_ID', 'local')}:{threading.current_thread().name}",
        "started_at": iso(started),
        "lease_expires_at": iso(started + timedelta(minutes=lease_minutes)),
        "attempt": int(task.get("worker_claim", {}).get("attempt", 0)) + 1,
    }
    task.pop("error", None)
    write_task(path, task)


def delay_for(response, attempt, config):
    cfg = config.get("openrouter", {})
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return min(float(retry_after), float(cfg.get("backoff_max_seconds", 60)))
            except ValueError:
                pass
    base_delay = float(cfg.get("backoff_base_seconds", 5))
    cap = float(cfg.get("backoff_max_seconds", 60))
    return min(cap, base_delay * (2 ** max(0, attempt - 1))) + random.uniform(0, min(1.0, base_delay))


def retrying_call_ox(config, system_prompt, user_prompt):
    """Drop-in replacement for base.call_ox used by each worker thread."""
    task = getattr(LOCAL, "task", {})
    cfg = config.get("openrouter", {})
    api_key = os.environ["OPENROUTER_API_KEY"]
    url = cfg["base_url"].rstrip("/") + "/chat/completions"
    effort = task.get("reasoning_effort", config.get("reasoning", {}).get("effort", "high"))
    timeout = int(task.get("request_timeout_seconds", cfg.get("request_timeout_seconds", 900)))
    max_attempts = int(task.get("max_attempts", cfg.get("max_attempts", 4)))
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "reasoning_effort": effort,
        "temperature": 1,
    }

    started = time.monotonic()
    last_error = None
    for attempt in range(1, max_attempts + 1):
        response = None
        try:
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=timeout,
            )
            if response.ok:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content")
                if not content:
                    raise RuntimeError("Ox Alpha returned an empty response")
                usage = data.get("usage", {})
                LOCAL.request_meta = {
                    "reasoning_effort": effort,
                    "request_attempts": attempt,
                    "request_duration_seconds": round(time.monotonic() - started, 3),
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                }
                return content
            last_error = RuntimeError(
                f"OpenRouter request failed ({response.status_code}): {response.text[:1200]}"
            )
            if response.status_code not in RETRYABLE_HTTP:
                raise last_error
        except requests.RequestException as exc:
            last_error = exc

        if attempt >= max_attempts:
            break
        wait = delay_for(response, attempt, config)
        print(f"{task.get('id', 'task')}: transient request failure; retry {attempt + 1}/{max_attempts} in {wait:.1f}s")
        time.sleep(wait)

    raise RuntimeError(f"Ox request failed after {max_attempts} attempts: {last_error}")


def run_one(path: Path, task: dict, config: dict, system_prompt: str):
    started = now()
    claim(path, task, config)
    LOCAL.task = task
    LOCAL.request_meta = {}
    try:
        # base.process_task expects PENDING only at discovery time, not here; it
        # operates on the supplied task directly and preserves our claim fields.
        base.process_task(path, task, config, system_prompt)
        completed = json.loads(path.read_text(encoding="utf-8"))
        completed["observability"] = {
            **getattr(LOCAL, "request_meta", {}),
            "wall_duration_seconds": round((now() - started).total_seconds(), 3),
            "completed_at": iso(now()),
        }
        write_task(path, completed)
        return True
    except Exception as exc:
        failed = task.copy()
        failed["status"] = "FAILED"
        failed["error"] = str(exc)[:4000]
        failed["observability"] = {
            **getattr(LOCAL, "request_meta", {}),
            "wall_duration_seconds": round((now() - started).total_seconds(), 3),
            "failed_at": iso(now()),
        }
        write_task(path, failed)
        print(f"FAILED {task.get('id')}: {exc}")
        return False
    finally:
        LOCAL.task = None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", action="append", default=[], help="Run only this task id; repeatable")
    parser.add_argument("--max-parallel", type=int, default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    config = base.load_config()
    base.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    base.TASKS_DIR.mkdir(parents=True, exist_ok=True)
    pending = select_pending(args.task)
    if not pending:
        print("No pending Ox tasks.")
        return

    system_prompt = (base.OX_DIR / "OX_SYSTEM_PROMPT.md").read_text(encoding="utf-8")
    configured = int(config.get("worker", {}).get("max_parallel", 3))
    requested = args.max_parallel if args.max_parallel is not None else configured
    max_parallel = max(1, min(3, requested, len(pending)))
    print(f"Ox batch: {len(pending)} pending; bounded parallelism={max_parallel}")

    # Monkeypatch only the model-call boundary; all proven context packaging and
    # report-writing behavior stays in the base worker.
    base.call_ox = retrying_call_ox

    results = []
    with ThreadPoolExecutor(max_workers=max_parallel, thread_name_prefix="ox") as pool:
        futures = {
            pool.submit(run_one, path, task, config, system_prompt): task.get("id")
            for path, task in pending
        }
        for future in as_completed(futures):
            results.append(bool(future.result()))

    if not all(results):
        raise SystemExit("One or more Ox tasks failed; aggregate task state is ready for the workflow commit step")


if __name__ == "__main__":
    main()
