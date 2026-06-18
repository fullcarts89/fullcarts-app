from vfx.capcut.checklist import build_filming_plan, build_checklist
from vfx.models import VFXRecipe, EditStep, AssetSpec, Channel


def _recipe():
    return VFXRecipe(slug="x", title="X Effect", difficulty="beginner", editor="CapCut",
        shot_on="phone", technique_primitive="t", summary="s", gear="tripod",
        asset_spec=[AssetSpec(name="action", type="shot",
                              capture_requirements={"locked_off": True},
                              acceptance_checks=["camera_locked_off"])],
        filming_steps=["Snap and drink."],
        edit_steps=[
            EditStep(index=1, instruction="Split the clip.", capcut_target="timeline/split", channel=Channel.DRAFT),
            EditStep(index=2, instruction="Add a mask.", capcut_target="video/mask", channel=Channel.GUI),
            EditStep(index=3, instruction="Fix white balance.", capcut_target="adjustment/basic", channel=Channel.JUDGMENT),
        ])


def test_filming_plan_lists_shots_and_gear():
    out = build_filming_plan(_recipe())
    assert "X Effect" in out and "action (shot)" in out and "locked_off" in out
    assert "tripod" in out and "Snap and drink." in out


def test_checklist_only_gui_and_judgment():
    out = build_checklist(_recipe())
    assert "Add a mask." in out and "Fix white balance." in out
    assert "Split the clip." not in out  # DRAFT steps are assembled, not hand-done


def test_checklist_empty_when_all_draft():
    r = _recipe(); r.edit_steps = [EditStep(index=1, instruction="Split.", capcut_target="timeline/split", channel=Channel.DRAFT)]
    assert "assembled automatically" in build_checklist(r)
