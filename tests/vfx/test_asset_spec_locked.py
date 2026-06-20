from vfx.ingest.vfxdata import derive_asset_spec


def test_clean_plate_implies_locked_off():
    # no explicit 'locked_off' tag, but clean_plate requires a locked-off camera
    specs = derive_asset_spec({"tags": ["clean_plate", "mask"]})
    assert all(s.capture_requirements.get("locked_off") for s in specs)
    assert all("camera_locked_off" in s.acceptance_checks for s in specs)


def test_no_clean_plate_no_lock():
    specs = derive_asset_spec({"tags": ["overlay"]})
    assert specs[0].capture_requirements.get("locked_off") is False
