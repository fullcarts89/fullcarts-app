from typing import List
from vfx.models import Channel

_JUDGMENT_KW = ["white balance", "hsl", "saturation", "hue", "luminance",
                "color grade", "grading", "color correct", "tone curve",
                "warm it", "cool it"]
_GUI_KW = ["mask", "feather", "keyframe", "blend mode", "blending mode",
           "opacity", "chroma", "green screen", "rotate", "crop the",
           "scale the", "brush", "eraser", "pen tool", "position the mask"]
_DRAFT_KW = ["split", "trim", "delete", "overlay", "drag", "duplicate",
             "import", "speed", "reverse", "mute", "timeline", "track",
             "in point", "out point"]


def _has(text: str, kws: List[str]) -> bool:
    return any(k in text for k in kws)


def classify_channel(text: str) -> Channel:
    """Best-effort channel for a narration-derived edit step.

    Precedence JUDGMENT > GUI > DRAFT; unknown/filler defaults to GUI so it
    surfaces in the finish-by-hand checklist (safe) rather than being
    auto-applied. This is a rough first pass; an optional LLM normalization
    step refines it later.
    """
    t = text.lower()
    if _has(t, _JUDGMENT_KW):
        return Channel.JUDGMENT
    if _has(t, _GUI_KW):
        return Channel.GUI
    if _has(t, _DRAFT_KW):
        return Channel.DRAFT
    return Channel.GUI
