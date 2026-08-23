# GPT Adjudication — task-003 RW reasoning system

## Status

ACCEPT WITH MODIFICATIONS

## Evidence scope

Ox inspected all 10 eligible reasoning/governance files selected from `Pikapika260214/rw-consulting-ppt` at commit `1df28e81de04b3255451eb47fb641d3ec176b33d` (125,996 characters). This task therefore had full coverage of the bounded reasoning package, unlike task-002 where context truncation left several converter modules unseen.

## ACCEPT — canonical renderer-agnostic principles

1. **Claim-first slide planning.** Each slide should have one governing message / complete-sentence page claim, with the title acting as the highest-priority conclusion rather than a topic label.
2. **Typed evidence boundary.** Preserve four states separately: confirmed fact, user/source assumption, model inference, and open uncertainty.
3. **Positive and negative claim-evidence mapping.** Record both what each evidence item supports and what it must not be interpreted as proving.
4. **Proof-object routing.** Choose the main visual structure based on the logical relationship that needs to be proven; generic cards/tables/three-column/process-arrow layouts are not default proof objects.
5. **Semantic connector guardrails.** Lines, arrows, gates, checkmarks, rings, axes, and 2x2 placement communicate claims and therefore must be justified by the evidence relationship.
6. **Message hierarchy.** One action title, one visual protagonist, evidence attached to that proof object, at most one bottom synthesis, and low-weight caveat/source material.
7. **Density as a design constraint.** The renderer should reduce reading friction rather than delete necessary evidence merely to achieve a clean visual.
8. **Deck-system vs page-local separation.** Global invariants (title/subtitle rhythm, page markers, source-note treatment, bottom-synthesis policy, material treatment) should be distinct from page-local proof-object choices.
9. **Sample-driven system calibration.** Representative samples should test both visual character and difficult information density before scaling a deck system.
10. **Named failure taxonomy.** Convert RW rejection labels into explicit QA checks where practical: multiple conclusion zones, weak proof object, detached metrics, evidence misattribution, false-precision chart, linework overload, sparse concept poster, and deck-system drift.

## MODIFY — adapt rather than copy

### Human approval gates
RW assumes repeated synchronous human approval. For the Stage 3 architecture experiment, convert these into machine-readable states and optional approval checkpoints rather than hardcoding conversational stops into the core IR.

### Deck System Contract
Preserve the concept, but represent it as structured design-system fields rather than verbatim prompt text. The same contract should feed native, vector, and image renderers.

### Proof-object picker
Treat the RW mappings as a strong initial policy library, not an exhaustive universal ontology. The experimental IR should support adding new proof-object types without schema migration.

### Visual mother concept
Keep it as an art-direction field, but do not let it become the layout source of truth. Structural relationships belong in semantic/layout objects; the mother concept may influence composition and generated visual assets.

## REJECT — do not carry forward

1. Full-slide image generation as the mandatory renderer.
2. Image-only PPTX packaging as the default delivery architecture.
3. Backend locks that forbid native PowerPoint/SVG/vector routes.
4. Prompt-only state as the canonical source of design truth.
5. Contact-sheet-only QA as sufficient structural verification.

## Minimum reasoning manifest to carry into Stage 3 Slide IR

At minimum every slide should preserve:

- `slide_id`
- `page_role`
- `governing_claim`
- `subtitle_support`
- `why_it_matters`
- `evidence[]`
  - `evidence_id`
  - `statement`
  - `status`: `confirmed | assumption | inference | uncertainty`
  - `supports_claims[]`
  - `does_not_prove[]`
  - `source_ref`
- `proof_object`
  - `type`
  - `logic`
  - `required_relationships[]`
  - `forbidden_implications[]`
- `visual_mother_concept`
- `must_keep[]`
- `hierarchy`
- `source_note`
- `density_target`
- `deck_system_ref`
- `qa_expectations[]`

These are reasoning fields, not yet final renderer coordinates.

## Application to QueueZero benchmark

### Problem / Hook
Need a single problem claim, evidence distinguishing observed/known congestion from inferred consequences, and a proof object that shows the user pain or operating mechanism without inventing causal precision.

### How It Works
Need explicit semantic nodes/edges for camera → queue estimation → wait prediction → recommendation. Connectors are claims; their direction and meaning must be retained structurally so the native/vector lane can render them faithfully.

### Validation / Traction
Need separate evidence states for measured results (42 students, 3 cafeterias, 3.8-minute MAE, 76% weekly-use intent) versus future commercial claims. Metrics should live inside the proof object rather than as detached KPI decoration.

## Canonical conclusion

Borrow RW's reasoning brain and governance discipline, but make the resulting artifacts renderer-agnostic and machine-readable. The Stage 3 Slide IR should carry claim/evidence/proof semantics forward into native/vector/image routing instead of collapsing them into an image prompt.
