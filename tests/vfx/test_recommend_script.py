from vfx.models import VFXRecipe, AssetSpec
from vfx.intake import Capabilities
from vfx.recommender import recommend_for_script, ScriptMatch


def _clone():
    return VFXRecipe(
        slug="clone", title="Clone Effect", difficulty="beginner",
        editor="CapCut", shot_on="phone",
        technique_primitive="overlay_bg_removal_clone",
        summary="make a clone of yourself standing next to you",
        asset_spec=[AssetSpec(name="empty", type="shot"),
                    AssetSpec(name="person", type="shot")],
        filming_steps=["empty: film the empty room", "person: step in"],
    )


def _tripod_locked():
    return VFXRecipe(
        slug="freeze", title="Freeze Frame", difficulty="beginner",
        editor="CapCut", shot_on="phone",
        technique_primitive="freeze_frame",
        summary="dramatic freeze frame of a jump",
        asset_spec=[AssetSpec(name="jump", type="shot",
                              capture_requirements={"locked_off": True})],
        filming_steps=["jump: jump in the air"],
    )


def _teleport():
    return VFXRecipe(
        slug="teleport", title="Teleport", difficulty="intermediate",
        editor="CapCut", shot_on="phone",
        technique_primitive="match_cut_teleport",
        summary="teleport across the city",
        asset_spec=[AssetSpec(name="a", type="shot")],
        filming_steps=["a: walk out of frame"],
    )


def test_script_match_feasible_ranks_first():
    recipes = [_teleport(), _tripod_locked(), _clone()]
    caps = Capabilities(equipment=[], props=[], location="home")
    out = recommend_for_script(recipes, "I want to make a clone of myself", caps, k=3)
    assert isinstance(out[0], ScriptMatch)
    assert out[0].recipe.slug == "clone"
    assert "clone" in out[0].why
    assert out[0].feasible is True


def test_recipe_needing_missing_gear_is_infeasible():
    recipes = [_tripod_locked()]
    caps = Capabilities(equipment=[], props=[], location="home")
    out = recommend_for_script(recipes, "a freeze frame jump", caps, k=3)
    match = next(m for m in out if m.recipe.slug == "freeze")
    assert match.feasible is False
    assert "missing some gear" in match.why


def test_gear_present_makes_feasible():
    recipes = [_tripod_locked()]
    caps = Capabilities(equipment=["tripod"], props=[], location="home")
    out = recommend_for_script(recipes, "a freeze frame jump", caps, k=3)
    assert out[0].feasible is True
