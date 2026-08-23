# task-003 — RW Consulting PPT: Reasoning-System Extraction Report

**Analyst:** ox-alpha (subordinate forensic engineer)
**Source:** 10 supplied files, repo `Pikapika260214/rw-consulting-ppt`, commit ref `1df28e81…` as supplied in the bounded package (not independently re-verified against remote).
**Evidence tags:** [DIRECT] = verbatim in supplied source · [INF] = derived · [REC] = my engineering proposal · [UNKNOWN] flagged explicitly.

---

## 1. Executive finding

RW Consulting PPT is **two coupled systems in one repo**:

1. **A renderer-agnostic reasoning contract**: claim-first page architecture, typed evidence boundaries, claim↔evidence↔visual-semantics mapping, strict message hierarchy, a two-tier deck-level/page-local consistency model, and gated approval artifacts. This layer is expressed entirely in content terms (claims, proof, hierarchy, policies) and is **fully portable** to a renderer-agnostic Slide IR.
2. **An image-generation execution layer**: backend locks ("Image2-style full-slide generation"), prompt scripts optimized for diffusion-model composition freedom, PNG/contact-sheet QA, and image-only PPTX packaging. This layer consumes the reasoning contract but its mechanics are tightly bound to probabilistic full-slide image models and should **not** be carried forward.

The highest-value portable assets, in order of uniqueness/strength: (a) the four-state evidence-boundary schema (confirmed / assumption / inference / open uncertainty); (b) the *negative* claim-evidence map ("evidence does **not** prove X"); (c) visual-connector semantics guardrails (lines/gates/checkmarks/rings/2x2 as falsifiable claims); (d) the proven-vs-pending category lists; (e) the claim-type→proof-object picker; (f) the deck-system vs page-local separation (global invariants + per-page variation axes); (g) the named failure-label taxonomy, convertible into automated QA assertions.

The biggest obstacle to automated reuse: the contract assumes a **conversational human approver at three hard gates**, duplicates much of its rule text across SKILL.md and five reference files (drift risk), and hard-wires image-only routing whose stop conditions must be deliberately inverted for a deterministic renderer.

---

## 2. Exact reasoning sequence (raw content → visual direction)

Reconstructed from `skills/rw-consulting-ppt/SKILL.md` §Workflow, cross-checked against `references/consulting-image-context.md` §New-Project Invocation Pattern. All [DIRECT] unless tagged.

