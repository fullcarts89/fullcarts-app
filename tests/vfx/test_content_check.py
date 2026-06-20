import shutil
import pytest
from vfx.qa.content_check import compare_products, ContentVerdict
from vfx.qa.gate import check_asset
from vfx.models import AssetSpec

pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


class _FakeResp:
    def __init__(self, text):
        self.content = [type("B", (), {"type": "text", "text": text})()]


class _FakeClient:
    """Returns a canned structured-output JSON, records the model used."""
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    class _Messages:
        def __init__(self, outer): self.outer = outer
        def create(self, **kw):
            self.outer.calls.append(kw)
            return _FakeResp(self.outer.payload)

    @property
    def messages(self):
        return _FakeClient._Messages(self)


def _img(tmp_path, name, color):
    import subprocess
    p = tmp_path / name
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                    "-i", f"color=c={color}:size=400x400:duration=0.1",
                    "-frames:v", "1", str(p)], check=True)
    return str(p)


def test_same_product_passes(tmp_path):
    a = _img(tmp_path, "a.jpg", "blue"); b = _img(tmp_path, "b.jpg", "blue")
    client = _FakeClient('{"same_product": true, "current_label": "Kraft 200g",'
                         '"old_label": "Kraft 225g", "old_clearly_smaller": false,'
                         '"confidence": 0.9, "reason": "same box, larger"}')
    v = compare_products(a, b, client=client)
    assert isinstance(v, ContentVerdict) and v.passed and v.same_product
    assert client.calls[0]["model"].startswith("claude-haiku")


def test_different_product_fails(tmp_path):
    a = _img(tmp_path, "a.jpg", "blue"); b = _img(tmp_path, "b.jpg", "red")
    client = _FakeClient('{"same_product": false, "current_label": "bottle",'
                         '"old_label": "tissue box", "old_clearly_smaller": false,'
                         '"confidence": 0.96, "reason": "different products"}')
    v = compare_products(a, b, client=client)
    assert not v.passed and not v.same_product


def test_gate_runs_vision_check_with_injected_client(tmp_path):
    a = _img(tmp_path, "a.jpg", "blue"); b = _img(tmp_path, "b.jpg", "red")
    spec = AssetSpec(name="old_pack", type="image", acceptance_checks=["product_matches_reference"])
    client = _FakeClient('{"same_product": false, "current_label": "x",'
                         '"old_label": "y", "old_clearly_smaller": false,'
                         '"confidence": 0.9, "reason": "mismatch"}')
    verdict = check_asset(spec, b, ref_path=a, content_client=client)
    assert not verdict.passed
    assert any("product_matches_reference" in f for f in verdict.failures)


def test_gate_degrades_to_manual_without_key_or_ref(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    spec = AssetSpec(name="old_pack", type="image", acceptance_checks=["product_matches_reference"])
    # no ref -> manual flag
    v1 = check_asset(spec, "x.jpg", ref_path=None)
    assert v1.passed and any("no reference" in m for m in v1.manual_checks)
    # ref but no key + no client -> manual flag (never spends money)
    v2 = check_asset(spec, "x.jpg", ref_path="ref.jpg")
    assert v2.passed and any("ANTHROPIC_API_KEY" in m for m in v2.manual_checks)
