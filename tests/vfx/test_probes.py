import shutil, subprocess
import pytest
from vfx.qa.probes import (probe_resolution, probe_duration, camera_shift_px,
                           has_green_screen, video_rotation_deg)

pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")

def _make(path, vf=None, size="320x240", dur="1", src="testsrc"):
    # lavfi filter options are introduced by '=' after the bare filter name and
    # separated by ':'. A bare src ("testsrc") needs '=' before its first option;
    # a src that already carries an option ("color=c=green") needs ':'.
    sep = ":" if "=" in src else "="
    source = f"{src}{sep}size={size}:rate=10:duration={dur}"
    cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", source]
    if vf: cmd += ["-vf", vf]
    cmd += [str(path)]
    subprocess.run(cmd, capture_output=True, check=True)

def test_resolution(tmp_path):
    p = tmp_path / "a.mp4"; _make(p, size="640x480")
    assert probe_resolution(p, 320, 240).passed
    assert not probe_resolution(p, 1280, 720).passed

def test_duration(tmp_path):
    p = tmp_path / "a.mp4"; _make(p, dur="2")
    assert probe_duration(p, 1.0).passed
    assert not probe_duration(p, 5.0).passed

def test_camera_locked_identical(tmp_path):
    a = tmp_path / "a.mp4"; b = tmp_path / "b.mp4"
    _make(a); _make(b)  # two testsrc clips: frame 0 is identical -> ~0px shift
    assert camera_shift_px(a, b, max_px=8.0).passed

def test_camera_moved(tmp_path):
    a = tmp_path / "a.mp4"; c = tmp_path / "c.mp4"
    _make(a)
    _make(c, vf="crop=iw-40:ih:40:0,pad=iw+40:ih:0:0")  # shift content ~40px
    res = camera_shift_px(a, c, max_px=8.0)
    assert not res.passed and res.value > 8.0

def test_green_screen(tmp_path):
    g = tmp_path / "g.mp4"; _make(g, src="color=c=green")
    n = tmp_path / "n.mp4"; _make(n, src="testsrc")
    assert has_green_screen(g).passed
    assert not has_green_screen(n).passed


def test_no_rotation_reads_zero(tmp_path):
    p = tmp_path / "flat.mp4"; _make(p, size="640x480")
    assert video_rotation_deg(p) == 0


# --- rotation handling (iPhone display-matrix), stubbed at the ffprobe layer ---
# Real iPhone portrait clips are stored landscape (e.g. 1920x1080) with a
# rotation=-90 display matrix. ffprobe with nokey emits a *bare* number ("-90"),
# which the original parser dropped (it required an "=" in the line). These tests
# pin both the parse and the resulting display-resolution swap.
import vfx.qa.probes as _probes


class _FakeProc:
    def __init__(self, stdout): self.stdout = stdout


def test_video_rotation_parses_bare_nokey_number(monkeypatch):
    monkeypatch.setattr(_probes.subprocess, "run", lambda *a, **k: _FakeProc("-90\n"))
    assert _probes.video_rotation_deg("x.mov") == 90  # abs(-90) % 360


def test_video_rotation_parses_keyed_output(monkeypatch):
    monkeypatch.setattr(_probes.subprocess, "run", lambda *a, **k: _FakeProc("rotation=270\n"))
    assert _probes.video_rotation_deg("x.mov") == 270


def test_resolution_swaps_on_90_rotation(monkeypatch):
    # stream reports landscape 1920x1080; rotation 90 => displays 1080x1920.
    monkeypatch.setattr(_probes.subprocess, "run", lambda *a, **k: _FakeProc("1920\n1080\n"))
    monkeypatch.setattr(_probes, "video_rotation_deg", lambda p: 90)
    res = probe_resolution("x.mov", 1080, 1920)
    assert res.passed and "1080x1920" in res.detail


def test_resolution_no_swap_on_zero_rotation(monkeypatch):
    monkeypatch.setattr(_probes.subprocess, "run", lambda *a, **k: _FakeProc("1920\n1080\n"))
    monkeypatch.setattr(_probes, "video_rotation_deg", lambda p: 0)
    res = probe_resolution("x.mov", 1080, 1920)
    assert (not res.passed) and "1920x1080" in res.detail
