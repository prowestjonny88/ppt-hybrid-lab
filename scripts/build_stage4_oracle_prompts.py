#!/usr/bin/env python3
"""Build deterministic full-slide visual-oracle prompts from frozen semantic IR.

The image oracle is art direction only. Semantic IR remains authoritative; prompts
therefore enumerate exact allowed strings and forbidden implications explicitly.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ir.runtime import load_json, resolved_object_text

SLIDES = [
    "experiment/queuezero/slide_semantics/problem_hook.v1.json",
    "experiment/queuezero/slide_semantics/how_it_works.v1.json",
    "experiment/queuezero/slide_semantics/validation_traction.v1.json",
]
OUT = ROOT / "dist/stage4/oracle/prompts"


def allowed_text(semantics):
    values = []
    for obj in semantics.get("semantic_objects", []):
        role = obj.get("role")
        if role in {"hero_visual_slot", "image_slot", "connector"}:
            continue
        try:
            text = resolved_object_text(obj, semantics)
        except Exception:
            text = obj.get("content") or obj.get("label")
        if text:
            values.append({"object_id": obj["object_id"], "role": role, "text": text})
        label = obj.get("label")
        if label and label != text:
            values.append({"object_id": obj["object_id"], "role": f"{role}_label", "text": label})
    return values


def build_prompt(semantics):
    exact_text = allowed_text(semantics)
    forbidden = semantics.get("forbidden_implications", [])
    payload = {
        "slide_id": semantics["slide_id"],
        "page_role": semantics["page_role"],
        "governing_claim": semantics.get("governing_claim"),
        "why_it_matters": semantics.get("why_it_matters"),
        "exact_allowed_slide_text": exact_text,
        "forbidden_implications": forbidden,
    }
    return f"""Create a single exceptionally polished 16:9 presentation-slide concept image for a high-stakes hackathon/startup pitch deck.

This image is a VISUAL ORACLE: maximize composition quality, visual hierarchy, typography, art direction, spatial rhythm, and memorable presentation impact. Do not imitate generic PowerPoint card grids. Favor one obvious visual protagonist, asymmetric editorial composition where appropriate, deliberate whitespace, and sophisticated but restrained graphic language. The result should feel competitive with best-in-class AI presentation products.

IMPORTANT SEMANTIC CONTRACT:
- The JSON payload below is the only factual source of truth.
- Do not invent metrics, claims, logos, certifications, badges, product capabilities, or sources.
- Do not add any readable text except strings listed in exact_allowed_slide_text.
- You may choose not to show low-priority allowed strings if the composition benefits, but never paraphrase or invent replacements.
- Treat forbidden_implications as strict exclusions.
- This image will later be reconstructed into editable PowerPoint objects, so maintain clear visual regions and separable design layers rather than relying on impossible photorealistic text effects.
- Do NOT optimize for editability now; optimize for the visual ceiling. The reconstruction system will separately preserve editability.

SEMANTIC PAYLOAD:
{json.dumps(payload, indent=2, ensure_ascii=False)}

Return only the slide image, edge-to-edge 16:9, with no surrounding device mockup, watermark, commentary, or presentation frame.
""".strip() + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": "stage4-oracle-prompts-v1", "prompts": []}
    for rel in SLIDES:
        semantics = load_json(ROOT / rel)
        text = build_prompt(semantics)
        path = OUT / f"{semantics['slide_id']}.txt"
        path.write_text(text, encoding="utf-8")
        manifest["prompts"].append({
            "slide_id": semantics["slide_id"],
            "semantic_file": rel,
            "prompt_file": str(path.relative_to(ROOT)),
            "prompt_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        })
    manifest_path = OUT.parent / "prompt_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(manifest['prompts'])} Stage 4 oracle prompts -> {manifest_path}")


if __name__ == "__main__":
    main()
