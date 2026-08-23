# task-007 — Visual System Forensics: gpt-image2-ppt-skills @ 2d57ef8

**Worker:** ox-alpha · **Status:** Analysis complete within bounded context · **No repositories modified**

---

## 0. Scope & Evidence Limitations (read first)

Supplied context: **43 files**, all of them `styles/**/*.layouts.json` (1 `initial/` hand-authored style + 42 `xiamulingzi/` distilled styles). The following high-value paths appear in the eligible inventory but were **NOT supplied**, so every question touching pipeline mechanics, prompts, approval flow, editing, and QA tooling is **UNKNOWN** below:

- `SKILL.md`, `README.md`, `styles/README.md`
- `docs/distilled-styles.md`, `docs/ppt-implementation-logic.md`, `docs/workflow.md`, `docs/edit_guide.md`, `docs/external_image_overlay_logic.txt`
- `scripts/template_analyzer.py`, `scripts/render_template.py`, `scripts/generate_ppt.py`, `scripts/image_generator.py`, `scripts/md_to_plan.py`, `scripts/runtime_profile.py`
- `scripts/editable_pptx/*` (scene/layers/renderer/workflow/poc/provider/masking)
- `examples/*/recipe.md`, `examples/*/slides_plan.md`, `examples/editable-pptx*/**.scene.json`, `case05-summer-poster/quality-report.json`
- The `.md` sibling of every `.layouts.json` (style cards) — none supplied

Everything below tagged **[D]** is read directly from the supplied `.layouts.json` corpus. Claims about *how* these artifacts are produced/consumed are **[I]** or **UNKNOWN** unless a script/doc is fetched.

---

## 1. Executive Summary — 10 most portable Stage 4 ideas

1. **Identity anchors as first-class, cross-slide, vector-implementable style atoms** (`theme.identity_anchors[]`). Most anchors are literally DrawingML/SVG primitives: color blocks, thick border frames, rotated marginalia, dot matrices, pill buttons, notch cutouts, shadow overlays. This is the single strongest mechanism for deck-wide consistency *without* full-slide rasters. [D]
2. **Two-layer style identity: prose positioning + structured theme tokens** (`global_style` + `theme.{palette, identity_anchors, density_rules, variation_rules, anti_repetition_rules}`). Port the structure; keep prose only as generator flavor text. [D]
3. **Machine-enforceable content contracts via per-layout JSON Schema** (`json_schema` with `minLength/maxLength/minItems/maxItems/required/additionalProperties:false`) — deterministic pre-flight validation of slide payloads *before* any visual generation. [D]
4. **Routing predicates separate deterministic shortlisting from model judgement**: `routing.content_shapes` (~21-token vocabulary) + `requires` + `min_items/max_items`, layered on top of the older pure-judgement `best_for/avoid_for`. The repo itself evolved from model-only to hybrid routing — evidence both regimes coexist. [D]
5. **Normalized external image slots** `{id, purpose, bbox[x,y,w,h], priority}` decouple photography from composition — directly portable to bounded-asset workflows. [D]
6. **Deck-rhythm controls**: `variation_tags[]`, `reuse_friendly` + `reuse_reason` ("Distinctive rhythm page" ⇒ once-per-deck), bookend/mirror relationships between cover and closing. [D]
7. **Anti-repetition as an explicit rule, not a hope**: `anti_repetition_rules: ["Do not repeat the same primary composition or decoration placement on adjacent slides."]` — identical text in every distilled style; should become a *checker*, not a prompt line. [D→R]
8. **Clean-room discipline baked into data**: every distilled layout carries `"copying source assets, source text, or an exact source arrangement"` inside `avoid_for`. Non-copying is enforced at the artifact level. [D]
9. **Provenance chain**: `source: "local-pptx-distillation"`, `source_hash` (sha256), per-layout `evidence_pages`, `page_index`, hash embedded in filename. Traceability from distilled grammar back to source pages. [D]
10. **Adaptation-over-cloning pattern**: when a source deck had no native table/timeline composition, the distiller wrote `"Adapt the source-supported grid into a table or timeline: <base composition>"` — the repository *itself admits* layouts are grammars to be rezoned, not frozen frames. [D]

---

## 2. DIRECT EVIDENCE

### 2.1 Top-level style-file contract (both generations coexist under `"version": "2"`)

