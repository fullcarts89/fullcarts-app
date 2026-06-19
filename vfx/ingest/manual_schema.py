"""Deterministic schema-manual ingester.

Parses a structured VFX manual (YAML or JSON, per docs/MANUAL_SCHEMA.md) into a
VFXRecipe via pure mapping -- zero AI inference, zero per-manual cost.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml

from vfx.models import AssetSpec, Channel, EditStep, VFXRecipe

# Actions that the draft engine can write directly into the CapCut project file.
_DRAFT_ACTIONS = {
    "import", "split", "delete", "trim", "overlay", "duplicate",
    "position", "transition", "text",
}
# Actions that are inherently a subjective human call.
_JUDGMENT_ACTIONS = {"adjustment"}

# Explicit channel tag -> Channel enum.
_CHANNEL_MAP = {
    "structural": Channel.DRAFT,
    "ui": Channel.GUI,
    "taste": Channel.JUDGMENT,
}


def load_manual_file(path: Union[str, Path]) -> Dict[str, Any]:
    """Read a manual file (.yaml/.yml via yaml.safe_load, .json via json.load)."""
    p = Path(path)
    suffix = p.suffix.lower()
    text = p.read_text(encoding="utf-8")
    if suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    if suffix == ".json":
        return json.loads(text)
    raise ValueError(
        "unsupported manual file extension %r (expected .yaml/.yml/.json)" % suffix
    )


def _infer_channel(action: str) -> Channel:
    if action in _DRAFT_ACTIONS:
        return Channel.DRAFT
    if action in _JUDGMENT_ACTIONS:
        return Channel.JUDGMENT
    return Channel.GUI


def _step_channel(step: Dict[str, Any]) -> Channel:
    tag = step.get("channel")
    if tag in _CHANNEL_MAP:
        return _CHANNEL_MAP[tag]
    return _infer_channel(step.get("action", ""))


def manual_to_recipe(m: Dict[str, Any]) -> VFXRecipe:
    """Pure mapping from a parsed manual dict to a VFXRecipe."""
    # --- Validation first ---
    for fieldname in ("id", "technique_primitive", "title"):
        if not m.get(fieldname):
            raise ValueError("manual missing required field: %r" % fieldname)
    inputs = m.get("inputs")
    if not inputs or not isinstance(inputs, list):
        raise ValueError("manual missing required non-empty list field: 'inputs'")
    edit_steps_raw = m.get("edit_steps")
    if not edit_steps_raw or not isinstance(edit_steps_raw, list):
        raise ValueError(
            "manual missing required non-empty list field: 'edit_steps'")

    summary = (
        m.get("result_description")
        or (m.get("result") or {}).get("description")
        or ""
    )

    gear = ", ".join(m.get("gear_required", [])) or None

    reference_images: List[str] = []
    frames = m.get("frames")
    if isinstance(frames, dict):
        reference_images = list(frames.get("demo", [])) + list(frames.get("editing", []))

    asset_spec: List[AssetSpec] = []
    for i in inputs:
        asset_spec.append(AssetSpec(
            name=i["name"],
            type=i.get("type", "shot"),
            capture_requirements=i.get("capture_requirements", {}),
            acceptance_checks=i.get("acceptance_checks", []),
            variance_tolerance=i.get("variance_tolerance", {}),
        ))

    filming_steps = [
        f"{i['name']}: {i['what_to_film']}"
        for i in inputs if i.get("what_to_film")
    ]

    edit_steps: List[EditStep] = []
    for idx, step in enumerate(edit_steps_raw, start=1):
        action = step.get("action", "")
        target = step.get("target", "")
        capcut_feature = step.get("capcut_feature")
        capcut_target = capcut_feature or action

        params = dict(step.get("params", {}))
        if "timing" in step:
            params["timing"] = step["timing"]

        instruction = f"{action.replace('_', ' ').capitalize()} — {target}"
        if capcut_feature:
            instruction += f" [{capcut_feature}]"

        edit_steps.append(EditStep(
            index=idx,
            instruction=instruction,
            capcut_target=capcut_target,
            params=params,
            channel=_step_channel(step),
            reference_screenshot=None,
            action=step.get("action"),
            target=step.get("target"),
        ))

    return VFXRecipe(
        slug=m["id"],
        title=m["title"],
        difficulty=m.get("difficulty", "unknown"),
        editor=m.get("tool", "CapCut"),
        shot_on=m.get("shot_on", "unknown"),
        technique_primitive=m["technique_primitive"],
        summary=summary,
        asset_spec=asset_spec,
        filming_steps=filming_steps,
        edit_steps=edit_steps,
        layers_reference=None,
        gear=gear,
        reference_images=reference_images,
        ingest_confidence=1.0,
        is_ai_generated=bool(m.get("is_ai_generated")),
        ai_generation=m.get("ai_generation") or [],
    )


def load_manual(path: Union[str, Path]) -> VFXRecipe:
    return manual_to_recipe(load_manual_file(path))
