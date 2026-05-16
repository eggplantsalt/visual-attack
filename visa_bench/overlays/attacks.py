"""High-level visual attack renderers."""

from __future__ import annotations

from typing import Any

from PIL import Image

from visa_bench.schema.sample import ATTACK_TYPES
from visa_bench.utils.geometry import (
    ensure_min_bbox_size,
    normalized_bbox_to_pixels,
    normalized_point_to_pixels,
    normalized_points_to_pixels,
)
from visa_bench.overlays.primitives import (
    draw_arrow,
    draw_polyline,
    draw_rectangle_marker,
    draw_text_box,
)


def apply_attack(image: Image.Image, record: dict[str, Any]) -> tuple[Image.Image, dict[str, Any]]:
    """Apply the requested attack and return the attacked image plus overlay metadata."""

    attacked = image.convert("RGBA")
    attack_type = record.get("attack_type")
    if attack_type not in ATTACK_TYPES:
        raise ValueError(f"unsupported attack_type: {attack_type}")

    if attack_type == "text_note":
        metadata = _text_note(attacked, record)
    elif attack_type == "arrow":
        metadata = _arrow(attacked, record)
    elif attack_type == "object_label":
        metadata = _object_label(attacked, record)
    elif attack_type == "region_marker":
        metadata = _region_marker(attacked, record)
    else:
        metadata = _trajectory_sketch(attacked, record)

    return attacked.convert("RGB"), metadata


def _style(record: dict[str, Any]) -> dict[str, Any]:
    style = record.get("style")
    return style if isinstance(style, dict) else {}


def _text(record: dict[str, Any]) -> str:
    return str(record.get("text") or record.get("attack_goal") or "ATTENTION")


def _bbox(
    record: dict[str, Any],
    width: int,
    height: int,
    default: tuple[float, float, float, float],
) -> tuple[int, int, int, int]:
    bbox = record.get("bbox", default)
    if not isinstance(bbox, list) or len(bbox) != 4:
        bbox = default
    return ensure_min_bbox_size(normalized_bbox_to_pixels(bbox, width, height), width, height)


def _text_note(image: Image.Image, record: dict[str, Any]) -> dict[str, Any]:
    width, height = image.size
    bbox = _bbox(record, width, height, (0.66, 0.76, 0.96, 0.94))
    style = _style(record)
    draw_text_box(
        image,
        bbox,
        _text(record),
        fill=tuple(style.get("fill", (255, 255, 240, 238))),
        outline=tuple(style.get("outline", (25, 25, 25, 255))),
        text_fill=tuple(style.get("text_fill", (0, 0, 0, 255))),
    )
    return {"overlay_bbox_pixels": list(bbox)}


def _arrow(image: Image.Image, record: dict[str, Any]) -> dict[str, Any]:
    width, height = image.size
    start = record.get("start") if isinstance(record.get("start"), list) else [0.15, 0.82]
    end = record.get("end") if isinstance(record.get("end"), list) else [0.5, 0.5]
    start_px = normalized_point_to_pixels(start, width, height)
    end_px = normalized_point_to_pixels(end, width, height)
    style = _style(record)
    draw_arrow(
        image,
        start_px,
        end_px,
        color=tuple(style.get("color", (230, 35, 35, 255))),
        width=style.get("width"),
    )
    return {"overlay_points_pixels": [list(start_px), list(end_px)]}


def _object_label(image: Image.Image, record: dict[str, Any]) -> dict[str, Any]:
    width, height = image.size
    anchor = _bbox(record, width, height, (0.04, 0.06, 0.28, 0.17))
    x1, y1, x2, y2 = anchor
    label_height = max(28, int(height * 0.1))
    label_width = max(80, min(int(width * 0.36), x2 - x1 + int(width * 0.12)))
    bbox = (
        max(0, x1),
        max(0, y1 - label_height // 2),
        min(width - 1, x1 + label_width),
        min(height - 1, y1 - label_height // 2 + label_height),
    )
    text = str(record.get("text") or record.get("attack_object") or record.get("attack_goal") or "label")
    style = _style(record)
    draw_text_box(
        image,
        bbox,
        text,
        fill=tuple(style.get("fill", (250, 250, 250, 240))),
        outline=tuple(style.get("outline", (35, 35, 35, 255))),
        text_fill=tuple(style.get("text_fill", (0, 0, 0, 255))),
        padding=5,
        font_size=style.get("font_size", 14),
    )
    return {"overlay_bbox_pixels": list(bbox)}


def _region_marker(image: Image.Image, record: dict[str, Any]) -> dict[str, Any]:
    width, height = image.size
    bbox = _bbox(record, width, height, (0.28, 0.28, 0.72, 0.72))
    style = _style(record)
    draw_rectangle_marker(
        image,
        bbox,
        outline=tuple(style.get("outline", (255, 205, 0, 255))),
        fill=tuple(style.get("fill", (255, 205, 0, 55))),
        width=style.get("width"),
    )
    if record.get("text"):
        label_bbox = (
            bbox[0],
            max(0, bbox[1] - max(26, height // 14)),
            min(width - 1, bbox[0] + max(100, (bbox[2] - bbox[0]) // 2)),
            max(24, bbox[1] - 2),
        )
        draw_text_box(
            image,
            label_bbox,
            str(record["text"]),
            fill=(255, 255, 220, 230),
            outline=tuple(style.get("outline", (255, 205, 0, 255))),
            padding=4,
            font_size=13,
        )
    return {"overlay_bbox_pixels": list(bbox)}


def _trajectory_sketch(image: Image.Image, record: dict[str, Any]) -> dict[str, Any]:
    width, height = image.size
    raw_points = record.get("points")
    if not isinstance(raw_points, list) or len(raw_points) < 2:
        raw_points = [[0.16, 0.72], [0.34, 0.58], [0.52, 0.66], [0.72, 0.42], [0.86, 0.5]]
    points = normalized_points_to_pixels(raw_points, width, height)
    style = _style(record)
    draw_polyline(
        image,
        points,
        color=tuple(style.get("color", (30, 110, 255, 255))),
        width=style.get("width"),
    )
    return {"overlay_points_pixels": [list(point) for point in points]}
