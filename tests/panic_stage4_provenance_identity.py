#!/usr/bin/env python3
import copy
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.audit_stage4_deck import LAYOUT, REAL, PPTX, audit_deck


def _expect_rejection(realizations, layouts, expected):
    with tempfile.TemporaryDirectory(prefix="stage4-provenance-panic-") as tmp:
        tmp = Path(tmp)
        real_path = tmp / "realizations.json"
        layout_path = tmp / "layout_solutions.json"
        real_path.write_text(json.dumps(realizations, indent=2) + "\n", encoding="utf-8")
        layout_path.write_text(json.dumps(layouts, indent=2) + "\n", encoding="utf-8")
        try:
            audit_deck(PPTX, real_path, layout_path)
        except ValueError as exc:
            if expected not in str(exc):
                raise AssertionError(f"expected {expected!r}; got {exc!r}") from exc
            return
    raise AssertionError(f"invalid provenance unexpectedly accepted: {expected}")


def main():
    if not PPTX.is_file() or not REAL.is_file() or not LAYOUT.is_file():
        raise SystemExit("Stage 4 deck outputs missing; build deck before provenance panic suite")

    realizations = json.loads(REAL.read_text(encoding="utf-8"))
    layouts = json.loads(LAYOUT.read_text(encoding="utf-8"))
    audit_deck(PPTX, REAL, LAYOUT)

    bad_real = copy.deepcopy(realizations)
    bad_real["slides"][0]["visual_ir_hash"] = "0" * 64
    _expect_rejection(bad_real, layouts, "layout/realization provenance drift")

    bad_layout = copy.deepcopy(layouts)
    bad_layout[0]["semantic_hash"] = "1" * 64
    _expect_rejection(realizations, bad_layout, "layout/realization provenance drift")

    bad_real = copy.deepcopy(realizations)
    bad_layout = copy.deepcopy(layouts)
    bad_real["slides"][1]["style_profile_hash"] = "2" * 64
    bad_layout[1]["style_profile_hash"] = "2" * 64
    _expect_rejection(bad_real, bad_layout, "source/layout provenance drift")

    bad_real = copy.deepcopy(realizations)
    bad_layout = copy.deepcopy(layouts)
    bad_real["slides"][2]["variant"] = "tampered_variant"
    bad_layout[2]["variant"] = "tampered_variant"
    _expect_rejection(bad_real, bad_layout, "source/layout provenance drift")

    print("Stage 4 provenance identity fail-closed panic suite: PASS")


if __name__ == "__main__":
    main()
