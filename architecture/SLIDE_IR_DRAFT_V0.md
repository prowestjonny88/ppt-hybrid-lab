# Stage 3 Experimental Slide IR — Draft V0

> Status: **DRAFT FOR RED-TEAMING**. This is not frozen product architecture.
>
> Purpose: provide one renderer-agnostic semantic representation that can drive the image-first, native/vector, and hybrid variants of the controlled QueueZero experiment.

## 1. Core design rule

The IR must preserve this traceable chain:

```text
SOURCE FACT / USER INPUT
        ↓
SEMANTIC OBJECT
        ↓
VISUAL OBJECT / RELATIONSHIP
        ↓
RENDER-LANE DECISION
        ↓
PPTX OBJECT(S) OR BOUNDED IMAGE ASSET
```

The IR must not flatten known text, numbers, evidence relationships, or editable assets into pixels merely because one renderer uses an image.

## 2. Separation of concerns

The experimental representation has four layers:

1. **Reasoning layer** — claim, evidence boundary, proof logic, hierarchy.
2. **Semantic visual layer** — objects and relationships that must exist to prove the claim.
3. **Render plan** — native / SVG→DrawingML / image / auto routing and bounded visual slots.
4. **Realization map** — emitted PowerPoint object IDs, asset IDs, and QA trace after compilation.

Reasoning remains identical across A/B/C benchmark variants. Only the render plan should differ.

## 3. Top-level schema

```json
{
  "ir_version": "0.1-experimental",
  "deck_id": "queuezero-stage3",
  "slide_id": "validation-traction",
  "page_role": "validation_traction",
  "governing_claim": "Early testing shows QueueZero can predict waits accurately enough to merit a semester pilot.",
  "subtitle_support": "42 students across 3 cafeterias produced a 3.8-minute MAE and 76% weekly-use intent.",
  "why_it_matters": "The prototype has both measurable technical performance and an initial demand signal, while commercial adoption remains unproven.",
  "evidence": [],
  "proof_object": {},
  "must_keep": [],
  "hierarchy": {},
  "semantic_objects": [],
  "relationships": [],
  "assets": [],
  "render_plan": {},
  "deck_system_ref": "queuezero-default-v0",
  "qa_expectations": [],
  "realization": null
}
```

## 4. Evidence object

Every quantitative or qualitative input that may affect the slide receives a stable ID.

```json
{
  "evidence_id": "weekly_use_intent",
  "statement": "76% of 42 tested students reported weekly-use intent.",
  "value": 76,
  "display_value": "76%",
  "unit": "%",
  "status": "confirmed",
  "source_ref": "queuezero_benchmark_brief",
  "supports_claims": [
    "initial user demand signal exists"
  ],
  "does_not_prove": [
    "semester retention",
    "paid university conversion",
    "campus-wide adoption"
  ]
}
```

Allowed experimental evidence states:

```text
confirmed
assumption
inference
uncertainty
```

A renderer may omit low-priority evidence visually, but it may not change its status or implication.

## 5. Proof object

The proof object describes **logic**, not coordinates.

```json
{
  "proof_object_id": "validation_evidence_stack",
  "type": "validation_stack",
  "logic": "Separate measured prototype performance from early user-demand evidence, then terminate in a clearly unproven pilot gate.",
  "primary_object_ids": [
    "metric_mae",
    "metric_students",
    "metric_weekly_intent",
    "metric_cafeterias",
    "pilot_gate"
  ],
  "required_relationships": [
    "technical_metrics_support_prototype_performance",
    "survey_metric_supports_initial_demand",
    "evidence_points_toward_pilot_not_market_validation"
  ],
  "forbidden_implications": [
    "76_percent_proves_retention",
    "42_students_proves_market_fit",
    "3_8_min_mae_proves_commercial_viability"
  ]
}
```

The proof-object vocabulary is extensible. Stage 3 should not hard-code a closed list into the schema.

## 6. Semantic object

A semantic object is something a user may reasonably need to understand, edit, move, replace, or regenerate independently.

```json
{
  "object_id": "metric_weekly_intent",
  "role": "metric",
  "content_ref": "weekly_use_intent",
  "label": "would use weekly",
  "importance": "primary",
  "editability_priority": "must_remain_editable",
  "visual_intent": {
    "emphasis": "high",
    "group": "demand_evidence",
    "relative_size": "large"
  },
  "allowed_render_lanes": ["native", "svg"],
  "preferred_render_lane": "native"
}
```

Initial `role` vocabulary:

```text
title
subtitle
body_text
metric
metric_label
card
shape
icon
image_slot
logo_slot
chart
table
diagram_node
connector
annotation
source_note
caveat
group
hero_visual_slot
```

The role vocabulary may expand after red-team review.

## 7. Semantic relationships

Relationships must be first-class because connectors and grouping can imply claims.

```json
{
  "relationship_id": "camera_to_estimator",
  "type": "data_flow",
  "from": "node_camera",
  "to": "node_queue_estimator",
  "label": "queue length",
  "directional": true,
  "evidence_refs": [],
  "semantic_strength": "explicit",
  "allowed_visual_forms": ["arrow", "directed_connector"],
  "forbidden_visual_forms": ["checkmark", "causal_flywheel"]
}
```

Initial relationship vocabulary:

```text
data_flow
sequence
contains
supports
contrasts_with
groups_with
must_pass_before
correlates_with
compares_to
annotates
```

For Stage 3, causal relationships should not be introduced unless supplied evidence explicitly supports causation.

## 8. Asset slots

Replaceable external assets must have stable slot identities.

