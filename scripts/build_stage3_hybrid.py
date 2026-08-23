#!/usr/bin/env python3
import argparse
from pathlib import Path

from src.hybrid.queuezero_renderer import build_hybrid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ppt-master-root", required=True)
    parser.add_argument("--out", default="dist/queuezero_hybrid.pptx")
    parser.add_argument("--realizations", default="dist/realizations/hybrid")
    parser.add_argument("--adapter-workspace", default="dist/ppt_master_adapter_workspace")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output, realizations = build_hybrid(
        root,
        Path(args.ppt_master_root),
        root / args.out,
        root / args.realizations,
        root / args.adapter_workspace,
    )
    print(f"Built {output}")
    print(f"Hybrid realizations: {len(realizations)} slides")


if __name__ == "__main__":
    main()
