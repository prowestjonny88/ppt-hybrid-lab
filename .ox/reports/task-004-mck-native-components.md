# task-004 — Layout Engine Analysis: Mck-ppt-design-skill @ e190e08

Analyst: ox-alpha (forensic subordinate report; canonical architecture decisions remain with lead GPT).

---

## 1. Executive Finding

DIRECT EVIDENCE supports this characterization: Mck-ppt-design-skill is an **immediate-mode, flat-shape layout engine** over python-pptx. ~60 `MckEngine` methods each emit one slide composed of independent, **ungrouped** native shapes (textboxes, `RECTANGLE`/`OVAL`/`CHEVRON`/`BLOCK_ARC` autoshapes, pictures) at EMU coordinates computed from shared constants plus per-method arithmetic. There are **no native chart objects, no connectors, no group shapes, and no shape identity/registry**. Robustness comes not from the object model but from three surrounding mechanisms: (a) a connector ban + XML sanitization pass (`full_cleanup`), (b) a two-layer QA system (geometry estimator + text-only auto-fix), and (c) machine-readable gates with code-enumerated exemptions.

Verdict for Stage 3: **adopt the principles, do not adopt the component layer as-is.** The engine's own QA whitelists `peer_font_inconsistency` as an engine bug (SKILL.md 反模式 3), and I can reconstruct the exact mechanism why (§7). A QueueZero-native component API needs shape identity and role-awareness that Mck deliberately never built.

---

## 2. Native Generation Call Chain

DIRECT EVIDENCE unless noted.

```
Entry A (programmatic):
  MckEngine(total_slides=N)                      mck_ppt/engine.py
    └─ Presentation(); slide_width=SW; slide_height=SH; _blank_layout = prs.slide_layouts[6]
  eng.<layout_method>(**kwargs)                  e.g. eng.cover(), eng.data_table()
    ├─ self._ns()                                → prs.slides.add_slide(blank); _page += 1
    ├─ add_action_title(s, title)                mck_ppt/core.py
    │    └─ add_text(...) + add_hline(...)
    ├─ layout body: repeated add_rect / add_text / add_oval / add_hline /
    │               add_block_arc / draw_harvey_ball / s.shapes.add_picture
    └─ self._footer(s, source)                   → add_source + add_page_number
  eng.save(path)                                 engine.py (tail NOT supplied — see §12)
  full_cleanup(path)                             mck_ppt/core.py
    └─ zipfile rewrite of every XML part:
         remove all <p:style> (PresentationML ns)
         remove outerShdw/innerShdw/scene3d/sp3d from theme parts

Entry B (storyline):
  DeckBuilder.build(storyline, out_path)         mck_ppt/deck_builder.py
    └─ for spec in storyline: getattr(eng, spec['type'])(**spec['data'])
       (unknown type → skip + record; per-slide try/except)
    └─ eng.save() → DeckBuilder.qa_validate(path) → full_cleanup(path)
```

Underlying library: **python-pptx only** (`from pptx import Presentation`; `MSO_SHAPE.*`; `slide.shapes.add_shape/add_textbox/add_picture`). No lxml-level DrawingML authoring except surgical edits: `add_block_arc` injects `a:avLst/a:gd` adjust values into `prstGeom` (core.py, `add_block_arc`), and `set_ea_font` appends `a:ea` typeface to run properties (core.py).

Z-order = **insertion order** (first added = bottom). `cover()` inserts the optional cover picture *first* with the explicit comment 「先添加，后续所有元素在其上方」 (engine.py, `cover`). No grouping anywhere in supplied code.

---

## 3. Component / Layout Inventory (with evidence)

### 3.1 Primitive layer — `mck_ppt/core.py`

