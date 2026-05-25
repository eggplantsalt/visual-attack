# VISA-Bench v13 Canonical 6-Model Goal Open-Loop Summary

Scope: LIBERO-Goal v13 open-loop paired clean-vs-attack evaluation.

Canonical rule: each model is evaluated using the visual streams consumed by its runner; dual-view models use full+wrist attacks, and OpenVLA-OFT uses the repaired-dot prediction file.

| model | visual streams | valid pairs | CAS@0.05 | CAS@0.10 | CAS@0.20 | mean_L2 | pose_L2 | xyz_L2 | rot_L2 | gripper_abs | status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| openvla | full | 35000 | 87.37% | 77.48% | 58.77% | 0.3651 | 0.3154 | 0.2945 | 0.0653 | 0.0704 | OK |
| pi0 | full+wrist | 35000 | 99.86% | 95.29% | 64.45% | 0.3874 | 0.2717 | 0.2427 | 0.1009 | 0.1436 | OK |
| pi0_5 | full+wrist | 35000 | 82.48% | 51.31% | 21.71% | 0.1813 | 0.1435 | 0.1377 | 0.0281 | 0.0456 | OK |
| openvla_oft | full+wrist+proprio | 35000 | 59.21% | 28.22% | 8.71% | 0.0940 | 0.0835 | 0.0812 | 0.0143 | 0.0164 | OK |
| vla_adapter_pro | full+wrist | 35000 | 77.73% | 46.13% | 18.37% | 0.1395 | 0.1239 | 0.1203 | 0.0224 | 0.0319 | OK |
| instructvla | full+wrist | 35000 | 91.67% | 66.90% | 33.99% | 0.2346 | 0.1907 | 0.1848 | 0.0320 | 0.0610 | OK |

## Source files
- openvla: summary=`/storage/v-xiangxizheng/zy_workspace/visual-attack/outputs/visa_reports/visa_v2_openloop_geom_v13/openvla_full_v1/openvla_geom_v13_summary_stream_v2.md`, predictions=`/storage/v-xiangxizheng/zy_workspace/visual-attack/outputs/visa_v2_openloop_eval_geom_v13/openvla_full_8shard_v1/predictions.jsonl`
- pi0: summary=`/storage/v-xiangxizheng/zy_workspace/visual-attack/outputs/visa_reports/visa_v2_openloop_geom_v13/pi0_bothview_v1/pi0_bothview_geom_v13_summary_stream_v1.md`, predictions=`/storage/v-xiangxizheng/zy_workspace/visual-attack/outputs/visa_v2_openloop_eval_geom_v13/pi0_bothview_8shard_v1/predictions.jsonl`
- pi0_5: summary=`/storage/v-xiangxizheng/zy_workspace/visual-attack/outputs/visa_reports/visa_v2_openloop_geom_v13/pi05_bothview_24shard_v1/pi05_bothview_geom_v13_summary_stream_v1.md`, predictions=`/storage/v-xiangxizheng/zy_workspace/visual-attack/outputs/visa_v2_openloop_eval_geom_v13/pi05_bothview_24shard_v1/predictions.jsonl`
- openvla_oft: summary=`/storage/v-xiangxizheng/zy_workspace/visual-attack/outputs/visa_reports/visa_v2_openloop_geom_v13/openvla_oft_bothview_state_v2_repaired_dot/openvla_oft_bothview_geom_v13_summary_repaired_dot_v3.md`, predictions=`/storage/v-xiangxizheng/zy_workspace/visual-attack/outputs/visa_v2_openloop_eval_geom_v13/openvla_oft_bothview_8shard_state_v2/predictions_repaired_emptylang_dot_v3.jsonl`
- vla_adapter_pro: summary=`/storage/v-xiangxizheng/zy_workspace/visual-attack/outputs/visa_reports/visa_v2_openloop_geom_v13/vla_adapter_pro_bothview_8shard_v1/vla_adapter_pro_bothview_geom_v13_summary_stream_v1.md`, predictions=`/storage/v-xiangxizheng/zy_workspace/visual-attack/outputs/visa_v2_openloop_eval_geom_v13/vla_adapter_pro_bothview_8shard_v1/predictions.jsonl`
- instructvla: summary=`/storage/v-xiangxizheng/zy_workspace/visual-attack/outputs/visa_reports/visa_v2_openloop_geom_v13/instructvla_bothview_v1/instructvla_bothview_geom_v13_summary_stream_v1.json`, predictions=`/storage/v-xiangxizheng/zy_workspace/visual-attack/outputs/visa_v2_openloop_eval_geom_v13/instructvla_bothview_8shard_v1/predictions.jsonl`
