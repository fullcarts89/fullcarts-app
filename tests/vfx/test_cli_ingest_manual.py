import subprocess, sys, json
from pathlib import Path


def test_ingest_manual_persists(tmp_path):
    db = tmp_path / "vfx.db"
    out = subprocess.run([sys.executable, "-m", "vfx", "ingest-manual",
                          "tests/vfx/fixtures/clone_effect_talking_head.yaml", "--db", str(db)],
                         capture_output=True, text=True, cwd="/home/user/fullcarts-app")
    assert out.returncode == 0, out.stderr
    assert "clone_effect_talking_head" in out.stdout
    # round-trips through the store
    from vfx.db import RecipeStore  # noqa
    r = RecipeStore(str(db)).get("clone_effect_talking_head")
    assert r is not None and len(r.edit_steps) == 5
