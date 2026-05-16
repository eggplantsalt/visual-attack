"""Schema helpers for VISA-Bench open-loop manifests."""

from __future__ import annotations

from typing import Any, Mapping


ATTACK_TYPES = (
    "text_note",
    "arrow",
    "object_label",
    "region_marker",
    "trajectory_sketch",
)

AUTHORITY_LABELS = (
    "trusted",
    "untrusted",
    "ambiguous",
    "irrelevant",
)

REQUIRED_FIELDS = (
    "sample_id",
    "clean_image",
    "task_instruction",
    "attack_type",
    "authority_label",
    "visual_source",
    "attack_goal",
    "task_goal",
)


def validate_record(record: Mapping[str, Any]) -> list[str]:
    """Return validation error strings for one input manifest record."""

    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing required field: {field}")
        elif not isinstance(record[field], str) or not record[field].strip():
            errors.append(f"field must be a non-empty string: {field}")

    attack_type = record.get("attack_type")
    if attack_type is not None and attack_type not in ATTACK_TYPES:
        errors.append(f"invalid attack_type: {attack_type}")

    authority_label = record.get("authority_label")
    if authority_label is not None and authority_label not in AUTHORITY_LABELS:
        errors.append(f"invalid authority_label: {authority_label}")

    _validate_optional_bbox(record, errors)
    _validate_optional_point(record, "start", errors)
    _validate_optional_point(record, "end", errors)
    _validate_optional_points(record, errors)

    if "style" in record and not isinstance(record["style"], dict):
        errors.append("style must be an object when provided")

    return errors


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_optional_bbox(record: Mapping[str, Any], errors: list[str]) -> None:
    if "bbox" not in record:
        return
    bbox = record["bbox"]
    if (
        not isinstance(bbox, list)
        or len(bbox) != 4
        or not all(_is_number(v) for v in bbox)
    ):
        errors.append("bbox must be [x1, y1, x2, y2] numeric list")


def _validate_optional_point(
    record: Mapping[str, Any], field: str, errors: list[str]
) -> None:
    if field not in record:
        return
    point = record[field]
    if (
        not isinstance(point, list)
        or len(point) != 2
        or not all(_is_number(v) for v in point)
    ):
        errors.append(f"{field} must be [x, y] numeric list")


def _validate_optional_points(record: Mapping[str, Any], errors: list[str]) -> None:
    if "points" not in record:
        return
    points = record["points"]
    if not isinstance(points, list):
        errors.append("points must be a list of [x, y] numeric points")
        return
    for idx, point in enumerate(points):
        if (
            not isinstance(point, list)
            or len(point) != 2
            or not all(_is_number(v) for v in point)
        ):
            errors.append(f"points[{idx}] must be [x, y] numeric list")
