#!/usr/bin/env python3
"""Fail-closed validation for Stage 4 Visual IR drafts.

This validator intentionally checks architecture boundaries, not rendered beauty.
Pixel/multimodal visual QA remains a separate Stage 4 gate.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHETYPES_PATH = ROOT / "architecture/COMPOSITION_ARCHETYPES.stage4.v0.json"
STYLE_PATH = ROOT / "experiment/queuezero/style_profiles/queuezero_hackathon_v0.json"
VISUAL_IR_DIR = ROOT / "experiment/queuezero/visual_ir"

FORBIDDEN_GEOMETRY_KEYS = {
    "x", "y", "w", "h", "left", "top", "right", "bottom",
    "width", "height", "bbox", "rect", "bounds", "bounds_emu",
    "normalized_box", "coordinates", "emu"
}

ALLOWED_HIERARCHY_ROLES = {
    "hero", "primary_support", "secondary_support", "annotation", "source", "decorative_only"
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def walk_forbidden_geometry(value, path="$"):
    errors = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_GEOMETRY_KEYS:
                errors.append(f"renderer geometry leaked into Visual IR at {child_path}")
            errors.extend(walk_forbidden_geometry(child, child_path))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            errors.extend(walk_forbidden_geometry(child, f"{path}[{idx}]"))
    return errors


def index_by(items, key):
    return {item[key]: item for item in items}


def validate_one(path: Path, archetypes, style):
    ir = load(path)
    errors = []

    if ir.get("schema_version") != "visual-ir-v0":
        errors.append("schema_version must be visual-ir-v0")

    semantic_rel = ir.get("semantic_file")
    if not semantic_rel:
        errors.append("semantic_file is required")
        return errors
    semantic_path = ROOT / semantic_rel
    if not semantic_path.exists():
        errors.append(f"semantic_file does not exist: {semantic_rel}")
        return errors

    semantics = load(semantic_path)
    if ir.get("slide_id") != semantics.get("slide_id"):
        errors.append(f"slide_id mismatch: visual={ir.get('slide_id')} semantic={semantics.get('slide_id')}")

    semantic_objects = index_by(semantics.get("semantic_objects", []), "object_id")
    semantic_groups = index_by(semantics.get("groups", []), "group_id")
    semantic_ids = set(semantic_objects)
    semantic_group_ids = set(semantic_groups)

    # Keep Visual IR as visual reasoning, not a renderer-coordinate sidecar.
    errors.extend(walk_forbidden_geometry(ir))

    hierarchy = ir.get("hierarchy", {})
    roles = hierarchy.get("roles", {})
    unknown_role_objects = sorted(set(roles) - semantic_ids)
    if unknown_role_objects:
        errors.append(f"hierarchy.roles references unknown semantic objects: {unknown_role_objects}")

    invalid_roles = sorted({role for role in roles.values() if role not in ALLOWED_HIERARCHY_ROLES})
    if invalid_roles:
        errors.append(f"invalid hierarchy role values: {invalid_roles}")

    hero_objects = [object_id for object_id, role in roles.items() if role == "hero"]
    if len(hero_objects) != 1:
        errors.append(f"exactly one semantic object must have hierarchy role hero in V0; found {hero_objects}")

    protagonist = hierarchy.get("protagonist")
    if protagonist not in semantic_ids and protagonist not in semantic_group_ids:
        errors.append(f"hierarchy.protagonist must reference a semantic object/group; got {protagonist!r}")

    reading_order = ir.get("communication", {}).get("reading_order", [])
    unknown_reading = sorted(set(reading_order) - semantic_ids)
    if unknown_reading:
        errors.append(f"communication.reading_order references unknown semantic objects: {unknown_reading}")

    composition = ir.get("composition", {})
    archetype_id = composition.get("archetype_id")
    if archetype_id not in archetypes:
        errors.append(f"unknown composition archetype: {archetype_id}")
    else:
        archetype = archetypes[archetype_id]
        density = composition.get("content_capacity", {}).get("density")
        if density not in archetype.get("density_range", []):
            errors.append(f"density {density!r} not allowed by archetype {archetype_id}")
        cap = composition.get("content_capacity", {})
        reg_cap = archetype.get("capacity", {})
        for key in ("max_primary_items", "max_secondary_items"):
            if key in cap and key in reg_cap and cap[key] > reg_cap[key]:
                errors.append(f"{key}={cap[key]} exceeds {archetype_id} registry capacity {reg_cap[key]}")

    style_ref = ir.get("style", {}).get("profile_id")
    if style_ref != style.get("profile_id"):
        errors.append(f"unknown/mismatched style profile {style_ref!r}; expected {style.get('profile_id')!r}")

    compatible = set(style.get("archetype_compatibility", {}).get("preferred", [])) | set(
        style.get("archetype_compatibility", {}).get("supported", [])
    )
    if archetype_id and archetype_id not in compatible:
        errors.append(f"style profile does not declare archetype compatibility for {archetype_id}")

    anchor_ids = {item["anchor_id"] for item in style.get("identity_anchors", [])}
    requested_anchors = set(ir.get("style", {}).get("identity_anchor_refs", []))
    unknown_anchors = sorted(requested_anchors - anchor_ids)
    if unknown_anchors:
        errors.append(f"unknown style identity anchors: {unknown_anchors}")

    shape_vocab = set(style.get("geometry", {}).get("shape_vocabulary", []))
    requested_shapes = set(ir.get("style", {}).get("shape_vocabulary", []))
    unknown_shapes = sorted(requested_shapes - shape_vocab)
    if unknown_shapes:
        errors.append(f"unknown style shape vocabulary items: {unknown_shapes}")

    spatial = ir.get("spatial_grammar", {})
    zones = spatial.get("zones", [])
    zone_ids = [zone.get("zone_id") for zone in zones]
    if None in zone_ids or len(zone_ids) != len(set(zone_ids)):
        errors.append("spatial_grammar zones must have unique non-null zone_id values")
    zone_id_set = set(zone_ids)
    seen_zone_objects = set()
    for zone in zones:
        relation_to = zone.get("relation_to")
        if relation_to is not None and relation_to not in zone_id_set:
            errors.append(f"zone {zone.get('zone_id')} relation_to unknown zone {relation_to}")
        for object_id in zone.get("contains", []):
            if object_id not in semantic_ids:
                errors.append(f"zone {zone.get('zone_id')} contains unknown semantic object {object_id}")
            if object_id in seen_zone_objects:
                errors.append(f"semantic object {object_id} assigned to multiple primary spatial zones")
            seen_zone_objects.add(object_id)

    visual_groups = ir.get("groups", [])
    visual_group_ids = set()
    for group in visual_groups:
        group_id = group.get("group_id")
        if not group_id or group_id in visual_group_ids:
            errors.append(f"visual groups require unique group_id; bad id {group_id!r}")
        visual_group_ids.add(group_id)
        unknown_members = sorted(set(group.get("members", [])) - semantic_ids)
        if unknown_members:
            errors.append(f"visual group {group_id} contains unknown semantic objects: {unknown_members}")
        unknown_internal = sorted(set(group.get("internal_hierarchy", [])) - set(group.get("members", [])))
        if unknown_internal:
            errors.append(f"visual group {group_id} internal_hierarchy has non-members: {unknown_internal}")

    for treatment in ir.get("asset_treatments", []):
        object_id = treatment.get("semantic_object_id")
        if object_id not in semantic_ids:
            errors.append(f"asset_treatment references unknown semantic object {object_id}")
        elif semantic_objects[object_id].get("editability_priority") != "replaceable_asset":
            errors.append(f"asset_treatment object {object_id} is not marked replaceable_asset in semantic IR")

    density = ir.get("density", {})
    if density.get("class") != composition.get("content_capacity", {}).get("density"):
        errors.append("density.class must match composition.content_capacity.density")
    if "shrink_all_text" not in density.get("forbidden_overflow_policy", []):
        errors.append("V0 requires shrink_all_text to be explicitly forbidden as an overflow policy")

    hard_fail = set(ir.get("qa_contract", {}).get("hard_fail", []))
    for required in ("semantic_leakage", "title_collision", "unreadable_primary_text"):
        if required not in hard_fail:
            errors.append(f"qa_contract.hard_fail must include {required}")

    targets = ir.get("qa_contract", {}).get("visual_targets", {})
    for key in ("first_impression_min", "hierarchy_min", "composition_min", "presentability_min"):
        if targets.get(key, 0) < 4:
            errors.append(f"visual target {key} must be >= 4")
    if targets.get("overall_mean_min", 0) < 4.0:
        errors.append("visual target overall_mean_min must be >= 4.0")

    return errors


def main():
    registry = load(ARCHETYPES_PATH)
    archetypes = index_by(registry.get("archetypes", []), "archetype_id")
    style = load(STYLE_PATH)

    paths = sorted(VISUAL_IR_DIR.glob("*.stage4.v0.json"))
    if not paths:
        print("FAIL: no Stage 4 Visual IR files found", file=sys.stderr)
        raise SystemExit(1)

    failures = 0
    for path in paths:
        errors = validate_one(path, archetypes, style)
        if errors:
            failures += 1
            print(f"FAIL {path.relative_to(ROOT)}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path.relative_to(ROOT)}")

    if failures:
        print(f"Visual IR validation failed for {failures}/{len(paths)} files", file=sys.stderr)
        raise SystemExit(1)

    print(f"Visual IR validation passed: {len(paths)} slides, {len(archetypes)} archetypes, style={style['profile_id']}")


if __name__ == "__main__":
    main()
