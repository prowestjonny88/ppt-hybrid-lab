#!/usr/bin/env python3
import argparse
from pathlib import Path

from src.image_first.package import build_image_first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets-dir", required=True)
    parser.add_argument("--out", default="dist/queuezero_image_first.pptx")
    parser.add_argument("--manifest", default="dist/realizations/image_first/package_manifest.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output, _ = build_image_first(root, root / args.assets_dir, root / args.out, root / args.manifest)
    print(f"Built {output}")


if __name__ == "__main__":
    main()
