"""CapCut Desktop draft writer (clone-and-rewrite).

Assembles a CapCut Desktop v8.6.0 project folder from a :class:`Timeline`.

Strategy (see ``FORMAT_NOTES.md``): copy the bundled golden skeleton, then
overwrite only the meaningful fields. The hundreds of CapCut-default fields on
materials/segments/tracks survive untouched because we deepcopy exemplars from
the skeleton rather than building objects from scratch.

All time values are microseconds (µs).
"""

import json
import os
import shutil
import time
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Union

from vfx.capcut.timeline import Timeline

SKELETON_DIR = Path(__file__).parent / "templates" / "draft_skeleton"

# Helper material arrays, one entry per clip. The order here is the order the
# skeleton segment emits its ``extra_material_refs`` (verified against the golden
# sample), so we keep segment refs and array contents in lock-step.
HELPERS = [
    "speeds",
    "placeholder_infos",
    "canvases",
    "sound_channel_mappings",
    "material_colors",
    "vocal_separations",
]


def _uid() -> str:
    """Return an uppercase uuid4 string, like CapCut."""
    return str(uuid.uuid4()).upper()


def _load_skeleton_draft_info() -> Dict[str, Any]:
    with open(SKELETON_DIR / "draft_info.json", encoding="utf-8") as fh:
        return json.load(fh)


def _ref_order(seg_tmpl: Dict[str, Any], helper_id_to_array: Dict[str, str]) -> List[str]:
    """Determine which helper array each of the template segment's refs belongs to.

    Returns a list of helper-array names in the order the template segment lists
    them in ``extra_material_refs``. Falls back to the canonical HELPERS order for
    any ref that doesn't map to a known helper array.
    """
    order: List[str] = []
    for ref in seg_tmpl.get("extra_material_refs", []):
        name = helper_id_to_array.get(ref)
        if name is not None:
            order.append(name)
    # If the template didn't resolve cleanly, fall back to canonical order.
    if sorted(order) != sorted(HELPERS):
        return list(HELPERS)
    return order


def build_draft_info(timeline: Timeline) -> Dict[str, Any]:
    """Build a fresh ``draft_info.json`` dict for ``timeline``."""
    tmpl = _load_skeleton_draft_info()

    # --- capture exemplars BEFORE mutating anything ---
    vid_tmpl = deepcopy(tmpl["materials"]["videos"][0])
    helper_tmpls = {h: deepcopy(tmpl["materials"][h][0]) for h in HELPERS}
    seg_tmpl = deepcopy(tmpl["tracks"][0]["segments"][0])
    track_tmpl = deepcopy(tmpl["tracks"][0])

    # Map the skeleton's helper ids -> array name so we can read the segment's
    # ref order the way CapCut wrote it.
    helper_id_to_array: Dict[str, str] = {}
    for h in HELPERS:
        for m in tmpl["materials"][h]:
            helper_id_to_array[m["id"]] = h
    ref_order = _ref_order(seg_tmpl, helper_id_to_array)

    new_videos: List[Dict[str, Any]] = []
    new_helpers: Dict[str, List[Dict[str, Any]]] = {h: [] for h in HELPERS}
    # track value -> list of segments
    segments_by_track: Dict[int, List[Dict[str, Any]]] = {}

    for clip in timeline.clips:
        # --- video material ---
        vid = deepcopy(vid_tmpl)
        vid_id = _uid()
        vid["id"] = vid_id
        vid["path"] = clip.source_path
        vid["material_name"] = os.path.basename(clip.source_path)
        vid["width"] = clip.src_width
        vid["height"] = clip.src_height
        vid["duration"] = clip.source_start_us + clip.duration_us
        new_videos.append(vid)

        # --- 6 helper materials, keyed by array name ---
        helper_ids: Dict[str, str] = {}
        for h in HELPERS:
            hm = deepcopy(helper_tmpls[h])
            hid = _uid()
            hm["id"] = hid
            helper_ids[h] = hid
            new_helpers[h].append(hm)

        # --- segment ---
        seg = deepcopy(seg_tmpl)
        seg["id"] = _uid()
        seg["material_id"] = vid_id
        seg["target_timerange"] = {
            "start": clip.timeline_start_us,
            "duration": clip.duration_us,
        }
        seg["source_timerange"] = {
            "start": clip.source_start_us,
            "duration": clip.duration_us,
        }
        seg["extra_material_refs"] = [helper_ids[name] for name in ref_order]
        # render_index assigned per-track below (ascending track position).
        segments_by_track.setdefault(clip.track, []).append(seg)

    # --- tracks: one per distinct track value, ascending = stack order ---
    new_tracks: List[Dict[str, Any]] = []
    for layer_index, track_value in enumerate(sorted(segments_by_track.keys())):
        track = deepcopy(track_tmpl)
        track["id"] = _uid()
        segs = segments_by_track[track_value]
        for seg in segs:
            seg["render_index"] = layer_index
        track["segments"] = segs
        new_tracks.append(track)

    # --- splice into the cloned template ---
    tmpl["materials"]["videos"] = new_videos
    for h in HELPERS:
        tmpl["materials"][h] = new_helpers[h]
    tmpl["tracks"] = new_tracks

    tmpl["canvas_config"]["width"] = timeline.width
    tmpl["canvas_config"]["height"] = timeline.height
    tmpl["fps"] = float(timeline.fps)

    duration = 0
    for clip in timeline.clips:
        end = clip.timeline_start_us + clip.duration_us
        if end > duration:
            duration = end
    tmpl["duration"] = duration

    tmpl["id"] = _uid()
    tmpl["name"] = ""

    return tmpl


