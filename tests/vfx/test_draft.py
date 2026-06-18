import json
from pathlib import Path

from vfx.capcut.timeline import Clip, Timeline
from vfx.capcut.draft import build_draft_info, write_project


def _two_track_timeline():
    return Timeline(clips=[
        Clip("/m/base.mp4", timeline_start_us=0, duration_us=5_000_000, track=0, src_width=1080, src_height=1920),
        Clip("/m/overlay.mp4", timeline_start_us=1_000_000, duration_us=3_000_000, track=1, src_width=720, src_height=1280),
    ], width=1080, height=1920)


def test_build_has_materials_tracks_and_resolves_refs():
    info = build_draft_info(_two_track_timeline())
    assert len(info["materials"]["videos"]) == 2
    assert len(info["tracks"]) == 2
    # every segment's material_id and extra_material_refs resolve to a material
    ids = set()
    for arr in info["materials"].values():
        if isinstance(arr, list):
            for m in arr:
                if isinstance(m, dict) and "id" in m:
                    ids.add(m["id"])
    for t in info["tracks"]:
        for s in t["segments"]:
            assert s["material_id"] in ids
            for r in s["extra_material_refs"]:
                assert r in ids
    assert info["canvas_config"]["width"] == 1080
    assert info["duration"] == 5_000_000  # max(0+5e6, 1e6+3e6)


def test_timeranges_and_layering():
    info = build_draft_info(_two_track_timeline())
    segs = [t["segments"][0] for t in info["tracks"]]
    starts = sorted(s["target_timerange"]["start"] for s in segs)
    assert starts == [0, 1_000_000]
    assert {s["render_index"] for s in segs} == {0, 1}


def test_sequential_same_track():
    tl = Timeline(clips=[
        Clip("/m/a.mp4", 0, 2_000_000, track=0),
        Clip("/m/b.mp4", 2_000_000, 2_000_000, track=0),
    ])
    info = build_draft_info(tl)
    assert len(info["tracks"]) == 1 and len(info["tracks"][0]["segments"]) == 2


def test_write_project_creates_openable_layout(tmp_path):
    dest = write_project(_two_track_timeline(), tmp_path, "MyProj")
    assert (dest / "draft_info.json").exists()
    tl_infos = list((dest / "Timelines").glob("*/draft_info.json"))
    assert tl_infos, "missing Timelines/<uuid>/draft_info.json"
    root = json.load(open(dest / "draft_info.json"))
    inner = json.load(open(tl_infos[0]))
    assert len(root["tracks"]) == 2 and len(inner["tracks"]) == 2
    meta = json.load(open(dest / "draft_meta_info.json"))
    assert meta["draft_name"] == "MyProj" and meta["tm_duration"] == 5_000_000
