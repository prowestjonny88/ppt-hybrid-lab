# Stage 4 Style Sample Protocol

Status: ACTIVE DRAFT

## Why this gate exists

Stage 3 demonstrated that a system can satisfy semantic, structural, and editability constraints while still producing slides nobody wants to present.

Stage 4 therefore requires a **representative content-slide sample** before scaling the visual system across the deck.

The approved sample is a **style reference**, not a frozen layout template.

## Sample selection

Prefer the slide that best exercises the intended design system rather than the easiest cover slide.

For QueueZero Stage 4, the first sample candidate is:

> `validation-traction`

Reason:
- it exposes hierarchy quality immediately;
- it contains one hero metric, one strong technical proof, compact scope evidence, uncertainty, and a terminal next step;
- generic card-grid tendencies are easy to detect;
- all information can remain native/editable, so visual quality cannot be attributed only to a generated hero image.

Secondary sample if needed:

> `how-it-works`

This tests diagram composition + real screenshot integration.

## Before generating the sample

The following must already exist and pass validation:
- semantic Slide IR;
- Visual IR;
- selected composition archetype;
- deck style profile;
- renderer capability routing;
- no raw coordinates in Visual IR;
- structural content/capacity gate.

## Sample output

Generate only one final-form candidate slide through the same architecture intended for production:

```text
Semantic IR
 -> Visual IR
 -> Visual IR compiler
 -> hybrid render lanes
 -> PPTX
 -> fixed pixel renderer
 -> sample PNG
```

Do not use an image-only mockup as the approval sample for an editable-product path.

## Human approval questions

The reviewer should answer only these product-relevant questions:

1. Does this look strong enough that you would want the rest of the deck to feel like it?
2. Is the visual protagonist obvious within one glance?
3. Does the composition feel intentionally designed rather than automatically arranged?
4. Is the typography/style direction right for a serious hackathon final?
5. Is the density right?
6. What should remain stable across the deck?
7. What specifically should vary so later slides do not feel copied?

The user does not need to approve renderer coordinates, object IDs, or technical implementation details.

## Approval artifact

After approval, record:

```json
{
  "sample_slide_id": "validation-traction",
  "approved_render_path": "...",
  "visual_ir_hash": "...",
  "style_profile_hash": "...",
  "compiler_version": "...",
  "stable_identity": [
    "palette",
    "typography_character",
    "whitespace_character",
    "shape_vocabulary",
    "image_treatment",
    "identity_anchors"
  ],
  "must_vary": [
    "primary_composition",
    "hero_position",
    "support_group_geometry"
  ]
}
```

## After approval

Later slides should use the sample as a style-only reference.

Preserve:
- palette relationships;
- typography character;
- density character;
- whitespace quality;
- shape / line language;
- image treatment;
- repeated identity anchors.

Do not preserve automatically:
- exact hero position;
- exact title position;
- exact zone geometry;
- identical containers;
- identical dark-field placement;
- exact decoration placement.

## Reject and revise

If the sample does not clear the Stage 4 Visual Acceptance Gate:
- do not generate the rest of the deck;
- diagnose whether the failure belongs to Visual IR, archetype, style profile, compiler, or renderer;
- fix the highest reusable layer possible;
- regenerate the same representative slide;
- repeat until approved or a genuine product/design decision requires human input.

## Paid visual generation

If the sample requires a new paid generated visual asset, explicit spend approval is required before the call. Structural/native iterations should proceed without paid regeneration whenever possible.
