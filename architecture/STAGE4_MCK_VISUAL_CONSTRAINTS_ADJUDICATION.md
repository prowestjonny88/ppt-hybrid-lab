# Stage 4 Adjudication — Task 008 MCK Visual-Constraint Forensics

Status: ADJUDICATED

Source report: `.ox/reports/task-008-mck-visual-constraints.md`
Inspected upstream commit: `likaku/Mck-ppt-design-skill@e190e083b715b63172e1c4fea01bc5f9bb21a021`

## ACCEPT — portable into Stage 4

1. Capacity must be canonical machine data. Adopt per-archetype max-items, field budgets, special limits and solvability constraints in the archetype registry; compiler consumes the same source that documentation renders from.

2. Gate verdicts must be machine-derived and non-overridable by model prose. Persist structured gate records and fail CI on blocking violations.

3. Use layered QA: pre-render compiler validation -> post-render structural/PPTX QA -> pixel/multimodal visual review. Geometry health is necessary but never sufficient for aesthetic acceptance.

4. Port dynamic-sizing invariants as archetype solvers, not renderer recipes: available-width packing, minimum gaps, row-height caps, font floors and bounded fallback behavior.

5. Promote recurring failures into structured experience/regression records with root cause, fix and named preventative rule/test.

6. Treat composition routing as constraints plus rhetorical choice: deterministic eligibility/rarity/adjacency rules first, model selection among survivors second.

7. Add explicit hierarchy and balance checks absent from MCK: focal-region requirement, support-weight differentiation, area/ink variance, dead-zone prediction and mandatory pixel review for final visual acceptance.

## MODIFY / constrain

- Text-fit estimation may be used as a conservative preflight heuristic, but must not be treated as exact typography metrics.
- Peer consistency checks should be semantic-role aware; do not infer identity only from Y-position or group size.
- Whitelists/exemptions must be scoped by rule + archetype/variant + evidence, never category-global.
- Auto-fix may compress/reflow within declared limits, but must not silently destroy hierarchy or shrink below role-specific floors.
- Dead-whitespace QA should distinguish intentional protected whitespace from unplanned empty regions and should not rely on bbox coverage alone.

## REJECT / DO NOT PORT

- the 72-layout/component catalog as product architecture;
- prose-YAML capacity declarations disconnected from enforcement;
- unknown-layout fallbacks that silently pass or drop content;
- geometry-only QA as a visual-quality gate;
- category-global bug whitelists;
- duplicated constants across compiler/QA layers;
- renderer-specific fonts, coordinates, environment paths or component recipes;
- equal-weight card-grid defaults that can pass structural gates while failing hierarchy.

## Required before Visual IR / archetype registry V1 freeze

1. Single-source capacity/guardrail schema consumed by compiler and validators.
2. Structured Stage 4 gate record with compiler, structural and pixel/multimodal tiers.
3. Evidence-scoped exemption schema.
4. Semantic-role-aware peer and hierarchy checks.
5. Experience/regression ledger promotion path.
6. Deck-level adjacency/reuse-budget validator.
7. Fail-closed behavior for unsupported archetypes/variants.

These findings reinforce the existing Stage 4 direction and do not require a product/architecture decision from the user. The remaining human gate is subjective visual acceptance of the representative QueueZero Stage 4 sample.