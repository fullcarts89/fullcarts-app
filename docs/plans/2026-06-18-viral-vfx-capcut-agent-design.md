# Viral VFX CapCut Agent — Design

**Date:** 2026-06-18
**Status:** Approved (brainstorming) → ready for implementation planning
**Owner:** liuxnard@gmail.com

## One-line summary

A **local, personal companion app** (myclaw-style) that takes a video idea from
script → finished CapCut edit: it co-writes the script, recommends viral VFX from
a library of step-by-step manuals based on what gear/props the user has, collects
the required assets with a quality gate, and assembles the edit in CapCut using a
**hybrid engine** (deterministic draft-file generation + computer-use for GUI-only
steps).

## Goals / non-goals

**Goals**
- End-to-end: idea → script → VFX pick → assets → assembled CapCut edit.
- Functional and efficient over polished. No UI chrome required.
- Runs locally on the user's Mac where CapCut Desktop lives.
- Reuse the user's existing PDF manual library as the knowledge source.

**Non-goals (v1)**
- Not a multi-user product (no accounts, hosting, billing, support).
- Not mobile CapCut (Desktop only — it has accessible draft files + reliable
  computer use).
- Not pixel-perfect autonomous editing on day one (computer use is Phase 2).

**Human-in-the-loop is intentional, not a limitation.** The agent never shoots
footage. By design the user provides all film, and two things stay human forever:
**filming** (the user shoots per the recipe's shot list) and **JUDGMENT-channel
steps** (subjective taste, e.g. color grading). The Asset QA Gate exists precisely
because the user is the one filming — it validates user-supplied footage against
the effect's spec and bounces it back with fixes. "Full automation" therefore
means: automate everything except the camera and the user's taste.

## Key decisions (and why)

| Decision | Choice | Why |
|---|---|---|
| Where it runs | Local app on the Mac | Personal tool; must drive local CapCut; no infra tax |
| CapCut version | **Desktop** | Only flavor with on-disk draft files (precision) + reliable computer use. Sample manual already ships a Desktop edit track. |
| Control surface | **Hybrid**: draft-file = spine, computer use = hands | Draft file is frame-exact & deterministic; computer use handles GUI-only steps but is slow/brittle, so it's used narrowly |
| Build sequence | **Draft-file first, computer-use last** | Phase 1 is useful with zero computer use; the brittle part is additive and degrades gracefully |
| Reasoning model | Claude Opus 4.8 (orchestration + computer use); Claude vision for asset QA; Haiku for cheap checks | Opus 4.8 has high-res vision (2576px) + pixel-accurate coordinates — right fit for a dense editing UI |
| Manual source | Parse existing PDFs | Confirmed library is "PDFs like this one" |

## Source-material findings (from the sample manual "Make an Object Appear")

The sample PDF is well-structured and validates feasibility:
1. **Machine-followable steps** — Part 2 is 38 discrete ordered edit steps
   (~75% executable, ~25% judgment tail like white-balance taste).
2. **Annotated UI screenshots** — circles/arrows mark the exact CapCut button
   (mask tool, rectangle mask). These are ground-truth references for the
   computer-use vision matcher — the single biggest de-risker.
3. **Implicit asset spec + quality gate** — "two shots: action + clean plate,"
   "focus lock," "shoot back-to-back (sun shift)," "clean plate, no cup,"
   "don't overlap your body with the mask." Some of this is programmatically
   checkable (camera locked-off between shots; object absent from plate).
4. **Desktop edit track already present** — library is not mobile-locked.
5. **Technique reuse** — "Object Appear" = *clean-plate + mask-reveal*, the same
   primitive behind disappear/teleport/clone. N manuals collapse to a few
   reusable `technique_primitive`s.

## Core data model — VFXRecipe

```
VFXRecipe
├── meta: title, slug, difficulty, editor=CapCut, shot_on, technique_primitive
├── summary / what_you_make / finished_still
├── asset_spec[]            # ordered, in capture sequence
│     ├── name, type (shot | clip | audio | ai_element)
│     ├── capture_requirements (locked_off?, green_screen?, framing, lighting)
│     └── acceptance_checks[] + variance_tolerance
├── filming_steps[]         # narration / shot list
├── edit_steps[]
│     ├── instruction, capcut_target (tool/panel), params
│     ├── channel: DRAFT | GUI | JUDGMENT     # how the agent executes it
│     └── reference_screenshot                # annotated shot, if present
└── layers_reference + narration (mobile/desktop)
```

`edit_step.channel` is the load-bearing field for execution:
- **DRAFT** — expressible in CapCut's project file (clip in/out, splits, overlay
  layers, text, transitions, timing).
- **GUI** — needs computer use (mask shape, feather drag, effect picker).
- **JUDGMENT** — handed back to the user (color taste).

## Architecture — 7 components, all local

