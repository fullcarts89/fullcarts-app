from vfx.db import RecipeStore
from vfx.models import VFXRecipe

def _recipe():
    return VFXRecipe(slug="s1", title="T", difficulty="beginner", editor="CapCut",
                     shot_on="phone", technique_primitive="clean_plate_mask_reveal",
                     summary="x")

def test_put_get_roundtrip(tmp_path):
    store = RecipeStore(tmp_path / "vfx.db")
    store.put(_recipe())
    got = store.get("s1")
    assert got.title == "T"

def test_list_and_query_by_primitive(tmp_path):
    store = RecipeStore(tmp_path / "vfx.db")
    store.put(_recipe())
    assert [r.slug for r in store.by_primitive("clean_plate_mask_reveal")] == ["s1"]
    assert store.get("missing") is None
    assert [r.slug for r in store.all()] == ["s1"]
