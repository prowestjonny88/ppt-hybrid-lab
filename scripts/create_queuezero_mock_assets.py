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


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / "product_ui_v1.png"
    product_ui(path)
    print(f"Created deterministic asset: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
