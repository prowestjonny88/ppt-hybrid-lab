#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ir.runtime import load_json
from src.visual_ir.compiler import compile_slide
from src.visual_ir.style_runtime import resolve_style_profile

PROFILE_PATH = ROOT / "experiment/queuezero/style_profiles/queuezero_hackathon_v0.json"
VISUAL_IR_DIR = ROOT / "experiment/queuezero/visual_ir"

GENERIC_FIELDS_FORBIDDEN_IN_PROFILE = {
    "forbidden_aesthetics",
    "typography",
    "whitespace",
    "geometry",
    "depth",
    "identity_anchors",
    "density_rules",
    "variation_rules",
    "anti_repetition_rules",
    "archetype_compatibility",
}

REQUIRED_RESOLVED_FIELDS = {
    "typography",
    "whitespace",
    "geometry",
    "depth",
    "identity_anchors",
    "density_rules",
    "variation_rules",
    "anti_repetition_rules",
    "archetype_compatibility",
    "palette",
    "image_treatment",
}

REQUIRED_PALETTE_TOKENS = {
    "canvas", "surface", "ink", "muted", "line", "signal", "signal_soft",
    "dark_field", "on_dark", "attention", "pending",
}


def main():
    resolved, profile, language = resolve_style_profile(ROOT, PROFILE_PATH)

    if profile.get("design_language_ref") != language.get("design_language_id"):
        raise SystemExit("DeckStyleProfile does not resolve to its declared DesignLanguage")

    duplicated = sorted(GENERIC_FIELDS_FORBIDDEN_IN_PROFILE & set(profile))
    if duplicated:
        raise SystemExit(f"DeckStyleProfile duplicated generic DesignLanguage fields: {duplicated}")

    missing = sorted(REQUIRED_RESOLVED_FIELDS - set(resolved))
    if missing:
        raise SystemExit(f"resolved style missing required fields: {missing}")

    palette_missing = sorted(REQUIRED_PALETTE_TOKENS - set(resolved.get("palette", {})))
    if palette_missing:
        raise SystemExit(f"resolved style missing palette tokens: {palette_missing}")

    active_anchors = {item["anchor_id"] for item in resolved.get("identity_anchors", [])}
    for path in sorted(VISUAL_IR_DIR.glob("*.stage4.v0.json")):
        ir = load_json(path)
        requested = set(ir.get("style", {}).get("identity_anchor_refs", []))
        unknown = sorted(requested - active_anchors)
        if unknown:
            raise SystemExit(f"{path.name}: inactive/unknown identity anchors {unknown}")

        solution = compile_slide(ROOT, path)
        if solution.get("design_language_id") != language["design_language_id"]:
            raise SystemExit(f"{path.name}: compiled solution lost design-language provenance")
        if solution.get("style_profile_id") != profile["profile_id"]:
            raise SystemExit(f"{path.name}: compiled solution lost style-profile provenance")

        for placement in solution.get("placements", []):
            token = placement.get("color_token")
            fallback = placement.get("fallback_fill_token")
            for value in (token, fallback):
                if value and value not in resolved["palette"]:
                    raise SystemExit(f"{path.name}: placement references unknown palette token {value!r}")
        for decor in solution.get("decorations", []):
            for key in ("fill_token", "line_token"):
                value = decor.get(key)
                if value and value not in resolved["palette"]:
                    raise SystemExit(f"{path.name}: decoration references unknown palette token {value!r}")

    print(
        "Stage 4 style layering: PASS "
        f"design_language={language['design_language_id']} profile={profile['profile_id']}"
    )


if __name__ == "__main__":
    main()
