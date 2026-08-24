#!/usr/bin/env python3
"""Negative regressions for Stage 4 deck-level rhythm and adjacency rules."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
for candidate in (ROOT, TESTS_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from validate_stage4_deck_rhythm import evaluate_resolved_rhythm, load

PLAN_PATH = ROOT / "experiment/queuezero/stage4_deck_plan.v0.json"


def _baseline():
    plan = load(PLAN_PATH)
    resolved = []
    for item in sorted(plan["slides"], key=lambda x: x["position"]):
        resolved.append((deepcopy(item), load(ROOT / item["visual_ir"])))
    return plan["deck_rules"], resolved


def _must_reject(label, mutate, needle):
    rules, resolved = _baseline()
    mutate(resolved)
    errors = evaluate_resolved_rhythm(resolved, rules)
    if not errors:
        raise SystemExit(f"deck-rhythm panic accepted invalid case: {label}")
    if not any(needle in error for error in errors):
        raise SystemExit(
            f"deck-rhythm panic wrong failure for {label}: expected {needle!r}; got {errors}"
        )
    print(f"PASS {label}: rejected -> {needle}")


def main():
    rules, baseline = _baseline()
    baseline_errors = evaluate_resolved_rhythm(baseline, rules)
    if baseline_errors:
        raise SystemExit(f"deck-rhythm panic fixture is not green: {baseline_errors}")

    def repeat_archetype(resolved):
        resolved[1][1]["composition"]["archetype_id"] = resolved[0][1]["composition"]["archetype_id"]

    _must_reject("adjacent_archetype_repeat", repeat_archetype, "repeated beyond adjacency budget")

    def repeat_variation(resolved):
        resolved[1][1]["style"]["variation_tags"] = deepcopy(
            resolved[0][1]["style"]["variation_tags"]
        )

    _must_reject("adjacent_variation_repeat", repeat_variation, "adjacent variation signature repeats")

    def repeat_anchor_three(resolved):
        for _, ir in resolved:
            ir.setdefault("deck_rhythm", {})["hero_anchor_preference"] = "same_edge"

    _must_reject("protagonist_anchor_streak", repeat_anchor_three, "repeated too many slides")

    def adjacent_dark_fields(resolved):
        refs = resolved[1][1].setdefault("style", {}).setdefault("identity_anchor_refs", [])
        if "dark_proof_field" not in refs:
            refs.append("dark_proof_field")
        refs = resolved[2][1].setdefault("style", {}).setdefault("identity_anchor_refs", [])
        if "dark_proof_field" not in refs:
            refs.append("dark_proof_field")

    _must_reject("adjacent_major_dark_fields", adjacent_dark_fields, "major dark field repeats on adjacent slides")

    def self_avoided_archetype(resolved):
        current = resolved[1][1]["composition"]["archetype_id"]
        resolved[1][1].setdefault("deck_rhythm", {}).setdefault("avoid_archetypes", []).append(current)

    _must_reject("current_archetype_in_avoid_list", self_avoided_archetype, "appears in its avoid_archetypes")

    def wrong_previous_archetype(resolved):
        resolved[1][1].setdefault("deck_rhythm", {})["previous_archetype"] = "wrong_previous"

    _must_reject("previous_archetype_mismatch", wrong_previous_archetype, "does not match actual")

    print("Stage 4 deck-rhythm panic suite: PASS (6 fail-closed mutations)")


if __name__ == "__main__":
    main()
