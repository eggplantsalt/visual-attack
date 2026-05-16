# LIBERO Repository Overview for VISA-Bench

This note was created after a read-only investigation of the cloned LIBERO repository at `E:\LIBERO`. No installs, tests, dataset downloads, model downloads, or simulation rollouts were run.

## Current Repository State

- `pwd`: `E:\LIBERO`
- `git status --short`: `?? docs/`
- Working tree is not clean: the `docs/` directory is currently untracked.

## High-Level Structure

- `README.md`: project description, installation commands, dataset download commands, and task/training/evaluation examples.
- `requirements.txt`: pinned runtime dependencies, including `robosuite==1.4.0`, `robomimic==0.2.0`, `bddl==1.0.1`, `hydra-core==1.2.0`, `gym==0.25.2`, and vision / logging packages.
- `setup.py`: installs package `libero`, exposes console scripts for lifelong training/eval and config/template helpers.
- `libero/configs/`: Hydra configuration files for data, training, eval, policies, algorithms, and experiment reproduction.
- `libero/libero/`: core LIBERO benchmark package: assets, BDDL task files, task suites, environments, init states, and utilities.
- `libero/lifelong/`: imitation/lifelong learning datasets, models, algorithms, training, metrics, and evaluation.
- `benchmark_scripts/`: benchmark utility scripts for dataset download, task rendering, suite checking, checksums.
- `scripts/`: dataset conversion, demonstration collection, task/template creation, dataset inspection, and integrity checking.
- `templates/`: scaffolding templates for custom LIBERO tasks/scenes.
- `notebooks/`: notebook-side examples and custom asset examples.
- `images/`: README/project images.
- `docs/`: currently untracked; contains `docs/PROJECT_CONTEXT.md`.

## Main Python Packages

- `libero.libero`: benchmark-facing package. Important entry file: `libero/libero/__init__.py`, which defines `get_libero_path()` and path defaults for `benchmark_root`, `bddl_files`, `init_states`, `datasets`, and `assets`.
- `libero.libero.benchmark`: task-suite registry and task metadata. Main files:
  - `libero/libero/benchmark/__init__.py`
  - `libero/libero/benchmark/libero_suite_task_map.py`
  - `libero/libero/benchmark/mu_creation.py`
- `libero.libero.envs`: robosuite/BDDL environments, task domains, arenas, objects, predicates, regions, robots, wrappers, and vector envs. Main files:
  - `libero/libero/envs/env_wrapper.py`
  - `libero/libero/envs/bddl_base_domain.py`
  - `libero/libero/envs/bddl_utils.py`
  - `libero/libero/envs/problems/*.py`
- `libero.lifelong`: policy training and evaluation code. Main files:
  - `libero/lifelong/main.py`
  - `libero/lifelong/evaluate.py`
  - `libero/lifelong/metric.py`
  - `libero/lifelong/datasets.py`
  - `libero/lifelong/models/*.py`
  - `libero/lifelong/algos/*.py`

## Installation and Dependency Notes

- README recommends Python `3.8.13`, `pip install -r requirements.txt`, then a specific CUDA Torch stack, then `pip install -e .`.
- `setup.py` leaves `install_requires=[]`; dependencies are only in `requirements.txt`.
- Importing `libero.libero` may create/read `~/.libero/config.yaml` and can prompt interactively if no config exists. Avoid casual imports in automation unless the config is already initialized.
- Do not install anything locally for VISA-Bench documentation or scaffolding work unless explicitly requested.

## Task Definitions

- Static BDDL task files live under:
  - `libero/libero/bddl_files/libero_spatial/`
  - `libero/libero/bddl_files/libero_object/`
  - `libero/libero/bddl_files/libero_goal/`
  - `libero/libero/bddl_files/libero_90/`
  - `libero/libero/bddl_files/libero_10/`
- Fixed/pruned initial states live under matching folders in `libero/libero/init_files/`.
- Suite-to-task-name mapping is in `libero/libero/benchmark/libero_suite_task_map.py`.
- Suite classes and `Task` metadata are in `libero/libero/benchmark/__init__.py`.
- Programmatic task/BDDL generation helpers are in:
  - `libero/libero/utils/task_generation_utils.py`
  - `libero/libero/utils/bddl_generation_utils.py`
  - `scripts/create_libero_task_example.py`
  - `templates/problem_class_template.py`
  - `templates/scene_template.xml`

## Environment Creation and Reset/Step Logic

- Environment wrapper entry point: `libero/libero/envs/env_wrapper.py`.
- `ControlEnv` parses a BDDL file, looks up `TASK_MAPPING`, creates the underlying robosuite environment, and exposes `reset()`, `step()`, `set_init_state()`, `regenerate_obs_from_state()`, `get_sim_state()`, and `close()`.
- `OffScreenRenderEnv` is the main wrapper used for evaluation and rendering; it forces `has_renderer=False` and `has_offscreen_renderer=True`.
- Base robosuite domain: `libero/libero/envs/bddl_base_domain.py`.
- `BDDLBaseDomain` extends `SingleArmEnv`, parses BDDL, loads arena/assets/objects/sites, sets cameras, handles object placement, implements `step()`, `_reset_internal()`, `_post_action()`, `_post_process()`, and sparse success reward wiring.
- Concrete domain/problem classes are in `libero/libero/envs/problems/`.

## Image Observations and Camera Rendering