| Field | initial/ (hand-authored) | xiamulingzi/ (distilled) | Citation |
|---|---|---|---|
| `version` | `"2"` | `"2"` | editorial-mono L2; all distilled files |
| `style_id` | ✓ | ✓ (= filename stem) | both |
| `style_name` | ✓ | ✗ | editorial-mono |
| `global_style` | long prose incl. usage-fit + color law | 1-line English gist | editorial-mono; 4f02fb97 |
| `source` | ✗ | `"local-pptx-distillation"` | 4f02fb97 |
| `source_hash` | ✗ | sha256 hex; also embedded in filename | 4f02fb97 `4f02fb9712e6…`; filename `…-1-4f02fb97.layouts.json` |
| `theme.primary/accent/background/fonts` | present but **all empty strings** | ✗ (replaced by `palette`) | editorial-mono `theme` block |
| `theme.palette[]` | ✗ | hex array (2–6 colors) | 4f02fb97 `[“#D6D6D6”,…]`; 26b85a39 has only 2 |
| `theme.identity_anchors[]` | ✗ | 3–5 prose strings | 4f02fb97; 242aaa71 (incl. *negative* anchor “Complete absence of gradients, shadows, or 3D effects”) |
| `theme.density_rules{low,medium,high}` | ✗ | prose triplet, **byte-identical across all 42 files** | 4f02fb97 ≡ f0e2c8d9 ≡ … |
| `theme.variation_rules[]` | ✗ | 1 string, byte-identical across corpus | all distilled |
| `theme.anti_repetition_rules[]` | ✗ | 1 string, byte-identical across corpus | all distilled |

### 2.2 Layout-object contract

| Field | initial | distilled | Notes / citation |
|---|---|---|---|
| `id` | ✓ | ✓ | e.g. `cover-primary`, `data-table` |
| `page_type` | cover/agenda/section/content/data/quote/closing | same set (+`agenda` in some) | editorial-mono; 5-b077b49a has `agenda-primary` |
| `semantic_role` | ✗ | ✓ — **always equal to `page_type`** (redundant) | 4f02fb97 |
| `page_index` | ✗ | ✓ source page number | 4f02fb97 |
| `summary` | bespoke prose | prose; `data-table` always prefixed `"Adapt the source-supported grid into a table or timeline: "` | 4f02fb97 `data-table`; 6-a9084536 `data-table` |
| `visual_signature` | short label (“封面主视觉”) | **composite prompt fragment**: `<summary> \| zones=["…"] \| anchors=<a1>; <a2>` | editorial-mono vs 4f02fb97 |
| `content_capacity` | free-text map (`"title": "8-18 个中文字符"`) — **not machine-parseable** | `{density: low\|medium\|high\|"very low", max_items: int}` | editorial-mono; 4f02fb97; off-enum `"very low"` in 19c402f9 `closing-primary` |
| `best_for[] / avoid_for[]` | ✓ | ✓ + universal clause `"copying source assets, source text, or an exact source arrangement"` appended to **every** layout | editorial-mono; 4f02fb97 |
| `variation_tags[]` | ✓ | ✓ | both |
| `external_image_slots[]` | `[]` everywhere | `{id, purpose, bbox:[x,y,w,h] normalized, priority:int}`; 0–6 slots; full-bleed `[0,0,1,1]` seen | 4f02fb97 `hero` bbox `[0.45,0.15,0.5,0.7]`; 17-fd10f39c `hero-bg [0,0,1,1]`; 32-75711782 six-tile grid |
| `reuse_friendly` / `reuse_reason` | ✓ / bespoke prose | ✓ / boilerplate: false⇒“Distinctive rhythm page”, true⇒“Reusable with variation rules” | editorial-mono bespoke; 4f02fb97 boilerplate |
| `json_schema` | ✓ full JSON Schema per layout | ✗ | editorial-mono only |
| `routing` | ✗ | `{content_shapes[], requires?[], min_items?, max_items?}` | 4f02fb97 |
| `evidence_pages[]` | ✗ | ✓ e.g. `["page-00"]` | 4f02fb97 |
| `validation_default` | ✗ | `false` in **every** observed layout | all distilled |
| `reference_image` | ✗ | `null` in **every** observed layout | all distilled |

