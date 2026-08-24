#!/usr/bin/env python3
"""Resolve reusable Stage 4 DesignLanguage into a deck-specific style profile."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from src.ir.runtime import load_json

DESIGN_LANGUAGES_PATH = "architecture/DESIGN_LANGUAGES.stage4.v0.json"


def _deep_merge(base, override):
    if isinstance(base, dict) and isinstance(override, dict):
        merged = deepcopy(base)
        for key, value in override.items():
            if key in merged:
                merged[key] = _deep_merge(merged[key], value)
            else:
                merged[key] = deepcopy(value)
        return merged
    # Lists are intentional whole-field declarations, not append semantics.
    return deepcopy(override)


def load_design_language_registry(root: Path):
    data = load_json(Path(root) / DESIGN_LANGUAGES_PATH)
    return {
        item["design_language_id"]: item
        for item in data.get("design_languages", [])
    }


def resolve_style_profile(root: Path, profile_path: Path):
    root = Path(root)
    profile_path = Path(profile_path)
    profile = load_json(profile_path)
    language_id = profile.get("design_language_ref")
    if not language_id:
        raise RuntimeError(f"style profile {profile_path} missing design_language_ref")

    registry = load_design_language_registry(root)
    language = registry.get(language_id)
    if language is None:
        raise RuntimeError(f"unknown design_language_ref {language_id!r}")

    resolved = _deep_merge(language, profile)
    resolved["design_language_id"] = language_id
    resolved["design_language_ref"] = language_id
    resolved["profile_id"] = profile["profile_id"]
    resolved["style_provenance"] = {
        "design_language": DESIGN_LANGUAGES_PATH,
        "profile": profile_path.relative_to(root).as_posix() if profile_path.is_relative_to(root) else str(profile_path),
    }

    active = profile.get("active_identity_anchors")
    if active is not None:
        anchor_map = {item["anchor_id"]: item for item in language.get("identity_anchors", [])}
        missing = sorted(set(active) - set(anchor_map))
        if missing:
            raise RuntimeError(f"style profile requests unknown identity anchors: {missing}")
        resolved["identity_anchors"] = [anchor_map[anchor_id] for anchor_id in active]

    return resolved, profile, language
