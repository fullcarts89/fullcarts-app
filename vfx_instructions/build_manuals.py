import json, os
import os as _os
ROOT=_os.path.dirname(_os.path.abspath(__file__))
SRC=json.load(open(os.path.join(ROOT,'external_sources.json')))['effects']
BY={e['slug']:e for e in SRC}
MAN=os.path.join(ROOT,'manuals'); os.makedirs(MAN,exist_ok=True)
HIGGS="66e733f1-17be-4bb6-b57b-70fea20b08b2"  # Higgsfield MCP server id

def S(action,target=None,feature=None,params=None,timing=None,channel="structural",**kw):
    d={"action":action,"channel":channel}
    if target is not None: d["target"]=target
    if feature is not None: d["capcut_feature"]=feature
    if params: d["params"]=params
    if timing: d["timing"]=timing
    d.update(kw)
    return d

# ---- hand-authored manuals (CapCut-able + AI) ----
M={}

M["clone_effect_talking_head"]=dict(
 technique_primitive="overlay_bg_removal_clone", difficulty="beginner",
 gear_required=["tripod","lighting"], props_required=["chair"],
 result_description="Two copies of you in one shot — you sit pointing, and your clone steps in and sits beside you.",
 inputs=[
  dict(name="pointing_clip", what_to_film="Sit, point to where the clone will be, then step out of frame.",
       capture_requirements={"locked_off":True,"green_screen":False,"framing":"leave the clone's seat empty"},
       acceptance_checks=["camera_locked_off","min_duration"], variance_tolerance={"camera_shift_px":8,"min_seconds":2}),
  dict(name="stepin_clip", what_to_film="Step into frame from the side and sit in the empty seat.",
       capture_requirements={"locked_off":True}, acceptance_checks=["camera_locked_off"], variance_tolerance={"camera_shift_px":8}),
 ],
 edit_steps=[
  S("import","both clips"),
  S("overlay","stepin_clip",params={"track":2}),
  S("position","stepin_clip",params={"note":"directly under the pointing clip"}),
  S("duplicate","pointing_clip",params={"to_track":3}),
  S("remove_background","top pointing clip",feature="Remove Background → Auto Removal",params={"mode":"auto"},channel="ui"),
 ],
 result={"description":"Clone sits beside you with no hard seam.","success_criteria":["Two people visible simultaneously","Clean cutout edge, no flicker"]},
)

M["text_behind_subject"]=dict(
 technique_primitive="text_reveal", difficulty="beginner",
 gear_required=["tripod"], props_required=[],
 result_description="A large text title sits behind you and is revealed as you walk across the frame.",
 inputs=[dict(name="walk_clip", what_to_film="Walk across the frame, side to side.",
   capture_requirements={"locked_off":True,"framing":"full body, room to cross frame"},
   acceptance_checks=["camera_locked_off","min_duration"], variance_tolerance={"camera_shift_px":8,"min_seconds":2})],
 edit_steps=[
  S("import","walk_clip"),
  S("text","new text layer",feature="Text → Add text",params={"size":"large"},channel="ui"),
  S("duplicate","walk_clip",params={"to_track":2}),
  S("position","duplicated walk_clip",params={"note":"align exactly over the original"}),
  S("mask","duplicated walk_clip",feature="Mask → Linear",params={"shape":"linear","rotation":90,"note":"horizontal mask rotated to vertical"},channel="ui"),
  S("keyframe","duplicated walk_clip",params={"property":"mask_position","note":"keyframe the mask line to follow you across frame"},timing={"cue":"each step as you cross"},channel="ui"),
  S("position","layer order",feature="Layers",params={"note":"move the masked overlay ABOVE the text layer"},channel="ui"),
 ],
 result={"description":"Text appears behind the walking subject.","success_criteria":["Text occluded by body as you pass","Mask edge tracks the body cleanly"]},
)

