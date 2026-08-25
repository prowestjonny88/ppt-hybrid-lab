#!/usr/bin/env python3
"""Stage 4 Visual IR compiler.

Semantic IR + Visual IR + resolved design language/profile -> normalized layout
solution. The compiler validates capacity and deterministic routing eligibility,
resolves concrete asset instances, and dispatches to a reusable archetype+variant
solver.
"""

from __future__ import annotations

from pathlib import Path

from src.ir.runtime import canonical_hash, load_json
from src.visual_ir.archetype_solvers import SOLVER_REGISTRY as BASE_SOLVER_REGISTRY
from src.visual_ir.oracle_reconstruction_solvers import ORACLE_SOLVER_REGISTRY
from src.visual_ir.capacity import require_capacity
from src.visual_ir.router import route_candidates
from src.visual_ir.style_runtime import resolve_style_profile

STYLE_PATH = "experiment/queuezero/style_profiles/queuezero_hackathon_v0.json"
ASSET_BINDINGS_PATH = "experiment/queuezero/stage4_asset_bindings.json"
SOLVER_REGISTRY = {**BASE_SOLVER_REGISTRY, **ORACLE_SOLVER_REGISTRY}


def _semantic_asset_source(semantics: dict, object_id: str):
    for asset in semantics.get("assets", []):
        if asset.get("semantic_object_id") != object_id:
            continue
        current = asset.get("current_instance") or {}
        source = current.get("source")
        if source:
            return source
    return None


def _asset_resolver(root: Path, ir: dict, semantics: dict, bindings_rel=ASSET_BINDINGS_PATH):
    bindings_path = root / bindings_rel
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


def compile_slide_ir(
    root: Path,
    ir: dict,
    *,
    style_path: str = STYLE_PATH,
    asset_bindings_path: str = ASSET_BINDINGS_PATH,
    compiler_label: str = "src/visual_ir/compiler.py::compile_slide_ir",
):
    """Compile an already-loaded Visual IR object.

    This preserves the normal fail-closed routing/capacity/style contracts while
    allowing derived benchmark variants to be created without mutating the
    canonical Stage 4 Visual IR files.
    """
    root = Path(root)
    semantics = load_json(root / ir["semantic_file"])
    style, profile, language = resolve_style_profile(root, root / style_path)

    if ir["style"]["profile_id"] != profile["profile_id"]:
        raise RuntimeError("Visual IR/style profile mismatch")

    capacity = require_capacity(root, ir, semantics)
    routing = route_candidates(root, semantics)
    selected_archetype = ir["composition"]["archetype_id"]
    if selected_archetype not in routing["candidates"]:
        raise RuntimeError(
            f"selected archetype {selected_archetype!r} was not deterministically eligible; "
            f"candidates={routing['candidates']}"
        )

    key = (selected_archetype, ir["composition"]["variant"])
    solver = SOLVER_REGISTRY.get(key)
    if solver is None:
        raise RuntimeError(f"unsupported Stage 4 archetype/variant {key}")

    placements, decorations = solver(
        ir,
        semantics,
        _asset_resolver(root, ir, semantics, asset_bindings_path),
    )

    return {
        "schema_version": "stage4-layout-solution-v0",
        "slide_id": ir["slide_id"],
        "semantic_file": ir["semantic_file"],
        "semantic_hash": canonical_hash(semantics),
        "visual_ir_hash": canonical_hash(ir),
        "design_language_id": language["design_language_id"],
        "design_language_hash": canonical_hash(language),
        "style_profile_id": profile["profile_id"],
        "style_profile_hash": canonical_hash(profile),
        "resolved_style_hash": canonical_hash(style),
        "archetype_id": key[0],
        "variant": key[1],
        "capacity_trace": capacity,
        "routing_trace": routing,
        "compiler": compiler_label,
        "solver": f"{solver.__module__}::{solver.__name__}",
        "canvas": {
            "width_norm": 1.0,
            "height_norm": 1.0,
            "background_token": ir.get("style", {}).get("canvas_background_token", "canvas"),
        },
        "placements": placements,
        "decorations": decorations,
    }


def compile_slide(root: Path, visual_ir_path: Path):
    root = Path(root)
    path = Path(visual_ir_path)
    ir = load_json(path)
    return compile_slide_ir(
        root,
        ir,
        compiler_label="src/visual_ir/compiler.py::compile_slide",
    )


def compile_validation_sample(root: Path, visual_ir_path: Path):
    """Backward-compatible entry point used by the representative sample workflow."""
    solution = compile_slide(root, visual_ir_path)
    if solution["slide_id"] != "validation-traction":
        raise RuntimeError("compile_validation_sample requires validation-traction")
    return solution
