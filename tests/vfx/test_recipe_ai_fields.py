from vfx.models import VFXRecipe


def _base(**kw):
    d = dict(slug="x", title="X", difficulty="beginner", editor="CapCut",
             shot_on="phone", technique_primitive="overlay", summary="s")
    d.update(kw)
    return VFXRecipe(**d)


def test_ai_fields_roundtrip():
    r = _base(is_ai_generated=True, ai_generation=[{"provider": "kling"}])
    r2 = VFXRecipe.from_dict(r.to_dict())
    assert r2.is_ai_generated is True
    assert r2.ai_generation == [{"provider": "kling"}]


def test_defaults_when_missing():
    r = _base()
    assert r.is_ai_generated is False
    assert r.ai_generation == []


def test_from_dict_missing_ai_keys_loads():
    d = _base().to_dict()
    d.pop("is_ai_generated", None)
    d.pop("ai_generation", None)
    r = VFXRecipe.from_dict(d)
    assert r.is_ai_generated is False
    assert r.ai_generation == []
