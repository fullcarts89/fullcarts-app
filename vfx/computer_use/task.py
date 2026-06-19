"""Build a computer-use task prompt from a recipe's GUI steps.

The file-writer (draft.py) already assembles everything expressible as data. The
computer-use runner only needs to perform the *GUI-only* steps that can't live in
the project file -- Remove Background, particle/sticker effects, certain masks.
This module turns those steps (Channel.GUI, with their exact ``capcut_feature``
labels) into a single, explicit instruction string for the model.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from vfx.models import Channel, VFXRecipe

# Manual asset paths (frames) are stored relative to the vfx_instructions dir.
_VFX_INSTRUCTIONS = Path(__file__).resolve().parents[2] / "vfx_instructions"

_PREAMBLE = (
    "You are operating CapCut **Desktop** on macOS to finish a video. The project "
    "is already open with all clips on the timeline; only the GUI-only effects "
    "below remain.\n\n"
    "IMPORTANT — mobile vs desktop: some steps may be worded for CapCut's MOBILE "
    "app (e.g. 'tap', 'bottom bar', 'swipe'). CapCut Desktop has the SAME features "
    "under the SAME names, only in different places (menus, the right-hand "
    "properties panel, the toolbar above the player). Treat each step's named "
    "feature as the source of truth and FIND IT on the desktop UI by reading the "
    "screen — ignore any mobile-specific location/gesture wording and translate it "
    "to the desktop equivalent (click, not tap; panels, not bottom sheets).\n\n"
    "Method: select the named clip on the timeline first if a control isn't "
    "visible; use the EXACT feature names given (they are CapCut's real labels). "
    "After each action, take a screenshot and verify the result before moving on. "
    "Do not touch color grading or anything not listed. If you genuinely cannot "
    "find a named feature after looking, say so in text and stop rather than "
    "clicking randomly. When every step is done, stop.\n\n"
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


def _resolve(rel: str, base_dir: Optional[Path]) -> Optional[Path]:
    """Resolve a (possibly relative) image path to a file that exists, or None."""
    if not rel:
        return None
    cands = []
    p = Path(rel)
    if p.is_absolute():
        cands.append(p)
    else:
        if base_dir:
            cands.append(Path(base_dir) / rel)
        cands.append(_VFX_INSTRUCTIONS / rel)
        cands.append(Path.cwd() / rel)
    for c in cands:
        if c.is_file():
            return c
    return None


def reference_blocks(
    recipe: VFXRecipe,
    base_dir: Optional[Path] = None,
    max_general: int = 4,
) -> List[Tuple[str, str]]:
    """Resolve reference screenshots to feed the runner as visual grounding.

    Returns a list of ``(caption, absolute_path)``:
      * one per GUI step that declares a ``reference_screenshot`` (step-aligned,
        the precise kind), captioned with that step's instruction; plus
      * up to ``max_general`` recipe-level frames as non-aligned context, only if
        no step-aligned refs exist (so we don't double up or blow the token budget).

    Missing files are skipped silently — a stale path never breaks a run.
    """
    blocks: List[Tuple[str, str]] = []
    n = 0
    for s in recipe.edit_steps:
        if s.channel != Channel.GUI or not s.reference_screenshot:
            continue
        n += 1
        resolved = _resolve(s.reference_screenshot, base_dir)
        if resolved:
            blocks.append((f"Reference for step {n} ({s.instruction})", str(resolved)))

    if not blocks:  # fall back to the recipe's general frame bundle (not step-aligned)
        for rel in recipe.reference_images[:max_general]:
            resolved = _resolve(rel, base_dir)
            if resolved:
                blocks.append(
                    ("General reference frame for this effect (not step-aligned)",
                     str(resolved)))
    return blocks


@dataclass
class RefCoverage:
    index: int            # GUI-step number (1-based among GUI steps)
    instruction: str
    declared: Optional[str]    # the path the manual declares, if any
    resolved: Optional[str]    # the file it resolves to on disk, if found

    @property
    def status(self) -> str:
        if self.resolved:
            return "ok"            # declared + file present
        if self.declared:
            return "missing"      # declared a path but the file isn't on disk
        return "none"             # no reference_screenshot on this step


def reference_coverage(recipe: VFXRecipe,
                       base_dir: Optional[Path] = None) -> List[RefCoverage]:
    """Per-GUI-step report: has a screenshot / declared-but-missing / none.

    Authoring aid (surfaced by ``vfx finish --dry-run``): the runtime path skips
    missing files silently so a run never breaks, but at authoring time you want
    to SEE the gaps so you know which frames to capture.
    """
    out: List[RefCoverage] = []
    n = 0
    for s in recipe.edit_steps:
        if s.channel != Channel.GUI:
            continue
        n += 1
        declared = s.reference_screenshot
        resolved = _resolve(declared, base_dir) if declared else None
        out.append(RefCoverage(n, s.instruction, declared,
                               str(resolved) if resolved else None))
    return out
