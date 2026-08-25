#!/usr/bin/env python3
"""Oracle-derived Stage 4 composition variants.

These variants reconstruct the *visual direction* of the generated oracle while
keeping Semantic IR as authority. They intentionally use native text/geometry and
only bounded replaceable picture assets; no full-slide oracle raster is accepted.
"""

from __future__ import annotations


def _box(x, y, w, h):
    return [round(x, 6), round(y, 6), round(w, 6), round(h, 6)]


def _text(obj, part, box, size, weight, color="ink", align="left", valign="top", source="content"):
    return {
        "semantic_object_id": obj,
        "part": part,
        "kind": "text",
        "box": box,
        "text_source": source,
        "font_size_pt": size,
        "font_weight": weight,
        "color_token": color,
        "align": align,
        "valign": valign,
    }


def _connector(obj, part, x1, y1, x2, y2, color="line", width=1.5):
    return {
        "semantic_object_id": obj,
        "part": part,
        "kind": "connector",
        "points": [round(x1, 6), round(y1, 6), round(x2, 6), round(y2, 6)],
        "color_token": color,
        "width_pt": width,
    }


def _objects(semantics):
    return {item["object_id"]: item for item in semantics.get("semantic_objects", [])}


def _ids_by_role(semantics, role):
    return [item["object_id"] for item in semantics.get("semantic_objects", []) if item.get("role") == role]


def _single(values, label):
    if len(values) != 1:
        raise RuntimeError(f"expected exactly one {label}; got {values}")
    return values[0]


def _single_role(semantics, role):
    return _single(_ids_by_role(semantics, role), f"semantic role {role!r}")


def _visual_role(ir, semantics, visual_role, semantic_role=None):
    objects = _objects(semantics)
    values = [oid for oid, role in ir.get("hierarchy", {}).get("roles", {}).items() if role == visual_role]
    if semantic_role is not None:
        values = [oid for oid in values if objects.get(oid, {}).get("role") == semantic_role]
    return _single(values, f"visual role {visual_role!r} / semantic role {semantic_role!r}")


def _process_group(semantics):
    matches = [g for g in semantics.get("groups", []) if g.get("layout_hint") == "left_to_right_process"]
    return _single(matches, "left_to_right_process group")


def solve_oracle_editorial_hero(ir, semantics, asset_path_for):
    if ir["composition"]["variant"] != "oracle_dark_metric_scene_right":
        raise RuntimeError("unsupported oracle editorial hero variant")

    title = _single_role(semantics, "title")
    subtitle = _single_role(semantics, "subtitle")
    source = _single_role(semantics, "source_note")
    metric = _visual_role(ir, semantics, "hero", "metric")
    annotation = _single_role(semantics, "annotation")
    visual = _single([oid for oid, obj in _objects(semantics).items() if obj.get("role") == "hero_visual_slot"], "hero visual")

    placements = [
        _text(title, "title", _box(0.055, 0.105, 0.525, 0.205), 31.5, 700, "on_dark"),
        _text(subtitle, "subtitle", _box(0.055, 0.335, 0.500, 0.095), 14.5, 400, "line"),
        _text(metric, "value", _box(0.075, 0.505, 0.430, 0.130), 58, 700, "attention", valign="middle"),
        _text(metric, "label", _box(0.078, 0.638, 0.190, 0.052), 17, 500, "on_dark", source="label"),
        _text(annotation, "annotation", _box(0.055, 0.755, 0.500, 0.125), 14.5, 500, "on_dark"),
        {
            "semantic_object_id": visual,
            "part": "asset",
            "kind": "picture",
            "box": _box(0.575, 0.095, 0.390, 0.790),
            "asset_path": asset_path_for(visual),
            "fallback_fill_token": "surface",
        },
        _text(source, "source", _box(0.055, 0.930, 0.490, 0.030), 8.5, 400, "line", valign="middle"),
    ]
    decorations = [
        {"decor_id": "metric_signal_bar", "kind": "rect", "box": _box(0.055, 0.510, 0.006, 0.185), "fill_token": "attention", "line_token": None},
        {"decor_id": "hero_frame_top", "kind": "rect", "box": _box(0.560, 0.080, 0.300, 0.003), "fill_token": "signal", "line_token": None},
        {"decor_id": "hero_frame_right", "kind": "rect", "box": _box(0.965, 0.145, 0.003, 0.670), "fill_token": "signal", "line_token": None},
        {"decor_id": "hero_frame_bottom", "kind": "rect", "box": _box(0.560, 0.895, 0.245, 0.003), "fill_token": "attention", "line_token": None},
        {"decor_id": "small_signal_tick", "kind": "rect", "box": _box(0.925, 0.330, 0.025, 0.004), "fill_token": "attention", "line_token": None},
    ]
    return placements, decorations


