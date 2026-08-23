# Stage 4 — Visual Quality Reset

Status: ACTIVE

## Why Stage 4 exists

Stage 3 proved that the engineering substrate is viable but the visual-design layer is not.

Verified engineering evidence retained from Stage 3:
- semantic Slide IR and stable semantic-object identity work;
- native-vector rendering can preserve full routine editability;
- the hybrid SVG/native/image route can preserve ~96% normalized editability;
- bounded generated imagery works;
- full-slide image generation can produce higher immediate polish but is not a trustworthy semantic source of truth;
- panic edits can remain local and deterministic.

Stage 3 visual outcome is explicitly **not** accepted as a design benchmark. The current QueueZero native/hybrid renderers are engineering fixtures, not product-quality composition engines.

The failure mode was architectural:

```text
strong reasoning
  -> semantic Slide IR
  -> primitive hard-coded layout functions
  -> technically valid but aesthetically weak slides
```

The missing layer is a visual-design brain that makes composition decisions *before* renderer coordinates and PowerPoint objects exist.

## Stage 4 objective

Build and validate this architecture:

```text
Pitch / narrative reasoning
        ↓
Semantic Slide IR (facts, claims, evidence, editable objects)
        ↓
VISUAL DIRECTOR
        ↓
Visual IR (composition intent + hierarchy + spatial grammar)
        ↓
Composition compiler / router
        ↓
Native text + native shapes + SVG + bounded images
        ↓
Editable PPTX
        ↓
Pixel render QA + semantic QA + editability QA
```

The Visual Director must not emit raw PowerPoint coordinates as its primary reasoning representation. It should choose and parameterize a composition system, then a deterministic compiler should realize it.

## Non-negotiable product bar

The release question is no longer:

> Does this look approximately as good as an image-first baseline?

The release question is:

> Would we willingly submit this deck to win a serious hackathon without apologizing for the design?

A slide that is technically valid but visually generic is a failure.

## What Stage 4 preserves from Stage 3

1. **Semantic Slide IR remains canonical for facts and user-editable content.**
2. **Stable object IDs remain canonical for round-trip editing.**
3. **Native-first for information.**
4. **Vector-first for structure.**
5. **Generated imagery only for bounded visual richness unless a full-slide raster is explicitly justified.**
6. **No OCR for text we already know.**
7. **Render-lane choice remains downstream of semantics.**
8. **Panic-test locality and user-added-object preservation stay mandatory.**

## What Stage 4 rejects

- treating `metric_card()` / `two_column()` / `four_column()` as the design intelligence;
- selecting a layout solely from content count;
- generic dashboard/card-grid composition as a universal fallback;
- equal visual weight for every evidence item;
- generated full-slide pixels as semantic truth;
- adding a generated hero to a weak layout and calling it a hybrid design system;
- style as only palette + font + corner radius;
- visual QA based only on overlap/overflow checks;
- an LLM verbally declaring its own slide visually successful.

## Visual Director responsibilities

For every slide, the Visual Director must decide at least:

### 1. Communication intent
- governing claim;
- audience action / belief shift;
- presentation moment: hook, explain, prove, compare, transition, ask, close;
- emotional register: urgency, confidence, clarity, delight, tension, proof.

### 2. Visual protagonist
Exactly one primary visual protagonist unless the selected archetype explicitly permits a dual focal system.

Examples:
- one dominant number;
- one product screenshot;
- one before/after contrast;
- one system diagram;
- one hero visual;
- one comparison axis;
- one progression / funnel;
- one quote / insight.

Supporting evidence must be visibly subordinate.

### 3. Hierarchy plan
Rank semantic objects into:
- `hero`
- `primary_support`
- `secondary_support`
- `annotation`
- `source`
- `decorative_only`

Hierarchy must control size, contrast, position, and whitespace—not merely font weight.

### 4. Composition archetype
Choose a reusable *composition grammar*, not a fixed screenshot template.

Initial Stage 4 families:
1. `editorial_hero`
2. `dominant_metric`
3. `product_stage`
4. `process_story`
5. `evidence_constellation`
6. `contrast_split`
7. `comparison_axis`
8. `funnel_or_progression`
9. `architecture_layers`
10. `timeline_journey`
11. `portfolio_map`
12. `terminal_ask`

These are hypotheses to be refined by reference forensics. Each archetype may expose variants rather than one frozen layout.

### 5. Spatial grammar
The Visual IR should describe relationships such as:
- dominant region / support region;
- alignment axes;
- overlap permissions;
- edge anchors;
- whitespace reservations;
- visual flow direction;
- relative scale ratios;
- image crop intent;
- grouping / proximity;
- optional asymmetry.

Coordinates are generated downstream.

### 6. Density strategy
Before rendering, classify the slide as `low`, `medium`, or `high` density.

Rules:
- low density: one focal idea, generous whitespace;
- medium density: several concise groups with a clear protagonist;
- high density: remove decoration and compress supporting detail before shrinking hierarchy-critical text.

