"""Shared helpers + controlled vocabularies for VFX *manuals* (MANUAL_SCHEMA.md).

A "manual" is the machine-executable recreation recipe the VFX tool consumes:
a header (technique_primitive, gear/props, result), ordered `inputs` (what to
film + acceptance checks), and ordered `edit_steps` (action/target/capcut_feature/
params/channel). AI effects additionally carry an `ai_generation` block.

This module is the single source of truth for:
  * the controlled vocabularies (so the converter, the validator, and the loader agree),
  * `record_to_draft_manual()` — turn an `external_sources.json` record into a *draft*
    manual (used by ingest_video.py so every future video lands in this format),
  * `rebuild_index()` — regenerate manuals/index.json from the manual files on disk.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
MANUALS_DIR = os.path.join(HERE, "manuals")
HIGGSFIELD_MCP = "66e733f1-17be-4bb6-b57b-70fea20b08b2"

SCHEMA_VERSION = 1

# --- controlled vocabularies ------------------------------------------------
TECHNIQUE_PRIMITIVES = {
    "overlay_bg_removal_clone",   # duplicate + auto background removal -> clone
    "chroma_key",                 # green/white screen composite
    "text_reveal",                # text behind/synced/3D, keyframed reveal
    "keyframe_motion",            # element animated via keyframed transform
    "clean_plate_mask_reveal",    # appear/disappear against an empty plate
    "match_cut",                  # in-camera cut hidden by matched motion
    "other",                      # catch-all (e.g. pure-AI generations)
}
# verbs an edit_step may use
ACTIONS = {
    "import", "overlay", "position", "duplicate", "remove_background", "chroma_key",
    "mask", "keyframe", "text", "transform", "filter", "split", "speed", "reverse",
    "trim", "opacity", "audio", "ai_generate",
}
# every step (and ai_generation step) is tagged with one channel
CHANNELS = {
    "structural",  # deterministic, auto-assemblable (import/overlay/duplicate/order)
    "ui",          # a named CapCut control the tool drives (Mask, Remove Background...)
    "taste",       # subjective/no fixed value (timing tweaks, color choices)
    "ai_gen",      # produced by an external generative tool / MCP
}

# free-text step  ->  (action, capcut_feature, default channel)
_STEP_RULES = [
    (r"\bimport|upload\b",          ("import", None, "structural")),
    (r"chroma key",                 ("chroma_key", "Remove Background → Chroma Key", "ui")),
    (r"remove background|auto removal|custom removal", ("remove_background", "Remove Background", "ui")),
    (r"\bduplicate\b",              ("duplicate", "Duplicate", "structural")),
    (r"\boverlay\b",                ("overlay", "Overlay", "structural")),
    (r"\bmask\b",                   ("mask", "Mask", "ui")),
    (r"\bkeyframe",                 ("keyframe", "Keyframes", "ui")),
    (r"opacity",                    ("opacity", "Opacity", "ui")),
    (r"\bsplit\b",                  ("split", "Split", "ui")),
    (r"\bspeed\b|slow (?:it|down)", ("speed", "Speed", "ui")),
    (r"reverse",                    ("reverse", "Reverse", "ui")),
    (r"\brotate\b|perspective",     ("transform", "Rotate", "ui")),
    (r"\bcrop\b|\bscale\b|resize",  ("transform", "Crop", "ui")),
    (r"body effects|video effects|effects? ", ("filter", "Effects", "ui")),
    (r"\btext\b",                   ("text", "Text", "ui")),
    (r"aspect ratio",              ("transform", "Aspect Ratio", "ui")),
    (r"\blayers?\b|front\b",        ("position", "Layers", "ui")),
    (r"\btrim\b",                   ("trim", None, "taste")),
    (r"sound|sfx|audio",            ("audio", None, "taste")),
]


def guess_primitive(rec):
    """Best-effort technique_primitive from a raw record's tags/features."""
    if rec.get("is_ai_generated"):
        return "other"
    tags = set(rec.get("tags", []))
    feats = set(rec.get("capcut_features", []))
    low = " ".join(rec.get("editing_steps", [])).lower()
    if "cloning" in tags or "clone" in low:
        return "overlay_bg_removal_clone"
    if "green_screen" in tags or "Chroma Key" in feats or "chroma key" in low:
        return "chroma_key"
    if "clean_plate" in tags or rec.get("needs_clean_plate"):
        return "clean_plate_mask_reveal"
    if "Text" in feats and "text behind" in low:
        return "text_reveal"
    if "Keyframes" in feats or "keyframes" in tags:
        return "keyframe_motion"
    if "Text" in feats:
        return "text_reveal"
    return "other"


def _classify_step(text):
    low = text.lower()
    for pat, (action, feat, chan) in _STEP_RULES:
        if re.search(pat, low):
            return action, feat, chan
    return "position", None, "structural"


