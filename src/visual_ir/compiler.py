#!/usr/bin/env python3
"""Stage 4 Visual IR compiler.

Semantic IR + Visual IR + style profile -> normalized layout solution.
The compiler is deliberately thin: it validates the composition contract, resolves
concrete asset instances, and dispatches to a reusable archetype+variant solver.
"""

from __future__ import annotations

from pathlib import Path

from src.ir.runtime import canonical_hash, load_json
from src.visual_ir.archetype_solvers import SOLVER_REGISTRY

STYLE_PATH = "experiment/queuezero/style_profiles/queuezero_hackathon_v0.json"
ASSET_BINDINGS_PATH = "experiment/queuezero/stage4_asset_bindings.json"


def _semantic_asset_source(semantics: dict, object_id: str):
    for asset in semantics.get("assets", []):
        if asset.get("semantic_object_id") != object_id:
            continue
        current = asset.get("current_instance") or {}
        source = current.get("source")
        if source:
            return source
    return None


def _asset_resolver(root: Path, ir: dict, semantics: dict):
    bindings_path = root / ASSET_BINDINGS_PATH
    bindings = load_json(bindings_path) if bindings_path.is_file() else {"bindings": {}}
    slide_bindings = bindings.get("bindings", {}).get(ir["slide_id"], {})

    def resolve(object_id: str):
        explicit = slide_bindings.get(object_id)
        if explicit:
            return explicit
        semantic_source = _semantic_asset_source(semantics, object_id)
        if semantic_source:
            return semantic_source
        raise RuntimeError(
            f"no concrete asset binding for slide={ir['slide_id']!r} object={object_id!r}"
        )

    return resolve


def compile_slide(root: Path, visual_ir_path: Path):
    root = Path(root)
    path = Path(visual_ir_path)
    ir = load_json(path)
    semantics = load_json(root / ir["semantic_file"])
    style = load_json(root / STYLE_PATH)

    if ir["style"]["profile_id"] != style["profile_id"]:
        raise RuntimeError("Visual IR/style profile mismatch")

    key = (ir["composition"]["archetype_id"], ir["composition"]["variant"])
    solver = SOLVER_REGISTRY.get(key)
    if solver is None:
        raise RuntimeError(f"unsupported Stage 4 archetype/variant {key}")

    placements, decorations = solver(
        ir,
        semantics,
        _asset_resolver(root, ir, semantics),
    )

    return {
        "schema_version": "stage4-layout-solution-v0",
        "slide_id": ir["slide_id"],
        "semantic_file": ir["semantic_file"],
        "semantic_hash": canonical_hash(semantics),
        "visual_ir_hash": canonical_hash(ir),
        "style_profile_hash": canonical_hash(style),
        "archetype_id": key[0],
        "variant": key[1],
        "compiler": "src/visual_ir/compiler.py::compile_slide",
        "solver": f"src.visual_ir.archetype_solvers::{solver.__name__}",
        "canvas": {"width_norm": 1.0, "height_norm": 1.0, "background_token": "canvas"},
        "placements": placements,
        "decorations": decorations,
    }


def compile_validation_sample(root: Path, visual_ir_path: Path):
    """Backward-compatible entry point used by the representative sample workflow."""
    solution = compile_slide(root, visual_ir_path)
    if solution["slide_id"] != "validation-traction":
        raise RuntimeError("compile_validation_sample requires validation-traction")
    return solution
