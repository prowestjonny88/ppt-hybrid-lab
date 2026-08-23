# Stage 3 Controlled Architecture Benchmark — Panic Test Protocol

> Status: experimental benchmark contract. Do not change scoring or edit tasks after seeing architecture results unless the change is versioned and all variants are rerun.

## 1. Objective

Test whether a hybrid native/vector/image architecture can retain most of the visual quality of a full-slide image baseline while approaching the last-mile editability of a native PowerPoint baseline.

Primary question:

> Can hybrid preserve roughly 80–90%+ of the perceived visual quality of image-first while delivering near-native local editability and avoiding whole-slide regeneration for normal hackathon edits?

## 2. Fixed benchmark content

Project: **QueueZero**

Slides:

1. `problem_hook`
2. `how_it_works`
3. `validation_traction`

Variants per slide:

- `A_image_first`
- `B_native_vector`
- `C_hybrid`

Total primary outputs: **9 slides**.

All three variants of each slide must consume the same governing claim, evidence set, proof-object logic, must-keep values, and deck-system intent from the semantic Slide IR.

## 3. Variant definitions

### A — Image-first baseline

- Full slide may be generated/rendered as one raster image.
- Semantic IR remains stored externally for comparison.
- PPTX may contain one full-slide image.
- This variant establishes the visual-quality reference, not the editability target.

### B — Native/vector baseline

- No full-slide rasterization.
- Text/metrics/common geometry should be native PowerPoint where practical.
- Constrained SVG→DrawingML is allowed for richer vector structures.
- User screenshots/logos may remain independently replaceable picture objects.
- Generated illustration should be avoided unless required by the fixed slide brief.

### C — Hybrid hypothesis

- No full-slide rasterization.
- Normal text, metrics, simple cards, source notes, replaceable screenshots/logos remain independently editable/replaceable.
- SVG→DrawingML may handle structured diagrams or vector composition.
- Image generation is limited to explicitly bounded `hero_visual_slot` / high-complexity visual regions.
- Regenerating a bounded image asset must not regenerate unrelated native objects.

## 4. Mandatory panic edits

Execute the same applicable edit sequence against each architecture.

### P1 — Metric update

Change:

```text
76% → 81%
```

Record whether the change requires:

- direct PowerPoint/object edit;
- structured data/IR update + local compile;
- code/layout modification;
- AI call;
- OCR/reconstruction;
- whole-slide regeneration.

### P2 — Headline rewrite

Replace the action title with a materially different sentence of similar meaning and slightly different length.

Check:

- text remains editable;
- fitting behavior;
- collateral movement;
- whether other slide content is regenerated.

### P3 — Screenshot replacement

Replace the product screenshot with a different aspect-ratio-compatible screenshot.

Check:

- independent picture/slot identity;
- crop policy;
- neighboring-object stability;
- need for AI/code rerun.

### P4 — Move KPI

Move one KPI approximately **30 px equivalent** from its original position.

Check whether this can be done locally without changing the proof object or rerendering the slide.

### P5 — Title resize

Reduce title size by approximately **15%**.

Check direct editability and whether the title remains within safe bounds.

### P6 — Accent recolor

Change the primary accent:

```text
blue → orange
```

Check:

- tokenized/local color update;
- unintended raster regions that cannot follow the theme;
- number of objects requiring manual changes.

### P7 — Delete one metric

Delete one secondary metric block.

Check:

- whether it is an independent object/group;
- whether layout collapses gracefully or leaves an unacceptable hole;
- whether regeneration is required.

### P8 — Add sponsor logo

Insert a sponsor logo into a designated safe region.

Check independent image insertion and whether normal slide editing remains straightforward.

### P9 — Diagram wording change

Change one diagram-node label.

Check:

- editable text identity;
- text fitting;
- connector stability;
- need to regenerate diagram/slide.

### P10 — Hero-only regeneration

For slides with a bounded generated visual, regenerate only that asset using a changed art-direction request.

Hard requirement for hybrid:

```text
native title        unchanged
native metrics      unchanged
native labels       unchanged
semantic diagram    unchanged
hero visual asset   changed
```

## 5. Structural PPTX audit

For each exported PPTX/slide record:

