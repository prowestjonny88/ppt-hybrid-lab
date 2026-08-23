# GPT Adjudication — Mck Native Component Analysis

Status: ACCEPT WITH MODIFICATION

Source: Ox task-004 over `likaku/Mck-ppt-design-skill` at commit `e190e083b715b63172e1c4fea01bc5f9bb21a021`.

## Canonical conclusions

### Accept
- Mck proves a native-object PowerPoint route can support local last-minute edits without whole-slide regeneration.
- Its composition model is immediate-mode and coordinate-driven over `python-pptx`, with native textboxes, autoshapes, pictures, and flat vector chart-like structures.
- Same-bbox image replacement is naturally isolated because neighboring objects are independently positioned.
- Adaptive item-count geometry, spacing arithmetic, explicit constants/tokens, and post-generation QA are useful engineering principles.
- Geometry-only QA can infer the wrong semantic peer groups; semantic roles/IDs are required for trustworthy QA.

### Modify
- Do not adopt Mck's ~60 layout methods as the product architecture. They are mostly fixed layout recipes with parameterized local geometry, not a semantic component graph.
- Do not use position/name heuristics as object identity. Every emitted object in Stage 3 must trace to a stable semantic object ID.
- Do not use text glyph arrows or a connector ban as our default. Relationships must be first-class and may compile through native or SVG/DrawingML lanes.
- Do not treat rectangle-based pseudo-charts as a substitute for native charts when editable chart data matters.
- Do not rely on its text overflow estimator or peer-font grouping as authoritative QA.

### Reject
- Style/locale-specific hardcoded labels and McKinsey visual conventions as architectural requirements.
- Orphaned image-placeholder siblings and untracked shape sets.
- Layout-count catalogs as the core planning abstraction.

## Minimum native component API for Stage 3

The native lane should expose semantic primitives rather than full slide templates:

- `add_text(object_id, role, text, box, style_ref, fit_policy)`
- `add_metric(object_id, value_ref, label, box, style_ref)`
- `add_shape(object_id, shape_kind, box, style_ref, geometry)`
- `add_image_slot(object_id, asset_id, box, crop_policy, replaceable=true)`
- `add_logo_slot(object_id, asset_id, box)`
- `add_group(object_id, child_ids, semantic_role)`
- `add_connector(object_id, relationship_id, from_id, to_id, style_ref)`
- `add_source_note(object_id, text, box, style_ref)`
- `add_chart(object_id, data_ref, chart_spec, box)` when native chart semantics are required
- `bind_style_token(object_id, token_ref)`

Every primitive must return a realization record containing semantic object ID, emitted PPT object ID(s), render lane, bounds, and fidelity/editability classification.

## Stage 3 routing implication

- Native lane: titles, subtitles, metrics, cards, source notes, image/logo slots, simple native shapes.
- SVG→DrawingML lane: freeform diagrams, process structures, complex arrows/connectors, vector icons when native primitives become cumbersome.
- Image lane: bounded decorative/hero visual only.

Mck therefore supports H2 as a viable editability lane but does not establish that native-only composition reaches the image-generation visual-quality ceiling.