| Symbol | Produces | Notes |
|---|---|---|
| `add_text` | `add_textbox`; word_wrap=True, auto_size=None, explicit `bodyPr` anchor + 45720 EMU insets | accepts str or list[str]; line_spacing = 0.93× multiple if ≥18pt else Pt(size×1.35) |
| `set_ea_font` | `a:ea` run attr | CJK rendering |
| `add_rect` | flat RECTANGLE, solid fill, no line, `_clean_shape` (strips `p:style`) | |
| `add_hline` | **thin RECTANGLE**, min 6350 EMU (~0.5pt) | "never use connectors" — Guard Rail #1 |
| `add_oval` | OVAL badge with centered text, zero insets, anchor ctr | |
| `add_image_placeholder` | gray RECT + 2 hairline RECTs + label textbox | **returns only the rect**; crosshairs/label are orphaned siblings (see §6) |
| `add_action_title` / `add_source` / `add_page_number` / `add_bottom_bar` | slide chrome from constants | |
| `add_block_arc` | BLOCK_ARC with computed adj1/adj2 (start/end angle ×60000) and adj3 (inner ratio 0–50000) | powers donut/pie/gauge; genuine math→OOXML parameterization |
| `add_color_legend` | swatch rect + text pairs | |
| `draw_harvey_ball` | 2 ovals + **white masking rects** for partial fills | masks occlude whatever is beneath — only safe on white backgrounds (adversarial note) |
| `_clean_shape` / `full_cleanup` | XML sanitation | |

### 3.2 Layout methods — `mck_ppt/engine.py` (visible portion; tail truncated)

Structure: `cover`, `section_divider`, `toc`, `closing`, `appendix_title`.
Data/KPI: `big_number`, `two_stat`, `three_stat`, `metric_cards`, `data_table`, `table_insight`, `scorecard`, `rag_status`.
Frameworks: `matrix_2x2`, `pyramid` (staircase + optional detail table + PNG-icon circles), `process_chevron`, `temple`, `cycle`, `venn` (**retired**), `funnel` (**retired**).
Comparison: `side_by_side`, `before_after` (dual-mode: structured dicts or plain strings), `pros_cons`, `swot`.
Narrative: `executive_summary`, `key_takeaway`, `four_column`, `quote`, `two_column_text`, `meet_the_team`, `case_study`, `action_items`.
Timeline: `timeline`, `vertical_steps`. Image: `content_right_image` (placeholder). Advanced: `checklist`, `value_chain`. Charts: `grouped_bar`, `stacked_bar` (truncated mid-body).

Chart methods draw **bars as rectangles scaled from data arrays** with hand-placed tick labels and legend rect+text pairs — native vector drawing, not embedded `add_chart` objects. Arrows between flow nodes are **text glyphs** `'→' '↓' '←' '↑'` (`process_chevron`, `value_chain`, `cycle`) or a single CHEVRON autoshape (`table_insight`). DIRECT EVIDENCE.

Supporting modules: `deck_builder.py` (storyline dispatcher + crude bounds QA), `review.py` (narrative QA + autofix), `qa.py` (geometry QA), `cover_image.py` (Tencent Hunyuan + rembg raster pipeline — orthogonal service, not composition architecture), `constants.py` (tokens), `storylines/ai_enterprise.py` (33-slide data-only storyline spec).

---

## 4. Parameterization vs Fixed-Template Classification

Mixed model: **fixed vertical template bands + item-count-driven horizontal distribution + adaptive font tiers.**

**Truly parameterized builders** (geometry derived from inputs):
- `metric_cards`: `card_w = (CW - 0.2"*(n-1))/n` — any count.
- `data_table`: adaptive `row_h = min(0.95", avail/n_rows)`; font downgrade `SMALL_SIZE if row_h>=0.6" else Pt(10)`.
- `process_chevron`: Guard Rail Rule 10 — `step_w = min(PREFERRED_W, (CW - MIN_GAP*(n-1))/n)`; adaptive sub/desc fonts by resulting width.
- `vertical_steps`: `step_h = min(1.1", avail/n_steps)`; `use_small` tier.
- `checklist`: dynamic row height cap 0.85", zebra rows, `status_map` injectable.
- `value_chain`: fills residual vertical space; `stage_w=(CW-arrow_w*(n-1))/n`.
- `pyramid`: staircase platform geometry from `n`; icons accept PNG path OR text glyph; optional `detail_rows` table.
- `table_insight`: `**bold**` inline markup parsed into bold/plain runs (`re.split(r'(\*\*.*?\*\*)', line)`) — the only rich-text parsing in visible code.
- Charts: all geometry from data arrays; `stacked_bar` legend uses adaptive spacing.
- `before_after`: polymorphic input (dict rows → structured layout; strings → bullet fallback).

