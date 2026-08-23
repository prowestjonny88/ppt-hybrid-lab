# Stage 4 Visual Acceptance Gate

Status: DRAFT / ACTIVE BENCHMARK CONTRACT

## Purpose

Stage 3 structural QA was necessary but insufficient. Stage 4 introduces a visual-quality gate that can reject a deck even when it is valid PPTX, collision-free, semantically correct, and highly editable.

The product-level bar is:

> Would a strong hackathon team willingly submit and present this deck to win?

## Gate layers

A candidate must pass all four layers:

1. semantic integrity;
2. structural/render integrity;
3. editability integrity;
4. visual quality.

A failure in any layer blocks product acceptance.

## A. Semantic hard failures

Immediate FAIL:
- invented fact, metric, source, badge, validation state, or claim;
- internal IR/schema label visible to the audience;
- uncertainty rendered as confirmed proof;
- generated artwork contains forbidden semantic text;
- known text differs materially from canonical semantic text unless the Visual IR explicitly permits a display-shortened form with traceability.

## B. Structural hard failures

Immediate FAIL:
- title/subtitle collision;
- clipped primary content;
- overlapping information objects not authorized by Visual IR;
- unreadable source caused by crop/overflow;
- image crop removes the required visual subject;
- object rendered outside the safe canvas;
- broken connector topology;
- accidental font fallback that materially changes hierarchy.

## C. Editability gate

For the hybrid product candidate:
- normalized panic-test editability >= 0.90;
- must-remain-editable text remains real PowerPoint text;
- product screenshots remain independently replaceable;
- bounded generated hero remains independently replaceable/regenerable;
- normal edits do not require full-slide regeneration;
- user-added objects survive later semantic edits.

## D. Visual scoring

Each rendered slide is scored 1–5 on ten dimensions.

### 1. First impression
1 = amateur / obviously generated badly
3 = acceptable business slide
5 = immediately feels intentional, premium, presentation-ready

### 2. Hierarchy clarity
1 = no clear reading order
3 = readable but ordinary
5 = protagonist is obvious within one glance and support hierarchy is effortless

### 3. Composition intentionality
1 = items merely placed into boxes
3 = coherent layout
5 = spatial relationships reinforce the message and feel deliberately art-directed

### 4. Originality / non-generic feel
1 = generic card dashboard / template filler
3 = competent familiar composition
5 = distinctive without becoming decorative noise

### 5. Information-to-space fit
1 = crowded or dead
3 = acceptable density
5 = excellent use of whitespace, scale, and compression for the amount of information

### 6. Typography
1 = weak sizing/wrapping/alignment
3 = professional baseline
5 = typography itself contributes to hierarchy and visual character

### 7. Visual protagonist strength
1 = multiple equal focal points or none
3 = primary object identifiable
5 = one strong visual idea carries the slide

### 8. Style coherence
1 = arbitrary visuals/tokens
3 = internally consistent
5 = clear identity anchors and treatment language without repetitive wallpaper

### 9. Deck rhythm
1 = same slide repeated / random sequence
3 = reasonable variation
5 = intentional pacing, escalation, relief, and transition across the deck

### 10. Judge-room presentability
1 = would avoid showing it
3 = could present it
5 = would confidently use it in a serious final pitch

## Minimum acceptance

Per slide:
- no hard failures;
- `hierarchy_clarity >= 4`;
- `composition_intentionality >= 4`;
- `judge_room_presentability >= 4`;
- mean of ten visual dimensions >= 4.0.

Per deck:
- no slide below 3 on any visual dimension;
- deck-rhythm score >= 4;
- at least two slides must score >= 4.5 overall to prevent a deck of merely uniform competence;
- no adjacent slides may use effectively identical primary composition unless Visual IR marks them as an intentional sequence.

## Comparison protocol

QueueZero Stage 4 redesign uses frozen Stage 3 semantics. The same claims/evidence are preserved.

Primary comparison:
- Stage 3 hybrid engineering fixture vs Stage 4 Visual-IR-driven hybrid.

Secondary reference:
- Stage 3 Gemini full-slide image-first output as an adversarial visual reference, not semantic authority.

Do not optimize Stage 4 to imitate image-first pixels. Optimize for the joint objective:

```text
visual quality
+ semantic integrity
+ routine editability
+ local regeneration
+ deterministic QA
```

## Review procedure

1. Render PPTX to pixels through one fixed renderer for all candidates.
2. Run semantic/structural automated checks first.
3. Hide implementation identity for visual scoring where practical.
4. Score each slide independently.
5. Score deck rhythm on the full contact sheet.
6. Record reasons for every score <= 3.
7. Fix pattern-level failures in Visual IR/archetype/style/compiler rather than page-specific coordinates whenever possible.
8. Rerender and rescore.

## Pattern-level failure examples

Treat these as architecture/system failures:
- all metric slides become equal cards;
- titles consistently consume excessive vertical space;
- diagrams are horizontally centered regardless of message;
- screenshots always use the same right-side phone frame;
- generated heroes feel visually detached from native content;
- dense slides shrink fonts rather than changing composition;
- style identity exists only as repeated blue accents;
- every slide begins with the same title/subtitle stack;
- supporting evidence is always boxed;
- whitespace is residual rather than intentionally protected.

## Stage 4 final question

A technically passing deck is not accepted until the answer to this question is YES:

> If judging started in 10 minutes, would we submit this exact rendered deck without wanting to redesign it first?
