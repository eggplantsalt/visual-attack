"""I/O helpers for JSONL manifests and paths."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def ensure_dir(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                records.append(
                    {
                        "_line_no": line_no,
                        "_json_error": f"{exc.msg} at column {exc.colno}",
                    }
                )
                continue
            if isinstance(record, dict):
                record.setdefault("_line_no", line_no)
                records.append(record)
            else:
                records.append(
                    {
                        "_line_no": line_no,
                        "_json_error": "line must be a JSON object",
                    }
                )
    return records


def write_jsonl(path: str | Path, records: Iterable[dict[str, Any]]) -> None:
    output_path = Path(path)
    ensure_dir(output_path.parent)
    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def resolve_input_path(path_value: str, input_root: str | Path | None = None) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path.resolve()
    if input_root is not None:
        candidate = Path(input_root) / path
        if candidate.exists():
            return candidate.resolve()
    return (Path.cwd() / path).resolve()


def relative_to_root(path: str | Path, root: str | Path) -> str:
    path_obj = Path(path).resolve()
    root_obj = Path(root).resolve()
    try:
        return path_obj.relative_to(root_obj).as_posix()
    except ValueError:
        return path_obj.as_posix()


def safe_output_stem(record: dict[str, Any], index: int) -> str:
    raw = str(record.get("output_name") or record.get("sample_id") or f"sample_{index:06d}")
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in raw)
    return safe.strip("._") or f"sample_{index:06d}"
