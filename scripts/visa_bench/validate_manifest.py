#!/usr/bin/env python
"""Validate a VISA-Bench input JSONL manifest."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from visa_bench.schema.sample import validate_record
from visa_bench.utils.io import read_jsonl, resolve_input_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--input-root", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = read_jsonl(args.manifest)
    total = len(records)
    valid = 0
    invalid = 0
    missing_images = 0
    attack_counts: Counter[str] = Counter()
    authority_counts: Counter[str] = Counter()

    for record in records:
        errors = []
        if record.get("_json_error"):
            errors.append(record["_json_error"])
        errors.extend(validate_record(record))

        if not errors and args.input_root:
            image_path = resolve_input_path(str(record["clean_image"]), args.input_root)
            if not image_path.exists():
                missing_images += 1
                errors.append(f"clean image not found: {image_path}")

        if errors:
            invalid += 1
            print(f"line {record.get('_line_no', '?')}: invalid: {'; '.join(errors)}")
        else:
            valid += 1
            attack_counts[str(record["attack_type"])] += 1
            authority_counts[str(record["authority_label"])] += 1

    print("Summary")
    print(f"  total lines: {total}")
    print(f"  valid: {valid}")
    print(f"  invalid: {invalid}")
    print(f"  missing images: {missing_images}")
    print(f"  attack type counts: {dict(sorted(attack_counts.items()))}")
    print(f"  authority label counts: {dict(sorted(authority_counts.items()))}")


if __name__ == "__main__":
    main()
