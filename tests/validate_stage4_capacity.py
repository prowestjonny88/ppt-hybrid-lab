#!/usr/bin/env python3
from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ir.runtime import load_json
from src.visual_ir.capacity import evaluate_capacity, load_archetypes

VISUAL_IR_DIR = ROOT / "experiment/queuezero/visual_ir"


def main():
    archetypes = load_archetypes(ROOT)
    paths = sorted(VISUAL_IR_DIR.glob("*.stage4.v0.json"))
    if not paths:
        raise SystemExit("no Stage 4 Visual IR files found")

    for path in paths:
        ir = load_json(path)
        semantics = load_json(ROOT / ir["semantic_file"])
        archetype = archetypes[ir["composition"]["archetype_id"]]
        trace = evaluate_capacity(ir, semantics, archetype)
        if not trace["passed"]:
            raise SystemExit(f"{path.name}: current capacity failed: {trace['errors']}")

        # Negative regression: lower the declared primary budget below actual
        # whenever this slide has primary body support. The preflight must reject.
        actual_primary = trace["actual"]["primary_items"]
        if actual_primary > 0:
            overstuffed = deepcopy(ir)
            overstuffed["composition"]["content_capacity"]["max_primary_items"] = actual_primary - 1
            negative = evaluate_capacity(overstuffed, semantics, archetype)
            if negative["passed"]:
                raise SystemExit(f"{path.name}: capacity preflight failed to reject undersized primary budget")

    print(f"Stage 4 archetype capacity: PASS ({len(paths)} current slides + negative regressions)")


if __name__ == "__main__":
    main()
