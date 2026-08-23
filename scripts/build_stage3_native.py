#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.native.queuezero_renderer import build_native_vector


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="dist/queuezero_native_vector.pptx")
    parser.add_argument("--realizations", default="dist/realizations/native_vector")
    args = parser.parse_args()
    output, realizations = build_native_vector(ROOT, ROOT / args.out, ROOT / args.realizations)
    print(f"Built {output}")
    print(f"Realizations: {len(realizations)} slides")


if __name__ == "__main__":
    main()
