#!/usr/bin/env python3
"""Reusable Stage 4 composition solvers.

These functions bind semantic objects by role/hierarchy/group structure and then
realize one declared archetype variant. They intentionally know nothing about
QueueZero slide IDs. Dataset-specific asset file selection is injected by the
compiler through ``asset_path_for``.
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


def _semantic_objects(semantics):
    return {item["object_id"]: item for item in semantics.get("semantic_objects", [])}


def _ids_by_semantic_role(semantics, role):
    return [
        item["object_id"]
        for item in semantics.get("semantic_objects", [])
        if item.get("role") == role
    ]


def _ids_by_visual_role(ir, role):
    return [
        object_id
        for object_id, visual_role in ir.get("hierarchy", {}).get("roles", {}).items()
        if visual_role == role
    ]


def _single(values, label):
    if len(values) != 1:
        raise RuntimeError(f"expected exactly one {label}; got {values}")
    return values[0]


def _single_semantic(semantics, role):
    return _single(_ids_by_semantic_role(semantics, role), f"semantic role {role!r}")


def _single_visual_semantic(ir, semantics, visual_role, semantic_role=None):
    objects = _semantic_objects(semantics)
    candidates = _ids_by_visual_role(ir, visual_role)
    if semantic_role is not None:
        candidates = [oid for oid in candidates if objects.get(oid, {}).get("role") == semantic_role]
    return _single(candidates, f"visual role {visual_role!r} / semantic role {semantic_role!r}")


def _semantic_group(semantics, *, layout_hint=None, group_id=None):
    groups = semantics.get("groups", [])
    matches = []
    for group in groups:
        if group_id is not None and group.get("group_id") == group_id:
            matches.append(group)
        elif layout_hint is not None and group.get("layout_hint") == layout_hint:
            matches.append(group)
    return _single(matches, f"semantic group group_id={group_id!r} layout_hint={layout_hint!r}")


def solve_editorial_hero(ir, semantics, asset_path_for):
    if ir["composition"]["variant"] != "open_metric_left_edge_crop_right":
        raise RuntimeError("unsupported editorial_hero variant")

    title = _single_semantic(semantics, "title")
    subtitle = _single_semantic(semantics, "subtitle")
    source = _single_semantic(semantics, "source_note")
    hero_metric = _single_visual_semantic(ir, semantics, "hero", "metric")
    annotation = _single_semantic(semantics, "annotation")

    objects = _semantic_objects(semantics)
    visual_candidates = [
        oid for oid, obj in objects.items()
        if obj.get("role") in {"hero_visual_slot", "image_slot"}
    ]
    visual = _single(visual_candidates, "editorial hero visual slot")

    placements = [
        _text(title, "title", _box(0.052, 0.080, 0.44, 0.175), 27, 700),
        _text(subtitle, "subtitle", _box(0.052, 0.270, 0.43, 0.072), 12.5, 400, "muted"),
        _text(hero_metric, "value", _box(0.052, 0.405, 0.43, 0.155), 64, 700, "signal", valign="middle"),
        _text(hero_metric, "label", _box(0.058, 0.575, 0.22, 0.050), 16, 600, source="label"),
        _text(annotation, "annotation", _box(0.052, 0.690, 0.41, 0.125), 15, 500),
        {
            "semantic_object_id": visual,
            "part": "asset",
            "kind": "picture",
            "box": _box(0.515, 0.000, 0.485, 1.000),
            "asset_path": asset_path_for(visual),
            "fallback_fill_token": "signal_soft",
        },
        _text(source, "source", _box(0.052, 0.935, 0.42, 0.030), 8.5, 400, "muted", valign="middle"),
    ]
    decorations = [
        {"decor_id": "top_signal_rule", "kind": "rect", "box": _box(0.052, 0.052, 0.10, 0.005), "fill_token": "signal", "line_token": None},
        {"decor_id": "image_edge", "kind": "rect", "box": _box(0.512, 0.000, 0.006, 1.000), "fill_token": "signal", "line_token": None},
        {"decor_id": "metric_rule", "kind": "rect", "box": _box(0.052, 0.655, 0.165, 0.004), "fill_token": "attention", "line_token": None},
    ]
    return placements, decorations


def solve_process_story(ir, semantics, asset_path_for):
    if ir["composition"]["variant"] != "signal_path_to_product_destination":
        raise RuntimeError("unsupported process_story variant")

    title = _single_semantic(semantics, "title")
    subtitle = _single_semantic(semantics, "subtitle")
    source = _single_semantic(semantics, "source_note")
    screenshot = _single_semantic(semantics, "image_slot")
    hero = _single_visual_semantic(ir, semantics, "hero", "diagram_node")

    group = _semantic_group(semantics, layout_hint="left_to_right_process")
    objects = _semantic_objects(semantics)
    ordered_nodes = [
        oid for oid in group.get("member_ids", [])
        if objects.get(oid, {}).get("role") == "diagram_node"
    ]
    if len(ordered_nodes) != 4:
        raise RuntimeError(f"process_story V0 expects four ordered diagram nodes; got {ordered_nodes}")
    camera, queue, prediction, decision = ordered_nodes
    if decision != hero:
        raise RuntimeError(f"process terminal node {decision!r} must match visual hero {hero!r}")

    connector_ids = [
        oid for oid in group.get("member_ids", [])
        if objects.get(oid, {}).get("role") == "connector"
    ]
    if len(connector_ids) != 3:
        raise RuntimeError(f"process_story V0 expects three connectors; got {connector_ids}")
    c1, c2, c3 = connector_ids

    placements = [
        _text(title, "title", _box(0.052, 0.070, 0.55, 0.135), 26.5, 700),
        _text(subtitle, "subtitle", _box(0.052, 0.215, 0.50, 0.065), 12, 400, "muted"),

        _text(camera, "node", _box(0.105, 0.355, 0.30, 0.055), 15, 600),
        _text(queue, "node", _box(0.105, 0.495, 0.30, 0.055), 15, 600),
        _text(prediction, "node", _box(0.105, 0.635, 0.37, 0.090), 25, 700, "signal"),

        {"semantic_object_id": c1, "part": "connector", "kind": "line", "box": _box(0.075, 0.405, 0.004, 0.095), "color_token": "line"},
        {"semantic_object_id": c2, "part": "connector", "kind": "line", "box": _box(0.075, 0.545, 0.004, 0.095), "color_token": "line"},
        {"semantic_object_id": c3, "part": "connector", "kind": "line", "box": _box(0.430, 0.690, 0.205, 0.005), "color_token": "signal"},

        _text(decision, "node", _box(0.665, 0.300, 0.285, 0.120), 20, 700),
        {
            "semantic_object_id": screenshot,
            "part": "asset",
            "kind": "picture",
            "box": _box(0.705, 0.445, 0.215, 0.405),
            "asset_path": asset_path_for(screenshot),
            "fallback_fill_token": "surface",
        },
        _text(source, "source", _box(0.052, 0.935, 0.50, 0.030), 8.5, 400, "muted", valign="middle"),
    ]
    decorations = [
        {"decor_id": "top_signal_rule", "kind": "rect", "box": _box(0.052, 0.045, 0.10, 0.005), "fill_token": "signal", "line_token": None},
        {"decor_id": "signal_track", "kind": "rect", "box": _box(0.073, 0.350, 0.006, 0.385), "fill_token": "line", "line_token": None},
        {"decor_id": "camera_node", "kind": "ellipse", "box": _box(0.062, 0.365, 0.026, 0.046), "fill_token": "surface", "line_token": "line"},
        {"decor_id": "queue_node", "kind": "ellipse", "box": _box(0.062, 0.505, 0.026, 0.046), "fill_token": "surface", "line_token": "line"},
        {"decor_id": "prediction_node", "kind": "ellipse", "box": _box(0.060, 0.650, 0.030, 0.053), "fill_token": "signal", "line_token": None},
        {"decor_id": "product_destination_field", "kind": "rect", "box": _box(0.625, 0.250, 0.375, 0.660), "fill_token": "signal_soft", "line_token": None},
        {"decor_id": "product_destination_edge", "kind": "rect", "box": _box(0.625, 0.250, 0.006, 0.660), "fill_token": "signal", "line_token": None},
        {"decor_id": "decision_node", "kind": "ellipse", "box": _box(0.615, 0.672, 0.026, 0.046), "fill_token": "attention", "line_token": None},
        {"decor_id": "product_stage_rule", "kind": "rect", "box": _box(0.705, 0.870, 0.215, 0.004), "fill_token": "signal", "line_token": None},
    ]
    return placements, decorations


def solve_dominant_metric(ir, semantics, asset_path_for):
    del asset_path_for  # This archetype variant has no external asset.
    if ir["composition"]["variant"] != "hero_left_technical_proof_right_terminal_band":
        raise RuntimeError("unsupported dominant_metric variant")

    title = _single_semantic(semantics, "title")
    subtitle = _single_semantic(semantics, "subtitle")
    source = _single_semantic(semantics, "source_note")
    hero = _single_visual_semantic(ir, semantics, "hero", "metric")

    objects = _semantic_objects(semantics)
    primary_metrics = [
        oid for oid in _ids_by_visual_role(ir, "primary_support")
        if objects.get(oid, {}).get("role") == "metric"
    ]
    primary_metric = _single(primary_metrics, "primary supporting metric")
    terminal = _single([
        oid for oid in _ids_by_visual_role(ir, "primary_support")
        if objects.get(oid, {}).get("role") == "annotation"
    ], "primary terminal annotation")
    secondary_metrics = [
        oid for oid in _ids_by_visual_role(ir, "secondary_support")
        if objects.get(oid, {}).get("role") == "metric"
    ]
    if len(secondary_metrics) != 2:
        raise RuntimeError(f"dominant_metric V0 expects two secondary metrics; got {secondary_metrics}")
    s1, s2 = secondary_metrics

    placements = [
        _text(title, "title", _box(0.052, 0.105, 0.505, 0.145), 29, 700),
        _text(subtitle, "subtitle", _box(0.052, 0.285, 0.490, 0.085), 12.5, 400, "muted"),
        _text(hero, "value", _box(0.052, 0.475, 0.500, 0.225), 92, 700, "signal", valign="middle"),
        _text(hero, "label", _box(0.058, 0.715, 0.330, 0.060), 18, 600, source="label"),
        _text(primary_metric, "value", _box(0.700, 0.125, 0.245, 0.115), 42, 700, "on_dark", valign="middle"),
        _text(primary_metric, "label", _box(0.702, 0.245, 0.220, 0.050), 13, 500, "on_dark", source="label"),
        _text(s1, "value", _box(0.702, 0.390, 0.100, 0.075), 28, 700, "on_dark", valign="middle"),
        _text(s1, "label", _box(0.702, 0.468, 0.145, 0.042), 10.5, 400, "line", source="label"),
        _text(s2, "value", _box(0.855, 0.390, 0.080, 0.075), 28, 700, "on_dark", valign="middle"),
        _text(s2, "label", _box(0.855, 0.468, 0.110, 0.042), 10.5, 400, "line", source="label"),
        _text(terminal, "label", _box(0.702, 0.690, 0.245, 0.145), 16, 600, "on_dark"),
        _text(source, "source", _box(0.052, 0.935, 0.500, 0.030), 8.5, 400, "muted", valign="middle"),
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
    return placements, decorations


SOLVER_REGISTRY = {
    ("editorial_hero", "open_metric_left_edge_crop_right"): solve_editorial_hero,
    ("process_story", "signal_path_to_product_destination"): solve_process_story,
    ("dominant_metric", "hero_left_technical_proof_right_terminal_band"): solve_dominant_metric,
}
