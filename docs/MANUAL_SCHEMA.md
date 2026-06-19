# VFX Manual Authoring Guide

**Purpose:** This document defines the ideal format for a Viral VFX manual so the
automation tool (the "Viral VFX CapCut Agent") can ingest it **deterministically**
— recommend it, validate your footage against it, and auto-assemble as much of the
CapCut edit as possible. Author your manuals to this spec and they drop straight
into the tool with no guesswork.

> **The one golden rule:** every value you provide as a **structured field** is a
> value the tool does **not** have to infer from prose. Inference is where
> reliability leaks. Wherever the creator made a *specific* choice, write the
> **exact value** (opacity `50`, feather `0.2`, transition `300 ms`), not a vague
> phrase ("a little," "bring it down," "quick").

> **Format:** Provide manuals as **YAML or JSON** (examples below are YAML). That
> path is parsed with zero AI inference and zero per-manual cost. PDFs still work,
> but they're the lossy fallback. You can keep the human-readable prose narration
> *in addition* — it's a useful backup and reference — but the structured fields
> are what the tool consumes.

---

## How the fields map to the tool

| Section | Feeds | What it enables |
|---|---|---|
| **Recipe header** | Recommender + grouping | "Which of my effects can I do with the gear/props I have?" + reusing one engine across similar effects |
| **Inputs** | Asset Director + QA gate | Tells you what to film, in order, and auto-checks your footage meets the effect's needs |
| **Edit steps** | Draft writer + checklist + computer-use | Auto-assembles the structural edit; labels the rest as clean steps to finish |
| **Result** | Verification + recommending | Lets the tool confirm the finished render matches the intent |

There are **three execution channels** for edit steps:
- **`structural`** → the tool writes it directly into the CapCut project file (fully automatic): imports, tracks/overlays, splits, durations, duplicates, transitions, text, timing.
- **`ui`** → a CapCut button/panel action (one click): Remove Background, apply a Mask, set Opacity. Done by you (checklist) or by computer-use reading the on-screen label.
- **`taste`** → a subjective human call (color grading, "looks right"). Always left to you.

You don't *have* to tag the channel — the tool can infer it — but tagging removes ambiguity.

---

## 1. Recipe header

```yaml
id: clone_auto_bg_removal          # REQUIRED. stable slug; never changes
technique_primitive: overlay_bg_removal_clone   # REQUIRED. controlled vocab (see below)
title: Clone Effect (Auto BG Removal)           # REQUIRED
difficulty: beginner               # beginner | intermediate | advanced
aspect_ratio: "9:16"               # "9:16" | "16:9" | "1:1" | "original"
gear_required: [tripod]            # list; [] if none. see vocab below
props_required: [chair]            # free-text list; [] if none
result_description: >              # HIGH VALUE. 1-2 sentences on the finished effect
  Two copies of you in one shot — one sits pointing, the clone steps in and sits.
source: "Elly Walton (@elly.walton)"   # optional, attribution
```

| Field | Required | Notes |
|---|---|---|
| `id` | ✅ | lowercase slug, stable forever (the tool keys on it) |
| `technique_primitive` | ✅ | **the highest-leverage field** — see controlled vocab |
| `title` | ✅ | human title |
| `difficulty` | – | `beginner` / `intermediate` / `advanced` |
| `aspect_ratio` | – | sets the project canvas |
| `gear_required` | – | drives "can I do this?" gating in the recommender |
| `props_required` | – | free-text items the skit needs |
| `result_description` | ⭐ | used to recommend *and* to verify the render |

---

## 2. Inputs (ordered list of clips/assets to capture)

List inputs **in the order they're filmed/needed**. Per input:

```yaml
inputs:
  - name: pointing_clip            # REQUIRED. short identifier
    what_to_film: "Sit, point to where the clone will be, then step out of frame."  # REQUIRED
    capture_requirements:          # explicit booleans/values (not prose)
      locked_off: true
      green_screen: false
      framing: "leave the clone's seat empty"
      lighting: "even, no window behind you"
    acceptance_checks: [camera_locked_off, min_duration]   # from the fixed list below
    variance_tolerance: {camera_shift_px: 8, min_seconds: 2}
  - name: stepin_clip
    what_to_film: "Step into frame from the side and sit in the empty seat."
    capture_requirements: {locked_off: true}
    acceptance_checks: [camera_locked_off]
    variance_tolerance: {camera_shift_px: 8}
```