M["printed_sticker_flying_object"]=dict(
 technique_primitive="chroma_key", difficulty="intermediate",
 gear_required=["tripod"], props_required=["football","printer + paper","green paper","tape"],
 result_description="A real thrown object (football) becomes a printed sticker that flies across the scene.",
 inputs=[
  dict(name="throw_clip", what_to_film="Throw a football across the field.", capture_requirements={"locked_off":True}, acceptance_checks=["camera_locked_off"], variance_tolerance={"camera_shift_px":8}),
  dict(name="pull_clip", what_to_film="Pull the printed sticker (behind a hole in green paper) through toward camera.", capture_requirements={"green_screen":True,"note":"green paper fills frame behind sticker"}, acceptance_checks=["has_green_screen"], variance_tolerance={"green_ratio":0.3}),
  dict(name="sticker_screenshot", what_to_film="Screenshot of the Instagram sticker on a green story background.", capture_requirements={"green_screen":True}, acceptance_checks=["has_green_screen"]),
 ],
 edit_steps=[
  S("import","throw_clip, pull_clip, sticker_screenshot (in order)"),
  S("chroma_key","sticker_screenshot",feature="Remove Background → Chroma Key",params={"key_color":"green"},channel="ui"),
  S("overlay","sticker_screenshot",params={"track":2,"note":"pull to front of track"}),
  S("chroma_key","pull_clip",feature="Remove Background → Chroma Key",params={"key_color":"green"},channel="ui"),
  S("overlay","pull_clip",params={"track":2,"note":"place at end of the screenshot clip"}),
  S("keyframe","pull_clip / sticker",params={"property":"position+scale","note":"keyframe paper/sticker to follow the ball"},timing={"cue":"ball travel path"},channel="ui"),
 ],
 result={"description":"Object turns into a flying sticker tracking the ball.","success_criteria":["Clean green key, no spill","Sticker follows the ball convincingly"]},
)

M["perspective_effect"]=dict(
 technique_primitive="text_reveal", difficulty="beginner",
 gear_required=[], props_required=[],
 result_description="Bold colored text sits in your scene at an angled 3D perspective.",
 inputs=[
  dict(name="main_clip", what_to_film="Your main shot the 3D text will sit in.", capture_requirements={}, acceptance_checks=["min_duration"]),
  dict(name="text_screenshot", what_to_film="Screenshot of bold (red/yellow) text on a white screen, made in CapCut.", capture_requirements={"note":"white background for keying"}),
 ],
 edit_steps=[
  S("import","white screen image"),
  S("text","new text layer",feature="Text → Add text",params={"color":"red or yellow"},channel="ui"),
  S("import","main_clip"),
  S("overlay","text_screenshot",params={"track":2}),
  S("transform","text_screenshot",feature="Crop",params={"note":"crop to text"},channel="ui"),
  S("chroma_key","text_screenshot",feature="Remove Background → Chroma Key",params={"key_color":"white"},channel="ui"),
  S("filter","text_screenshot",feature="Effects → Video Effects → Player 3",params={"glow":False,"texture":False},channel="ui"),
  S("transform","text_screenshot",feature="Rotate",params={"note":"adjust perspective to angled 3D"},channel="taste"),
 ],
 result={"description":"Angled 3D text composited into the scene.","success_criteria":["White fully keyed out","Perspective reads as 3D"]},
)

M["screen_pop_out_push"]=dict(
 technique_primitive="other", difficulty="beginner",
 gear_required=["tripod"], props_required=[],
 result_description="Your hand pushes out of a screenshot of your own Instagram post toward the viewer.",
 inputs=[dict(name="push_clip", what_to_film="Push your hand toward the camera.", capture_requirements={"locked_off":True}, acceptance_checks=["camera_locked_off"], variance_tolerance={"camera_shift_px":8}),
  dict(name="post_screenshot", what_to_film="Screenshot of one of your Instagram posts.", capture_requirements={})],
 edit_steps=[
  S("import","post_screenshot, push_clip"),
  S("overlay","push_clip",params={"track":2}),
  S("transform","push_clip",feature="Crop",params={"note":"fit exactly over the post in the screenshot"},channel="ui"),
  S("duplicate","push_clip",params={"to_track":3,"note":"move under original; crop to where hand pops out"}),
  S("remove_background","duplicated push_clip",feature="Remove Background → Auto Removal",params={"mode":"auto","note":"keep only the hand"},channel="ui"),
  S("text","caption + SFX",channel="taste"),
 ],
 result={"description":"Hand breaks the frame of the post.","success_criteria":["Hand cleanly cut out","Pop-out aligns with the post edge"]},
)

M["tap_synced_text"]=dict(
 technique_primitive="text_reveal", difficulty="intermediate",
 gear_required=["tripod"], props_required=[],
 result_description="Three text lines reveal one-by-one, synced to foot taps / jumps, with you popping in front of the text.",
 inputs=[dict(name="landscape_clip", what_to_film="Landscape shot; tap 3 times then jump 3 times as sync points.",
   capture_requirements={"locked_off":True,"note":"shot in landscape"}, acceptance_checks=["camera_locked_off"], variance_tolerance={"camera_shift_px":8})],
 edit_steps=[
  S("import","landscape_clip"),
  S("transform","project",feature="Aspect Ratio",params={"aspect":"9:16"},channel="ui"),
  S("text","3 text layers",feature="Text → Add text",params={"count":3,"animation":"none/static"},channel="ui"),
  S("keyframe","landscape_clip",params={"property":"position","note":"keyframe just before each tap, then 1 frame later drag video down; reveal text after each move"},timing={"cue":"each foot tap / jump"},channel="ui"),
  S("duplicate","landscape_clip",params={"to_track":2,"note":"overlay, drag under original"}),
  S("position","layer order",feature="Layers → Front",params={"note":"bring subject in front of text"},channel="ui"),
 ],
 result={"description":"Text reveals in sync with movement, subject in front.","success_criteria":["Each line lands on a tap","Subject occludes text correctly"]},
)