def _rebuild_draft_materials(
    existing: Any, timeline: Timeline, now_s: int
) -> Any:
    """Best-effort rebuild of the ``draft_materials`` manifest's video group.

    ``draft_materials`` is a list of type-tagged groups; the ``type == 0`` group
    holds the imported-video manifest. We clone one entry from the existing video
    group as an exemplar and emit one per clip. Other groups are left untouched.
    If the structure isn't what we expect, we return it unchanged.
    """
    if not isinstance(existing, list):
        return existing

    out = deepcopy(existing)
    video_group = None
    for group in out:
        if isinstance(group, dict) and group.get("type") == 0:
            video_group = group
            break
    if video_group is None or not isinstance(video_group.get("value"), list):
        return out

    entry_tmpl = deepcopy(video_group["value"][0]) if video_group["value"] else None
    if entry_tmpl is None:
        return out

    new_value: List[Dict[str, Any]] = []
    for clip in timeline.clips:
        entry = deepcopy(entry_tmpl)
        entry["id"] = str(uuid.uuid4())  # manifest ids are lowercase in the sample
        entry["file_Path"] = clip.source_path
        entry["extra_info"] = os.path.basename(clip.source_path)
        dur = clip.source_start_us + clip.duration_us
        entry["duration"] = dur
        entry["width"] = clip.src_width
        entry["height"] = clip.src_height
        entry["create_time"] = now_s
        entry["import_time"] = now_s
        entry["import_time_ms"] = now_s * 1_000_000
        if isinstance(entry.get("roughcut_time_range"), dict):
            entry["roughcut_time_range"] = {"start": 0, "duration": dur}
        new_value.append(entry)
    video_group["value"] = new_value
    return out


def write_project(timeline: Timeline, out_dir: Union[str, Path], name: str) -> Path:
    """Write a complete CapCut project folder for ``timeline`` and return its path."""
    dest = Path(out_dir) / name
    shutil.copytree(SKELETON_DIR, dest)

    # The skeleton's main-timeline id lives in the root + inner draft_info.json,
    # the Timelines/<id>/ folder name, project.json, timeline_layout.json and
    # mini_draft.json. Regenerate it and propagate everywhere — otherwise CapCut
    # lists the project (from meta) but can't load the timeline.
    tl_dirs = [p for p in (dest / "Timelines").iterdir() if p.is_dir()]
    old_tl_id = tl_dirs[0].name
    new_tl_id = _uid()

    info = build_draft_info(timeline)
    info["id"] = new_tl_id
    info["name"] = name

    # Root draft_info.json
    with open(dest / "draft_info.json", "w", encoding="utf-8") as fh:
        json.dump(info, fh, ensure_ascii=False)

    # Rename Timelines/<old_id> -> Timelines/<new_id> and write its draft_info.json
    new_tl_dir = dest / "Timelines" / new_tl_id
    tl_dirs[0].rename(new_tl_dir)
    with open(new_tl_dir / "draft_info.json", "w", encoding="utf-8") as fh:
        json.dump(info, fh, ensure_ascii=False)

    # Propagate the id swap into the carried-over reference files (binary-safe).
    for rel in (
        Path("Timelines") / "project.json",
        Path("timeline_layout.json"),
        Path("Timelines") / new_tl_id / "attachment" / "patch" / "mini_draft.json",
    ):
        p = dest / rel
        if p.exists():
            data = p.read_bytes()
            p.write_bytes(data.replace(old_tl_id.encode(), new_tl_id.encode()))

    # Patch draft_meta_info.json
    meta_path = dest / "draft_meta_info.json"
    with open(meta_path, encoding="utf-8") as fh:
        meta = json.load(fh)

    now_us = int(time.time() * 1e6)
    now_s = int(time.time())
    resolved = dest.resolve()
    meta["draft_id"] = _uid()
    meta["draft_name"] = name
    meta["draft_fold_path"] = str(resolved)
    meta["draft_root_path"] = str(resolved.parent)
    meta["tm_draft_create"] = now_us
    meta["tm_draft_modified"] = now_us
    meta["tm_duration"] = info["duration"]
    if "draft_materials" in meta:
        meta["draft_materials"] = _rebuild_draft_materials(
            meta["draft_materials"], timeline, now_s
        )

    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False)

    return dest
