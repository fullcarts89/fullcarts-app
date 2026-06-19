"""Computer-use subsystem: drive CapCut's GUI-only steps on the user's Mac.

Pairs with the file-writer (vfx/capcut): the draft writer assembles everything
expressible as data; this drives the genuine button-clicks (Remove Background,
sticker/particle effects) that can't live in the project file.
"""
from vfx.computer_use.executor import Action, DryRunExecutor, Executor, MacExecutor
from vfx.computer_use.runner import RunResult, run_task
from vfx.computer_use.task import build_task, gui_steps

__all__ = [
    "Action", "Executor", "DryRunExecutor", "MacExecutor",
    "run_task", "RunResult", "build_task", "gui_steps",
]
