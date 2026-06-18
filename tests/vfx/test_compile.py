from vfx.ingest.manual_schema import load_manual
from vfx.capcut.compile import compile_timeline, CompileResult

FAKE = lambda p: (6_000_000, 1080, 1920)  # 6s clip


def test_clone_compiles_to_overlay_timeline():
    r = load_manual("tests/vfx/fixtures/clone_effect_talking_head.yaml")
    res = compile_timeline(r, {"pointing_clip": "/m/p.mp4", "stepin_clip": "/m/s.mp4"}, probe=FAKE)
    assert isinstance(res, CompileResult)
    tl = res.timeline
    # at least the 2 assets + the duplicate => >= 3 clips on multiple tracks
    assert len(tl.clips) >= 3
    assert len({c.track for c in tl.clips}) >= 2          # layered
    assert all(c.duration_us == 6_000_000 for c in tl.clips)  # full length from probe
    # the GUI 'remove_background' step is surfaced for manual finishing
    assert any("Remove Background" in n for n in res.manual_notes)


def test_missing_asset_is_tolerated():
    r = load_manual("tests/vfx/fixtures/clone_effect_talking_head.yaml")
    res = compile_timeline(r, {"pointing_clip": "/m/p.mp4"}, probe=FAKE)  # only 1 of 2
    assert len(res.timeline.clips) >= 1  # still builds something