No renderer may solve overload by indiscriminately reducing font sizes.

### 7. Style identity
A deck style is more than tokens. Stage 4 style profiles should include:
- palette and type tokens;
- identity anchors;
- recurring framing devices;
- image treatment;
- shape vocabulary;
- edge / border language;
- depth language;
- whitespace character;
- geometry character (soft, rigid, technical, editorial, kinetic, etc.);
- decoration budget;
- variation rules;
- anti-repetition rules.

### 8. Asset strategy
For each visual slot decide:
- native geometry;
- SVG/vector illustration;
- product screenshot;
- bounded generated image;
- icon / logo asset;
- chart / data graphic.

Generated assets must have a semantic exclusion contract (forbidden text, forbidden claims, forbidden badges, etc.).

## Composition archetype contract

Every archetype definition should eventually carry:

```json
{
  "archetype_id": "dominant_metric",
  "intent_fit": ["prove", "hook"],
  "content_shapes": ["one_primary_metric", "supporting_evidence"],
  "density_range": ["low", "medium"],
  "required_roles": ["hero"],
  "optional_roles": ["primary_support", "secondary_support", "annotation"],
  "max_items": 5,
  "spatial_grammar": {
    "focal_ratio_min": 2.2,
    "primary_axis": "horizontal",
    "whitespace_min": 0.22,
    "overlap_policy": "bounded"
  },
  "best_for": [],
  "avoid_for": [],
  "variation_tags": [],
  "anti_repetition": [],
  "renderer_capabilities": ["native", "svg", "bounded_image"]
}
```

The `max_items` and content budgets are constraints, not the reason to choose the archetype.

## Deck-level rhythm

Good individual slides can still make a bad deck. The Visual Director therefore needs a deck-level pass.

Required deck rhythm checks:
- adjacent slides should not reuse the same primary composition unless intentionally creating a sequence;
- hero position should vary with controlled rhythm;
- dense slides should be separated by visual relief when possible;
- full-bleed / split / contained compositions should alternate intentionally;
- repeated identity anchors should unify the deck without becoming wallpaper;
- transitions should create escalation toward the ask.

## Visual acceptance gate

Stage 4 must introduce a machine-recorded and human/multimodal visual gate. Structural QA alone is insufficient.

Minimum visual dimensions to score 1–5:
1. first-impression quality;
2. hierarchy clarity;
3. composition intentionality;
4. originality / non-generic feel;
5. information-to-space fit;
6. typography quality;
7. visual protagonist strength;
8. style coherence;
9. deck rhythm;
10. judge-room presentability.

Hard visual failures regardless of mean score:
- title/subtitle collision;
- unreadable primary text;
- accidental crowding / dead zones;
- equal-weight card soup with no protagonist;
- leaked IR/internal labels;
- invented semantic claims;
- generated text where native text was required;
- obvious template repetition across adjacent slides;
- decorative treatment that competes with evidence;
- visual that looks like a generic SaaS dashboard when the slide is not a dashboard.

## Stage 4 benchmark strategy

Do **not** beautify all three Stage 3 architecture variants.

Stage 4 will use the Stage 3 engineering winner as the implementation substrate:

> **Hybrid semantic-first architecture** — native text/information + editable vector structure + bounded generated richness.

Native-only remains a fallback lane; image-first remains a visual reference / adversarial benchmark, not the product architecture.

QueueZero remains the controlled benchmark because its semantic inputs are already frozen. We will redesign the same three slides after the Visual IR and archetype grammar are ready.

## Research program

Reference forensics should extract *portable visual reasoning*, not code volume.

Priority questions:
- How are style identity and layout identity represented?
- How is layout suitability described beyond page type?
- How are content capacity and density bounded?
- How is variation / anti-repetition encoded?
- How are visual samples approved before full-deck generation?
- How are templates distilled from reference decks?
- How does QA distinguish a usable slide from a beautiful slide?
- Which decisions belong in an LLM vs deterministic compiler?

Priority repositories initially:
- `JuneYaooo/gpt-image2-ppt-skills`
- `likaku/Mck-ppt-design-skill`
- additional Stage 1 leaders as evidence requires.

## Stage 4 exit criteria

Stage 4 is not complete until:

- Visual IR v1 is frozen after red-team review;
- at least 8–12 composition archetypes have explicit contracts and capacity limits;
- at least one deck style profile has identity anchors + variation + anti-repetition rules;
- a Visual Director can route frozen QueueZero semantics into Visual IR without emitting raw PPTX coordinates;
- a deterministic compiler can realize the Visual IR into our hybrid lanes;
- pixel renders pass structural QA and visual QA;
- redesigned QueueZero is materially stronger than the Stage 3 decks;
- routine editability remains at or above 0.90 normalized;
- no full-slide regeneration is required for normal edits;
- final output clears the human question: **"would submit this to win."**