```
Raw brief / bullets / research notes
 │
 ├─ Stage 0  ALIGNMENT GATE (hard, conversational)
 │    12 required alignment items; 6 minimum user-controlled prefs:
 │    delivery mode, theme color, page count, detail level, visual style,
 │    output format (+ audience, core question, outline, language,
 │    evidence boundary, input-transformation mode).
 │    Stop condition: no artifact until user confirms or says "use defaults".
 │
 ├─ Stage 1  INPUT PRODUCTION PASS
 │    Transformation mode: Expand | Compress | Rewrite | Sharpen | Preserve
 │    Output artifact: `Inputs for PPT Production`
 │      - Context (audience/use case/mode/pages/language/theme)
 │      - Core Question (one question the deck answers)
 │      - Working Thesis (one-sentence judgment)
 │      - Storyline (numbered logic steps)
 │      - Page-Level Inputs per page:
 │        Claim / Why it matters / Proof object (draft) /
 │        Evidence available / Evidence needed / Caveats / Takeaway
 │      - Open Questions
 │    HARD STOP: user approves before blueprinting.   ← proof object first
 │                                                    appears as hypothesis
 ├─ Stage 2  NORMALIZE INTO MESSAGE INVENTORY
 │    core question; draft answer; supporting arguments;
 │    evidence/examples/numbers; USER ASSUMPTIONS; CODEX INFERENCES;
 │    open uncertainties.                            ← provenance typing born here
 │
 ├─ Stage 3  DECK BLUEPRINT
 │    title; one-sentence storyline; audience; page count;
 │    delivery mode + text-density target; per-page GOVERNING MESSAGE;
 │    per-page PROOF OBJECT; suggested VISUAL MOTHER CONCEPT;
 │    missing-evidence list.
 │    Rule: titles are conclusions, not topics
 │      ("Workflow ROI is replacing model price…" not "Pricing Overview")
 │    APPROVAL GATE 2 (mandatory visible handoff block).
 │
 ├─ Stage 4  SLIDE BRIEFS (13 fields per page)
 │    page #; page CLAIM (one complete sentence);
 │    EVIDENCE BOUNDARY {confirmed facts | user assumptions |
 │      Codex inference | open uncertainties};
 │    CLAIM-EVIDENCE MAP; PROOF OBJECT; VISUAL MOTHER CONCEPT;
 │    MUST-KEEP text/numbers (3–6); delivery mode;
 │    body copy (standalone only); source-note/caveat line;
 │    TEXT HIERARCHY; AVOID LIST; image prompt.
 │
 ├─ Stage 5  CONCEPT IMAGE DIRECTOR PASS
 │    visual mode ∈ {Clear Report | Hero Concept | Evidence Architecture};
 │    strongest proof object via PICKER; visual mother concept;
 │    evidence ANCHORS; claim-evidence FIT; VISUAL IMPLICATION GUARDRAILS;
 │    bad-output RISKS; PROMPT EXCLUSIONS.
 │    HARD STOPS: no named proof object → repair brief;
 │    weak structure (cards/table/3-column/process-arrows) → replace;
 │    >1 action title, >1 takeaway, or detached large metrics → split page.
 │
 ├─ Stage 6  PROMPT AS CONTENT SCRIPT  (image-layer; portability: §7)
 │
 ├─ Stage 7  SAMPLES: 1–2 representative PNGs
 │    (cover/opening thesis + densest body page; standalone must include
 │     ≥1 explanatory-text-density test)
 │
 ├─ Stage 8  SAMPLE REJECTION GATE → user approval   (see §5)
 │
 └─ Stage 9  DECK SYSTEM CONTRACT (authored from approved sample)
      → repeated VERBATIM in every batch prompt
      → batch generate → contact-sheet consistency QA
      → regenerate drifted slides → optional image-only PPTX packaging
```

**Canonical reasoning chain to preserve:** content → transformation mode → provenance-typed message inventory → core question + working thesis → storyline → per-page claim → evidence boundary → claim-evidence map (positive *and* negative) → proof object (typed, keyed to claim) → visual mode + mother concept → anchors + omit list → collapsed hierarchy → render contract → sample gate → deck system contract → batch → consistency QA. [INF from full pipeline]

---

## 3. Reasoning artifact & contract inventory

### 3.1 Produced artifacts (pipeline outputs)

| Artifact | Schema location | Notes |
|---|---|---|
| Alignment summary (6-pref block, zh) | SKILL.md §Alignment Gate | Conversational handoff |
| `Inputs for PPT Production` | SKILL.md §Workflow 1 | Full Markdown schema given |
| Deck blueprint + handoff block | SKILL.md §Workflow 3–4 | Self-contained approval required |
| Slide brief (13 fields) | SKILL.md §Workflow 5; consulting-image-context.md §Slide Brief Schema | Two slightly different field listings (see §10.4) |
| Sample page brief | SKILL.md §Workflow 5.5 | Compact: mode, proof object, mother concept, must-keep, evidenced-vs-pending, guardrails, omissions |
| Image prompt (content script) | SKILL.md §Prompt Pattern; concept-image-director.md §Prompt Skeleton | Base + standalone + live extensions |
| **Deck System Contract** | deck-consistency-lock.md §Deck System Contract + Batch Prompt Block | Verbatim reuse per slide |
| Contact sheet QA report | deck-consistency-lock.md §Contact-Sheet Consistency QA | Failure-label taxonomy |
| Packaging acceptance test | image-only-output-contract.md | Image-pipeline only |

