#!/usr/bin/env python3
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMANTICS_DIR = ROOT / "experiment" / "queuezero" / "slide_semantics"
BINDING_RE = re.compile(r"\{([A-Za-z0-9_-]+)\.display_value\}")
FORBIDDEN_SEMANTIC_KEYS = {"allowed_render_lanes", "preferred_render_lane", "render_lane"}


def canonical_hash(data):
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def fail(errors, message):
    errors.append(message)


def walk_values(value, path=""):
    if isinstance(value, dict):
        for k, v in value.items():
            p = f"{path}.{k}" if path else k
            yield p, v
            yield from walk_values(v, p)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            p = f"{path}[{i}]"
            yield p, v
            yield from walk_values(v, p)


def validate_ref(ref, objects, groups, evidence, errors, path):
    if ref is None:
        return
    if not isinstance(ref, dict):
        fail(errors, f"{path}: ref must be an object")
        return
    typ, rid = ref.get("ref_type"), ref.get("id")
    if typ == "object" and rid not in objects:
        fail(errors, f"{path}: unknown object ref {rid!r}")
    elif typ == "group" and rid not in groups:
        fail(errors, f"{path}: unknown group ref {rid!r}")
    elif typ == "evidence" and rid not in evidence:
        fail(errors, f"{path}: unknown evidence ref {rid!r}")
    elif typ not in {"object", "group", "evidence"}:
        fail(errors, f"{path}: invalid ref_type {typ!r}")


