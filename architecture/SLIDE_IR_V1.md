# Stage 3 Experimental Slide IR — v1

Status: **FROZEN FOR CONTROLLED STAGE 3 BENCHMARK** after Ox task-005 red-team and GPT adjudication.

This is an experimental contract, not the final product schema.

## 1. Invariant architecture

Stage 3 uses three separate artifacts:

1. `slide_semantics/*.v1.json` — renderer-agnostic invariant meaning.
2. `render_plans/<slide>.<variant>.json` — per-variant routing overlay.
3. `realizations/<slide>.<variant>.json` — compiler output, PPT object IDs, bounds, fidelity and fallback trace.

The benchmark harness MUST hash the canonicalized `slide_semantics` document and record the identical semantic hash in all A/B/C variant manifests.

```text
SOURCE FACT / INPUT
      ↓
EVIDENCE
      ↓
SEMANTIC OBJECTS + GROUPS + RELATIONSHIPS
      ↓
RENDER PLAN OVERLAY
      ↓
PPTX OBJECTS / BOUNDED ASSETS
      ↓
REALIZATION MAP + QA TRACE
```

Renderer choice is forbidden in the semantic layer.

## 2. Evidence

Each evidence record has a stable `evidence_id` and may contain:

- `value`: scalar, null, or `{min,max}` range.
- `display_value`.
- `unit`.
- `status`: `confirmed | assumption | inference | uncertainty`.
- `source_ref` and optional `source_span`.
- `supports_claims[]`.
- `does_not_prove[]`.
- optional `derivation {formula,input_evidence_refs[]}`.
- optional `supersedes`, `history[]`, `conflicts_with[]`.

Prose may reference evidence with bindings such as:

```text
{weekly_use_intent.display_value}
```

Do not duplicate mutable evidence values as free literals in slide prose.

## 3. Semantic objects

Each independently meaningful/editable item receives a stable `object_id`.

Required fields:

- `object_id`
- `role`
- `importance`
- `editability_priority`

Content uses either `content`, `content_template`, or `content_ref`.

`editability_priority`:

- `must_remain_editable`
- `should_remain_editable`
- `replaceable_asset`
- `raster_allowed`

Semantic objects MAY carry `token_refs[]`, `region_ref`, `fit_policy`, and semantic `visual_intent`, but MUST NOT carry render-lane preferences.

## 4. Groups

Groups are first-class semantic containers:

```json
{
  "group_id": "validation_evidence_stack",
  "member_ids": ["metric_mae", "metric_weekly_intent"],
  "layout_hint": "evidence_stack",
  "reflow_policy": "local"
}
```

Groups express ownership/composition intent without absolute coordinates.

## 5. Relationships

Relationship endpoints are typed references:

```json
{
  "ref_type": "object",
  "id": "metric_mae"
}
```

or:

```json
{
  "ref_type": "group",
  "id": "validation_evidence_stack"
}
```

Every endpoint and `evidence_ref` must resolve.

Relationship types in Stage 3 include:

`data_flow`, `sequence`, `contains`, `supports`, `contrasts_with`, `groups_with`, `must_pass_before`, `correlates_with`, `compares_to`, `annotates`.

No causal relation may be introduced unless evidence supports causation.

## 6. Structured forbidden implications

Guardrails are machine-addressable:

```json
{
  "guardrail_id": "intent_not_retention",
  "applies_to": [{"ref_type":"object","id":"metric_weekly_intent"}],
  "forbidden_claim": "weekly intent proves retention",
  "forbidden_visual_forms": ["retention_loop", "verified_checkmark"],
  "forbidden_depictions": ["validated retention badge"]
}
```

Evidence `does_not_prove` statements feed these guardrails.

## 7. Regions

A slide may define normalized regions in `[0,1]` coordinates:

```json
{
  "region_id": "hero_frame",
  "purpose": "hero_frame",
  "rect": {"x":0.52,"y":0.15,"w":0.43,"h":0.70}
}
```

Allowed purposes include `content`, `hero_frame`, `image_slot`, `insertion_zone`, `safe_area`, `proof_object`, and `footer`.

The panic protocol interprets pixel-like moves against the fixed reference canvas **1280×720**, then converts to normalized coordinates.

## 8. Assets and bounded generation

Asset slots are stable identities; asset instances are versioned.

Generated asset declarations must include:

