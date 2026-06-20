"""Executors carry out computer-use actions on a real (or fake) desktop.

The runner (``runner.py``) is desktop-agnostic: it asks an Executor to take a
screenshot and to perform mouse/keyboard actions. This split lets us unit-test
the control loop with a ``DryRunExecutor`` (records actions, returns a blank
screenshot) and run for real on macOS with ``MacExecutor`` -- which shells out to
the built-in ``screencapture`` plus ``cliclick`` for input.

Why this exists: CapCut only runs on the user's Mac, not in our sandbox. So the
loop is authored + tested here; the MacExecutor is the part that touches their
machine. Keeping input behind a tiny interface also means a future Windows/Linux
executor is a drop-in.
"""
from __future__ import annotations

import base64
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Protocol, Tuple


@dataclass
class Action:
    """One computer-use action requested by the model."""
    kind: str                      # screenshot|left_click|double_click|type|key|mouse_move|scroll|wait
    x: Optional[int] = None
    y: Optional[int] = None
    text: Optional[str] = None     # for type / key
    scroll_direction: Optional[str] = None
    scroll_amount: Optional[int] = None


class Executor(Protocol):
    def screenshot(self) -> bytes: ...          # PNG bytes
    def dimensions(self) -> Tuple[int, int]: ...  # (width, height) the model reasons in
    def perform(self, action: Action) -> None: ...


@dataclass
class DryRunExecutor:
    """Records actions; returns a 1x1 PNG. For tests + 'plan only' dry runs."""
    width: int = 1366
    height: int = 768
    actions: List[Action] = field(default_factory=list)
    # a minimal valid 1x1 transparent PNG
    _PNG: bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

    def screenshot(self) -> bytes:
        self.actions.append(Action("screenshot"))
        return self._PNG

    def dimensions(self) -> Tuple[int, int]:
        return (self.width, self.height)

    def perform(self, action: Action) -> None:
        self.actions.append(action)


class MacExecutor:
    """Real macOS executor: ``screencapture`` for frames, ``cliclick`` for input.

    Requires (one-time):
      - ``brew install cliclick`` (mouse/keyboard driver)
      - System Settings → Privacy & Security → grant the terminal/app
        **Screen Recording** and **Accessibility**.
    Untested in our sandbox (no macOS/CapCut here) -- validated on the user's Mac.
    """

    def __init__(self, width: int = 1366, height: int = 768):
        self._w, self._h = width, height
        if shutil.which("screencapture") is None:
            raise RuntimeError("screencapture not found -- MacExecutor needs macOS")
        self._cliclick = shutil.which("cliclick")
        if self._cliclick is None:
            raise RuntimeError("cliclick not found -- run: brew install cliclick")

    def dimensions(self) -> Tuple[int, int]:
        return (self._w, self._h)

    def screenshot(self) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tmp:
            subprocess.run(["screencapture", "-x", "-C", tmp.name], check=True)
            return Path(tmp.name).read_bytes()

    def perform(self, action: Action) -> None:
        cc = self._cliclick
        a = action
        if a.kind == "screenshot":
            return
        if a.kind == "mouse_move":
            subprocess.run([cc, f"m:{a.x},{a.y}"], check=True)
        elif a.kind == "left_click":
            subprocess.run([cc, f"c:{a.x},{a.y}"], check=True)
        elif a.kind == "double_click":
            subprocess.run([cc, f"dc:{a.x},{a.y}"], check=True)
        elif a.kind == "right_click":
            subprocess.run([cc, f"rc:{a.x},{a.y}"], check=True)
        elif a.kind == "type":
            subprocess.run([cc, f"t:{a.text or ''}"], check=True)
        elif a.kind == "key":
            # cliclick key presses, e.g. "return", "esc"; pass through key name
            subprocess.run([cc, f"kp:{a.text or ''}"], check=True)
        elif a.kind == "scroll":
            # cliclick has no native scroll; no-op + caller can fall back.
            pass
        elif a.kind == "wait":
            subprocess.run(["sleep", "1"], check=True)
        else:
            raise ValueError(f"unknown action kind: {a.kind!r}")
