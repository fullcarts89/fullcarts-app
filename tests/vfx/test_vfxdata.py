from vfx.ingest.vfxdata import record_to_recipe, derive_primitive, ingest_all
from vfx.db import RecipeStore
from vfx_instructions.vfx_loader import VFXData


def test_derive_primitive_clean_plate():
    assert derive_primitive(["mask", "clean_plate"]) == "clean_plate_mask_reveal"


def test_record_to_recipe_maps_core_fields():
    rec = VFXData().get("make_an_object_appear")
    r = record_to_recipe(rec)
    assert r.slug == "make_an_object_appear"
    assert r.title == "Make an Object Appear"
    assert r.editor == "CapCut"
    assert r.technique_primitive == "clean_plate_mask_reveal"
    assert len(r.edit_steps) == len(rec["editing_steps"])
    assert len(r.reference_images) == len(rec["breakdown_images"])
    assert len(r.asset_spec) == 2  # clean_plate -> action shot + clean plate


def test_ingest_all_persists_every_record(tmp_path):
    store = RecipeStore(tmp_path / "vfx.db")
    n = ingest_all(store)
    assert n == len(VFXData())   # every source record persisted (dataset-size agnostic)
    got = store.get("make_an_object_appear")
    assert got is not None and got.technique_primitive == "clean_plate_mask_reveal"
