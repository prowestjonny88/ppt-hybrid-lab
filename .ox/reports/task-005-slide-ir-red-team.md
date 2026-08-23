# Ox Alpha — Red-Team Report: Stage 3 Slide IR Draft V0

**Task:** task-005 · **Type:** architecture_red_team · **Ref inspected:** `1d15d3ec4c763ddf06c07ffd7602726ea4138479` (supplied bounded context: 7 files)
**Mode:** analysis only. No repositories were modified.

---

## 1. Executive verdict

### **FREEZE-WITH-CHANGES** — conditional freeze.

The four-layer separation (reasoning → semantic visual → render plan → realization) is sound and worth preserving. **[DIRECT EVIDENCE]** `architecture/SLIDE_IR_DRAFT_V0.md` §2 explicitly separates the layers and §9 correctly places `fallback_policy` and `full_slide_rasterization_allowed` at the variant/policy level, not in semantics.

However, the draft **must not be frozen as-is**, because:

1. The change-impact contract's own P1 example is **falsified by the schema's own fields** (denormalized prose embedding literal values). A compliant compiler following §14 would ship a self-contradicting slide and pass the fidelity checks.
2. The supplied example IR `experiment/queuezero/slide_ir/validation_traction.v0.json` **already contains dangling references**, demonstrating that the proof-object/semantic-object identity boundary is broken in practice, not just in theory.
3. "Bounded" image regeneration is not actually bounded — no frame, aspect ratio, exclusion zone, or insertion region exists anywhere in the schema, so P3/P8/P10 of the panic protocol are unexecutable-as-specified.
4. Two verification probes must pass before the 3×3 build starts (see §13).

All required fixes are additive or small migrations. None require abandoning the layering. Patch list in §10; freeze gates in §14.

---

## 2. Critical architecture flaws, ranked by severity

### C1 — CRITICAL: Denormalized prose falsifies the change-impact contract (P1 blast radius understated)

**[DIRECT EVIDENCE]** The value `76%` appears as a literal string in **at least six independent locations** in the invariant layer:

| Location | File | Field |
|---|---|---|
| Evidence record | `validation_traction.v0.json` | `evidence[weekly_use_intent].statement` ("76% of 42 tested students…"), `.value`, `.display_value` |
| Top-level prose | `SLIDE_IR_DRAFT_V0.md` §3 / JSON | `subtitle_support`: "…produced a 3.8-minute MAE and **76%** weekly-use intent" |
| Exact-value list | JSON | `must_keep`: `"76%"` |
| QA prose | JSON | `qa_expectations`: "All four numeric findings remain exact." |
| Metric label channel | JSON | `metric_weekly_intent` (via `content_ref` — this one is correct) |
| Contract example | `SLIDE_IR_DRAFT_V0.md` §14 | declares the edit "affects: evidence.weekly_use_intent + metric_weekly_intent; **should not affect**: hero visual, title geometry, other metrics" |

**[INFERENCE]** A compiler implementing §14 literally will update the metric and evidence but leave `subtitle_support` and `must_keep` stale. The rendered slide then shows "81%" in the KPI and "76%" in the subtitle. Under protocol §11 ("requested new value preserved after edits; no hallucinated metrics") this is either a fidelity failure or — worse — an ambiguous pass, because the *metric* was preserved. The change-impact contract is the document the benchmark trusts; it is wrong on its first example.

**[RECOMMENDATION]** Smallest fix: template bindings. Allow `{evidence_id.display_value}` tokens in `governing_claim` / `subtitle_support` / semantic-object `content` / `must_keep`, plus a lint rule: every literal that matches an evidence `display_value` must either be a binding or be flagged. Change-impact rule: *any evidence revision touches all prose fields bound to it.* Update §14 accordingly.

### C2 — CRITICAL: No referential integrity, and the example IR already violates it; no deletion cascade

**[DIRECT EVIDENCE]** In `validation_traction.v0.json`:

- `relationships[2].from = "validation_evidence_stack"` — this is a **`proof_object_id`**, not a `semantic_objects[].object_id`. The relationship schema (draft §7) defines endpoints as semantic objects. **Dangling reference in the shipped example.**
- `hierarchy.visual_protagonist = "validation_evidence_stack"` — same defect (draft §11).
- The relationship name `technical_metrics_support_prototype_performance` (plural "metrics") has `from: "metric_mae"` — a single endpoint. The n-ary intent cannot be expressed.

**[DIRECT EVIDENCE]** Nothing in the draft defines deletion semantics. P7 (delete one metric) orphans, at minimum: `relationships[1]` (`survey_metric_supports_initial_demand`), `proof_object.primary_object_ids`, `hierarchy.primary_numbers`, and the `demand_evidence` group tag. The draft's §15 QA list contains no referential-integrity check.

