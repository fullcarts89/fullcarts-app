from vfx.models import VFXRecipe, EditStep, AssetSpec, Channel

def test_channel_values():
    assert {c.value for c in Channel} == {"DRAFT", "GUI", "JUDGMENT"}

def test_recipe_roundtrips_to_dict():
    recipe = VFXRecipe(
        slug="make-object-appear",
        title="Make an Object Appear",
        difficulty="beginner",
        editor="CapCut",
        shot_on="phone",
        technique_primitive="clean_plate_mask_reveal",
        summary="Snap to make an object appear.",
        asset_spec=[
            AssetSpec(name="action_shot", type="shot",
                      capture_requirements={"locked_off": True},
                      acceptance_checks=["camera_locked_off", "object_present"],
                      variance_tolerance={"camera_shift_px": 8}),
            AssetSpec(name="clean_plate", type="shot",
                      capture_requirements={"locked_off": True},
                      acceptance_checks=["camera_locked_off", "object_absent"],
                      variance_tolerance={"camera_shift_px": 8}),
        ],
        filming_steps=["Snap, pick up cup, drink.", "Clean plate, no cup."],
        edit_steps=[
            EditStep(index=1, instruction="Split and delete the front.",
                     capcut_target="timeline/split", params={}, channel=Channel.DRAFT),
            EditStep(index=2, instruction="Select the mask tool.",
                     capcut_target="video/mask", params={"shape": "rectangle"},
                     channel=Channel.GUI, reference_screenshot="edit-07.png"),
            EditStep(index=3, instruction="Fix white balance to taste.",
                     capcut_target="adjustment/basic", params={}, channel=Channel.JUDGMENT),
        ],
    )
    d = recipe.to_dict()
    assert d["slug"] == "make-object-appear"
    assert d["edit_steps"][1]["channel"] == "GUI"
    again = VFXRecipe.from_dict(d)
    assert again == recipe


def test_new_fields_roundtrip():
    recipe = VFXRecipe(
        slug="make-object-appear",
        title="Make an Object Appear",
        difficulty="beginner",
        editor="CapCut",
        shot_on="phone",
        technique_primitive="clean_plate_mask_reveal",
        summary="Snap to make an object appear.",
        gear="tripod",
        reference_images=["a.jpg", "b.jpg"],
    )
    d = recipe.to_dict()
    assert d["gear"] == "tripod"
    assert d["reference_images"] == ["a.jpg", "b.jpg"]
    again = VFXRecipe.from_dict(d)
    assert again.gear == "tripod"
    assert again.reference_images == ["a.jpg", "b.jpg"]
    assert again == recipe
