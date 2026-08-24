#!/usr/bin/env python3
"""Deterministic Stage 4 archetype eligibility router.

This layer runs before visual-director/model judgement. It derives conservative
semantic features and evaluates machine-readable routing predicates. Unknown or
unsupported features fail closed rather than widening the candidate set.
"""

from __future__ import annotations

from pathlib import Path

from src.ir.runtime import load_json

RULES_PATH = "architecture/ARCHETYPE_ROUTING_RULES.stage4.v0.json"


def derive_features(semantics: dict):
    objects = semantics.get("semantic_objects", [])
    relationships = semantics.get("relationships", [])
    groups = semantics.get("groups", [])

    role_count = {}
    for obj in objects:
        role = obj.get("role")
        role_count[role] = role_count.get(role, 0) + 1

    relationship_types = {rel.get("type") for rel in relationships}
    layout_hints = {group.get("layout_hint") for group in groups}

    # The fields below are intentionally conservative. Features that do not have
    # a reliable representation in the current Semantic IR stay at zero/false,
    # making archetypes that require them ineligible rather than guessed.
    return {
        "metric_count": role_count.get("metric", 0),
        "hero_visual_count": role_count.get("hero_visual_slot", 0),
        "image_slot_count": role_count.get("image_slot", 0) + role_count.get("hero_visual_slot", 0),
        "diagram_node_count": role_count.get("diagram_node", 0),
        "connector_count": role_count.get("connector", 0),
        "ask_object_count": role_count.get("ask", 0),
        "ordered_flow": bool(
            {"sequence", "data_flow"} & relationship_types
            or {"left_to_right_process", "timeline", "progression"} & layout_hints
        ),
        "ordered_stage_count": role_count.get("diagram_node", 0) if "sequence" in relationship_types else 0,
        "comparison_group_count": 0,
        "comparison_entity_count": 0,
        "semantic_axis_count": 0,
        "layer_group_count": sum(1 for group in groups if group.get("layout_hint") in {"layer_stack", "architecture_layers"}),
        "temporal_milestone_count": 0,
        "portfolio_module_count": 0,
    }


def _compare(actual, op, expected):
    if op == ">=":
        return actual >= expected
    if op == "<=":
        return actual <= expected
    if op == "==":
        return actual == expected
    if op == ">":
        return actual > expected
    if op == "<":
        return actual < expected
    raise RuntimeError(f"unsupported routing operator {op!r}")


def route_candidates(root: Path, semantics: dict):
    root = Path(root)
    spec = load_json(root / RULES_PATH)
    page_role = semantics.get("page_role")
    intents = set(spec.get("page_role_to_intents", {}).get(page_role, []))
    if not intents:
        raise RuntimeError(f"no deterministic intent mapping for page_role {page_role!r}")

    features = derive_features(semantics)
    candidates = []
    evaluations = {}

    for archetype_id, rule in spec.get("rules", {}).items():
        intent_ok = bool(intents & set(rule.get("intent_any", [])))
        checks = []
        for predicate in rule.get("all", []):
            feature = predicate["feature"]
            actual = features.get(feature)
            passed = actual is not None and _compare(actual, predicate["op"], predicate["value"])
            checks.append({**predicate, "actual": actual, "passed": passed})
        eligible = intent_ok and all(item["passed"] for item in checks)
        evaluations[archetype_id] = {
            "intent_ok": intent_ok,
            "predicate_checks": checks,
            "eligible": eligible,
        }
        if eligible:
            candidates.append(archetype_id)

    if not candidates:
        raise RuntimeError(
            f"no deterministic archetype candidates for page_role={page_role!r} features={features}"
        )

    return {
        "page_role": page_role,
        "intents": sorted(intents),
        "features": features,
        "candidates": candidates,
        "evaluations": evaluations,
    }
