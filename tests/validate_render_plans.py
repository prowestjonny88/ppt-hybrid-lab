#!/usr/bin/env python3
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN_DIR = ROOT / "experiment" / "queuezero" / "render_plans"
REGISTRY = ROOT / "architecture" / "CAPABILITY_REGISTRY.stage3.json"
EXPECTED_VARIANTS = {"image_first", "native_vector", "hybrid"}


def canonical_hash(data):
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_lane(plan, obj):
    override = plan.get("routing", {}).get("object_overrides", {}).get(obj["object_id"])
    if isinstance(override, str):
        return override
    if isinstance(override, dict):
        return override.get("lane")
    defaults = plan.get("routing", {}).get("role_defaults", {})
    return defaults.get(obj.get("role"), defaults.get("*"))


def main():
    registry = load(REGISTRY)
    hard = registry["hard_constraints"]
    plans = sorted(PLAN_DIR.glob("*.json"))
    if not plans:
        print("No render plans", file=sys.stderr)
        return 2

    by_slide = defaultdict(list)
    errors = []

    for path in plans:
        plan = load(path)
        by_slide[plan.get("slide_id")].append((path, plan))

    for slide_id, entries in sorted(by_slide.items()):
        variants = {plan.get("variant") for _, plan in entries}
        if variants != EXPECTED_VARIANTS:
            errors.append(f"{slide_id}: expected variants {sorted(EXPECTED_VARIANTS)}, got {sorted(variants)}")
            continue

        semantic_files = {plan.get("semantic_file") for _, plan in entries}
        if len(semantic_files) != 1:
            errors.append(f"{slide_id}: variants point to different semantic files: {semantic_files}")
            continue
        semantic_rel = next(iter(semantic_files))
        semantic_path = ROOT / semantic_rel
        if not semantic_path.exists():
            errors.append(f"{slide_id}: semantic file missing: {semantic_rel}")
            continue
        semantics = load(semantic_path)
        sem_hash = canonical_hash(semantics)
        print(f"SEMANTIC {slide_id} sha256={sem_hash}")

        for path, plan in entries:
            variant = plan["variant"]
            declared = plan.get("semantic_hash")
            if declared not in (None, sem_hash):
                errors.append(f"{path.name}: semantic_hash does not match invariant semantics")
            if variant != "image_first" and plan.get("full_slide_rasterization_allowed") is not False:
                errors.append(f"{path.name}: structured variant must forbid full-slide rasterization")
            if variant == "image_first":
                if plan.get("mode") != "full_slide_image" or plan.get("full_slide_rasterization_allowed") is not True:
                    errors.append(f"{path.name}: image-first baseline contract invalid")
                continue

            for obj in semantics.get("semantic_objects", []):
                lane = resolve_lane(plan, obj)
                priority = obj.get("editability_priority")
                if lane is None:
                    errors.append(f"{path.name}: no routing decision for {obj['object_id']} ({obj.get('role')})")
                    continue
                if priority == "must_remain_editable" and lane not in hard["must_remain_editable_text"]:
                    errors.append(f"{path.name}: {obj['object_id']} must remain editable but routes to {lane}")
                if priority == "replaceable_asset" and lane not in hard["replaceable_asset"]:
                    errors.append(f"{path.name}: {obj['object_id']} replaceable asset routes to illegal lane {lane}")
                if lane == "image" and priority == "must_remain_editable":
                    errors.append(f"{path.name}: editable object {obj['object_id']} cannot route to image")

        # Fairness invariant: same semantic hash is the value all manifests must consume.
        print(f"FAIRNESS {slide_id}: A/B/C share {semantic_rel} ({sem_hash})")

    if errors:
        print("\nRender-plan validation FAILED", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"All {len(plans)} Stage 3 render plans passed fairness/capability validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