### 2.3 Routing vocabulary (observed `content_shapes` tokens)

`hero, title-subtitle, section-divider, bullets, cards, grid, comparison, before-after, metrics-series, chart, trend, table, timeline, milestone, quote, testimonial, closing, call-to-action, contact, agenda, numbered-list` — with `requires` predicates: `"paired groups"`, `"metrics or series"`, `"table or timeline"`. [D — 4f02fb97, f0e2c8d9, 19c402f9, 5-b077b49a, 15-b12ea38a, 37-45157cb4]

### 2.4 Machine-checked capacity (initial generation only)

- `cover-hero-composition.json_schema`: `title maxLength 24`, `subtitle maxLength 56`, `meta maxLength 40`, `required:["title"]`, `additionalProperties:false`. [D — editorial-mono]
- `agenda-structured-overview`: `items minItems 3 maxItems 6`, item `name maxLength 18`, `description maxLength 36`. [D]
- `data-visual-callouts`: `metrics minItems 2 maxItems 5`, `metric maxLength 14`. [D]
- `quote-statement-focus`: `quote minLength 6 maxLength 56`. [D]
- `closing-summary-contact`: `contact maxLength 90`. [D]

### 2.5 Identity-anchor taxonomy (sampled, all [D])

- Texture/shadow: foliage shadow overlay (4f02fb97), film grain (820c7100), dappled window light (47347745), leaf shadows (b077b49a, 5d8944ef, 39-7f77a308, 20-d5a94cd5)
- Geometry: corner blobs (c9574110, 12-c2928b30, 3-1ccdba09, 16-9ad7d5dd), diamonds (15-b12ea38a), cropped circles/rings (242aaa71), notches (31-9b25a819), letterform mask “D-shape” (35-1dc1d3b3)
- Frame/edge: thick outer border every slide (1-8dc42f63), dual-color left band (15-26be2d46), vertical margin text (32-75711782, 18-dab5f352, 22-5b38446b), thin nav header/footer (35-1dc1d3b3), rotated marginalia (26-0ba94a68)
- Motif: three-dot ◆◆◆ (2-6fda302a), 3-dot rust/sand/mustard (b077b49a, 820c7100), offset black circle strokes (f0e2c8d9), dashed confetti (8-a694ca1e), 3×3 dot matrix (c9574110), oversized quotation marks (33-af429968), pagination markers (22-5b38446b)
- Typography: underscore-prefixed serif headers (19c402f9), extreme scale contrast (756e8b62, 35-1dc1d3b3), wide-tracked uppercase (27-aac790a5, 39-7f77a308), brush-script pairing (14-1678fc3d), vertical rotated caps (21-1d3a03bb)
- Negative constraints: “Complete absence of gradients, shadows, or 3D effects” (242aaa71); editorial-mono “每份 deck 只允许一种 accent 色” and “暖白 #FAF8F2 或墨黑 #1A1A1A（每份 deck 选一种，不混用）” [D]

### 2.6 Defect-aware curation (QA knowledge stored as avoidance)

`linzi-morandi-2-21-35-ppt-ppt-4-349295b8.layouts.json` → `closing-primary.summary`: *"Identical structure to the cover page but with severe text clipping at the bottom edge"*; `avoid_for`: *"Any slide requiring legible text at the bottom"*. The distiller visually reviewed source pages and encoded an observed rendering failure as a routing exclusion. [D]

### 2.7 Observed data-quality debt (matters for any port)

- Same `summary`/`visual_signature`/slots cloned across roles within one style: `data-metrics` ≡ `content-content` in 4f02fb97, 47347745, 242aaa71, 3e234ad9, af429968, 485ae190, 1d3a03bb, 6fda302a, 75711782, 9b25a819, 45157cb4, 7f77a308, 26be2d46(partial), a3030c28. [D]
- `content_capacity.max_items` conflicts with `routing.max_items`: d980ea26 `content-content` 9 vs 6; c9574110 `data-metrics` 25 (five-column table). [D]
- Duplicate `evidence_pages` across layouts of one style (e.g., `page-01` claimed by 3+ layouts in several files; 15-b12ea38a `closing-primary.evidence_pages=["page-01"]` collides with its own `section-primary`). [D]
- Missing roles in some styles (aac790a5 has no closing; 242aaa71, 22-5b38446b, 25-5d8944ef, 26b85a39 have no agenda/quote). [D]
- `editorial-mono.global_style` ends mid-hex `#B8860` — truncated at write time. [D]
- `theme` block entirely empty strings in editorial-mono despite rich prose `global_style`. [D]
- Registry explosion: ~300+ near-duplicate style files under `xiamulingzi/`, most sharing the same boilerplate rule triplets; granularity is *per source deck*, not per design language. [D from inventory + files]

