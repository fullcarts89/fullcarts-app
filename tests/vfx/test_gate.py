from vfx.models import AssetSpec
from vfx.qa import gate, probes

def test_unknown_checks_go_to_manual(monkeypatch):
    spec = AssetSpec(name="a", type="shot",
                     acceptance_checks=["object_present", "framing_ok", "min_duration"],
                     variance_tolerance={"min_seconds": 0.5})
    monkeypatch.setattr(probes, "probe_duration",
                        lambda p, s: probes.ProbeResult(True, "ok"))
    v = gate.check_asset(spec, "x.mp4")
    assert set(v.manual_checks) == {"object_present", "framing_ok"}
    assert v.passed is True

def test_failure_is_collected(monkeypatch):
    spec = AssetSpec(name="a", type="shot", acceptance_checks=["min_resolution"],
                     variance_tolerance={"min_w": 1920, "min_h": 1080})
    monkeypatch.setattr(probes, "probe_resolution",
                        lambda p, w, h: probes.ProbeResult(False, "640x480 (min 1920x1080)"))
    v = gate.check_asset(spec, "x.mp4")
    assert not v.passed and "min_resolution" in v.failures[0]

def test_camera_locked_off_no_ref_passes(monkeypatch):
    spec = AssetSpec(name="action", type="shot", acceptance_checks=["camera_locked_off"],
                     variance_tolerance={"camera_shift_px": 8})
    v = gate.check_asset(spec, "x.mp4", ref_path=None)
    assert v.passed  # first shot, nothing to compare
