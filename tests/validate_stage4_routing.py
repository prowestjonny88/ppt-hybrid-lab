#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ir.runtime import load_json
from src.visual_ir.router import route_candidates

CASES = [
    (
        "experiment/queuezero/slide_semantics/problem_hook.v1.json",
        {"editorial_hero", "dominant_metric"},
        "editorial_hero",
    ),
    (
        "experiment/queuezero/slide_semantics/how_it_works.v1.json",
        {"process_story", "product_stage"},
        "process_story",
    ),
    (
        "experiment/queuezero/slide_semantics/validation_traction.v1.json",
        {"dominant_metric", "evidence_constellation"},
        "dominant_metric",
    ),
]


def main():
    for rel, expected_subset, selected in CASES:
        semantics = load_json(ROOT / rel)
        trace = route_candidates(ROOT, semantics)
        candidates = set(trace["candidates"])
        missing = expected_subset - candidates
        if missing:
            raise SystemExit(f"{rel}: routing missing expected candidates {sorted(missing)}; got {sorted(candidates)}")
        if selected not in candidates:
            raise SystemExit(f"{rel}: selected benchmark archetype {selected!r} not eligible")
    print("Stage 4 deterministic archetype routing: PASS")


if __name__ == "__main__":
    main()
