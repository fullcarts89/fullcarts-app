from vfx.ingest.enrich_llm import enrich_record, enrich_all
from vfx.models import Channel
from vfx.db import RecipeStore


class FakeLLM:
    def __init__(self): self.calls = []

    def normalize_effect(self, record, image_paths=None):
        self.calls.append((record["slug"], image_paths))
        return [
            {"index": 1, "instruction": "Split and delete the front.",
             "capcut_target": "timeline/split", "channel": "DRAFT"},
            {"index": 2, "instruction": "Add a rectangle mask over the object.",
             "capcut_target": "video/mask", "channel": "GUI"},
        ]


REC = {"slug": "make_an_object_appear", "effect": "Make an Object Appear",
       "difficulty": "Beginner", "gear": None, "technique_note": None,
       "filming_steps": ["a", "b"], "editing_steps": ["x", "y", "filler"],
       "tags": ["mask", "clean_plate"], "breakdown_images": ["assets/x/img.jpg"]}


def test_enrich_record_replaces_steps_and_bumps_confidence():
    r = enrich_record(REC, FakeLLM())
    assert [s.channel for s in r.edit_steps] == [Channel.DRAFT, Channel.GUI]
    assert r.edit_steps[0].capcut_target == "timeline/split"
    assert r.technique_primitive == "clean_plate_mask_reveal"
    assert r.ingest_confidence == 0.9


def test_enrich_record_passes_images_when_resolver_given():
    llm = FakeLLM()
    enrich_record(REC, llm, with_vision=True, asset_resolver=lambda rel: "/abs/" + rel)
    assert llm.calls[0][1] == ["/abs/assets/x/img.jpg"]


def test_enrich_all_writes_every_record(tmp_path):
    store = RecipeStore(tmp_path / "vfx.db")
    n = enrich_all([REC, {**REC, "slug": "two"}], FakeLLM(), store)
    assert n == 2 and store.get("two") is not None