**`capture_requirements`** — common keys (add others as free-text):
`locked_off` (bool — tripod, camera must not move), `green_screen` (bool),
`framing` (str), `lighting` (str), `distance` (str), `subject_exits_frame` (bool).

**`acceptance_checks`** — use values from this fixed list (the tool runs these against your footage):

| check | automated now? | what it verifies |
|---|---|---|
| `camera_locked_off` | ✅ yes | the camera didn't move (vs the paired shot) within `camera_shift_px` |
| `min_duration` | ✅ yes | clip ≥ `min_seconds` |
| `min_resolution` | ✅ yes | clip ≥ `min_w` × `min_h` |
| `has_green_screen` | ✅ yes | enough green pixels present |
| `object_present` | ⏳ vision (later) | the object/subject is in the shot |
| `object_absent` | ⏳ vision (later) | the object/subject is gone (clean plate) |
| `framing_ok` | ⏳ vision (later) | matches the framing note |
| `lighting_consistent` | ⏳ vision (later) | lighting matches across shots |

**`variance_tolerance`** — the thresholds for the checks: `camera_shift_px` (default 8),
`min_seconds`, `min_w`, `min_h`, `green_ratio` (default 0.3).

---

## 3. Edit steps (the recipe)

A list, in execution order. Per step, the gold-standard shape:

```yaml
edit_steps:
  - action: import
    target: "both clips"
    channel: structural
  - action: overlay
    target: stepin_clip
    params: {track: 2}
    channel: structural
  - action: duplicate
    target: pointing_clip
    params: {to_track: 3}
    channel: structural
  - action: remove_background
    target: "top pointing clip"
    capcut_feature: "Remove Background → Auto Removal"   # exact desktop UI label
    channel: ui
  - action: mask
    target: overlay_clip
    capcut_feature: "Mask → Split"
    params: {shape: split, rotation: 90, feather: 0.2}    # EXACT numbers
    channel: ui
  - action: opacity
    target: overlay_clip
    params: {opacity: 50}            # set to see alignment, then back to 100
    channel: ui
  - action: split
    target: main_clip
    timing: {cue: "the moment you snap your fingers"}     # content-dependent
    channel: structural
```

| field | required | example | why |
|---|---|---|---|
| `action` | ✅ | `overlay`, `split`, `remove_background` | the verb the engine dispatches on (vocab below) |
| `target` | ✅ | `"overlay clip"`, `"bottom track"`, `clip 2` | which clip/track it applies to |
| `capcut_feature` | ⭐ (for `ui` steps) | `"Remove Background → Auto Removal"` | the **exact desktop UI label** — bridges mobile→desktop and is what computer-use finds on screen |
| `params` | ⭐ | `{opacity: 50}`, `{shape: split, feather: 0.2}` | **exact values** — every number here makes the step deterministic instead of a guess |
| `timing` | – | `{at_ms: 2300}` or `{cue: "when you step in"}` | flags whether the cut is an absolute time vs a moment in *your* footage you'll mark |
| `channel` | – (inferable) | `structural` / `ui` / `taste` | which execution path; tag it to remove ambiguity |
| `reference_screenshot` | ⭐ (for `ui` steps) | `assets/<id>/step_remove_bg.jpg` | a frame showing **this step** — fed to computer-use as visual grounding so it can match the control on screen even when the wording doesn't name a button. Path is relative to `vfx_instructions/`. |

**Reference screenshots (visual grounding).** When computer-use finishes the
`ui` steps in CapCut, it can be shown the tutorial frame for each step next to the
live desktop — so it matches "the control the creator used" by sight, not just by
the text. Tag the precise frame per step with `reference_screenshot`. It's
**optional and additive**: a manual with no per-step screenshots falls back to the
recipe's general `frames` bundle, and a path that doesn't resolve is skipped (a
stale path never breaks a run). Run `python -m vfx finish <id> --dry-run` to see a
**coverage report** — which `ui` steps have a screenshot, which declared one that's
missing on disk, and which have none.

