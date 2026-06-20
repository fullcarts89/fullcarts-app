"""Computer-use control loop: screenshot -> model -> action -> repeat.

Desktop-agnostic. Given a task string, it drives an :class:`Executor` using the
Anthropic *computer-use* tool until the model stops requesting actions or a step
budget is hit. The Anthropic client is injectable so the loop is unit-tested with
a scripted fake (no API spend); production builds the real client lazily.

Safety rails baked in (the user's machine + money are on the line):
  - ``max_steps`` hard cap (default 60) so a confused model can't loop forever.
  - ``confirm`` callback fires before *every* action; returning False aborts.
  - ``on_event`` callback streams a human-readable log of what's happening.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

from vfx.computer_use.executor import Action, Executor

# Anthropic computer-use tool. The tool-type string AND its matching beta header
# depend on the model: Opus 4.5+/4.6/4.7/4.8 and Sonnet 4.6 use the newer
# computer_20251124 (zoom); older 4.x models use computer_20250124. Pairing the
# wrong version with a model returns a 400 ("does not support tool types"). Verified
# against platform.claude.com computer-use-tool docs (2026-06).
_NEW_TOOL = ("computer_20251124", "computer-use-2025-11-24")
_OLD_TOOL = ("computer_20250124", "computer-use-2025-01-24")
_NEW_MODELS = ("opus-4-8", "opus-4-7", "opus-4-6", "opus-4-5", "sonnet-4-6")
_DEFAULT_MODEL = "claude-opus-4-8"


def _computer_tool_for(model: str):
    m = (model or "").lower()
    return _NEW_TOOL if any(tag in m for tag in _NEW_MODELS) else _OLD_TOOL

# Map the tool's action names -> our Action.kind (those we execute directly).
_CLICK_KINDS = {
    "left_click": "left_click",
    "double_click": "double_click",
    "right_click": "right_click",
    "mouse_move": "mouse_move",
}


@dataclass
class RunResult:
    completed: bool                       # model ended on its own (not budget-capped)
    steps: int
    transcript: List[str] = field(default_factory=list)


def _to_action(name: str, inp: dict) -> Optional[Action]:
    """Translate a computer tool_use input into an Action (None = just re-shoot)."""
    coord = inp.get("coordinate") or [None, None]
    x, y = (coord + [None, None])[:2]
    if name == "screenshot":
        return Action("screenshot")
    if name in _CLICK_KINDS:
        return Action(_CLICK_KINDS[name], x=x, y=y)
    if name == "type":
        return Action("type", text=inp.get("text"))
    if name == "key":
        return Action("key", text=inp.get("text"))
    if name == "scroll":
        return Action("scroll", x=x, y=y,
                      scroll_direction=inp.get("scroll_direction"),
                      scroll_amount=inp.get("scroll_amount"))
    if name == "wait":
        return Action("wait")
    return Action("screenshot")  # unknown -> safe re-screenshot


def _img_block(png: bytes) -> dict:
    return {"type": "image", "source": {
        "type": "base64", "media_type": "image/png",
        "data": base64.standard_b64encode(png).decode("ascii")}}


_MEDIA_BY_EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                 ".webp": "image/webp", ".gif": "image/gif"}


def _file_img_block(path: str) -> dict:
    import os
    data = open(path, "rb").read()
    media = _MEDIA_BY_EXT.get(os.path.splitext(path)[1].lower(), "image/jpeg")
    return {"type": "image", "source": {
        "type": "base64", "media_type": media,
        "data": base64.standard_b64encode(data).decode("ascii")}}


def _describe(action: Action) -> str:
    if action.kind in ("left_click", "double_click", "right_click", "mouse_move"):
        return f"{action.kind} @ ({action.x},{action.y})"
    if action.kind == "type":
        return f"type {action.text!r}"
    if action.kind == "key":
        return f"key {action.text!r}"
    return action.kind


def run_task(
    task: str,
    executor: Executor,
    client: Optional[Any] = None,
    model: str = _DEFAULT_MODEL,
    max_steps: int = 60,
    max_tokens: int = 1500,
    confirm: Optional[Callable[[Action], bool]] = None,
    on_event: Optional[Callable[[str], None]] = None,
    reference_images: Optional[List[tuple]] = None,
) -> RunResult:
    width, height = executor.dimensions()
    tool_type, beta = _computer_tool_for(model)
    tools = [{"type": tool_type, "name": "computer",
              "display_width_px": width, "display_height_px": height}]

    def log(msg: str) -> None:
        if on_event:
            on_event(msg)

    if client is None:
        import anthropic  # lazy
        client = anthropic.Anthropic()

    # Seed with the task, any reference screenshots (visual grounding), then the
    # live desktop screenshot. The references come from the tutorial/manual so the
    # model can match "the control the creator used" to the desktop UI in front of
    # it — even when a step doesn't spell out which button to click.
    seed: List[dict] = [{"type": "text", "text": task}]
    refs = reference_images or []
    if refs:
        seed.append({"type": "text", "text": (
            "\nREFERENCE SCREENSHOTS (from the tutorial — what each step should "
            "look like; they may be from CapCut mobile, so match by feature, not "
            "position):")})
        for caption, path in refs:
            try:
                block = _file_img_block(path)
            except OSError:
                continue
            seed.append({"type": "text", "text": caption})
            seed.append(block)
        log(f"attached {sum(1 for c in seed if c.get('type') == 'image')} reference image(s)")
    seed.append({"type": "text", "text": "\nYOUR CURRENT DESKTOP SCREEN:"})
    seed.append(_img_block(executor.screenshot()))
    messages: List[dict] = [{"role": "user", "content": seed}]
    transcript: List[str] = []

    steps = 0
    while steps < max_steps:
        resp = client.beta.messages.create(
            model=model, max_tokens=max_tokens, tools=tools,
            betas=[beta], messages=messages)
        assistant_content: List[dict] = []
        tool_results: List[dict] = []
        used_tool = False

        for block in resp.content:
            btype = getattr(block, "type", None)
            if btype == "text":
                txt = getattr(block, "text", "")
                transcript.append(txt)
                log(f"… {txt.strip()[:160]}")
                assistant_content.append({"type": "text", "text": txt})
            elif btype == "tool_use":
                used_tool = True
                inp = block.input or {}
                action = _to_action(inp.get("action", ""), inp)
                assistant_content.append({
                    "type": "tool_use", "id": block.id,
                    "name": block.name, "input": block.input})
                if confirm is not None and action.kind != "screenshot" \
                        and not confirm(action):
                    log(f"ABORTED before: {_describe(action)}")
                    messages.append({"role": "assistant", "content": assistant_content})
                    return RunResult(False, steps, transcript)
                log(_describe(action))
                executor.perform(action)
                shot = executor.screenshot()
                tool_results.append({
                    "type": "tool_result", "tool_use_id": block.id,
                    "content": [_img_block(shot)]})

        messages.append({"role": "assistant", "content": assistant_content})
        steps += 1

        if not used_tool or getattr(resp, "stop_reason", None) == "end_turn":
            log("done.")
            return RunResult(True, steps, transcript)
        messages.append({"role": "user", "content": tool_results})

    log(f"stopped: hit max_steps={max_steps}")
    return RunResult(False, steps, transcript)
