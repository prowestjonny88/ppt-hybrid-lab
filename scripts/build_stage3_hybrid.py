#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.hybrid.queuezero_renderer import build_hybrid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ppt-master-root", required=True)
    parser.add_argument("--out", default="dist/queuezero_hybrid.pptx")
    parser.add_argument("--realizations", default="dist/realizations/hybrid")
    parser.add_argument("--adapter-workspace", default="dist/ppt_master_adapter_workspace")
    parser.add_argument(
        "--hero-asset",
        default=None,
        help="Optional real generated bounded Problem hero; omitted for structural CI fixture.",
    )
    args = parser.parse_args()
    hero_asset = Path(args.hero_asset) if args.hero_asset else None
    output, realizations = build_hybrid(
        ROOT,
        Path(args.ppt_master_root),
        ROOT / args.out,
        ROOT / args.realizations,
        ROOT / args.adapter_workspace,
        hero_asset=hero_asset,
    )
    print(f"Built {output}")
    print(f"Hybrid realizations: {len(realizations)} slides")
    if hero_asset:
        print(f"Hybrid visual benchmark hero: {hero_asset}")


if __name__ == "__main__":
    main()
