import json
import os
from pathlib import Path

import requests
import yaml


ROOT = Path(__file__).resolve().parents[2]
OX_DIR = ROOT / ".ox"
TASKS_DIR = OX_DIR / "tasks"
REPORTS_DIR = OX_DIR / "reports"
CONFIG_PATH = OX_DIR / "config.yml"


def load_config():
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def load_pending_tasks():
    pending = []

    if not TASKS_DIR.exists():
        return pending

    for path in sorted(TASKS_DIR.glob("*.json")):
        task = json.loads(path.read_text(encoding="utf-8"))

        if task.get("status") == "PENDING":
            pending.append((path, task))

    return pending


def build_inventory():
    excluded = {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        "dist",
        "build",
    }

    files = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        if any(part in excluded for part in path.parts):
            continue

        files.append(str(path.relative_to(ROOT)))

    return "\n".join(sorted(files))


def build_prompt(task, inventory):
    questions = "\n".join(f"- {q}" for q in task.get("questions", []))
    expected = "\n".join(f"- {x}" for x in task.get("expected_output", []))

    return f"""
# DELEGATED TASK

Task ID: {task['id']}
Task type: {task['type']}

## Objective

{task['objective']}

## Questions

{questions}

## Expected output

{expected}

## Current repository inventory

{inventory}

## Evidence requirement

Return evidence-rich findings.

Clearly distinguish:

- DIRECT EVIDENCE
- INFERENCE
- RECOMMENDATION
- UNKNOWN
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
        timeout=600,
    )

    if not response.ok:
        raise RuntimeError(
            f"OpenRouter request failed ({response.status_code}): {response.text[:2000]}"
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


def main():
    config = load_config()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    pending = load_pending_tasks()

    if not pending:
        print("No pending Ox tasks.")
        return

    system_prompt_path = OX_DIR / "OX_SYSTEM_PROMPT.md"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    inventory = build_inventory()

    for task_path, task in pending:
        print(f"Running {task['id']}")
        prompt = build_prompt(task, inventory)
        result = call_ox(config, system_prompt, prompt)

        output_path = ROOT / task["output"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result, encoding="utf-8")

        task["status"] = "COMPLETE"
        task_path.write_text(
            json.dumps(task, indent=2) + "\n",
            encoding="utf-8",
        )

        print(f"Completed {task['id']} -> {output_path}")


if __name__ == "__main__":
    main()
