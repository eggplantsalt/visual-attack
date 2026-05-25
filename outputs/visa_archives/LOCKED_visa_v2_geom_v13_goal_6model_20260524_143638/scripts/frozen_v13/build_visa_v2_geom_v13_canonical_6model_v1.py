import json, re, csv, shutil, subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path("/storage/v-xiangxizheng/zy_workspace/visual-attack")
OUTDIR = ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/canonical_6model_goal_v1"
OUTDIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    {
        "model": "openvla",
        "visual_streams_used": "full",
        "summary_md": ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/openvla_full_v1/openvla_geom_v13_summary_stream_v2.md",
        "summary_csv": ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/openvla_full_v1/openvla_geom_v13_summary_stream_v2.csv",
        "predictions": ROOT / "outputs/visa_v2_openloop_eval_geom_v13/openvla_full_8shard_v1/predictions.jsonl",
    },
    {
        "model": "pi0",
        "visual_streams_used": "full+wrist",
        "summary_md": ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/pi0_bothview_v1/pi0_bothview_geom_v13_summary_stream_v1.md",
        "summary_csv": ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/pi0_bothview_v1/pi0_bothview_geom_v13_summary_stream_v1.csv",
        "predictions": ROOT / "outputs/visa_v2_openloop_eval_geom_v13/pi0_bothview_8shard_v1/predictions.jsonl",
    },
    {
        "model": "pi0_5",
        "visual_streams_used": "full+wrist",
        "summary_md": ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/pi05_bothview_24shard_v1/pi05_bothview_geom_v13_summary_stream_v1.md",
        "summary_csv": ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/pi05_bothview_24shard_v1/pi05_bothview_geom_v13_summary_stream_v1.csv",
        "predictions": ROOT / "outputs/visa_v2_openloop_eval_geom_v13/pi05_bothview_24shard_v1/predictions.jsonl",
    },
    {
        "model": "openvla_oft",
        "visual_streams_used": "full+wrist+proprio",
        "summary_md": ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/openvla_oft_bothview_state_v2_repaired_dot/openvla_oft_bothview_geom_v13_summary_repaired_dot_v3.md",
        "summary_csv": ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/openvla_oft_bothview_state_v2_repaired_dot/openvla_oft_bothview_geom_v13_summary_repaired_dot_v3.csv",
        "predictions": ROOT / "outputs/visa_v2_openloop_eval_geom_v13/openvla_oft_bothview_8shard_state_v2/predictions_repaired_emptylang_dot_v3.jsonl",
    },
    {
        "model": "vla_adapter_pro",
        "visual_streams_used": "full+wrist",
        "summary_md": ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/vla_adapter_pro_bothview_8shard_v1/vla_adapter_pro_bothview_geom_v13_summary_stream_v1.md",
        "summary_csv": ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/vla_adapter_pro_bothview_8shard_v1/vla_adapter_pro_bothview_geom_v13_summary_stream_v1.csv",
        "predictions": ROOT / "outputs/visa_v2_openloop_eval_geom_v13/vla_adapter_pro_bothview_8shard_v1/predictions.jsonl",
    },
    {
        "model": "instructvla",
        "visual_streams_used": "full+wrist",
        "summary_md": ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/instructvla_bothview_v1/instructvla_bothview_geom_v13_summary_stream_v1.md",
        "summary_json": ROOT / "outputs/visa_reports/visa_v2_openloop_geom_v13/instructvla_bothview_v1/instructvla_bothview_geom_v13_summary_stream_v1.json",
        "predictions": ROOT / "outputs/visa_v2_openloop_eval_geom_v13/instructvla_bothview_8shard_v1/predictions.jsonl",
    },
]

def parse_percent(x):
    x = str(x).strip()
    if x.endswith("%"):
        return float(x[:-1])
    v = float(x)
    return v * 100 if v <= 1 else v

def read_overall_from_json(p):
    d = json.loads(p.read_text(encoding="utf-8"))
    o = d["overall"]
    return {
        "valid_pairs": int(o.get("n", d.get("valid_pairs", 0))),
        "CAS@0.05": parse_percent(o["CAS@0.05"]),
        "CAS@0.10": parse_percent(o["CAS@0.10"]),
        "CAS@0.20": parse_percent(o["CAS@0.20"]),
        "mean_L2": float(o["mean_L2"]),
        "pose_L2": float(o["pose_L2"]),
        "xyz_L2": float(o["xyz_L2"]),
        "rot_L2": float(o["rot_L2"]),
        "gripper_abs": float(o["gripper_abs"]),
        "status": d.get("status") or d.get("STATUS") or "OK",
    }