```json
{
  "asset_id": "product_screenshot_main",
  "kind": "screenshot",
  "source": "experiment/assets/queuezero-ui.png",
  "replaceable": true,
  "crop_policy": "contain",
  "editability_priority": "must_be_replaceable",
  "semantic_object_id": "screenshot_main"
}
```

Generated visuals use the same principle:

```json
{
  "asset_id": "hero_visual_problem",
  "kind": "generated_visual",
  "source": null,
  "replaceable": true,
  "generation_brief_ref": "hero_problem_v1",
  "regeneration_scope": "asset_only",
  "semantic_object_id": "hero_visual_slot"
}
```

## 9. Render plan

The same semantic slide can produce three benchmark variants.

```json
{
  "variant": "hybrid",
  "routing": {
    "title": "native",
    "subtitle": "native",
    "metric": "native",
    "metric_label": "native",
    "diagram_node": "svg",
    "connector": "svg",
    "image_slot": "native",
    "logo_slot": "native",
    "hero_visual_slot": "image",
    "source_note": "native"
  },
  "fallback_policy": "fail_closed",
  "full_slide_rasterization_allowed": false
}
```

Allowed experimental lanes:

- `native` — directly emitted PowerPoint object.
- `svg` — authored/compiled through the constrained SVG→DrawingML lane.
- `image` — bounded raster/generated visual asset.
- `auto` — router chooses one of the above and records the reason.

For the **image-first baseline only**, a render adapter may produce a full-slide image, but the underlying semantic IR remains intact so the benchmark can compare information loss rather than pretending it never existed.

## 10. Editability priority

Every user-facing semantic object should declare one of:

```text
must_remain_editable
should_remain_editable
replaceable_asset
raster_allowed
```

Stage 3 default policy:

### must_remain_editable
- titles and subtitles
- metrics and metric labels
- ordinary explanatory text
- simple cards
- simple diagram labels/nodes
- major connectors whose wording/direction may change
- source/caveat text

### replaceable_asset
- screenshots
- logos
- generated hero visuals

### raster_allowed
- decorative artwork
- complex illustration
- texture/background art
- bounded high-complexity visuals with no likely last-minute semantic edits

## 11. Hierarchy object

```json
{
  "highest_priority": "title",
  "visual_protagonist": "validation_evidence_stack",
  "primary_numbers": [
    "metric_weekly_intent",
    "metric_mae"
  ],
  "secondary_numbers": [
    "metric_students",
    "metric_cafeterias"
  ],
  "bottom_synthesis": "pilot_gate",
  "source_note_weight": "low"
}
```

The renderer can choose exact size/placement while preserving the hierarchy contract.

## 12. Deck System Contract reference

The deck-level design system should be structured separately from page-local proof objects.

Example fields:

```json
{
  "deck_system_id": "queuezero-default-v0",
  "slide_size": "16:9",
  "title_policy": {},
  "subtitle_policy": {},
  "page_marker_policy": "none",
  "source_note_policy": {},
  "bottom_synthesis_policy": "judgment_slides_only",
  "material_treatment": "flat_with_selective_depth",
  "design_tokens": {},
  "safe_margins": {}
}
```

Exact design tokens are intentionally not frozen yet.

## 13. Realization map

After compilation, every emitted object should be traceable back to semantics.

```json
{
  "variant": "hybrid",
  "objects": [
    {
      "semantic_object_id": "metric_weekly_intent",
      "render_lane": "native",
      "ppt_object_ids": ["shape_27"],
      "asset_ids": [],
      "fidelity": "semantic_and_editable"
    },
    {
      "semantic_object_id": "hero_visual_slot",
      "render_lane": "image",
      "ppt_object_ids": ["picture_31"],
      "asset_ids": ["hero_visual_problem_v2"],
      "fidelity": "bounded_raster"
    }
  ]
}
```

This realization map is the basis for local editing, change-impact analysis, and structural QA.

## 14. Change-impact contract

A simple edit should identify affected semantic objects before anything is regenerated.

Examples:

```text
76% → 81%
  affects: evidence.weekly_use_intent + metric_weekly_intent
  should not affect: hero visual, title geometry, other metrics

replace product screenshot
  affects: asset.product_screenshot_main + screenshot_main
  should not affect: text, diagram, theme

blue → orange accent
  affects: deck-system design token + objects bound to that token
  should not affect: content/evidence

regenerate hero visual
  affects: one generated asset slot
  should not affect: native text/metrics/diagram
```

## 15. Stage 3 QA expectations

The compiler/test harness should eventually be able to assert:

- every `must_remain_editable` object maps to at least one non-raster PPT object;
- every `replaceable_asset` maps to an independently addressable picture object;
- no full-slide picture exists in native/vector or hybrid variants;
- all confirmed metrics preserve exact displayed values;
- every rendered connector maps to a semantic relationship;
- no semantic relationship is invented by the renderer;
- critical object IDs survive local edits where feasible;
- renderer fallbacks are recorded, never silent;
- bounded image regeneration changes only the target asset/object;
- ordinary panic-test edits do not require whole-slide regeneration.

## 16. Questions for Ox red-team

The next architecture review should attack at least:

1. Is semantic meaning mixed with presentation too early?
2. Are IDs stable enough for incremental editing?
3. Is the evidence model sufficient for derived/simple arithmetic values?
4. Are chart/table data schemas missing?
5. How should groups and nested ownership work?
6. How should generated visuals declare text-free regions and exclusion zones?
7. What information is required for deterministic text fitting?
8. Does `allowed_render_lanes` belong in semantic IR or a separate capability policy?
9. How should renderer-specific constraints be represented without polluting semantics?
10. What information would we regret losing when a slide is edited after export?
