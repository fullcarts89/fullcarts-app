from vfx.director import AssetDirector
from vfx import director as director_mod
from vfx.qa.gate import Verdict
from vfx.models import VFXRecipe, AssetSpec


def _recipe():
    return VFXRecipe(slug="x", title="X", difficulty="b", editor="CapCut", shot_on="phone",
        technique_primitive="t", summary="s",
        asset_spec=[AssetSpec(name="action", type="shot"), AssetSpec(name="plate", type="shot")])


def test_pending_advances_on_accept(monkeypatch):
    monkeypatch.setattr(director_mod, "check_asset", lambda s, p, ref_path=None: Verdict(True))
    d = AssetDirector(_recipe())
    assert d.pending().name == "action"
    assert d.submit("action", "a.mp4").passed
    assert d.pending().name == "plate"  # advanced
    d.submit("plate", "p.mp4")
    assert d.complete()


def test_bounce_keeps_pending(monkeypatch):
    monkeypatch.setattr(director_mod, "check_asset",
                        lambda s, p, ref_path=None: Verdict(False, failures=["camera_locked_off: moved 30px"]))
    d = AssetDirector(_recipe())
    v = d.submit("action", "bad.mp4")
    assert not v.passed and "30px" in v.failures[0]
    assert d.pending().name == "action"  # still pending, must reshoot


def test_ref_is_first_accepted(monkeypatch):
    seen = {}
    def fake(spec, path, ref_path=None): seen[spec.name] = ref_path; return Verdict(True)
    monkeypatch.setattr(director_mod, "check_asset", fake)
    d = AssetDirector(_recipe())
    d.submit("action", "a.mp4"); d.submit("plate", "p.mp4")
    assert seen["action"] is None and seen["plate"] == "a.mp4"