### 3.2 Governance locks (SKILL.md §Visual Governance Locks — declared "core skill, not optional") [DIRECT]

1. **Style Master Lock** — any approved sample/reference becomes the "full-page rhythm" master (title scale/placement, subtitle weight/proximity, proof-object dominance, evidence-band structure, bottom-takeaway treatment, density, typography mood, motifs). Conflicts require stating the tradeoff.
2. **Deck Consistency Lock** — deck-system elements locked; page-local proof-object elements explicitly *not* locked.
3. **Message Hierarchy Lock** — one governing message, one highest-priority conclusion zone, one action title, ≤1 bottom takeaway, numbers anchored to proof object, low-weight source notes.
4. **Claim-Evidence-Visual Lock** — evidence mapped to exact claim *before* design; connectors are semantic claims.
5. **Density Preservation Lock** — density is part of the style system for standalone decks; sparse-but-clean = density *failure*, not success.
6. **Prompt Shape Lock** — fixed priority order: action title → subtitle → proof object → evidence anchors → takeaway → source note.
7. **Sample Rejection Lock** — enumerated rejection conditions (see §5).

### 3.3 Gates & checklists [DIRECT]

- **Alignment Gate:** three non-collapsible approvals (preferences → storyline/blueprint → sample brief); self-check: "if the user could reasonably ask 'what story am I approving?', the handoff failed."
- **Slide Brief Gate** (concept-image-director.md): 8 checks — clear claim, named proof object, evidence boundary, must-keep 3–6, claim-evidence mapping, visual guardrails, distinct layers, avoid list.
- **Pre-Prompt Checklist** (message-hierarchy-rules.md): 7 questions (governing message; one proof object; attached numbers; one takeaway; quiet source note; deck-policy compliance; omission plan).
- **Anti-Slop Gate** (SKILL.md, end): any preserved rule must contain ≥1 of {trigger condition, acceptance test, good/bad example, non-negotiable constraint, stop condition} — i.e., the repo polices its own rule quality.

---

## 4. Proof-object selection logic

### 4.1 Operative decision machinery (enforced by gates) [DIRECT]

**Picker A — by business question type** (`references/concept-image-director.md` §Proof Object Picker; invoked mandatorily by SKILL.md §Workflow 5.5: *"Use the proof-object picker in references/concept-image-director.md"*):

| Claim/question type | Strong proof object | Avoid |
|---|---|---|
| Price/monetization architecture | layered price ladder, route split, value staircase + judgment rail | vendor cards with scattered prices |
| Player landscape | route map, ecosystem stack, battlefield map | logo grid, ordinary comparison table |
| Player control points | control-point map, layered ecosystem, value-chain ownership map | forced 2x2 mixing unlike assets (IP vs trust vs channel) |
| Demand validation | validation funnel, three-gate test, pain-frequency-willingness map, adoption-friction stack | abstract "real demand" arrows |
| Product architecture | layered stack, control-point map, workflow runtime map, system boundary diagram | generic feature cards |
| Competitive wedge | entry wedge map, chain-control map, before/after operating model, maturity ladder | equal-weight process-arrow boxes |
| Failure analysis | failure-condition matrix, then-vs-now map, risk-carryover bridge | icon list of reasons |
| Future winners | capability stack, winning-formula map, thresholded 2x2 | vague trend cards |
| Portfolio/assortment | common-core decomposition, overlap fingerprint, ranked concentration map | large example tables |

**Picker B — by evidence relationship** (`references/message-proof-mapping.md` §Proof Object Selection; invoked whenever a page has players/metrics/risks/gates/validation claims): control-point map for multi-role competition; *observed-signal list → compact mechanism → validation checklist* for "speed observed, trust pending"; evidence strips for route-difference facts; funnel/gate with metrics **inside** stages; audit checklist / neutral gate for unverified risks.

