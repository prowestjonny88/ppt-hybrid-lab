# Task-006 Report — PPT Master as External Stage 3 SVG→DrawingML Experiment Adapter

Repo: `hugohe3/ppt-master` @ `65bb2eca59a36270819caba377097910c4466c6e`.
Evidence tags: **[DIRECT]** (read in supplied source), **[INFER]** (derived), **[REC]** (my recommendation), **[UNKNOWN/NEEDS SOURCE]**.

---

## 1. Recommended minimal adapter sequence

**[REC]** Drive the pinned converter as a **subprocess CLI** inside a disposable scaffold — not as an imported library. Sequence for `src/svg_lane/ppt_master_adapter.py`:

1. Pin upstream: checkout `hugohe3/ppt-master` at `65bb2eca…` into a CI cache dir (never mutate; run in place so `require_skill_integrity()` sees pristine files — see §3).
2. Materialize scaffold:
   ```
   <workspace>/
     svg_output/queuezero_hiw.svg        # sole authored input (§8 grammar)
     validation/                          # empty; filled by checker + exporter
   ```
3. Run quality gate (**mandatory even in lockless mode**, §2):
   ```
   python3 skills/ppt-master/scripts/svg_quality_checker.py "<workspace>" --quick-generate --stage final --json
   ```
   Assert exit 0 and that `<workspace>/validation/svg_quality_report.json` exists with `schema=ppt-master.svg-quality-report.v1`, `stage=final`, `categories.blocking.count=0`, and `source_fingerprint` matching the SVG bytes.
4. Export:
   ```
   python3 skills/ppt-master/scripts/svg_to_pptx/pptx_package/cli.py \
     "<workspace>" --quick-generate --no-animations -o <workspace>/out.pptx \
     --conversion-trace trace.json -q
   ```
   Explicit `-o` suppresses the `backup/<ts>/` snapshot and the timestamped filename **[DIRECT: cli.py — `if args.output: native_path = Path(args.output)` … else backup branch]**.
5. Consume artifacts: `out.pptx`, `trace.json`, `validation/out.report.json` (auto-postflight). Adopt the produced slide per §7, then validate per §10.

Why `--quick-generate`: it is the only route that needs **no** `spec_lock.md`, **no** theme contract, **no** notes, and forces `pptx_structure='flat'` **[DIRECT: cli.py — `args.pptx_structure = 'flat'`; `if not args.with_notes: args.no_notes = True`; conflict guard rejects `-s` and `--pptx-structure` overrides]**.

---

## 2. Exact entry points and call chain

### CLI (recommended)

**[DIRECT]** `skills/ppt-master/scripts/svg_to_pptx/pptx_package/cli.py`, `def main(argv: list[str] | None = None) -> int`, executable directly (`if __name__ == '__main__': raise SystemExit(main())`; the module self-bootstraps its package via the `__package__ in {None,''}` shim). Relevant arguments verified in the argparse block: positional `project_path`; `-o/--output`; `-f/--format`; `--quick-generate`; `--no-animations`; `--no-notes`; `--conversion-trace [PATH]` (`nargs='?'`, default path `<project>/validation/<output_stem>.trace.json`); `--reflow-text/--no-merge` (default `TEXT_FLOW_PRESERVE`).

Internal chain **[DIRECT]**: `main()` → `require_skill_integrity()` (first statement) → gate checks → `find_svg_files(project_path, 'output', …)` (module `discovery.py`) → quality-gate fingerprint compare → `create_pptx_with_native_svg(...)` → `_write_postflight_report(...)`.

### Library

**[DIRECT]** `skills/ppt-master/scripts/svg_to_pptx/pptx_package/builder.py` exports `create_pptx_with_native_svg`. Its exact call is fixed by cli.py:

```python
success = create_pptx_with_native_svg(
    output_path=native_path,
    use_native_shapes=True,
    svg_files=native_files,
    conversion_trace_path=conversion_trace_path,
    **shared_kwargs,   # ~40 kwargs: canvas_format, expected_viewbox, transition,
                       # animation_*, notes, enable_notes, text_flow, pptx_structure,
                       # theme_font_spec, master_text_style_spec, theme_color_spec,
                       # primary_language, image_*, native_objects, …
)
```

**[REC]** Do **not** call the library form in the adapter: the builder's full signature is not in the supplied context (file truncated before the `def`), and cli.py provably pre-validates theme/lock contracts that the builder may assume. Subprocess + CLI keeps the contract enforced by the repo's own front door.

