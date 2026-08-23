#!/usr/bin/env python3
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "experiment" / "queuezero" / "assets"


def product_ui(path):
    image = Image.new("RGB", (720, 1280), "#F7F8FA")
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((35, 35, 685, 1245), radius=38, fill="#FFFFFF", outline="#D1D5DB", width=4)
    d.rounded_rectangle((75, 95, 645, 250), radius=20, fill="#E8F0FF")
    d.text((105, 155), "QueueZero - live cafeteria waits", fill="#111827")
    rows = [(320, "North cafeteria", "8 min"), (525, "Central cafeteria", "18 min"), (730, "South cafeteria", "11 min")]
    for y, label, wait in rows:
        d.rounded_rectangle((85, y, 635, y + 165), radius=20, fill="#FFFFFF", outline="#E5E7EB", width=3)
        d.text((120, y + 55), label, fill="#111827")
        d.text((510, y + 55), wait, fill="#2563EB")
    d.rounded_rectangle((155, 1000, 565, 1120), radius=30, fill="#2563EB")
    d.text((270, 1045), "Best option", fill="#FFFFFF")
    image.save(path)


def structural_problem_hero(path):
    """Text-free deterministic fixture used only for structural hybrid testing."""
    image = Image.new("RGB", (960, 720), "#F3F4F6")
    d = ImageDraw.Draw(image)
    d.rectangle((0, 470, 960, 720), fill="#D1D5DB")
    d.rectangle((500, 105, 900, 320), fill="#FFFFFF", outline="#9CA3AF", width=4)
    d.rectangle((555, 150, 845, 265), fill="#2563EB")
    people = [(155, 500), (290, 470), (425, 440), (560, 410), (695, 380)]
    for idx, (x, y) in enumerate(people):
        fill = "#2563EB" if idx == 0 else "#6B7280"
        d.ellipse((x - 34, y - 90, x + 34, y - 22), fill=fill)
        d.rounded_rectangle((x - 45, y - 25, x + 45, y + 105), radius=22, fill=fill)
    d.line((105, 625, 790, 365), fill="#9CA3AF", width=8)
    image.save(path)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    product = ASSETS / "product_ui_v1.png"
    hero = ASSETS / "problem_hero_structural_v1.png"
    product_ui(product)
    structural_problem_hero(hero)
    print(f"Created deterministic asset: {product.relative_to(ROOT)}")
    print(f"Created structural-only hero fixture: {hero.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
