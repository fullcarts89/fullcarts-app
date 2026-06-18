import subprocess
import sys


def _run(*args):
    return subprocess.run([sys.executable, "-m", "vfx", *args],
                          capture_output=True, text=True, cwd="/home/user/fullcarts-app")


def test_recommend_prints_k():
    out = _run("recommend", "--equipment", "tripod,phone", "-k", "3")
    assert out.returncode == 0, out.stderr
    assert len(out.stdout.strip().splitlines()) == 3


def test_plan_prints_sections():
    out = _run("plan", "make_an_object_appear")
    assert out.returncode == 0, out.stderr
    assert "Filming plan" in out.stdout and "Finish-by-hand" in out.stdout
