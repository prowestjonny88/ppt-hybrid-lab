#!/usr/bin/env python3
"""Generate Stage 3 visual benchmark assets with the pinned stable Gemini image model.

This script intentionally fails closed:
- only the pinned stable model is accepted;
- preview/latest/Imagen aliases are rejected;
- no automatic model fallback is allowed;
- exact prompt and image hashes are persisted for benchmark reproducibility.
"""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path

from google import genai


ROOT = Path(__file__).resolve().parents[1]
PINNED_MODEL = "gemini-3.1-flash-image"

JOBS = [
    {
        "kind": "image_first",
        "prompt": "dist/prompts/problem-hook.image_first.txt",
        "output": "image_first/problem_hook.png",
        "aspect_ratio": "16:9",
    },
    {
        "kind": "image_first",
        "prompt": "dist/prompts/how-it-works.image_first.txt",
        "output": "image_first/how_it_works.png",
        "aspect_ratio": "16:9",
    },
    {
        "kind": "image_first",
        "prompt": "dist/prompts/validation-traction.image_first.txt",
        "output": "image_first/validation_traction.png",
        "aspect_ratio": "16:9",
    },
    {
        "kind": "hybrid_bounded_asset",
        "prompt": "dist/prompts/problem-hook.problem_hero.hybrid.txt",
        "output": "hybrid/problem_hero.png",
        "aspect_ratio": "4:3",
    },
]


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def decode_image_data(data):
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return base64.b64decode(data)
    raise RuntimeError(f"unexpected Gemini image payload type: {type(data)!r}")


def serialize_usage(interaction):
    usage = getattr(interaction, "usage", None) or getattr(interaction, "usage_metadata", None)
    if usage is None:
        return None
    if hasattr(usage, "model_dump"):
        try:
            return usage.model_dump(mode="json")
        except TypeError:
            return usage.model_dump()
    if isinstance(usage, dict):
        return usage
    return str(usage)


def verify_model(client, model):
    if model != PINNED_MODEL:
        raise RuntimeError(
            f"Stage 3 is pinned to stable {PINNED_MODEL}; refusing unverified model {model!r}. "
            "Update the pin only after re-checking Google's current model/deprecation docs."
        )
    lowered = model.lower()
    if any(marker in lowered for marker in ("preview", "experimental", "-exp", "latest", "imagen")):
        raise RuntimeError(f"refusing non-stable or legacy image model identifier: {model}")

    info = client.models.get(model=model)
    resolved_name = getattr(info, "name", None) or getattr(info, "display_name", None) or str(info)
    print(f"Gemini model preflight OK: {resolved_name}")
    return resolved_name


def generate_one(client, model, prompt, aspect_ratio, image_size):
    interaction = client.interactions.create(
        model=model,
        input=prompt,
        response_format={
            "type": "image",
            "mime_type": "image/png",
            "aspect_ratio": aspect_ratio,
            "image_size": image_size,
        },
    )

    output_image = getattr(interaction, "output_image", None)
    if output_image is None or getattr(output_image, "data", None) is None:
        raise RuntimeError("Gemini returned no output_image data")

    raw = decode_image_data(output_image.data)
    if len(raw) < 1024:
        raise RuntimeError(f"Gemini image payload is unexpectedly small ({len(raw)} bytes)")

    return raw, {
        "interaction_id": getattr(interaction, "id", None),
        "output_text": getattr(interaction, "output_text", None),
        "usage": serialize_usage(interaction),
        "mime_type": getattr(output_image, "mime_type", None) or "image/png",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=PINNED_MODEL)
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing")

    client = genai.Client(api_key=api_key)
    resolved_model = verify_model(client, args.model)

    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": "stage3-gemini-image-generation-v1",
        "provider": "Google Gemini Developer API",
        "model": args.model,
        "resolved_model": resolved_model,
        "resolution": args.resolution,
        "fallback_allowed": False,
        "jobs": [],
    }

    for job in JOBS:
        prompt_path = ROOT / job["prompt"]
        if not prompt_path.exists():
            raise RuntimeError(f"missing deterministic prompt: {prompt_path}")
        prompt = prompt_path.read_text(encoding="utf-8").strip()
        out_path = output_dir / job["output"]
        out_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Generating {job['output']} ({job['aspect_ratio']}, {args.resolution})")
        raw, response_meta = generate_one(
            client,
            args.model,
            prompt,
            job["aspect_ratio"],
            args.resolution,
        )
        out_path.write_bytes(raw)

        manifest["jobs"].append(
            {
                "kind": job["kind"],
                "prompt_path": job["prompt"],
                "prompt_sha256": sha_text(prompt),
                "output_path": str(out_path.relative_to(ROOT)),
                "image_sha256": sha_bytes(raw),
                "image_bytes": len(raw),
                "aspect_ratio": job["aspect_ratio"],
                "image_size": args.resolution,
                "response": response_meta,
            }
        )

    manifest_path = output_dir / "generation_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated {len(JOBS)} assets; manifest: {manifest_path}")


if __name__ == "__main__":
    main()
