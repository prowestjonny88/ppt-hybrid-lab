# Forensic Analysis: PPT Master SVG→DrawingML Pipeline (task-002)

Repo: `hugohe3/ppt-master` @ `65bb2eca59a36270819caba377097910c4466c6e`
Scope caveat: 11 of 54 eligible files were supplied. `drawingml/elements.py` was **truncated mid-text-converter**, and `pptx_package/*`, `native_objects/*`, `utils.py`, `tspan_flattener.py`, `use_expander.py`, `canvas_contract.py`, and both docs were **not** supplied. Claims below are tagged accordingly.

---

## 1. Executive finding

PPT Master is **not a best-effort SVG converter**. It is a *fail-closed compiler* from a deliberately narrowed SVG dialect ("the project grammar") to native, editable DrawingML. There is **no rasterization fallback anywhere in the supplied code** — unsupported constructs abort the conversion with aggregated diagnostics (`converter.py::convert_svg_to_slide_shapes` calls ~22 `_require_project_*` / `collect_unsupported_visuals` gates before any shape is emitted). Editability is engineered in explicitly: preset geometries with live adjustment handles, native text frames (glyph outlining exists only in a separate Shape Boolean tool, `text_outline.py`), native backgrounds, native connector attachments, theme-token binding, and an internal fidelity taxonomy (`exact` / `native-normalized` / `visual-only` in `_geometry_trace_metadata`). For QueueZero Stage 3, a conservative subset (rect/circle/ellipse/line/path/polygon + anchored text + arrow-marker lines + local-use icons + one validated PNG/JPEG) sits entirely inside the proven-native surface.

---

## 2. End-to-end execution trace (DIRECT EVIDENCE unless noted)

Entry point: **`convert_svg_to_slide_shapes()`** in `skills/ppt-master/scripts/svg_to_pptx/drawingml/converter.py`. Returns `(slide_xml, media_files, rel_entries, anim_targets, package_files, content_type_overrides)`.

1. `ET.parse` → root; `_hydrate_native_payloads` → `hydrate_native_payload_refs` (top-level `native_payloads` module — *not supplied*).
2. Root contract: `parse_project_svg_root` / `parse_project_viewbox` (`canvas_contract.py` — *not supplied*).
3. Marker/hyperlink preflight: `_require_native_marker_attributes`, `_require_inline_formula_markers`, `_require_project_hyperlinks` (validates `#slide-N` against `slide_count`).
4. Round-trip integrity lowering: `validate_authored_preset_tree` + `materialize_compact_authored_preset_tree` (`pptx_to_svg.preset_authoring` — *external, not supplied*); `_mark_unchanged_txbody_groups` / `_mark_unchanged_preset_previews` snapshot SHA-256 fingerprints.
5. Geometry materialization: `materialize_inline_geometry_properties` (`geometry_properties.py` — *not supplied*) + `project_geometry_length_errors`.
6. The validation battery: text properties, freeform geometry, stroke styles, opacities, paints, masks, definitions, paint references, line-end markers, gradients, effect status, filters, image aspect ratios, transforms — each aggregating errors (first 8 shown + "+N more").
7. `<use>` expansion: `expand_use_data_icons` + `expand_local_use_references` (`use_expander.py` — *not supplied*); then the battery **re-runs** on injected subtrees.
8. Text metric lowering: `materialize_project_text_metrics` (`text_properties.py`) — relative font sizes / em letter-spacing resolved to canonical decimals.
9. Positional-tspan lowering: `flatten_positional_tspans` (`tspan_flattener.py` — *not supplied*) under `text_flow` policy `preserve|reflow|split` (`context.py::resolve_text_flow`); formula/hyperlink counts re-checked to prove lowering didn't mutate semantics.
10. `resolve_project_font_sizes` + `resolve_project_letter_spacings`; `collect_unsupported_visuals` (hard gate); `collect_defs`; `_build_source_shape_id_map` (reserves imported IDs).
11. `ConvertContext` constructed (`context.py`) — carries translate/scale/full-matrix state, inherited styles, opacity multiplier, media/rel/package accumulators, reserved-vs-claimed-vs-referenced shape-ID sets, trace buffer.
12. Background promotion: `_extract_background_candidate` → first full-canvas rect becomes `p:bg/p:bgPr`.
13. Dispatch loop over root children → `convert_element` → `_CONVERTERS[tag]` (`rect/circle/ellipse/line/path/polygon/polyline/text/image/g/a/svg`); recursion via `convert_g::ctx.child()`; post-check that all connector-referenced shape IDs were claimed (`referenced_shape_ids − claimed_shape_ids` → error).
14. Slide XML assembled inline (`p:sld > p:cSld > [p:bg] p:spTree`), preserving document order (= z-order). Animation timing is *not* emitted here; `anim_targets` is consumed by the package builder (per docstring — `pptx_package/builder.py` not supplied).

