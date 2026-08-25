#!/usr/bin/env python3
"""Generate fresh Stage 4 full-slide visual-oracle images with a pinned model.

Paid calls are resumable and hash-checked. Existing verified outputs are skipped so
reruns do not duplicate spend. These images are art-direction evidence only.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path

from google import genai

ROOT = Path(__file__).resolve().parents[1]
PINNED_MODEL = "gemini-3.1-flash-image"
OUTPUT_MIME = "image/jpeg"
SLIDES = ["problem-hook", "how-it-works", "validation-traction"]


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def decode_image(data):
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return base64.b64decode(data)
    raise RuntimeError(f"unexpected image payload type: {type(data)!r}")


def usage_json(interaction):
    usage = getattr(interaction, "usage", None) or getattr(interaction, "usage_metadata", None)
    if usage is None:
        return None
    if hasattr(usage, "model_dump"):
        try:
            return usage.model_dump(mode="json")
        except TypeError:
            return usage.model_dump()
    return usage if isinstance(usage, dict) else str(usage)


def verify_model(client, model):
    if model != PINNED_MODEL:
        raise RuntimeError(f"refusing unverified model {model!r}; pinned model is {PINNED_MODEL}")
    if any(x in model.lower() for x in ("preview", "experimental", "latest", "imagen")):
        raise RuntimeError(f"refusing unstable/legacy image model identifier: {model}")
    info = client.models.get(model=model)
    return getattr(info, "name", None) or str(info)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model", default=PINNED_MODEL)
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing")
    client = genai.Client(api_key=api_key)
    resolved = verify_model(client, args.model)

    prompt_root = ROOT / "dist/stage4/oracle/prompts"
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "generation_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {
            "schema_version": "stage4-visual-oracle-generation-v1",
            "semantic_authority": false,
            "provider": "Google Gemini Developer API",
            "model": args.model,
            "resolved_model": resolved,
            "resolution": args.resolution,
            "output_mime_type": OUTPUT_MIME,
            "jobs": [],
            "complete": false if False else False
        }

    if manifest.get("model") != args.model or manifest.get("resolution") != args.resolution:
        raise RuntimeError("existing oracle manifest model/resolution mismatch; use a new generation directory")

    records = {r.get("slide_id"): r for r in manifest.get("jobs", [])}
    for slide_id in SLIDES:
        prompt_path = prompt_root / f"{slide_id}.txt"
        if not prompt_path.is_file():
            raise RuntimeError(f"missing deterministic oracle prompt: {prompt_path}")
        prompt = prompt_path.read_text(encoding="utf-8").strip()
        prompt_sha = sha_bytes(prompt.encode("utf-8"))
        output_path = out / f"{slide_id}.jpg"
        existing = records.get(slide_id)
        if (
            existing
            and existing.get("status") == "success"
            and existing.get("prompt_sha256") == prompt_sha
            and output_path.is_file()
            and existing.get("image_sha256") == sha_bytes(output_path.read_bytes())
        ):
            print(f"SKIP verified paid oracle: {slide_id}")
            continue

        interaction = client.interactions.create(
            model=args.model,
            input=prompt,
            response_format={
                "type": "image",
                "mime_type": OUTPUT_MIME,
                "aspect_ratio": "16:9",
                "image_size": args.resolution,
            },
        )
        output_image = getattr(interaction, "output_image", None)
        if output_image is None or getattr(output_image, "data", None) is None:
            raise RuntimeError(f"Gemini returned no image for {slide_id}")
        raw = decode_image(output_image.data)
        if len(raw) < 1024 or not raw.startswith(b"\xff\xd8"):
            raise RuntimeError(f"invalid JPEG oracle output for {slide_id}")
        output_path.write_bytes(raw)
        records[slide_id] = {
            "slide_id": slide_id,
            "status": "success",
            "prompt_path": str(prompt_path.relative_to(ROOT)),
            "prompt_sha256": prompt_sha,
            "output_path": str(output_path.relative_to(ROOT)),
            "image_sha256": sha_bytes(raw),
            "image_bytes": len(raw),
            "aspect_ratio": "16:9",
            "image_size": args.resolution,
            "interaction_id": getattr(interaction, "id", None),
            "usage": usage_json(interaction),
        }
        manifest["jobs"] = [records[x] for x in SLIDES if x in records]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    manifest["jobs"] = [records[x] for x in SLIDES if x in records]
    manifest["complete"] = all(records.get(x, {}).get("status") == "success" for x in SLIDES)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if not manifest["complete"]:
        raise RuntimeError("visual-oracle generation incomplete")
    print(f"Verified {len(SLIDES)} fresh Stage 4 visual oracles -> {manifest_path}")


if __name__ == "__main__":
    main()
