from vfx.ingest.classify import classify_channel
from vfx.models import Channel


def test_classify_draft():
    assert classify_channel("Split the clip and delete the front part.") == Channel.DRAFT


def test_classify_gui():
    assert classify_channel("Use the mask tool and boost the feather.") == Channel.GUI


def test_classify_judgment():
    assert classify_channel("Fix the white balance and pull the HSL saturation down.") == Channel.JUDGMENT


def test_classify_default_is_gui():
    assert classify_channel("Here we go.") == Channel.GUI
