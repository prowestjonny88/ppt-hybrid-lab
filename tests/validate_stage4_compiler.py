#!/usr/bin/env python3
"""Compile every frozen QueueZero semantic slide through Stage 4 Visual IR.

This gate proves that deck planning is no longer a single-slide fixture: every
planned slide must resolve into deterministic normalized geometry without
renderer-specific coordinates leaking back into Visual IR.
"""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.visual_ir.compiler import compile_slide


def main():
    plan = json.loads((ROOT / "experiment/queuezero/stage4_deck_plan.v0.json").read_text(encoding="utf-8"))
    failures = []
    compiled = []
    for entry in plan["slides"]:
        path = ROOT / entry["visual_ir"]
        try:
            solution = compile_slide(ROOT, path)
        except Exception as exc:
            failures.append(f"{entry['slide_id']}: compile failed: {exc}")
            continue
        if solution["slide_id"] != entry["slide_id"]:
            failures.append(f"{entry['slide_id']}: compiled slide_id mismatch")
        if not solution.get("placements"):
            failures.append(f"{entry['slide_id']}: no placements")
        for placement in solution.get("placements", []):
            box = placement.get("box")
            if not isinstance(box, list) or len(box) != 4:
                failures.append(f"{entry['slide_id']}: invalid box for {placement.get('semantic_object_id')}")
                continue
            x, y, w, h = box
            if min(x, y, w, h) < 0 or x + w > 1.000001 or y + h > 1.000001:
                failures.append(f"{entry['slide_id']}: out-of-bounds placement {placement.get('semantic_object_id')}: {box}")
        compiled.append({
            "slide_id": solution["slide_id"],
            "archetype_id": solution["archetype_id"],
            "variant": solution["variant"],
            "placement_count": len(solution["placements"]),
            "decoration_count": len(solution["decorations"]),
        })

    print(json.dumps({"compiled": compiled, "failures": failures}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
