#!/usr/bin/env python3
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "experiment" / "queuezero" / "assets"


def product_ui(path, variant=1):
    image = Image.new("RGB", (720, 1280), "#F7F8FA" if variant == 1 else "#F9FAFB")
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((35, 35, 685, 1245), radius=38, fill="#FFFFFF", outline="#D1D5DB", width=4)
    d.rounded_rectangle((75, 95, 645, 250), radius=20, fill="#E8F0FF" if variant == 1 else "#FFF3E8")
    d.text((105, 155), "QueueZero - live cafeteria waits", fill="#111827")
    waits = ("8 min", "18 min", "11 min") if variant == 1 else ("6 min", "14 min", "9 min")
    rows = [(320, "North cafeteria", waits[0]), (525, "Central cafeteria", waits[1]), (730, "South cafeteria", waits[2])]
    for y, label, wait in rows:
        d.rounded_rectangle((85, y, 635, y + 165), radius=20, fill="#FFFFFF", outline="#E5E7EB", width=3)
        d.text((120, y + 55), label, fill="#111827")
        d.text((510, y + 55), wait, fill="#2563EB" if variant == 1 else "#F97316")
    d.rounded_rectangle((155, 1000, 565, 1120), radius=30, fill="#2563EB" if variant == 1 else "#F97316")
    d.text((270, 1045), "Best option", fill="#FFFFFF")
    image.save(path)


def structural_problem_hero(path, variant=1):
    """Text-free deterministic fixture used only for structural hybrid testing."""
    image = Image.new("RGB", (960, 720), "#F3F4F6")
    d = ImageDraw.Draw(image)
    d.rectangle((0, 470, 960, 720), fill="#D1D5DB")
    d.rectangle((500, 105, 900, 320), fill="#FFFFFF", outline="#9CA3AF", width=4)
    d.rectangle((555, 150, 845, 265), fill="#2563EB" if variant == 1 else "#F97316")
    people = [(155, 500), (290, 470), (425, 440), (560, 410), (695, 380)]
    if variant == 2:
        people = [(130, 520), (245, 485), (360, 455), (475, 425), (590, 395), (705, 365)]
    for idx, (x, y) in enumerate(people):
        fill = ("#2563EB" if variant == 1 else "#F97316") if idx == 0 else "#6B7280"
        d.ellipse((x - 34, y - 90, x + 34, y - 22), fill=fill)
        d.rounded_rectangle((x - 45, y - 25, x + 45, y + 105), radius=22, fill=fill)
    d.line((105, 625, 790, 365), fill="#9CA3AF", width=8)
    image.save(path)


def sponsor_logo(path):
    image = Image.new("RGBA", (420, 160), (255, 255, 255, 0))
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((8, 8, 412, 152), radius=30, fill="#111827")
    d.ellipse((30, 32, 118, 120), fill="#F97316")
    d.text((145, 58), "SPONSOR", fill="#FFFFFF")
    image.save(path)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    outputs = [
        (ASSETS / "product_ui_v1.png", lambda p: product_ui(p, 1)),
        (ASSETS / "product_ui_v2.png", lambda p: product_ui(p, 2)),
        (ASSETS / "problem_hero_structural_v1.png", lambda p: structural_problem_hero(p, 1)),
        (ASSETS / "problem_hero_structural_v2.png", lambda p: structural_problem_hero(p, 2)),
        (ASSETS / "sponsor_logo_v1.png", sponsor_logo),
    ]
    for path, builder in outputs:
        builder(path)
        print(f"Created benchmark fixture: {path.relative_to(ROOT)}")
    print("NOTE: structural hero fixtures are not eligible for blind visual-quality scoring.")


if __name__ == "__main__":
    main()
