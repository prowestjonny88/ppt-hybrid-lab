# Visual IR — Draft V0

Status: DRAFT / NOT FROZEN

Purpose: introduce an explicit visual-composition representation between semantic Slide IR and renderer-specific plans.

This file is intentionally architecture-first. It must survive reference forensics and Ox red-team before becoming V1.

## Layer boundaries

### Semantic Slide IR owns
- factual claims;
- evidence and uncertainty;
- exact editable text and numbers;
- semantic object IDs;
- editability priority;
- relationships between information objects;
- asset semantic restrictions;
- source provenance.

### Visual IR owns
- communication moment;
- visual protagonist;
- hierarchy ranks;
- composition archetype;
- spatial relationships;
- density strategy;
- visual flow;
- visual grouping;
- style identity references;
- asset treatment intent;
- controlled variation;
- visual QA expectations.

### Render Plan owns
- implementation lane routing;
- capability checks;
- native/SVG/image decisions;
- compiler versions;
- fail-closed fallbacks.

### Realization owns
- exact PowerPoint object IDs;
- exact coordinates;
- exact crops;
- exact fonts after fitting;
- rendered object hashes;
- round-trip state.

Visual IR must therefore avoid becoming a disguised PPTX coordinate file.

## Proposed top-level schema

```json
{
  "schema_version": "visual-ir-v0",
  "slide_id": "validation-traction",
  "semantic_hash": "...",
  "communication": {},
  "hierarchy": {},
  "composition": {},
  "spatial_grammar": {},
  "density": {},
  "style": {},
  "asset_treatments": [],
  "groups": [],
  "deck_rhythm": {},
  "visual_guardrails": [],
  "qa_contract": {}
}
```

## 1. Communication

```json
{
  "communication": {
    "moment": "prove",
    "belief_shift": "Early evidence is strong enough to justify a semester pilot, but does not prove retention or market fit.",
    "emotional_register": ["confidence", "measured_optimism"],
    "reading_order": ["metric_weekly_intent", "metric_mae", "metric_students", "metric_cafeterias", "pilot_gate"]
  }
}
```

Allowed `moment` candidates for V0:
- `hook`
- `frame`
- `explain`
- `demonstrate`
- `prove`
- `compare`
- `transition`
- `ask`
- `close`

These are communication states, not page types.

## 2. Hierarchy

Every visible semantic object gets an explicit visual rank.

```json
{
  "hierarchy": {
    "protagonist": "metric_weekly_intent",
    "roles": {
      "title": "primary_support",
      "subtitle": "annotation",
      "metric_weekly_intent": "hero",
      "metric_mae": "primary_support",
      "metric_students": "secondary_support",
      "metric_cafeterias": "secondary_support",
      "pilot_gate": "primary_support",
      "source_note": "source"
    },
    "contrast_ratio_targets": {
      "hero_to_primary_support": 2.2,
      "primary_to_secondary": 1.35
    }
  }
}
```

Initial hierarchy role vocabulary:
- `hero`
- `primary_support`
- `secondary_support`
- `annotation`
- `source`
- `decorative_only`

Rules:
- exactly one `hero` by default;
- `decorative_only` may never contain a semantic claim;
- title does not automatically become the largest visible element;
- source always remains readable but visually subordinate.

## 3. Composition

```json
{
  "composition": {
    "archetype_id": "dominant_metric",
    "variant": "hero-left_proof-right_terminal-bottom",
    "selection_reason": "The weekly-use-intent metric is the strongest audience-facing demand signal; other evidence should validate rather than compete.",
    "content_capacity": {
      "density": "medium",
      "max_primary_items": 2,
      "max_secondary_items": 3
    }
  }
}
```

The `selection_reason` is retained for auditability but is not rendered.

## 4. Spatial grammar

Spatial grammar describes constraints and relationships rather than absolute positions.

```json
{
  "spatial_grammar": {
    "primary_axis": "horizontal",
    "flow": "left_to_right_then_down",
    "zones": [
      {
        "zone_id": "hero_zone",
        "importance": 1.0,
        "preferred_area": 0.34,
        "edge_anchor": "left",
        "contains": ["metric_weekly_intent"]
      },
      {
        "zone_id": "proof_zone",
        "importance": 0.75,
        "preferred_area": 0.36,
        "relation_to": "hero_zone",
        "relation": "right_of",
        "contains": ["metric_mae", "metric_students", "metric_cafeterias"]
      },
      {
        "zone_id": "terminal_zone",
        "importance": 0.7,
        "preferred_area": 0.12,
        "relation_to": "hero_zone",
        "relation": "below_span",
        "contains": ["pilot_gate"]
      }
    ],
    "whitespace": {
      "minimum_fraction": 0.20,
      "protected_between_zones": true
    },
    "overlap": {
      "allowed": false
    }
  }
}
```

Candidate relationships:
- `left_of`
- `right_of`
- `above`
- `below`
- `below_span`
- `inside`
- `overlap_bounded`
- `aligned_left`
- `aligned_right`
- `aligned_center`
- `shares_baseline`
- `radial_around`
- `follows_path`

The compiler converts these into exact normalized coordinates.

## 5. Density

```json
{
  "density": {
    "class": "medium",
    "content_budget": {
      "hero_items": 1,
      "primary_support_items": 2,
      "secondary_support_items": 3,
      "annotation_lines": 2
    },
    "overflow_policy": [
      "remove_nonsemantic_decoration",
      "compress_secondary_support",
      "switch_archetype",
      "fail"
    ],
    "forbidden_overflow_policy": [
      "shrink_all_text"
    ]
  }
}
```

Text fitting remains downstream, but Visual IR must state what can be sacrificed before typography hierarchy is damaged.

## 6. Style reference

Visual IR references a separate deck style profile.

