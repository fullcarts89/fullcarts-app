import shutil, subprocess
import pytest
from vfx.qa.probes import (probe_resolution, probe_duration, camera_shift_px, has_green_screen)

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