**[RECOMMENDATION]** (a) Add a referential-integrity validator as a freeze gate: every `content_ref`, relationship endpoint, `primary_object_ids`, `hierarchy.*`, group membership, and `evidence_refs` must resolve. (b) Define exactly one deletion policy — recommended: **tombstone + explicit cascade record** (deleting an object marks dependent relationships `dangling_by_design` and removes them from `required_relationships`, with an audit entry), rather than silent dangling or hard forbid. (c) Either promote proof objects to first-class `role: "group"` semantic objects (preferred — see §7) or introduce a typed reference (`{"ref_type": "proof_object", "id": …}`) so endpoints are unambiguous.

### C3 — CRITICAL: No geometry/region layer — "bounded" regeneration is unbounded, P4/P5/P8 have no home

**[DIRECT EVIDENCE]** Across the entire schema there is **no field carrying any rectangle, frame, aspect ratio, safe region, or insertion zone**:

- `assets` (draft §8) have `crop_policy: "contain"` but no frame or aspect ratio. The image generator for `hero_visual_problem` has no way to know what shape of canvas to generate, and the compositor has no frame to place it in.
- The draft §16 Q6 acknowledges text-free zones are an open question; they are not just open, they are structurally unrepresentable today.
- P8's "designated safe region" (protocol §4) exists nowhere: `deck_system.safe_margins` (§12) is margins, not insertion zones.
- **[DIRECT EVIDENCE]** `architecture/MCK_NATIVE_COMPONENT_ADJUDICATION.md`, "Minimum native component API": *"Every primitive must return a realization record containing semantic object ID, emitted PPT object ID(s), render lane, **bounds**, and fidelity/editability classification."* The draft §13 realization record omits **`bounds`**. The IR draft is non-compliant with the adjudicated task-004 conclusion.

**[INFERENCE]** Without a region layer: P10 cannot guarantee "hero visual asset changed / native title unchanged" (a regenerated image can occlude the title and nothing in the schema forbids it); P4's "30 px equivalent" has no defined coordinate frame; P5's "-15%" has no box to shrink within; structured-recompile edits (protocol §6 `LOCAL_STRUCTURED_RECOMPILE`) have nowhere to record a user geometry override.

**[RECOMMENDATION]** Add a minimal slide-level `regions` map: named relative-rect frames (fractions of slide, resolution-independent) with `purpose` (`hero_frame`, `insertion_zone`, `safe_area`), referenced by slots and assets. Realization records absolute bounds (EMU) per emitted object. Define the panic protocol's "px equivalent" against a fixed reference canvas (e.g., 1280×720) in the protocol, not per-variant.

### C4 — CRITICAL: No round-trip identity — manual edits are untracked and will be destroyed by recompile

**[DIRECT EVIDENCE]** `MCK_NATIVE_COMPONENT_ADJUDICATION.md`, Modify section: *"Do not use position/name heuristics as object identity. Every emitted object in Stage 3 must trace to a stable semantic object ID."* The draft §13 realization map lives **outside the PPTX** and the draft specifies no shape-naming convention, no PPTX↔realization reconciliation, and no policy for objects the user adds manually.

**[INFERENCE — adversarial scenario]** P8 inserts a sponsor logo in PowerPoint. Then P1 triggers a `LOCAL_STRUCTURED_RECOMPILE`. The sponsor logo is not in `semantic_objects`, so a re-emit **deletes the user's object**. The protocol executes edits as a sequence against each architecture; this failure is reachable in the benchmark itself, not a hypothetical. Likewise, P4 (drag a KPI) makes the realization map stale; the §7 collateral-damage ratio requires object-level diffing that is impossible without identity embedded in the PPTX.

**[RECOMMENDATION]** (a) Mandatory deterministic shape-name convention, e.g. `oxq:{slide_id}:{object_id}[:{part}]` written into `shape.name` (and/or alt-text) at emit time. (b) Realization records gain `pptx_content_hash` + `realization_rev`. (c) An **adoption rule**: user-added objects inside a declared `insertion_zone` are adopted as `provenance: "user_added"` semantic objects on reconcile; user objects outside zones are preserved-but-flagged. This single rule makes P4/P8 auditable and protects manual work from recompiles.

### C5 — HIGH: Render-lane policy leaks into semantics, and role-keyed routing is not expressive enough

**[DIRECT EVIDENCE]** Draft §6: semantic objects carry `allowed_render_lanes` and `preferred_render_lane`. Draft §9: `render_plan.routing` is keyed by **role** (`"metric": "native"`), not by object.

