#!/usr/bin/env python3
"""Fail-closed regression tests for Stage 4 asset binding resolution."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from src.visual_ir.compiler import ASSET_BINDINGS_PATH, _asset_resolver


def _write_bindings(root: Path, bindings: dict) -> None:
    path = root / ASSET_BINDINGS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema_version": "stage4-asset-bindings-v0", "bindings": bindings}),
        encoding="utf-8",
    )


def main() -> None:
    ir = {"slide_id": "sample-slide"}

    with tempfile.TemporaryDirectory(prefix="stage4-asset-panic-") as tmp:
        root = Path(tmp)

        # Explicit benchmark binding must win over semantic current_instance.
        _write_bindings(root, {"sample-slide": {"hero": "explicit/hero.png"}})
        semantics = {
            "assets": [
                {
                    "semantic_object_id": "hero",
                    "current_instance": {"source": "semantic/hero.png"},
                }
            ]
        }
        resolve = _asset_resolver(root, ir, semantics)
        assert resolve("hero") == "explicit/hero.png"

        # Missing explicit binding must fall back to semantic asset source.
        _write_bindings(root, {})
        resolve = _asset_resolver(root, ir, semantics)
        assert resolve("hero") == "semantic/hero.png"

        # Missing both explicit and semantic sources must fail closed.
        resolve = _asset_resolver(root, ir, {"assets": []})
        try:
            resolve("hero")
        except RuntimeError as exc:
            msg = str(exc)
            assert "no concrete asset binding" in msg
            assert "sample-slide" in msg and "hero" in msg
        else:
            raise AssertionError("missing required asset unexpectedly resolved")

        # A binding for a different slide must never leak across slide identity.
        _write_bindings(root, {"other-slide": {"hero": "wrong/hero.png"}})
        resolve = _asset_resolver(root, ir, {"assets": []})
        try:
            resolve("hero")
        except RuntimeError:
            pass
        else:
            raise AssertionError("cross-slide asset binding leakage was not rejected")

    print("Stage 4 asset binding panic suite: PASS")


if __name__ == "__main__":
    main()
