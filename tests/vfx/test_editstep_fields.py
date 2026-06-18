from vfx.models import EditStep, Channel, VFXRecipe


def test_editstep_action_target_default_none():
    s = EditStep(index=1, instruction="x", capcut_target="overlay")
    assert s.action is None and s.target is None


def test_editstep_roundtrip_with_action():
    s = EditStep(index=1, instruction="x", capcut_target="overlay",
                 channel=Channel.DRAFT, action="overlay", target="stepin_clip")
    r = VFXRecipe(slug="s", title="t", difficulty="b", editor="CapCut", shot_on="phone",
                  technique_primitive="p", summary="", edit_steps=[s])
    back = VFXRecipe.from_dict(r.to_dict())
    assert back.edit_steps[0].action == "overlay" and back.edit_steps[0].target == "stepin_clip"