```json
{
  "style": {
    "profile_id": "queuezero-hackathon-v1",
    "identity_anchor_refs": ["precision_grid", "electric_blue_signal", "soft_product_depth"],
    "decoration_budget": "low",
    "shape_vocabulary": ["flat_panel", "hairline_rule", "soft_rounded_crop"],
    "image_treatment": "editorial_product",
    "variation_tags": ["asymmetric", "large_type"]
  }
}
```

The style profile should contain:
- tokens;
- identity anchors;
- image language;
- geometric language;
- whitespace character;
- depth rules;
- variation rules;
- anti-repetition rules;
- forbidden aesthetics.

## 7. Asset treatment

```json
{
  "asset_treatments": [
    {
      "semantic_object_id": "hero_visual_slot",
      "role": "bounded_generated_hero",
      "visual_weight": 0.75,
      "crop_intent": "scene_concentrated_lower_right",
      "background_behavior": "blend_with_surface",
      "edge_behavior": "soft_crop",
      "text_policy": "forbidden",
      "semantic_exclusions": [
        "numeric wait labels",
        "invented signage claims",
        "logos"
      ]
    }
  ]
}
```

## 8. Groups

Groups define visual units while preserving individual semantic object identity.

```json
{
  "groups": [
    {
      "group_id": "technical_proof",
      "members": ["metric_mae", "metric_students", "metric_cafeterias"],
      "visual_relation": "support_cluster",
      "internal_hierarchy": ["metric_mae", "metric_students", "metric_cafeterias"]
    }
  ]
}
```

Groups may influence local layout but may not erase semantic identity.

## 9. Deck rhythm

Per-slide Visual IR may receive deck-relative constraints:

```json
{
  "deck_rhythm": {
    "previous_archetype": "process_story",
    "avoid_archetypes": ["process_story"],
    "preferred_change": "increase_visual_protagonist_scale",
    "hero_anchor_preference": "left",
    "rhythm_role": "proof_peak"
  }
}
```

The deck-level planner owns the actual rhythm policy; this section records resolved slide-local consequences.

## 10. Visual guardrails

Guardrails convert qualitative design failures into explicit rejection rules.

```json
{
  "visual_guardrails": [
    {
      "id": "single_protagonist",
      "rule": "No secondary metric may visually equal or exceed metric_weekly_intent."
    },
    {
      "id": "intent_not_retention",
      "rule": "Do not visually badge weekly-use intent as retention or market fit."
    },
    {
      "id": "no_card_soup",
      "rule": "Do not render all four metrics as equal cards."
    }
  ]
}
```

## 11. QA contract

```json
{
  "qa_contract": {
    "hard_fail": [
      "semantic_leakage",
      "title_collision",
      "unreadable_primary_text",
      "multiple_equal_protagonists",
      "invented_claim",
      "forbidden_generated_text"
    ],
    "visual_targets": {
      "first_impression_min": 4,
      "hierarchy_min": 4,
      "composition_min": 4,
      "presentability_min": 4,
      "overall_mean_min": 4.0
    }
  }
}
```

## Archetype V0 candidates

These are hypotheses, not frozen templates.

### `editorial_hero`
One large narrative visual or scene with tightly controlled headline/support copy. Best for hook/problem/emotional framing.

### `dominant_metric`
One oversized number or quantified conclusion dominates; smaller proof cluster validates it. Best for traction, impact, economics.

### `product_stage`
One product screenshot/demo frame is the protagonist; annotations orbit or sequence around it. Best for demo and product experience.

### `process_story`
Directional sequence with one emphasized transformation point and a terminal outcome. Best for how-it-works / workflow.

### `evidence_constellation`
One thesis in the visual center or edge anchor, with heterogeneous evidence arranged around it using differentiated weights. Best when evidence types differ.

### `contrast_split`
Two intentionally opposed fields. Best for before/after, old/new, pain/solution, manual/automated.

### `comparison_axis`
Entities placed on one or two semantic axes with one highlighted wedge. Best for competition or positioning.

### `funnel_or_progression`
Tapered or staged progression from broad input to proof/output. Best for validation funnel or adoption progression.

### `architecture_layers`
Stacked or nested structural model with deliberate depth hierarchy. Best for technical architecture/platform layers.

### `timeline_journey`
Temporal or maturity path with one emphasized current/next state. Best for roadmap, rollout, evolution.

### `portfolio_map`
Common core plus differentiated modules / use cases / segments. Best for product portfolio or expansion map.

### `terminal_ask`
A clear destination / ask with only the minimum evidence required to support action. Best for pilot/CTA/closing.

## Compiler responsibilities

A Visual IR compiler should:
1. validate archetype capacity;
2. solve zone geometry from relational constraints;
3. map hierarchy to scale/contrast tokens;
4. select component variants compatible with content length;
5. route visual objects through capability registry;
6. preserve semantic object IDs;
7. emit deterministic normalized boxes into the renderer-specific plan;
8. fail rather than silently collapse hierarchy.

The compiler should **not** invent semantic content or choose the governing claim.

## Open questions for forensics / red-team

1. Is `moment` the right routing dimension or should it be decomposed into rhetorical goal + proof type?
2. How much geometry should Visual IR expose before it becomes too renderer-specific?
3. Should archetype variants be hand-authored, learned/distilled from references, or both?
4. How should a style profile declare valid archetype variants?
5. How should visual diversity be measured across a deck without rewarding arbitrary variation?
6. Which visual QA checks can be deterministic vs multimodal?
7. Can we score focal dominance and whitespace reliably from rendered pixels?
8. How should user-provided templates override Visual IR while preserving semantic editability?
9. How should title length influence composition selection before local font fitting?
10. What is the minimum archetype library that covers hackathon decks without collapsing into generic templates?
