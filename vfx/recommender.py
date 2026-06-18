from typing import List
from vfx.models import VFXRecipe
from vfx.intake import Capabilities, requirement_met


def feasibility_score(recipe: VFXRecipe, caps: Capabilities) -> float:
    reqs = [a.capture_requirements for a in recipe.asset_spec]
    if not reqs:
        return 1.0
    met = sum(1 for r in reqs if requirement_met(r, caps))
    return met / len(reqs)


def top_recipes(recipes: List[VFXRecipe], caps: Capabilities,
                k: int = 3) -> List[VFXRecipe]:
    ranked = sorted(recipes, key=lambda r: feasibility_score(r, caps), reverse=True)
    return ranked[:k]