---

## 3. INFERENCE (derived from artifacts; mechanism not directly observed)

- **[I-1] `visual_signature` is a prompt fragment, not metadata.** Its exact format `<summary> | zones=[...] | anchors=a; b; c` appears verbatim-consistent across all 42 distilled files, suggesting the distillation pipeline emits it specifically for injection into an image-generation prompt. The initial generation’s short labels suggest an older prompt strategy.
- **[I-2] Density/variation/anti-repetition rule triplets are pipeline boilerplate**, not per-style analysis: byte-identical across 42 independently hashed source decks. Their informational value is the *concept*, not the text.
- **[I-3] `reuse_friendly:false` ⇒ intended once-per-deck usage.** editorial-mono states it plainly (“建议同一 deck 只使用一次”); distilled files compress it to “Distinctive rhythm page”. Combined with cover/closing “Mirror of…” summaries, this implies a deck-rhythm model: unique anchors at open/close, rotating reusable bodies between.
- **[I-4] Routing execution is hybrid**: `content_shapes`/`requires`/min-max are cheaply evaluable predicates (deterministic shortlist), while final selection among survivors plausibly falls to the LLM using `best_for/avoid_for/summary`. The executor code is not supplied — UNKNOWN.
- **[I-5] `validation_default:false` likely means “do not run per-layout validation by default”**, implying a validation mode exists somewhere (probably `scripts/template_analyzer.py` or `generate_ppt.py`). Semantics UNKNOWN.
- **[I-6] `reference_image:null` is a reserved hook** for pinning a rendered exemplar per layout; unused in this corpus. If populated elsewhere, it would be a raster-freeze vector — see Reject §6.
- **[I-7] The distiller maps each source deck onto a canonical role skeleton** (cover, section, content×1–2, data×2, optional quote/agenda, closing) and assigns best-fitting observed compositions, cloning when the source lacked variety — explaining §2.7 duplication. The *role skeleton* is the stable part; the *composition instances* are samples.
- **[I-8] Anchor persistence language (“persistent”, “permanently fixed”, “across almost every slide”) implies a continuity contract** the generator is expected to honor on every page — exactly the property an editable-object pipeline can guarantee deterministically (place the anchor layer once per master) whereas a per-slide image model can only approximate.

---

## 4. Question-by-question findings

**Q1 Structured representations** — Fully answered in §2 (tables 2.1–2.5). Everything that exists is in the `.layouts.json` contract; no other structured visual artifact was supplied.

**Q2 Distillation pipeline** — Inputs/outputs evidenced ([D]: `source`, `source_hash`, `evidence_pages`, filename-hash binding, boilerplate rule injection, role-skeleton mapping, defect encoding). Prompts, intermediate renders, and validation steps: **UNKNOWN**. Follow-up: `scripts/template_analyzer.py`, `scripts/render_template.py`, `docs/distilled-styles.md`.

**Q3 Routing determinism vs model judgement** — Data side fully evidenced (§2.3). Executor: **UNKNOWN**. Note the corpus preserves *both* regimes: initial styles route purely by `best_for/avoid_for` (model judgement), distilled styles add predicates (hybrid). Recommended reading: `scripts/generate_ppt.py`, `scripts/md_to_plan.py`.

**Q4 Preview/approve one sample before full deck** — **UNKNOWN.** Nothing in the supplied artifacts references sampling, approval, or per-slide iteration. Likely documented in `SKILL.md` / `docs/workflow.md` / `scripts/image_generator.py`. The `examples/editable-pptx-poc/demo1-cover.scene.json` (single-cover scene) hints at a one-slide-first PoC but was not supplied.

