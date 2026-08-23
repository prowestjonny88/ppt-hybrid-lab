#!/usr/bin/env python3
"""Stage 4 Visual IR compiler.

V0 intentionally supports ONE QueueZero composition variant only. The point is to
prove the architecture boundary before expanding the archetype library.

Semantic IR + Visual IR + style profile -> deterministic layout solution.
Visual IR itself never contains PPTX coordinates; this compiler is where
normalized geometry first becomes concrete.
"""

from __future__ import annotations

from pathlib import Path

from src.ir.runtime import canonical_hash, load_json

SUPPORTED = ("dominant_metric", "hero_left_technical_proof_right_terminal_band")


def _box(x, y, w, h):
    return [round(x, 6), round(y, 6), round(w, 6), round(h, 6)]


def compile_validation_sample(root: Path, visual_ir_path: Path):
    root = Path(root)
    visual_ir_path = Path(visual_ir_path)
    ir = load_json(visual_ir_path)
    semantics = load_json(root / ir["semantic_file"])
    style = load_json(root / "experiment/queuezero/style_profiles/queuezero_hackathon_v0.json")

    if ir["slide_id"] != "validation-traction":
        raise RuntimeError(f"Stage 4 V0 compiler only supports validation-traction; got {ir['slide_id']}")
    key = (ir["composition"]["archetype_id"], ir["composition"]["variant"])
    if key != SUPPORTED:
        raise RuntimeError(f"unsupported Stage 4 V0 composition {key}; expected {SUPPORTED}")
    if ir["style"]["profile_id"] != style["profile_id"]:
        raise RuntimeError("Visual IR/style profile mismatch")

    # Layout grammar for dominant_metric / hero-left + proof-right + terminal-band.
    # Coordinates first appear HERE, downstream of visual reasoning.
    placements = [
        {
            "semantic_object_id": "title", "part": "title", "kind": "text",
            "box": _box(0.052, 0.058, 0.89, 0.075), "text_source": "content",
            "type_role": "title", "font_size_pt": 24.5, "font_weight": 700,
            "color_token": "ink", "align": "left", "valign": "top"
        },
        {
            "semantic_object_id": "subtitle", "part": "subtitle", "kind": "text",
            "box": _box(0.052, 0.143, 0.82, 0.050), "text_source": "content",
            "type_role": "subtitle", "font_size_pt": 12.0, "font_weight": 400,
            "color_token": "muted", "align": "left", "valign": "top"
        },
        {
            "semantic_object_id": "metric_weekly_intent", "part": "value", "kind": "text",
            "box": _box(0.052, 0.265, 0.36, 0.235), "text_source": "content",
            "type_role": "hero_numeric", "font_size_pt": 78, "font_weight": 700,
            "color_token": "signal", "align": "left", "valign": "middle"
        },
        {
            "semantic_object_id": "metric_weekly_intent", "part": "label", "kind": "text",
            "box": _box(0.058, 0.505, 0.30, 0.060), "text_source": "label",
            "type_role": "hero_label", "font_size_pt": 17, "font_weight": 600,
            "color_token": "ink", "align": "left", "valign": "top"
        },
        {
            "semantic_object_id": "metric_mae", "part": "value", "kind": "text",
            "box": _box(0.605, 0.285, 0.30, 0.115), "text_source": "content",
            "type_role": "support_numeric", "font_size_pt": 42, "font_weight": 700,
            "color_token": "on_dark", "align": "left", "valign": "middle"
        },
        {
            "semantic_object_id": "metric_mae", "part": "label", "kind": "text",
            "box": _box(0.608, 0.402, 0.28, 0.050), "text_source": "label",
            "type_role": "support_label", "font_size_pt": 13, "font_weight": 500,
            "color_token": "on_dark", "align": "left", "valign": "top"
        },
        {
            "semantic_object_id": "metric_students", "part": "value", "kind": "text",
            "box": _box(0.608, 0.515, 0.11, 0.075), "text_source": "content",
            "type_role": "scope_numeric", "font_size_pt": 27, "font_weight": 700,
            "color_token": "on_dark", "align": "left", "valign": "middle"
        },
        {
            "semantic_object_id": "metric_students", "part": "label", "kind": "text",
            "box": _box(0.608, 0.592, 0.17, 0.042), "text_source": "label",
            "type_role": "scope_label", "font_size_pt": 10.5, "font_weight": 400,
            "color_token": "line", "align": "left", "valign": "top"
        },
        {
            "semantic_object_id": "metric_cafeterias", "part": "value", "kind": "text",
            "box": _box(0.810, 0.515, 0.09, 0.075), "text_source": "content",
            "type_role": "scope_numeric", "font_size_pt": 27, "font_weight": 700,
            "color_token": "on_dark", "align": "left", "valign": "middle"
        },
        {
            "semantic_object_id": "metric_cafeterias", "part": "label", "kind": "text",
            "box": _box(0.810, 0.592, 0.14, 0.042), "text_source": "label",
            "type_role": "scope_label", "font_size_pt": 10.5, "font_weight": 400,
            "color_token": "line", "align": "left", "valign": "top"
        },
        {
            "semantic_object_id": "pilot_gate", "part": "label", "kind": "text",
            "box": _box(0.445, 0.775, 0.47, 0.055), "text_source": "content",
            "type_role": "terminal", "font_size_pt": 14.5, "font_weight": 600,
            "color_token": "ink", "align": "right", "valign": "middle"
        },
        {
            "semantic_object_id": "source_note", "part": "source", "kind": "text",
            "box": _box(0.052, 0.935, 0.62, 0.030), "text_source": "content",
            "type_role": "source", "font_size_pt": 8.5, "font_weight": 400,
            "color_token": "muted", "align": "left", "valign": "middle"
        }
    ]

    decorations = [
        {
            "decor_id": "top_signal_rule", "kind": "rect",
            "box": _box(0.052, 0.035, 0.105, 0.005), "fill_token": "signal", "line_token": None
        },
        {
            "decor_id": "technical_proof_field", "kind": "rect",
            "box": _box(0.565, 0.230, 0.435, 0.475), "fill_token": "dark_field", "line_token": None
        },
        {
            "decor_id": "technical_signal_edge", "kind": "rect",
            "box": _box(0.565, 0.230, 0.006, 0.475), "fill_token": "signal", "line_token": None
        },
        {
            "decor_id": "technical_divider", "kind": "rect",
            "box": _box(0.608, 0.478, 0.330, 0.003), "fill_token": "muted", "line_token": None
        },
        {
            "decor_id": "pilot_signal_line", "kind": "rect",
            "box": _box(0.052, 0.855, 0.350, 0.004), "fill_token": "line", "line_token": None
        },
        {
            "decor_id": "pilot_signal_line_active", "kind": "rect",
            "box": _box(0.402, 0.855, 0.505, 0.004), "fill_token": "signal", "line_token": None
        },
        {
            "decor_id": "pilot_node", "kind": "ellipse",
            "box": _box(0.914, 0.839, 0.017, 0.030), "fill_token": "attention", "line_token": None
        }
    ]

    return {
        "schema_version": "stage4-layout-solution-v0",
        "slide_id": ir["slide_id"],
        "semantic_hash": canonical_hash(semantics),
        "visual_ir_hash": canonical_hash(ir),
        "style_profile_hash": canonical_hash(style),
        "archetype_id": ir["composition"]["archetype_id"],
        "variant": ir["composition"]["variant"],
        "compiler": "src/visual_ir/compiler.py::compile_validation_sample",
        "canvas": {"width_norm": 1.0, "height_norm": 1.0, "background_token": "canvas"},
        "placements": placements,
        "decorations": decorations
    }
