from vfx.ingest.manual_schema import manual_to_recipe


def _manual(**kw):
    m = {
        "id": "ai_demo",
        "title": "AI Demo",
        "technique_primitive": "ai_transition",
        "inputs": [{"name": "photoA", "type": "shot", "what_to_film": "a face"}],
        "edit_steps": [{"action": "overlay", "target": "photoA"}],
    }
    m.update(kw)
    return m


def test_ai_fields_preserved():
    gen = [{"provider": "kling", "operation": "first_last_frame_video"}]
    r = manual_to_recipe(_manual(is_ai_generated=True, ai_generation=gen))
    assert r.is_ai_generated is True
    assert r.ai_generation == gen


def test_non_ai_defaults():
    r = manual_to_recipe(_manual())
    assert r.is_ai_generated is False
    assert r.ai_generation == []
