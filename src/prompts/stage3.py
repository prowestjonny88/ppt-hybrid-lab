import json

from src.ir.runtime import evidence_index, object_index, resolve_template, resolved_object_text


def _guardrails(semantics):
    lines = []
    for item in semantics.get("forbidden_implications", []):
        if item.get("forbidden_claim"):
            lines.append(f"- Do NOT imply: {item['forbidden_claim']}")
        for depiction in item.get("forbidden_depictions", []):
            lines.append(f"- Do NOT depict: {depiction}")
    return lines


def _evidence_lines(semantics):
    lines = []
    for item in semantics.get("evidence", []):
        statement = resolve_template(item.get("statement_template", ""), semantics)
        if statement:
            lines.append(f"- [{item['status']}] {statement}")
        for boundary in item.get("does_not_prove", []):
            lines.append(f"  Boundary: does not prove {boundary}.")
    return lines


def _semantic_text_lines(semantics):
    lines = []
    for obj in semantics.get("semantic_objects", []):
        if obj.get("role") in {"hero_visual_slot", "image_slot", "logo_slot", "connector"}:
            continue
        text = resolved_object_text(obj, semantics)
        if text:
            label = obj.get("label")
            rendered = f"{text} — {label}" if label else text
            lines.append(f"- {obj['object_id']} ({obj['role']}): {rendered}")
    return lines


def full_slide_image_prompt(semantics, deck_system):
    proof = semantics.get("proof_object", {})
    hierarchy = semantics.get("hierarchy", {})
    title = resolved_object_text(object_index(semantics)["title"], semantics)
    subtitle_obj = object_index(semantics).get("subtitle")
    subtitle = resolved_object_text(subtitle_obj, semantics) if subtitle_obj else ""
    token_summary = ", ".join(f"{k}={v}" for k, v in deck_system["tokens"].items())

    sections = [
        "Create ONE complete 16:9 hackathon pitch slide as a full-slide image baseline.",
        "This is a controlled architecture benchmark. Preserve all supplied semantics exactly; do not add facts, metrics, claims, labels, badges, or validation status.",
        "",
        f"SLIDE ROLE: {semantics['page_role']}",
        f"GOVERNING CLAIM: {semantics['governing_claim']}",
        f"ACTION TITLE (exact text): {title}",
        f"SUBTITLE (exact text): {subtitle}" if subtitle else "SUBTITLE: none",
        f"WHY IT MATTERS: {semantics.get('why_it_matters','')}",
        "",
        f"PROOF OBJECT: {proof.get('type','')}",
        f"PROOF LOGIC: {proof.get('logic','')}",
        "",
        "EXACT SEMANTIC TEXT / METRICS:",
        *_semantic_text_lines(semantics),
        "",
        "EVIDENCE BOUNDARY:",
        *_evidence_lines(semantics),
        "",
        "VISUAL SEMANTIC GUARDRAILS:",
        *_guardrails(semantics),
        "",
        "HIERARCHY: action title is the single highest-priority conclusion; the proof object is the visual protagonist; source notes are low-weight. Do not create a second title-like conclusion or detached KPI rail.",
        "STYLE: polished modern hackathon pitch deck, strong information hierarchy, premium editorial composition, selective depth, not a generic dashboard/card grid.",
        f"PALETTE TOKENS: {token_summary}",
        "OUTPUT: full-bleed 16:9 slide image only. All visible slide text must use the exact supplied wording."
    ]
    return "\n".join(sections)


def bounded_asset_prompt(semantics, asset, deck_system):
    region = next(r for r in semantics["regions"] if r["region_id"] == asset["region_ref"])
    parts = [
        "Create ONE bounded visual asset for a hybrid PowerPoint slide, NOT a complete slide.",
        f"Slide role: {semantics['page_role']}",
        f"Asset slot: {asset['asset_id']}",
        f"Target aspect ratio: {asset['aspect_ratio']}",
        f"Target normalized region: {json.dumps(region['rect'], sort_keys=True)}",
        f"Composition anchor: {asset.get('composition_anchor','center')}",
        "The asset MUST contain NO slide typography, labels, metrics, captions, UI copy, logos, or readable signage." if asset.get("text_free") else "Do not invent claims or metrics inside the asset.",
        "The native PowerPoint layer will supply all information-bearing text and numbers.",
        "Visual style: premium hackathon presentation visual, coherent with a clean modern product pitch, realistic enough to carry first-impression quality without looking like stock art.",
        f"Palette references: {', '.join(asset.get('palette_token_refs', [])) or 'none'}",
    ]
    for item in asset.get("forbidden_depictions", []):
        parts.append(f"Do NOT depict: {item}")
    parts.extend(_guardrails(semantics))
    return "\n".join(parts)
