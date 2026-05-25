#!/usr/bin/env bash
set -euo pipefail

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate /tmp/conda_env/instructvla_libero || conda activate instructvla_libero

cd /storage/v-xiangxizheng/zy_workspace/visual-attack
export PYTHONPATH="$PWD:${PYTHONPATH:-}"
export TOKENIZERS_PARALLELISM=false
export TF_CPP_MIN_LOG_LEVEL=3

MANIFEST="outputs/visa_v2_ladder_goal_core_geom_v13/manifests/visa_ladder_v2_goal_openloop_manifest_geom_v13_canonical_no_multilingual.jsonl"
OUTROOT="outputs/visa_v2_openloop_eval_geom_v13/instructvla_bothview_8shard_v1"
SHARDDIR="$OUTROOT/manifest_shards"
PREDDIR="$OUTROOT/prediction_shards"
SMOKE="$OUTROOT/manifest_smoke32.jsonl"
SMOKE_OUT="$OUTROOT/predictions_smoke32.jsonl"

mkdir -p "$OUTROOT" "$SHARDDIR" "$PREDDIR" logs

echo "===== INPUT CHECK ====="
test -s "$MANIFEST"
wc -l "$MANIFEST"

echo
echo "===== MANIFEST FIRST ROW ====="
python - <<'PY'
import json
from pathlib import Path
p = Path("outputs/visa_v2_ladder_goal_core_geom_v13/manifests/visa_ladder_v2_goal_openloop_manifest_geom_v13_canonical_no_multilingual.jsonl")
r = json.loads(next(p.open()))
for k in ["action_eval_id","pair_id","image_kind","attack_family","attack_form","artifact_position","task_instruction","full_image_path","wrist_image_path"]:
    print(k, "=", r.get(k))
print("full_exists =", Path(r["full_image_path"]).exists())
print("wrist_exists =", Path(r["wrist_image_path"]).exists())
PY

echo
echo "===== MAKE SMOKE32 ====="
head -n 32 "$MANIFEST" > "$SMOKE"
wc -l "$SMOKE"

echo
echo "===== RUN SMOKE32 ====="
rm -f "$SMOKE_OUT"
export CUDA_VISIBLE_DEVICES=0
export MASTER_ADDR=127.0.0.1
export MASTER_PORT=45731
export WORLD_SIZE=1
export RANK=0
export LOCAL_RANK=0

python scripts/visa_bench/run_instructvla_predict_v0_2.py \
  --suite libero_goal \
  --input-jsonl "$SMOKE" \
  --output-jsonl "$SMOKE_OUT" \
  --progress-every 1 \
  2>&1 | tee logs/instructvla_geom_v13_smoke32_v1.log

echo
echo "===== SMOKE AUDIT ====="
python - <<'PY'
import json, sys
from pathlib import Path

p = Path("outputs/visa_v2_openloop_eval_geom_v13/instructvla_bothview_8shard_v1/predictions_smoke32.jsonl")
rows = [json.loads(x) for x in p.open() if x.strip()]
ok = []
bad = []
for r in rows:
    a = r.get("action") or r.get("predicted_action")
    if r.get("prediction_status") == "success" and isinstance(a, list) and len(a) >= 7:
        ok.append(r)
    else:
        bad.append(r)

print("rows =", len(rows))
print("ok =", len(ok))
print("bad =", len(bad))
if ok:
    print("first_ok_action_dim =", len(ok[0].get("action") or ok[0].get("predicted_action")))
    print("first_ok_action =", (ok[0].get("action") or ok[0].get("predicted_action"))[:7])
if bad:
    print("first_bad =", {k: bad[0].get(k) for k in ["action_eval_id","prediction_status","error","error_message"]})
    sys.exit("SMOKE FAILED")
if len(ok) != 32:
    sys.exit("SMOKE DID NOT PRODUCE 32 VALID ACTIONS")
print("SMOKE OK")
PY

