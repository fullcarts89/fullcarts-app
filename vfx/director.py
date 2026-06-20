from typing import Dict, Optional
from vfx.models import VFXRecipe, AssetSpec
from vfx.qa.gate import check_asset, Verdict


class AssetDirector:
    """Collects the recipe's assets one at a time, gating each on QA."""

    def __init__(self, recipe: VFXRecipe):
        self.recipe = recipe
        self.accepted: Dict[str, str] = {}  # asset name -> media path

    def pending(self) -> Optional[AssetSpec]:
        for a in self.recipe.asset_spec:
            if a.name not in self.accepted:
                return a
        return None

    def complete(self) -> bool:
        return self.pending() is None

    def submit(self, name: str, path: str) -> Verdict:
        spec = next(a for a in self.recipe.asset_spec if a.name == name)
        # reference for camera_locked_off: the first already-accepted shot
        ref = next(iter(self.accepted.values()), None)
        verdict = check_asset(spec, path, ref_path=ref)
        if verdict.passed:
            self.accepted[name] = path
        return verdict
