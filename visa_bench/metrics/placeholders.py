"""Future metric entry points.

These functions intentionally do not implement model evaluation yet. The first
milestone only generates open-loop attacked image pairs and metadata.
"""


def compute_vls(*args, **kwargs):
    """Visual Literacy Score: whether a model understands the visual cue."""
    raise NotImplementedError("VLS requires model outputs and is not implemented yet.")


def compute_aja(*args, **kwargs):
    """Authority Judgment Accuracy: whether a model judges cue authority correctly."""
    raise NotImplementedError("AJA requires model outputs and is not implemented yet.")


def compute_cas(*args, **kwargs):
    """Causal Action Shift: whether attacked images change action outputs."""
    raise NotImplementedError("CAS requires paired model actions and is not implemented yet.")


def compute_gtr(*args, **kwargs):
    """Goal Taint Rate: whether untrusted visual cues alter inferred goals."""
    raise NotImplementedError("GTR requires model goal/action outputs and is not implemented yet.")


def compute_uer(*args, **kwargs):
    """Unsafe Execution Rate: whether closed-loop execution becomes unsafe."""
    raise NotImplementedError("UER requires closed-loop rollouts and is not implemented yet.")
