#!/usr/bin/env python3
"""Fail-closed regression cases for Stage 4 design-language/profile resolution."""

from __future__ import annotations

import json
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ir.runtime import load_json
from src.visual_ir.style_runtime import resolve_style_profile

PROFILE_PATH = ROOT / "experiment/queuezero/style_profiles/queuezero_hackathon_v0.json"


def _expect_runtime_error(profile: dict, expected_fragment: str) -> None:
    with tempfile.TemporaryDirectory(prefix="stage4-style-panic-", dir=ROOT) as tmp:
        path = Path(tmp) / "profile.json"
        path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
        try:
            resolve_style_profile(ROOT, path)
        except RuntimeError as exc:
            if expected_fragment not in str(exc):
                raise SystemExit(
                    f"wrong fail-closed error: expected {expected_fragment!r}, got {str(exc)!r}"
                ) from exc
        else:
            raise SystemExit(f"style resolver unexpectedly accepted invalid profile: {expected_fragment}")


def main() -> None:
    base = load_json(PROFILE_PATH)

    missing_ref = deepcopy(base)
    missing_ref.pop("design_language_ref", None)
    _expect_runtime_error(missing_ref, "missing design_language_ref")

    unknown_ref = deepcopy(base)
    unknown_ref["design_language_ref"] = "does-not-exist"
    _expect_runtime_error(unknown_ref, "unknown design_language_ref")

    unknown_anchor = deepcopy(base)
    unknown_anchor["active_identity_anchors"] = ["definitely-not-an-anchor"]
    _expect_runtime_error(unknown_anchor, "unknown identity anchors")

    print("Stage 4 style-layering panic suite: PASS")


if __name__ == "__main__":
    main()
