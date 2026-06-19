from fastapi.testclient import TestClient
from vfx.web.app import create_app


def _client(tmp_path):
    app = create_app(work_dir=tmp_path / "work", out_dir=tmp_path / "out")
    return TestClient(app)


def test_health_uses_manuals_default(tmp_path):
    c = _client(tmp_path)
    j = c.get("/api/health").json()
    assert j["status"] == "ok"
    assert j["recipes"] >= 15


def test_recommend_finds_clone(tmp_path):
    c = _client(tmp_path)
    r = c.post("/api/recommend", json={
        "script": "clone effect talking head — clone myself talking to myself",
        "equipment": [], "props": [], "location": "home", "k": 15})
    assert r.status_code == 200
    cands = r.json()["candidates"]
    assert any("clone" in cc["slug"].lower() for cc in cands)
    assert all("ai" in cc for cc in cands)


def test_plan_surfaces_ai(tmp_path):
    c = _client(tmp_path)
    p = c.post("/api/plan", json={"slug": "ai_location_transition"})
    assert p.status_code == 200
    body = p.json()
    assert body["is_ai_generated"] is True
    assert body["ai_generation"]
