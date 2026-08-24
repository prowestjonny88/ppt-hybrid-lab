#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.visual_ir.compiler import compile_slide
from src.visual_ir.sample_renderer import new_presentation, render_layout_slide

VISUAL_IR = [
    "experiment/queuezero/visual_ir/problem_hook.stage4.v0.json",
    "experiment/queuezero/visual_ir/how_it_works.stage4.v0.json",
    "experiment/queuezero/visual_ir/validation_traction.stage4.v0.json",
]


def main():
    prs = new_presentation()
    realizations = []
    solutions = []
    for rel in VISUAL_IR:
        solution = compile_slide(ROOT, ROOT / rel)
        solutions.append(solution)
        realizations.append(render_layout_slide(ROOT, prs, solution))

    out_dir = ROOT / "dist/stage4/deck"
    out_dir.mkdir(parents=True, exist_ok=True)
    pptx = out_dir / "queuezero_stage4_v0.pptx"
    prs.save(pptx)
    (out_dir / "layout_solutions.json").write_text(json.dumps(solutions, indent=2) + "\n", encoding="utf-8")
    (out_dir / "realizations.json").write_text(json.dumps({
        "schema_version": "stage4-deck-realization-v0",
        "pptx": str(pptx.relative_to(ROOT)),
        "slide_count": len(realizations),
        "slides": realizations,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Built {pptx}")
    print(f"Slides: {len(realizations)}")


if __name__ == "__main__":
    main()