**Fixed-template regions** (hard-coded inches regardless of content):
- Vertical chrome everywhere: title band `TITLE_TOP/TITLE_H/TITLE_LINE_Y`, content from `CONTENT_TOP=1.3"`, source at `SOURCE_Y=7.05"`, bottom bar `BOTTOM_BAR_Y=6.2"` (constants.py; mirrored in qa.py).
- `temple`: pillars fixed 2.5"–5.3", foundation 5.5". `matrix_2x2`: fixed 4.5×2.0" cells. `timeline`: axis at y=3.0". `two_stat`/`side_by_side`: fixed 2.0"/4.2" body heights. `cover` title height heuristic `0.8"+0.62"*(extra lines)`.

**Hardcoded locale/style inside layout code** (style-specific, see §10): `'解决路径'/'详细说明'` (`big_number`), `'协同机制分析'` (`key_takeaway`), `f'负责人：{owner}'` (`action_items`), scorecard headers `['技术领域','评分','成熟度']`, default `status_map` with emoji labels (`checklist`), `'Key Takeaways'`.

**Interface-drift artifact worth flagging**: `run_qa_tests.py` calls `metric_cards` with `(name, value, delta)` triples, but engine.py destructures `card[:3]` as `(letter, ctitle, desc)` and puts element 0 into a 0.45″ circle badge. Structurally confirmed; the QA fixture and the engine disagree on the contract. DIRECT EVIDENCE of fixture/engine drift.

Version drift across docs: `__version__='2.3.0'` vs SKILL.md "2.3.3-harness-v2"; run_qa_tests says "55 layout methods", SKILL.md says "67 methods", layout-catalog.md says "72 types" (some reserved/retired). DIRECT EVIDENCE.

---

## 5. Text Fitting / Overflow Behavior

**Capacity model**: capacity is enforced *upstream of code* via `references/layout-matrix.yaml` char budgets per layout field (e.g., donut/pie "6 segments max ⚠️ 超6段必然溢出", four_column max 4), checked at Stage 3 by `gate_check_s3.py` (script not supplied). The engine itself performs **no fitting** — `word_wrap=True, auto_size=None` means text wraps but boxes never grow and nothing clips; excess renders outside the box.

**Adaptive mitigation at generation time**: row-height compression + font-tier downgrades (§4 list).

**Post-generation detection** (`mck_ppt/qa.py`):
- `_estimate_text_height(tf, box_w)`: per paragraph resolves font (run→para→default 14pt); line height = pt×1.4×12700 EMU; char width ≈0.55×size latin / 1.0×size CJK (ranges U+4E00–9FFF, U+3000–303F); `num_lines = ceil(est_width/(box_w−91440EMU))`.
- `_check_text_overflow`: est > box_h×1.15 → WARNING; >30% over → ERROR.
- Known estimator bias (DIRECT EVIDENCE from code reading): it **ignores `p.space_before`**, which `core.add_text` sets (Pt 6–10) between list lines → **underestimates** real height for bulleted lists (false negatives). Conversely it assumes 1.4× leading while engine sets Pt(size×1.35) and 0.93× for ≥18pt → **overestimates** titles/tight body (feeds false positives in `text_line_collision`). Two opposing biases coexist.

**Repair** (`mck_ppt/review.py`, `AutoFixPipeline`): strict priority chain mutating **text only, never geometry** (explicit constraint in module docstring): 去冗余 regex removals → 统一语言 (map `_LANG_REPLACEMENTS` currently `{}` — disabled) → 压缩句式 → 重构层级 (clause trimming) → 字号微调 (−1pt steps, floors 20/11/9pt, max 4 rounds). Then `_harmonize_peer_fonts`: peer groups (≥3 shapes, tops within 0.02″) converge to `min(sizes)` — chosen specifically so harmonization cannot induce overflow. If all strategies hit floors, the error persists → gate fails → content revision required. **The system never resizes or moves boxes to solve overflow.**

---

## 6. Image / Screenshot Replaceability