---

## 3. SVG feature support matrix

| Feature | Status | Mechanism / evidence |
|---|---|---|
| `rect` (plain) | **NATIVE** | `prstGeom prst="rect"` (`elements.py::convert_rect`) |
| `rect` rx==ry | **NATIVE** | `prstGeom roundRect` + `adj` (draggable handle kept) |
| `rect` rx≠ry | **PARTIAL** | `_build_round_rect_custgeom` cubic arcs; loses adjustment handle (documented trade-off) |
| `circle`/`ellipse` | **NATIVE** | `prstGeom ellipse`; donut arcs → annular-sector `custGeom` (`convert_circle`, `_build_arc_ring_path`) |
| `line` w/ markers | **NATIVE** | `prstGeom prst="line"` + flipH/V so `headEnd/tailEnd` render (`convert_line` — PowerPoint ignores arrow ends on custGeom, per in-code comment) |
| `line` plain | **NATIVE** (custGeom) | visual-equivalent, not a "real" line preset |
| `path` | **NATIVE** (custGeom) | full grammar → absolutized → normalized to M/L/C/Z (`paths.py::normalize_path_commands`: S/Q/T→C, A→cubic via SVG-spec F.6.5, ≤90° segments) |
| `polygon`/`polyline` | **NATIVE** (custGeom) | `convert_polygon/_polyline` |
| `text` | **NATIVE** (closed grammar) | see §4; `convert_text` body truncated — frame emission details UNKNOWN |
| positional `tspan` | **PARTIAL/NATIVE** | pre-flattened into independent `<text>`/hard breaks (`flatten_positional_tspans`) |
| `image` | **NATIVE** (validated) | strict format whitelist + byte validators (`_valid_emf_payload`, WMF checksum, PIL verify); `p:pic` construction truncated → UNKNOWN |
| nested `<svg>` | **UNSUPPORTED** except picture-crop transport | `project_nested_svg_crop_errors`: "Reject nested SVG outside the imported picture-crop transport" |
| `g` | **NATIVE** | `p:grpSp`, bbox union, single-child flatten, pivot-compensated rotation |
| `a` (anchor) | **NATIVE** | `convert_a` → `apply_shape_hyperlink` onto every leaf `cNvPr` (groups excluded deliberately) |
| `use` local / `data-icon` | **NATIVE after expansion** | expanded pre-flight, then converted as primitives |
| linearGradient | **NATIVE** | `gradFill`+`lin ang` (`styles.py::build_gradient_fill`) |
| radialGradient | **PARTIAL** | focus constrained to canonical circle @0.5,0.5 r=0.5, else error |
| pattern fill | **PARTIAL** | round-trip-annotated patterns → `pattFill`; unresolvable → `noFill` (`build_pattern_fill`); whether preflight blocks hand-authored ones UNKNOWN |
| filters | **PARTIAL** | only shadow (feOffset≠0) / glow classified; others blocked (`_require_project_filters`) |
| markers/arrows | **PARTIAL** | 5 presets (triangle/stealth/diamond/oval/arrow) × sm/med/lg; unclassifiable → warning + dropped (`styles.py::_emit_line_end`) |
| clip-path | **PARTIAL** | only where it yields "native picture geometry"; else rejected (`project_clip_path_errors` docstring) |
| mask | **UNSUPPORTED** | hard-rejected: "before native conversion can silently drop them" (`_require_project_masks`) |
| `symbol`, `foreignObject`, `textPath`… | **UNSUPPORTED** | not in `_CONVERTERS`; `collect_unsupported_visuals` aborts |
| `<style>` CSS block | **EFFECTIVELY UNSUPPORTED** | in `_NON_VISUAL_TAGS` → silently skipped; only attributes + inline `style=` inherit |
| group opacity | **PARTIAL** (approximated) | multiplied into descendants; forbidden on active native replacements (error) |
| dasharray >2 values | **PARTIAL** | normalized to first dash/gap pair (`styles.py::build_stroke_xml`) |
| shear / non-orthogonal transforms | **UNSUPPORTED** | `parse_transform` + `validate_dml_shape_matrix` fail closed |
| text-align, line-height, text-transform, white-space, writing-mode, RTL/BiDi… | **UNSUPPORTED** | explicit denylist (`text_properties._UNSUPPORTED_TEXT_PROPERTIES`; `text_outline._UNSUPPORTED_BIDI_CLASSES`) |
| **Rasterization fallback** | **ABSENT** | no rasterizer dependency exists; refusal, not raster |

