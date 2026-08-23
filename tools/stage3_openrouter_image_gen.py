#!/usr/bin/env python3
"""Generate the paid Stage 3 visual-baseline assets through OpenRouter.

This tool is intentionally outside the normal validation workflow. It reads the
already-derived Stage 3 prompt files, calls OpenRouter's dedicated /images API,
and writes PNGs plus a provenance manifest. It never prints or stores the API
key.
"""

import argparse
import hashlib
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

ASSETS = [
    {
        "kind": "image_first",
        "prompt": "problem-hook.image_first.txt",
        "output": "image_first/problem_hook.png",
        "aspect_ratio": "16:9",
        "slide_id": "problem-hook",
    },
    {
        "kind": "image_first",
        "prompt": "how-it-works.image_first.txt",
        "output": "image_first/how_it_works.png",
        "aspect_ratio": "16:9",
        "slide_id": "how-it-works",
    },
    {
        "kind": "image_first",
        "prompt": "validation-traction.image_first.txt",
        "output": "image_first/validation_traction.png",
        "aspect_ratio": "16:9",
        "slide_id": "validation-traction",
    },
    {
        "kind": "hybrid_bounded_asset",
        "prompt": "problem-hook.problem_hero.hybrid.txt",
        "output": "hybrid/problem_hero.png",
        "aspect_ratio": "4:3",
        "slide_id": "problem-hook",
        "asset_id": "problem_hero",
    },
]


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_text(value):
    return sha_bytes(value.encode("utf-8"))


def image_request(base_url, api_key, model, prompt, aspect_ratio, resolution):
    payload = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "n": 1,
    }
    if resolution:
        payload["resolution"] = resolution

    response = requests.post(
        base_url.rstrip("/") + "/images",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=900,
    )
    if not response.ok:
        raise RuntimeError(
            f"OpenRouter image request failed ({response.status_code}): "
            f"{response.text[:3000]}"
        )
    data = response.json()
    images = data.get("data") or []
    if not images or not images[0].get("b64_json"):
        raise RuntimeError(
            "OpenRouter image response did not contain data[0].b64_json: "
            + json.dumps({k: v for k, v in data.items() if k != "data"})[:3000]
        )
    return data


def save_png(b64_json, destination):
    import base64

    raw = base64.b64decode(b64_json)
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, format="PNG", optimize=True)
    return {
        "width": image.width,
        "height": image.height,
        "sha256": sha_bytes(destination.read_bytes()),
        "bytes": destination.stat().st_size,
    }


def sanitize_usage(usage):
    if not isinstance(usage, dict):
        return usage
    allowed = {
        "cost",
        "total_cost",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "input_tokens",
        "output_tokens",
        "images",
    }
    return {k: v for k, v in usage.items() if k in allowed}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--resolution", default="2K")
    parser.add_argument("--prompt-dir", default="dist/prompts")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not set")

    prompt_dir = ROOT / args.prompt_dir
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": "stage3-openrouter-image-generation-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "resolution": args.resolution,
        "base_url": args.base_url,
        "assets": [],
    }

    for spec in ASSETS:
        prompt_path = prompt_dir / spec["prompt"]
        if not prompt_path.exists():
            raise RuntimeError(f"missing derived prompt: {prompt_path}")
        prompt = prompt_path.read_text(encoding="utf-8").strip()
        print(f"Generating {spec['output']} with {args.model} ({spec['aspect_ratio']})")
        result = image_request(
            args.base_url,
            api_key,
            args.model,
            prompt,
            spec["aspect_ratio"],
            args.resolution,
        )
        image_info = save_png(
            result["data"][0]["b64_json"],
            output_dir / spec["output"],
        )
        record = {
            **{k: v for k, v in spec.items() if k != "prompt"},
            "prompt_file": str(prompt_path.relative_to(ROOT)),
            "prompt_sha256": sha_text(prompt),
            "model": args.model,
            "resolution": args.resolution,
            "image": image_info,
            "usage": sanitize_usage(result.get("usage")),
        }
        manifest["assets"].append(record)

    manifest_path = output_dir / "generation_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
