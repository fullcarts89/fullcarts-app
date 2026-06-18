import re
from dataclasses import dataclass
from typing import List, Set
from vfx.models import VFXRecipe
from vfx.intake import Capabilities, requirement_met


@dataclass
class ScriptMatch:
    recipe: VFXRecipe
    score: float
    why: str
    feasible: bool


_STOP = {"the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "you", "your",
         "i", "it", "is", "are", "this", "that", "my", "me", "we", "they", "them", "then",
         "into", "out", "up", "down", "at", "as", "be", "do", "so", "just", "like"}


def _tokens(text: str) -> Set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower())
            if len(w) > 2 and w not in _STOP}


def recommend_for_script(recipes, script, caps, k: int = 3) -> List["ScriptMatch"]:
    """Rank recipes by (feasibility, then script keyword overlap)."""
    s_tokens = _tokens(script)
    out: List[ScriptMatch] = []
    for r in recipes:
        hay = " ".join([r.title, r.technique_primitive.replace("_", " "), r.summary,
                        " ".join(r.filming_steps),
                        " ".join(a.name for a in r.asset_spec)])
        overlap = s_tokens & _tokens(hay)
        feas = feasibility_score(r, caps)
        score = feas * 100 + len(overlap)
        why_bits: List[str] = []
        if overlap:
            why_bits.append("matches: " + ", ".join(sorted(overlap)[:5]))
        why_bits.append("gear OK" if feas >= 1.0 else "missing some gear")
        out.append(ScriptMatch(r, score, "; ".join(why_bits), feas >= 1.0))
    out.sort(key=lambda m: m.score, reverse=True)
    return out[:k]


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
