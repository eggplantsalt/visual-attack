"""Open-loop VISA-Bench image attack generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image

from visa_bench import GENERATOR_VERSION
from visa_bench.overlays.attacks import apply_attack
from visa_bench.schema.sample import validate_record
from visa_bench.utils.io import (
    ensure_dir,
    read_jsonl,
    relative_to_root,
    resolve_input_path,
    safe_output_stem,
    write_jsonl,
)


def generate_open_loop_attacks(
    manifest: str | Path,
    input_root: str | Path | None,
    output_root: str | Path,
    output_manifest: str | Path | None = None,
    overwrite: bool = False,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Generate attacked images and write an output JSONL manifest."""

    output_root_path = ensure_dir(output_root)
    image_dir = ensure_dir(output_root_path / "images")
    output_manifest_path = Path(output_manifest) if output_manifest else output_root_path / "manifest_attacked.jsonl"

    records = read_jsonl(manifest)
    if limit is not None:
        records = records[:limit]

    output_records = []
    for index, record in enumerate(records):
        output_record = {k: v for k, v in record.items() if not k.startswith("_")}
        output_record["generator_version"] = GENERATOR_VERSION
        output_record.setdefault("attacked_image", None)
        output_record.setdefault("clean_image_resolved", None)
        output_record.setdefault("image_width", None)
        output_record.setdefault("image_height", None)
        output_record.setdefault("overlay_bbox_pixels", None)
        output_record.setdefault("overlay_points_pixels", None)
        output_record["generation_status"] = "failed"
        output_record["error_message"] = None

        try:
            if record.get("_json_error"):
                raise ValueError(record["_json_error"])
            errors = validate_record(record)
            if errors:
                raise ValueError("; ".join(errors))

            clean_path = resolve_input_path(str(record["clean_image"]), input_root)
            if not clean_path.exists():
                raise FileNotFoundError(f"clean image not found: {clean_path}")

            with Image.open(clean_path) as clean_image:
                clean_image = clean_image.convert("RGB")
                width, height = clean_image.size
                attacked_image, overlay_metadata = apply_attack(clean_image, record)

            output_name = safe_output_stem(record, index)
            output_path = image_dir / f"{output_name}.png"
            if output_path.exists() and not overwrite:
                raise FileExistsError(f"output image exists, use --overwrite: {output_path}")

            attacked_image.save(output_path)

            output_record.update(overlay_metadata)
            output_record["attacked_image"] = relative_to_root(output_path, output_root_path)
            output_record["clean_image_resolved"] = clean_path.as_posix()
            output_record["image_width"] = width
            output_record["image_height"] = height
            output_record["generation_status"] = "success"
        except Exception as exc:
            output_record["error_message"] = str(exc)

        output_records.append(output_record)

    write_jsonl(output_manifest_path, output_records)
    return output_records
