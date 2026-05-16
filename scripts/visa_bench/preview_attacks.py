#!/usr/bin/env python
"""Create a preview grid for generated VISA-Bench attack pairs."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from visa_bench.utils.io import ensure_dir, read_jsonl, resolve_input_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Output manifest from generator.")
    parser.add_argument("--input-root", required=True, help="Root directory for clean images.")
    parser.add_argument("--output-root", required=True, help="Root directory containing attacked images.")
    parser.add_argument("--preview-out", required=True, help="Path to save preview grid image.")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--thumb-size", type=int, default=192)
    return parser.parse_args()


def _font() -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size=13)
    except OSError:
        return ImageFont.load_default()


def _thumb(path: Path, size: int) -> Image.Image:
    with Image.open(path) as image:
        image = image.convert("RGB")
        image.thumbnail((size, size))
        canvas = Image.new("RGB", (size, size), (245, 245, 245))
        x = (size - image.width) // 2
        y = (size - image.height) // 2
        canvas.paste(image, (x, y))
        return canvas


def _resolve_clean_image(record: dict, input_root: str) -> Path:
    clean_path = resolve_input_path(str(record["clean_image"]), input_root)
    if clean_path.exists():
        return clean_path
    resolved = record.get("clean_image_resolved")
    if resolved:
        fallback = Path(str(resolved))
        if fallback.exists():
            return fallback
    return clean_path


def main() -> None:
    args = parse_args()
    records = [
        record
        for record in read_jsonl(args.manifest)
        if record.get("generation_status") == "success"
    ][: args.limit]

    if not records:
        raise SystemExit("No successful records found to preview.")

    thumb = args.thumb_size
    label_h = 28
    pair_w = thumb * 2
    cell_h = thumb + label_h
    cols = min(3, len(records))
    rows = (len(records) + cols - 1) // cols
    grid = Image.new("RGB", (cols * pair_w, rows * cell_h), (255, 255, 255))
    draw = ImageDraw.Draw(grid)
    font = _font()

    for idx, record in enumerate(records):
        row = idx // cols
        col = idx % cols
        x = col * pair_w
        y = row * cell_h
        clean_path = _resolve_clean_image(record, args.input_root)
        attacked_path = Path(args.output_root) / str(record["attacked_image"])
        clean_thumb = _thumb(clean_path, thumb)
        attacked_thumb = _thumb(attacked_path, thumb)
        grid.paste(clean_thumb, (x, y + label_h))
        grid.paste(attacked_thumb, (x + thumb, y + label_h))
        label = f"{record.get('sample_id', '?')} | {record.get('attack_type', '?')}"
        draw.text((x + 4, y + 6), label[:60], fill=(0, 0, 0), font=font)
        draw.line((x + thumb, y + label_h, x + thumb, y + cell_h), fill=(210, 210, 210), width=1)

    preview_path = Path(args.preview_out)
    ensure_dir(preview_path.parent)
    grid.save(preview_path)
    print(f"Saved preview: {preview_path}")


if __name__ == "__main__":
    main()