**Q5 Cross-slide variation / anti-repetition / rhythm** — Represented, not enforced (within supplied evidence): theme-level rules [D], per-layout `reuse_friendly` [D], `variation_tags` [D], bookend mirroring [D]. No numeric constraints (e.g., “same archetype ≥ N apart”) anywhere. Whether any code computes adjacency: **UNKNOWN**.

**Q6 Versioning / edit / regenerate / rollback / visual review** — **UNKNOWN** from supplied context. Candidates: `docs/edit_guide.md`, `scripts/editable_pptx/workflow.py`, `examples/editable-pptx/case05-summer-poster/quality-report.json`. The only versioning signal in supplied data is `"version":"2"` on style files [D].

**Q7 What QA is machine-derived vs prompt/human** — From supplied data: machine-checkable today = payload JSON Schema conformance, item counts, text budgets, accent/background laws (all [D] as *contracts*; whether validators run is UNKNOWN). Render-derived QA: none evidenced except defect-encoding into `avoid_for` (§2.6). Everything else (anchor adherence, style fidelity) is prompt-guidance-class [I-1].

**Q8 Useful without full-slide images** — Nearly the entire *descriptive* layer ports cleanly: anchors (mostly vector-implementable), palettes, typography treatments, zone bboxes, capacity contracts, routing predicates, rhythm policy, provenance. See §5.

**Q9 Reject list** — §6.

---

## 5. RECOMMENDATION → ppt-hybrid-lab Stage 4

| # | Recommendation | Basis |
|---|---|---|
| R1 | Make **identity anchors** the consistency backbone: render them as a persistent per-master object layer (editable shapes), never as baked pixels. Tag each anchor `implementable_as: vector \| image \| raster-overlay` and forbid `raster-overlay` for anything carrying text. | [D anchors] + [I-8] |
| R2 | Adopt **JSON-Schema content contracts per archetype** (from the initial generation) as the *only* capacity mechanism; delete free-text `content_capacity` strings. Validate payloads before any generation call. | [D §2.4 vs §2.2] |
| R3 | Implement routing as **two stages**: deterministic predicate filter (`content_shapes ∩ requires ∩ item-count`) → model choice among survivors scored by `best_for/avoid_for`. Log the survivor set per slide for auditability. | [D §2.3] + [I-4] |
| R4 | Convert anti-repetition from prompt text to a **deck-level constraint solver/checker**: no identical `archetype_id+variation_signature` on adjacent slides; rhythm pages (`reuse_friendly:false`) used ≤1×; cover/closing may mirror deliberately. | [D rules] + [R] |
| R5 | Keep **normalized bbox slots** for imagery, but add `flexible` and `aspect_lock` flags so an editable renderer can reflow zones instead of failing when content shape differs. | [D bbox] + [R] |
| R6 | Treat distilled corpora as **noisy evidence, not gospel**: dedupe boilerplate, reconcile `max_items` conflicts (take `min(capacity, routing)`), drop redundant `semantic_role`, repair `evidence_pages` collisions before ingesting. | [D §2.7] |
| R7 | Collapse the per-deck style explosion into a **two-tier registry**: DesignLanguage (Morandi-editorial, Swiss-grid, …) → DeckStyleProfile (palette instantiation, accent choice, background mode). Filename-hash provenance preserved at the profile level. | [D §2.7 registry explosion] + [R] |
| R8 | Encode **negative style laws** (single accent, single background mode, “no gradients/shadows/3D”) as first-class constraint fields with validators, not prose. | [D §2.5] |
| R9 | Preserve the **adaptation pattern**: archetypes declare `adaptable_to: [table, timeline]` with a rezone method, instead of fabricating fake “table templates”. | [D data-table prefix] |
| R10 | Carry **defect-encoding forward as QA seeds**: observed failure modes (bottom-edge clipping) become named render-QA checks, not `avoid_for` folklore. | [D §2.6] |

---

## 6. REJECT / DO NOT PORT

