#!/usr/bin/env python3
import argparse
from pathlib import Path

from src.native.queuezero_renderer import build_native_vector


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="dist/queuezero_native_vector.pptx")
    parser.add_argument("--realizations", default="dist/realizations/native_vector")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output, realizations = build_native_vector(root, root / args.out, root / args.realizations)
    print(f"Built {output}")
    print(f"Realizations: {len(realizations)} slides")


if __name__ == "__main__":
    main()
