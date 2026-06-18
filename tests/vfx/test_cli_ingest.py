import subprocess
import sys
from vfx.db import RecipeStore


def test_cli_ingest_dataset(tmp_path):
    db = tmp_path / "vfx.db"
    out = subprocess.run([sys.executable, "-m", "vfx", "ingest-dataset", "--db", str(db)],
                         capture_output=True, text=True, cwd="/home/user/fullcarts-app")
    assert out.returncode == 0, out.stderr
    assert "ingested 34" in out.stdout
    assert RecipeStore(db).get("make_an_object_appear") is not None