def solve_oracle_process_story(ir, semantics, asset_path_for):
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
        _text(decision, "node", _box(0.465, 0.770, 0.170, 0.080), 13.5, 600, "ink", align="center", valign="middle"),
        _connector(c1, "connector", 0.285, 0.285, 0.330, 0.405, "signal", 1.7),
        _connector(c2, "connector", 0.410, 0.460, 0.455, 0.575, "signal", 1.7),
        _connector(c3, "connector", 0.525, 0.635, 0.545, 0.755, "signal", 2.1),
        {
            "semantic_object_id": screenshot,
            "part": "asset",
            "kind": "picture",
            "box": _box(0.505, 0.710, 0.135, 0.205),
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
        {"decor_id": "decision_stage", "kind": "round_rect", "box": _box(0.455, 0.745, 0.190, 0.115), "fill_token": "signal_soft", "line_token": "signal"},
        {"decor_id": "signal_dot_1", "kind": "ellipse", "box": _box(0.305, 0.335, 0.014, 0.025), "fill_token": "signal", "line_token": None},
        {"decor_id": "signal_dot_2", "kind": "ellipse", "box": _box(0.425, 0.510, 0.014, 0.025), "fill_token": "signal", "line_token": None},
        {"decor_id": "signal_dot_3", "kind": "ellipse", "box": _box(0.535, 0.690, 0.014, 0.025), "fill_token": "signal", "line_token": None},
        {"decor_id": "faint_floor", "kind": "rect", "box": _box(0.060, 0.885, 0.560, 0.003), "fill_token": "line", "line_token": None},
    ]
    return placements, decorations