Lower-level `convert_svg_to_slide_shapes` (`drawingml/converter.py`, imported in builder.py line `from ..drawingml.converter import convert_svg_to_slide_shapes`) exists, but its signature, return contract, and trace format are **[UNKNOWN/NEEDS SOURCE]** — see §11. Do not target it yet.

### Hard gates on the default path (why the recipe looks like this)

All **[DIRECT]** from `cli.py::main`:

| Gate | Trigger | Bypass |
|---|---|---|
| `spec_lock.md` must exist | any non-quick run | `--quick-generate` |
| `canvas.viewBox` in lock | non-quick run (`Error: spec_lock.md must contain canvas.viewBox…`) | `--quick-generate` |
| theme contract (`typography font_family/title_family/body_family`, `colors`) | `pptx_structure ∈ {flat,structured}` non-quick | `--quick-generate` |
| final quality report w/ matching sha256 fingerprint | `release_quality_gate = args.quick_generate or args.source in {None,'output'}` — **true for quick too** | only `-s <custom>` (which then requires spec_lock again) |

The quality gate compares `_svg_source_fingerprint` (per-file SHA-256 + aggregate) against `validation/svg_quality_report.json`; mismatch ⇒ `stale` ⇒ exit 1. **Consequence:** the checker must be re-run whenever the SVG changes; the SVG must be frozen before export.

Post-flight is not optional **[DIRECT]**: `_write_postflight_report` re-opens the ZIP, verifies integrity, and raises `PptxPostflightValidationError` (exit 1, "must not be used") if `slides != len(svg_files)` — free package validation for the adapter.

---

## 3. Mandatory vs optional dependencies (Ubuntu runner)

**Mandatory:**
- Python ≥ 3.10 **[DIRECT: README Quick Start]**.
- `python-pptx` — **[DIRECT: builder.py `from pptx import Presentation`; `from pptx.util import Emu`]**
- The repo's sibling modules imported unconditionally by cli.py/builder.py: `attribution_guard` (`require_skill_integrity`), `console_encoding`, `language_tags`, `native_payloads`, `pptx_animations`, `pptx_transitions`, `pptx_opc_validation`, `hyperlink_contract`, `config`, `project_utils`, `update_spec`, `svg_quality_checker`, plus package internals (`svg_to_pptx.drawingml.*`, `.native_objects`, `.animation_config`, `.semantic_markers`, `canvas_contract`). All resolved via `sys.path.insert(0, scripts_dir)` **[DIRECT: cli.py `_SCRIPTS_DIR = Path(__file__).resolve().parents[1]`]**. They ship with the pinned checkout; several are not in the supplied inventory, so their own third-party imports are **[UNKNOWN]** — `requirements.txt` is not in the inventory and was not supplied (§11).
- `require_skill_integrity()` runs unconditionally as the first statement of `main()` **[DIRECT]**; its mechanics (what it hashes, whether partial vendoring breaks it) are **[UNKNOWN]** until `attribution_guard.py` is fetched. **[REC]** treat "run from an intact pinned clone" as a hard invariant; do not cherry-pick files into a thinner tree until this is verified.

**Conditionally needed / safely avoided on our constrained route:**
- `ffprobe/ffmpeg` — only `probe_audio_duration` (narration) shells out **[DIRECT: narration.py]**; omit narration flags ⇒ not needed.
- `pandoc` — document ingestion only, unrelated to the converter **[DIRECT: README edge-case fallback]**.
- Raster/PNG renderer (`media.py`: `PNG_RENDERER`, `convert_svg_to_png*`) — imported by builder unconditionally, but exercised only for rasterized content/images. Whether `PNG_RENDERER` initializes eagerly at import is **[UNKNOWN/NEEDS SOURCE: pptx_package/media.py]**. Our grammar (§8) aims for zero rasterization; still budget one CI apt package for the renderer if media.py proves eager.
- Optional features to disable explicitly: transitions/animations (`--no-animations`), notes (default-off in quick mode), narration (omit), native Chart/Table replacement (omit `--native-charts-and-tables`), structured/template machinery (omit `--pptx-structure structured`).

---

## 4. Minimum project/directory scaffold

**Standalone SVG without a project:** `create_pptx_with_native_svg(svg_files=[one.svg], …)` plausibly accepts a lone file — `dimensions.resolve_svg_canvas` with `expected_viewbox=None` derives the canvas from the first SVG and merely requires consistency across files **[DIRECT: dimensions.py]** — but whether the flat path tolerates `theme_*_spec=None` (cli.py always supplies them for flat) is unverifiable from the truncated builder **[UNKNOWN]**.

