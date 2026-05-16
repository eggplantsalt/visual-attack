# VISA-Bench Open-Loop Runbook

This milestone works only with image files and JSONL metadata. It does not require LIBERO simulation, robosuite, MuJoCo, torch, GPU inference, model downloads, or datasets beyond your own clean images.

## Validate An Input Manifest

```bash
python scripts/visa_bench/validate_manifest.py \
  --manifest data/visa_input.jsonl \
  --input-root data/images
```

The validator checks required fields, enum values, optional coordinate field shapes, and clean image existence when `--input-root` is provided.

## Generate Attacked Images

```bash
python scripts/visa_bench/generate_open_loop_attacks.py \
  --manifest data/visa_input.jsonl \
  --input-root data/images \
  --output-root outputs/visa_open_loop \
  --overwrite
```

Generated images are written under:

```text
outputs/visa_open_loop/images/
```

The default output manifest is:

```text
outputs/visa_open_loop/manifest_attacked.jsonl
```

Use `--limit 10` for a small debugging batch.

## Preview Results

```bash
python scripts/visa_bench/preview_attacks.py \
  --manifest outputs/visa_open_loop/manifest_attacked.jsonl \
  --input-root data/images \
  --output-root outputs/visa_open_loop \
  --preview-out outputs/visa_open_loop/preview.png \
  --limit 25 \
  --thumb-size 192
```

The preview grid shows clean and attacked images side by side with sample labels.

## Notes

- Coordinates are normalized floats in `[0, 1]`.
- Missing coordinates use deterministic defaults.
- Per-sample generator failures are recorded in the output JSONL and do not stop the full batch.
- This package intentionally does not import LIBERO or modify original LIBERO files.