**Hard axioms layered on both pickers:**
- **2x2 fairness axiom:** a 2x2 is legal only if both dimensions fairly apply to every plotted item; otherwise escalate to control-point/ecosystem map. [DIRECT, both files]
- **Split-structure rule:** observed activity vs unproven requirements must be visually separated, never merged into one dominant object (e.g., no flywheel implying solved trust). [DIRECT]
- **Anti-default rule:** "cards", "comparison table", "three columns", "process arrows" may not serve as the main visual *unless the structure genuinely is the proof object*; prefer overlap / decomposition / contrast / concentration / sequence / decision-logic carriers (SKILL.md §Proof Object Rules). [DIRECT]
- **Primacy rule:** proof object must be recognizable before supporting labels. [DIRECT]
- **Number-attachment rule:** large numbers only inside/on the proof object; detached KPI rails are a rejection condition. [DIRECT]

### 4.2 Operative vs descriptive classification [INF]

- **Operative (gate-enforced, prompt-blocking):** Pickers A/B, the four axioms above, the semantic-guardrail vocabulary (line=supports/feeds; gate=must-pass-before-next; checkmark=verified; flywheel=reinforcing mechanism; ring=contains-controls; 2x2=comparable-dimensions), and the hard stops in §Workflow 5.5.
- **Descriptive (calibration material, not gate-enforced):** the five "Reusable Good Patterns" in concept-image-director.md (layered price ladder, route split map, decision matrix + path, decomposition/common-core, **demand validation funnel** with six named gates: pain frequency → alternative inadequacy → willingness to pay → daily-use feasibility → trust/privacy acceptance → ecosystem closure) and all case narratives in example-lessons.md, which carry explicit "Do not overgeneralize" caveats. These seed judgment; nothing in the pipeline *requires* consulting them, whereas the pickers and hard stops are wired into the workflow by name.

[REC] When porting: promote the demand-validation funnel's six gates from descriptive pattern into the QueueZero Validation/Traction reasoning manifest — they are the most concrete auditable checklist in the corpus.

---

## 5. Sample approval loop and Deck System Contract formation

### 5.1 Loop [DIRECT]

1. Generate 1–2 samples chosen to *test the deck*: cover/opening thesis + highest-evidence-load body page; standalone mode must include a density test.
2. Inspect against hard visual floor + rejection rubric **before** showing the user: *"Do not ask the user to approve a weak sample"* (sample-rejection-rubric.md, opening line).
3. Failures are **named precisely** from a fixed vocabulary (≈21-row reject table + labels such as `weak proof object`, `evidence misattribution`, `false precision chart`, `linework overload`, `multiple conclusion zones`, `sparse concept poster`).
4. **Regeneration Rule:** revise around a *changed brief*, never cosmetic tweaks — the rubric gives an explicit bad-fix vs good-fix pair ("Make it cleaner and more premium" ✗ vs "Keep the six-gate proof object as the only visual protagonist. Move 27% and 91% into the evidence band…" ✓).
5. Diagnose in a fixed 12-step order: proof object visibility → evidence attribution → player readability → hierarchy → competing modules → metric placement → bottom area → density fit → color/linework → deck consistency → bottom synthesis → text fidelity.
6. Only then: user approves.

### 5.2 What the approval does and does not convey [DIRECT — key subtlety]

*"Sample approval preserves the proof-object direction and quality bar; it does not automatically approve missing or drifting deck-system elements."*

### 5.3 Deck System Contract [DIRECT]

Authored after approval, before batch prompts, from approved sample + user feedback. Locks **only**:

1. Page-marker system (exactly one of: none everywhere / plain text `01 / 06` / compact badge — never mixed);
2. Action-title scale, weight, top alignment, block width (wrap within width, never dramatic shrink);
3. Subtitle position/weight relative to title;
4. Top-left motif/accent;
5. Source-note style (same bottom position, tiny gray weight);
6. **Bottom-synthesis policy** — a deck-level tri-state: none anywhere / light synthesis on every slide / named judgment slides only;
7. Material treatment (flat 2D / subtle depth / 3D) — chosen once.

