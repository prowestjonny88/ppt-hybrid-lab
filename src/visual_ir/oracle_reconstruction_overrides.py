#!/usr/bin/env python3
"""Targeted oracle-reconstruction geometry refinements.

Kept separate from the first-pass solver module so visual regressions can be
isolated and reviewed without rewriting the initial oracle-derived variants.
"""

from __future__ import annotations

from src.visual_ir.oracle_reconstruction_solvers import (
    _box,
    _connector,
    _objects,
    _process_group,
    _single_role,
    _text,
)


def solve_oracle_process_story_v2(ir, semantics, asset_path_for):
    if ir["composition"]["variant"] != "oracle_visual_system_left_copy_right":
        raise RuntimeError("unsupported oracle process-story variant")

    title = _single_role(semantics, "title")
    subtitle = _single_role(semantics, "subtitle")
    source = _single_role(semantics, "source_note")
    screenshot = _single_role(semantics, "image_slot")
    group = _process_group(semantics)
    objects = _objects(semantics)
    nodes = [oid for oid in group.get("member_ids", []) if objects.get(oid, {}).get("role") == "diagram_node"]
    connectors = [oid for oid in group.get("member_ids", []) if objects.get(oid, {}).get("role") == "connector"]
    if len(nodes) != 4 or len(connectors) != 3:
        raise RuntimeError("oracle process variant requires four nodes and three connectors")
    camera, queue, prediction, decision = nodes
    c1, c2, c3 = connectors

    placements = [
        _text(camera, "node", _box(0.125, 0.215, 0.175, 0.075), 16, 600, "on_dark", valign="middle"),
        _text(queue, "node", _box(0.245, 0.390, 0.175, 0.075), 16, 600, "on_dark", valign="middle"),
        _text(prediction, "node", _box(0.365, 0.565, 0.185, 0.085), 17, 700, "on_dark", valign="middle"),
        # Decision remains readable and independent; product UI becomes a small
        # supporting proof object to its right instead of covering the label.
        _text(decision, "node", _box(0.425, 0.765, 0.140, 0.078), 12.5, 600, "ink", align="center", valign="middle"),
        _connector(c1, "connector", 0.285, 0.285, 0.330, 0.405, "signal", 1.7),
        _connector(c2, "connector", 0.410, 0.460, 0.455, 0.575, "signal", 1.7),
        _connector(c3, "connector", 0.525, 0.635, 0.495, 0.745, "signal", 2.1),
        {
            "semantic_object_id": screenshot,
            "part": "asset",
            "kind": "picture",
            "box": _box(0.575, 0.735, 0.075, 0.150),
            "asset_path": asset_path_for(screenshot),
            "fallback_fill_token": "surface",
        },
        _text(title, "title", _box(0.625, 0.125, 0.325, 0.255), 29.5, 700, "ink"),
        _text(subtitle, "subtitle", _box(0.645, 0.440, 0.300, 0.160), 15.5, 400, "ink", align="center"),
        _text(source, "source", _box(0.725, 0.925, 0.225, 0.030), 8.5, 400, "muted", align="right", valign="middle"),
    ]
    decorations = [
        {"decor_id": "camera_stage", "kind": "round_rect", "box": _box(0.105, 0.190, 0.225, 0.125), "fill_token": "dark_field", "line_token": "signal"},
        {"decor_id": "queue_stage", "kind": "round_rect", "box": _box(0.225, 0.365, 0.225, 0.125), "fill_token": "dark_field", "line_token": "signal"},
        {"decor_id": "prediction_stage", "kind": "round_rect", "box": _box(0.345, 0.535, 0.235, 0.145), "fill_token": "dark_field", "line_token": "signal"},
        {"decor_id": "decision_stage", "kind": "round_rect", "box": _box(0.415, 0.745, 0.160, 0.115), "fill_token": "signal_soft", "line_token": "signal"},
        {"decor_id": "product_proof_stage", "kind": "round_rect", "box": _box(0.565, 0.720, 0.095, 0.180), "fill_token": "surface", "line_token": "line"},
        {"decor_id": "signal_dot_1", "kind": "ellipse", "box": _box(0.305, 0.335, 0.014, 0.025), "fill_token": "signal", "line_token": None},
        {"decor_id": "signal_dot_2", "kind": "ellipse", "box": _box(0.425, 0.510, 0.014, 0.025), "fill_token": "signal", "line_token": None},
        {"decor_id": "signal_dot_3", "kind": "ellipse", "box": _box(0.492, 0.695, 0.014, 0.025), "fill_token": "signal", "line_token": None},
        {"decor_id": "faint_floor", "kind": "rect", "box": _box(0.060, 0.910, 0.600, 0.003), "fill_token": "line", "line_token": None},
    ]
    return placements, decorations


ORACLE_OVERRIDE_SOLVER_REGISTRY = {
    ("process_story", "oracle_visual_system_left_copy_right"): solve_oracle_process_story_v2,
}
