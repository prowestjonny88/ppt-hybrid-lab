#!/usr/bin/env python3
"""Negative regression suite for the Stage 4 Visual IR contract.

Each mutation starts from a known-good QueueZero Visual IR fixture and must be
rejected by the same validator used in CI. This protects the architecture
boundary from gradually becoming permissive as the compiler expands.
"""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.visual_ir.style_runtime import resolve_style_profile
from tests.validate_visual_ir import load, index_by, validate_one

ARCHETYPES_PATH = ROOT / "architecture/COMPOSITION_ARCHETYPES.stage4.v0.json"
STYLE_PATH = ROOT / "experiment/queuezero/style_profiles/queuezero_hackathon_v0.json"
BASE_IR_PATH = ROOT / "experiment/queuezero/visual_ir/problem_hook.stage4.v0.json"


def _validate_payload(payload: dict, archetypes: dict, style: dict) -> list[str]:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".stage4.v0.json", encoding="utf-8", delete=False
    ) as handle:
        json.dump(payload, handle)
        temp_path = Path(handle.name)
    try:
        return validate_one(temp_path, archetypes, style)
    finally:
        temp_path.unlink(missing_ok=True)


def _expect_reject(name: str, payload: dict, needle: str, archetypes: dict, style: dict):
    errors = _validate_payload(payload, archetypes, style)
    if not errors:
        raise SystemExit(f"PANIC FAIL {name}: invalid Visual IR was accepted")
    if not any(needle in error for error in errors):
        raise SystemExit(
            f"PANIC FAIL {name}: expected error containing {needle!r}; got {errors}"
        )
    print(f"PASS {name}: rejected -> {needle}")


def main():
    registry = load(ARCHETYPES_PATH)
    archetypes = index_by(registry.get("archetypes", []), "archetype_id")
    style, _, _ = resolve_style_profile(ROOT, STYLE_PATH)
    base = load(BASE_IR_PATH)

    cases = []

    p = copy.deepcopy(base)
    p["spatial_grammar"]["zones"][0]["x"] = 0.1
    cases.append(("coordinate_leakage", p, "renderer geometry leaked into Visual IR"))

    p = copy.deepcopy(base)
    p["hierarchy"]["roles"]["invented_object"] = "primary_support"
    cases.append(("unknown_semantic_role_object", p, "hierarchy.roles references unknown semantic objects"))

    p = copy.deepcopy(base)
    p["hierarchy"]["roles"]["title"] = "hero"
    cases.append(("multiple_heroes", p, "exactly one semantic object must have hierarchy role hero"))

    p = copy.deepcopy(base)
    p["composition"]["archetype_id"] = "totally_unknown_archetype"
    cases.append(("unknown_archetype", p, "unknown composition archetype"))

    p = copy.deepcopy(base)
    p["composition"]["content_capacity"]["density"] = "high"
    p["density"]["class"] = "high"
    cases.append(("archetype_density_violation", p, "density 'high' not allowed by archetype editorial_hero"))

    p = copy.deepcopy(base)
    p["style"]["identity_anchor_refs"].append("imaginary_anchor")
    cases.append(("unknown_identity_anchor", p, "unknown active identity anchors"))

    p = copy.deepcopy(base)
    existing = p["spatial_grammar"]["zones"][0]["contains"][0]
    p["spatial_grammar"]["zones"][1]["contains"].append(existing)
    cases.append(("duplicate_primary_zone_assignment", p, "assigned to multiple primary spatial zones"))

    p = copy.deepcopy(base)
    p["asset_treatments"][0]["semantic_object_id"] = "title"
    cases.append(("asset_treatment_nonreplaceable", p, "is not marked replaceable_asset in semantic IR"))

    p = copy.deepcopy(base)
    p["density"]["forbidden_overflow_policy"] = [
        item for item in p["density"]["forbidden_overflow_policy"] if item != "shrink_all_text"
    ]
    cases.append(("silent_global_text_shrink", p, "shrink_all_text to be explicitly forbidden"))

    p = copy.deepcopy(base)
    p["qa_contract"]["hard_fail"].remove("semantic_leakage")
    cases.append(("missing_semantic_leakage_hard_fail", p, "qa_contract.hard_fail must include semantic_leakage"))

    p = copy.deepcopy(base)
    p["qa_contract"]["visual_targets"]["hierarchy_min"] = 3
    cases.append(("weak_visual_acceptance_threshold", p, "visual target hierarchy_min must be >= 4"))

    for name, payload, needle in cases:
        _expect_reject(name, payload, needle, archetypes, style)

    print(f"Stage 4 Visual IR panic suite: PASS ({len(cases)} fail-closed mutations)")


if __name__ == "__main__":
    main()
