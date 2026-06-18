import io
from fastapi.testclient import TestClient
from vfx.web.app import create_app
from vfx.db import RecipeStore
from vfx.models import VFXRecipe, AssetSpec, EditStep, Channel
from vfx.qa.gate import Verdict


def _store(tmp_path):
    s = RecipeStore(tmp_path / "db.sqlite")
    s.put(VFXRecipe(slug="clone", title="Clone Effect", difficulty="beginner",
        editor="CapCut", shot_on="phone", technique_primitive="overlay_bg_removal_clone",
        summary="make a clone of yourself", gear="tripod",
        asset_spec=[AssetSpec(name="a", type="shot"), AssetSpec(name="b", type="shot")],
        filming_steps=["a: point and step out", "b: step in and sit"],
        edit_steps=[EditStep(index=1, instruction="overlay", capcut_target="overlay",
                             channel=Channel.DRAFT, action="overlay", target="b")]))
    return s


def _client(tmp_path):
    app = create_app(store=_store(tmp_path), work_dir=tmp_path / "work",
                     out_dir=tmp_path / "out",
                     qa_check=lambda spec, path, ref_path=None: Verdict(True))
    return TestClient(app)


def test_recommend_then_plan_then_upload_then_build(tmp_path):
    c = _client(tmp_path)
    r = c.post("/api/recommend", json={"script": "I want to clone myself", "equipment": ["tripod"], "props": [], "location": "home", "k": 3})
    assert r.status_code == 200 and r.json()["candidates"][0]["slug"] == "clone"
    p = c.post("/api/plan", json={"slug": "clone"})
    assert p.status_code == 200 and len(p.json()["inputs"]) == 2
    up = c.post("/api/upload", data={"slug": "clone", "asset_name": "a"},
                files={"file": ("a.mp4", io.BytesIO(b"x"), "video/mp4")})
    assert up.status_code == 200 and up.json()["accepted"] is True
    c.post("/api/upload", data={"slug": "clone", "asset_name": "b"},
           files={"file": ("b.mp4", io.BytesIO(b"y"), "video/mp4")})
    b = c.post("/api/build", json={"slug": "clone"})
    assert b.status_code == 200
    import os
    proj = b.json()["project_path"]
    assert os.path.exists(os.path.join(proj, "draft_info.json"))
    assert os.path.exists(os.path.join(proj, "FINISH_BY_HAND.md"))


def test_health(tmp_path):
    assert _client(tmp_path).get("/api/health").json()["status"] == "ok"


def test_plan_404_for_unknown(tmp_path):
    c = _client(tmp_path)
    assert c.post("/api/plan", json={"slug": "nope"}).status_code == 404


def test_upload_unknown_asset_400(tmp_path):
    c = _client(tmp_path)
    up = c.post("/api/upload", data={"slug": "clone", "asset_name": "zzz"},
                files={"file": ("z.mp4", io.BytesIO(b"x"), "video/mp4")})
    assert up.status_code == 400


def test_build_without_assets_400(tmp_path):
    c = _client(tmp_path)
    c.post("/api/recommend", json={"script": "x", "equipment": [], "props": [], "location": "home"})
    assert c.post("/api/build", json={"slug": "clone"}).status_code == 400


def test_root_backend_ok_when_no_static(tmp_path):
    c = _client(tmp_path)
    body = c.get("/").json()
    assert "backend ok" in body["status"]