def record_to_draft_manual(rec):
    """Convert an external_sources.json record into a *draft* manual.

    Drafts carry ``"draft": true`` + ``"needs_authoring": true`` so a human (or
    Claude) knows the structural skeleton is auto-derived and params/acceptance
    checks still need a pass. Hand-authored manuals drop those flags.
    """
    slug = rec["slug"]
    is_ai = bool(rec.get("is_ai_generated"))
    sm = rec.get("source_meta", {}) or {}

    inputs = []
    for i, step in enumerate(rec.get("filming_steps", []) or []):
        inputs.append({
            "name": "clip_%d" % (i + 1),
            "what_to_film": step,
            "capture_requirements": {"locked_off": bool(rec.get("needs_tripod"))},
            "acceptance_checks": (["camera_locked_off"] if rec.get("needs_tripod") else []),
            "variance_tolerance": {},
        })

    edit_steps, ai_steps = [], []
    for step in rec.get("editing_steps", []) or []:
        action, feat, chan = _classify_step(step)
        s = {"action": action, "channel": chan, "note": step}
        if feat:
            s["capcut_feature"] = feat
        edit_steps.append(s)

    if is_ai:
        for tool in (rec.get("ai_tools") or ["AI"]):
            ai_steps.append({
                "provider": tool.lower(),
                "mcp_server": HIGGSFIELD_MCP if tool.lower() == "higgsfield" else None,
                "operation": "image_to_video",
                "inputs": [inp["name"] for inp in inputs] or ["source_photo"],
                "prompt_strategy": "author at runtime",
                "settings": {},
                "channel": "ai_gen",
            })

    manual = {
        "id": slug,
        "schema_version": SCHEMA_VERSION,
        "draft": True,
        "needs_authoring": True,
        "technique_primitive": guess_primitive(rec),
        "title": rec.get("effect") or slug,
        "difficulty": (rec.get("difficulty") or "beginner").lower(),
        "aspect_ratio": rec.get("output_aspect") or "9:16",
        "gear_required": (["tripod"] if rec.get("needs_tripod") else []),
        "props_required": rec.get("props") or [],
        "result_description": rec.get("effect") or "",
        "source": rec.get("source_creator"),
        "source_url": rec.get("source_url"),
        "is_ai_generated": is_ai,
        "tool": rec.get("tool"),
        "inputs": inputs,
        "edit_steps": edit_steps,
        "result": {"description": "", "success_criteria": []},
        "narration_transcript": (rec.get("lessons", [{}]) or [{}])[0].get("transcript"),
        "frames": {"demo": rec.get("demo_frames", []), "editing": rec.get("editing_screenshots", [])},
        "source_meta": {k: sm.get(k) for k in
                        ("creator_handle", "like_count", "comment_count", "upload_date", "caption", "hashtags")},
    }
    if ai_steps:
        manual["ai_generation"] = ai_steps
    return manual


def write_manual(manual, manuals_dir=MANUALS_DIR):
    os.makedirs(manuals_dir, exist_ok=True)
    path = os.path.join(manuals_dir, manual["id"] + ".json")
    json.dump(manual, open(path, "w"), indent=1, ensure_ascii=False)
    return path


def write_draft_if_absent(rec, manuals_dir=MANUALS_DIR):
    """Emit a draft manual for a record unless a *hand-authored* one already exists.

    Existing drafts are refreshed; hand-authored manuals (no ``draft`` flag) are
    preserved so re-ingesting a URL never clobbers human work.
    """
    path = os.path.join(manuals_dir, rec["slug"] + ".json")
    if os.path.exists(path):
        try:
            if not json.load(open(path)).get("draft"):
                return path, "kept-authored"
        except Exception:
            pass
    write_manual(record_to_draft_manual(rec), manuals_dir)
    return path, "wrote-draft"


def rebuild_index(manuals_dir=MANUALS_DIR):
    """Regenerate manuals/index.json from the manual files present on disk."""
    rows = []
    for fn in sorted(os.listdir(manuals_dir)):
        if not fn.endswith(".json") or fn == "index.json":
            continue
        m = json.load(open(os.path.join(manuals_dir, fn)))
        rows.append({
            "id": m["id"], "title": m.get("title"),
            "technique_primitive": m.get("technique_primitive"),
            "difficulty": m.get("difficulty"), "is_ai_generated": bool(m.get("is_ai_generated")),
            "gear_required": m.get("gear_required", []), "props_required": m.get("props_required", []),
            "tool": m.get("tool"), "draft": bool(m.get("draft")),
            "file": "manuals/%s" % fn,
        })
    idx = {"schema_version": SCHEMA_VERSION, "count": len(rows), "manuals": rows}
    json.dump(idx, open(os.path.join(manuals_dir, "index.json"), "w"), indent=1, ensure_ascii=False)
    return idx
