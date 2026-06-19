"""Manuals-backed recipe source.

Reads the canonical ``vfx_instructions`` manual catalog live (via the
``Manuals`` loader) and converts each manual to a :class:`VFXRecipe`. This is
the web app's default recipe source, replacing the baked-in sqlite.
"""
from typing import List, Optional

from vfx.models import VFXRecipe
from vfx.ingest.manual_schema import manual_to_recipe


def _loader():
    from vfx_instructions.vfx_loader import Manuals
    return Manuals()


def all_recipes() -> List[VFXRecipe]:
    """Every manual in the canonical catalog, as VFXRecipes (skips any that fail to convert)."""
    out: List[VFXRecipe] = []
    loader = _loader()
    for row in loader.index:
        try:
            full = loader.get(row["id"])
            if full:
                out.append(manual_to_recipe(full))
        except Exception:
            continue
    return out


def get_recipe(mid: str) -> Optional[VFXRecipe]:
    loader = _loader()
    full = loader.get(mid)
    if not full:
        return None
    try:
        return manual_to_recipe(full)
    except Exception:
        return None