1. **Full-slide generated raster as the semantic carrier** — the repo’s core architecture; explicitly out of scope for Stage 4. All text baked into pixels is unrecoverable, uneditable, and unvalidatable against our content contracts.
2. **`reference_image` per layout** — a pixel-pin hook; even reserved, it invites freezing compositions. Do not carry the field into the archetype registry.
3. **Boilerplate rule triplets as “per-style intelligence”** — importing 42 copies of identical `density_rules/variation_rules/anti_repetition_rules` strings adds noise masquerading as analysis. Extract the concepts once.
4. **Free-text `content_capacity`** — unparseable bilingual strings (“8-18 个中文字符”); superseded by JSON Schema budgets.
5. **Empty `theme` token blocks (initial generation)** — style identity living only in prose is unenforceable; reject the pattern, keep the prose as flavor.
6. **`validation_default:false` + `semantic_role` redundancy** — dead/vestigial fields; do not import schema debt.
7. **Per-deck style-file granularity** — hundreds of near-duplicate registries; reject as an authoring model.
8. **Unconstrained generated text inside visuals** — anything that relies on the image model rendering copy (titles, metrics) is incompatible with semantic-first editing; our text must live in IR objects above the canvas.

---

## 7. Proposed clean-room Stage 4 schema fragments

Provenance tags: **[D]** direct evidence in supplied corpus · **[I]** inference · **[R]** recommendation (new engineering).

### (a) DeckStyleProfile

```jsonc
{
  "schema_version": "3",                          // [R] repo drifted within "2"; bump & lock
  "style_id": "morandi-editorial@v3",             // [D pattern: style_id] [R: language-tier id]
  "name": "Morandi Editorial",                    // [D: style_name]
  "provenance": {
    "origin": "authored | distilled",             // [R] made explicit; [D] implicit via source field
    "sources": [{"kind":"pptx","ref":"…","sha256":"…"}],   // [D: source/source_hash]
    "evidence_pages": ["page-00","page-01"]       // [D: evidence_pages]
  },
  "positioning": "…one-paragraph gist…",          // [D: global_style (distilled form)]
  "audience_fit": ["brand launch","lookbook"],    // [D: global_style tail "适合…"] [R: structured]
  "color": {
    "palette": [{"hex":"#DE5A4E","role":"accent"}],         // [D: theme.palette] [R: roles]
    "accent_budget": 1,                                      // [D: editorial-mono 单一 accent 法则]
    "background_modes": [
      {"name":"warm-paper","hex":"#FAF8F2","exclusive_in_deck":true},
      {"name":"ink","hex":"#1A1A1A","exclusive_in_deck":true}
    ]                                                        // [D: 不混用法则] [R: enum]
  },
  "typography": {
    "families": {"title":"serif-display","body":"sans"},     // [D partial: theme.fonts; anchors]
    "scale_contrast": "extreme",                             // [D: 756e8b62 / 35-1dc1d3b3 anchors]
    "treatments": ["underscore-prefixed-headers","rotated-caps","wide-tracking"] // [D: anchors]
  },
  "identity_anchors": [{
    "id":"leaf-shadow-overlay",
    "kind":"texture|motif|geometry|typography|shadow|frame|edge",   // [R taxonomy; D instances]
    "description":"…",                                       // [D]
    "persistence":"every_slide | structural",                // [I-8 from 'persistent' wording]
    "implementable_as":"vector | image | raster-overlay",    // [R portability triage]
    "text_bearing": false                                    // [R safety]
  }],
  "density_policy": {"low":"…","medium":"…","high":"…"},     // [D concepts] [R structured]
  "variation_axes": ["image-text-balance","emphasis","mirror"],// [D: variation_rules] [R enumerated]
  "anti_repetition": {
    "adjacent_same_composition": "forbid",                   // [D rule text]
    "rhythm_page_max_uses": 1                                // [I-3] [R]
  },
  "forbidden": ["gradients","drop-shadows","3d-effects",     // [D: 242aaa71 negative anchor]
                ">1 accent color","mixed background modes"]  // [D: editorial-mono]
}
```

### (b) CompositionArchetype registry entry

