# PPT Master SVG→DrawingML — GPT Adjudication

Source Ox report: `.ox/reports/task-002-ppt-master-svg-drawingml.md`
Reference repo: `hugohe3/ppt-master` @ `65bb2eca59a36270819caba377097910c4466c6e`

## Decision summary

### ACCEPT

1. **Fail-closed compiler architecture.** The SVG→DrawingML path validates a deliberately constrained SVG grammar and raises on unsupported visual constructs rather than silently rasterizing the slide.
2. **Native basic geometry is a viable Stage 3 substrate.** Basic rect/circle/ellipse/line/path/polygon/polyline/group dispatch exists and produces DrawingML-native output paths.
3. **Text is deliberately constrained for deterministic native mapping.** The text-property module uses a closed allowlist/denylist shared by validation and conversion.
4. **Unsupported visual tags are explicitly rejected.** `collect_unsupported_visuals()` plus `convert_element()` form an explicit fail-closed boundary.
5. **Native chart/table replacement is a separate opt-in path.** It is not required for the first QueueZero hybrid experiment.
6. **A conservative fresh-authoring SVG subset is appropriate for Stage 3.** Use simple shapes, controlled paths, controlled text, simple line markers, local-use icons only if needed, and validated raster images.

### MODIFY / NARROW

1. Ox's complete feature support matrix is accepted only for claims directly supported by the supplied 11-file source package. Do not generalize unsupported/partial behavior to unsupplied helpers without follow-up evidence.
2. For Stage 3 v0, prefer PNG/JPEG for raster assets even though the implementation recognizes a broader format set. This is a deliberately narrower experimental contract, not a claim about PPT Master's total support.
3. Do not require every group trace to report `exact` fidelity: group geometry may be classified `visual-only` while still being native. Critical leaf objects should instead be checked for expected native output and absence of skips/errors.

### NEEDS VERIFICATION

1. `convert_text` internals: wrapping, anchoring, autofit/body properties, run coalescing.
2. `convert_image` internals: `p:pic`, crop, media and relationship construction.
3. `drawingml/utils.py`: filter parameters, marker classification, transform/length support details.
4. Native chart/table marker implementation.
5. Final `pptx_package/builder.py` wiring and any visual QA outside the supplied converter files.
6. Silent skip behavior for degenerate shapes in real benchmark slides.

## Stage 3 minimum native/vector contract

For the first QueueZero experiment, constrain authored SVG to:

- explicit root `viewBox`;
- `rect` and equal-radius rounded rects;
- `circle` / `ellipse`;
- `line` with simple approved marker ends;
- `path` limited to straightforward M/L/C/Z geometry where practical;
- `polygon` / `polyline`;
- native text using only the closed project text grammar;
- flat or shallow groups with conservative transforms;
- simple solid fills; optional simple linear gradients only if needed;
- one validated PNG/JPEG image with explicit positive width/height;
- no masks, `foreignObject`, `textPath`, CSS `<style>` blocks, complex filters, or arbitrary shear transforms.

## Architectural implication

PPT Master provides enough verified evidence to justify testing **native/vector as a first-class rendering lane** in Stage 3. It does **not** yet prove that native/vector output can match image-generation visual quality. That remains the purpose of the 3×3 QueueZero architecture experiment.
