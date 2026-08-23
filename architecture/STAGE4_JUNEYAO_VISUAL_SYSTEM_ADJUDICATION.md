# Stage 4 Adjudication — Task 007 JuneYao Visual-System Forensics

Status: ADJUDICATED

Source report: `.ox/reports/task-007-juneyao-visual-system.md`
Inspected upstream commit: `JuneYaooo/gpt-image2-ppt-skills@2d57ef8127b83e8232a1be4e9515f0b3cc9fc91e`

## Evidence limitation

Ox's bounded context contained 43 `styles/**/*.layouts.json` files and did **not** contain the upstream workflow/docs/scripts. Therefore this adjudication accepts direct claims about the structured style/layout corpus, while treating pipeline-mechanism claims from the Ox report as inference unless independently verified elsewhere.

## ACCEPT — portable into Stage 4

### 1. Identity anchors are first-class deck-system state

Direct corpus evidence shows distilled styles carrying `theme.identity_anchors[]` describing recurring visual atoms: borders, margin text, dot matrices, geometric cutouts, texture rules, pagination markers, extreme scale relationships, and explicit negative laws.

Decision:
- keep `identity_anchors` as first-class style-profile data;
- each anchor must declare an implementation class (`native_vector`, `bounded_image`, or other explicitly allowed lane);
- any anchor carrying audience-visible text must remain native/editable;
- usage frequency and semantic requirement should be machine-checkable where possible.

This strengthens, rather than replaces, `queuezero_hackathon_v0.json`.

### 2. Capacity is a machine contract, not prose

Direct evidence from the hand-authored generation shows per-layout JSON Schema constraints using `required`, `minLength`, `maxLength`, `minItems`, `maxItems`, and `additionalProperties:false`.

Decision:
- Stage 4 archetypes should gain machine-readable payload/content schemas;
- free-text capacity guidance may remain documentation, but cannot be the canonical gate;
- compiler must validate capacity before coordinate solving.

### 3. Routing should be two-stage

Direct distilled fields include `routing.content_shapes`, optional `requires`, and min/max item predicates, alongside `best_for` / `avoid_for` prose.

Decision:
- deterministic eligibility filter first;
- model/Visual Director may choose among eligible archetypes using rhetorical fit and `best_for` / `avoid_for`;
- log the eligible survivor set and final selection reason for auditability;
- never ask the model to choose from archetypes that already violate hard capacity/capability constraints.

### 4. Anti-repetition becomes a checker

The corpus explicitly stores variation and anti-repetition rules, including avoiding repeated primary composition/decoration placement on adjacent slides.

Decision:
- anti-repetition must be promoted from prompt guidance into a deck-level validator/constraint solver;
- adjacent slides may not share an identical `archetype_id + variation_signature` unless intentionally marked as a sequence;
- rhythm/one-off compositions should carry reuse budgets.

### 5. Distilled layouts are grammars, not frozen frames

Direct evidence includes layouts whose summary explicitly says to **adapt** a source-supported grid into a table or timeline rather than copy the source arrangement.

Decision:
- preserve our Stage 4 definition of archetypes as composition grammars;
- variants expose relationships/zones/capacities, not a screenshot coordinate template;
- provenance/reference examples may inform grammar but never become hidden mandatory coordinates.

### 6. Bounded image slots remain useful

Direct evidence includes normalized image slots with purpose, bbox and priority.

Decision:
- retain bounded image slots downstream of semantic truth;
- add future slot flags for `aspect_lock`, `flexible_rezone`, and crop intent;
- a slot never authorizes generated semantic text.

### 7. Negative style laws deserve explicit fields

Direct examples include style laws such as no gradients/shadows/3D and single-accent/background-mode constraints.

Decision:
- encode negative style laws separately from flavor prose;
- include them in style validation and pixel/structural QA where measurable.

### 8. Defects should seed future gates

Direct evidence includes source-layout defects (for example bottom clipping) stored as `avoid_for` knowledge.

Decision:
- pattern-level visual defects discovered in Stage 4 should become named QA rules/tests when measurable;
- do not leave recurrent failures only as prose memories.

## MODIFY / constrain

### Two-tier style registry

Ox recommends collapsing per-source-deck style explosion into `DesignLanguage -> DeckStyleProfile`.

Decision: ACCEPT CONCEPTUALLY, DEFER SCHEMA FREEZE.

Reason:
- it cleanly separates reusable visual language from project-specific palette/identity instantiation;
- but we only have one product style profile today, so premature schema complexity would slow the sample proof.

Stage 4 sample may continue with one `DeckStyleProfile`; introduce `DesignLanguage` before broad style-library ingestion.

### Provenance

Direct corpus evidence has `source`, `source_hash`, `evidence_pages`, and page index.

Decision:
- preserve provenance whenever a style/archetype is distilled from external references;
- clean-room product archetypes need a `derivation` record, but runtime need not carry bulky source metadata into every slide.

## REJECT / DO NOT PORT

- full-slide generated image as semantic source of truth;
- unconstrained generated audience text;
- OCR/reconstruction as the normal path for content we already know;
- exact source arrangements or source assets copied into clean-room archetypes;
- treating hundreds of per-source-deck near-duplicate style files as a product-ready registry;
- trusting conflicting `max_items`, duplicated evidence pages, redundant roles, or boilerplate rules without normalization;
- letting `visual_signature` prompt fragments become canonical layout state;
- any mechanism claim from Task 007 that depends on upstream scripts/docs not included in the bounded Ox context.

## Changes required before Visual IR V1 freeze

1. Add machine payload/content contracts to archetype registry.
2. Add deck-level variation signature + anti-repetition checker.
3. Add `implementable_as` / usage semantics to identity anchors.
4. Add explicit negative style-law structure.
5. Add flexible/aspect-lock semantics to bounded visual slots.
6. Preserve deterministic routing eligibility separate from model selection.
7. Record provenance/derivation for future reference-distilled archetypes.

These changes are **not** blockers for the one-slide Validation sample proof, because that sample uses one already-selected archetype and no external image slot. They are blockers for freezing Stage 4 Visual IR/registry V1 and scaling generation across arbitrary decks.
