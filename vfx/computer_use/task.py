"""Build a computer-use task prompt from a recipe's GUI steps.

The file-writer (draft.py) already assembles everything expressible as data. The
computer-use runner only needs to perform the *GUI-only* steps that can't live in
the project file -- Remove Background, particle/sticker effects, certain masks.
This module turns those steps (Channel.GUI, with their exact ``capcut_feature``
labels) into a single, explicit instruction string for the model.
"""
from __future__ import annotations

from typing import List

from vfx.models import Channel, VFXRecipe

_PREAMBLE = (
    "You are operating CapCut Desktop on macOS to finish a video. The project is "
    "already open with all clips on the timeline; only the GUI-only effects below "
    "remain. Work strictly through CapCut's on-screen controls. Use the EXACT "
    "feature names given (they are CapCut's real menu labels). After each action, "
    "take a screenshot and verify the result before moving on. Do not touch color "
    "grading or anything not listed. If a control isn't visible, select the named "
    "clip on the timeline first. When every step is done, stop.\n\n"
    "STEPS (in order):\n"
)


def gui_steps(recipe: VFXRecipe) -> List[str]:
    """The human-readable GUI-only steps the runner is responsible for."""
    out: List[str] = []
    for s in recipe.edit_steps:
        if s.channel != Channel.GUI:
            continue
        line = s.instruction
        feat = (s.params or {}).get("capcut_feature")
        out.append(line if not feat else f"{line}  [{feat}]")
    return out


def build_task(recipe: VFXRecipe) -> str:
    steps = gui_steps(recipe)
    if not steps:
        return ""  # nothing GUI-only to do
    body = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))
    return _PREAMBLE + body