M["talking_head_match_cut"]=dict(
 technique_primitive="match_cut", difficulty="beginner",
 gear_required=["camera_operator"], props_required=[],
 result_description="A talking-head script broken into 3 framings (wide/close/medium) cut together so motion hides the cuts.",
 inputs=[
  dict(name="wide_shot", what_to_film="Wide: walk toward camera, turn head left at a set point.", capture_requirements={}, acceptance_checks=["min_duration"]),
  dict(name="close_shot", what_to_film="Close-up: deliver next part, walk out of frame.", capture_requirements={}, acceptance_checks=["min_duration"]),
  dict(name="medium_shot", what_to_film="Medium: walk into frame for the final part.", capture_requirements={}, acceptance_checks=["min_duration"]),
 ],
 edit_steps=[
  S("import","wide_shot, close_shot, medium_shot"),
  S("trim","each shot",params={"note":"cut on the matched motion (head turn / walk out / walk in)"}),
  S("position","sequence",params={"note":"order wide → close → medium"}),
 ],
 result={"description":"Seamless match-cut talking head.","success_criteria":["Cuts hidden by motion","Continuous energy across shots"]},
)

M["scrunch_paper_reveal"]=dict(
 technique_primitive="other", difficulty="beginner",
 gear_required=["tripod"], props_required=["paper","dark background"],
 result_description="A stop-motion of paper un-scrunching reveals an object/title as an intro.",
 inputs=[dict(name="scrunch_photos", what_to_film="~7 photos of paper from flat to fully scrunched on a dark background.",
   capture_requirements={"locked_off":True,"note":"~7 stages"}, acceptance_checks=["camera_locked_off"], variance_tolerance={"camera_shift_px":8})],
 edit_steps=[
  S("import","scrunch_photos (flat → scrunched order)"),
  S("overlay","each photo",params={"track":2}),
  S("trim","each photo",params={"duration_s":0.1}),
  S("remove_background","each photo",feature="Remove Background → Custom Removal",params={"mode":"custom","note":"highlight the paper"},channel="ui"),
  S("filter","background video",feature="Effects → Flash 2",channel="ui"),
  S("audio","crumpled-paper SFX",channel="taste"),
 ],
 result={"description":"Paper-reveal intro.","success_criteria":["Smooth stop-motion crumple","Object revealed on final frame"]},
)

M["phone_hologram"]=dict(
 technique_primitive="keyframe_motion", difficulty="intermediate",
 gear_required=["tripod"], props_required=["phone"],
 result_description="A floating holographic screen rises out of your phone as you swipe up.",
 inputs=[
  dict(name="swipe_clip", what_to_film="Face camera holding a phone; swipe up from the screen as if pulling the display into the air, then scroll the floating screen.", capture_requirements={"locked_off":True}, acceptance_checks=["camera_locked_off"], variance_tolerance={"camera_shift_px":8}),
  dict(name="screen_recording", what_to_film="Screen recording of you scrolling on the phone.", capture_requirements={}),
 ],
 edit_steps=[
  S("import","swipe_clip, screen_recording"),
  S("overlay","screen_recording",params={"track":2}),
  S("opacity","screen_recording",feature="Opacity",params={"opacity":50},channel="ui"),  # read from frame p_057 (on-screen "50%")
  S("keyframe","screen_recording",params={"property":"position","note":"start just below the phone; rise up on the swipe"},timing={"cue":"the swipe-up gesture"},channel="ui"),
  S("duplicate","swipe_clip",params={"to_track":3}),
  S("mask","duplicated swipe_clip",feature="Mask → Linear",params={"shape":"linear","orientation":"horizontal","position":"top edge of phone","feather":"slight"},channel="ui"),
  S("trim","clips",params={"note":"match scrolling to finger movement; trim to sync"},channel="taste"),
 ],
 result={"description":"Hologram screen emerges from the phone.","success_criteria":["Screen rises exactly with the swipe","Mask edge hidden at phone top"]},
)

