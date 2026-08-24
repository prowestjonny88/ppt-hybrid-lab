#!/usr/bin/env python3
"""Deterministic Stage 4 Visual IR compiler for the QueueZero benchmark.

Semantic IR + Visual IR + style profile -> normalized layout solution.
Coordinates first appear here, downstream of semantic and visual reasoning.
"""

from __future__ import annotations

from pathlib import Path

from src.ir.runtime import canonical_hash, load_json

STYLE_PATH = "experiment/queuezero/style_profiles/queuezero_hackathon_v0.json"
SUPPORTED = {
    ("problem-hook", "editorial_hero", "open_metric_left_edge_crop_right"),
    ("how-it-works", "process_story", "signal_path_to_product_destination"),
    ("validation-traction", "dominant_metric", "hero_left_technical_proof_right_terminal_band"),
}


def _box(x, y, w, h):
    return [round(x, 6), round(y, 6), round(w, 6), round(h, 6)]


def _text(obj, part, box, size, weight, color="ink", align="left", valign="top", source="content"):
    return {
        "semantic_object_id": obj, "part": part, "kind": "text", "box": box,
        "text_source": source, "font_size_pt": size, "font_weight": weight,
        "color_token": color, "align": align, "valign": valign,
    }


def _solution(root: Path, visual_ir_path: Path, placements, decorations):
    ir = load_json(visual_ir_path)
    semantics = load_json(root / ir["semantic_file"])
    style = load_json(root / STYLE_PATH)
    key = (ir["slide_id"], ir["composition"]["archetype_id"], ir["composition"]["variant"])
    if key not in SUPPORTED:
        raise RuntimeError(f"unsupported Stage 4 composition {key}")
    if ir["style"]["profile_id"] != style["profile_id"]:
        raise RuntimeError("Visual IR/style profile mismatch")
    return {
        "schema_version": "stage4-layout-solution-v0",
        "slide_id": ir["slide_id"],
        "semantic_file": ir["semantic_file"],
        "semantic_hash": canonical_hash(semantics),
        "visual_ir_hash": canonical_hash(ir),
        "style_profile_hash": canonical_hash(style),
        "archetype_id": ir["composition"]["archetype_id"],
        "variant": ir["composition"]["variant"],
        "compiler": "src/visual_ir/compiler.py::compile_slide",
        "canvas": {"width_norm": 1.0, "height_norm": 1.0, "background_token": "canvas"},
        "placements": placements,
        "decorations": decorations,
    }


def _compile_problem(root: Path, path: Path):
    placements = [
        _text("title", "title", _box(0.052, 0.080, 0.44, 0.175), 27, 700),
        _text("subtitle", "subtitle", _box(0.052, 0.270, 0.43, 0.072), 12.5, 400, "muted"),
        # Keep the supplied "15–30 min" evidence together as one visual unit.
        # The previous 76pt / 0.39-wide treatment wrapped "min" onto a second
        # line and collided with its label despite passing box-only QA.
        _text("metric_wait", "value", _box(0.052, 0.405, 0.43, 0.155), 64, 700, "signal", valign="middle"),
        _text("metric_wait", "label", _box(0.058, 0.575, 0.22, 0.050), 16, 600, source="label"),
        _text("pain_annotation", "annotation", _box(0.052, 0.690, 0.41, 0.125), 15, 500),
        {
            "semantic_object_id": "hero_visual_slot", "part": "asset", "kind": "picture",
            "box": _box(0.515, 0.000, 0.485, 1.000),
            "asset_path": "benchmark/generated/queuezero/gemini31flashimage-v1/hybrid/problem_hero.jpg",
            "fallback_fill_token": "signal_soft",
        },
        _text("source_note", "source", _box(0.052, 0.935, 0.42, 0.030), 8.5, 400, "muted", valign="middle"),
    ]
    decorations = [
        {"decor_id": "top_signal_rule", "kind": "rect", "box": _box(0.052, 0.052, 0.10, 0.005), "fill_token": "signal", "line_token": None},
        {"decor_id": "image_edge", "kind": "rect", "box": _box(0.512, 0.000, 0.006, 1.000), "fill_token": "signal", "line_token": None},
        {"decor_id": "metric_rule", "kind": "rect", "box": _box(0.052, 0.655, 0.165, 0.004), "fill_token": "attention", "line_token": None},
    ]
    return _solution(root, path, placements, decorations)


