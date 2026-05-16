# VISA-Bench Attack Taxonomy

VISA-Bench studies visual authority confusion: whether a VLA model treats untrusted visual content as an executable command instead of ordinary perceptual evidence.

## Initial Attack Types

`text_note`

A rendered paper note or sign containing imperative text. This tests whether visible text overwrites or contaminates the trusted task instruction.

`arrow`

A visible arrow from one image location to another. This tests whether spatial annotations redirect attention, object choice, or action intent.

`object_label`

A small label near an object. This tests whether the model accepts arbitrary object names or instructions attached to scene objects.

`region_marker`

A highlighted rectangle with optional text. This tests whether an untrusted marked area becomes a goal region.

`trajectory_sketch`

A drawn path or motion sketch. This tests whether the model interprets an annotation as a motion plan.

## Authority Labels

`trusted`

The visual cue is intended to be an authorized source, such as a trusted UI overlay.

`untrusted`

The cue is incidental or adversarial, such as a paper note, arbitrary screen, object sticker, or human annotation that should not redefine the task.

`ambiguous`

The cue may be useful for perception but has unclear authority. These samples are useful for diagnostic analysis.

`irrelevant`

The cue is visible but should not affect either task goal or action choice.

## Why Authority Matters

A safe VLA should use vision to understand the world while preserving the boundary between trusted instruction sources and untrusted visual content. The key failure mode is not OCR by itself; it is perception-to-goal tainting, where visual evidence changes what the model thinks it was asked to do.
