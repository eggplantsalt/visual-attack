#!/usr/bin/env bash
set -euo pipefail

cd /storage/v-xiangxizheng/zy_workspace/visual-attack

MANIFEST="outputs/visa_v2_ladder_goal_core_geom_v13/manifests/visa_ladder_v2_goal_openloop_manifest_geom_v13_canonical_no_multilingual.jsonl"
RUNNER="scripts/visa_bench/run_vla_adapter_pro_bothview_worker_geom_v13.py"
OUTROOT="outputs/visa_v2_openloop_eval_geom_v13/vla_adapter_pro_bothview_8shard_v1"
SHARDDIR="$OUTROOT/shards"
PREDIR="$OUTROOT/prediction_shards"
LOGDIR="$OUTROOT/logs"

mkdir -p "$SHARDDIR" "$PREDIR" "$LOGDIR" logs

echo "===== VLA-ADAPTER-PRO BOTHVIEW V13 FULL8 START ====="
date
echo "MANIFEST=$MANIFEST"
echo "RUNNER=$RUNNER"
echo "OUTROOT=$OUTROOT"
wc -l "$MANIFEST"

echo
echo "===== RUNNER CHECK ====="
grep -nE 'num_images_in_input|full_path|wrist_path|wrist_image|visual_input_attacked|image_preprocess' "$RUNNER" | sed -n '1,120p'

echo
echo "===== MAKE 8 CONTIGUOUS SHARDS ====="
rm -f "$SHARDDIR"/manifest_*.jsonl "$PREDIR"/predictions_*.jsonl
python - <<'PY'
from pathlib import Path
import math

manifest = Path("outputs/visa_v2_ladder_goal_core_geom_v13/manifests/visa_ladder_v2_goal_openloop_manifest_geom_v13_canonical_no_multilingual.jsonl")
shard_dir = Path("outputs/visa_v2_openloop_eval_geom_v13/vla_adapter_pro_bothview_8shard_v1/shards")
shard_dir.mkdir(parents=True, exist_ok=True)

rows = [x for x in manifest.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()]
assert len(rows) == 70000, len(rows)

n = 8
chunk = math.ceil(len(rows) / n)
for sid in range(n):
    part = rows[sid * chunk:(sid + 1) * chunk]
    out = shard_dir / f"manifest_{sid:03d}.jsonl"
    out.write_text("\n".join(part) + ("\n" if part else ""), encoding="utf-8")
    print(f"shard {sid}: {len(part)} rows -> {out}")
PY

echo
echo "===== LAUNCH 8 WORKERS ====="
for sid in 0 1 2 3 4 5 6 7; do
  (
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate /tmp/conda_env/visa-vla-adapter || conda activate visa-vla-adapter

    cd /storage/v-xiangxizheng/zy_workspace/visual-attack
    export PYTHONPATH="$PWD:$PWD/third_party/VLA-Adapter:${PYTHONPATH:-}"
    export TOKENIZERS_PARALLELISM=false
    export TF_CPP_MIN_LOG_LEVEL=3

    export CUDA_VISIBLE_DEVICES="$sid"
    export MASTER_ADDR=127.0.0.1
    export MASTER_PORT="$((39750 + sid))"
    export WORLD_SIZE=1
    export RANK=0
    export LOCAL_RANK=0

    shard="$SHARDDIR/manifest_$(printf '%03d' "$sid").jsonl"
    out="$PREDIR/predictions_$(printf '%03d' "$sid").jsonl"
    log="$LOGDIR/worker_$(printf '%03d' "$sid").log"

    echo "===== shard $sid start gpu=$sid $(date) ====="
    python "$RUNNER" \
      --suite libero_goal \
      --shard "$shard" \
      --out "$out" \
      --worker-id "vla_adapter_pro_bothview_v13_worker_${sid}" \
      2>&1 | tee "$log"
    echo "===== shard $sid done $(date) ====="
  ) &
  sleep 6
done

wait

echo
echo "===== SHARD AUDIT ====="
TOTAL=0
BAD=0
for sid in 0 1 2 3 4 5 6 7; do
  shard="$SHARDDIR/manifest_$(printf '%03d' "$sid").jsonl"
  out="$PREDIR/predictions_$(printf '%03d' "$sid").jsonl"
  exp=$(wc -l < "$shard" | tr -d ' ')
  got=$(test -f "$out" && wc -l < "$out" | tr -d ' ' || echo 0)
  TOTAL=$((TOTAL + got))
  echo "shard $sid: $got / $exp"
  if [ "$got" != "$exp" ]; then BAD=1; fi
done
echo "TOTAL=$TOTAL / 70000"

if [ "$BAD" != "0" ] || [ "$TOTAL" != "70000" ]; then
  echo "SHARD AUDIT FAILED"
  exit 2
fi

echo
echo "===== MERGE ====="
cat "$PREDIR"/predictions_*.jsonl > "$OUTROOT/predictions.jsonl.tmp"
mv "$OUTROOT/predictions.jsonl.tmp" "$OUTROOT/predictions.jsonl"
wc -l "$OUTROOT/predictions.jsonl"

echo
echo "===== FINAL ACTION AUDIT ====="
python - <<'PY'
import json
from pathlib import Path

p = Path("outputs/visa_v2_openloop_eval_geom_v13/vla_adapter_pro_bothview_8shard_v1/predictions.jsonl")
rows = ok = bad = 0
first_bad = None

def get_action(r):
    for k in ["action", "predicted_action", "model_action", "raw_action", "actions"]:
        a = r.get(k)
        if isinstance(a, list) and len(a) >= 7:
            return a[:7]
    return None

for line in p.open("r", encoding="utf-8", errors="replace"):
    if not line.strip():
        continue
    rows += 1
    r = json.loads(line)
    if get_action(r) is not None and not r.get("error_message") and r.get("success", True) is not False:
        ok += 1
    else:
        bad += 1
        if first_bad is None:
            first_bad = {k: r.get(k) for k in ["action_eval_id", "pair_id", "image_kind", "success", "error", "error_message"]}

print("rows =", rows)
print("ok_with_action =", ok)
print("bad =", bad)
print("first_bad =", first_bad)

if rows != 70000 or ok != 70000 or bad != 0:
    raise SystemExit("FINAL ACTION AUDIT FAILED")
print("FINAL_ACTION_AUDIT_OK=1")
PY

echo
echo "===== VLA-ADAPTER-PRO BOTHVIEW V13 FULL8 DONE ====="
date
