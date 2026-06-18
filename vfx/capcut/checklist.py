from typing import List
from vfx.models import VFXRecipe, Channel


def build_filming_plan(recipe: VFXRecipe) -> str:
    lines: List[str] = [f"# Filming plan: {recipe.title}", ""]
    if recipe.gear:
        lines.append(f"Gear: {recipe.gear}")
        lines.append("")
    lines.append("## Shots to capture (in order)")
    for i, a in enumerate(recipe.asset_spec, 1):
        reqs = ", ".join(k for k, v in a.capture_requirements.items() if v) or "no special setup"
        checks = ", ".join(a.acceptance_checks) or "—"
        lines.append(f"{i}. {a.name} ({a.type}) — {reqs}; checks: {checks}")
    lines.append("")
    lines.append("## Filming notes")
    for s in recipe.filming_steps:
        lines.append(f"- {s}")
    return "\n".join(lines)


def build_checklist(recipe: VFXRecipe) -> str:
    lines: List[str] = [f"# Finish-by-hand steps: {recipe.title}", ""]
    n = 0
    for s in recipe.edit_steps:
        if s.channel in (Channel.GUI, Channel.JUDGMENT):
            n += 1
            ref = f"  (ref: {s.reference_screenshot})" if s.reference_screenshot else ""
            lines.append(f"{n}. [{s.channel.value}] {s.instruction}{ref}")
    if n == 0:
        lines.append("_All edit steps can be assembled automatically (no GUI/JUDGMENT steps)._")
    return "\n".join(lines)