- slide count;
- native text object count;
- native shape count;
- connector count;
- group count;
- chart count;
- table count;
- picture count;
- full-slide picture count;
- generated-asset picture count;
- replaceable screenshot/logo count;
- semantic objects with no realization mapping;
- `must_remain_editable` objects realized only as raster;
- silent renderer fallbacks;
- file size.

Expected:

### Image-first

Full-slide picture is allowed and expected.

### Native/vector and hybrid

```text
full_slide_picture_count = 0
```

Every `must_remain_editable` semantic object must map to a non-raster PowerPoint object.

## 6. Edit-operation outcome labels

Each panic edit receives one dominant outcome:

```text
DIRECT_PPT_EDIT
LOCAL_STRUCTURED_RECOMPILE
LOCAL_ASSET_REGEN
CODE_LAYOUT_CHANGE
WHOLE_SLIDE_REGEN
OCR_RECONSTRUCTION
BLOCKED
```

Also record:

- affected semantic object IDs;
- affected PPT object IDs;
- unexpected changed objects;
- AI call count;
- manual operation count;
- rendered visual regression observed: yes/no;
- exact-value fidelity preserved: yes/no.

## 7. Collateral-damage metric

For each edit:

```text
collateral_damage_ratio = unexpected_changed_objects / pre_edit_addressable_objects
```

If object-level diffing is unavailable, record a conservative manual classification:

```text
NONE
LOCAL
REGIONAL
WHOLE_SLIDE
```

Hybrid success requires normal text/data/screenshot edits to remain `NONE` or `LOCAL`.

## 8. Blind visual review

Render all slides to images and hide architecture labels.

Use anonymous IDs only.

Score 1–5:

- first impression;
- professional design quality;
- visual hierarchy;
- originality / non-template feel;
- pitch clarity;
- proof-object clarity;
- information density appropriateness;
- visual consistency;
- judge-readability at presentation distance;
- willingness to present at a hackathon.

Do not reveal A/B/C identity until scoring is recorded.

## 9. Visual-quality retention

For a given slide:

```text
hybrid_visual_retention = hybrid_blind_score / image_first_blind_score
native_visual_retention = native_blind_score / image_first_blind_score
```

Interpretation is experimental rather than statistically rigorous because the initial benchmark has only three slides.

Target hypothesis:

```text
hybrid_visual_retention >= 0.85
```

A result below ~0.80 should trigger serious reconsideration rather than architecture rationalization.

## 10. Editability score

Score each mandatory edit:

- 5 = direct/local edit, no collateral damage, no AI call;
- 4 = local structured recompile or bounded asset replacement;
- 3 = localized code/layout change or moderate collateral movement;
- 2 = substantial regeneration/reconstruction;
- 1 = whole-slide regeneration for ordinary content edit;
- 0 = blocked or corrupted.

Normalize across applicable edits.

Target hypothesis:

```text
hybrid_editability >= 0.90 * native_editability
```

## 11. Text/data fidelity

Hard checks:

- exact must-keep values preserved before edits;
- requested new value preserved after edits;
- no hallucinated metrics;
- evidence status not changed by renderer;
- `does_not_prove` guardrails not visually contradicted;
- no OCR used for text already known in semantic IR in native/vector or hybrid lanes.

## 12. Runtime/cost instrumentation

Where observable, record:

- total generation wall-clock duration;
- model/API call count;
- image-generation call count;
- Ox/GPT architecture-analysis calls are excluded from per-slide generation cost;
- renderer retries;
- failed validation attempts;
- generated asset count;
- output file size.

Do not fabricate exact dollar cost if provider accounting is unavailable.

## 13. Decision rule

### Prefer hybrid if

- visual retention is approximately 85–90%+ of image-first;
- editability is at least ~90% of native baseline;
- ordinary panic edits do not require whole-slide regeneration;
- hero-only regeneration is cleanly local;
- semantic/evidence fidelity remains intact.

### Prefer native/vector if

- its blind visual quality is statistically/qualitatively indistinguishable from hybrid for the benchmark;
- generated visuals add little perceived value;
- native/vector materially simplifies generation and editing.

### Reconsider image-first/reconstruction if

- image-first wins visually by a large margin that hybrid cannot close;
- hybrid composition looks structurally generic or visibly stitched;
- bounded image generation cannot integrate naturally with native objects.

No architecture is declared the winner before all three slide types and all mandatory applicable edits are evaluated.
