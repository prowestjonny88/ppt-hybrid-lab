# GPT Adjudication — Ox task-005 Slide IR Red-Team

Source: `.ox/reports/task-005-slide-ir-red-team.md`.

## Verdict

**ACCEPT: FREEZE-WITH-CHANGES.** The four-layer architecture survives. The v0 draft is retained only as history; Stage 3 build uses `architecture/SLIDE_IR_V1.md`.

## Accepted freeze-blocking findings

1. **Separate invariant semantics from render plans and realizations.** Implemented as `slide_semantics/`, `render_plans/`, and future `realizations/`.
2. **Remove renderer lane choices from semantic objects.** Implemented. Routing is now overlay-only and checked against `CAPABILITY_REGISTRY.stage3.json`.
3. **Add explicit normalized regions and realization bounds.** Implemented in v1 semantics; realization emitter must record EMU bounds.
4. **Add referential integrity + deletion cascade.** Implemented validator; Stage 3 deletion policy is tombstone + recorded cascade.
5. **Add deterministic round-trip shape identity.** Frozen naming convention: `oxq:{slide_id}:{object_id}[:{part}]`.
6. **Make guardrails structured and make vector text-as-curves fail editability QA.** Implemented in schema/capability contract.

## Accepted supporting findings

- Evidence supports scalar/range values plus optional derivation/history/conflict/source-span fields.
- Mutable evidence values in slide prose use bindings such as `{weekly_use_intent.display_value}`.
- Minimal design tokens/type scale are frozen for benchmark fairness.
- Groups are first-class semantic containers with `member_ids`, `layout_hint`, and `reflow_policy`.
- Generated assets are bounded, versioned slots with aspect ratio, crop, text-free policy, forbidden depictions and token dependencies.
- Realization records must include bounds, fit result, fallback trace, semantic identity and content hash.

## Modified from Ox recommendation

- Stage 3 does not require general nested group recursion; groups contain semantic objects only. This is sufficient for the three-slide benchmark and avoids premature layout-tree complexity.
- Full evidence revision history/conflict resolution is optional in Stage 3. The schema permits it, but the benchmark does not build a general evidence database.
- Charts/tables remain deferred because none of the selected three benchmark slides requires a true editable chart/table object.

## Probe adjudication

### V1 — SVG editable text

Accepted as **verified for the Stage 3 constrained subset** based on the prior controlled Stage 2 PPT Master fixture (editable text objects were emitted) plus direct source evidence that the converter has a closed native text grammar and a dedicated `convert_text` DrawingML path. Stage 3 capability registry records `text_as_curves=false` for the constrained lane. Any later implementation that outlines text will fail realization QA.

### V2 — Native single-object patch

Implemented as `tests/probes/native_patch_probe.py`. CI must prove that `76% -> 81%` changes only the deterministically named target object while preserving geometry and all peer objects.

## Freeze status

The Stage 3 IR v1 is frozen for the controlled experiment subject to automated validator/probe success. Schema expansion during the benchmark requires an explicit amendment and rationale; no silent goalpost changes.