Explicitly **excluded** from the contract: page-local icons, diagrams, badges, chips, proof-object motifs — these *should* vary when page logic requires.

**Overcorrection guards** (notable systems thinking): banning all takeaways because one sample had duplicate conclusions is itself a named failure (`overcorrected no-takeaway`); likewise `duplicate bottom conclusion` and `bottom-synthesis drift`. Batch QA runs on a contact sheet at thumbnail scale against a 10-point checklist, then affected slides regenerate before packaging.

---

## 6. Renderer-agnostic reusable principles (port to Slide IR)

All [DIRECT] observations of the rule; [REC] framing of the port.

1. **Claim-first pages:** every page governed by one complete-sentence judgment; titles are conclusions (blueprint rule).
2. **Four-state evidence boundary:** `{confirmed facts, assumptions, inference, open uncertainties}` — a ready-made provenance enum for IR.
3. **Bidirectional claim-evidence mapping:** "Evidence supports: X → proves ⟨specific sub-claim⟩" *plus* "Evidence does not prove: Y ↛ ⟨unsupported conclusion⟩" (message-proof-mapping.md template). Negative mapping is the rarest and most valuable idea here.
4. **Proven-vs-pending category lists:** observed = financing, shipments, price tests, IP partnerships, product routes, channel launches, public user behavior; pending = safety, compliance, retention, repeat purchase, subscription renewal, unit economics, channel complaints, recall response. Directly machine-checkable.
5. **Connector semantics:** every line/arrow/gate/check/ring/color-status is a proposition with truth conditions; guardrails enumerate forbidden implications per page.
6. **Layered message jobs with failure modes:** the message-hierarchy-rules.md table (layer / job / failure mode) is effectively a typed schema for text slots.
7. **Invariants:** one conclusion zone; one action title; one main proof object; ≤1 takeaway; takeaway weight > source-note weight (strict visual ordering).
8. **Must-keep + omit-list pairing:** explicit positive text contract (3–6 anchors) *and* explicit negative scope per page — ideal IR fields.
9. **Two-tier consistency:** deck-system invariants (7 fields) frozen; page-local variation axes free. This is exactly a global-style-token vs per-slide-override split.
10. **Bottom-synthesis tri-state policy** recorded once at deck level.
11. **Delivery-mode parameterization:** live vs standalone changes density targets, body-copy presence, QA criteria — a clean mode enum.
12. **Named-failure diagnostics:** fixed-order diagnostic sequence + failure-label vocabulary → directly implementable as ordered lint/assertion passes.
13. **Fix-cause-not-symptom regeneration rule** — process discipline worth keeping in any iteration loop.
14. **Rule-hygiene gate (Anti-Slop)** — meta-principle for maintaining the rule library itself.

---

## 7. Image-first-coupled mechanisms — do NOT carry forward

| Mechanism | Source | Why it must not transfer |
|---|---|---|
| Generation Backend Lock + hard stop ("if no image backend, stop after prompts"; forbidden fallback list HTML/CSS/SVG/Pillow/…) | SKILL.md §Routing/Backend Lock; image-only-output-contract.md | Pure image-route plumbing; inverted for a deterministic renderer |
| "Manage intent, not coordinates"; forbid x/y positions in prompts | SKILL.md §Core Principle; concept-image-director.md §Prompt Discipline | Correct *for diffusion models*; a deterministic renderer needs the opposite — precise geometry. Keep the semantic layers above the geometry, discard the compositional-freedom doctrine |
| Visual mother concept as diffusion-composition aid | throughout | Function is to help an image model invent a memorable composition; at most retain as an optional `metaphor_hint` string |
| Text-fidelity mitigations (shorter chunks because models garble text; fake-text inspection) | SKILL.md §Workflow 6; image-only-output-contract.md §Text Density | Irrelevant if renderer draws text deterministically; keep only the *density governance* motive |
| Contact sheets, PNG visual inspection, `slidesWithEditableText = 0`, packaging acceptance test, `scripts/package_image_deck.py` | SKILL.md; image-only-output-contract.md | Image-pipeline QA/packaging |
| Style-master extraction by inspecting reference *images* (trait sniffing) | visual-style-master.md | Replaced by explicit style tokens; however its trait list (what counts as "page rhythm") is an excellent token inventory — port the list, not the sniffing |
| "Editable-PPT screenshot feel" / "generic dashboard" aesthetic rejections calibrated against image-model failure modes | rubric | Partially aesthetic-image-era; the underlying principle (structure must carry the claim) survives |

