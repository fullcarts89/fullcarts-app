import os
import subprocess
import sys


def test_enrich_refuses_without_key(tmp_path):
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)
    out = subprocess.run(
        [sys.executable, "-m", "vfx", "enrich", "--db", str(tmp_path / "x.db")],
        capture_output=True, text=True, cwd="/home/user/fullcarts-app", env=env)
    assert out.returncode != 0
    assert "ANTHROPIC_API_KEY" in (out.stderr + out.stdout)
