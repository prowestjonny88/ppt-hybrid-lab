import json
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.util import Inches

from src.ir.runtime import canonical_hash, load_json

SLIDES = [
    ("problem-hook", "problem_hook.png", "problem_hook.v1.json"),
    ("how-it-works", "how_it_works.png", "how_it_works.v1.json"),
    ("validation-traction", "validation_traction.png", "validation_traction.v1.json"),
]


def _name_shape(shape, name):
    for elem in shape._element.iter():
        if elem.tag.endswith("}cNvPr"):
            elem.set("name", name)
            return
    raise RuntimeError("shape has no cNvPr")


def _validate_image(path):
    with Image.open(path) as image:
        width, height = image.size
    ratio = width / height
    if abs(ratio - (16 / 9)) > 0.01:
        raise RuntimeError(f"image-first asset must be 16:9: {path} is {width}x{height}")
    return width, height


def build_image_first(root, assets_dir, output_pptx, manifest_path):
    root = Path(root)
    assets_dir = Path(assets_dir)
    deck = load_json(root / "experiment/queuezero/deck_system.stage3.json")
    prs = Presentation()
    prs.slide_width = Inches(deck["slide_size"]["width_in"])
    prs.slide_height = Inches(deck["slide_size"]["height_in"])
    blank = prs.slide_layouts[6]
    manifest = {
        "schema_version": "stage3-image-first-package-v1",
        "variant": "image_first",
        "slides": [],
    }
    for slide_id, filename, semantics_name in SLIDES:
        image_path = assets_dir / filename
        if not image_path.exists():
            raise RuntimeError(f"missing generated image-first asset: {image_path}")
        width, height = _validate_image(image_path)
        semantics = load_json(root / "experiment/queuezero/slide_semantics" / semantics_name)
        slide = prs.slides.add_slide(blank)
        picture = slide.shapes.add_picture(str(image_path), 0, 0, prs.slide_width, prs.slide_height)
        _name_shape(picture, f"oxq:{slide_id}:full_slide:image_first")
        manifest["slides"].append({
            "slide_id": slide_id,
            "image": str(image_path),
            "pixel_size": [width, height],
            "semantic_hash": canonical_hash(semantics),
            "ppt_shape_name": picture.name,
            "editability_class": "full_slide_raster_baseline",
        })
    output_pptx = Path(output_pptx)
    output_pptx.parent.mkdir(parents=True, exist_ok=True)
    prs.save(output_pptx)
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_pptx, manifest