**Nuance worth recording for the architect:** the Prompt Shape Lock's complaint about "flat equally-weighted field lists" is really a claim about *attachment semantics* (anchors bind to the proof object) and *weight ordering* (title > subtitle > anchors > takeaway > note) — both survive as pure IR constraints even though the "don't feed the model a flat list" rationale dies with the image model.

---

## 8. Recommended minimal reasoning manifest for QueueZero Stage 3

[REC] One JSON/YAML document per deck; fields mapped to their RW provenance so the architect can audit lineage.

```yaml
deck:
  core_question: string            # SKILL.md Inputs schema
  working_thesis: string           # ditto
  storyline: [string]              # ordered logic steps
  audience: string
  delivery_mode: live|standalone   # SKILL.md §Delivery Mode Choice
  language: string
  style_tokens:                    # replaces image "style master"
    palette_roles: {base, anchor, accent, risk}
    density_target: concise|standard|dense
    material: flat|subtle_depth|3d
  deck_system_contract:            # deck-consistency-lock.md 7 fields
    page_marker: none|text|badge
    title_system: {scale, weight, align, wrap_width}
    subtitle_system: {position, weight}
    motif_system: none|<spec>
    source_note_system: <spec>
    bottom_synthesis_policy: none|every|named_slides[:ids]
    material_treatment: <token>
  failure_vocabulary: [...]        # deck-consistency-lock.md labels, for QA reports

slides:
  - id: string
    role: hook|mechanism|evidence|comparison|decision|roadmap|closing
    claim: string                  # complete-sentence judgment == action title
    subtitle: string|null          # WHY the claim holds; never restates claim
    evidence_boundary:             # 4-state enum
      confirmed: [...]
      assumptions: [...]
      inference: [...]
      open_questions: [...]
    claim_evidence_map:
      supports:      [{anchor: id, proves: subclaim, strength: confirmed|directional}]
      does_not_prove:[{anchor: id, unsupported_conclusion: string}]
      pending:       [string]       # proven-vs-pending split
    proof_object:
      type: route_map|ladder|funnel|matrix|stack|decomposition|
            timeline|control_point_map|validation_checklist|comparison|...
      rationale: string             # why this carrier fits THIS claim
      anchors:                      # must-keep, 3–6 (dense mode may exceed)
        - {id, text, attaches_to: <proof_object part>}
    takeaway: string|null           # ≤1; obeys deck bottom_synthesis_policy
    source_note: string|null        # always lower weight than takeaway
    omit_list: [string]
    visual_guardrails: [string]     # forbidden connector implications
    metaphor_hint: string|null      # OPTIONAL residue of "visual mother concept"
```

**Validator mappings (RW gate → automated lint/post-render assertion):**

| RW gate | Port |
|---|---|
| Pre-prompt checklist (7 Qs) | manifest completeness linter |
| Slide Brief Gate (8 checks) | manifest schema validation |
| "one conclusion zone / one title" | render assertion: exactly one title-class element |
| number-attachment rule | geometric assertion: numeric elements intersect proof-object bbox |
| takeaway weight > source note | style assertion on font size/weight tokens |
| 2x2 fairness axiom | proof_object.type + plotted-role metadata check |
| proven-vs-pending | no `check/pass` glyph on any `pending` item — enforceable in a deterministic renderer |
| deck contract conformance | cross-slide token diff |

