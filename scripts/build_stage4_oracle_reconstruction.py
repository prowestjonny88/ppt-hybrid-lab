#!/usr/bin/env python3
"""Build the first oracle-derived editable reconstruction deck.

The full-slide Gemini outputs are never placed as slide backgrounds. The only
oracle-derived raster used here is a deterministic, text-free crop of the problem
slide's human hero region. All authoritative slide text remains native PowerPoint
text from frozen Semantic IR.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ir.runtime import load_json
from src.visual_ir.compiler import compile_slide_ir
from src.visual_ir.sample_renderer import new_presentation, render_layout_slide

GENERATION_ID = "gemini31flash-oracle-v1"
ORACLE_ROOT = ROOT / "benchmark" / "generated" / "queuezero" / GENERATION_ID
OUT = ROOT / "dist" / "stage4" / "oracle_reconstruction_v1"
ASSET_DIR = OUT / "assets"
DERIVED_IR_DIR = OUT / "visual_ir"
BINDINGS_REL = "dist/stage4/oracle_reconstruction_v1/asset_bindings.json"

BASE_IR = {
    "problem-hook": ROOT / "experiment/queuezero/visual_ir/problem_hook.stage4.v0.json",
    "how-it-works": ROOT / "experiment/queuezero/visual_ir/how_it_works.stage4.v0.json",
    "validation-traction": ROOT / "experiment/queuezero/visual_ir/validation_traction.stage4.v0.json",
}
VARIANTS = {
    "problem-hook": "oracle_dark_metric_scene_right",
    "how-it-works": "oracle_visual_system_left_copy_right",
    "validation-traction": "oracle_evidence_field_to_pilot",
}


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_problem_hero():
    src = ORACLE_ROOT / "problem-hook.jpg"
    if not src.is_file():
        raise RuntimeError(f"missing persisted visual oracle: {src}")
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    dst = ASSET_DIR / "problem_person_text_free_crop.jpg"
    with Image.open(src) as im:
        w, h = im.size
        # Text-free right-side human/scene region only. The full-slide oracle is
        # not used as a slide image and no raster typography is retained.
        crop = im.crop((int(w * 0.575), int(h * 0.080), int(w * 0.990), int(h * 0.910)))
        crop.save(dst, format="JPEG", quality=92, optimize=True)
    return src, dst


def derived_ir(slide_id: str):
    ir = copy.deepcopy(load_json(BASE_IR[slide_id]))
    ir["status"] = "oracle_reconstruction_v1_not_style_frozen"
    ir["composition"]["variant"] = VARIANTS[slide_id]
    ir["composition"]["selection_reason"] = (
        "Oracle-derived reconstruction variant: preserve frozen semantics while "
        "testing whether stronger composition reduces the visual-ceiling gap."
    )
    ir.setdefault("style", {})["oracle_generation_id"] = GENERATION_ID
    if slide_id == "problem-hook":
        ir["style"]["canvas_background_token"] = "dark_field"
    ir["oracle_reconstruction"] = {
        "visual_oracle_generation_id": GENERATION_ID,
        "semantic_authority": False,
        "full_slide_raster_forbidden": True,
        "variant": VARIANTS[slide_id],
    }
    return ir


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    DERIVED_IR_DIR.mkdir(parents=True, exist_ok=True)
    oracle_src, hero_crop = prepare_problem_hero()

    bindings = {
        "schema_version": "stage4-oracle-reconstruction-bindings-v1",
        "semantic_authority": False,
        "bindings": {
            "problem-hook": {
                "hero_visual_slot": str(hero_crop.relative_to(ROOT)),
            }
        },
        "derived_assets": [{
            "output": str(hero_crop.relative_to(ROOT)),
            "source_oracle": str(oracle_src.relative_to(ROOT)),
            "source_sha256": sha256(oracle_src),
            "output_sha256": sha256(hero_crop),
            "operation": "deterministic_text_free_crop",
            "crop_norm": [0.575, 0.080, 0.415, 0.830],
            "semantic_authority": False,
        }],
    }
    bindings_path = ROOT / BINDINGS_REL
    bindings_path.parent.mkdir(parents=True, exist_ok=True)
    bindings_path.write_text(json.dumps(bindings, indent=2) + "\n", encoding="utf-8")

    prs = new_presentation()
    solutions, realizations, derived_irs = [], [], []
    for slide_id in ("problem-hook", "how-it-works", "validation-traction"):
        ir = derived_ir(slide_id)
        derived_path = DERIVED_IR_DIR / f"{slide_id}.json"
        derived_path.write_text(json.dumps(ir, indent=2) + "\n", encoding="utf-8")
        solution = compile_slide_ir(
            ROOT,
            ir,
            asset_bindings_path=BINDINGS_REL,
            compiler_label="scripts/build_stage4_oracle_reconstruction.py::compile_slide_ir",
        )
        solutions.append(solution)
        realizations.append(render_layout_slide(ROOT, prs, solution))
        derived_irs.append({
            "slide_id": slide_id,
            "path": str(derived_path.relative_to(ROOT)),
            "variant": VARIANTS[slide_id],
            "visual_ir_hash": solution["visual_ir_hash"],
            "semantic_hash": solution["semantic_hash"],
        })

    pptx = OUT / "queuezero_stage4_oracle_reconstruction_v1.pptx"
    prs.save(pptx)
    (OUT / "layout_solutions.json").write_text(json.dumps(solutions, indent=2) + "\n", encoding="utf-8")
    (OUT / "realizations.json").write_text(json.dumps({
        "schema_version": "stage4-oracle-reconstruction-realization-v1",
        "pptx": str(pptx.relative_to(ROOT)),
        "visual_oracle_generation_id": GENERATION_ID,
        "semantic_authority": "frozen_stage3_semantic_ir",
        "full_slide_oracle_raster_used": False,
        "slide_count": len(realizations),
        "derived_visual_ir": derived_irs,
        "slides": realizations,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Built {pptx}")
    print("Full-slide oracle raster used: false")
    print(f"Slides: {len(realizations)}")


if __name__ == "__main__":
    main()