```jsonc
{
  "archetype_id": "split-hero-right",            // [D: layout.id pattern]
  "semantic_roles": ["cover","closing"],         // [D: page_type/semantic_role] [R: multi-role legal]
  "zone_grammar": [{
    "zone_id":"hero", "accepts":"image",
    "bbox_hint":[0.45,0.15,0.5,0.7],             // [D: external_image_slots.bbox]
    "priority":1,                                 // [D: slot.priority]
    "flexible":true, "aspect_lock":false          // [R: enable reflow]
  },{
    "zone_id":"title","accepts":"text","bbox_hint":[0.05,0.2,0.35,0.4],
    "flexible":true
  }],
  "content_contract": { /* JSON Schema */ },     // [D: json_schema (initial)] [R: mandatory for all]
  "routing": {
    "content_shapes":["hero","title-subtitle"],  // [D: routing.content_shapes]
    "requires":[],                               // [D: routing.requires]
    "items":{"min":1,"max":2}                    // [D: routing.min/max_items]
  },
  "capacity": {
    "density":"low",                              // [D: content_capacity.density]
    "max_items": 2,                               // [D] [R: reconcile w/ routing → min()]
    "text_budgets":{"title":{"min":2,"max":24}}   // [D: json_schema maxLength]
  },
  "variation": {
    "tags":["hero-image","asymmetrical"],         // [D: variation_tags]
    "mirrors": null,                              // [D: 'Mirror of the cover' summaries] [R: typed]
    "transforms":["flip-x","swap-sides","reweight","accent-swap"] // [R: operationalized]
  },
  "reuse_policy": {"friendly":false,"reason":"rhythm-page","max_uses_per_deck":1}, // [D]+[I-3]
  "adaptable_to": [{"role":"table","method":"rezone"},{"role":"timeline","method":"rezone"}], // [D: data-table adapt pattern]
  "evidence": {"style_ids":["4f02fb97"],"pages":["page-00"]}  // [D: evidence_pages]
}
```

### (c) SlideVisualIR

```jsonc
{
  "slide_id":"s07", "deck_id":"d01",
  "style_ref":"morandi-editorial@v3",             // [R]
  "archetype_ref":"split-hero-right",             // [R]
  "instance": {
    "variation_selected":{"tags":["asymmetrical"],"transforms":["swap-sides"],"mirrored_of":null}, // [I-3][R]
    "zones":[{"zone_id":"hero","bbox":[0.45,0.15,0.5,0.7],"z":2}]  // [R: resolved geometry]
  },
  "content": { /* conforms to archetype.content_contract */ },       // [D basis]
  "assets":[{"slot_id":"hero","asset_ref":"img_0142|null",
             "origin":"user|generated|stock","license":"…"}],        // [D slot ids][R lifecycle]
  "text_policy":{"text_inside_raster":false},     // [R hard rule]
  "generation":{
    "attempts":[{"n":1,"prompt_ref":"p_88","params":{},"artifact_ref":"a_1","qa":"fail:clip-bottom"},
                 {"n":2,"prompt_ref":"p_89","artifact_ref":"a_2","qa":"pass"}],
    "accepted":2,
    "parent_version":"s07@v1"                     // [R; repo mechanism UNKNOWN]
  },
  "qa":{"state":"approved","checks":["qa-004","qa-007"]}  // [R]
}
```

### (d) VisualQAContract (check catalog seeded from evidence)

```jsonc
{"checks":[
 {"id":"qa-001","layer":"schema","evaluator":"deterministic","blocking":true,
  "spec":"payload validates against archetype.content_contract"},          // [D §2.4]
 {"id":"qa-002","layer":"capacity","evaluator":"deterministic","blocking":true,
  "spec":"item_count within min(routing.items, capacity.max_items)"},      // [D + §2.7 conflict fix]
 {"id":"qa-003","layer":"style","evaluator":"deterministic","blocking":true,
  "spec":"accent_count <= style.color.accent_budget; single background_mode"}, // [D editorial-mono]
 {"id":"qa-004","layer":"rhythm","evaluator":"deterministic","blocking":true,
  "spec":"no identical (archetype, variation_signature) on adjacent slides; rhythm pages <=1"}, // [D rule][R impl]
 {"id":"qa-005","layer":"style","evaluator":"deterministic","blocking":true,
  "spec":"every identity_anchor with persistence=every_slide present in master layer"}, // [I-8][R]
 {"id":"qa-006","layer":"render","evaluator":"deterministic","blocking":true,
  "spec":"slot bbox containment + aspect tolerance on rendered geometry"}, // [D bbox][R]
 {"id":"qa-007","layer":"render","evaluator":"deterministic","blocking":true,
  "spec":"no text clipped at canvas edges (regression: 349295b8 bottom-clip)"}, // [D §2.6][R]
 {"id":"qa-008","layer":"render","evaluator":"deterministic","blocking":false,
  "spec":"WCAG contrast ratio for text zones"},                            // [R]
 {"id":"qa-009","layer":"perceptual","evaluator":"vlm","blocking":false,
  "spec":"anchor adherence + style fidelity vs DeckStyleProfile"},         // [R; repo today = prompt-only, I-1]
 {"id":"qa-010","layer":"policy","evaluator":"deterministic","blocking":true,
  "spec":"zero glyphs inside raster assets"}                               // [R]
]}
```

