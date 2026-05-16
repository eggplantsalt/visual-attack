"""Low-level Pillow drawing primitives for visual attacks."""

from __future__ import annotations

import math
import textwrap
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont


Color = tuple[int, int, int] | tuple[int, int, int, int]


def get_font(size: int | None = None) -> ImageFont.ImageFont:
    if size is None:
        size = 16
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=3)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_text_to_width(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int
) -> str:
    words = text.split()
    if not words:
        return ""
    lines: list[str] = []
    line = words[0]
    for word in words[1:]:
        trial = f"{line} {word}"
        if text_size(draw, trial, font)[0] <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    wrapped: list[str] = []
    for line in lines:
        if text_size(draw, line, font)[0] <= max_width:
            wrapped.append(line)
        else:
            wrapped.extend(textwrap.wrap(line, width=max(8, max_width // 8)))
    return "\n".join(wrapped)


def draw_text_box(
    image: Image.Image,
    bbox: tuple[int, int, int, int],
    text: str,
    fill: Color = (255, 255, 235, 235),
    outline: Color = (30, 30, 30, 255),
    text_fill: Color = (0, 0, 0, 255),
    padding: int = 8,
    font_size: int | None = None,
) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    x1, y1, x2, y2 = bbox
    draw.rectangle(bbox, fill=fill, outline=outline, width=max(1, min(image.size) // 180))
    font = get_font(font_size or max(12, min(24, (y2 - y1) // 5)))
    max_text_width = max(1, x2 - x1 - padding * 2)
    wrapped = wrap_text_to_width(draw, text, font, max_text_width)
    draw.multiline_text((x1 + padding, y1 + padding), wrapped, fill=text_fill, font=font, spacing=3)


def draw_arrow(
    image: Image.Image,
    start: tuple[int, int],
    end: tuple[int, int],
    color: Color = (230, 35, 35, 255),
    width: int | None = None,
) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    if width is None:
        width = max(4, min(image.size) // 80)
    draw.line([start, end], fill=color, width=width)

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    head_len = max(12, width * 4)
    spread = math.radians(28)
    p1 = (
        int(end[0] - head_len * math.cos(angle - spread)),
        int(end[1] - head_len * math.sin(angle - spread)),
    )
    p2 = (
        int(end[0] - head_len * math.cos(angle + spread)),
        int(end[1] - head_len * math.sin(angle + spread)),
    )
    draw.polygon([end, p1, p2], fill=color)


def draw_rectangle_marker(
    image: Image.Image,
    bbox: tuple[int, int, int, int],
    outline: Color = (255, 205, 0, 255),
    fill: Color = (255, 205, 0, 55),
    width: int | None = None,
) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    if width is None:
        width = max(3, min(image.size) // 100)
    draw.rectangle(bbox, fill=fill)
    for offset in range(width):
        draw.rectangle(
            (bbox[0] + offset, bbox[1] + offset, bbox[2] - offset, bbox[3] - offset),
            outline=outline,
        )


def draw_polyline(
    image: Image.Image,
    points: Sequence[tuple[int, int]],
    color: Color = (30, 110, 255, 255),
    width: int | None = None,
    add_arrow_end: bool = True,
) -> None:
    if len(points) < 2:
        return
    draw = ImageDraw.Draw(image, "RGBA")
    if width is None:
        width = max(4, min(image.size) // 90)
    draw.line(list(points), fill=color, width=width, joint="curve")
    for point in points:
        radius = max(2, width // 2)
        draw.ellipse(
            (point[0] - radius, point[1] - radius, point[0] + radius, point[1] + radius),
            fill=color,
        )
    if add_arrow_end:
        draw_arrow(image, points[-2], points[-1], color=color, width=width)
