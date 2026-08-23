# Stage 3 Architecture Hypotheses

These are hypotheses to test, not accepted architecture decisions.

## H1 — Full-slide image-first

Pipeline:

```text
slide brief
→ image generation
→ full-slide raster
→ PPTX packaging
→ optional reconstruction
```

### Hypothesis

Whole-slide image generation may produce the highest visual ceiling, and that advantage may justify downstream reconstruction/editing friction.

### Evidence needed

- blinded visual-quality comparison
- exact-text reliability
- cost/time of ordinary last-minute edits
- collateral changes during regeneration
- reconstruction quality when editability is requested

---

## H2 — Native/vector-first

Pipeline:

```text
semantic slide specification
→ native PowerPoint components and/or authored SVG
→ DrawingML/PPTX
```

### Hypothesis

A constrained native/vector renderer may already be visually strong enough for hackathon pitch decks, making full-slide image generation unnecessary.

### Evidence needed

- actual visual ceiling on Problem / How It Works / Validation slides
- SVG-to-DrawingML feature limits
- text/layout freedom
- native object audit
- edit-speed tests

---

## H3 — Hybrid native/vector/image

Pipeline:

```text
semantic Slide IR
→ routing decision per element/region
   ├─ native PPT objects
   ├─ SVG/vector → DrawingML
   └─ bounded generated imagery
→ assembled editable PPTX
```

### Hypothesis

Native objects can preserve information and last-mile editability while bounded image generation supplies visual richness, yielding most of image-first visual quality with near-native editability.

### Evidence needed

- image-first vs native/vector vs hybrid comparison on identical content
- ability to regenerate only a hero/visual region
- no full-slide raster fallback for ordinary information slides
- exact metric/text fidelity
- screenshot/image replacement
- local editing without code or AI calls

---

# Decision criterion

Do not accept H3 merely because it sounds architecturally elegant.

The Stage 3 experiment must determine whether hybrid retains enough visual quality to justify its added routing/assembly complexity.

A provisional success target is:

- hybrid visual quality close to the image-first baseline
- hybrid last-mile editability close to the native/vector baseline
- no whole-slide regeneration for ordinary text, metric, screenshot, logo, color, or position changes

Exact numeric thresholds should be treated as experimental evaluation guidance rather than product requirements until real benchmark results exist.