```
   PDF library ──► 0. Ingestor (PDF → VFXRecipe DB)        # one-time / on new manuals
                            │ SQLite recipe DB
   ┌────────────────────────────────────────────────────────────┐
   │  LOCAL AGENT APP (Mac) — Claude Agent SDK                   │
   │  1. Script Studio   – hook, beats, SFX, b-roll, transitions,│
   │                       lighting, design                      │
   │  2. Context Intake  – location, gear, props on hand         │
   │  3. Recommender     – top-3 feasible VFX given script+gear  │
   │  4. Asset Director  – ordered checklist, asks one at a time │
   │  5. Asset QA Gate   – ffmpeg/OpenCV + Claude vision checks  │
   │  6. CapCut Engine   – DRAFT writer + computer-use hands     │
   └────────────────────────────────────────────────────────────┘
```

### Component responsibilities
- **0. Ingestor** — `pdftotext`/`pdftoppm` for text + page rasters; Claude vision
  to read annotated screenshots and tag which UI element each step points at;
  emits a `VFXRecipe` row + classifies each edit step's `channel`.
- **1. Script Studio** — conversational; produces a structured script object
  (hook, beats, SFX cues, b-roll list, transitions, lighting/design notes).
  Kept lean — function over polish.
- **2. Context Intake** — captures location, equipment, available props as a
  `capabilities` record used to filter recipes.
- **3. Recommender** — ranks recipes whose `asset_spec`/`capture_requirements`
  are satisfiable by `capabilities` + script; returns top 3; user picks one.
- **4. Asset Director** — walks `asset_spec` in capture order, requesting one
  asset at a time.
- **5. Asset QA Gate** — runs `acceptance_checks` per asset: programmatic
  (ffmpeg/OpenCV — e.g. camera-motion/alignment between action shot & clean
  plate, object presence/absence, duration, resolution) + Claude vision
  (framing, lighting, subjective spec). Accept, or bounce with specific fix
  feedback. `variance_tolerance` defines pass/fail thresholds.
- **6. CapCut Engine** — DRAFT-file writer (reverse-engineered desktop
  `draft_content.json`) for structural steps; computer-use loop for GUI steps,
  using recipe `reference_screenshot`s as visual anchors; JUDGMENT steps emitted
  to a finish-by-hand checklist.

## Runtime loop (the user's workflow)

Script Studio co-writes the video → Intake asks location/gear/props →
Recommender filters to the 3 achievable VFX and the user picks → Asset Director
hands over the asset list in capture order → per asset, QA Gate checks against
`acceptance_checks` and accepts or bounces with feedback → once all assets pass,
CapCut Engine assembles the edit → (Phase 3) verification compares the render to
the script.

## Phasing

- **Phase 0 — Ingestor.** Parse the PDF library into the recipe DB. Validate
  against the sample manual. Deliverable: queryable `VFXRecipe` records.
- **Phase 1 — MVP ("assisted").** Full brain (Script Studio → QA Gate) +
  **DRAFT-file generation**. Output: a CapCut project that opens pre-assembled +
  a short checklist of GUI/JUDGMENT steps to finish by hand. No computer use.
  Fully useful, low risk.
- **Phase 2 — close the loop.** Add the computer-use executor for GUI steps.
- **Phase 3 — verify & scale.** Automated render-vs-script verification, more
  primitives, polish.

Graceful degradation: if computer use breaks (CapCut UI update), the app falls
back to Phase-1 behavior, not a dead app.

## Tech stack

- **Language:** Python 3.9-compatible (matches repo conventions — no `X|Y`
  unions, use `typing`), in a new top-level module (e.g. `vfx/`).
- **Agent:** Claude Agent SDK / Anthropic SDK; Opus 4.8 orchestration, vision QA.
- **PDF ingest:** poppler-utils (`pdftotext`, `pdftoppm`) + Claude vision.
- **Asset QA:** ffmpeg (already available) + OpenCV.
- **Storage:** local SQLite (personal tool — no Supabase dependency).
- **CapCut:** desktop `draft_content.json` writer; computer use self-hosted on
  the Mac via the Agent SDK.

## Top risks / open questions

1. **CapCut draft-file format** is undocumented/reverse-engineered and can change
   between CapCut versions. Mitigation: pin a CapCut version; keep DRAFT scope to
   stable structural fields; computer use covers the rest.
2. **Computer-use precision/speed** on a dense timeline. Mitigation: Phase-2-only;
   narrow GUI scope; lean on annotated-screenshot anchors.
3. **Asset QA thresholds** — `variance_tolerance` needs calibration per primitive.
   Mitigation: start strict + manual override; tune against real footage.
4. **Manual variability** — not all PDFs may be as clean as the sample.
   Mitigation: ingestor emits a confidence/coverage score; low-confidence recipes
   flagged for human review.
5. **Dev environment** — this repo (cloud container) builds & tests the brain +
   draft writer; computer use can only run on the user's Mac. CapCut-driving steps
   are validated locally, not in CI.

## Out of scope for now
Multi-user/product surface, mobile CapCut, non-CapCut editors, marketplace/sharing.
