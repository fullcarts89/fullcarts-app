from vfx.recommender import feasibility_score, top_recipes
from vfx.intake import Capabilities
from vfx.models import VFXRecipe, AssetSpec


def _r(slug, reqs):
    return VFXRecipe(slug=slug, title=slug, difficulty="beginner", editor="CapCut",
                     shot_on="phone", technique_primitive="x", summary="x",
                     asset_spec=[AssetSpec(name="a", type="shot", capture_requirements=r)
                                 for r in reqs])


def test_no_requirements_scores_full():
    assert feasibility_score(_r("free", [{}]), Capabilities()) == 1.0


def test_locked_off_needs_tripod():
    r = _r("lock", [{"locked_off": True}])
    assert feasibility_score(r, Capabilities(equipment=["tripod"])) == 1.0
    assert feasibility_score(r, Capabilities()) == 0.0


def test_partial_satisfaction():
    r = _r("mix", [{"locked_off": True}, {"green_screen": True}])
    score = feasibility_score(r, Capabilities(equipment=["tripod"]))
    assert 0.0 < score < 1.0


def test_top_recipes_ranks_feasible_first():
    caps = Capabilities(equipment=["tripod"])
    recipes = [_r("gs", [{"green_screen": True}]), _r("easy", [{}]), _r("lock", [{"locked_off": True}])]
    top = top_recipes(recipes, caps, k=2)
    assert top[0].slug in ("easy", "lock")
    assert len(top) == 2


def test_real_dataset_smoke(tmp_path):
    from vfx.db import RecipeStore
    from vfx.ingest.vfxdata import ingest_all
    store = RecipeStore(tmp_path / "vfx.db"); ingest_all(store)
    top = top_recipes(store.all(), Capabilities(equipment=["tripod", "phone"]), k=3)
    assert len(top) == 3
