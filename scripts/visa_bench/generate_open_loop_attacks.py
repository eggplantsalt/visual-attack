#!/usr/bin/env python
"""Generate open-loop VISA-Bench attacked images from a JSONL manifest."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from visa_bench.generators.open_loop_generator import generate_open_loop_attacks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Input JSONL manifest.")
    parser.add_argument("--input-root", required=True, help="Root directory for clean images.")
    parser.add_argument("--output-root", required=True, help="Output directory for images and manifest.")
    parser.add_argument("--output-manifest", default=None, help="Optional output JSONL path.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing attacked images.")
    parser.add_argument("--limit", type=int, default=None, help="Optional small-batch limit.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = generate_open_loop_attacks(
        manifest=args.manifest,
        input_root=args.input_root,
        output_root=args.output_root,
        output_manifest=args.output_manifest,
        overwrite=args.overwrite,
        limit=args.limit,
    )
    successes = sum(1 for record in records if record.get("generation_status") == "success")
    failures = len(records) - successes
    manifest_path = args.output_manifest or str(Path(args.output_root) / "manifest_attacked.jsonl")
    print(f"Generated {successes} succeeded, {failures} failed.")
    print(f"Output manifest: {manifest_path}")


if __name__ == "__main__":
    main()
