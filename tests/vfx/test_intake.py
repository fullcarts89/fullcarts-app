from vfx.intake import Capabilities, requirement_met


def test_capabilities_defaults():
    c = Capabilities()
    assert c.equipment == [] and c.props == [] and c.location is None


def test_requirement_met_locked_off_needs_tripod():
    have = Capabilities(equipment=["tripod", "phone"])
    lack = Capabilities(equipment=["phone"])
    assert requirement_met({"locked_off": True}, have) is True
    assert requirement_met({"locked_off": True}, lack) is False


def test_requirement_met_green_screen():
    assert requirement_met({"green_screen": True}, Capabilities(equipment=["green_screen"])) is True
    assert requirement_met({"green_screen": True}, Capabilities()) is False


def test_no_special_requirement_always_met():
    assert requirement_met({}, Capabilities()) is True
    assert requirement_met({"locked_off": False}, Capabilities()) is True
