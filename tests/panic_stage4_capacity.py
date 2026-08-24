#!/usr/bin/env python3
"""Fail-closed regression cases for Stage 4 archetype capacity preflight."""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ir.runtime import load_json
from src.visual_ir.capacity import load_archetypes, require_capacity

VISUAL_IR_PATH = ROOT / "experiment/queuezero/visual_ir/problem_hook.stage4.v0.json"
SEMANTICS_PATH = ROOT / "experiment/queuezero/slide_semantics/problem_hook.v1.json"


def _expect_runtime_error(ir: dict, semantics: dict, expected_fragment: str) -> None:
    try:
        require_capacity(ROOT, ir, semantics)
    except RuntimeError as exc:
        if expected_fragment not in str(exc):
            raise SystemExit(
                f"wrong fail-closed error: expected {expected_fragment!r}, got {str(exc)!r}"
            ) from exc
    else:
        raise SystemExit(f"capacity preflight unexpectedly accepted invalid case: {expected_fragment}")


def main() -> None:
    base_ir = load_json(VISUAL_IR_PATH)
    semantics = load_json(SEMANTICS_PATH)

    # Baseline must stay green or these negative tests are meaningless.
    require_capacity(ROOT, base_ir, semantics)

    unknown_archetype = deepcopy(base_ir)
    unknown_archetype["composition"]["archetype_id"] = "does-not-exist"
    _expect_runtime_error(unknown_archetype, semantics, "unknown archetype")

    missing_primary_budget = deepcopy(base_ir)
    missing_primary_budget["composition"]["content_capacity"].pop("max_primary_items", None)
    _expect_runtime_error(missing_primary_budget, semantics, "missing declared capacity max_primary_items")

    ceiling_overclaim = deepcopy(base_ir)
    archetypes = load_archetypes(ROOT)
    ceiling = archetypes[base_ir["composition"]["archetype_id"]]["capacity"]["max_primary_items"]
    ceiling_overclaim["composition"]["content_capacity"]["max_primary_items"] = ceiling + 1
    _expect_runtime_error(ceiling_overclaim, semantics, "exceeds archetype ceiling")

    no_hero = deepcopy(base_ir)
    protagonist = no_hero["hierarchy"]["protagonist"]
    no_hero["hierarchy"]["roles"][protagonist] = "primary_support"
    _expect_runtime_error(no_hero, semantics, "requires exactly one hero")

    too_many_primary = deepcopy(base_ir)
    # Promote an existing secondary support object to primary while tightening the
    # declared slide budget below the actual count. This verifies actual-vs-declared
    # enforcement independently of the registry ceiling check above.
    secondary_ids = [
        object_id for object_id, role in too_many_primary["hierarchy"]["roles"].items()
        if role == "secondary_support"
    ]
    if not secondary_ids:
        raise SystemExit("capacity panic fixture requires at least one secondary support object")
    too_many_primary["hierarchy"]["roles"][secondary_ids[0]] = "primary_support"
    too_many_primary["composition"]["content_capacity"]["max_primary_items"] = 1
    _expect_runtime_error(too_many_primary, semantics, "exceeds slide budget max_primary_items")

    print("Stage 4 capacity panic suite: PASS")


if __name__ == "__main__":
    main()
