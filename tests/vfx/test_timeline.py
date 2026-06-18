"""Trivial construction + default tests for the Timeline model."""

from vfx.capcut.timeline import Clip, Timeline


def test_clip_defaults():
    c = Clip("/a.mp4", 0, 1_000_000)
    assert c.source_path == "/a.mp4"
    assert c.timeline_start_us == 0
    assert c.duration_us == 1_000_000
    assert c.source_start_us == 0
    assert c.track == 0
    assert c.src_width == 1080
    assert c.src_height == 1920


def test_clip_overrides():
    c = Clip(
        "/b.mov",
        timeline_start_us=2_000_000,
        duration_us=3_000_000,
        source_start_us=500_000,
        track=2,
        src_width=720,
        src_height=1280,
    )
    assert c.source_start_us == 500_000
    assert c.track == 2
    assert c.src_width == 720
    assert c.src_height == 1280


def test_timeline_defaults():
    t = Timeline()
    assert t.clips == []
    assert t.width == 1080
    assert t.height == 1920
    assert t.fps == 30.0


def test_timeline_with_clips():
    t = Timeline(clips=[Clip("/a.mp4", 0, 1_000_000)], width=1920, height=1080, fps=24.0)
    assert len(t.clips) == 1
    assert t.width == 1920
    assert t.height == 1080
    assert t.fps == 24.0
