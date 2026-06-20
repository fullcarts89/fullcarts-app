from vfx.ingest.manual_schema import load_manual


def test_ingester_preserves_action_and_target():
    r = load_manual("tests/vfx/fixtures/clone_effect_talking_head.yaml")
    acts = [s.action for s in r.edit_steps]
    assert "overlay" in acts and "duplicate" in acts and "remove_background" in acts
    overlay = [s for s in r.edit_steps if s.action == "overlay"][0]
    assert overlay.target == "stepin_clip"
