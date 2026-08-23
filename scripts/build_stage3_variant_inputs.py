#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ir.runtime import canonical_hash, load_json
from src.prompts.stage3 import bounded_asset_prompt, full_slide_image_prompt

PLAN_DIR = ROOT / "experiment" / "queuezero" / "render_plans"
OUT_DIR = ROOT / "dist" / "variant_inputs"
PROMPT_DIR = ROOT / "dist" / "prompts"


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def main():
    deck_path = ROOT / "experiment" / "queuezero" / "deck_system.stage3.json"
    registry_path = ROOT / "architecture" / "CAPABILITY_REGISTRY.stage3.json"
    deck = load_json(deck_path)
    registry = load_json(registry_path)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)

    manifests = []
    by_slide_hash = {}

    for plan_path in sorted(PLAN_DIR.glob("*.json")):
        plan = load_json(plan_path)
        semantic_path = ROOT / plan["semantic_file"]
        semantics = load_json(semantic_path)
        semantic_hash = canonical_hash(semantics)
        slide_id = plan["slide_id"]
        variant = plan["variant"]
        by_slide_hash.setdefault(slide_id, set()).add(semantic_hash)

        prompt_records = []
        if variant == "image_first":
            prompt = full_slide_image_prompt(semantics, deck)
            prompt_path = PROMPT_DIR / f"{slide_id}.image_first.txt"
            write_text(prompt_path, prompt)
            prompt_records.append({
                "kind": "full_slide_image",
                "path": str(prompt_path.relative_to(ROOT)),
                "sha256": sha_text(prompt),
            })
        elif variant == "hybrid":
            for asset in semantics.get("assets", []):
                if asset.get("kind") != "generated_visual":
                    continue
                prompt = bounded_asset_prompt(semantics, asset, deck)
                prompt_path = PROMPT_DIR / f"{slide_id}.{asset['asset_id']}.hybrid.txt"
                write_text(prompt_path, prompt)
                prompt_records.append({
                    "kind": "bounded_asset",
                    "asset_id": asset["asset_id"],
                    "path": str(prompt_path.relative_to(ROOT)),
                    "sha256": sha_text(prompt),
                })

        source_assets = []
        for asset in semantics.get("assets", []):
            source = (asset.get("current_instance") or {}).get("source")
            if source:
                path = ROOT / source
                source_assets.append({
                    "asset_id": asset["asset_id"],
                    "path": source,
                    "sha256": sha_file(path) if path.exists() else None,
                    "exists": path.exists(),
                })

        manifest = {
            "manifest_version": "stage3-variant-input-v1",
            "slide_id": slide_id,
            "variant": variant,
            "semantic_file": plan["semantic_file"],
            "semantic_hash": semantic_hash,
            "render_plan_file": str(plan_path.relative_to(ROOT)),
            "render_plan_hash": canonical_hash(plan),
            "deck_system_file": str(deck_path.relative_to(ROOT)),
            "deck_system_hash": canonical_hash(deck),
            "capability_registry_file": str(registry_path.relative_to(ROOT)),
            "capability_registry_hash": canonical_hash(registry),
            "prompts": prompt_records,
            "source_assets": source_assets,
        }
        out = OUT_DIR / f"{slide_id}.{variant}.manifest.json"
        out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        manifests.append(manifest)

    errors = []
    for slide_id, hashes in by_slide_hash.items():
        if len(hashes) != 1:
            errors.append(f"{slide_id}: variants do not share one semantic hash: {sorted(hashes)}")
    if len(manifests) != 9:
        errors.append(f"expected 9 variant manifests, got {len(manifests)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Built {len(manifests)} variant input manifests with semantic-hash parity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