---

## 4. Text & editability analysis

**Closed grammar (DIRECT):** `text_properties.py` allowlists exactly `font-weight, font-style, text-anchor, letter-spacing, text-decoration` (+`baseline-shift`, `font-family/-size`), with enumerated values (`normal|bold|100–900(+medium/semibold)`; `normal|italic`; `start|middle|end` — anchor barred on `tspan`; `underline/line-through` combos; `super`→baseline 30000, `sub`→−25000). Letter-spacing accepts decimal/px/pt/em and is range-checked against DrawingML `spc` ±400,000 (`drawingml_letter_spacing`). Anything prefixed `font-/text-` outside the registry is rejected ("native PPTX export would ignore it").

**Layout:** three policies (`context.py`): `preserve` (authored breaks = hard breaks in one frame), `reflow` ("lets PowerPoint wrap"), `split` (one frame per line). Width estimation uses per-run serif/all-caps headroom calibrated against **LibreOffice renders** (`_TEXT_WIDTH_HEADROOM_*`, `elements.py`) — an honest empirical-fidelity hack. Alignment derives from `text-anchor` only; `text-align` is banned. Bullets: leading `·•●▪■◆◇◦‣` are promoted to native `buChar` paragraphs with computed `marL/indent` (`_extract_text_bullet`, `_build_bullet_xml`).

**Editability retained (DIRECT):** real character runs (not outlines — `text_outline.py` is exclusively the Shape Boolean operand tool), `rPr@spc`, baseline shifts, theme font tokens (`+mj/+mn` via `theme_font_spec`), BCP-47 `primary_language`, hyperlinks on runs/shapes, stable shape-ID space with connector `stCxn/endCxn` reattachment, semantic names (`data-pptx-shape-name`), page-role→layout mapping (`semantic_markers.PAGE_ROLE_TO_LAYOUT`), and animation grouping on top-level `<g id>`. **Lost/downgraded:** group alpha, banned typography, and anything hitting the `visual-only` fidelity class (e.g., authored freeform custGeom). Round-trip guards: txBody SHA-256 + base64 restore (`_decode_unchanged_txbody`), preset-preview fingerprint enforcement (`_require_unchanged_preset_preview` — *"export stopped to avoid silently discarding the SVG edit"*), custom-geometry hash gating (`_build_preserved_custom_geom`).

---

## 5. Charts / tables / formulas

**Separate native path, not the generic converter (DIRECT):** `data-pptx-replace-with` markers; `formula` is intrinsically enabled, `chart|table` require `native_objects=True` (default **off**, "to preserve SVG output") — `_native_replacement_enabled`. Output is `p:graphicFrame` plus side-car `package_files` (chart XML, embedded workbook) and `[Content_Types]` overrides (return contract). Marker subtrees face stricter transform rules (translate/scale only, rotation zeroed, group opacity forbidden). With the flag off, the marker subtree converts as ordinary vector fallback. Module inventory confirms `chart_xml/chartex/workbook/table/formula_*` exist; their internals were **not supplied** → UNKNOWN detail.

---

## 6. Unsupported-feature behavior

Fail-closed, three tiers (all DIRECT): (1) **preflight aggregation** — each `_require_project_*` collects all errors and raises once with a bounded preview; (2) **dispatch gate** — `collect_unsupported_visuals` aborts on any non-dispatchable visual tag; (3) **per-element wrap** — `convert_element` rethrows any converter exception as `SvgNativeConversionError` with a trace `'error'` event. Known soft spots: degenerate shapes return `None` → counted `skipped` ("empty-or-non-rendering"); unclassifiable markers `print` a warning and drop the arrowhead; `build_pattern_fill` returning `''` degrades to `noFill` (whether preflight intercepts first depends on unsupplied `utils.py`).

## 7. Validation / QA

