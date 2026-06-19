from vfx.ingest.manuals_source import all_recipes, get_recipe
from vfx.models import VFXRecipe


def test_all_recipes_loads_catalog():
    rs = all_recipes()
    assert len(rs) >= 15
    assert all(isinstance(r, VFXRecipe) for r in rs)


def test_get_recipe_clone():
    r = get_recipe("clone_effect_talking_head")
    assert r is not None
    assert len(r.asset_spec) >= 2


def test_get_recipe_missing_returns_none():
    assert get_recipe("does_not_exist_zzz") is None


def test_at_least_one_ai_recipe():
    rs = all_recipes()
    ai = [r for r in rs if r.is_ai_generated and r.ai_generation]
    assert ai, "expected at least one AI-generated recipe with ai_generation"


def test_ai_location_transition_is_ai():
    r = get_recipe("ai_location_transition")
    assert r is not None
    assert r.is_ai_generated is True
    assert r.ai_generation
