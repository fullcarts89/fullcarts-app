import json

from vfx.capcut.timeline import Timeline, Clip
from vfx.capcut.draft import write_project

OLD_SKELETON_ID = "8D347C57-CBB7-49D3-A6E7-6CC04C416312"


def test_timeline_id_consistent_everywhere(tmp_path):
    dest = write_project(Timeline(clips=[
        Clip("/m/a.mp4", 0, 5_000_000, track=0),
        Clip("/m/b.mp4", 1_000_000, 3_000_000, track=1),
    ]), tmp_path, "P")

    root = json.load(open(dest / "draft_info.json"))
    tl_id = root["id"]

    tl_dirs = [p for p in (dest / "Timelines").iterdir() if p.is_dir()]
    assert len(tl_dirs) == 1
    assert tl_dirs[0].name == tl_id                          # folder name == id
    inner = json.load(open(tl_dirs[0] / "draft_info.json"))
    assert inner["id"] == tl_id                              # inner draft == id

    pj = json.load(open(dest / "Timelines" / "project.json"))
    assert pj["main_timeline_id"] == tl_id                   # project.json main == id
    assert all(t["id"] == tl_id for t in pj["timelines"])    # timelines[].id == id

    # the skeleton's original id must be gone from every propagated file
    assert tl_id != OLD_SKELETON_ID
    assert OLD_SKELETON_ID not in json.dumps(pj)
    assert OLD_SKELETON_ID not in (dest / "timeline_layout.json").read_text()
