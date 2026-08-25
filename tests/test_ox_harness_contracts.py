#!/usr/bin/env python3
"""Deterministic, no-cost contract tests for the Ox Alpha execution harness."""

from __future__ import annotations

import importlib.util
import json
import os
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / ".ox" / "runner" / "ox_runner.py"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "ox-worker.yml"

spec = importlib.util.spec_from_file_location("ox_runner_under_test", RUNNER_PATH)
ox = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(ox)


class FakeResponse:
    def __init__(self, status_code, payload=None, text="", headers=None):
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.headers = headers or {}

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


def base_config():
    return {
        "model": "stealth/ox-alpha",
        "reasoning": {"effort": "high"},
        "openrouter": {
            "base_url": "https://openrouter.ai/api/v1",
            "max_attempts": 4,
            "request_timeout_seconds": 30,
            "backoff_base_seconds": 1,
            "backoff_max_seconds": 8,
        },
    }


def test_retry_policy():
    cfg = base_config()["openrouter"]
    with mock.patch.object(ox.random, "uniform", return_value=0):
        assert ox.retry_delay(cfg, 1) == 1
        assert ox.retry_delay(cfg, 2) == 2
        assert ox.retry_delay(cfg, 4) == 8
    response = FakeResponse(429, headers={"Retry-After": "99"})
    assert ox.retry_delay(cfg, 1, response) == 8


def test_retryable_then_success():
    responses = [
        FakeResponse(503, text="busy", headers={"Retry-After": "0"}),
        FakeResponse(
            200,
            payload={
                "choices": [{"message": {"content": "done"}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1},
                "provider": "test-provider",
            },
        ),
    ]
    sleeps = []
    with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "test"}), \
         mock.patch.object(ox.requests, "post", side_effect=responses), \
         mock.patch.object(ox.time, "sleep", side_effect=lambda s: sleeps.append(s)), \
         mock.patch.object(ox.random, "uniform", return_value=0):
        content, telemetry = ox.call_ox(base_config(), {}, "system", "user")
    assert content == "done"
    assert len(telemetry["attempts"]) == 2
    assert telemetry["attempts"][0]["status_code"] == 503
    assert telemetry["attempts"][1]["status_code"] == 200
    assert sleeps == [0.0]


def test_nonretryable_fails_once():
    with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "test"}), \
         mock.patch.object(ox.requests, "post", return_value=FakeResponse(401, text="bad auth")):
        try:
            ox.call_ox(base_config(), {}, "system", "user")
        except ox.OxCallError as exc:
            assert len(exc.telemetry["attempts"]) == 1
            assert exc.telemetry["attempts"][0]["status_code"] == 401
        else:
            raise AssertionError("401 must fail closed")


def test_context_hard_limits():
    worker = {
        "max_context_chars": 250000,
        "hard_max_context_chars": 600000,
    }
    assert ox.bounded_int({}, worker, "max_context_chars", 250000, "hard_max_context_chars") == 250000
    assert ox.bounded_int({"max_context_chars": 900000}, worker, "max_context_chars", 250000, "hard_max_context_chars") == 600000


def test_per_task_discovery_isolated():
    original = ox.TASKS_DIR
    with tempfile.TemporaryDirectory() as td:
        task_dir = Path(td)
        ox.TASKS_DIR = task_dir
        try:
            (task_dir / "a.json").write_text(json.dumps({"id": "a", "status": "PENDING"}), encoding="utf-8")
            (task_dir / "b.json").write_text(json.dumps({"id": "b", "status": "PENDING"}), encoding="utf-8")
            assert [t[1]["id"] for t in ox.load_pending_tasks("a")] == ["a"]
            assert {t[1]["id"] for t in ox.load_pending_tasks()} == {"a", "b"}
        finally:
            ox.TASKS_DIR = original


def test_workflow_parallelism_and_single_writer_contract():
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "max-parallel: 3" in text
    assert 'python .ox/runner/ox_runner.py --task-id "${{ matrix.task_id }}"' in text
    assert "Upload isolated task result" in text
    assert "Download all worker results" in text
    assert "Commit Ox task/report state once" in text
    worker_section = text.split("  worker:", 1)[1].split("  aggregate:", 1)[0]
    assert "git push" not in worker_section
    aggregate_section = text.split("  aggregate:", 1)[1]
    assert aggregate_section.count("git push") == 1


def main():
    tests = [
        test_retry_policy,
        test_retryable_then_success,
        test_nonretryable_fails_once,
        test_context_hard_limits,
        test_per_task_discovery_isolated,
        test_workflow_parallelism_and_single_writer_contract,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"Ox harness contract suite: PASS ({len(tests)} tests)")


if __name__ == "__main__":
    main()