**[REC] Minimum scaffold for the CLI route (proven surface):**

```
<workspace>/svg_output/queuezero_hiw.svg          # authored
<workspace>/validation/svg_quality_report.json    # generated by checker (step 3)
```

Nothing else. No `spec_lock.md`, no `notes/`, no `metadata.json`, no `animations.json`, no theme files — all either skipped or default-empty under `--quick-generate` **[DIRECT: cli.py]**. Workspace must be writable (exports/validation reports land inside it).

Release-flat alternative (rejected for the experiment, kept for record): add `spec_lock.md` with `canvas.viewBox: 0 0 1280 720`, `pptx_structure.mode: flat`, a `colors` section, and `typography.font_family/title_family/body_family` **[DIRECT: the cli.py error string enumerates exactly these]** — but the precise YAML/markdown schema of the lock is defined in `update_spec.parse_lock` / `theme_fonts.load_theme_font_spec` / `theme_colors.load_theme_color_spec`, none supplied ⇒ **[NEEDS SOURCE]** if Mode 2 is ever wanted.

---

## 5. Canvas/viewBox contract (1280×720 landing)

**[DIRECT] `dimensions.py`:**
- Fallback registry: `CANVAS_FORMATS = {'ppt169': {'name': 'PPT 16:9', 'dimensions': '1280×720', 'viewbox': '0 0 1280 720'}}`.
- `EMU_PER_PIXEL = 914400 / 96 = 9525`; `get_slide_dimensions` multiplies px × 9525.
- `resolve_svg_canvas(...)` is fail-closed: all SVGs must share one canonical viewBox; a locked/format viewBox must match exactly.

Contract for the adapter:
- Author the SVG with `viewBox="0 0 1280 720"` (and matching `width="1280" height="720"` — strictness of `read_project_viewbox` on width/height attributes is **[NEEDS SOURCE: canvas_contract.py]**; supplying both is the safe superset).
- Slide becomes 1280×9525 = **12,192,000 × 6,858,000 EMU** (13.333″ × 7.5″), the standard 16:9 — identical to a default python-pptx 16:9 deck, so diagram-region EMUs transfer 1:1 with no post-scaling.
- SVG user units map linearly: 1 unit = 9525 EMU, origin top-left, y-down in both systems. Example: a node rect at `(x=200,y=160,w=240,h=96)` lands at `a:off 1905000,1524000` / `a:ext 2286000,914400`.
- Because the diagram is the *entire* slide content, reserve margins inside the 1280×720 box; our hybrid assembler positions nothing — geometry is baked by the converter.

---

## 6. Trace and semantic identity mapping

**Obtain it via the CLI — yes, it propagates. [DIRECT]**

- cli.py: `--conversion-trace` resolves to `<project>/validation/<output_stem>.trace.json` (or an explicit path) and is forwarded: `create_pptx_with_native_svg(..., conversion_trace_path=conversion_trace_path, ...)`.
- builder.py consumes traces structurally; `_trace_native_shape_ids` reveals the on-disk schema:

```python
for event in trace.get("events", []):
    if event.get("decision") != "native": continue
    svg_id = event.get("id"); shape_id = event.get("shape_id")
    result.setdefault(str(svg_id), []).append(str(shape_id))
```

Events additionally carry `data-pptx-role` / `data-pptx-placeholder` (see `_trace_chrome_shape_ids`), and `slide_num` is a top-level key (used by `_template_runtime_slides`). One SVG id may map to **multiple** shape ids (merged/split text lines), hence the list.

- The join `shape_id → p:cNvPr/@id` is the same join the repo itself performs: `_top_level_shapes_by_id(root)` indexes `p:spTree` children by their first `p:cNvPr` id, and `_template_shape_for_item` resolves `state.shape_ids_by_svg_id` against exactly that dict **[DIRECT]**. So: *trace `shape_id` ≡ slide-local `p:cNvPr/@id` of a top-level emitted shape* is the repo's own architectural contract (emitting code unsupplied ⇒ formally **[INFER, high confidence]**).

**Do not** call `convert_svg_to_slide_shapes` directly to chase trace fidelity: the builder is what allocates final shape ids, applies theme/font/color specs, and writes the trace. **[REC]** Adapter post-pass: read `trace.json`, then rewrite each mapped shape's `p:cNvPr/@name` to `qz:<svg_id>` during adoption (§7). Generated names are otherwise generic ("Image 2"-style, per the comment in `_canonical_shape_xml`) **[DIRECT]**, so semantic identity must be stamped by us.

