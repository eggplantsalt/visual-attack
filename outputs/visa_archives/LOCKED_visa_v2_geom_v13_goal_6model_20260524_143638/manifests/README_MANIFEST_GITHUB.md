# Manifest storage note

The raw v13 manifest JSONL is intentionally not committed directly because it is larger than GitHub's 100 MiB single-file limit.

Committed here:
- visa_ladder_v2_goal_openloop_manifest_geom_v13_canonical_no_multilingual.jsonl.gz
- manifest_raw_sha256.txt
- manifest_raw_line_count.txt

Raw local manifest path before compression:
- outputs/visa_archives/LOCKED_visa_v2_geom_v13_goal_6model_20260524_143638/manifests/visa_ladder_v2_goal_openloop_manifest_geom_v13_canonical_no_multilingual.jsonl

To restore:
```bash
gzip -dk visa_ladder_v2_goal_openloop_manifest_geom_v13_canonical_no_multilingual.jsonl.gz
sha256sum -c manifest_raw_sha256.txt
```
