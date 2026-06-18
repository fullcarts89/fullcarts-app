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
         "into", "out", "up", "down", "at", "as", "be", "do", "so", "just", "like",
         # generic fillers that otherwise drown out the meaningful keywords
         "have", "has", "had", "want", "wants", "make", "makes", "get", "got", "go",
         "going", "show", "shows", "talk", "talks", "talking", "see", "look", "looking",
         "take", "put", "use", "using", "will", "would", "can", "could", "should",
         "need", "really", "here", "there", "what", "when", "where", "how", "all",
         "one", "two", "first", "next", "also", "video", "clip", "clips", "effect",
         "effects", "myself", "yourself", "about", "from", "going", "want", "some"}


def _tokens(text: str) -> Set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower())
            if len(w) > 2 and w not in _STOP}


def _stem(w: str) -> str:
    """Crude stemmer so clone/cloning/clones/cloned all match (ranking only)."""
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[: -len(suf)]
            break
    return w.rstrip("e")


def recommend_for_script(recipes, script, caps, k: int = 3) -> List["ScriptMatch"]:
    """Rank recipes by (feasibility, then stemmed script-keyword overlap)."""
    # stem -> the original script word, so the "why" stays human-readable
    s_by_stem = {}
    for w in _tokens(script):
        s_by_stem.setdefault(_stem(w), w)
    out: List[ScriptMatch] = []
    for r in recipes:
        hay = " ".join([r.title, r.technique_primitive.replace("_", " "), r.summary,
                        " ".join(r.filming_steps),
                        " ".join(a.name for a in r.asset_spec)])
        hay_stems = {_stem(w) for w in _tokens(hay)}
        matched_stems = set(s_by_stem) & hay_stems
        matched_words = sorted(s_by_stem[st] for st in matched_stems)
        feas = feasibility_score(r, caps)
        score = feas * 100 + len(matched_stems)
        why_bits: List[str] = []
        if matched_words:
            why_bits.append("matches: " + ", ".join(matched_words[:5]))
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