def validate_file(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = []

    if data.get("schema_version") != "stage3-slide-semantics-v1":
        fail(errors, "schema_version must be stage3-slide-semantics-v1")
    for forbidden in ("render_plan", "realization"):
        if forbidden in data:
            fail(errors, f"top-level {forbidden} leaks renderer/runtime state into semantics")

    evidence_items = data.get("evidence", [])
    object_items = data.get("semantic_objects", [])
    group_items = data.get("groups", [])
    relationship_items = data.get("relationships", [])
    region_items = data.get("regions", [])
    asset_items = data.get("assets", [])

    def unique(items, key, label):
        seen = set()
        for idx, item in enumerate(items):
            ident = item.get(key)
            if not ident:
                fail(errors, f"{label}[{idx}] missing {key}")
            elif ident in seen:
                fail(errors, f"duplicate {label} id {ident!r}")
            seen.add(ident)
        return seen

    evidence = unique(evidence_items, "evidence_id", "evidence")
    objects = unique(object_items, "object_id", "semantic_objects")
    groups = unique(group_items, "group_id", "groups")
    relationships = unique(relationship_items, "relationship_id", "relationships")
    regions = unique(region_items, "region_id", "regions")
    assets = unique(asset_items, "asset_id", "assets")

    # Semantic layer must not contain renderer preferences.
    for p, value in walk_values(object_items, "semantic_objects"):
        if p.rsplit(".", 1)[-1] in FORBIDDEN_SEMANTIC_KEYS:
            fail(errors, f"{p}: renderer-lane field forbidden in semantic objects")

    # Evidence bindings and simple range contract.
    for idx, item in enumerate(evidence_items):
        val = item.get("value")
        if isinstance(val, dict):
            if set(val) != {"min", "max"} or val["min"] > val["max"]:
                fail(errors, f"evidence[{idx}].value invalid range")
        for ref in item.get("derivation", {}).get("input_evidence_refs", []):
            if ref not in evidence:
                fail(errors, f"evidence[{idx}].derivation unknown evidence {ref!r}")
        for key in ("supersedes",):
            ref = item.get(key)
            if ref is not None and ref not in evidence:
                fail(errors, f"evidence[{idx}].{key} unknown evidence {ref!r}")
        for ref in item.get("conflicts_with", []):
            if ref not in evidence:
                fail(errors, f"evidence[{idx}].conflicts_with unknown evidence {ref!r}")

    # Resolve all template bindings anywhere in the semantic document.
    for p, value in walk_values(data):
        if isinstance(value, str):
            for match in BINDING_RE.finditer(value):
                if match.group(1) not in evidence:
                    fail(errors, f"{p}: binding references unknown evidence {match.group(1)!r}")

    # Detect high-risk duplicated mutable display literals in slide prose.
    mutable_fields = [
        ("governing_claim", data.get("governing_claim")),
        ("subtitle_support", data.get("subtitle_support")),
        ("why_it_matters", data.get("why_it_matters")),
    ]
    for obj in object_items:
        mutable_fields.append((f"object:{obj.get('object_id')}:content", obj.get("content")))
        mutable_fields.append((f"object:{obj.get('object_id')}:content_template", obj.get("content_template")))
    for ev in evidence_items:
        display = ev.get("display_value")
        if not isinstance(display, str) or len(display) < 3:
            continue
        token = "{" + ev["evidence_id"] + ".display_value}"
        for field_name, text in mutable_fields:
            if isinstance(text, str) and display in text and token not in text:
                fail(errors, f"{field_name}: literal mutable evidence {display!r}; use {token}")

    for idx, obj in enumerate(object_items):
        cref = obj.get("content_ref")
        if cref is not None and cref not in evidence:
            fail(errors, f"semantic_objects[{idx}].content_ref unknown evidence {cref!r}")
        region = obj.get("region_ref")
        if region is not None and region not in regions:
            fail(errors, f"semantic_objects[{idx}].region_ref unknown region {region!r}")

    for idx, group in enumerate(group_items):
        members = group.get("member_ids", [])
        if len(members) != len(set(members)):
            fail(errors, f"groups[{idx}] contains duplicate member_ids")
        for member in members:
            if member not in objects:
                fail(errors, f"groups[{idx}] unknown object member {member!r}")

    for idx, rel in enumerate(relationship_items):
        validate_ref(rel.get("from"), objects, groups, evidence, errors, f"relationships[{idx}].from")
        validate_ref(rel.get("to"), objects, groups, evidence, errors, f"relationships[{idx}].to")
        for ref in rel.get("evidence_refs", []):
            if ref not in evidence:
                fail(errors, f"relationships[{idx}].evidence_refs unknown evidence {ref!r}")

    proof = data.get("proof_object", {})
    for idx, ref in enumerate(proof.get("primary_refs", [])):
        validate_ref(ref, objects, groups, evidence, errors, f"proof_object.primary_refs[{idx}]")
    for rel_id in proof.get("required_relationships", []):
        if rel_id not in relationships:
            fail(errors, f"proof_object.required_relationships unknown relationship {rel_id!r}")

    for idx, guard in enumerate(data.get("forbidden_implications", [])):
        for j, ref in enumerate(guard.get("applies_to", [])):
            validate_ref(ref, objects, groups, evidence, errors, f"forbidden_implications[{idx}].applies_to[{j}]")

    for idx, ref in enumerate(data.get("must_keep_refs", [])):
        validate_ref(ref, objects, groups, evidence, errors, f"must_keep_refs[{idx}]")

    hierarchy = data.get("hierarchy", {})
    for key in ("highest_priority", "visual_protagonist", "bottom_synthesis"):
        validate_ref(hierarchy.get(key), objects, groups, evidence, errors, f"hierarchy.{key}")
    for key in ("primary_numbers", "secondary_numbers"):
        for idx, ref in enumerate(hierarchy.get(key, [])):
            validate_ref(ref, objects, groups, evidence, errors, f"hierarchy.{key}[{idx}]")

    for idx, region in enumerate(region_items):
        rect = region.get("rect", {})
        try:
            x, y, w, h = (float(rect[k]) for k in ("x", "y", "w", "h"))
            if min(x, y, w, h) < 0 or x + w > 1.000001 or y + h > 1.000001 or w <= 0 or h <= 0:
                fail(errors, f"regions[{idx}] rect out of normalized slide bounds: {rect}")
        except Exception:
            fail(errors, f"regions[{idx}] invalid rect: {rect}")

    if not any(r.get("purpose") == "insertion_zone" for r in region_items):
        fail(errors, "slide must declare an insertion_zone for panic-test sponsor/user additions")

    for idx, asset in enumerate(asset_items):
        object_id = asset.get("semantic_object_id")
        if object_id not in objects:
            fail(errors, f"assets[{idx}] unknown semantic_object_id {object_id!r}")
        region = asset.get("region_ref")
        if region not in regions:
            fail(errors, f"assets[{idx}] unknown region_ref {region!r}")
        if asset.get("kind") == "generated_visual" and asset.get("text_free") is not True:
            fail(errors, f"assets[{idx}] generated_visual must be text_free in Stage 3")
        if not isinstance(asset.get("current_instance"), dict):
            fail(errors, f"assets[{idx}] missing versioned current_instance")

    return data, errors


def main():
    paths = sorted(SEMANTICS_DIR.glob("*.v1.json"))
    if not paths:
        print("No v1 semantics files found", file=sys.stderr)
        return 2
    failures = 0
    for path in paths:
        data, errors = validate_file(path)
        rel = path.relative_to(ROOT)
        if errors:
            failures += 1
            print(f"FAIL {rel}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {rel} sha256={canonical_hash(data)}")
    if failures:
        print(f"{failures}/{len(paths)} semantics files failed", file=sys.stderr)
        return 1
    print(f"All {len(paths)} Stage 3 semantics files passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