M["flash_effect_clean_plate"]=dict(
 technique_primitive="clean_plate_mask_reveal", difficulty="intermediate",
 gear_required=["tripod"], props_required=[],
 result_description="A white flash and you instantly vanish/appear, using a clean plate of the scene.",
 inputs=[
  dict(name="talking_clip", what_to_film="Talk to camera in the scene.", capture_requirements={"locked_off":True}, acceptance_checks=["camera_locked_off"], variance_tolerance={"camera_shift_px":8}),
  dict(name="clean_plate", what_to_film="Same scene, empty, camera unmoved.", capture_requirements={"locked_off":True,"subject_exits_frame":True}, acceptance_checks=["camera_locked_off","object_absent"], variance_tolerance={"camera_shift_px":8}),
 ],
 edit_steps=[
  S("import","clean_plate, talking_clip"),
  S("overlay","talking_clip",params={"track":2,"note":"start of layer 2"}),
  S("trim","talking_clip",params={"note":"trim start slightly"}),
  S("split","talking_clip",timing={"cue":"a few frames in"}),
  S("filter","first section",feature="Effects → Body Effects → White Flash",channel="ui"),
  S("remove_background","talking_clip",feature="Remove Background → Auto Removal",params={"mode":"auto"},channel="ui"),
 ],
 result={"description":"Flash transition reveal.","success_criteria":["Flash masks the cut","Subject appears/disappears cleanly"]},
)

M["floating_mini_clone"]=dict(
 technique_primitive="keyframe_motion", difficulty="intermediate",
 gear_required=["tripod"], props_required=[],
 result_description="A shrunken, slow-motion clone of you floats/jumps within your main shot.",
 inputs=[
  dict(name="foreground_clip", what_to_film="Your main foreground shot.", capture_requirements={"locked_off":True}, acceptance_checks=["camera_locked_off"], variance_tolerance={"camera_shift_px":8}),
  dict(name="jump_clip", what_to_film="A jump, ideally on an iPhone/rig for smooth slow motion.", capture_requirements={"locked_off":True}, acceptance_checks=["camera_locked_off"], variance_tolerance={"camera_shift_px":8}),
 ],
 edit_steps=[
  S("import","foreground_clip, jump_clip"),
  S("overlay","jump_clip",params={"track":2}),
  S("remove_background","jump_clip",feature="Remove Background → Auto Removal",params={"mode":"auto"},channel="ui"),
  S("speed","jump_clip",feature="Speed",params={"note":"slow down (rate set to taste)"},channel="ui"),
  S("transform","jump_clip",feature="Scale",params={"note":"scale the cutout down, position in scene"},channel="ui"),
  S("keyframe","jump_clip",params={"property":"position","note":"keyframe start, then a few frames later raise it for the float"},timing={"cue":"jump apex"},channel="ui"),
 ],
 result={"description":"Mini floating clone composited in.","success_criteria":["Clean cutout","Smooth slow-mo float"]},
)

# ---- AI / Higgsfield effects ----
M["pendulum_effect_ai"]=dict(
 technique_primitive="other", difficulty="beginner",
 gear_required=[], props_required=[],
 result_description="An AI 'aerial pullback' from a single photo of you, looped back-and-forth into a pendulum swing.",
 inputs=[dict(name="selfie_photo", what_to_film="One photo of yourself.", capture_requirements={}, acceptance_checks=["min_resolution"])],
 ai_generation=[
  dict(provider="higgsfield", mcp_server=HIGGS, operation="image_to_video", tool="generate_video",
       inputs=["selfie_photo"], motion="Aerial Pullback",
       prompt_strategy="author at runtime (creator gated the exact prompt)", settings={"note":"creator's settings not shown"}),
 ],
 edit_steps=[
  S("import","generated clip"),
  S("duplicate","generated clip",params={"to_track":1}),
  S("reverse","second copy",feature="Reverse",channel="ui"),
 ],
 result={"description":"Pendulum back-and-forth from one photo.","success_criteria":["Seamless forward/reverse loop"]},
)

M["floating_outfit_effect"]=dict(
 technique_primitive="other", difficulty="intermediate",
 gear_required=[], props_required=[],
 result_description="An AI-generated shot of your outfit floating as if worn by an invisible person.",
 inputs=[dict(name="outfit_photo", what_to_film="One photo of you in the outfit.", capture_requirements={}, acceptance_checks=["min_resolution"])],
 ai_generation=[
  dict(provider="higgsfield", mcp_server=HIGGS, operation="image_generation", tool="generate_image",
       inputs=["outfit_photo"], prompt_strategy="floating-outfit prompt, authored at runtime", settings={}),
  dict(provider="higgsfield", mcp_server=HIGGS, operation="cleanup", tool="remove_background/outpaint", optional=True,
       note="optional: remove background people (inpaint), relight to golden hour"),
  dict(provider="higgsfield", mcp_server=HIGGS, operation="image_to_video", tool="generate_video",
       inputs=["generated floating-outfit still"], prompt_strategy="author at runtime", settings={}),
 ],
 edit_steps=[S("import","generated clip")],
 result={"description":"Floating outfit clip.","success_criteria":["Outfit holds a worn shape","No visible body"]},
)