**[INFERENCE]** Two defects: (1) leakage — "which engine draws this" is a realization decision, and it is *derivable*: `must_remain_editable` ⇒ lane ∈ {native, svg-with-native-text}; `raster_allowed` ⇒ image permitted. The lane fields are redundant with `editability_priority` and will drift from it. (2) Expressiveness — role-keyed routing forces all objects of a role into one lane. On S2 (`how_it_works`), one diagram node may be a screenshot thumbnail (native picture) while its siblings are SVG freeform; the current schema cannot express that.

**[RECOMMENDATION]** Concrete three-tier split:
1. **Semantics** keeps only `editability_priority` (this is genuine user intent). Delete `allowed_render_lanes` / `preferred_render_lane` from semantic objects.
2. **Capability registry** (pipeline-level, not per-slide): declares what each lane can do (`svg_lane.text_as_curves: false`, `native_lane.supported_roles`, `image_lane.bounded_only: true`).
3. **Render plan** (per variant): role→lane defaults + per-object-id overrides + recorded `reason` per decision + fallback records. The router must satisfy `editability_priority` as a hard constraint; `fail_closed` stays.

### C6 — HIGH: Editability QA hole — "non-raster" ≠ "editable" (SVG text-as-curves)

**[DIRECT EVIDENCE]** Draft §15: *"every `must_remain_editable` object maps to at least one non-raster PPT object."* Protocol §5 audit counts `native text object count`. But vector **text converted to curves** is non-raster and passes §15 while being completely uneditable.

**[INFERENCE]** P9 (diagram wording change) routes connectors/diagram nodes through the SVG→DrawingML lane (draft §9 routing example: `"diagram_node": "svg"`). Whether the constrained SVG lane emits text as native text frames or as curve outlines determines whether P9 scores `DIRECT_PPT_EDIT` or `BLOCKED`/`OCR_RECONSTRUCTION`. `PROJECT_STATE.json` records `ppt_master_closed_native_text_grammar: true` and `ppt_master_fail_closed_svg_compiler: true`, but the supplied context does not show the compiler's text handling.

**[RECOMMENDATION]** (a) Extend the realization `fidelity` enum: `semantic_and_editable` | `vector_text_as_curves` | `bounded_raster` — and make QA assert `must_remain_editable` **text** maps to a text-frame-bearing object, never curves. (b) Run the verification probe in §13 before freeze.

### C7 — HIGH: Benchmark-fairness mechanics are absent from the schema

