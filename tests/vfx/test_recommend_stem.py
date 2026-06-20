from vfx.recommender import recommend_for_script
from vfx.intake import Capabilities
from vfx.models import VFXRecipe


def _r(slug, title, prim="other", summary=""):
    return VFXRecipe(slug=slug, title=title, difficulty="beginner", editor="CapCut",
                     shot_on="phone", technique_primitive=prim, summary=summary)


def test_stemming_matches_clone_to_cloning():
    recipes = [
        _r("clone", "Your 1st Cloning Video", "split_screen_clone"),
        _r("book", "Floating Book", "keyframe_motion"),
    ]
    res = recommend_for_script(recipes, "I want to clone myself", Capabilities(), k=2)
    assert res[0].recipe.slug == "clone"
    assert "clone" in res[0].why          # original script word shown, not the stem


def test_no_false_positive_when_unrelated():
    recipes = [_r("book", "Floating Book", "keyframe_motion")]
    res = recommend_for_script(recipes, "clone myself talking", Capabilities(), k=1)
    assert "matches:" not in res[0].why   # no spurious overlap
