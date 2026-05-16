#!/usr/bin/env python
"""Build a VISA-Bench open-loop input manifest from images or scene metadata."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from visa_bench.generators.manifest_builder import build_open_loop_manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-root", required=True)
    parser.add_argument("--output-manifest", required=True)
    parser.add_argument("--scene-manifest", default=None)
    parser.add_argument("--attack-types", default=None, help="Comma-separated attack types.")
    parser.add_argument("--authority-label", default="untrusted")
    parser.add_argument("--visual-source", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_open_loop_manifest(
        image_root=args.image_root,
        output_manifest=args.output_manifest,
        scene_manifest=args.scene_manifest,
        attack_types=args.attack_types,
        authority_label=args.authority_label,
        visual_source=args.visual_source,
        limit=args.limit,
        seed=args.seed,
        overwrite=args.overwrite,
    )

    print("Manifest builder summary")
    print(f"  clean scenes: {summary['num_clean_scenes']}")
    print(f"  generated attack records: {summary['num_attack_records']}")
    print(f"  attack type counts: {dict(sorted(summary['attack_type_counts'].items()))}")
    print(f"  output path: {summary['output_manifest']}")


if __name__ == "__main__":
    main()