---

## 9. Application to the three QueueZero benchmark slides

Structural recipes only; QueueZero-specific evidence must come from upstream content (clean-room: mechanism → principle → relevance, no copying of RW cases). QueueZero content assumed to concern queue elimination/waiting-cost; correct me if the product domain differs.

### 9.1 Problem/Hook
- **RW mapping:** opening thesis → Hero Concept Exhibit *selectively*, or Clear Report if standalone-dense (SKILL.md §Visual Mode Selection).
- **Claim type:** strategic judgment about pain/cost → Picker A row "Demand validation" (friction/adoption stack) or "Failure analysis" (then-vs-now condition map) depending on framing.
- **Reasoning artifacts to freeze upstream:** one-sentence hook claim; 3–6 anchors quantifying the problem; explicit pending list (any claimed pain frequency/cost that is directional rather than measured goes in `does_not_prove`/`pending`).
- **Guardrail:** hook must not visually pre-prove the solution works (split-structure rule applied forward).

### 9.2 How It Works
- **RW mapping:** Evidence Architecture Exhibit — "the structure carries the argument before the labels do".
- **Claim type:** product architecture/mechanism → Picker A "Product architecture": layered stack, workflow runtime map, system-boundary diagram; decomposition if common-core vs variant.
- **Semantics:** every arrow is "feeds/supports/belongs" — declare each in `visual_guardrails`; stage metrics attach inside stages (metric-placement rule).
- **Guardrail:** no implied outcome proof (a mechanism diagram must not assert throughput/quality numbers that live elsewhere in evidence).

