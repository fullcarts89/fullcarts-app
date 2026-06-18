from fastapi.testclient import TestClient
from vfx.web.app import create_app


def test_root_serves_html(tmp_path):
    c = TestClient(create_app(work_dir=tmp_path / "w", out_dir=tmp_path / "o"))
    r = c.get("/")
    assert r.status_code == 200
    body = r.text.lower()
    assert "<html" in body
    assert "script" in body and "build" in body   # the flow is present
