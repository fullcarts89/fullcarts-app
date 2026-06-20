"""Compile a VFXRecipe + accepted clips into a Timeline.

This is the deterministic "compile step" between ingestion and the draft writer.
It probes each provided asset for its real dimensions/duration, lays the assets
down as base clips, then walks the recipe's structural (``Channel.DRAFT``) edit
steps to assemble a layered-overlay Timeline. Steps it cannot resolve
deterministically in v1 (content-dependent timing, GUI/JUDGMENT actions) are
surfaced as ``manual_notes`` for a human to finish by hand.

No media is required at test time -- callers inject a fake ``probe``.
"""

import json
import subprocess
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from vfx.models import VFXRecipe, Channel
from vfx.capcut.timeline import Timeline, Clip

# Fallback when an asset cannot be probed: 5s at canvas dimensions.
_DEFAULT_DUR_US = 5_000_000


@dataclass
class CompileResult:
    timeline: Timeline
    manual_notes: List[str] = field(default_factory=list)  # steps to finish by hand


def ffprobe_media(path: str) -> Tuple[int, int, int]:
    """Return (duration_us, width, height) via ffprobe."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-of", "json",
         "-show_entries", "stream=width,height:format=duration", str(path)],
        capture_output=True, text=True, check=True)
    d = json.loads(out.stdout)
    stream = next(s for s in d.get("streams", []) if "width" in s)
    dur_us = int(float(d["format"]["duration"]) * 1_000_000)
    return dur_us, int(stream["width"]), int(stream["height"])


def _match_asset(target: Optional[str], asset_names: List[str]) -> Optional[str]:
    """Resolve a step target to a single asset name by substring matching.

    "both"/"all"/None (or anything that matches zero or many assets) -> None.
    """
    if not target:
        return None
    t = target.lower()
    if "both" in t or "all" in t:
        return None
    # Prefer an exact asset name appearing as a substring of the target, or
    # the target appearing as a substring of the asset name.
    matches = [
        name for name in asset_names
        if name.lower() in t or t in name.lower()
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def compile_timeline(
    recipe: VFXRecipe,
    assets: Dict[str, str],                 # asset name -> file path
    width: int = 1080,
    height: int = 1920,
    fps: float = 30.0,
    probe: Callable[[str], Tuple[int, int, int]] = ffprobe_media,
) -> CompileResult:
    notes: List[str] = []

    # --- 1. Probe each provided asset. ---
    probed: Dict[str, Tuple[int, int, int]] = {}
    for name, path in assets.items():
        try:
            probed[name] = probe(path)
        except Exception as exc:  # noqa: BLE001 - any probe failure degrades gracefully
            notes.append(f"Could not probe asset {name!r} ({path}): {exc}")
            probed[name] = (_DEFAULT_DUR_US, width, height)

    # --- 2. Base clips, one per present asset, in asset_spec order. ---
    spec_order = [a.name for a in recipe.asset_spec]
    if spec_order:
        ordered_names = [n for n in spec_order if n in assets]
    else:
        ordered_names = list(assets.keys())

    clips: List[Clip] = []
    track_by_asset: Dict[str, Clip] = {}
    for track_idx, name in enumerate(ordered_names):
        dur, w, h = probed[name]
        clip = Clip(
            source_path=assets[name],
            timeline_start_us=0,
            duration_us=dur,
            source_start_us=0,
            track=track_idx,
            src_width=w,
            src_height=h,
        )
        clips.append(clip)
        track_by_asset[name] = clip

    asset_names = list(assets.keys())

    def _max_track() -> int:
        return max((c.track for c in clips), default=-1)

    # --- 3. Walk structural steps in order. ---
    for step in recipe.edit_steps:
        if step.channel != Channel.DRAFT:
            # --- 4. Non-DRAFT steps -> readable manual note. ---
            notes.append(f"[{step.channel.value}] {step.instruction}")
            continue

        action = (step.action or "").lower()
        params = step.params or {}
        matched = _match_asset(step.target, asset_names)
        matched_clip = track_by_asset.get(matched) if matched else None

        if action == "import":
            continue

        if action == "overlay":
            if matched_clip is not None:
                matched_clip.track = params.get("track", matched_clip.track)
                continue
            notes.append(f"Manual: {step.instruction}")
            continue

        if action == "duplicate":
            if matched_clip is not None:
                to_track = params.get("to_track", _max_track() + 1)
                clips.append(Clip(
                    source_path=matched_clip.source_path,
                    timeline_start_us=0,
                    duration_us=matched_clip.duration_us,
                    source_start_us=0,
                    track=to_track,
                    src_width=matched_clip.src_width,
                    src_height=matched_clip.src_height,
                ))
                continue
            notes.append(f"Manual: {step.instruction}")
            continue

        if action == "position":
            if matched_clip is not None:
                if "timeline_start_ms" in params:
                    matched_clip.timeline_start_us = int(params["timeline_start_ms"]) * 1000
                    continue
                align_to = params.get("align_to")
                ref = track_by_asset.get(align_to) if align_to else None
                if ref is not None:
                    matched_clip.timeline_start_us = ref.timeline_start_us
                    continue
            notes.append(f"Manual: {step.instruction}")
            continue

        if action in ("split", "trim", "delete"):
            notes.append(f"Manual ({action}): {step.instruction}")
            continue

        # Any other DRAFT action, or unmatched target.
        notes.append(f"Manual: {step.instruction}")

    # --- 5. Assemble Timeline, clips ordered by track. ---
    clips.sort(key=lambda c: c.track)
    return CompileResult(
        timeline=Timeline(clips=clips, width=width, height=height, fps=fps),
        manual_notes=notes,
    )
