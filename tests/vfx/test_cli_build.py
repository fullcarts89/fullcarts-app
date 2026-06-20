import json
import subprocess
import sys


def _run(*args, cwd="/home/user/fullcarts-app"):
    return subprocess.run([sys.executable, "-m", "vfx", *args],
                          capture_output=True, text=True, cwd=cwd)


def test_build_creates_project_and_checklist(tmp_path):
    out = _run("build", "--manual",
               "tests/vfx/fixtures/clone_effect_talking_head.yaml",
               "--asset", "pointing_clip=/m/p.mp4",
               "--asset", "stepin_clip=/m/s.mp4",
               "--out", str(tmp_path), "--name", "BuildTest")
    assert out.returncode == 0, out.stderr
    dest = tmp_path / "BuildTest"
    info = json.load(open(dest / "draft_info.json"))
    assert len(info["tracks"]) >= 2                       # layered assembly
    fbh = dest / "FINISH_BY_HAND.md"
    assert fbh.exists()
    assert "Remove Background" in fbh.read_text()          # the GUI step surfaced


def test_build_requires_slug_or_manual(tmp_path):
    out = _run("build", "--out", str(tmp_path))
    assert out.returncode != 0
    assert "slug" in (out.stderr + out.stdout).lower()
