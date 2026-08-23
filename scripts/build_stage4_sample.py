#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.visual_ir.compiler import compile_validation_sample
from src.visual_ir.sample_renderer import render_compiled_sample


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--visual-ir",
        default="experiment/queuezero/visual_ir/validation_traction.stage4.v0.json",
    )
    parser.add_argument(
        "--layout-solution",
        default="dist/stage4/validation_traction.layout_solution.v0.json",
    )
    parser.add_argument(
        "--out",
        default="dist/stage4/validation_traction_sample_v0.pptx",
    )
    parser.add_argument(
        "--realization",
        default="dist/stage4/validation_traction.realization.v0.json",
    )
    args = parser.parse_args()

    visual_ir = ROOT / args.visual_ir
    solution = compile_validation_sample(ROOT, visual_ir)

    solution_path = ROOT / args.layout_solution
    solution_path.parent.mkdir(parents=True, exist_ok=True)
    solution_path.write_text(json.dumps(solution, indent=2) + "\n", encoding="utf-8")

    output, realization = render_compiled_sample(
        ROOT,
        solution,
        ROOT / args.out,
        ROOT / args.realization,
    )
    print(f"Built {output}")
    print(f"Layout solution: {solution_path}")
    print(f"Editable semantic parts: {len(realization['objects'])}")


if __name__ == "__main__":
    main()