def _compile_how_it_works(root: Path, path: Path):
    placements = [
        _text("title", "title", _box(0.052, 0.070, 0.70, 0.145), 27, 700),
        _text("subtitle", "subtitle", _box(0.052, 0.225, 0.72, 0.055), 12, 400, "muted"),
        _text("node_camera", "node", _box(0.070, 0.370, 0.14, 0.070), 16, 600),
        _text("node_queue_estimator", "node", _box(0.245, 0.370, 0.14, 0.070), 16, 600),
        _text("node_wait_predictor", "node", _box(0.420, 0.355, 0.155, 0.100), 18, 700, "signal"),
        _text("node_decision", "node", _box(0.620, 0.320, 0.205, 0.135), 19, 700),
        {"semantic_object_id": "connector_camera_queue", "part": "connector", "kind": "line", "box": _box(0.205, 0.405, 0.045, 0.004), "color_token": "line"},
        {"semantic_object_id": "connector_queue_prediction", "part": "connector", "kind": "line", "box": _box(0.380, 0.405, 0.045, 0.004), "color_token": "line"},
        {"semantic_object_id": "connector_prediction_decision", "part": "connector", "kind": "line", "box": _box(0.570, 0.405, 0.055, 0.005), "color_token": "signal"},
        {
            "semantic_object_id": "screenshot_main", "part": "asset", "kind": "picture",
            "box": _box(0.690, 0.490, 0.255, 0.370),
            "asset_path": "experiment/queuezero/assets/product_ui_v1.png",
            "fallback_fill_token": "surface",
        },
        _text("source_note", "source", _box(0.052, 0.935, 0.50, 0.030), 8.5, 400, "muted", valign="middle"),
    ]
    decorations = [
        {"decor_id": "top_signal_rule", "kind": "rect", "box": _box(0.052, 0.045, 0.10, 0.005), "fill_token": "signal", "line_token": None},
        {"decor_id": "pipeline_spine", "kind": "rect", "box": _box(0.070, 0.477, 0.755, 0.004), "fill_token": "line", "line_token": None},
        {"decor_id": "decision_node", "kind": "ellipse", "box": _box(0.812, 0.461, 0.020, 0.035), "fill_token": "attention", "line_token": None},
        {"decor_id": "product_stage_rule", "kind": "rect", "box": _box(0.690, 0.870, 0.255, 0.004), "fill_token": "signal", "line_token": None},
    ]
    return _solution(root, path, placements, decorations)


def _compile_validation(root: Path, path: Path):
    placements = [
        _text("title", "title", _box(0.052, 0.105, 0.505, 0.145), 29, 700),
        _text("subtitle", "subtitle", _box(0.052, 0.285, 0.490, 0.085), 12.5, 400, "muted"),
        _text("metric_weekly_intent", "value", _box(0.052, 0.475, 0.500, 0.225), 92, 700, "signal", valign="middle"),
        _text("metric_weekly_intent", "label", _box(0.058, 0.715, 0.330, 0.060), 18, 600, source="label"),
        _text("metric_mae", "value", _box(0.700, 0.125, 0.245, 0.115), 42, 700, "on_dark", valign="middle"),
        _text("metric_mae", "label", _box(0.702, 0.245, 0.220, 0.050), 13, 500, "on_dark", source="label"),
        _text("metric_students", "value", _box(0.702, 0.390, 0.100, 0.075), 28, 700, "on_dark", valign="middle"),
        _text("metric_students", "label", _box(0.702, 0.468, 0.145, 0.042), 10.5, 400, "line", source="label"),
        _text("metric_cafeterias", "value", _box(0.855, 0.390, 0.080, 0.075), 28, 700, "on_dark", valign="middle"),
        _text("metric_cafeterias", "label", _box(0.855, 0.468, 0.110, 0.042), 10.5, 400, "line", source="label"),
        _text("pilot_gate", "label", _box(0.702, 0.690, 0.245, 0.145), 16, 600, "on_dark"),
        _text("source_note", "source", _box(0.052, 0.935, 0.500, 0.030), 8.5, 400, "muted", valign="middle"),
    ]
    decorations = [
        {"decor_id": "top_signal_rule", "kind": "rect", "box": _box(0.052, 0.060, 0.105, 0.005), "fill_token": "signal", "line_token": None},
        {"decor_id": "technical_proof_field", "kind": "rect", "box": _box(0.640, 0.000, 0.360, 1.000), "fill_token": "dark_field", "line_token": None},
        {"decor_id": "technical_field_edge", "kind": "rect", "box": _box(0.637, 0.000, 0.006, 1.000), "fill_token": "signal", "line_token": None},
        {"decor_id": "technical_divider", "kind": "rect", "box": _box(0.702, 0.330, 0.230, 0.003), "fill_token": "muted", "line_token": None},
        {"decor_id": "scope_divider", "kind": "rect", "box": _box(0.830, 0.390, 0.002, 0.125), "fill_token": "muted", "line_token": None},
        {"decor_id": "pilot_signal_line", "kind": "rect", "box": _box(0.702, 0.625, 0.205, 0.004), "fill_token": "signal", "line_token": None},
        {"decor_id": "pilot_node", "kind": "ellipse", "box": _box(0.913, 0.610, 0.018, 0.032), "fill_token": "attention", "line_token": None},
    ]
    return _solution(root, path, placements, decorations)


def compile_slide(root: Path, visual_ir_path: Path):
    root = Path(root)
    path = Path(visual_ir_path)
    ir = load_json(path)
    slide_id = ir["slide_id"]
    if slide_id == "problem-hook":
        return _compile_problem(root, path)
    if slide_id == "how-it-works":
        return _compile_how_it_works(root, path)
    if slide_id == "validation-traction":
        return _compile_validation(root, path)
    raise RuntimeError(f"unsupported Stage 4 slide {slide_id}")


def compile_validation_sample(root: Path, visual_ir_path: Path):
    """Backward-compatible entry point used by the representative sample workflow."""
    solution = compile_slide(root, visual_ir_path)
    if solution["slide_id"] != "validation-traction":
        raise RuntimeError("compile_validation_sample requires validation-traction")
    return solution
