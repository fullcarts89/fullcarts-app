from vfx.llm import STEP_SCHEMA, build_prompt


def test_schema_is_strict_object():
    assert STEP_SCHEMA["type"] == "object"
    assert STEP_SCHEMA["additionalProperties"] is False
    items = STEP_SCHEMA["properties"]["steps"]["items"]
    assert items["additionalProperties"] is False
    assert set(items["required"]) == {"index", "instruction", "capcut_target", "channel"}
    assert items["properties"]["channel"]["enum"] == ["DRAFT", "GUI", "JUDGMENT"]


def test_build_prompt_includes_steps_and_tags():
    rec = {"effect": "Make X", "tags": ["mask", "clean_plate"],
           "filming_steps": ["Shoot A", "Shoot B"],
           "editing_steps": ["split the clip", "add a mask", "here we go"]}
    sys_p, user_p = build_prompt(rec)
    assert "mask" in user_p and "split the clip" in user_p
    assert "DRAFT" in sys_p and "GUI" in sys_p and "JUDGMENT" in sys_p
