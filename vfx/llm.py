import base64
import json
from typing import Any, Dict, List, Optional

MODEL = "claude-opus-4-8"

STEP_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "index": {"type": "integer"},
                    "instruction": {"type": "string"},
                    "capcut_target": {"type": "string"},
                    "channel": {"type": "string", "enum": ["DRAFT", "GUI", "JUDGMENT"]},
                },
                "required": ["index", "instruction", "capcut_target", "channel"],
            },
        }
    },
    "required": ["steps"],
}

_SYSTEM = (
    "You normalize a CapCut VFX tutorial's narration into clean, ordered, "
    "executable edit steps. Drop filler/commentary. For each real action emit: "
    "a concise imperative instruction, a capcut_target (the tool/panel, e.g. "
    "'timeline/split', 'video/mask', 'adjustment/basic'), and a channel: "
    "DRAFT (expressible in a CapCut project file: clip in/out, splits, overlay "
    "layers, text, transitions, timing), GUI (needs direct UI manipulation: "
    "mask shape, feather, blend mode, opacity, keyframes, chroma key), or "
    "JUDGMENT (subjective taste handed to the user, e.g. color grading / white "
    "balance / HSL). Index steps from 1 in execution order."
)


def build_prompt(record: Dict[str, Any]):
    user = (
        f"EFFECT: {record.get('effect','')}\n"
        f"TAGS: {', '.join(record.get('tags', []))}\n\n"
        f"FILMING STEPS:\n" + "\n".join(record.get("filming_steps", [])) + "\n\n"
        f"RAW EDITING NARRATION (convert to clean steps):\n"
        + "\n".join(f"- {s}" for s in record.get("editing_steps", []))
    )
    return _SYSTEM, user


def _encode_image(path: str, max_edge: int = 2000) -> str:
    """Base64-encode a JPEG, downscaling so the long edge <= max_edge.

    The Anthropic API rejects images whose dimensions exceed ~8000px; the tall
    breakdown infographics (e.g. 850x9690) trip that. Downscaling also caps the
    image token cost. (Very tall step-strips lose legibility here; tiling is a
    future improvement — the narration remains the primary step source.)
    """
    from PIL import Image  # lazy import; module stays importable without Pillow
    import io
    with Image.open(path) as im:
        im = im.convert("RGB")
        w, h = im.size
        longest = max(w, h)
        if longest > max_edge:
            scale = max_edge / float(longest)
            im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=85)
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


class LLM:
    """Real client. Lazy-imports anthropic so the module loads without it."""

    def __init__(self, client: Optional[Any] = None, max_tokens: int = 4000):
        self._client = client
        self.max_tokens = max_tokens

    def _ensure(self):
        if self._client is None:
            import anthropic  # lazy: only when actually calling the API
            self._client = anthropic.Anthropic()
        return self._client

    def normalize_effect(self, record: Dict[str, Any],
                         image_paths: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        client = self._ensure()
        system, user_text = build_prompt(record)
        content: List[Dict[str, Any]] = [{"type": "text", "text": user_text}]
        for p in (image_paths or []):
            content.append({"type": "image", "source": {
                "type": "base64", "media_type": "image/jpeg",
                "data": _encode_image(p)}})
        resp = client.messages.create(
            model=MODEL, max_tokens=self.max_tokens, system=system,
            thinking={"type": "adaptive"},
            output_config={"format": {"type": "json_schema", "schema": STEP_SCHEMA}},
            messages=[{"role": "user", "content": content}],
        )
        text = next(b.text for b in resp.content if b.type == "text")
        self.last_usage = getattr(resp, "usage", None)
        return json.loads(text)["steps"]
