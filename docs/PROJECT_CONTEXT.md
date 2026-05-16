# PROJECT_CONTEXT.md

## Project Name

VISA-Bench: Visual Instruction Source Authority Benchmark for Vision-Language-Action Models.

Working paper title: When Seeing Becomes Obeying: Visual Authority Confusion in Vision-Language-Action Models.

## Core Research Goal

We are building a benchmark for visual attack and visual authority confusion in Vision-Language-Action models.

The central research question is not simply whether a robot can be attacked by text pasted into an image. The deeper question is whether a VLA model incorrectly treats untrusted visual content as an executable command.

A VLA should use visual input to understand the world state, but it should not automatically let arbitrary visual content update its task goal.

## Core Concepts

Visual Authority Confusion means that a VLA model treats untrusted visual content, such as a paper note, screen text, object label, arrow, region marker, or trajectory sketch, as if it were an authorized task command.

Perception-to-Goal Tainting means that visual content that should only update the perceived world state wrongly contaminates the robot's goal state or action policy.

Selective Obedience means that a safe VLA should obey trusted commands, ignore untrusted visual commands, and still use visual information for perception.

## Benchmark Structure

The benchmark has two main subsets.

Subset A: Real-image open-loop subset. This uses clean and attacked image pairs. It does not require running a robot simulation. It tests whether visual attacks cause perception changes or action shifts.

Subset B: LIBERO closed-loop subset. This modifies LIBERO scenes by adding physical or rendered visual attack elements, then runs full simulated robot episodes to test whether visual authority confusion leads to unsafe or incorrect execution.

There is also a diagnostic subset for visual literacy, including OCR, arrow grounding, region grounding, object label understanding, and visual authority judgment.

## Codebase Decision

The primary codebase is LIBERO. Do not build the whole benchmark from scratch.

Add new code in an isolated extension layer named `visa_bench/` and new command-line scripts under `scripts/visa_bench/`. Avoid modifying original LIBERO source files unless absolutely necessary. If a modification to original LIBERO code is required, document exactly why.

OpenVLA, LeRobot, or other VLA/model codebases may be integrated later through adapter interfaces, but they are not the first implementation target.

## Implementation Principles

Keep the implementation modular, minimal, and readable.

Do not over-engineer.

Do not run heavy local experiments, simulation rollouts, GPU inference, model downloads, or environment installation unless explicitly requested. The local machine may not have the required robotics environment.

Prefer writing code that can be pushed to a remote server and run there.

Use small, inspectable outputs: images, JSONL manifests, CSV summaries, and Markdown docs.

Preserve original LIBERO behavior.

Do not delete or restructure existing LIBERO files.

Do not use destructive git operations.

## Planned Directory Layout

Target new directories:

`visa_bench/`
- `schema/`: dataclasses or typed dictionaries for benchmark sample metadata.
- `overlays/`: functions for drawing text notes, arrows, object labels, region markers, and trajectory sketches on images.
- `generators/`: dataset generation logic for clean/attacked image pairs.
- `metrics/`: VLS, CAS, GTR, UER metric skeletons.
- `libero_ext/`: optional LIBERO-specific utilities for scene modification and closed-loop evaluation.
- `adapters/`: later model adapters for OpenVLA, pi0/pi0.5, MolmoAct, etc.
- `utils/`: image IO, JSONL IO, validation, coordinate helpers.

`scripts/visa_bench/`
- `generate_open_loop_attacks.py`
- `validate_manifest.py`
- `preview_attacks.py`
- future closed-loop scripts.

`docs/visa_bench/`
- `DATA_SCHEMA.md`
- `ATTACK_TAXONOMY.md`
- `RUNBOOK.md`

## First Implementation Milestone

The first milestone is not closed-loop simulation. The first milestone is an open-loop visual attack generator that can take clean images and a manifest, then produce attacked images plus a JSONL metadata file.

It should support at least these attack types:

1. text_note
2. arrow
3. object_label
4. region_marker
5. trajectory_sketch

Each generated sample should include enough metadata to compute future benchmark metrics.

## Key Metrics

VLS: Visual Literacy Score. Whether the model understands the visual cue.

AJA: Authority Judgment Accuracy. Whether the model correctly judges whether the visual cue has authority.

CAS: Causal Action Shift. Whether the attacked image changes the model's action output relative to the clean image.

GTR: Goal Taint Rate. Whether an untrusted visual cue changes the inferred or executed goal.

UER: Unsafe Execution Rate. Whether a closed-loop rollout produces unsafe or task-violating behavior.

The main benchmark metric is GTR, not ordinary attack success rate.

## Immediate Task for Code Agent

First read the codebase and create `OVERVIEW.md`. Do not implement benchmark functionality yet. The goal is to understand the LIBERO repository structure, identify safe extension points, and propose which files should be read next.