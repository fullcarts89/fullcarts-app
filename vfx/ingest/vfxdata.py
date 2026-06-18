from typing import Any, Dict, List, Optional
from vfx.models import VFXRecipe, EditStep, AssetSpec
from vfx.ingest.classify import classify_channel


def derive_primitive(tags: List[str]) -> str:
    ts = set(tags)
    if {"clean_plate", "mask"} <= ts:
        return "clean_plate_mask_reveal"
    if "green_screen" in ts:
        return "green_screen_composite"
    if "transition" in ts:
        return "transition"
    if "keyframes" in ts:
        return "keyframe_motion"
    if "speed_ramp" in ts:
        return "speed_ramp"
    if "cutout" in ts:
        return "cutout_composite"
    if tags:
        return "_".join(sorted(tags)[:2])
    return "general"


def derive_asset_spec(rec: Dict[str, Any]) -> List[AssetSpec]:
    tags = set(rec.get("tags", []))
    locked = "locked_off" in tags
    cap = {"locked_off": locked}
    lock_checks = ["camera_locked_off"] if locked else []
    if "clean_plate" in tags:
        return [
            AssetSpec(name="action_shot", type="shot", capture_requirements=cap,
                      acceptance_checks=lock_checks + ["object_present"],
                      variance_tolerance={"camera_shift_px": 8}),
            AssetSpec(name="clean_plate", type="shot", capture_requirements=cap,
                      acceptance_checks=lock_checks + ["object_absent"],
                      variance_tolerance={"camera_shift_px": 8}),
        ]
    if "green_screen" in tags:
        return [AssetSpec(name="subject_green_screen", type="shot",
                          capture_requirements={"green_screen": True},
                          acceptance_checks=["has_green_screen"],
                          variance_tolerance={})]
    return [AssetSpec(name="main_shot", type="shot", capture_requirements=cap,
                      acceptance_checks=lock_checks,
                      variance_tolerance={"camera_shift_px": 8} if locked else {})]


def record_to_recipe(rec: Dict[str, Any]) -> VFXRecipe:
    edit_steps = [
        EditStep(index=i + 1, instruction=s, capcut_target="",
                 channel=classify_channel(s))
        for i, s in enumerate(rec.get("editing_steps", []))
    ]
    return VFXRecipe(
        slug=rec["slug"],
        title=rec["effect"],
        difficulty=rec.get("difficulty", "unknown"),
        editor="CapCut",
        shot_on="phone",
        technique_primitive=derive_primitive(rec.get("tags", [])),
        summary=(rec.get("technique_note") or rec["effect"]),
        asset_spec=derive_asset_spec(rec),
        filming_steps=rec.get("filming_steps", []),
        edit_steps=edit_steps,
        reference_images=rec.get("breakdown_images", []),
        gear=rec.get("gear"),
        ingest_confidence=0.5,  # narration steps unnormalized; raise after LLM pass
    )


def load_records(effects_json: Optional[str] = None) -> List[Dict[str, Any]]:
    from vfx_instructions.vfx_loader import VFXData
    d = VFXData(effects_json) if effects_json else VFXData()
    return list(d)


def ingest_all(store, effects_json: Optional[str] = None) -> int:
    n = 0
    for rec in load_records(effects_json):
        store.put(record_to_recipe(rec))
        n += 1
    return n
