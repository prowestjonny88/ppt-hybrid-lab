#!/usr/bin/env python3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "experiment" / "queuezero" / "assets"


def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def product_ui(path, variant=1):
    """Deterministic product mock used as a replaceable screenshot fixture.

    Keep the UI illustrative but semantically conservative: no fabricated wait
    values, accuracy, retention, or market-fit claims. The only product decision
    text comes directly from the frozen QueueZero semantics.
    """
    signal = "#2563EB" if variant == 1 else "#F97316"
    signal_soft = "#E8EEFF" if variant == 1 else "#FFF0E8"
    image = Image.new("RGB", (720, 1280), "#EEF1F6")
    d = ImageDraw.Draw(image)

    # Device canvas.
    d.rounded_rectangle((32, 24, 688, 1256), radius=42, fill="#FFFFFF", outline="#CBD1DA", width=4)

    # Header / live sensing cue.
    d.text((78, 78), "QUEUEZERO", font=_font(25, True), fill="#111827")
    d.text((78, 120), "Live cafeteria decision", font=_font(18), fill="#6B7280")
    d.ellipse((575, 78, 597, 100), fill=signal)
    d.text((610, 76), "LIVE", font=_font(16, True), fill=signal)

    # Product output is the visual protagonist.
    d.rounded_rectangle((72, 205, 648, 510), radius=34, fill=signal)
    d.text((110, 250), "WAIT PREDICTION", font=_font(18, True), fill="#DCE5FF" if variant == 1 else "#FFE0CF")
    d.text((110, 300), "Go now", font=_font(54, True), fill="#FFFFFF")
    d.text((110, 382), "or choose another cafeteria", font=_font(22), fill="#FFFFFF")

    # Three known cafeteria contexts; no invented numeric estimates.
    d.text((78, 575), "Cafeterias", font=_font(20, True), fill="#111827")
    for idx, y in enumerate((635, 785, 935), start=1):
        d.rounded_rectangle((72, y, 648, y + 118), radius=24, fill="#F8FAFC", outline="#E3E7EE", width=3)
        d.text((104, y + 28), f"Cafeteria {idx}", font=_font(20, True), fill="#111827")
        d.text((104, y + 66), "wait estimate", font=_font(16), fill="#6B7280")
        # Small visual signal bar; decorative only, not a quantitative scale.
        d.rounded_rectangle((500, y + 45, 604, y + 60), radius=8, fill=signal_soft)
        d.rounded_rectangle((500, y + 45, 552 + idx * 8, y + 60), radius=8, fill=signal)

    d.text((78, 1125), "3 cafeterias in the controlled test", font=_font(17), fill="#6B7280")
    d.rounded_rectangle((78, 1175, 330, 1222), radius=22, fill=signal_soft)
    d.text((110, 1187), "Decision ready", font=_font(16, True), fill=signal)
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