---

## 8. Critique: “fixed templates” vs grammar/constraint system

The corpus argues **both ways**, and the split is instructive:

**Where the repo already behaves like a grammar (port this):**
- Theme-level invariants (anchors, palette ratios, density ladder) held constant while compositions vary — the declared intent of `variation_rules` (“Vary image/text balance and emphasis **while preserving anchors, grid, and color ratios**”). [D]
- Explicit adjacency non-repetition rule ⇒ compositions are *samples from a distribution*, not repeated stamps. [D]
- `variation_tags` as a transform vocabulary; deliberate mirror/bookend relations between cover and closing. [D]
- The `data-table` fabrication (“Adapt the source-supported grid into a table or timeline: …”) is a written admission that a missing role is solved by **rezoning an existing grammar**, not by inventing a new frozen frame. [D]
- Routing predicates accept *content shapes*, not pixel arrangements. [D]

**Where the repo froze things (do not replicate):**
- One `summary` + one pinned bbox-set per layout, then **cloned wholesale across roles** when the source deck lacked variety (§2.7) — the direct cost of instance-thinking: duplication instead of parameterization.
- `reuse_friendly:false` pages treated as atomic untouchables rather than as “grammar instance usable once”.
- `reference_image` hook inviting pixel pinning.

**Stage 4 stance:** store the **constraint bundle** (anchors + zone relations + capacity + routing predicates + variation transforms + reuse policy) as the reusable unit; treat any concrete arrangement as a *named instance* recorded in SlideVisualIR (`instance.variation_selected`), regenerable and swappable. Anti-repetition then becomes a solver over instances, and “templates” dissolve into “archetypes + sampled variations”.

---

## 9. Open questions / exact follow-up source needs

Priority order (bounded-context gaps that currently force UNKNOWN):

1. **Pipeline & prompts:** `scripts/template_analyzer.py`, `scripts/render_template.py`, `docs/distilled-styles.md`, `docs/ppt-implementation-logic.md` — needed to answer Q2 (distillation prompts, intermediate artifacts, validation steps) and confirm [I-1], [I-5], [I-7].
2. **Generation & approval loop:** `SKILL.md`, `docs/workflow.md`, `scripts/generate_ppt.py`, `scripts/image_generator.py`, `scripts/md_to_plan.py`, plus one exemplar pair `examples/product-launch/recipe.md` + `slides_plan.md` — needed for Q3 executor semantics, Q4 sample-approval, and the slides-plan ↔ layout-binding contract.
3. **Edit/version/QA:** `docs/edit_guide.md`, `scripts/editable_pptx/workflow.py`, `scripts/editable_pptx/scene.py`, `scripts/editable_pptx/renderer.py`, `examples/editable-pptx/case05-summer-poster/slide-01.scene.json` + `quality-report.json`, `examples/editable-pptx-poc/demo1-cover.scene.json` — needed for Q6 (versioning/regeneration) and Q7 (what QA is render-derived). Symbol-level asks: whatever function emits `quality-report.json`, and the scene-schema writer in `scene.py`.
4. **External image overlay rules:** `docs/external_image_overlay_logic.txt`, `scripts/editable_pptx/masking.py`, `scripts/editable_pptx/layers.py` — determines how `external_image_slots.bbox` is honored/composited; affects our slot `flexible/aspect_lock` design.
5. **Style cards:** any `.md` sibling, e.g. `styles/featured/geometric-business.md`, `styles/initial/editorial-mono.md`, one `styles/xiamulingzi/*.md` — likely the prompt-facing style narrative; needed to decide what survives as `positioning` prose vs structured tokens.
6. **Routing executor confirmation:** search targets in `scripts/generate_ppt.py` for consumers of `routing.content_shapes`, `validation_default`, `reference_image` (resolves [I-4], [I-5], [I-6]).

— end of report, ox-alpha