M["giant_effect_ai"]=dict(
 technique_primitive="other", difficulty="beginner",
 gear_required=[], props_required=[],
 result_description="An AI transition turning you into a giant, from one photo.",
 inputs=[dict(name="selfie_photo", what_to_film="One photo of yourself.", capture_requirements={}, acceptance_checks=["min_resolution"])],
 ai_generation=[
  dict(provider="higgsfield", mcp_server=HIGGS, operation="image_generation", tool="generate_image",
       inputs=["selfie_photo"], prompt_strategy="giant-scene prompt, authored at runtime", settings={}),
  dict(provider="higgsfield", mcp_server=HIGGS, operation="first_last_frame_video", tool="generate_video",
       inputs=["selfie_photo (start frame)","generated giant image (end frame)"], prompt_strategy="author at runtime", settings={}),
 ],
 edit_steps=[S("import","generated clip")],
 result={"description":"Transition into a giant.","success_criteria":["Smooth scale transition","Face consistent"]},
)

M["ai_location_transition"]=dict(
 technique_primitive="other", difficulty="intermediate",
 gear_required=[], props_required=[],
 result_description="An AI first/last-frame video transitioning you between two locations with a consistent face.",
 inputs=[dict(name="location_photos", what_to_film="Two photos of yourself in two different locations.", capture_requirements={}, acceptance_checks=["min_resolution"])],
 ai_generation=[
  dict(provider="openart", mcp_server=None, operation="first_last_frame_video", tool="Kling 2.0 (OpenArt)",
       inputs=["photo A (first frame)","photo B (last frame)"], prompt_strategy="author at runtime; generate 3-4, pick best",
       note="No MCP for OpenArt/Kling in this environment — manual/human step.", settings={"face_consistency":True}),
 ],
 edit_steps=[S("import","generated clip")],
 result={"description":"Location-to-location AI transition.","success_criteria":["Face consistent across frames","Smooth morph"]},
)

# ---- assemble + write ----
index=[]
for slug,m in M.items():
    src=BY.get(slug,{})
    sm=src.get('source_meta',{})
    has_ai = bool(m.get('ai_generation'))
    manual={
      "id":slug,
      "schema_version":1,
      "technique_primitive":m["technique_primitive"],
      "title":src.get('effect') or slug,
      "difficulty":m["difficulty"],
      "aspect_ratio":src.get('output_aspect') or "9:16",
      "gear_required":m["gear_required"],
      "props_required":m["props_required"],
      "result_description":m["result_description"],
      "source":src.get('source_creator'),
      "source_url":src.get('source_url'),
      "is_ai_generated":has_ai,
      "tool":src.get('tool'),
      "inputs":m["inputs"],
      "edit_steps":m["edit_steps"],
      "result":m.get("result",{}),
      # references kept alongside (schema allows prose backup)
      "narration_transcript":(src.get('lessons',[{}])[0].get('transcript')),
      "frames":{"demo":src.get('demo_frames',[]),"editing":src.get('editing_screenshots',[])},
      "source_meta":{k:sm.get(k) for k in ("creator_handle","like_count","comment_count","upload_date","caption","hashtags")},
    }
    if has_ai:
        for step in m["ai_generation"]: step.setdefault("channel","ai_gen")
        manual["ai_generation"]=m["ai_generation"]
    json.dump(manual, open(os.path.join(MAN,slug+'.json'),'w'), indent=1, ensure_ascii=False)
    index.append({"id":slug,"title":manual["title"],"technique_primitive":manual["technique_primitive"],
                  "difficulty":manual["difficulty"],"is_ai_generated":has_ai,
                  "gear_required":manual["gear_required"],"props_required":manual["props_required"],
                  "tool":manual["tool"],"file":"manuals/%s.json"%slug})
json.dump({"schema_version":1,"count":len(index),"manuals":index},
          open(os.path.join(MAN,'index.json'),'w'), indent=1, ensure_ascii=False)
print("wrote %d manuals + index.json"%len(index))
for i in index: print("  %-30s %-26s ai=%s"%(i['id'],i['technique_primitive'],i['is_ai_generated']))
