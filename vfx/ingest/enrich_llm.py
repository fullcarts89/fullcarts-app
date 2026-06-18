from typing import Any, Callable, Dict, List, Optional
from vfx.models import VFXRecipe, EditStep, Channel
from vfx.ingest.vfxdata import derive_primitive, derive_asset_spec


def enrich_record(record: Dict[str, Any], llm, with_vision: bool = False,
                  asset_resolver: Optional[Callable[[str], str]] = None) -> VFXRecipe:
    image_paths = None
    if with_vision and asset_resolver:
        image_paths = [asset_resolver(p) for p in record.get("breakdown_images", [])]
    normalized = llm.normalize_effect(record, image_paths=image_paths)
    edit_steps = [
        EditStep(index=s.get("index", i + 1), instruction=s["instruction"],
                 capcut_target=s.get("capcut_target", ""),
                 channel=Channel(s["channel"]))
        for i, s in enumerate(normalized)
    ]
    return VFXRecipe(
        slug=record["slug"], title=record["effect"],
        difficulty=record.get("difficulty", "unknown"), editor="CapCut",
        shot_on="phone", technique_primitive=derive_primitive(record.get("tags", [])),
        summary=(record.get("technique_note") or record["effect"]),
        asset_spec=derive_asset_spec(record),
        filming_steps=record.get("filming_steps", []),
        edit_steps=edit_steps,
        reference_images=record.get("breakdown_images", []),
        gear=record.get("gear"), ingest_confidence=0.9)


def enrich_all(records: List[Dict[str, Any]], llm, store, with_vision: bool = False,
               asset_resolver: Optional[Callable[[str], str]] = None) -> int:
    n = 0
    for rec in records:
        store.put(enrich_record(rec, llm, with_vision=with_vision,
                                asset_resolver=asset_resolver))
        n += 1
    return n