**[DIRECT EVIDENCE]** Protocol §3: image-first keeps "Semantic IR … stored externally for comparison." Draft §2: "Reasoning remains identical across A/B/C. Only the render plan should differ." But the draft stores `render_plan` **inside the same document** as semantics (§3 top-level schema), and the example JSON has `render_plan: {variant: "unresolved", routing: {}}` — so the three variants are either three full documents (drift risk: someone edits evidence in A's copy only) or an unspecified overlay mechanism.

**[INFERENCE]** Additional asymmetries with no control: (a) nothing proves B/C received no extra facts; (b) the image prompt for A is derived from the IR by an unspecified process — if the derivation drops `does_not_prove` guards, A can render a big "validated ✓" and *win the blind review while violating evidence semantics*; (c) `hierarchy` gives only relative sizes ("large"), so the image model invents typography freely while the native lane must guess — visual-retention scores would penalize hybrid for **spec gaps**, not architecture.

**[RECOMMENDATION]** (a) Split documents: invariant `slide_semantics` + `render_plan.{a,b,c}` overlays; the harness asserts an identical **semantic-layer hash** across all three variants. (b) Add a `variant_input_manifest` per variant recording exactly which IR fields and prompts each pipeline consumed (prompt hash included). (c) Freeze a minimal type scale in the deck system (§10, C9) so all three variants share typography intent.

### C8 — MEDIUM-HIGH: Evidence model cannot represent the benchmark's own facts

**[DIRECT EVIDENCE]** Draft §4: `value` is a scalar; statuses are `confirmed | assumption | inference | uncertainty`; `source_ref` is an opaque string. No derivation, range, revision, or conflict fields.

- **[DIRECT EVIDENCE]** `experiment/queuezero/brief.md` S1 requires "**15–30 minutes** wasted at peak meal periods" — a **range**, unrepresentable as `value: number`. The problem slide's headline fact cannot round-trip through the evidence model.
- Derived values: "76% of 42 students" is a ratio; nothing links numerator/denominator or recomputes on edit.
- Revision: P1 (76→81) destroys the prior fact with no `history`/`supersedes` — the protocol's audit trail and any "revised evidence" question are unsupported.
- Conflict: two contradictory evidence items have no representation; renderer behavior is undefined.
- Source spans: `source_ref: "queuezero_benchmark_brief"` has no locator/quote; provenance is unverifiable.

**[RECOMMENDATION]** Minimal additions (all optional fields, no breaking change): `derivation {formula, input_evidence_refs[]}`, `value` widened to `number | {min,max}` (or sibling `range`), `supersedes: evidence_id`, `history[]` (one entry deep is enough for Stage 3), `conflicts_with[]`, optional `source_span {quote, locator}`.

### C9 — MEDIUM: Design tokens and type scale are unfrozen, making P5/P6 nondeterministic

**[DIRECT EVIDENCE]** Draft §12: `design_tokens: {}` — "intentionally not frozen yet." Semantic objects carry **no `style_ref`/token binding**, while the adjudicated MCK API includes `bind_style_token(object_id, token_ref)` and `style_ref` on every primitive. Protocol P6 checks "tokenized/local color update" and "unintended raster regions that cannot follow the theme."

**[INFERENCE]** With no token vocabulary and no object→token binding in the IR, P6's blast radius ("objects bound to that token", draft §14) is **uncomputable** — the renderer's incidental choices become the de facto binding. Generated hero art that consumed the accent blue has no declaration of that fact, so nothing tells you the raster must be regenerated or will clash ("visibly stitched" failure, protocol §13).

**[RECOMMENDATION]** Freeze a **minimal** benchmark token set (`accent.primary`, `accent.on`, `surface`, `surface.raised`, `text.primary`, `text.secondary`) + a type scale (display/h1/h2/body/caption) + per-role default `fit_policy`. Add optional `token_refs[]` on semantic objects (renderer may default by role, but the binding must be recorded in realization). Add `palette_token_refs` + `regeneration_trigger: "token_change" | "manual" | "never"` on generated assets. Require the SVG lane to resolve colors **only** through tokens (fail-closed on missing token) so P6 cannot leave hardcoded SVG literals behind. Map `accent.primary` to a PPTX theme color slot so direct theme recolor also works in PowerPoint.

### C10 — MEDIUM: Grouping is tags without containers; reflow on delete is undefined

**[DIRECT EVIDENCE]** `visual_intent.group` is a free string (`"demand_evidence"`); the role vocabulary contains `group` (§6) and the adjudicated API has `add_group(object_id, child_ids, semantic_role)`, but the example IR contains **zero group objects** despite using four group tags. No `member_ids`, no order, no `layout_hint`, no reflow policy.

**[DIRECT EVIDENCE]** Protocol P7 explicitly tests "whether layout collapses gracefully or leaves an unacceptable hole." With no group container there is no reflow policy to test — every variant will improvise.

**[RECOMMENDATION]** Add `role: "group"` objects: `{member_ids (ordered), layout_hint: row|grid|stack|free, reflow_policy: reflow|collapse|leave_gap}`. This also fixes C2's n-ary relationship problem: `technical_metrics_support_prototype_performance` becomes a relationship **from the group** `technical_evidence` to `pilot_gate`.

---

## 3. Renderer leakage analysis

| Item | Location | Classification | Ruling |
|---|---|---|---|
| `allowed_render_lanes`, `preferred_render_lane` | §6 semantic object | **Leak.** Redundant with `editability_priority`; variant-dependent | **[RECOMMENDATION]** Remove from semantics; re-express as render-plan policy + per-object overrides (C5) |
| `editability_priority` | §6, §8, §10 | **Correct in semantics** — it is user intent about the artifact, not a rendering decision | Keep |
| `visual_intent.emphasis / relative_size / group` | §6 | Borderline but defensible: communication intent, renderer-agnostic | Keep; `group` tag should cross-check the group container (C10) |
| `allowed_visual_forms` / `forbidden_visual_forms` | §7 | Dual-nature: visual vocabulary, but encodes **claim safety** (flywheel ⇒ causation) | Keep as compiled hints; make structured `forbidden_implications` (§5) the source of truth (§6 of this report) |
| `crop_policy` | §8 | Acceptable: constrains how an asset may be framed — a slot-level semantic constraint | Keep; add frame reference (C3) |
| `fallback_policy`, `full_slide_rasterization_allowed` | §9 | **Correct placement** (variant/policy layer) | Keep |
| `routing` keyed by role | §9 | Right layer, wrong key granularity | Object-id overrides (C5) |
| Variant-conditional QA strings in the invariant doc | JSON `qa_expectations` items 4–5 ("in native/vector and hybrid variants…") | **Leak**: variant concerns inside the variant-invariant document | Move structural-variant QA to render plan/protocol; keep content QA (numeric exactness) in semantics |
| `subtitle_support` vs `subtitle` object | §3 vs JSON `semantic_objects[1]` | Two different strings both functioning as "subtitle" (`subtitle_support` embeds numbers; the object's `content` does not) — drift channel | **[RECOMMENDATION]** Render-facing text lives only in semantic objects; `subtitle_support`/`why_it_matters` become bound prose or are dropped |

---

## 4. Identity and change-impact failure analysis

**What is sound.** `object_id` / `evidence_id` / `asset_id` / `relationship_id` namespaces exist, `content_ref` links metrics to evidence, and the realization map concept (§13) is the right anchor for change impact. **[DIRECT EVIDENCE]** §14's four examples show the intended discipline.

**Failure inventory (all reachable by the mandatory panic edits):**

1. **P1 (76→81):** understated blast radius — C1. Six touchpoints, contract names two.
2. **P7 (delete metric):** dangling refs, no cascade — C2. Also: does `must_keep` shrink? Undefined.
3. **P4 (move KPI) / P5 (title resize):** no geometry layer to record overrides or verify "30 px"/"15%" — C3. Direct PowerPoint drag is fine (`DIRECT_PPT_EDIT`), but the structured-recompile path has no override home, and the realization map goes stale with no reconciliation rule — C4.
4. **P8 (sponsor logo):** no insertion zone (C3); **adoption gap** — a user-added object is invisible to the IR and destroyed by the next recompile (C4). This is the single most dangerous unhandled interaction in the protocol sequence.
5. **P9 (diagram wording):** connector label editability depends on unverified SVG text behavior (C6); label length change needs `fit_policy` that doesn't exist (§8).
6. **P10 (hero regen):** no frame/aspect/exclusion/palette declaration (C3, C9); asset versioning is implicit only (realization references `hero_visual_problem_v2` vs `asset_id: "hero_visual_problem"` — **[DIRECT EVIDENCE]** draft §8/§13 — make instance versioning explicit: stable slot id, versioned asset instances).
7. **P6 (accent recolor):** uncomputable impact set without token bindings (C9).
8. **P3 (screenshot replace):** best-handled edit (same-bbox replacement, per MCK evidence) — but still needs the frame + crop anchor + instance versioning from C3.

**[RECOMMENDATION]** Add to §14 a **rule-form contract**, not examples: impact(evidence_revision) = {objects via content_ref} ∪ {bound prose} ∪ {must_keep entries} ∪ {derived evidence} ∪ {assets with regeneration_trigger=token/value change}; impact(token_change) = {bound objects} ∪ {generated assets consuming token}; impact(delete) = per cascade policy. Plus the idempotence rule: *recompile with unchanged semantics must produce an identical object set except the edited object* — otherwise the §7 collateral metric measures compiler noise, not architecture.

---

## 5. Evidence/provenance model gaps

| Required capability (task question) | Status | Evidence |
|---|---|---|
| Raw facts | Partial | §4 fields exist; `source_ref` opaque string, no span **[DIRECT EVIDENCE]** |
| Derived values / simple arithmetic | **Missing** | No `derivation` field; "76% of 42" unlinkable **[DIRECT EVIDENCE]** |
| Ranges | **Missing** | `value` scalar; brief requires "15–30 minutes" **[DIRECT EVIDENCE]** |
| Assumptions / inferences / uncertainty | Present as statuses | §4 vocabulary; but no rule maps status → allowed visual treatment. JSON `qa_expectations` says "pilot gate visually distinct from confirmed evidence" — hand-written prose where a structural rule belongs: **[RECOMMENDATION]** deck-system rule `uncertainty ⇒ distinct treatment`, and give `pilot_gate` an `evidence_status_ref` so the rule is checkable |
| Source spans | **Missing** | Add optional `source_span {quote, locator}`; population can be deferred, the field cannot (schema-break avoidance) |
| Conflicting evidence | **Missing** | Add `conflicts_with[]` + resolution policy |
| Revised evidence | **Missing** | Add `supersedes` + `history[]`; P1 becomes a revision, preserving audit trail |
| `does_not_prove` enforcement | Declared, not enforceable | §4 guardrail + §5 `forbidden_implications` are free text; no mapping to checkable visual forms — see §6 |

---

## 6. Relationship and misleading-visual risk analysis

The draft's instincts are good — relationships are first-class, `forbidden_visual_forms` bans flywheels/checkmarks, and §7 says causal types require supporting evidence. **[DIRECT EVIDENCE]** §7 example bans `causal_flywheel` and `retention_loop`. What's missing:

1. **Evidential weight is unrepresented.** `semantic_strength: "explicit"` describes explicitness, not support strength. A single n=42 survey "supports" the demand claim only weakly; a thick causal-style arrow overstates it. **[RECOMMENDATION]** Add `support_strength: weak|moderate|strong` on `supports`-type relationships, with a deck-system visual mapping policy (weak ⇒ no heavy arrow / no emphasis color).
2. **`forbidden_implications` are unenforceable prose.** **[RECOMMENDATION]** Structure them: `{implication_id, text, forbidden_visual_forms[], forbidden_depictions[], applies_to_object_ids[]}`, and derive per-slide instances from evidence `does_not_prove`. QA then checks mechanically. Extend `forbidden_depictions` to **generated art briefs** — a hero image depicting a green approval checkmark next to the metrics is a visual claim no evidence supports, and today nothing bans it.
3. **`supports` relationships may have empty `evidence_refs`.** §7's own `camera_to_estimator` example has `evidence_refs: []` — legitimate for `data_flow`, but **[RECOMMENDATION]** make ≥1 evidence ref mandatory for `supports` / `must_pass_before`.
4. **N-ary support impossible** — fixed by group containers (C10).
5. **Correlation guardrail:** `correlates_with` is in the vocabulary but unused in Stage 3 slides. Keep the type but add a default rule: `correlates_with` forbids causal forms unless an explicit override with causal evidence exists. Cheap insurance; enforce later.

---

## 7. Grouping, ownership, nesting, ordering, constraints

- **Containers:** missing — C10. `visual_intent.group` tags are not groups.
- **Nested objects / composite realization:** adequately representable — one semantic object may emit multiple PPT objects (`realization.ppt_object_ids` is an array, §13), and the metric card (value + label + background) works this way. Sub-part editing (label vs value) would want `part` discrimination in the naming convention (`…:{object_id}:{part}`) — covered by C4's fix.
- **Repeated components:** four metric cards are explicitly enumerated — acceptable for Stage 3. **[RECOMMENDATION]** Defer prototype/instance patterns; do not add now.
- **Z-order / reading order:** absent. **[DIRECT EVIDENCE]** no field in §6/§11. **[RECOMMENDATION]** Minimal: optional `z_band: background|content|foreground` on semantic objects; group member order defines reading order within groups. Full z integers deferred.
- **Constraints (non-overlap, alignment, min sizes):** absent, and correctly so at semantic level — but the *realization* layer must record bounds (C3) so QA can assert constraints post-hoc. That is the Mck-adjudicated pattern: geometry QA with semantic IDs, not coordinate planning in semantics.

---

## 8. Text fitting and bounded image regeneration requirements

**Deterministic text fitting — minimum information set:**
1. Content (exists) + language (defer; English-only benchmark).
2. Font family + size **via deck-system type scale tokens** (missing — C9).
3. Box (realization `bounds`, missing — C3).
4. `fit_policy` per role with defaults: e.g., title `shrink_to_fit(min=0.85×)`, metric value `fixed`, body `wrap+shrink(min=0.8×)`, caption `clip+flag`. PowerPoint-native equivalents (`normAutofit`) should be emitted where possible so direct edits behave identically.
5. Overflow behavior must be **recorded, never silent** (extend the §15 fallback-recording rule to text fitting: `fit_result: fit|shrunk|overflow_flagged`).

P5 (-15% title) then becomes verifiable: new size ≥ policy min, re-fit deterministic, no cascade. Without items 2–4, P5 outcomes are renderer folklore.

**Generated hero declaration — minimum field set on the slot/asset:**
`frame_ref` (regions layer, C3) · `aspect_ratio` · `text_free: true` (hard rule: no `must_keep` strings or any text in generated art) · `exclusion_zones[]` (relative rects inside the frame that must stay low-detail for overlay legibility) · `safe_crop` · `composition_anchor` (relative focal point that must survive regeneration) · `palette_token_refs[]` (C9) · `forbidden_depictions[]` (§6) · `regeneration_scope: asset_only` (exists — **[DIRECT EVIDENCE]** §8) · `regeneration_trigger`.

P10's hard requirement (native everything unchanged, hero changed) is then checkable: the compositor places instance v+1 into the recorded frame; exclusion zones and anchor are generation-brief constraints; QA asserts only `picture_31`'s image part changed.

---

## 9. Benchmark fairness analysis (image-first vs native vs hybrid)

**The risk is real and currently unmitigated:**

1. **Semantic parity is asserted, not enforced.** Three full IR documents invite drift. **[RECOMMENDATION]** Invariant-layer hash asserted identical across variants (C7) — this is the single cheapest fairness control and it should be a hard harness check.
2. **Input asymmetry via prompt derivation.** A's whole-slide prompt is derived from the IR by an unspecified process. If it drops `does_not_prove`/`forbidden_depictions`, A can produce visually persuasive but semantically misleading slides and win blind review. **[RECOMMENDATION]** Prompt-derivation spec becomes part of the frozen protocol: must include governing claim, must_keep strings, hierarchy intent, type-scale intent, and all forbidden implications/depictions; prompt hash recorded in `variant_input_manifest`. Blind reviewers never see this; the audit does.
3. **Typography freedom asymmetry.** Image models invent kerning/scale natively; the native lane needs the type scale to compete fairly (C7c/C9). Otherwise §9's `visual_retention` measures spec completeness, not architecture.
4. **OCR asymmetry is already handled.** **[DIRECT EVIDENCE]** Protocol §11 restricts the OCR ban to "native/vector or hybrid lanes," implicitly permitting OCR as an *audit* tool for A's raster text. Make that explicit in the protocol ("OCR permitted for audit of A only; never as an edit path") so it isn't read as a loophole.
5. **No extra facts to B/C.** With the split-document design, render plans can only add lane decisions, not content; §15's "no semantic relationship is invented by the renderer" plus the semantic hash close this.

**Ruling:** with the C7 mechanics added, the same IR can fairly drive all three variants. Without them, the benchmark is biased in ways that would be invisible in the scores.

---

## 10. Minimum schema patch list before freeze

Ordered; items 1–6 are **freeze-blocking**, 7–12 strongly recommended, 13 is protocol-level.

1. **Split documents:** invariant `slide_semantics` (hash-pinned) + `render_plan.{a,b,c}` overlays + `variant_input_manifest`. Harness asserts semantic-hash parity. (C7, C5)
2. **Remove** `allowed_render_lanes`/`preferred_render_lane` from semantic objects; render plan gains role defaults + per-object-id overrides + recorded reasons; router hard-constrained by `editability_priority`. (C5)
3. **Add `regions` layer** (relative-rect frames: `hero_frame`, `insertion_zone`, `safe_area`) + realization `bounds` (EMU). Defines "30 px equivalent" against a fixed reference canvas in the protocol. (C3)
4. **Referential integrity validator + deletion cascade policy (tombstone + recorded cascade).** Fix the two existing dangling refs (`validation_evidence_stack` as relationship endpoint and `visual_protagonist`) by introducing group containers. (C2, C10)
5. **Round-trip identity:** deterministic shape naming `oxq:{slide_id}:{object_id}[:{part}]`, realization `pptx_content_hash`/`rev`, user-object adoption rule for `insertion_zone` contents. (C4)
6. **Structured `forbidden_implications`** with `forbidden_visual_forms` / `forbidden_depictions` / `applies_to`; derive from evidence `does_not_prove`; extend to generated-art briefs. Fidelity enum gains `vector_text_as_curves` (fails `must_remain_editable`). (C6, §6)
7. **Evidence patch:** `derivation`, range-valued `value`, `supersedes`+`history`, `conflicts_with`, optional `source_span`. (C8)
8. **Prose bindings** `{evidence_id.display_value}` in `governing_claim`/`subtitle_support`/`content`/`must_keep` + lint + updated §14 rule-form impact contract incl. idempotent-recompile rule. (C1)
9. **Freeze minimal tokens + type scale + per-role `fit_policy` defaults;** `token_refs[]` on objects (recorded in realization); SVG lane resolves colors via tokens only; accent token mapped to a PPTX theme slot; generated assets declare `palette_token_refs` + `regeneration_trigger`. (C9)
10. **Group containers** with `member_ids`/`layout_hint`/`reflow_policy`; relationships may endpoint on groups. (C10, C2)
11. **Generated-asset declaration set** (§8 of this report): frame, aspect, `text_free`, exclusion zones, safe crop, anchor, forbidden depictions, explicit asset-instance versioning (stable slot id, versioned instances). (C3, P10)
12. **Realization fallback records** `{from_lane, reason}` and `fit_result`; extend §15 QA with: referential integrity, semantic-hash parity, shape-name convention, curves-vs-text check, recompile idempotence.
13. **Protocol amendments:** define the px-reference canvas; make A-audit OCR explicitly legal; add P-sequence interaction note (P8-then-P1 exercises the adoption rule).

---

## 11. Fields to defer from Stage 3

| Field/capability | Rationale |
|---|---|
| Chart/table data schemas | No chart/table in the three QueueZero slides (**[DIRECT EVIDENCE]** `brief.md` S1–S3). Keep `chart`/`table` roles as stubs; when introduced: `data_ref` → `{series[], categories[], value_evidence_refs[], number_format, chart_type}`, table cells with per-cell evidence refs. Do not build now (MCK adjudication already warns against pseudo-charts). |
| `source_span` population | Field stub yes (avoid schema break); population deferred |
| Confidence scores / numeric uncertainty intervals | Optional later; statuses suffice for Stage 3 |
| `correlates_with`, `compares_to`, `contrasts_with` enforcement | Unused in the three slides; keep vocabulary, defer rules |
| Locale/i18n, `text_case` transforms | English-only benchmark |
| Prototype/instance patterns for repeated components | Explicit enumeration suffices for 4 metrics |
| Speaker notes, animations, transitions | Not in protocol; absent from draft — correctly so |
| `why_it_matters` as a separate channel | Collapses into bound prose or subtitle; redundant with `governing_claim` + subtitle object (**[DIRECT EVIDENCE]**: three overlapping prose strings in the example) |
| Full z-order integers | `z_band` is enough |
| Free-text `qa_expectations` | Replace derivable items (numeric exactness from `must_keep`) with generated checks; keep only genuinely slide-specific guards |

---

## 12. Concrete adversarial edit scenarios (current schema, pre-patch)

| # | Scenario | Failure under draft v0 | Patch that fixes it |
|---|---|---|---|
| E1 | P1 via IR edit only | Metric shows 81%, `subtitle_support` still says 76% — self-contradicting slide passes "requested new value preserved" | P8 (bindings), P-13 (contract) |
| E2 | Delete `metric_weekly_intent` | Dangling relationship, proof ref, hierarchy ref; compiler crashes or emits orphan connector | P4 (integrity + cascade) |
| E3 | P6 accent → orange | Hero raster stays blue; no field records it consumed the accent; "visibly stitched" outcome the decision rule fears | P9, P11 |
| E4 | P9 wording on S2 if SVG lane emits curves | `BLOCKED`/`OCR_RECONSTRUCTION`; §15 QA **passes** (non-raster) — silent QA hole | P6 + probe V1 |
| E5 | P10 regen with new composition | New hero occludes native title; no exclusion zone or frame to violate | P3, P11 |
| E6 | Router needs one diagram node native (screenshot thumbnail) among SVG siblings | Role-keyed routing cannot express it | P2 |
| E7 | Image-first prompt omits `does_not_prove` | A renders "validated ✓" badge, wins blind review, violates evidence semantics | P1 (manifests), P6 (depictions) |
| E8 | P8 logo, then P1 recompile | Sponsor logo deleted — not in IR, no adoption rule | P5 |
| E9 | S1 "15–30 minutes" | `value` scalar cannot hold the range; fidelity check loses its comparison target | P7 |
| E10 | Two conflicting survey results (76% vs 64%) | No conflict model; renderer picks arbitrarily | P7 |
| E11 | P4 drag KPI, then any recompile | Move lost or realization map stale with no reconciliation | P3, P5 |
| E12 | P5 title −15% | No type scale/fit policy/bounds → outcome is renderer folklore, not measurable | P3, P9 |

---

## 13. Residual unknowns / needs-more-source

1. **[UNKNOWN — probe V1, freeze-blocking]** Does the constrained SVG→DrawingML lane emit text as native text frames or curve outlines? Determines P9's achievable outcome class and validates patch P6. *Fetch:* the ppt-master SVG compiler source implementing the verified `ppt_master_fail_closed_svg_compiler` / `ppt_master_closed_native_text_grammar` capabilities (exact paths not in supplied context; PROJECT_STATE.json names the capabilities but not files).
2. **[UNKNOWN — probe V2, freeze-blocking]** Can the compile pipeline patch a single object in an existing PPTX (python-pptx in-place edit) or only re-emit the slide? Determines whether `LOCAL_STRUCTURED_RECOMPILE` is genuinely local and whether the idempotence rule (P8/§4) is implementable. *Fetch:* the Stage 3 compile pipeline skeleton once task-004's minimum API is implemented.
3. **[UNKNOWN]** Target schema of `generation_brief_ref` (hero briefs) — referenced in draft §8, not present in supplied files.
4. **[UNKNOWN]** `deck_system queuezero-default-v0` document — referenced by `deck_system_ref`, not supplied; token freeze (P9) depends on it.
5. **[UNKNOWN]** Object-level PPTX diff tooling choice for the §7 collateral metric — the protocol hedges ("if object-level diffing is unavailable…"); the shape-naming convention (P5) makes diffing tractable, but the tool should be named before the build.

---

## 14. Recommended verdict wording for the freeze gate

**Freeze-with-changes**, gated on:

- Patches 1–6 applied and the referential-integrity validator passing on a corrected `validation_traction.v0.json` (the two `validation_evidence_stack` dangling refs fixed);
- Probe V1 (SVG text behavior) and Probe V2 (single-object patch path) completed and their results written into the render-plan capability registry;
- The corrected example IR re-validated against the full P1–P10 impact contract on paper (E1–E12 must each have a defined outcome class).

The layering survives. What must not survive the freeze is the current §14 contract, the unbounded hero, the untracked PPTX round-trip, and the unenforceable guardrails — those four are the difference between a trustworthy controlled experiment and one that rationalizes whichever architecture ships the prettiest contradiction.

— Ox Alpha, subordinate forensic engineer. Analysis only; no canonical decisions made. Awaiting GPT adjudication.