### 9.3 Validation/Traction
- **RW mapping:** this is the exact regime message-proof-mapping.md was written for; apply it wholesale.
- **Split structure mandated:** observed signals (pilots, deployments, usage, revenue, price tests — adapt RW's observed list) rendered as evidence strips; pending items (retention, unit economics, reliability-at-scale) rendered as a neutral validation checklist/gates, **never** green checkmarks or passed-gate glyphs.
- **Customer/player examples:** readable evidence sentences, not logo/name tags (the Haivivi/FoloToy weak-vs-strong pattern).
- **Proof object:** validation funnel or gate sequence with metrics *inside* stages; consider the six-gate demand-validation funnel if traction = demand proof.
- **Reject triggers to encode:** `evidence misattribution`, `label-only player evidence`, `false precision chart`.

**Cross-slide:** identical deck_system_contract; one bottom-synthesis policy (for a 3-slide benchmark, `named_slides` = likely Validation only, decided once); uniform markers/title scale; density per delivery_mode.

---

## 10. Brittleness / contradiction / hidden-assumption analysis

1. **Triple duplication of the rejection rules** (SKILL.md §7.5 + Sample Rejection Lock; sample-rejection-rubric.md; concept-image-director.md §Sample Rejection Gate) with wording drift — e.g., deck-level rows (`title scale drift`, `inconsistent page marker`, `bottom-synthesis drift`) appear in the rubric but not in SKILL.md's inline lock. Long-term divergence risk; port from the rubric as the superset. [DIRECT comparison]
2. **Numeric bound inconsistency:** must-keep "3-6 items" (SKILL.md §Workflow 5, concept-image-director.md Slide Brief Gate) vs "3-8 evidence labels or numbers" (Mode B typical must-keep); concept-image-director.md adds an unstated escape hatch ("unless the user explicitly chose a dense report page"). An automated validator needs one reconciled bound. [DIRECT]
3. **Human-in-the-loop assumption:** three hard conversational gates, visible-handoff requirements, "wait for user confirmation" — unexecutable in a batch benchmark. Translation needed: gates → artifact-completeness validations, not pauses. [INF]
4. **Schema drift between the two slide-brief listings** (SKILL.md §Workflow 5 vs consulting-image-context.md §Slide Brief Schema — field sets nearly but not fully identical, e.g., output-mode field present only in the latter). Pick one canon. [DIRECT]
5. **Tool-name leakage:** "Codex inferences" hardcoded in the provenance enum (SKILL.md §Normalize; consulting-image-context.md; image-only-output-contract.md) — an operator-specific term baked into the portable layer; generalize to `agent_inference`. [DIRECT]
6. **Coordinate doctrine tension:** SKILL.md §Core Principle forbids managing exact coordinates, while deck-consistency-lock.md §Deck System Contract specifies "title x/y position, title width". Internally resolvable (system frame locked, content area free) but stated nowhere as a reconciliation. [DIRECT]
7. **Sanitization inconsistency:** message-proof-mapping.md uses real-looking names (Haivivi, FoloToy, Ropet, Fuzozo) while SKILL.md mandates `[Company A]`-style neutrals and example-lessons.md demands keeping private assets out of the public repo. Either synthetic or a sanitization slip — treat as untrusted exemplar data. [DIRECT observation; classification UNKNOWN]
8. **Encoding artifact:** example-lessons.md contains `璇佹嵁杈界晽` — GBK-misdecoded 证据边界 — indicating an encoding fault in the authoring chain. Any port of the Chinese label vocabulary (证据锚点， 战略含义， 商业启示…) must verify encoding integrity. [DIRECT; decoding INF]
9. **Underspecified "named judgment slides":** the third bottom-synthesis policy depends on a page-role taxonomy that is never formally defined (roles surface only ad hoc: cover/thesis/evidence/comparison/decision/roadmap/closing). QueueZero manifest must define the role enum explicitly. [INF]
10. **Dual diagnostic orders:** rubric's 12-step diagnostic sequence vs SKILL.md Iteration Lessons' 6-step list — compatible but no declared precedence. [DIRECT]
11. **Hidden language assumption:** operational templates and label vocabulary assume a Chinese-literate audience; localization decision required for QueueZero. [DIRECT]
12. **Hidden premise that one governing message per page is always achievable** — handled by split/demote rules, but the *selection* of what to demote is pure judgment with no procedure; expect LLM variance here and compensate with the omit_list being reviewed. [INF]

---

## 11. Unknowns and exact follow-up requests

Per the evidence standard, the following cannot be resolved from the bounded package:

1. **[UNKNOWN] Remaining 85 tracked files.** The package lists 95 tracked / 10 eligible-text files. I did not see the other paths. If any contain *filled examples* of the pipeline artifacts (actual `Inputs for PPT Production`, blueprints, slide briefs, Deck System Contracts), they would materially upgrade this reconstruction from schema-level to instance-level.
 **Request:** supply `git ls-files` output for the repo, or at minimum any `.md` files outside `skills/rw-consulting-ppt/references/`, plus a grep for the symbols `Inputs for PPT Production`, `Deck System Contract`, `visual mother concept` across all tracked files to catch undocumented copies.
2. **[UNKNOWN] `scripts/package_image_deck.py`** — referenced twice (SKILL.md §Generation Backend Lock, §Workflow 8), not supplied. Packaging-only; correctly excluded by task scope. **Request only if** Stage 3 ever needs packaging-parity testing.
3. **[UNKNOWN] Whether "Image2" is a specific internal backend API** — irrelevant to reasoning extraction; noted so nobody chases it.
4. **Dependency on architect decision:** the manifest's `anchors[].attaches_to` and post-render geometric assertions assume the Stage 3 renderer exposes element bounding boxes and deterministic text. Please confirm renderer capability before the manifest schema is frozen.

**Bottom line for the lead:** preserve RW's reasoning spine (claim → typed evidence boundary → bidirectional claim-evidence map → claim-keyed proof object → collapsed hierarchy → two-tier consistency contract → named-failure QA), discard the image-model execution shell, and treat the three approval gates as validation lints rather than conversation points. I am ready to draft the concrete QueueZero manifest instances for the three benchmark slides once the upstream QueueZero evidence inventory is provided.