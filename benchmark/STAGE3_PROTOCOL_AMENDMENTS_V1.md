# Stage 3 Panic-Test Protocol — v1 Amendments

These amendments refine `STAGE3_PANIC_TEST_PROTOCOL.md` without changing the benchmark goal.

## Fixed coordinate reference

Any panic edit expressed in pixels is interpreted against a **1280×720 reference canvas** and converted to normalized slide coordinates before compilation.

Example: move 30 px right = `30 / 1280 = 0.0234375` normalized x.

## Image-first structural audit

OCR is explicitly permitted **only for post-hoc audit of the image-first baseline**, because its PPTX intentionally contains a full-slide raster. OCR is not permitted as a reconstruction step for native-vector or hybrid variants and is not permitted to recover known authored text before generation.

## Sequential edit interaction

The panic test is sequential within each architecture. Therefore P8 sponsor-logo insertion followed by a later structured recompile intentionally tests whether user-added objects survive reconciliation/adoption.

User-added objects inside a declared `insertion_zone` must be adopted/preserved. User-added objects outside insertion zones must be preserved and flagged rather than silently deleted.

## Local edit identity

Object-level comparison uses deterministic PowerPoint shape names:

`oxq:{slide_id}:{object_id}[:{part}]`

If an architecture cannot preserve an equivalent stable identity, record that as an editability/traceability failure rather than substituting coordinate heuristics.

## Semantic fairness

For every slide, variants A/B/C must consume the same canonical `slide_semantics` file. The harness records its canonical SHA-256 plus render-plan, deck-system, capability-registry, prompt/instruction and source-asset hashes in a variant input manifest.

## Generated-asset locality

Hybrid generated assets must be bounded to declared regions, use versioned asset instances, obey `text_free` and forbidden-depiction rules, and may not cover or regenerate native information-bearing objects.

## Recompile idempotence

A structured recompile with unchanged semantics, plan, deck system and assets must preserve the same semantic object set, shape identities and content. Non-semantic OOXML/package noise is ignored; semantic-object changes are not.
