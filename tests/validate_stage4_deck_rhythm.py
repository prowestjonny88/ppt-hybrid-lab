#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "experiment/queuezero/stage4_deck_plan.v0.json"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    plan = load(PLAN_PATH)
    errors = []
    slides = sorted(plan["slides"], key=lambda x: x["position"])
    rules = plan["deck_rules"]

    positions = [s["position"] for s in slides]
    if positions != list(range(1, len(slides) + 1)):
        errors.append(f"positions must be contiguous from 1; got {positions}")

    seen_ids = set()
    resolved = []
    for item in slides:
        if item["slide_id"] in seen_ids:
            errors.append(f"duplicate slide_id {item['slide_id']}")
        seen_ids.add(item["slide_id"])
        path = ROOT / item["visual_ir"]
        if not path.exists():
            errors.append(f"missing Visual IR {item['visual_ir']}")
            continue
        ir = load(path)
        if ir.get("slide_id") != item["slide_id"]:
            errors.append(f"slide_id mismatch for {item['visual_ir']}")
        resolved.append((item, ir))

    same_archetype_streak = 0
    anchor_streak = 0
    previous_archetype = None
    previous_signature = None
    previous_anchor = None
    previous_dark = False

    for item, ir in resolved:
        archetype = ir["composition"]["archetype_id"]
        variation_tags = tuple(sorted(ir.get("style", {}).get("variation_tags", [])))
        hero_anchor = ir.get("deck_rhythm", {}).get("hero_anchor_preference")
        anchors = set(ir.get("style", {}).get("identity_anchor_refs", []))
        uses_dark = "dark_proof_field" in anchors

        declared_previous = ir.get("deck_rhythm", {}).get("previous_archetype")
        if item["position"] > 1 and declared_previous and declared_previous != previous_archetype:
            errors.append(
                f"{item['slide_id']}: previous_archetype={declared_previous!r} does not match actual {previous_archetype!r}"
            )

        avoid = set(ir.get("deck_rhythm", {}).get("avoid_archetypes", []))
        if archetype in avoid:
            errors.append(f"{item['slide_id']}: current archetype {archetype!r} appears in its avoid_archetypes")

        if archetype == previous_archetype:
            same_archetype_streak += 1
        else:
            same_archetype_streak = 1
        if same_archetype_streak > rules["max_adjacent_same_archetype"]:
            errors.append(f"{item['slide_id']}: archetype {archetype!r} repeated beyond adjacency budget")

        if rules.get("require_distinct_adjacent_variation_signature") and previous_signature == variation_tags:
            errors.append(f"{item['slide_id']}: adjacent variation signature repeats {variation_tags}")

        if hero_anchor and hero_anchor == previous_anchor:
            anchor_streak += 1
        else:
            anchor_streak = 1 if hero_anchor else 0
        if anchor_streak > rules["max_same_protagonist_anchor_streak"]:
            errors.append(f"{item['slide_id']}: protagonist anchor {hero_anchor!r} repeated too many slides")

        if rules["major_dark_field_max_adjacent"] <= 1 and previous_dark and uses_dark:
            errors.append(f"{item['slide_id']}: major dark field repeats on adjacent slides")

        previous_archetype = archetype
        previous_signature = variation_tags
        previous_anchor = hero_anchor
        previous_dark = uses_dark

    if errors:
        print(f"Stage 4 deck rhythm validation failed with {len(errors)} issue(s)")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)

    print(f"Stage 4 deck rhythm validation passed for {len(resolved)} slides")


if __name__ == "__main__":
    main()
