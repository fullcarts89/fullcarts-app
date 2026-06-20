"""Vision content-check: does `old_pack` show the SAME product as `current_pack`?

The deterministic probes (resolution/duration/lock-off) verify technical specs
but cannot tell a Kraft box from a tissue box. For the morph format that gap is
fatal -- the two assets MUST be the same product, just a different size. This
module asks a vision model to compare a frame from each asset.

Cost: one API call per check (two downscaled frames + a short prompt). Defaults
to Claude Haiku (cheapest sensible). It is only invoked when an API key is
present; callers degrade to a manual-confirm flag otherwise (see gate.py), so
nothing here ever spends money without the key being set.
"""
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

from vfx.llm import _encode_image

PathLike = Union[str, Path]

# Cheapest sensible vision model; the extraction pipeline already uses Haiku.
HAIKU = "claude-haiku-4-5-20251001"

_SYSTEM = (
    "You verify assets for a shrinkflation 'morph' video, where a product's "
    "CURRENT package visually morphs into its OLDER, LARGER version. The two "
    "images MUST be the same product (same brand + item), only a different "
    "size. Image A is the CURRENT package; Image B is the proposed OLDER/LARGER "
    "package. Judge identity strictly: a different product category (e.g. a "
    "tissue box vs a snack box) is NOT a match. Size cues from a single photo "
    "are unreliable, so only mark old_clearly_smaller when B is unmistakably the "
    "smaller item. Be concise and literal."
)

_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "same_product": {"type": "boolean"},
        "current_label": {"type": "string"},
        "old_label": {"type": "string"},
        "old_clearly_smaller": {"type": "boolean"},
        "confidence": {"type": "number"},
        "reason": {"type": "string"},
    },
    "required": ["same_product", "current_label", "old_label",
                 "old_clearly_smaller", "confidence", "reason"],
}


@dataclass
class ContentVerdict:
    passed: bool
    same_product: bool
    old_clearly_smaller: bool
    confidence: float
    detail: str


def frame_jpeg(path: PathLike, out_path: PathLike) -> Path:
    """Extract one display-oriented frame as JPEG (works for video OR image).

    ffmpeg auto-applies the display-matrix rotation, so an iPhone portrait clip
    yields an upright frame -- matching what the resolution probe now judges.
    """
    out = Path(out_path)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(path), "-frames:v", "1", str(out)],
        capture_output=True, check=True)
    return out


def compare_products(
    current_path: PathLike,
    old_path: PathLike,
    client: Optional[Any] = None,
    model: str = HAIKU,
    min_confidence: float = 0.55,
) -> ContentVerdict:
    """Compare the two assets. Pass = same product AND not clearly-smaller-old.

    ``client`` is an Anthropic-style client (injectable for tests). When None it
    is lazily constructed (requires ANTHROPIC_API_KEY) -- so importing this
    module never needs the SDK or a key.
    """
    with tempfile.TemporaryDirectory() as td:
        a = frame_jpeg(current_path, Path(td) / "a.jpg")
        b = frame_jpeg(old_path, Path(td) / "b.jpg")
        content = [
            {"type": "text", "text": "Image A = CURRENT package:"},
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                         "data": _encode_image(str(a))}},
            {"type": "text", "text": "Image B = proposed OLDER/LARGER package:"},
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                         "data": _encode_image(str(b))}},
            {"type": "text", "text": "Are A and B the same product? Respond per schema."},
        ]
        if client is None:
            import anthropic  # lazy
            client = anthropic.Anthropic()
        resp = client.messages.create(
            model=model, max_tokens=600, system=_SYSTEM,
            output_config={"format": {"type": "json_schema", "schema": _SCHEMA}},
            messages=[{"role": "user", "content": content}],
        )
        data = json.loads(next(blk.text for blk in resp.content if blk.type == "text"))

    same = bool(data["same_product"])
    smaller = bool(data["old_clearly_smaller"])
    conf = float(data["confidence"])
    passed = same and (not smaller) and conf >= min_confidence
    bits = [
        ("same product" if same else "DIFFERENT product"),
        f"A={data['current_label']!r}", f"B={data['old_label']!r}",
        f"conf={conf:.2f}",
    ]
    if smaller:
        bits.append("B looks SMALLER, not larger")
    bits.append(data["reason"])
    return ContentVerdict(passed=passed, same_product=same,
                          old_clearly_smaller=smaller, confidence=conf,
                          detail="; ".join(bits))