Avoid ids that collide with chrome tokens — `_CHROME_TRACE_TOKENS = (logo, footer, header, watermark, chrome, pagenumber, slidenumber, pagenum, slidenum)` feed `_chrome_token_from_svg_id` **[DIRECT]**. Naming nodes `header_box` etc. invites chrome logic; harmless at 1 slide today, fragile later.

---

## 7. Transplant vs base-slide — decision

**[REC] Adopt the PPT-Master-produced slide as the base slide of our hybrid deck; do not graft individual shapes.**

Concrete reasoning from the supplied code:

*What a generated slide-local shape may legally reference* — `_shape_relationships_supported` whitelists exactly three relation kinds: internal `image`, external `hyperlink`, internal `slide` **[DIRECT: builder.py `_REL_ATTRS` + `_shape_relationships_supported`]**. With our vector-only grammar (§8) none should occur, but the *possibility class* is what transplant must defend against, plus:

| Hazard | Transplant | Base-slide adoption |
|---|---|---|
| `r:embed`/`r:link`/`r:id` remap into our package | manual re-relate each occurrence (image part copy, external hyperlink re-registration) | unnecessary — rels file travels with the slide |
| `p:cNvPr/@id` collisions with our shapes | must renumber (repo precedent exists: `_renumber_shape_ids`, `_next_master_shape_id` — reuse the *pattern*, not the code) | only our appended shapes need ids > max |
| layout/master/theme coupling | shapes may carry `schemeClr`/`+mj-lt` fonts resolving against *their* theme (flat export applies `ThemeColorSpec`/`ThemeFontSpec`; `_set_placeholder_theme_font_role` shows `+mj/+mn` usage) — silent recolor/remodel in our theme | one relationship rewrite: point the slide's `slideLayout` rel at our Blank layout (mechanic proven in-repo: `_set_slide_layout_target`) |
| `p:timing` spTgt references, `p:bg` | must be stripped/scanned | stripped once, defensively |
| namespace/spine integrity of our assembler | lxml splice into foreign `p:spTree` | none — we append via python-pptx afterwards |

Adoption procedure **[REC]**: extract `ppt/slides/slide1.xml` + its `_rels/slide1.xml.rels` from `out.pptx`; delete every relationship except the layout rel; retarget layout rel to our layout part; drop any `p:timing`/`p:transition` children; register the part in `[Content_Types].xml` and `presentation.xml`/rels per our assembler's normal slide-add path; stamp `cNvPr/@name=qz:<svg_id>` using `trace.json`; then append our native title/screenshot/source objects with ordinary python-pptx APIs.

If the lead prefers transplant anyway, the mandatory remaps are: (1) scan copied nodes for the three `_REL_ATTRS` qualified attributes and rebuild each as a real relationship in *our* slide part; (2) renumber all `cNvPr` ids from `max_existing+1`; (3) diff `schemeClr` usage against our theme accents; (4) reject any `mc:AlternateContent` / `p:pic` outright (means rasterization happened → fail the build).

---

## 8. Safe QueueZero SVG subset (zero rasterization, editable text)

Grounding: the repo's own signals — text-flow modes exist precisely to turn positioned SVG text into editable frames (`--reflow-text`: "reflow conservative dy-stacked text inside one editable text frame"; `--no-merge`: "every positioned visual line as its own text frame") **[DIRECT: cli.py help strings]**; group rotation/flip is rejected during structural unwrap (`_flatten_group_transform`: "unsupported group rotation or flip") **[DIRECT]**; `_source_resource_audit` treats `<image href>` and font stacks as the portability-sensitive surface **[DIRECT: cli.py]**.

**[REC] Use only:** `<svg viewBox="0 0 1280 720">` · `<g id="…">` (nesting ≤ 2, no transform) · `<rect>` · `<line>` · `<path>` (absolute `M/L/C/Q/Z`, no arcs, no `A`) · `<polygon>` (arrowheads) · `<circle>/<ellipse>` if needed · `<text>` with `x, y, font-family="Arial", font-size, fill, font-weight` — **one `<text>` per label, single line, no `<tspan>` stacking, no `text-anchor` dependence until validated**.

**Avoid:** `<image>` (⇒ `p:pic` + rels + renderer), `marker-*` (draw arrowheads as polygons), `transform=` anywhere (bake coordinates), `filter/mask/clipPath/pattern/use/symbol`, gradients (converter support unverified), CSS classes/stylesheets (presentation attributes only), `data-pptx-*` attributes (reserved semantics: role/placeholder/replace-with **[DIRECT: builder/cli usage]**), and any feature that would trip the checker's blocking categories.

