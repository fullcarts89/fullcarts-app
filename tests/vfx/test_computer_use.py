from types import SimpleNamespace

from vfx.computer_use import DryRunExecutor, run_task, build_task, gui_steps
from vfx.computer_use.executor import Action
from vfx.ingest.manual_schema import load_manual


def _text(t):
    return SimpleNamespace(type="text", text=t)


def _tool(id, name, inp):
    return SimpleNamespace(type="tool_use", id=id, name=name, input=inp)


def _resp(content, stop_reason="tool_use"):
    return SimpleNamespace(content=content, stop_reason=stop_reason)


class _ScriptedClient:
    """Returns a queued list of responses, one per create() call."""
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    class _Beta:
        def __init__(self, outer): self.outer = outer

        class _Messages:
            def __init__(self, outer): self.outer = outer
            def create(self, **kw):
                self.outer.calls.append(kw)
                return self.outer._responses.pop(0)

        @property
        def messages(self):
            return _ScriptedClient._Beta._Messages(self.outer)

    @property
    def beta(self):
        return _ScriptedClient._Beta(self)


def test_loop_performs_action_then_finishes():
    ex = DryRunExecutor()
    client = _ScriptedClient([
        _resp([_text("clicking remove bg"),
               _tool("t1", "computer", {"action": "left_click", "coordinate": [100, 200]})]),
        _resp([_text("all done")], stop_reason="end_turn"),
    ])
    res = run_task("do the thing", ex, client=client, max_steps=10)
    assert res.completed and res.steps == 2
    # the click landed on the executor
    clicks = [a for a in ex.actions if a.kind == "left_click"]
    assert clicks and clicks[0].x == 100 and clicks[0].y == 200
    # tool config + beta header were sent
    assert client.calls[0]["tools"][0]["type"].startswith("computer_")
    assert "computer-use" in client.calls[0]["betas"][0]


def test_confirm_false_aborts_before_action():
    ex = DryRunExecutor()
    client = _ScriptedClient([
        _resp([_tool("t1", "computer", {"action": "left_click", "coordinate": [5, 5]})]),
    ])
    res = run_task("x", ex, client=client, confirm=lambda a: False)
    assert not res.completed
    assert not any(a.kind == "left_click" for a in ex.actions)  # never performed


def test_max_steps_cap():
    ex = DryRunExecutor()
    # always asks for another click -> never ends on its own
    forever = [_resp([_tool(f"t{i}", "computer",
                            {"action": "left_click", "coordinate": [1, 1]})])
               for i in range(10)]
    res = run_task("loop", ex, client=_ScriptedClient(forever), max_steps=3)
    assert not res.completed and res.steps == 3


def test_build_task_only_includes_gui_steps():
    recipe = load_manual("vfx_instructions/manuals/package_morph_transition.json")
    steps = gui_steps(recipe)
    joined = " ".join(steps).lower()
    # GUI-only effects present
    assert any("remove background" in s.lower() for s in steps)
    assert any("sticker" in s.lower() or "dust" in s.lower() for s in steps)
    # structural steps (import/overlay/transition/text) excluded
    assert "import" not in joined and "overlay" not in joined
    task = build_task(recipe)
    assert task and "CapCut" in task and "STEPS" in task


# --- Q1: reference-screenshot grounding -----------------------------------

def _png(path):
    import subprocess
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                    "-i", "color=c=blue:size=64x64:duration=0.1",
                    "-frames:v", "1", str(path)], check=True)
    return str(path)


def test_reference_blocks_step_aligned(tmp_path):
    from vfx.computer_use import reference_blocks
    from vfx.models import VFXRecipe, EditStep, Channel
    img = _png(tmp_path / "step.png")
    r = VFXRecipe(slug="x", title="X", difficulty="b", editor="CapCut", shot_on="phone",
                  technique_primitive="other", summary="",
                  edit_steps=[EditStep(1, "Remove Background", "rbg",
                                       channel=Channel.GUI, reference_screenshot=img)])
    blocks = reference_blocks(r)
    assert len(blocks) == 1 and blocks[0][1] == img and "step 1" in blocks[0][0].lower()


def test_reference_blocks_general_fallback_and_missing_skipped(tmp_path):
    from vfx.computer_use import reference_blocks
    from vfx.models import VFXRecipe
    img = _png(tmp_path / "frame.png")
    r = VFXRecipe(slug="x", title="X", difficulty="b", editor="CapCut", shot_on="phone",
                  technique_primitive="other", summary="",
                  reference_images=[img, "/does/not/exist.jpg"])
    blocks = reference_blocks(r, max_general=4)
    assert len(blocks) == 1 and blocks[0][1] == img      # missing one skipped
    assert "not step-aligned" in blocks[0][0]


def test_runner_injects_reference_images_into_seed(tmp_path):
    img = _png(tmp_path / "ref.png")
    ex = DryRunExecutor()
    client = _ScriptedClient([_resp([_text("done")], stop_reason="end_turn")])
    run_task("t", ex, client=client, reference_images=[("Reference for step 1", img)])
    seed = client.calls[0]["messages"][0]["content"]
    images = [b for b in seed if b.get("type") == "image"]
    # one reference image + the live screenshot
    assert len(images) == 2
    assert any(b.get("type") == "text" and "Reference for step 1" in b["text"] for b in seed)


def test_manual_schema_reads_reference_screenshot(tmp_path):
    import json
    from vfx.ingest.manual_schema import load_manual
    m = {
        "id": "t", "technique_primitive": "other", "title": "T",
        "inputs": [{"name": "a", "what_to_film": "x"}],
        "edit_steps": [{"action": "remove_background", "target": "a",
                        "channel": "ui", "reference_screenshot": "assets/t/s1.jpg"}],
    }
    p = tmp_path / "m.json"; p.write_text(json.dumps(m))
    r = load_manual(p)
    assert r.edit_steps[0].reference_screenshot == "assets/t/s1.jpg"


def test_reference_coverage_three_states(tmp_path):
    from vfx.computer_use import reference_coverage
    from vfx.models import VFXRecipe, EditStep, Channel
    present = _png(tmp_path / "ok.png")
    r = VFXRecipe(slug="x", title="X", difficulty="b", editor="CapCut", shot_on="phone",
                  technique_primitive="other", summary="", edit_steps=[
        EditStep(1, "has shot", "a", channel=Channel.GUI, reference_screenshot=present),
        EditStep(2, "declared missing", "b", channel=Channel.GUI,
                 reference_screenshot="/nope/missing.jpg"),
        EditStep(3, "no ref", "c", channel=Channel.GUI),
        EditStep(4, "structural ignored", "d", channel=Channel.DRAFT),
    ])
    cov = reference_coverage(r)
    assert [c.status for c in cov] == ["ok", "missing", "none"]   # DRAFT excluded
    assert cov[0].resolved == present


def test_morph_manual_declares_step_screenshots():
    from vfx.computer_use import reference_coverage
    from vfx.ingest.manual_schema import load_manual
    r = load_manual("vfx_instructions/manuals/package_morph_transition.json")
    cov = reference_coverage(r)
    declared = [c for c in cov if c.declared]
    assert len(declared) >= 3   # keyframe scale, dust sticker, remove bg
    assert all(c.declared.startswith("assets/package_morph_transition/") for c in declared)
