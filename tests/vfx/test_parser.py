from vfx.ingest.parser import parse_manual_text

SAMPLE = open("tests/vfx/fixtures/sample.txt").read()

def test_parses_title_and_meta():
    p = parse_manual_text(SAMPLE)
    assert p["title"] == "Make an Object Appear"
    assert p["difficulty"].lower() == "beginner"
    assert p["editor"] == "CapCut"

def test_splits_filming_and_edit_steps():
    p = parse_manual_text(SAMPLE)
    assert len(p["filming_steps"]) >= 5
    assert len(p["edit_steps"]) >= 20
    assert all(isinstance(s, str) for s in p["edit_steps"])