- Camera configuration enters through `ControlEnv` / `BDDLBaseDomain` args: `camera_names`, `camera_heights`, `camera_widths`, `camera_depths`, `camera_segmentations`, `render_camera`.
- Default wrapper cameras in `libero/libero/envs/env_wrapper.py`: `agentview` and `robot0_eye_in_hand`, at `128x128`.
- Domain camera poses are set in `_setup_camera()` methods:
  - `libero/libero/envs/bddl_base_domain.py`
  - `libero/libero/envs/problems/libero_tabletop_manipulation.py`
  - `libero/libero/envs/problems/libero_kitchen_tabletop_manipulation.py`
  - `libero/libero/envs/problems/libero_living_room_tabletop_manipulation.py`
  - `libero/libero/envs/problems/libero_study_tabletop_manipulation.py`
  - `libero/libero/envs/problems/libero_coffee_table_manipulation.py`
  - `libero/libero/envs/problems/libero_floor_manipulation.py`
- Training/eval config maps environment image keys to dataset/model keys in `libero/configs/data/default.yaml`:
  - `agentview_rgb -> agentview_image`
  - `eye_in_hand_rgb -> robot0_eye_in_hand_image`
- Video helper uses image obs in `libero/libero/utils/video_utils.py`.

## Dataset, Demo Loading, and Replay Logic

- Dataset download script: `benchmark_scripts/download_libero_datasets.py`.
- Demonstration collection scripts:
  - `scripts/collect_demonstration.py`
  - `scripts/libero_100_collect_demonstrations.py`
- Raw demo to learning dataset conversion: `scripts/create_dataset.py`.
  - Reads HDF5 demos, replays actions/states, captures `agentview_image` and `robot0_eye_in_hand_image`, and writes `agentview_rgb` / `eye_in_hand_rgb`.
- Dataset inspection / checking:
  - `scripts/get_dataset_info.py`
  - `scripts/check_dataset_integrity.py`
- Training dataset loader: `libero/lifelong/datasets.py`, especially `get_dataset()`, `SequenceVLDataset`, and `GroupedTaskDataset`.

## Evaluation Scripts

- Main training loop with on-the-fly eval: `libero/lifelong/main.py`.
- Standalone policy evaluation: `libero/lifelong/evaluate.py`.
- Shared evaluation helpers: `libero/lifelong/metric.py`.
  - `evaluate_one_task_success()` creates `OffScreenRenderEnv`, loads fixed init states, rolls out policies, and computes success.
  - `raw_obs_to_tensor_obs()` maps raw env observations into policy input tensors.
- Rendering utility: `benchmark_scripts/render_single_task.py`.
- Suite checking utility: `benchmark_scripts/check_task_suites.py`.

## Policies

- Policy registry and base class: `libero/lifelong/models/base_policy.py`.
- Existing policy implementations:
  - `libero/lifelong/models/bc_rnn_policy.py`
  - `libero/lifelong/models/bc_transformer_policy.py`
  - `libero/lifelong/models/bc_vilt_policy.py`
- Policy configs:
  - `libero/configs/policy/bc_rnn_policy.yaml`
  - `libero/configs/policy/bc_transformer_policy.yaml`
  - `libero/configs/policy/bc_vilt_policy.yaml`

## Safe VISA-Bench Extension Points

- Add a new top-level package: `visa_bench/`.
  - This is the safest place for open-loop image attack generation, schemas, metrics, adapters, and optional LIBERO integration helpers.
- Add scripts under `scripts/visa_bench/`.
  - Keep CLI tools separate from LIBERO's existing scripts and do not alter existing entry points.
- Add documentation under `docs/visa_bench/`.
  - Current `docs/` is untracked, so coordinate with git ownership before assuming it is committed.
- For open-loop work, operate on image files and manifests outside LIBERO internals.
- For closed-loop work later, prefer wrapper/adaptor code around `OffScreenRenderEnv` and BDDL/init-state paths rather than editing `libero/libero/envs/*`.
- For new benchmark task suites later, prefer external metadata/manifests that reference existing LIBERO BDDL files, or external generated BDDL files loaded via explicit paths, instead of changing `libero/libero/benchmark/libero_suite_task_map.py`.
- For visual overlays on observations, prefer post-processing obs dictionaries in a VISA-Bench wrapper before policy input, or generating attacked image datasets offline.

## Recommended New Package Location

Create `visa_bench/` at the repository root, parallel to `libero/`, with scripts in `scripts/visa_bench/`.

This preserves original LIBERO behavior and avoids changing `setup.py` until packaging is actually needed. If installable packaging is needed later, document the reason before touching `setup.py`.

## Candidate Files to Inspect Next

- `libero/libero/envs/problems/*.py`: exact object loading, site/region setup, and camera poses for closed-loop visual attack placement.
- `libero/libero/envs/objects/*.py`: object XML wrappers and whether a paper/note/sign object can be represented cleanly.
- `libero/libero/envs/arenas/*.py`: arena XML loading and scene composition.
- `libero/libero/assets/scenes/*.xml`: scene/camera/static geometry details.
- `libero/libero/utils/mu_utils.py`: scene template registry and scene metadata.
- `scripts/create_dataset.py`: best source for image extraction and replay conventions.
- `libero/lifelong/metric.py`: best source for closed-loop rollout/evaluation wrapper design.
- `libero/configs/data/default.yaml`: observation key conventions and image sizes.
- `benchmark_scripts/render_single_task.py`: lightweight rendering reference, but do not run until simulation dependencies are available.

## Risks and Uncertainty

- Importing `libero.libero` may have side effects through `~/.libero/config.yaml` initialization.
- Simulation depends on robosuite, MuJoCo, rendering backends, GPU/EGL setup, and local datasets; local availability was not verified.
- Dataset files are not present in the inspected top-level tree unless stored elsewhere through `~/.libero/config.yaml`.
- Closed-loop visual attacks may require new MuJoCo assets or generated BDDL files; this should be done outside original LIBERO source where possible.
- `docs/` is untracked, so documentation ownership should be clarified before committing.