**Why exact `params` matter so much:** "boost the feather a little," "bring opacity
down," "a quick transition" are the steps that *can't* be automated — they stay
fuzzy GUI actions. The same steps with `{feather: 0.2}`, `{opacity: 50}`,
`{transition: "zoom", duration_ms: 300}` can be written precisely. **Capture the
number the creator actually used.**

---

## 4. Result (optional but valuable)

```yaml
result:
  description: "Clone sits beside you; the seam down the middle is invisible."
  success_criteria:                 # what a correct render looks like
    - "Two people visible simultaneously"
    - "No hard seam at the split line"
```

---

## Controlled vocabularies

### `technique_primitive` (effects sharing one collapse to a single engine)
Pick the closest; if none fit, use `other` and describe it.

| primitive | what it covers |
|---|---|
| `clean_plate_mask_reveal` | object appear/disappear/teleport via a clean plate + mask |
| `overlay_bg_removal_clone` | clone using Auto Background Removal on an overlay |
| `split_screen_clone` | clone using a split/mirror mask (manual) |
| `speed_ramp` | time-remap / speed ramps |
| `object_transition` | hand-off / object-swap transitions (ball, egg, etc.) |
| `portal_transition` | step-through-a-portal style |
| `mask_transition` | shape/wipe mask transitions between scenes |
| `keyframe_motion` | floating/flying objects via keyframed transform + masking |
| `chroma_key` | green-screen composite |
| `match_cut` | seamless/match cut between shots |
| `text_reveal` | animated text/title reveal |
| `other` | none of the above (describe in `result_description`) |

### `action` verbs (for edit steps)
`import`, `split`, `delete`, `trim`, `overlay`, `duplicate`, `position` (move/align),
`speed`, `reverse`, `freeze_frame`, `opacity`, `mask`, `remove_background`,
`chroma_key`, `keyframe`, `transform` (scale/rotate), `transition`, `text`,
`sticker`, `filter`, `adjustment` (color/white-balance), `audio`.

### `params` cheat-sheet by action
- `opacity`: `{opacity: 0-100}`
- `mask`: `{shape: rectangle|circle|split|linear|mirror, feather: 0.0-1.0, rotation: <deg>, position: {x,y}, size: {w,h}}`
- `transition`: `{name: "<capcut name>", duration_ms: <int>}`
- `speed`: `{rate: <float>}` or `{curve: "<capcut name>"}`
- `text`: `{content: "...", style: "<capcut name>"}`
- `overlay` / `duplicate`: `{track: <int>}` / `{to_track: <int>}`
- `remove_background`: `{mode: auto|manual}`
- `transform`: `{scale: <float>, rotation: <deg>, x: <px>, y: <px>}`

### `capcut_feature` — write the **exact desktop UI label**
e.g. `"Mask → Split"`, `"Remove Background → Auto Removal"`, `"Opacity"`,
`"Adjustment → Basic → Temperature"`. Mobile and desktop CapCut have the **same
features under the same names** — only their location differs. Writing the label
(not "tap the mask icon") is what lets the tool work on desktop and find the
control by reading the screen.

### `channel`
`structural` (auto via draft file) · `ui` (one button/panel action) · `taste` (human judgment).

---

## Priorities, if you're updating manuals

1. **Must-have:** `id`, `technique_primitive`, ordered `inputs` (with
   `capture_requirements` + `acceptance_checks`), and `edit_steps` with `action` +
   `capcut_feature`.
2. **High-value:** `params` with **real numbers**; `timing` (`at_ms` vs `cue`);
   `result_description`.
3. **Nice:** `props_required`, `success_criteria`, intent notes, the prose
   narration kept alongside.

## Common pitfalls to avoid
- ❌ Vague magnitudes ("a little feather," "bring it down") → ✅ exact numbers.
- ❌ "Tap the icon in the bottom bar" → ✅ name the feature (`capcut_feature`).
- ❌ Burying the inputs in prose → ✅ an explicit ordered `inputs` list.
- ❌ Free-text technique → ✅ a `technique_primitive` from the vocab.
- ❌ Implying a tripod only in narration → ✅ `gear_required: [tripod]` +
  `capture_requirements.locked_off: true`.

See `manual_template.yaml` for a blank fill-in template.