Every visual node gets a stable `id="qz-node-ingest"` style identifier → guaranteed trace row (§6).

---

## 9. Adapter validation checklist

Run in CI after step 4; all assertions hard-fail the job:

1. **Gate artifacts**: `svg_quality_report.json` has `stage=final`, `blocking.count=0`, `source_match` digest equals locally recomputed `_svg_source_fingerprint` equivalent (sha256 of file bytes).
2. **Postflight**: `validation/out.report.json` `status ∈ {passed}` (warnings acceptable), `checks.zip_integrity=passed`, `package.slides=1`.
3. **No raster**: unzip `out.pptx`, parse `ppt/slides/slide1.xml`: zero `p:pic`, zero `a:blip`, zero occurrences of `r:embed|r:link|r:id` (byte regex), zero `mc:AlternateContent`.
4. **Editable text**: ≥ N `p:sp` with non-empty `a:t` runs equal to authored label count; no text baked into paths (assert `a:t` contents match expected strings exactly).
5. **No motion**: zero `p:timing`, zero `p:transition`.
6. **Traceability**: `trace.json` events all `decision=="native"`; set(`event.id`) ⊇ authored ids; every id maps to exactly one `cNvPr/@id` present in slide1.xml; after renaming, `cNvPr/@name == qz:<id>`.
7. **Relationship census**: `slide1.xml.rels` contains only the (retargeted) layout rel.
8. **Hybrid integrity**: our final PPTX opens via `Presentation(...)`; renamed shapes discoverable; slide size still 12192000×6858000.
9. **Determinism**: rebuild twice; `ppt/slides/slide1.xml` bytes identical (whole-ZIP equality is *not* expected — docProps timestamps vary).
10. *(Optional)* LibreOffice headless render for visual smoke — informational only.

---

## 10. Follow-up source requests (exact paths/symbols)

Required before hardening the adapter beyond v0:

1. `skills/ppt-master/scripts/svg_to_pptx/pptx_package/builder.py` — full `def create_pptx_with_native_svg` (parameter contract, whether flat path tolerates `theme_*_spec=None`, trace-write site, slide-size derivation, when `convert_svg_to_png` can fire for vector-only input).
2. `skills/ppt-master/scripts/svg_to_pptx/drawingml/converter.py` — `convert_svg_to_slide_shapes` signature/return; native-vs-raster feature table; `cNvPr/@name` policy.
3. `skills/ppt-master/scripts/svg_to_pptx/drawingml/utils.py` — `EMU_PER_PX` value (confirm 9525).
4. `skills/ppt-master/scripts/svg_to_pptx/pptx_package/media.py` — `PNG_RENDERER` initialization eagerness + renderer backends.
5. `skills/ppt-master/scripts/attribution_guard.py` — `require_skill_integrity` mechanics (partial-vendor tolerance).
6. Root `requirements.txt` — CI pins (absent from inventory entirely).
7. `skills/ppt-master/scripts/svg_to_pptx/canvas_contract.py` — `ProjectViewBox`/`read_project_viewbox` strictness (width/height attrs, units).
8. `skills/ppt-master/scripts/svg_quality_checker.py` — CLI flags, report write path confirmation, blocking-category list relevant to our subset.
9. `skills/ppt-master/scripts/svg_to_pptx/pptx_package/discovery.py` — `find_svg_files` ordering (moot at 1 file, needed for determinism guarantees later).
10. Only if Mode 2 (release-flat) is ever adopted: `scripts/update_spec.py::parse_lock`, `drawingml/theme_fonts.py::load_theme_font_spec`, `drawingml/theme_colors.py::load_theme_color_spec`, plus one real `examples/*/spec_lock.md`.
11. Reference material: `skills/ppt-master/scripts/docs/svg-pipeline.md` (sanctioned SVG grammar) and one small `examples/*/svg_output/*.svg`.

---

### Bottom line

**[REC]** Pinned-clone + `--quick-generate` CLI + mandatory pre-run of `svg_quality_checker.py --stage final` + `--conversion-trace` + explicit `-o`; consume the produced slide wholesale into our hybrid package (layout-rel retarget + defensive strip), stamp semantic names from the trace, and enforce the §9 checklist. Direct-library and direct-converter integration remain blocked on follow-up items 1–2. Nothing above modifies any repository; all analysis is read-only per my mandate, and canonical architecture decisions rest with you.