#!/usr/bin/env python3
"""Machine-enforced Stage 4 composition capacity contracts."""

from __future__ import annotations

from pathlib import Path

from src.ir.runtime import load_json

ARCHETYPES_PATH = "architecture/COMPOSITION_ARCHETYPES.stage4.v0.json"

# These objects are present on the slide but do not consume the body-item capacity
# budget. They have separate typography/topology constraints and pixel QA.
BODY_CAPACITY_EXCLUDED_SEMANTIC_ROLES = {
    "title",
    "subtitle",
    "source_note",
    "connector",
}


def load_archetypes(root: Path):
    data = load_json(Path(root) / ARCHETYPES_PATH)
    return {item["archetype_id"]: item for item in data.get("archetypes", [])}


def evaluate_capacity(ir: dict, semantics: dict, archetype: dict):
    objects = {item["object_id"]: item for item in semantics.get("semantic_objects", [])}
    roles = ir.get("hierarchy", {}).get("roles", {})

    body_roles = {}
    for object_id, visual_role in roles.items():
        semantic_role = objects.get(object_id, {}).get("role")
        if semantic_role in BODY_CAPACITY_EXCLUDED_SEMANTIC_ROLES:
            continue
        body_roles[object_id] = visual_role

    actual = {
        "hero_items": sum(role == "hero" for role in body_roles.values()),
        "primary_items": sum(role == "primary_support" for role in body_roles.values()),
        "secondary_items": sum(role == "secondary_support" for role in body_roles.values()),
    }
    actual["total_visible_groups"] = (
        actual["hero_items"] + actual["primary_items"] + actual["secondary_items"]
    )

    slide_budget = ir.get("composition", {}).get("content_capacity", {})
    registry_budget = archetype.get("capacity", {})
    errors = []

    if actual["hero_items"] != 1:
        errors.append(f"body capacity requires exactly one hero; actual={actual['hero_items']}")

    comparisons = [
        ("primary_items", "max_primary_items"),
        ("secondary_items", "max_secondary_items"),
    ]
    for actual_key, budget_key in comparisons:
        declared = slide_budget.get(budget_key)
        ceiling = registry_budget.get(budget_key)
        if declared is None:
            errors.append(f"Visual IR missing declared capacity {budget_key}")
            continue
        if ceiling is None:
            errors.append(f"archetype missing registry capacity {budget_key}")
            continue
        if actual[actual_key] > declared:
            errors.append(
                f"actual {actual_key}={actual[actual_key]} exceeds slide budget {budget_key}={declared}"
            )
        if declared > ceiling:
            errors.append(
                f"slide budget {budget_key}={declared} exceeds archetype ceiling {ceiling}"
            )

    total_ceiling = registry_budget.get("max_total_visible_groups")
    if total_ceiling is not None and actual["total_visible_groups"] > total_ceiling:
        errors.append(
            f"actual total_visible_groups={actual['total_visible_groups']} exceeds archetype ceiling {total_ceiling}"
        )

    return {
        "actual": actual,
        "slide_budget": slide_budget,
        "archetype_ceiling": registry_budget,
        "excluded_semantic_roles": sorted(BODY_CAPACITY_EXCLUDED_SEMANTIC_ROLES),
        "errors": errors,
        "passed": not errors,
    }


def require_capacity(root: Path, ir: dict, semantics: dict):
    archetypes = load_archetypes(root)
    archetype_id = ir.get("composition", {}).get("archetype_id")
    archetype = archetypes.get(archetype_id)
    if archetype is None:
        raise RuntimeError(f"unknown archetype {archetype_id!r} during capacity preflight")
    trace = evaluate_capacity(ir, semantics, archetype)
    if not trace["passed"]:
        raise RuntimeError(
            f"capacity preflight failed for {ir.get('slide_id')}: " + "; ".join(trace["errors"])
        )
    return trace
