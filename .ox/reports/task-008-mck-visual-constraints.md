# task-008 — Forensic Report: Mck-ppt-design-skill Visual Constraints & Gating

**Repo:** likaku/Mck-ppt-design-skill @ e190e08 · **Analyst:** ox-alpha (subordinate forensic engineer) · **Stance:** clean-room extraction of mechanisms → principles → relevance. No canonical architecture decided here.

---

## 1. Executive Summary — Portable Constraint/Gating Ideas

MCK's genuinely valuable, portable assets are **not** its 72-layout component catalog (already rejected). They are:

1. **A declared capacity matrix per layout** (`layout-matrix.yaml`: max items, per-field char budgets, special limits) — but critically, **the declared matrix is not what the gate enforces**. Enforcement is a separate hard-coded Python checker covering only ~9 layouts explicitly. This declared-vs-enforced drift is itself a finding: port the *concept* of a machine-consumable capacity registry, not MCK's prose-YAML-plus-hand-coded-checker split.
2. **Machine-derived gate verdicts**: `passed` is a Python bool computed from classified errors (`user_code_errors == 0`), written to JSON, exit-coded for CI. AI cannot verbally override. This is the single most portable governance idea.
3. **Evidence-gated exemptions**: engine-bug whitelists require written evidence in code comments; verbal exemption is explicitly banned. (But the implementation has a scope bug — see §3, row 5.)
4. **A layered anti-collapse stack**: pre-render structural checks (S3) → render → post-render geometric QA (bounds, text-fit estimation, text/line collision, peer-font consistency, legend-cluster overflow, dead-whitespace grid, overlap, corruption guards) → optional auto-fix with a fixed priority chain and font floors.
5. **Dynamic-sizing invariants** baked into the engine: `item_w = min(preferred, (CW − min_gap·(n−1))/n)`, row-height caps with font-step fallbacks, bottom-bar y-clamping `[6.1", 6.4"]`, cover subtitle following computed title height. These are portable as **archetype sizing solvers**, not as code.
6. **Experience-ledger self-refinement**: recurring failures become dated Problem/Root-Cause/Fix/**Rule** records; the Rule field names the gate check that now prevents recurrence; S3 must read all experience files before filling content. Portable if re-cast as structured records with promotion into compiler validations and regression fixtures.
7. **Composition routing as constraints, not templates**: adjacency non-repetition, global rarity caps (`two_column_text ≤ 1/deck`), "data with time axis ⇒ chart family," "≥8 pages ⇒ ≥1 image slot," opening-slide priority ranking. This is rhetorical routing expressed as checkable constraints — exactly the right granularity for a Visual-IR compiler.
8. **Known blind spot, confirmed by their own A/B note**: the QA score measures *layout health*, not content or aesthetic quality; `passed` ignores the score entirely. Equal-weight card grids with weak focal hierarchy and bbox-"covered" dead space **pass cleanly**. Our Stage 4 must add hierarchy/balance checks MCK lacks.

---

## 2. Question Coverage Map

| Q | One-line answer | Detail in |
|---|---|---|
| Q1 capacity constraints location/data-driven? | Declared in `layout-matrix.yaml`; enforced (partially, hard-coded) in `gate_check_s3.py`; sizing limits hard-coded in `engine.py`; density caps in `review.py`; QA thresholds in `qa.py`. Matrix is **not loaded by any supplied script**. | §3 rows 1–4, §4-I1 |
| Q2 Stage-2 selection semantics? | Rhetorical/semantic guidance (content-type→layout tables, narrative skeletons, priority rankings) + mechanical constraints (adjacency, rarity, counts). Execution is a string type dispatched via `getattr`. | §3 rows 14, 17; §4-I4 |
| Q3 anti-collapse rules? | Extensive; see evidence rows 6–15, 19–20, 27–30. | §3 |
| Q4 gate pass/fail derivation? | S3: zero issues from per-layout checker list (unknown layouts → source-check only). S4: zero non-whitelisted QA errors. Both objective-core/proxy-shell; several false-pass vectors identified. | §3 rows 2, 4, 5, 31; §4-I2, I3, I5 |
| Q5 experiences/ loop? | Markdown Problem/RootCause/Fix/**Rule** ledger, read mandatorily at S3; whitelist edits demand written evidence. Port as structured records with promotion path. | §3 rows 15, 16; §5.4 |
| Q6 portable archetype constraints? | Item ceilings, per-field char budgets, single-line badges, edge-proximity caps, rarity caps, sizing invariants, CJK measurement coefficients, mandatory page elements. Not portable: BLOCK_ARC adj values, EMU coordinates, KaiTi/Hunyuan recipes. | §5.1 |
| Q7 check tiering? | Compiler: structure/counts/budgets/solvability/predicted-fit. Post-render structural: geometry, corruption, peer fonts, collisions, legend clusters. Multimodal: hierarchy, balance, legibility, aesthetic pass. | §5.3 |
| Q8 what to reject? | Catalog-as-product, card-soup defaults, category-global exemptions, AI self-eval gates, prose-as-machine-truth, geometry-only pass, retired-but-live APIs, duplicated constants/env-pinned paths. | §6 |
| Q9 clean-room schemas? | §5.2 (capacity record, composition rules, gate record). | §5.2 |
| Q10 preventing weak-focal/equal-weight/dead-space? | MCK has only a binary-coverage proxy. Add focal-region requirements, area-variance floors, ink-weighted coverage bands, pre-render dead-zone prediction, multimodal hierarchy review. | §5.5 |
| Q11 follow-up paths? | §7. | §7 |
| Q12 (implicit) | Covered throughout. | — |

---

## 3. DIRECT EVIDENCE Table

| # | Finding | Path | Symbol / Location | Notes |
|---|---|---|---|---|
| 1 | Per-layout capacity matrix declared: Max Items, Title Chars, Body/Cell Chars, Special Limits (e.g., `process_chevron` 5 steps / label 10 / title 20 / desc 50; `donut`,`pie` "**6 segments max** ⚠️ 超6段必然溢出"; `four_column` 4 cols; `two_column_text` "全局≤1张"; `timeline` 6 milestones / last-label context) | `references/layout-matrix.yaml` | "Layout Capacity Matrix" table; trailing pseudocode `LAYOUT_MATRIX[layout]['char_budget'].get(field, 80)` | Pseudocode is labeled 示例 (illustrative). Default budget fallback = 80 chars. |
| 2 | S3 gate = per-layout checker routing; `passed = len(all_issues)==0`; unknown layouts fall back to `[check_source]` only | `references/scripts/gate_check_s3.py` | `LAYOUT_CHECKERS` dict; `run_gate_check_s3()`; `.get(layout, [check_source])` | Explicit checkers exist for only: four_column, executive_summary, matrix_2x2, process_chevron, donut, pie, grouped_bar, stacked_bar(count-less), timeline + generic source/title for ~13 more. Remaining ~45 engine methods unchecked beyond source. |
| 3 | **Declared-vs-enforced gap**: matrix mandates `title ≤ 40`, `four_column desc ≤ 120`, `toc` budgets, etc.; S3 script implements **none** of these char-budget checks. Its only text-length checks: chevron `desc ≤ 50`, timeline last label `≤ 6`, action title `> 10`. | `references/layout-matrix.yaml` vs `references/scripts/gate_check_s3.py` | compare `check_*` functions against matrix rows | Char-budget enforcement de facto deferred to render-time estimation (`qa.py`) or never. |
| 4 | S4 gate: errors partitioned by `ENGINE_BUG_WHITELIST = {"peer_font_inconsistency", "chart_legend_overflow"}`; `passed = len(user_code_errors)==0`; result written to `gate_result.json`; exit code 0/1 | `references/scripts/gate_check.py` | `ENGINE_BUG_WHITELIST`, `run_gate_check()`, `main()` | `overall_score` is reported but **not** part of the pass decision. `MAX_WARNINGS_ALLOWED = 3` is defined and **never read** (dead config). Skill path hard-coded: `~/.workbuddy/skills/mck-ppt-design`. |
| 5 | **Whitelist scope bug**: comment block says chart_legend_overflow exemption is "仅豁免 timeline 版式 … 其他版式不豁免" (timeline-only), but code exempts **by category globally** — any slide, any layout. | `references/scripts/gate_check.py` | comment above `ENGINE_BUG_WHITELIST` vs `if issue.category in ENGINE_BUG_WHITELIST:` | Documented intent ≠ implementation. Same for `peer_font_inconsistency` (comment cites intentional 18pt/14pt in table_insight/process_chevron; code exempts everywhere). |
| 6 | QA check inventory executed per slide: body_overflow, text_overflow, text_line_collision, dead_whitespace, shape_overlap, fonts, peer_font_consistency, chart_legend_overflow, connectors; global: p:style remnants | `mck_ppt/qa.py` | `PptQA._check_slide`, `_check_global` | Thresholds: `OVERFLOW_TOLERANCE=Emu(18288)` (0.02"), `WHITESPACE_THRESHOLD=0.55`, `TEXT_OVERFLOW_LINE_RATIO=1.15`, `MIN_FONT_SIZE=Pt(8)`, `TEXT_LINE_GAP_MIN=Emu(27432)` (0.03"), `PEER_Y_TOLERANCE=Emu(18288)`. |
| 7 | Text-fit estimator: per-paragraph font resolution (run → para → 14pt default); line height = `pt × 1.4`; char width = latin `0.55×pt`, CJK `1.0×pt`; usable width minus 0.1" padding; ERROR if est > box×1.15 and overflow >30%, else WARNING | `mck_ppt/qa.py` | `_estimate_text_height`, `_check_text_overflow` | Heuristic, no font metrics. Matches `experiences/cjk-issues.md` Exp 002 rule ("CJK 行高系数 1.4") — evidence the experience loop fed back into QA constants. |
| 8 | Dead-whitespace: 20×20 grid over content area (`CONTENT_TOP..SOURCE_Y`, `LM..LM+CW`); empty ratio > 0.55 → WARNING; dead zones localized to `bottom_third / right_third / left_third / center / scattered`; slides with no content shapes skipped (cover/divider exempt) | `mck_ppt/qa.py` | `_check_whitespace`, `_identify_dead_zones` | Coverage is **binary bbox union** — a large empty gray panel counts as "covered." |
| 9 | Peer-font consistency: text shapes grouped by top-Y within 0.02"; groups **≥3** members with divergent size/family → ERROR | `mck_ppt/qa.py` | `_check_peer_font_consistency` (`if len(g) < 3: continue`) | False negative for 2-item peer rows — e.g., `two_stat` renders exactly 2 stat cards (`engine.py::two_stat`). |
| 10 | Auto-fix priority chain (text-only, no layout mutation): 去冗余 → 统一语言(disabled/empty map) → 压缩句式 → 重构层级 → 字号微调; font floors `TITLE_MIN_PT=20, BODY_MIN_PT=11, SMALL_MIN_PT=9`; iterate ≤3 rounds; then peer harmonization to `min(sizes)` | `mck_ppt/review.py` | `AutoFixPipeline._apply_fixes`, `_fix_font_size`, `_harmonize_peer_fonts`, `CHAR_DENSITY_LIMITS` (height-keyed: 0.2"→15 chars … 5.0"→1200) | Min-size harmonization chosen explicitly to avoid creating new overflow. |
| 11 | Dynamic sizing in engine: `data_table` `row_h=min(0.95", avail/n)`, font `SMALL if row_h≥0.6" else Pt(10)`; `table_insight` `row_h=min(1.55", avail/n)`; `vertical_steps` `step_h=min(1.1", avail/n)`, small-mode < 0.85"; `checklist` `row_h=min(0.85", avail/n)`, small font < 0.65" | `mck_ppt/engine.py` | `data_table`, `table_insight`, `vertical_steps`, `checklist` | All compute `avail` down to `BOTTOM_BAR_Y − 0.15"` or `SOURCE_Y − 0.1"`. |
| 12 | Horizontal packing invariant: `max_step_w=(CW − MIN_GAP·(n−1))/n; step_w=min(PREFERRED_W, max_step_w)` with `MIN_GAP=0.35"`, `PREFERRED_W=2.6"`; adaptive fonts at width thresholds 2.0"/1.8" | `mck_ppt/engine.py` | `process_chevron` | Mirrors guard-rail Rule 10 formula; same pattern in `metric_cards`, `four_column`, `meet_the_team`, `action_items` (`col_w=(CW−gap·(n−1))/n`). |
| 13 | Guard rails (declared): Rule 1 bottom-bar gap ≥0.15"; Rule 2 bounds right ≤ 12.533", bottom ≤ 6.95", inner inset 0.15"; Rule 3 bar_y clamp `[6.1", 6.4"]`; Rule 5 title uniformity + content top 1.25"; Rule 7 ≥1 image placeholder for ≥8-page decks; Rule 8 dynamic sizing formulas; Rule 10 horizontal overflow formula; anti-corruption: no connectors, `_clean_shape`, `full_cleanup`, `set_ea_font` | `references/framework/guard-rails.md` | Rules 1–10 + Anti-Corruption list | README presents "13 rules" (adds text-line collision, QA gate, legend overflow) — numbering drift between docs. |
| 14 | Composition routing rules: opening priority `table_insight > big_number > key_takeaway`; "date/period + value ⇒ must use chart layout"; "≥8 pages ⇒ ≥1 image layout"; "相邻幻灯片不得使用同一版式"; "`two_column_text` 全局不超过1张（最低视觉吸引力）"; density: ≥3 visual blocks, content-area usage ≥50%, action title must be a full insight sentence | `references/framework/planning-guide.md`; `references/framework/engine-api.md` | "Layout Selection Rules", "Content Density Requirements"; "Content-to-Layout Quick Match" table | Semantic/rhetorical routing expressed as checkable constraints. |
| 15 | Experience ledger format: `## Experience NNN` + Date/Problem/Root Cause/Fix/**Rule**; S3 must read all `experiences/*.md`; protocol: ONE-TIME vs PATTERN triage, pattern ⇒ must write | `experiences/*.md`; `SKILL.md` | Self-Refinement 协议 block; files `overflow.md`(6), `chart-limits.md`(2), `layout-pitfalls.md`(5), `cjk-issues.md`(2) | Rule field always names the gate-level prevention (e.g., "S3 门禁检查 `len(title) <= 40`"). |
| 16 | Evidence-gated whitelist culture: timeline last-label false positive documented with repro ("即使改为最短标签（如 '36月' 2字），仍然报 overflow 0.47\""); rule: whitelist edits require textual evidence, verbal exemption forbidden | `experiences/layout-pitfalls.md` Exp 005; `references/scripts/gate_check.py` header comment | `ENGINE_BUG_WHITELIST` provenance comments | Root cause: engine `timeline` uses fixed right-aligned positioning for last node label (`engine.py::timeline` places label at `mx − 1.0"` width 2.0" centered — last node near right edge). |
| 17 | Declarative composition spec: storyline = list of `{'type': name, 'data': kwargs}`; dispatch via `getattr(eng, slide_type)`; **unknown type → print warning, append local error, continue building**; post-build `qa_validate` checks off-screen (±0.5" tolerance) and negative dims; deck saved regardless | `mck_ppt/deck_builder.py` | `DeckBuilder.build`, `qa_validate` | Combined with S3's `[check_source]` fallback (row 2), a typo'd layout name passes S3 and silently drops a slide. |
| 18 | Constants duplicated between modules with a "must match" comment: `SW/SH/LM/CW/CONTENT_TOP/SOURCE_Y/BOTTOM_BAR_Y…` re-declared in qa.py | `mck_ppt/qa.py` header vs `mck_ppt/constants.py` | duplicate literal definitions | Drift risk made explicit by their own comment. |
| 19 | Tolerance divergence between QA layers: `deck_builder.qa_validate` allows ±0.5" outside slide; `qa.py` flags at +0.02" | `mck_ppt/deck_builder.py` vs `mck_ppt/qa.py` | `qa_validate` bounds vs `OVERFLOW_TOLERANCE` | Two geometries-of-truth; port lesson: single tolerance source. |
| 20 | Bottom-bar collision history + fix: fixed `Inches(6.2)` overlapped growing tables; fix `bar_y=max(last_row_bottom+0.2", 6.1")` clamped `min(...,6.4")`; engine encodes `bottom_limit = BOTTOM_BAR_Y − 0.15"` when bottom_bar present | `experiences/layout-pitfalls.md` Exp 004; `guard-rails.md` Rules 1&3; `engine.py::data_table` | — | Canonical example of experience → engine invariant → rail. |
| 21 | Cover collapse fix: subtitle was pinned at 3.5"; now `title_h = 0.8" + 0.62"·(n_lines−1)`, `sub_y = 1.15" + title_h + 0.24"` | `experiences/layout-pitfalls.md` Exp 002; `engine.py::cover` | title_h/sub_y computation | Dynamic-flow precedent for variable-height headers. |
| 22 | Chart data ceilings + remediation recipe: donut/pie >6 ⇒ auto-merge to top-5 + "其他" (code snippet provided); grouped_bar ≤6 cats × ≤3 series ⇒ else split slides | `experiences/chart-limits.md` Exp 001–002; enforced in `gate_check_s3.py::check_donut_pie`, `check_grouped_bar` | — | Includes a concrete **auto-transform** (merge), not just rejection — portable idea. |
| 23 | Chevron label single-line rule: `\n` in step label blew oval height by 21% (fixed 0.45" badge); rule `'\n' not in step_label` | `experiences/overflow.md` Exp 004; `gate_check_s3.py::check_process_chevron`; `core.py::add_oval` (fixed size param) | — | Constraint derived from a fixed-size primitive — exactly an archetype slot constraint. |
| 24 | Timeline last-milestone edge-proximity rule: label ≤6 chars (uniform distribution pushes last label past content right edge by 0.47") | `experiences/overflow.md` Exp 006; `gate_check_s3.py::check_timeline_last_label`; `engine.py::timeline` | — | Edge-proximity constraints are positional-archetype facts, portable as such. |
| 25 | CJK font injection: `set_ea_font` adds `a:ea` typeface KaiTi to run rPr; rule: any handwritten `add_text` with Chinese must call it | `mck_ppt/core.py::set_ea_font`; `experiences/cjk-issues.md` Exp 001 | — | Renderer-specific; principle (script-aware font completeness) portable. |
| 26 | Dual line-spacing regime in `add_text`: ≥18pt ⇒ 0.93× multiple; body ⇒ `Pt(size×1.35)` "to prevent CJK overlap" | `mck_ppt/core.py::add_text` | line_spacing branch | Typography invariant tied to measurement model. |
| 27 | Legend-cluster overflow check: small texts (h≤0.5", w≤2.5", len≤20, top≤6.8") excluding `^\d+/\d+$` page numbers; right edge > content right + tol ⇒ ERROR | `mck_ppt/qa.py::_check_chart_legend_overflow` | — | Page-number filter is regex-brittle. |
| 28 | Text/line collision: separator = rect with h ≤ 38100 EMU (~3pt) and w > 1"; flag when line_top − est_text_bottom ∈ (−0.2", +0.03"); ERROR if overlapping; skips ctr/bottom-anchored text, ≤2-char labels, <0.25" shapes; requires ≥0.5" horizontal overlap | `mck_ppt/qa.py::_check_text_line_collision` | — | Sophisticated and portable as a post-render check. |
| 29 | Slide scoring arithmetic: error −25 body_overflow / −20 text_overflow / −30 guard_rail / −15 other; warning −10 dead_ws / −8 text_of / −10 overlap / −5 other; info −1; floor 0; `overall_score` = mean | `mck_ppt/qa.py::_calc_slide_score` | — | Score is rule-trigger-frequency-dependent (their own A/B caveat, README). |
| 30 | Corruption guards: connector scan `<p:cxnSp` ⇒ ERROR; `<p:style` count ⇒ WARNING; `full_cleanup` strips p:style + theme outerShdw/innerShdw/scene3d/sp3d post-save | `mck_ppt/qa.py::_check_connectors`, `_check_global`; `core.py::full_cleanup` | — | PPTX-specific; principle (post-save sanitize + verify) portable. |
| 31 | S2 gate is AI self-check only: cover exists; `count ≤ duration×1.2`; layouts defined in matrix; titles are sentences (**len>10, 包含动词**) ; `two_column_text ≤1`. Downstream script enforces only `len>10` — **verb check unenforced anywhere** | `SKILL.md` Stage 2; `gate_check_s3.py::check_action_title` | — | Second declared-vs-enforced drift instance. |
| 32 | Fast-track bypass: ≤5 pages ∧ no chart layouts ∧ user says "quick" ⇒ skip S2/S3 review; S4 gate always mandatory | `SKILL.md` "Fast Track" | — | Risk-tiered gating depth — portable. |
| 33 | Checkpoint/resume state machine driven purely by artifact presence (brief/outline/content/gate_s3/pptx/gate_result) | `SKILL.md` "Checkpoint" snippet | glob/existence ladder | Operational pattern, portable. |
| 34 | Empirical capacity tuning anecdote: pyramid demo reduced to 3 levels "避免楼梯超出画面" | `mck_ppt/storylines/ai_enterprise.py` SLIDE 15 comment | `'levels'` 3-tuple list | Practitioner-discovered ceiling not present in any matrix/gate. |
| 35 | Mandatory page furniture: action title band (top 0.15", h 0.9", rule at 1.05"), content 1.3"–6.5", source at 7.05", page num bottom-right; source format `Source: [机构 年份]` | `references/team/presentation-convention.md`; `constants.py` vertical grid; `core.py::add_action_title/add_source/add_page_number` | — | Page-class furniture contract, portable. |
| 36 | Strict type scale: 44/28/22/18/16/14/9pt only; NAVY for all circular markers/titles; accents only for ≥3 parallel items; card body always DARK_GRAY | `references/team/brand-guide.md`; `color-palette.md`; `constants.py` | — | Token-level constraints, portable as design tokens. |

---

## 4. INFERENCE

- **I1 — The capacity matrix is decorative in the pipeline.** No supplied script imports or parses `layout-matrix.yaml` (gate_check_s3.py contains only literals; no `yaml` import anywhere in the supplied set). The YAML's own gate snippet is labeled pseudocode. Consequence: most char budgets (title ≤40, four_column desc ≤120, toc/metric_cards budgets…) are enforced *nowhere pre-render*; they surface only if the render-time heuristic (`_estimate_text_height`) trips, and only for boxes the estimator sees. **Classification: INFERENCE from absence + labeling.** Follow-up: grep repo for `yaml`/`load` consumers to confirm (§7).
- **I2 — S3 false-pass vectors (concrete):** (a) layout-name typo → default `[check_source]` passes, then `DeckBuilder` skips the unknown type with a warning and ships a deck missing a slide (rows 2, 17); (b) all char budgets except three ad-hoc ones unchecked (row 3); (c) "action title is a sentence" reduces to `len>10` — "竞争格局分散" (6+4 chars, no predicate) style labels can pass; (d) `source` presence ≠ validity.
- **I3 — S4 false-pass classes:** `passed` ignores `overall_score`; a deck of only-warnings (dead whitespace 54%, overlaps 14%, density 1.29×) passes. Binary grid coverage rewards large inert panels. Peer check blind below 3 members (two-stat rows). Whitelist is category-global (row 5), so a *genuine* legend overflow on any non-timeline layout is excused if categorized identically. Text-fit is a char-width heuristic — real font metrics (KaiTi is wider/taller) can diverge; their own CJK experience admits the estimator needed a 1.4 coefficient patch, i.e., known systematic error.
- **I4 — Stage-2 "routing" is constraint-bounded LLM judgment, not a router.** There is no scoring/selection function anywhere; the "routing" lives in prose tables (engine-api Quick Match, planning-guide priorities) plus mechanical post-hoc rules (adjacency, rarity). Portable conclusion: keep routing semantic, but move *all mechanical parts* into compiler validations.
- **I5 — The experience dates (2026-05-02/03) coincide with the harness release (v2.3.3-harness, 2026-05-03)**, suggesting the ledger was largely backfilled during the harness refactor rather than grown organically. Doesn't reduce the value of the *format*, but cautions against assuming the entries were each produced by the loop they describe. Needs git history to verify (§7).
- **I6 — The QA-score A/B inversion (95 simple vs 92 rich) is consistent with the scoring arithmetic** (more layouts ⇒ more rule triggers ⇒ lower mean), supporting MCK's own caveat that score ≠ quality. Reinforces: never let a composite score be the gate; gate on classified blocking findings.
- **I7 — Engine bugs cluster around fixed-position assumptions** (timeline last label; old cover subtitle pin; old bottom bar pin). Principle: every fixed coordinate adjacent to variable content is a latent collapse; the durable fix pattern they converged on is *derive-from-measured-neighbors* (rows 20, 21) — directly applicable to our IR compiler (no absolute Y for anything downstream of variable-height content).

---

## 5. RECOMMENDATION — Stage 4 Visual IR / Archetype Registry / Compiler / QA

### 5.1 Portable-as-archetype-constraints (distilled from evidence)

Port as **declarative slot constraints**, not renderer recipes:

- Cardinality ceilings + `on_exceed` policy: `reject | auto_transform | split_slide` (MCK has all three: chevron reject, donut merge-top-N+其他, grouped_bar split-hint — rows 12, 22).
- Per-field char budgets with **reason refs** (badge fixed-height ⇒ no multiline; edge slot ⇒ short label).
- Single-line/forbidden-character constraints tied to fixed primitives.
- Sizing solver contract per archetype: packing strategy, min gap, preferred size, font ladder thresholds, hard floors (20/11/9pt pattern).
- Measurement model shared deck-wide: latin 0.55×pt, CJK 1.0×pt char width; 1.4× line height (with a plan to swap in real font metrics later — MCK's heuristic is a known-error stopgap, I3).
- Page-class furniture contracts (title band, source, page number, content window) and page-class-aware check exemption (their whitespace check correctly skips covers/dividers, row 8).
- Design tokens: closed type scale, role-fixed colors, accent-only-for-≥3-parallels rule.

Not portable (renderer recipes): BLOCK_ARC adj formulas, EMU coordinates, KaiTi injection mechanics, Harvey-ball masking, Hunyuan cover pipeline, `p:style` surgery specifics (keep the *verification*, drop the recipe).

### 5.2 Clean-room schema fragments

**(a) Archetype capacity record** (registry entry; every limit carries provenance):

```yaml
# archetype.capacity.yaml — one document per archetype
id: flow.horizontal_chevron
version: 3
family: process
slots:
  - id: steps
    kind: ordered_list
    cardinality: {min: 2, max: 5, on_exceed: reject_with_split_hint}
    item_fields:
      badge: {type: short_label, max_chars: 10, multiline: false,
              constraint_ref: "EXP/OVF-004"}        # fixed-height oval badge
      title: {type: short_label, max_chars: 20}
      desc:  {type: paragraph,   max_chars: 50}
focal:
  required: true
  selector: terminal_step_inverted                  # last step navy = focal
  min_area_share: 0.10
sizing:
  solver: pack_horizontal
  params: {content_width_in: 11.733, min_gap_in: 0.35, preferred_item_in: 2.6}
  font_ladder:
    - {when_slot_width_lt_in: 2.0, apply: {title_pt: 14}}
    - {when_slot_width_lt_in: 1.8, apply: {desc_pt: 12}}
  floors_pt: {display: 20, body: 11, caption: 9}
measurement:
  estimator: heuristic_v1                            # upgrade path: font_metrics_v2
  char_width_factor: {latin: 0.55, cjk: 1.0}
  line_height_factor: 1.4
provenance: ["EXP/OVF-003", "GR/RULE-10", "ENG/process_chevron@e190e08"]
```

**(b) Deck-level composition constraints** (compiler validations, replacing prose):

```yaml
composition_rules:
  adjacency: {window: 1, block_same_family: true}
  rarity_caps:
    - {archetype: text.two_column, max_per_deck: 1, reason: "EXP/PIT-001"}
  conditional_requirements:
    - {when: {slide_count_gte: 8}, require: image_slot_present, reason: "GR/RULE-7"}
    - {when: {payload_has: time_series}, require: family_in: [chart], reason: "PG/DATA"}
  opening_priority: [table_insight, big_number, key_takeaway]   # advisory rank
  page_furniture:
    content_pages: [action_title_band, source_line, page_number]
    exempt_classes: [cover, divider, closing]
```

**(c) Machine-recorded Stage-4 gate record** (single source of truth; verdict derived, never asserted):

```json
{
  "schema": "ppt-hybrid-lab.gate.v1",
  "stage": "S4_visual",
  "inputs": { "ir_digest": "sha256:...", "pptx_digest": "sha256:..." },
  "decision": { "passed": false, "rule": "blocking_count == 0" },
  "findings": [
    { "id": "geom.bounds.right", "tier": "post_render_structural",
      "severity": "error", "disposition": "blocking", "slide": 6,
      "measured_in": 12.61, "limit_in": 12.533,
      "target": { "archetype": "chart.donut", "slot": "legend" } }
  ],
  "exemptions": [
    { "check_id": "label.edge_proximity",
      "scope": { "archetype": "flow.timeline", "slot_index": "last" },
      "evidence_ref": "EXP/PIT-005", "approved_by": "engine-owner",
      "expires": "2026-09-01" }
  ],
  "advisory": [
    { "id": "hierarchy.no_dominant_region", "tier": "multimodal_review",
      "slide": 9, "detail": "max region area = 1.3x median" }
  ],
  "scores": { "structural": 88, "hierarchy": null }
}
```

Design rules embedded above, each fixing an MCK defect: exemptions are **scope-bound** (archetype+slot, expiry, approver — fixes row 5), blocking/advisory separated (fixes I3), verdict rule stated in-record (fixes "AI signs its own certificate"), every limit traceable to an experience/rail ID (fixes prose-drift), digests bind gate to exact IR/render artifacts.

### 5.3 Check tiering (Q7)

| Tier | Checks (from MCK inventory) | Rationale |
|---|---|---|
| **T1 Compiler (pre-render, on Visual IR)** | slot arity & cardinality; per-field char budgets; forbidden `\n` in fixed-height slots; required fields (source); archetype existence (reject unknown — fixes I2a); rarity caps; adjacency; chart dimension limits; **sizing solvability** (does a packing exist ≥ floors & gaps? else fail with split/merge hint); **predicted text fit** per region using the shared measurement model; furniture presence per page class; conditional requirements (image slot, chart family) | All inputs exist in IR; failures are cheap to fix before render; mirrors MCK's own finding that S3-class errors are never caught by mental review (README anti-pattern 2). |
| **T2 Post-render structural (on PPTX)** | bounds overflow (single tolerance source — fixes row 19); negative dims; connector/`p:style` corruption; peer-font consistency (raise min-group to 2, or make configurable — fixes row 9); legend/label cluster overflow; text/line collision; text-text overlap; font-floor violations; **actual-vs-predicted drift** (compare rendered text extents against T1 predictions; drift > ε ⇒ recalibrate estimator) | Depends on final geometry/attributes that autofix or renderer may have altered. |
| **T3 Pixel / multimodal review** | focal hierarchy strength; weighted balance & dead-space aesthetics; contrast/legibility; chart label crowding as perceived; brand-feel consistency; final "ship/no-ship" aesthetic judgment | No geometric proxy can measure these (MCK proof: rows 8, 29, 31 + their own A/B caveat). Advisory until calibrated; specific prompts in §5.5. |

### 5.4 Self-refinement loop redesign (Q5)

Keep MCK's triage (ONE-TIME vs PATTERN) and evidence-gated exemption culture; replace free-text markdown as *machine input* with a structured ledger:

```yaml
experience:
  id: EXP/OVF-004
  date: 2026-05-02
  signature:            # matcher, not prose
    archetype: flow.horizontal_chevron
    symptom: text_overflow
    target_slot: steps.badge
  root_cause: fixed_primitive_height
  fix_transform: forbid_multiline_badge
  promotes_to:
    - compiler_validation: slot.multiline=false
    - regression_fixture: case_chevron_badge_newline
  status: promoted       # proposed | promoted | retired
```

Loop: failure → record → promote to T1 validation + regression fixture → exemption whitelists only ever reference `experience.id` with scope+expiry. MCK's "Rule" field becomes the `promotes_to` block; their whitelist-evidence requirement becomes `evidence_ref` mandatory.

### 5.5 Preventing the Stage-3 failure mode: equal-weight layouts, weak focal hierarchy, dead space (Q10)

MCK's only relevant instruments are binary grid coverage >55% (row 8), "usage ≥50%" prose, and adjacency diversity — none measure hierarchy. Add, in order of leverage:

1. **Focal-region requirement per archetype (T1).** Each archetype declares a focal slot (or `focal: none` for deliberately flat archetypes like TOC). Compiler verifies exactly one region satisfies: `area_share ∈ [0.25, 0.70]` **or** `type_size ≥ 1.8 × body_pt` **or** inverted-fill emphasis. Fail with `equal_weight_risk` otherwise. (Directly targets metric_cards/four_column/icon_grid-style outcomes.)
2. **Sibling variance floor (T1).** For non-tabular archetypes: `stdev(sibling_areas)/mean ≥ 0.15`, else warn. Kills uniform tile grids.
3. **Ink-weighted coverage band (T1 predict, T2 confirm).** Replace binary cell coverage with weight = Σ(font_pt × contrast_factor × filled_fraction) per grid cell; require weighted coverage ∈ [0.45, 0.85]. A giant BG_GRAY panel no longer "covers" like dense content (fixes row 8's blind spot in both directions — dead space *and* wall-to-wall monotony).
4. **Dead-zone prediction at composition time.** Port `_identify_dead_zones` naming (bottom_third/right_third/left_third/center) but evaluate on *planned* IR geometry: if the archetype's natural fill leaves a named zone >80% empty, require either a bottom summary slot, a focal enlargement, or an archetype swap — before rendering.
5. **Bottom-anchor policy.** If planned content bottom < ~5.6" with no summary/furniture slot, flag `floating_content` (generalizes MCK's bottom-bar rails, rows 13/20).
6. **T3 multimodal hierarchy review** with structured output: "Name the first element the eye lands on; is there exactly one dominant region; which quadrant/zone is dead; rate 1–5." Feed as advisory findings into the gate record; promote recurring signatures into T1 rules via the §5.4 loop.

---

## 6. REJECT / DO NOT PORT

| Reject | Why (evidence) |
|---|---|
| **Flat high-level component API as product architecture** | Already rejected by lead; reaffirmed: 72 numbered types with positional identity (`Pattern#`) bind semantics to catalog indices (`layout-catalog.md`, `engine-api.md`). |
| **Card-grid defaults & "≥3 visual blocks" normalization** | `planning-guide.md` density rules + card-heavy Quick Match push equal-weight tiles; no hierarchy counterweight anywhere (I3, §5.5). |
| **Category-global whitelist exemptions** | Row 5: code contradicts its own documented timeline-only scope. Port exemptions only as scope-bound records (§5.2c). |
| **AI self-eval gates at ANY stage** | Their own anti-patterns #1–#3 exist because S1/S2 remain self-checked (rows 31; SKILL.md). Make S2 mechanical: existence, counts, adjacency, rarity, duration math, title-length are all computable. |
| **Prose/YAML-as-documentation serving as constraint source of truth** | Rows 1–3, 31: declared budgets and the verb-rule are unenforced. Constraints must live in one machine-consumed registry. |
| **Geometry-only pass criteria; score-agnostic shipping** | Row 4/29: `passed` ignores score; warnings never block; no aesthetic tier. Adopt T3. |
| **Retired-but-live API surface** | `venn`, `funnel`, `gauge` marked "⚠️ RETIRED" in docstrings yet still callable and still tested in `run_qa_tests.py`; catalog retains struck-through entries. Our registry must hard-retire (remove from valid-id set) so compilers reject them. |
| **Per-archetype hand-coded checker functions as the extension mechanism** | `gate_check_s3.py::LAYOUT_CHECKERS` requires editing Python per layout; ~45 methods uncovered. Use data-driven registry + generic validator over slot schemas. |
| **Duplicated constants / dual tolerances / env-pinned paths** | Rows 18, 19, 4 (`~/.workbuddy/...` hardcoded in gate script; qa.py re-declares geometry "must match"). Single constants module; inject paths. |
| **Regex-brittle filters inside QA** | Page-number exclusion `^\d+/\d+$` and footer `top > 6.8` cutoff in `_check_chart_legend_overflow` break under format change; tag furniture shapes explicitly in IR instead. |
| **Doc-numbering drift as tolerated state** | README "13 rules" vs guard-rails.md "10 rules"; engine-api lists `staircase #15b` not present in engine; "67 layouts" vs 72-row catalog vs retired trio. Version the registry; generate docs from it. |

---

## 7. Open Questions / Exact Follow-Up Source Needs

1. **`references/layouts/*.md` (entire directory)** — routed by INDEX/SKILL for S4 but **not supplied**. Needed to finish Q6 (which layout notes are archetype constraints vs renderer recipes). Priority: `charts-circular.md`, `frameworks.md`, `structure.md`.
2. **`mck_ppt/engine.py` tail** — supplied copy truncates mid-`two_col_image_grid`; `numbered_list_panel` (claimed v2.3.1 dynamic row height in CHANGELOG notes) is **not visible**. Fetch full file or the symbol `MckEngine.numbered_list_panel`.
3. **Runtime consumers of `layout-matrix.yaml`** — confirm I1: grep repo for `yaml`, `safe_load`, `layout-matrix` outside docs. If truly unconsumed, our registry design is validated; if some loader exists, fetch it.
4. **`CHANGELOG.md`** — version evolution of rules/limits (useful for distinguishing stable invariants from recent experiments).
5. **Git history of `experiences/`** — verify I5 (backfill vs organic accumulation); request log for `experiences/*` around 2026-04→05.
6. **Any gate-level tests** — `run_qa_tests.py` exercises `PptQA` only; no supplied test executes `gate_check*.py`. Confirm whether tests exist elsewhere (e.g., `examples/`, CI config) before we claim the gates are regression-covered.
7. **`MAX_WARNINGS_ALLOWED` usage** — unused in supplied `gate_check.py`; confirm no other consumer before discarding the concept (we'd repurpose it as an advisory-threshold anyway).
8. **Multi-theme plumbing** — `layout-matrix.yaml` lists `tech_minimal` as 待扩展; `constants.py` has a single profile. If themes matter for ppt-hybrid-lab, need the intended theme-parameterization surface (likely UNKNOWN/not-yet-built).

---

**Authority note:** All findings above are investigation and recommendation only. Canonical acceptance/modification of the proposed registry and gate schemas rests with the lead architect.