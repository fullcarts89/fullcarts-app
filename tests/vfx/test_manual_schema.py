import pytest
from vfx.ingest.manual_schema import load_manual, manual_to_recipe
from vfx.models import Channel

YAML = "tests/vfx/fixtures/clone_effect_talking_head.yaml"
JSON = "tests/vfx/fixtures/clone_effect_talking_head.json"


def test_yaml_maps_core_fields():
    r = load_manual(YAML)
    assert r.slug == "clone_effect_talking_head"
    assert r.technique_primitive == "overlay_bg_removal_clone"
    assert r.difficulty == "beginner" and r.editor == "CapCut"
    assert "tripod" in (r.gear or "")
    assert len(r.asset_spec) == 2
    assert r.asset_spec[0].acceptance_checks  # non-empty
    assert "camera_locked_off" in r.asset_spec[0].acceptance_checks


def test_edit_step_channels():
    r = load_manual(YAML)
    assert len(r.edit_steps) == 5
    chans = [s.channel for s in r.edit_steps]
    assert chans.count(Channel.DRAFT) == 4
    assert chans.count(Channel.GUI) == 1
    bg = [s for s in r.edit_steps if s.channel == Channel.GUI][0]
    assert "Remove Background" in bg.capcut_target  # exact UI label preserved


def test_yaml_and_json_agree_on_core():
    ry, rj = load_manual(YAML), load_manual(JSON)
    assert ry.slug == rj.slug
    assert ry.technique_primitive == rj.technique_primitive
    assert len(ry.edit_steps) == len(rj.edit_steps)
    assert [a.name for a in ry.asset_spec] == [a.name for a in rj.asset_spec]
    # JSON includes frames -> reference_images; YAML does not. So they differ here:
    assert rj.reference_images and not ry.reference_images


def test_missing_required_field_raises():
    with pytest.raises(ValueError):
        manual_to_recipe({"id": "x", "title": "x"})  # no technique_primitive/inputs/edit_steps
