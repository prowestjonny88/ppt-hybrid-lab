#!/usr/bin/env python3
from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ir.runtime import load_json
from src.visual_ir.router import route_candidates


CASES = [
    "experiment/queuezero/slide_semantics/problem_hook.v1.json",
    "experiment/queuezero/slide_semantics/how_it_works.v1.json",
    "experiment/queuezero/slide_semantics/validation_traction.v1.json",
]


def _expect_failure(label, fn):
    try:
        fn()
    except RuntimeError:
        return
    raise SystemExit(f"routing panic failed closed contract: {label} unexpectedly succeeded")


def _route_or_no_candidates(payload):
    """Return a normal routing trace or an empty-candidate trace on fail-closed.

    Negative panic mutations are allowed to make *every* archetype ineligible.
    In that case route_candidates() correctly raises RuntimeError. The panic test
    should treat that as the strongest valid fail-closed outcome rather than as a
    test harness failure.
    """
    try:
        return route_candidates(ROOT, payload)
    except RuntimeError as exc:
        if "no deterministic archetype candidates" not in str(exc):
            raise
        return {"candidates": [], "fail_closed": True, "error": str(exc)}


def main():
    for rel in CASES:
        semantics = load_json(ROOT / rel)
        baseline = route_candidates(ROOT, semantics)
        if not baseline["candidates"]:
            raise SystemExit(f"{rel}: baseline unexpectedly has no candidates")

        unknown_role = deepcopy(semantics)
        unknown_role["page_role"] = "__unknown_stage4_role__"
        _expect_failure(
            f"{rel}: unknown page_role",
            lambda payload=unknown_role: route_candidates(ROOT, payload),
        )

    # A mechanism slide with all directional evidence removed must not retain the
    # process_story candidate merely because its page role sounds explanatory.
    how_it_works = load_json(ROOT / CASES[1])
    no_flow = deepcopy(how_it_works)
    no_flow["relationships"] = []
    for group in no_flow.get("groups", []):
        group["layout_hint"] = None
    trace = _route_or_no_candidates(no_flow)
    if "process_story" in trace["candidates"]:
        raise SystemExit("routing panic: process_story remained eligible without ordered-flow evidence")

    # Removing all metrics from validation semantics must eliminate metric-led
    # archetypes instead of guessing them from the validation page role. A total
    # no-candidate RuntimeError is also an acceptable (and stricter) outcome.
    validation = load_json(ROOT / CASES[2])
    no_metrics = deepcopy(validation)
    no_metrics["semantic_objects"] = [
        obj for obj in no_metrics.get("semantic_objects", []) if obj.get("role") != "metric"
    ]
    trace = _route_or_no_candidates(no_metrics)
    if "dominant_metric" in trace["candidates"]:
        raise SystemExit("routing panic: dominant_metric remained eligible with zero metrics")

    print("Stage 4 routing panic regressions: PASS")


if __name__ == "__main__":
    main()
