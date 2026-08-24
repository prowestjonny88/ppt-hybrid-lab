#!/usr/bin/env python3
"""Negative regressions for reusable Stage 4 archetype solver contracts.

These tests deliberately corrupt semantic/Visual IR inputs and require the
reusable composition solvers to fail closed rather than emit a plausible but
semantically invalid layout.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ir.runtime import load_json
from src.visual_ir.archetype_solvers import SOLVER_REGISTRY

CASES = {
    "editorial_hero": (
        ROOT / "experiment/queuezero/visual_ir/problem_hook.stage4.v0.json",
        ROOT / "experiment/queuezero/slide_semantics/problem_hook.v1.json",
    ),
    "process_story": (
        ROOT / "experiment/queuezero/visual_ir/how_it_works.stage4.v0.json",
        ROOT / "experiment/queuezero/slide_semantics/how_it_works.v1.json",
    ),
    "dominant_metric": (
        ROOT / "experiment/queuezero/visual_ir/validation_traction.stage4.v0.json",
        ROOT / "experiment/queuezero/slide_semantics/validation_traction.v1.json",
    ),
}


def _solver(ir):
    key = (ir["composition"]["archetype_id"], ir["composition"]["variant"])
    return SOLVER_REGISTRY[key]


def _asset(_object_id):
    return "tests/fixture-not-required.png"


def _must_fail(label, fn):
    try:
        fn()
    except (RuntimeError, KeyError, ValueError):
        return
    raise SystemExit(f"solver panic failed closed contract: {label}")


def _remove_first_role(semantics, role):
    data = deepcopy(semantics)
    for idx, obj in enumerate(data.get("semantic_objects", [])):
        if obj.get("role") == role:
            del data["semantic_objects"][idx]
            return data
    raise SystemExit(f"test fixture missing semantic role {role!r}")


def main():
    fixtures = {}
    for name, (ir_path, sem_path) in CASES.items():
        fixtures[name] = (load_json(ir_path), load_json(sem_path))

    # Every currently proven solver must reject an unknown variant even when the
    # rest of the semantic payload is otherwise valid.
    for name, (ir, semantics) in fixtures.items():
        bad = deepcopy(ir)
        bad["composition"]["variant"] = "panic_unknown_variant"
        solver = SOLVER_REGISTRY[(ir["composition"]["archetype_id"], ir["composition"]["variant"])]
        _must_fail(
            f"{name}: unknown variant",
            lambda solver=solver, bad=bad, semantics=semantics: solver(bad, semantics, _asset),
        )

    # Editorial hero requires one real annotation and must not silently repurpose
    # another object when that role disappears.
    ir, semantics = fixtures["editorial_hero"]
    missing_annotation = _remove_first_role(semantics, "annotation")
    _must_fail(
        "editorial_hero: missing annotation role",
        lambda: _solver(ir)(ir, missing_annotation, _asset),
    )

    # Process story V0 is a four-node ordered transformation with three explicit
    # connectors. Removing either topology element must be a hard failure.
    ir, semantics = fixtures["process_story"]
    missing_connector = _remove_first_role(semantics, "connector")
    _must_fail(
        "process_story: missing connector",
        lambda: _solver(ir)(ir, missing_connector, _asset),
    )
    missing_node = _remove_first_role(semantics, "diagram_node")
    _must_fail(
        "process_story: missing ordered node",
        lambda: _solver(ir)(ir, missing_node, _asset),
    )

    # Dominant metric requires the declared evidence hierarchy. Removing a metric
    # must not collapse into a generic two-metric arrangement.
    ir, semantics = fixtures["dominant_metric"]
    missing_metric = _remove_first_role(semantics, "metric")
    _must_fail(
        "dominant_metric: missing metric",
        lambda: _solver(ir)(ir, missing_metric, _asset),
    )

    print("Stage 4 solver contract panic suite: PASS")


if __name__ == "__main__":
    main()
