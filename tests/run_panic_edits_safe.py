#!/usr/bin/env python3
"""Run the Stage 3 panic-edit suite without mutating unrelated XML during P6.

The original recolor helper walks python-pptx Font/fill/line objects. Some of
those accessors materialize formatting nodes as a side effect, which makes the
collateral-damage detector report false positives. This wrapper replaces only
existing a:srgbClr nodes in each shape's XML, so P6 measures the requested
accent edit rather than accessor normalization.
"""

import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

import run_panic_edits as panic  # noqa: E402


BLUE_HEX = "2563EB"
ORANGE_HEX = "F97316"


def recolor_blue_xml_only(prs):
    touched = set()
    for slide in prs.slides:
        for shape in slide.shapes:
            changed = False
            for elem in shape._element.iter():
                if not elem.tag.endswith("}srgbClr"):
                    continue
                value = (elem.get("val") or "").upper()
                if value == BLUE_HEX:
                    elem.set("val", ORANGE_HEX)
                    changed = True
            if changed:
                touched.add(shape.name)
    return touched


panic.recolor_blue = recolor_blue_xml_only


if __name__ == "__main__":
    panic.main()