echo
echo "===== SPLIT 8 SHARDS ====="
python - <<'PY'
from pathlib import Path

manifest = Path("outputs/visa_v2_ladder_goal_core_geom_v13/manifests/visa_ladder_v2_goal_openloop_manifest_geom_v13_canonical_no_multilingual.jsonl")
outdir = Path("outputs/visa_v2_openloop_eval_geom_v13/instructvla_bothview_8shard_v1/manifest_shards")
outdir.mkdir(parents=True, exist_ok=True)

lines = manifest.read_text(encoding="utf-8").splitlines()
n = len(lines)
assert n == 70000, n
num = 8
base = n // num
rem = n % num

start = 0
for sid in range(num):
    cnt = base + (1 if sid < rem else 0)
    shard = lines[start:start+cnt]
    p = outdir / f"manifest_{sid:03d}.jsonl"
    p.write_text("\n".join(shard) + "\n", encoding="utf-8")
    print(f"shard {sid}: {len(shard)} rows -> {p}")
    start += cnt
PY

echo
echo "===== WRITE WORKER SCRIPT ====="
cat > /tmp/instructvla_geom_v13_worker_v1.sh <<'WSH'
#!/usr/bin/env bash
set -euo pipefail

SID="$1"
GPU="$2"
PORT="$3"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate /tmp/conda_env/instructvla_libero || conda activate instructvla_libero

cd /storage/v-xiangxizheng/zy_workspace/visual-attack
export PYTHONPATH="$PWD:${PYTHONPATH:-}"
export TOKENIZERS_PARALLELISM=false
export TF_CPP_MIN_LOG_LEVEL=3

export CUDA_VISIBLE_DEVICES="$GPU"
export MASTER_ADDR=127.0.0.1
export MASTER_PORT="$PORT"
export WORLD_SIZE=1
export RANK=0
export LOCAL_RANK=0

IN="outputs/visa_v2_openloop_eval_geom_v13/instructvla_bothview_8shard_v1/manifest_shards/manifest_$(printf "%03d" "$SID").jsonl"
OUT="outputs/visa_v2_openloop_eval_geom_v13/instructvla_bothview_8shard_v1/prediction_shards/predictions_$(printf "%03d" "$SID").jsonl"
LOG="logs/instructvla_geom_v13_shard_$(printf "%03d" "$SID").log"

echo "===== START shard=$SID gpu=$GPU port=$PORT ====="
date
wc -l "$IN"

python scripts/visa_bench/run_instructvla_predict_v0_2.py \
  --suite libero_goal \
  --input-jsonl "$IN" \
  --output-jsonl "$OUT" \
  --progress-every 20 \
  2>&1 | tee "$LOG"

echo "===== DONE shard=$SID ====="
date
wc -l "$OUT"
WSH
chmod +x /tmp/instructvla_geom_v13_worker_v1.sh

echo
echo "===== LAUNCH 8GPU TMUX ====="
tmux kill-session -t instructvla_geom_v13 2>/dev/null || true
tmux new -d -s instructvla_geom_v13 "cd /storage/v-xiangxizheng/zy_workspace/visual-attack && bash -lc '
for sid in 0 1 2 3 4 5 6 7; do
  gpu=\$sid
  port=\$((45800 + sid))
  /tmp/instructvla_geom_v13_worker_v1.sh \$sid \$gpu \$port &
done
wait
echo ===== ALL INSTRUCTVLA SHARDS DONE =====
date
' 2>&1 | tee logs/instructvla_geom_v13_8gpu_master.log"

echo "started tmux session: instructvla_geom_v13"
echo
echo "Check progress with:"
echo "  tmux attach -t instructvla_geom_v13"
echo "or:"
echo "  for sid in 0 1 2 3 4 5 6 7; do f=\"$PREDDIR/predictions_\$(printf \"%03d\" \$sid).jsonl\"; echo shard \$sid: \$(test -f \"\$f\" && wc -l < \"\$f\" || echo 0) / 8750; done"