- `asset_id` stable slot.
- `semantic_object_id`.
- `region_ref`.
- `aspect_ratio`.
- `text_free` boolean.
- optional `exclusion_zones[]`.
- optional `safe_crop`.
- optional `composition_anchor`.
- `forbidden_depictions[]`.
- `palette_token_refs[]`.
- `regeneration_trigger`: `token_change | manual | never`.
- `current_instance {instance_id,version,source}`.

Regeneration changes the asset instance, not the slot identity.

## 9. Deck system

Stage 3 freezes a minimal design system separately from semantics:

- color tokens
- type scale
- default role→type-token mapping
- per-role text fit policy
- safe margins
- bottom-synthesis policy

Semantic objects may bind to token names; concrete rendering values live in the deck system.

## 10. Render plan overlay

Each variant receives a separate render plan:

```json
{
  "variant": "hybrid",
  "semantic_hash": "<filled by harness>",
  "routing": {
    "role_defaults": {"metric":"native"},
    "object_overrides": {},
    "decisions": []
  },
  "fallback_policy": "fail_closed",
  "full_slide_rasterization_allowed": false
}
```

The router MUST satisfy `editability_priority` as a hard constraint.

A capability registry defines what each lane can produce. Semantic objects never declare lanes.

## 11. Variant input manifest

Every generated variant records:

- semantic file path + hash
- render-plan path + hash
- deck-system path + hash
- capability-registry hash
- prompt/instruction hash where a model is involved
- source asset hashes

This is the benchmark-fairness audit trail.

## 12. Realization map

Each emitted object records:

```json
{
  "semantic_object_id": "metric_weekly_intent",
  "render_lane": "native",
  "ppt_object_ids": ["shape_27"],
  "ppt_shape_names": ["oxq:validation-traction:metric_weekly_intent:value"],
  "bounds_emu": [{"x":0,"y":0,"w":0,"h":0}],
  "token_refs": ["accent.primary"],
  "fidelity": "semantic_and_editable",
  "fit_result": "fit",
  "fallback": null,
  "pptx_content_hash": "...",
  "realization_rev": 1
}
```

Fidelity vocabulary:

- `semantic_and_editable`
- `editable_picture_slot`
- `native_normalized`
- `vector_text_as_curves`
- `bounded_raster`
- `full_slide_raster`

`must_remain_editable` text MUST map to an actual text-frame-bearing object; `vector_text_as_curves` does not satisfy the requirement.

## 13. Round-trip identity and manual edits

Every emitted object uses deterministic naming:

```text
oxq:{slide_id}:{object_id}[:{part}]
```

The realization map records the name and content hash.

Reconciliation policy:

- known named objects are matched by semantic identity, never position/name heuristics alone;
- user-added objects inside an `insertion_zone` are adopted as `provenance: user_added` objects;
- user-added objects outside declared insertion zones are preserved and flagged for review;
- recompilation must not silently delete user-added objects.

## 14. Deletion and cascade

Stage 3 uses **tombstone + recorded cascade**:

- deleted object receives a tombstone/audit entry;
- dependent relationships are removed from active rendering and recorded in the cascade log;
- group membership, hierarchy refs, proof-object refs and required relationships are updated explicitly;
- dangling references fail validation.

## 15. Text fitting

Each editable text object resolves a `fit_policy` from object override or deck-system role default.

Stage 3 policies:

- `fixed_box_wrap`
- `shrink_to_floor`
- `local_reflow`
- `fail_on_overflow`

The realization records the resolved box, font token/size, line count estimate or renderer result, and `fit_result`.

A title edit must remain local unless its declared group `reflow_policy` permits neighboring movement.

## 16. Change-impact rules

Edits are dependency-driven, not prose examples.

- Evidence revision touches its evidence record, every bound template, every semantic object using `content_ref`, and dependent QA assertions.
- Asset replacement touches only the slot's current instance and its picture realization unless crop policy changes.
- Token change touches objects/assets bound to that token; generated assets with `regeneration_trigger=token_change` are marked stale.
- Object movement changes only its geometry override/realization unless the owning group's `reflow_policy` says otherwise.
- Hero regeneration changes one versioned asset instance and picture object.
- Recompiling with no semantic/render changes MUST be idempotent at the semantic-object level.

## 17. Freeze gates

Before build:

1. Referential-integrity validator passes on all v1 semantics.
2. A/B/C plans reference the same semantic hash.
3. V1 capability probe confirms SVG-lane editable text behavior.
4. V2 native-patch probe confirms one metric can change without collateral semantic-object mutation.
5. The panic-test P1–P10 edits all map to a defined outcome class.

The v0 draft remains in the repository as red-team history and is not used by the Stage 3 compiler.
