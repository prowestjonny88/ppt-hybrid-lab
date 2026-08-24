#!/usr/bin/env python3
"""Fail closed if Stage 4 drifts back to slide-specific compiler recipes."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ir.runtime import load_json
from src.visual_ir.archetype_solvers import SOLVER_REGISTRY
from src.visual_ir.compiler import compile_slide

VISUAL_IR_DIR = ROOT / "experiment/queuezero/visual_ir"
CURRENT = [
    VISUAL_IR_DIR / "problem_hook.stage4.v0.json",
    VISUAL_IR_DIR / "how_it_works.stage4.v0.json",
    VISUAL_IR_DIR / "validation_traction.stage4.v0.json",
]


def main():
    solver_source = (ROOT / "src/visual_ir/archetype_solvers.py").read_text(encoding="utf-8")
    compiler_source = (ROOT / "src/visual_ir/compiler.py").read_text(encoding="utf-8")

    # The reusable solver module may bind semantic roles and groups, but it must
    # not select behavior by benchmark slide ID.
    for slide_id in ("problem-hook", "how-it-works", "validation-traction"):
        if slide_id in solver_source:
            raise SystemExit(f"archetype solver leaked benchmark slide id {slide_id!r}")
        if f'if slide_id == "{slide_id}"' in compiler_source:
            raise SystemExit(f"compiler regressed to slide-id dispatch for {slide_id!r}")

    seen = set()
    for path in CURRENT:
        ir = load_json(path)
        key = (ir["composition"]["archetype_id"], ir["composition"]["variant"])
        if key not in SOLVER_REGISTRY:
            raise SystemExit(f"missing solver registration for {key}")
        solution = compile_slide(ROOT, path)
        if solution.get("solver") is None:
            raise SystemExit(f"compiled solution missing solver trace for {path.name}")
        if not solution.get("placements"):
            raise SystemExit(f"solver produced no semantic placements for {path.name}")
        seen.add(key)

    if len(seen) != 3:
        raise SystemExit(f"expected three distinct Stage 4 solver variants, got {seen}")

    print("Stage 4 archetype solver registry: PASS")


if __name__ == "__main__":
    main()
