"""Coordinate conversion helpers for normalized image annotations."""

from __future__ import annotations

from typing import Iterable, Sequence


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def clamp01(value: float) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = 0.0
    return clamp(numeric, 0.0, 1.0)


def normalized_point_to_pixels(point: Sequence[float], width: int, height: int) -> tuple[int, int]:
    x = int(round(clamp01(point[0]) * max(width - 1, 0)))
    y = int(round(clamp01(point[1]) * max(height - 1, 0)))
    return x, y


def normalized_bbox_to_pixels(bbox: Sequence[float], width: int, height: int) -> tuple[int, int, int, int]:
    p1 = normalized_point_to_pixels((bbox[0], bbox[1]), width, height)
    p2 = normalized_point_to_pixels((bbox[2], bbox[3]), width, height)
    x1, x2 = sorted((p1[0], p2[0]))
    y1, y2 = sorted((p1[1], p2[1]))
    return x1, y1, x2, y2


def normalized_points_to_pixels(
    points: Iterable[Sequence[float]], width: int, height: int
) -> list[tuple[int, int]]:
    return [normalized_point_to_pixels(point, width, height) for point in points]


def ensure_min_bbox_size(
    bbox: tuple[int, int, int, int], width: int, height: int, min_size: int = 8
) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = bbox
    if x2 - x1 < min_size:
        x2 = min(width - 1, x1 + min_size)
        x1 = max(0, min(x1, x2 - min_size))
    if y2 - y1 < min_size:
        y2 = min(height - 1, y1 + min_size)
        y1 = max(0, min(y1, y2 - min_size))
    return x1, y1, x2, y2
