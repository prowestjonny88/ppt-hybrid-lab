#!/usr/bin/env python3
import json
import math
import sys
from pathlib import Path

from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PPTX = ROOT / "dist/stage4/deck/queuezero_stage4_v0.pptx"
REAL = ROOT / "dist/stage4/deck/realizations.json"
EXPECTED_SLIDES = ["problem-hook", "how-it-works", "validation-traction"]
EMU_PER_INCH = 914400


def _max_font_pt(shape):
    sizes = []
    if not getattr(shape, "has_text_frame", False):
        return None
    for paragraph in shape.text_frame.paragraphs:
        for run in paragraph.runs:
            if run.font.size is not None:
                sizes.append(run.font.size.pt)
    return max(sizes) if sizes else None


def _estimated_required_height_in(shape):
    """Conservative wrap estimate for high-risk title-band text.

    This is deliberately a proxy, not a replacement for pixel review. It catches
    the exact failure class where the PowerPoint textbox bounds are valid but a
    renderer wraps glyphs beyond the intended title band and into the subtitle.
    """
    text = " ".join((shape.text or "").split())
    font_pt = _max_font_pt(shape)
    if not text or not font_pt:
        return 0.0
    width_in = shape.width / EMU_PER_INCH
    # Approximate average glyph width at 0.62 em, then add 20% line leading.
    chars_per_line = max(1, int((width_in * 72.0) / (font_pt * 0.62)))
    line_count = max(1, math.ceil(len(text) / chars_per_line))
    return line_count * font_pt * 1.20 / 72.0


def _check_title_band_capacity(slide, slide_id):
    risky = []
    for shape in slide.shapes:
        if not getattr(shape, "has_text_frame", False):
            continue
        if not (
            shape.name.endswith(":title:title")
            or shape.name.endswith(":subtitle:subtitle")
        ):
            continue
        required = _estimated_required_height_in(shape)
        available = shape.height / EMU_PER_INCH
        if required > available * 0.96:
            risky.append(
                f"{shape.name} requires~{required:.2f}in but box is {available:.2f}in"
            )
    if risky:
        raise SystemExit(
            f"title-band overflow risk on {slide_id}: " + "; ".join(risky)
        )


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
        _check_title_band_capacity(slide, realization["slide_id"])

    if len(all_names) < 20:
        raise SystemExit("deck unexpectedly sparse; structural realization likely incomplete")
    print("Stage 4 deck structural audit: PASS")


if __name__ == "__main__":
    main()