def solve_oracle_dominant_metric(ir, semantics, asset_path_for):
    del asset_path_for
    if ir["composition"]["variant"] != "oracle_evidence_field_to_pilot":
        raise RuntimeError("unsupported oracle dominant-metric variant")

    title = _single_role(semantics, "title")
    subtitle = _single_role(semantics, "subtitle")
    source = _single_role(semantics, "source_note")
    hero = _visual_role(ir, semantics, "hero", "metric")
    objects = _objects(semantics)
    primary_metric = _single([
        oid for oid, vr in ir.get("hierarchy", {}).get("roles", {}).items()
        if vr == "primary_support" and objects.get(oid, {}).get("role") == "metric"
    ], "primary supporting metric")
    pilot = _single([
        oid for oid, vr in ir.get("hierarchy", {}).get("roles", {}).items()
        if vr == "primary_support" and objects.get(oid, {}).get("role") == "annotation"
    ], "pilot annotation")
    secondary = [
        oid for oid, vr in ir.get("hierarchy", {}).get("roles", {}).items()
        if vr == "secondary_support" and objects.get(oid, {}).get("role") == "metric"
    ]
    if len(secondary) != 2:
        raise RuntimeError("oracle validation variant requires two secondary metrics")
    s1, s2 = secondary

    placements = [
        _text(title, "title", _box(0.050, 0.060, 0.900, 0.105), 30.5, 700, "ink"),
        _text(subtitle, "subtitle", _box(0.050, 0.170, 0.900, 0.060), 14.5, 400, "ink"),
        _text(primary_metric, "value", _box(0.285, 0.305, 0.185, 0.095), 36, 700, "on_dark", valign="middle"),
        _text(primary_metric, "label", _box(0.285, 0.400, 0.180, 0.040), 12.5, 400, "on_dark", source="label"),
        _text(hero, "value", _box(0.285, 0.465, 0.185, 0.100), 40, 700, "on_dark", valign="middle"),
        _text(hero, "label", _box(0.285, 0.565, 0.180, 0.040), 12.5, 400, "on_dark", source="label"),
        _text(s1, "value", _box(0.285, 0.630, 0.100, 0.070), 28, 700, "on_dark", valign="middle"),
        _text(s1, "label", _box(0.285, 0.700, 0.135, 0.036), 10.5, 400, "on_dark", source="label"),
        _text(s2, "value", _box(0.285, 0.755, 0.100, 0.070), 28, 700, "on_dark", valign="middle"),
        _text(s2, "label", _box(0.285, 0.825, 0.135, 0.036), 10.5, 400, "on_dark", source="label"),
        _text(pilot, "destination", _box(0.790, 0.475, 0.175, 0.150), 18, 600, "ink", valign="middle"),
        _text(source, "source", _box(0.705, 0.925, 0.260, 0.030), 8.5, 400, "muted", align="right", valign="middle"),
    ]
    decorations = [
        {"decor_id": "evidence_field", "kind": "round_rect", "box": _box(0.000, 0.255, 0.515, 0.665), "fill_token": "dark_field", "line_token": None},
        {"decor_id": "ribbon_signal_a", "kind": "round_rect", "box": _box(0.000, 0.455, 0.255, 0.055), "fill_token": "signal", "line_token": None},
        {"decor_id": "ribbon_signal_b", "kind": "round_rect", "box": _box(0.000, 0.580, 0.235, 0.040), "fill_token": "attention", "line_token": None},
        {"decor_id": "ribbon_signal_c", "kind": "round_rect", "box": _box(0.000, 0.705, 0.250, 0.035), "fill_token": "line", "line_token": None},
        {"decor_id": "strand_1", "kind": "line", "points": [0.455, 0.350, 0.780, 0.525], "color_token": "line", "width_pt": 1.25},
        {"decor_id": "strand_2", "kind": "line", "points": [0.455, 0.520, 0.780, 0.525], "color_token": "signal", "width_pt": 1.8},
        {"decor_id": "strand_3", "kind": "line", "points": [0.430, 0.670, 0.780, 0.525], "color_token": "line", "width_pt": 1.25},
        {"decor_id": "strand_4", "kind": "line", "points": [0.430, 0.800, 0.780, 0.525], "color_token": "line", "width_pt": 1.25},
        {"decor_id": "node_1", "kind": "ellipse", "box": _box(0.630, 0.375, 0.018, 0.032), "fill_token": "signal", "line_token": "dark_field"},
        {"decor_id": "node_2", "kind": "ellipse", "box": _box(0.630, 0.485, 0.018, 0.032), "fill_token": "signal", "line_token": "dark_field"},
        {"decor_id": "node_3", "kind": "ellipse", "box": _box(0.630, 0.595, 0.018, 0.032), "fill_token": "signal", "line_token": "dark_field"},
        {"decor_id": "destination_node", "kind": "ellipse", "box": _box(0.765, 0.505, 0.025, 0.045), "fill_token": "signal", "line_token": None},
        {"decor_id": "source_rule", "kind": "rect", "box": _box(0.505, 0.900, 0.465, 0.002), "fill_token": "line", "line_token": None},
    ]
    return placements, decorations


ORACLE_SOLVER_REGISTRY = {
    ("editorial_hero", "oracle_dark_metric_scene_right"): solve_oracle_editorial_hero,
    ("process_story", "oracle_visual_system_left_copy_right"): solve_oracle_process_story,
    ("dominant_metric", "oracle_evidence_field_to_pilot"): solve_oracle_dominant_metric,
}