def read_overall_from_md(p):
    txt = p.read_text(encoding="utf-8", errors="replace")
    status = "OK" if re.search(r"STATUS:\s*OK", txt) else "CHECK"
    m = re.search(
        r"\|\s*(?:all\s*\|\s*)?(\d+)\s*\|\s*([\d.]+)%\s*\|\s*([\d.]+)%\s*\|\s*([\d.]+)%\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|",
        txt,
    )
    if not m:
        raise RuntimeError(f"Cannot parse overall table from {p}")
    return {
        "valid_pairs": int(m.group(1)),
        "CAS@0.05": float(m.group(2)),
        "CAS@0.10": float(m.group(3)),
        "CAS@0.20": float(m.group(4)),
        "mean_L2": float(m.group(5)),
        "pose_L2": float(m.group(6)),
        "xyz_L2": float(m.group(7)),
        "rot_L2": float(m.group(8)),
        "gripper_abs": float(m.group(9)),
        "status": status,
    }

def read_overall(spec):
    if spec.get("summary_json") and spec["summary_json"].exists():
        return read_overall_from_json(spec["summary_json"])
    if spec.get("summary_md") and spec["summary_md"].exists():
        return read_overall_from_md(spec["summary_md"])
    raise FileNotFoundError(f"No summary found for {spec['model']}: {spec}")

rows = []
missing = []
for spec in MODELS:
    for key in ["predictions"]:
        if not spec[key].exists():
            missing.append(str(spec[key]))
    if spec.get("summary_md") and not spec["summary_md"].exists():
        if not (spec.get("summary_json") and spec["summary_json"].exists()):
            missing.append(str(spec["summary_md"]))

if missing:
    print("MISSING FILES:")
    for x in missing:
        print(" -", x)
    raise SystemExit("missing canonical inputs")

for spec in MODELS:
    o = read_overall(spec)
    row = {
        "model": spec["model"],
        "suite": "libero_goal",
        "visual_streams_used": spec["visual_streams_used"],
        "valid_pairs": o["valid_pairs"],
        "CAS@0.05": o["CAS@0.05"],
        "CAS@0.10": o["CAS@0.10"],
        "CAS@0.20": o["CAS@0.20"],
        "mean_L2": o["mean_L2"],
        "pose_L2": o["pose_L2"],
        "xyz_L2": o["xyz_L2"],
        "rot_L2": o["rot_L2"],
        "gripper_abs": o["gripper_abs"],
        "status": o["status"],
        "summary": str(spec.get("summary_json") or spec.get("summary_md")),
        "predictions": str(spec["predictions"]),
    }
    rows.append(row)

csv_path = OUTDIR / "visa_v2_geom_v13_canonical_6model_goal_v1.csv"
with csv_path.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

json_path = OUTDIR / "visa_v2_geom_v13_canonical_6model_goal_v1.json"
json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

lines = []
lines.append("# VISA-Bench v13 Canonical 6-Model Goal Open-Loop Summary")
lines.append("")
lines.append("Scope: LIBERO-Goal v13 open-loop paired clean-vs-attack evaluation.")
lines.append("")
lines.append("Canonical rule: each model is evaluated using the visual streams consumed by its runner; dual-view models use full+wrist attacks, and OpenVLA-OFT uses the repaired-dot prediction file.")
lines.append("")
lines.append("| model | visual streams | valid pairs | CAS@0.05 | CAS@0.10 | CAS@0.20 | mean_L2 | pose_L2 | xyz_L2 | rot_L2 | gripper_abs | status |")
lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
for r in rows:
    lines.append(
        f"| {r['model']} | {r['visual_streams_used']} | {r['valid_pairs']} | "
        f"{r['CAS@0.05']:.2f}% | {r['CAS@0.10']:.2f}% | {r['CAS@0.20']:.2f}% | "
        f"{r['mean_L2']:.4f} | {r['pose_L2']:.4f} | {r['xyz_L2']:.4f} | {r['rot_L2']:.4f} | {r['gripper_abs']:.4f} | {r['status']} |"
    )

lines.append("")
lines.append("## Source files")
for r in rows:
    lines.append(f"- {r['model']}: summary=`{r['summary']}`, predictions=`{r['predictions']}`")

md_path = OUTDIR / "visa_v2_geom_v13_canonical_6model_goal_v1.md"
md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(md_path.read_text(encoding="utf-8"))
print("WROTE", csv_path)
print("WROTE", json_path)
