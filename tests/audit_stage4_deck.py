#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PPTX = ROOT / "dist/stage4/deck/queuezero_stage4_v0.pptx"
REAL = ROOT / "dist/stage4/deck/realizations.json"
EXPECTED_SLIDES = ["problem-hook", "how-it-works", "validation-traction"]


def main():
    if not PPTX.is_file() or not REAL.is_file():
        raise SystemExit("Stage 4 deck outputs missing")
    prs = Presentation(PPTX)
    data = json.loads(REAL.read_text(encoding="utf-8"))
    if len(prs.slides) != 3 or data.get("slide_count") != 3:
        raise SystemExit("Stage 4 deck must contain exactly three slides")
    ids = [s["slide_id"] for s in data["slides"]]
    if ids != EXPECTED_SLIDES:
        raise SystemExit(f"unexpected slide order: {ids}")

    all_names = []
    for slide, realization in zip(prs.slides, data["slides"]):
        names = [shape.name for shape in slide.shapes]
        if len(names) != len(set(names)):
            raise SystemExit(f"duplicate PowerPoint shape names on {realization['slide_id']}")
        if not any(name.startswith(f"oxq:{realization['slide_id']}:") for name in names):
            raise SystemExit(f"missing semantic identity on {realization['slide_id']}")
        all_names.extend(names)
        for obj in realization["objects"]:
            if obj["kind"] == "picture" and not obj.get("asset_present"):
                raise SystemExit(f"required visual asset missing: {obj.get('asset_path')}")

    if len(all_names) < 20:
        raise SystemExit("deck unexpectedly sparse; structural realization likely incomplete")
    print("Stage 4 deck structural audit: PASS")


if __name__ == "__main__":
    main()