DIRECT EVIDENCE findings:
1. Images enter via exactly three paths: `cover(cover_image=path|'auto')` full-slide picture inserted first (z-bottom); `pyramid` icon overlay (`endswith('.png'/'.svg') and os.path.isfile` → `add_picture` inset 0.08″ on navy circle); `add_image_placeholder` (gray box + crosshair + `[ label ]`).
2. **No image-slot abstraction exists.** `add_image_placeholder` returns only the backing rect; the two hairlines and label textbox are untracked siblings. Programmatic replacement today requires matching shapes by name (`TextBox N`) or position.
3. That said, **same-bbox replacement is inherently safe** in this architecture: because all shapes are independent and absolutely positioned, swapping the picture at identical (left, top, w, h) cannot disturb neighbors. `content_right_image` computes the slot deterministically (`img_x = LM + left_w + 0.3"`), making positional targeting viable. What's missing is *identity*, not isolation.
4. Suspected defect: the `.svg` acceptance branch in `pyramid` would call `python-pptx add_picture` on an SVG — python-pptx has no SVG image handler; INFERENCE (untested) that this path raises. Needs verification before anyone relies on it.
5. `cover_image='auto'` hard-depends on Tencent Hunyuan credentials (`EnvironmentError` if unset) — external service coupled into slide generation.

---

## 7. QA Mechanisms and False-Positive Analysis

`mck_ppt/qa.py` `PptQA` checks (per slide unless noted): body_overflow (±0.02″ tol); text_overflow (estimator §5); dead_whitespace (20×20 grid coverage vs 55%, dead-zone naming); shape_overlap (**text-on-text only**, >15% of smaller area — intentional text-over-panel overlaps invisible by design); font_issue (<8pt); text_line_collision (text est-bottom vs "separator" = thin rect ≤3pt tall, >1″ wide; skips ≤2-char texts, <0.25″ shapes, and `anchor in {ctr,b}` shapes; requires ≥0.5″ horizontal overlap); peer_font_inconsistency; chart_legend_overflow (small-text heuristic; excludes `^\d+/\d+$` page numbers and top>6.8″); connector guard rail (any `<p:cxnSp` in slide XML → ERROR); global `<p:style>` remnants. Scoring: weighted deductions, `passed == (zero ERRORs)`. Second, looser layer: `DeckBuilder.qa_validate` (bounds with ±0.5″ slack, negative dims).

**Concrete false-positive mechanism — peer_font_inconsistency on `table_insight`** (the strongest finding of this analysis):

- qa.py `_check_peer_font_consistency` groups text shapes **solely by top-Y within 0.02″**, ignoring X/columns, and flags any group of ≥3 with mixed sizes as ERROR.
- engine.py `table_insight` renders row label cells with `SUB_HEADER_SIZE` (18pt) and sibling cells in the *same row, same `ry`, same anchor* at `row_font` = BODY_SIZE(14) or SMALL_SIZE(12).
- Therefore **every multi-row `table_insight` slide deterministically produces a `peer_font_inconsistency` ERROR** — geometric Y-proximity inferred semantic peerhood incorrectly across a column boundary.
- Corroboration: SKILL.md 反模式 3 states `peer_font_inconsistency` is in the hard-coded `ENGINE_BUG_WHITELIST` of `gate_check.py` — the authors themselves classify it as an engine-induced artifact. (Script contents unsupplied; whitelist membership of other categories UNKNOWN.)