Pre-conversion: the ~22-gate battery above + fingerprint snapshots + connector-target closure check + formula/hyperlink-count invariants around tspan lowering. Post-conversion: per-element `trace_events` (decision, shape_id, bounds_emu, fidelity class) and a per-slide `trace_out` summary. What it **cannot** detect: cross-renderer text metrics (mitigated only by calibrated headroom constants), consumer-machine font availability (for the export path; `text_outline` does enforce local fonts but that's off-path), and true visual regression (no raster-diff in supplied code — UNKNOWN, plausibly in `svg_quality_checker.py`, which is *referenced in docstrings but absent from the supplied inventory*).

---

## 8. Minimum safe SVG subset for QueueZero Stage 3 (RECOMMENDATION)

- **Canvas:** root `<svg>` with explicit `viewBox` (contract-enforced); no `<style>` element — presentation **attributes or inline `style=` only**.
- **Structure:** flat top-level `<g id="queuezero-…">` per logical block (animation + selection); group transforms limited to none/translate/scale (full-matrix support predicate `supports_full_project_transform` is unsupplied — don't rely on it).
- **KPI cards:** `<rect rx=R ry=R>` (equal) → native roundRect with live handle. Never rx≠ry.
- **Arrows/connectors:** `<line>` + `marker-start/end` referencing one of the five classifiable markers (default `markerUnits="strokeWidth"`, ratio 2.5 ≈ med). True attached connectors require the import-metadata vocabulary — out of scope for fresh authoring.
- **Process diagrams:** `rect/circle/ellipse/path(M/L/C/Z)/polygon` + arrowed lines + text. Gradients: linear axis-aligned; radial with default center focus only.
- **Icons:** `<use href="#local-def-id">` (same-document) — verified expansion path exists.
- **Text:** `<text x y>` with only allowlisted properties; tspans only as dy-stacked lines or `baseline-shift`; literal casing (no `text-transform`); pick `text_flow='preserve'` initially.
- **Image:** exactly one `<image>` with explicit positive width/height, **PNG or JPEG**, data URI or project-relative path; no clip/filter/transform on it in v1 (aspect-ratio grammar unsupplied).
- **Run flags:** `native_objects=False` (default), `promote_background=True`, capture `trace_out` and assert zero `skip`/non-`exact`-fidelity events for critical shapes.

## 9. Reusable engineering principles vs repo-specific code

**Reusable (principle → evidence):** closed-grammar allow/denylists with shared checker+converter diagnostics (`text_properties` header states this dual use) → validate-before-emit compilers beat best-effort converters; minimal IR normalization (M/L/C/Z) → backend simplification; affine decomposition with hard failure on inexpressible cases; explicit fidelity taxonomy in traces; content-hash edit-guard fingerprints; ID reservation/claim/reference closure for referential integrity; documented approximation constants (Bézier k≈0.5523, σ×2 shadow, α×0.75, headroom tables); narrow heuristics (background promotion candidacy test).
**Repo-specific, don't copy blindly:** the `data-pptx-*` attribute vocabulary (round-trip coupled to `pptx_to_svg`), hash-locked 187-shape preset registry (`pptx_shapes.load_shape_type_values`), `spec_lock.md` theme parsing, `resource_paths` project layout, chrome-ID animation heuristics, and the base64 txBody restoration machinery.

## 10. Risks & unknowns

R1: text-frame internals (wrap/anchor/autofit XML) unverified — truncated. R2: `p:pic`/crop/media-rel construction unverified. R3: shadow/glow input grammar (`parse_project_filter_params`) undefined — our SVGs must copy corpus filters verbatim until sourced. R4: chart/table marker contract unread. R5: packaging layer (`builder.py`) unreviewed — converter output alone lacks timing/layout/master wiring. R6: silent-skip tier (degenerate shapes) could quietly drop thin dividers.

## 11. Follow-up source requests

1. `drawingml/elements.py` bytes beyond the truncation point (symbols: `convert_text`, `convert_image`, `convert_nested_svg`, `_coalesce_text_runs`, txBody emission).
2. `drawingml/utils.py` (`parse_project_filter_params`, `classify_project_marker_shape`, `parse_project_stroke_dasharray`, `parse_project_image_aspect_ratio`, `supports_full_project_length/project_transform`, `font_px_to_hpt`).
3. `tspan_flattener.py`, `use_expander.py`, `canvas_contract.py`, `geometry_properties.py`.
4. `native_objects/__init__.py`, `table.py`, `chart_xml.py`, `marker_attributes.py`, `fallback_hash.py`.
5. `pptx_package/builder.py`, `cli.py`, `slide_xml.py`, `media.py`.
6. `drawingml/theme_fonts.py`; top-level `hyperlink_contract.py`, `resource_paths.py`, `native_payloads.py`.
7. `docs/technical-design.md`, `scripts/docs/svg-pipeline.md`, `references/svg-image-embedding.md`; locate `svg_quality_checker.py` (referenced, absent from inventory).

Awaiting GPT disposition on findings and follow-up fetch priority.