Other inference risks:
- `text_line_collision`: inherits estimator bias (§5); full-width `add_hline` row separators mean almost any top-anchored wrapped cell horizontally overlaps ≥0.5″ — correctness rests entirely on the gap math driven by a biased estimate.
- `dead_whitespace`: bounding-box union counts large background panels (e.g., `key_takeaway`'s 5.2″ gray panel) as covered → masks real emptiness (false-negative direction).
- `shape_overlap`: blind to text-over-background collisions; two text blocks sliding together is caught, text sliding onto someone else's panel is not.
- qa.py **duplicates** SW/SH/LM/CW… locally with comment "must match constants.py" instead of importing — deliberate decoupling (QA can audit foreign decks) but a live drift hazard. Pattern to avoid replicating (RECOMMENDATION).

Governance layer (SKILL.md): five-stage flow; S3/S4 gates MUST be executed scripts producing `gate_result.json`/`gate_s3.json` with `"passed": bool`; exemptions only via code-enumerated whitelist — explicitly designed to prevent AI self-certification ("口头宣布门禁通过" anti-pattern). This is the repo's best idea. Gate script internals: not supplied.

---

## 8. QueueZero Three-Slide Component Mapping

Assumption (INFERENCE): Problem/Hook = headline + tension + few stats; How It Works = 3–5 stage mechanism; Validation/Traction = KPIs + proof artifacts. Correct me if the QueueZero specs differ.

| Need | Available Mck components | Verdict |
|---|---|---|
| **Problem/Hook** | `executive_summary` (headline band + numbered items), `key_takeaway` (analysis + side panel), `big_number`, `three_stat`/`two_stat`, `quote` | Structurally sufficient. Editorial hook typography (oversized serif pull-quote, asymmetric hero) exceeds these recipes → SVG lane candidate. |
| **How It Works** | `process_chevron` (2–7 steps, dynamic widths), `value_chain` (full-width stages), `vertical_steps`, `pyramid` (PNG icons + detail table), `timeline`, `cycle` | Sufficient for linear chains. **Gaps:** no true connectors (glyph arrows only), no annotated system schematic, no swimlane/branching diagram, no arrowhead geometry between arbitrary anchors → new component or SVG lane. |
| **Validation/Traction** | `metric_cards`, `scorecard`/`kpi_tracker` (dual-rect progress bars), `data_table`, `horizontal_bar`, `donut` (BLOCK_ARC), `dashboard_kpi_chart` (impl truncated), `waterfall`/`pareto` (impl truncated) | Metrics covered. **Gaps:** no screenshot/product-visual slot (placeholder only), **no logo wall / customer-logo row**, no testimonial-with-attribution card (`meet_the_team` is people-profile shaped) → new components needed; complex composed traction graphics → SVG lane. |

Cross-cutting gap: nothing in the kit produces a *identified, editable composite* — every layout is write-once flat shapes.

---

## 9. Recommended Minimum Native Component API for Stage 3 (RECOMMENDATION)

Designed against Mck's demonstrated failure modes (no identity, name-based lookup, Y-only peer inference, locale-baked strings):

```
SlideCanvas(theme_tokens, locale_strings)          # inject palette/type/copy — nothing hardcoded
  .title(text) -> TitleRef                         # owns title textbox + rule line as children
  .source(text) / .page(n, total)
  .metric_card(value, label, delta?) -> MetricCard # set_value/label/delta/recolor — geometry recomputed
  .kpi_row(specs) -> list[MetricCard]
  .text_block(text, role) -> TextRef               # set_text runs refit check before commit
  .image_slot(bbox, fit='contain') -> ImageSlot    # .replace(path) swaps picture ONLY;
                                                   #   frame + caption are owned children, untouched
  .process_flow(steps) -> Flow                     # node move repositions owned glyph/arrow children
  .bar_chart(data) / .donut(segments)              # setters recompute geometry from stored spec
                                                   #   (Mck precedent: metric_cards/data_table formulas)

Every component: stable id, semantic role, bbox, children[] (each shape tagged).
Canvas ops: canvas.move(id,dx,dy) / .resize(id,w,h) / .recolor(id,tok) / .remove(id)
            → cascade to children; neighbors never touched (isolation already proven by flat model).
canvas.validate(role_aware=True)                  # port Mck's checks but group peers by ROLE,
                                                  #   not Y-proximity — eliminates the table_insight FP class.
save(): render → post-save sanitizer pass (p:style/shadow/3D strip; connector ban enforced)
```

Core principles: (1) factories return handles with identity; (2) declarative spec → regenerated geometry rather than mutated absolutes; (3) role-aware validation; (4) cleanup as save-interceptor; (5) text-only autofit with floors, never geometry mutation.

---

## 10. Reusable Principles vs Style-Specific Mechanisms

**Reuse as engineering principles** (clean-room: mechanism → principle → relevance):
- Primitive layer consumed by all layouts; upper layers barred from raw pptx (`core.py` docstring) → *strict layering keeps object emission auditable.*
- `full_cleanup` p:style + theme effect stripping; connector ban + QA scan → *deterministic flat output; renderer-variance and corruption immunity.*
- Char-budget matrix as upstream truth + executed JSON gates + code-only exemption whitelists (SKILL.md) → *capacity knowledge lives in data; verdicts are machine-derived, not AI-asserted.*
- Dynamic sizing formulas `min(preferred, avail/n)` with font tiers → *variable-cardinality layouts without overflow by construction.*
- Text-only autofix priority chain; min-font peer harmonization → *repair preserves spatial intent and cannot create new overflow.*
- BLOCK_ARC angle math (math-CCW → OOXML cw-from-12 ×60000, adj3 inner ratio) → *preset-geometry parameterization recipe.*
- Run-level `a:ea` injection → *correct CJK in mixed-script decks.*
- Insertion-order z-discipline with explicit comments → *predictable stacking without groups.*

**Do not copy (style/template-specific):**
- McKinsey palette + Georgia/Arial/KaiTi baked into constants and method defaults; hardcoded Chinese UI copy inside layout methods; emoji status maps.
- Per-layout magic offsets tuned once (`before_after`, `cover` line-height heuristics) — template fossils.
- Dead retired layouts retained in code (`venn`, `funnel`, retired `#14`).
- `cover_image.py` vendor pipeline (Hunyuan/rembg) — unrelated to composition.
- qa.py constant duplication instead of import (drift hazard).
- Nameless-shape emission model — the root cause Mck's own tooling compensates for.

---

## 11. Gaps Requiring SVG Lane or New Components

1. True connectors/elbow arrows between arbitrary anchors (Mck bans connectors outright; glyphs don't scale semantically).
2. Annotated system/mechanism schematics (branching, feedback loops) — no Mck analog.
3. Screenshot slot with frame/caption identity; logo wall; testimonial card.
4. Editorial hero/hook typography beyond recipe scale.
5. Any composite requiring post-edit identity (everything, per §9).

---

## 12. Unknowns and Exact Follow-Up Requests

UNKNOWN — bounded package insufficient. Exact requests, no guessing:

1. **`mck_ppt/engine.py`, remainder** (truncate point: inside `stacked_bar`, at `for pi, period in enumerate(periods): bx = cl + sbs * pi + ...`). Needed symbols: `horizontal_bar`, `line_chart`, `donut`, `waterfall`, `pareto`, `kpi_tracker`, `bubble`, `risk_matrix`, `gauge`, `harvey_ball_table`, `pie`, `stacked_area`, `dashboard_kpi_chart`, `stakeholder_map`, `decision_tree`, `metric_comparison`, `icon_grid`, `agenda`, `numbered_list_panel`, `two_col_image_grid`, `three_images`, `image_four_points`, `full_width_image`, `case_study_image`, `quote_bg_image`, `goals_illustration`, plus the `save()` tail (does save internally invoke `full_cleanup`? SKILL.md's template comments "# 自动 full_cleanup" yet `staircase_civilization.py` and `deck_builder.py` both call it again externally — contradictory signals).
2. **`references/scripts/gate_check.py`** — `ENGINE_BUG_WHITELIST` full enumeration, `user_code_errors` schema, scoring/exit semantics.
3. **`references/scripts/gate_check_s3.py`** — how `layout-matrix.yaml` budgets are parsed/enforced; API-format validation tables (SKILL.md cites real historical failures in `four_column`/`matrix_2x2`/`executive_summary` arg formats).
4. **`references/framework/guard-rails.md`** — canonical rules 1–10 (only #1 and #10 inferable from code comments).
5. **`references/framework/engine-api.md`** and one or two of `references/layouts/*.md` (suggest `charts-circular.md`, `images.md`) — per-layout contracts.
6. Verification sample: any `.svg` asset under `assets/icons/` (to test the suspected unsupported-SVG `add_picture` path in `pyramid`).

— end of report, ox-alpha. Findings offered for lead GPT disposition; no repositories were modified.