# FullCarts Production Playbook — Stack + Repeatable Workflow

**Date:** June 10, 2026
**Parent strategy:** `docs/plans/2026-06-10-face-forward-content-strategy.md`
**Goal:** Produce 3–5 face-forward, rules-compliant clips/week in **4–6 hrs**, from one batch film day, without burning out. This is the operational layer — the "how," step by step.

You have no content-creation experience, so this is written as a literal procedure. Follow the loop; the quality is engineered into the steps.

---

## The core principle: separate the moat from the labor

Two layers, two very different treatments:

- **The moat (do once, reuse forever):** your face, your **real before/after evidence images**, your data visualizations, your FullCarts screen-records. These are what nobody can copy. Build a reusable kit so each one costs minutes, not hours. (You usually *won't* have the physical product — the proof is the documented image, not a product in your hands.)
- **The labor (automate ruthlessly):** captioning, silence-trimming, b-roll cutaways, scheduling, scripting first drafts. Hand all of it to AI tools.

The whole stack below is just this principle applied tool by tool.

---

## Recommended stack (mapped to the tools you already have)

| Stage | Tool | Role | Notes |
|---|---|---|---|
| **Ideation** | **Claude** (via the `fullcarts-content` skill) | Run the brief generator; rank ideas; pull data from the FullCarts DB (Supabase) | Ideation only — never writes the finished post. The convergence detector + 5-rule scorer. |
| **Scripting** | **Claude** | Draft the full hybrid script (hook→proof→context→payoff→CTA), captions, hashtags per platform | You edit to your voice. Claude proposes; you approve. |
| **Filming** | **Your phone** | Film the hook + explainer (face, to camera) | The proof is shown as **real before/after image cutaways**, not a held product. Authentic > polished. |
| **Data viz** | **Remotion** (the `video/` toolkit; Claude renders) | On-brand data overlays: the −12.5%, "32oz → 28oz," the FullCarts step-chart, lower-thirds | The moat, custom and reusable. Template built once (`video/`); feed it data forever. |
| **Atmosphere b-roll** | **Higgsfield** (MCP) | Bucket-2 connective shots ONLY — abstract intros, mood, metaphor | NEVER fake packaging/charts (Bucket 3). Toggle the AI label. Use `virality_predictor` to gut-check a cut. |
| **B-side / hook tests** | **Agent Opus** (`opus.pro/agent`) | AI-UGC web app: a script/brief → 9:16 video with cloned-or-AI voice + your-or-AI avatar + stock visuals; multiple hook variations | **Separate tool, NOT Claude.** Faceless evergreen + A/B hook tests only, clearly AI-labeled. Never a stand-in for your real face on authority pieces. |
| **Assembly + captions** | **Captions App** | Rough cut, burn-in captions, silence removal, eye-contact, layer sound FX/music, batch edit | The finishing line. Where most of the labor disappears. No API — manual by design. |
| **AI voice** | **ElevenLabs** | Voiceover for *faceless evergreen / pure-data* clips only | Keep your REAL voice on authority + personal pieces. AI voice is for the SEO/data B-side. |
| **Scheduling** | Buffer (free) or native schedulers | Queue TikTok/Reels/Shorts; post X reactively | X newsjacking is posted live, not scheduled. |

**Subscription verdict:** this covers everything — no need to add Placid/JSON2Video from the old plan (those rendered fake stat-cards, which is exactly the Bucket-3 failure mode). If you want one *optional* add, **Opus Clip or Submagic** (~$9–23/mo) is the best "long explainer → many shorts" slicer and has punchy auto-captions; you can defer it until you're filming longer-form. **Teleprompter app** (free) is worth it day one — it kills retakes on the hook.

---

## The reusable asset kit (build this ONCE, week 0)

Spend one 60–90 min session before your first batch making "real" the fast path:

1. **Screen-record FullCarts pages** — the homepage counter, a `/brands/[name]` timeline, a `/products/[id]` step-chart, the running shrink total. Clean 1080×1920 captures you'll reuse across dozens of videos.
2. **Screenshot the real source charts** — FRED CPI, BLS shrinkflation series, ICE coffee. Grab fresh on data-drop days.
3. **Build a before/after image bank** — collect the real side-by-side / before→after images for your picks (from FullCarts entries, retailer listings, Reddit r/shrinkflation, news). This is your proof layer; you source it, you don't film it.
4. **The Remotion template is already built** — see the `video/` package (`@fullcarts/video`). It has four data-driven compositions (`ShrinkOverlay`, `StatCard`, `RundownChip`, `SourceFrame`); each takes a props JSON (`{brand, oldSize, newSize, pctChange, unit, source}`) and renders the branded overlay. Claude renders these for you; every new overlay is a one-line props change. (See `video/README.md`.)
5. **Set the look** — pull the FullCarts design system (dark graphite + Space Grotesk + JetBrains Mono + alert red, per `FULLCARTS_DESIGN_EXPORT.md`) into the Remotion template and your caption style so every clip is unmistakably yours.

---

## The weekly loop (4–6 hrs)

### ① Saturday — Brief (15–30 min)
- Run the content-brief generator (`pipeline/scripts/generate_content_briefs.py`, via Claude / the `fullcarts-content` skill) → ranked digest of ideas, each with data + why-now + source URLs + a 5-rule score.
- **Pick 3–5.** Favor a mix across the content buckets (≈2 educational, 1 newsjack, 1 reveal/entertainment, rotate in 1 personal).
- For a newsjack, check the BLS/CPI/USDA calendar — if a print lands this week, that's an automatic slot.

### ② Saturday — Scripts + assets (30–45 min)
- Claude drafts each script in the repeatable template (hook→proof→context→payoff→CTA) with per-platform captions + hashtags. **You edit each to sound like you** — read it out loud; if you wouldn't say it at the store, change it.
- Run each script through the **pre-publish checklist** (`content-rules.md`). 5/5 or it doesn't make the shoot list.
- Claude renders the **Remotion overlays** for each from the `video/` toolkit (feed it the numbers from the brief). Render now so they're ready for edit.
- (Optional B-side) feed the script to **Agent Opus** to generate a faceless UGC variant or hook A/B tests — clearly AI-labeled, never a stand-in for your real-face core.
- Pull the needed real assets for each pick: the **before/after image** (FullCarts entry / listing / Reddit / news), the FullCarts screen-record, the source chart.

### ③ Sunday — Batch film (60–90 min)
- One sitting, good light (window or ring light), phone on a stand, **teleprompter app** running your hooks.
- Film **all 3–5 pieces** to camera back to back (hook + explainer). The proof images/screens are dropped in at edit — you don't film them. Batching like-with-like is the time saver.
- Don't aim for perfect — aim for real and energetic. Reshoot only the hook if the first 3 seconds are flat (that's the one beat worth a retake).

### ④ Sunday — Assemble + caption (60–90 min)
- In **Captions App**: drop each clip, auto-caption (burn them in), trim silences, fix eye contact, layer light sound design.
- Drop in the **Remotion overlay** *the moment you say the number* (≈0.2–0.5s before you say the subject — the brain reads visuals slightly ahead of audio). Pin it next to the product.
- Add a **Higgsfield** atmosphere shot only if a clip needs an intro/transition — labeled, Bucket-2 only. Optionally run the cut through Higgsfield `virality_predictor` for a hook gut-check.
- Final pass against the checklist: captions on, 9:16, cut every 2–4s, CTA present, no Bucket-3 AI.

### ⑤ Sunday — Schedule (15–20 min)
- Queue the week: TikTok first (native), cross-post to Reels + Shorts with per-platform caption tweaks. Stagger across Mon/Wed/Thu/Fri.
- Leave the X slots empty on purpose — those are live newsjacks.

### ⑥ Mon–Fri — Engage (15 min/day)
- Reply to every comment in the first hour (first-hour engagement drives ~80% of reach).
- 5–10 quality comments on other creators' / news posts in the niche.
- Fire any reactive X post when a data drop or viral receipt hits — quote it with your chart + a one-line verified take.

---

## Faceless evergreen B-side (optional, for volume)

When you want extra reach without filming, spin a **pure-data, faceless** clip: Remotion data-viz + **ElevenLabs** voiceover (your cloned voice or a brand voice) + Captions. These are great for SEO/evergreen ("Every Cadbury size change since 2019") and don't cost a film day. Keep them clearly the B-side — your face stays the channel's identity. (Still Bucket-1 clean: real screenshots, real numbers.)

---

## How assembly actually works (where graphics/cutaways/SFX get added)

Important mental model: **Remotion doesn't watch your footage and decide things.** It's a deterministic
renderer — it only places what it's told to place. The *decisions* (which overlay, when, which cutaway,
which SFX) come from the **script/packet** (Claude) and your judgement. Two ways to assemble:

**Model A — Remotion makes the assets, you assemble in Captions App (START HERE).**
1. Film your talking head on your phone.
2. Claude renders the branded graphics as **alpha `.mov` overlays** (ShrinkOverlay, CaughtTitle, etc.) + the StatCard/Thumbnail.
3. In **Captions App**: import your film → auto-captions (set to the caption-lane style) → drop each `.mov` overlay onto a track above the video at the beat the packet specifies → add cutaways/b-roll and SFX from Captions' library (or your bank) using the packet's cues.
- *Why start here:* fastest to learn, full tactile control, captions + SFX + cutaways are exactly what Captions App is built for. No coding per video.

**Model B — full programmatic assembly in Remotion (scale-up, optional).**
You hand Remotion your raw film **plus a timeline** (a JSON: overlay cues + cutaway clips/timestamps + SFX cues + caption text/timings), and a single `FinalVideo` composition composites *everything* — your footage (`<OffthreadVideo>`), the overlays, cutaways, burned-in captions, and SFX (`<Audio>`) — into one finished MP4.
- *Yes, this is the "feed Remotion my film and it layers on the graphics + cutaways + sound" idea — it's fully possible.* The catch: it needs accurate caption timing (auto-transcribe with Whisper / `@remotion/captions`), the cutaway clips + SFX files prepared, and the timeline authored (Claude can generate the timeline JSON from the packet). It's more setup and less tactile, but it's repeatable and consistent at volume.

**Recommendation:** run **Model A** for your first batches (learn the rhythm, see what lands). Once the format is dialed and you want to cut edit time, I can build the **`FinalVideo`** Remotion composition (Model B) so the operator outputs near-finished cuts and you just review. Either way, Claude's packet is the brain (cues + caption text + cutaway/SFX suggestions); Remotion and Captions App are just the two ways to execute it.

## The proven loop (SRT-synced Model B) — USE THIS

Validated on the first real piece (Caught: Folgers). This is the standing process for every piece:

1. **Film** to camera — vertical **9:16**, ~60s, **no product needed** (the proof is the real
   before/after image, shown as a cutaway). Face upper-center; leave the lower-middle clear.
2. **Caption it in your app** (CapCut/Captions) and **export the `.srt`**. (Your app transcribes the
   audio anyway — the SRT is just that transcript with word timings.)
3. **Send the operator, as FILES:**
   - the **film** (compress to <30 MB if the chat caps it),
   - the **`.srt`**,
   - the **evidence** — before/after listing screenshots + any chart — **zipped** (⚠️ pasted/attached
     *images* don't reach the operator in some environments; only real files like `.mov`/`.zip`/`.srt`
     do — so **zip the images**).
4. **Operator builds it:** a clean **before/after card** (real cans cropped out of the listing +
   brand labels for size + price-per-oz), the **real chart** behind the `SourceFrame` citation, and
   **every overlay/cutaway synced to the SRT word timings** — evidence appears *only when you name it*,
   your face is primary the rest of the time, no duplicated data. Output: a finished MP4, **no captions**.
5. **You** add captions in your app (from the same SRT) and post.

**Why the SRT is non-negotiable:** without it, overlay timing is a blind guess and the cut feels like
a slideshow interrupting you (we saw this on the first attempt). With it, evidence lands on the exact
word. The engine is the `FinalVideo` composition (`video/`); the SRT timings drive a timeline JSON
(`src/props/<brand>-final.json`).

## Cutaway layout + evidence — LOCKED (from the 4th-of-July build)

Hard-won on the 4th-of-July "Generosity Tax" cut (cost a lot of back-and-forth). Bake these in so the
operator nails it on the first pass:

- **Every evidence cutaway shows the creator's REAL product photo(s).** A branded number graphic with
  no bag on screen is *not* trustworthy — viewers won't believe a size shrink they can't see. Use 1–2
  photos per item (two = before/after; one = a shot that already shows both). Numbers stay photo-verified.
- **For paired photos, the creator tags which is BEFORE vs NOW** — the operator often can't tell from the
  image. Put it in the zip filenames or the handoff note.
- **Layout law — evidence fills the TOP 2/3; the BOTTOM 1/3 stays clean** for the creator's (minimized)
  talking head + burned-in captions, which they overlay in their app. The operator renders the top-2/3
  plate and never fills the bottom third.
- **Sequence:** open on the face + ONE hook line ("'Party size' is a lie") → **back-to-back full-frame
  animated evidence cutaways**, one per product, *no cut back to face between them* → return to the face
  for the take → close on the `OutroCard` "follow" animation (same as past cuts).
- **The operator delivers the finished MP4 in-session.** Remotion renders in the cloud sandbox — point it
  at the headless-shell binary (plain chrome fails with "old headless removed"):
  `--browser-executable=/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell`; ffmpeg
  via `pip install imageio-ffmpeg`. Engine = the `ShrinkCutaway` composition inside `FinalVideo`; the
  SRT timings drive `src/props/<brand>-final.json`. Full recipe in `video/README.md`.

## Tool-by-tool cheat notes

- **Claude** (the `fullcarts-content` skill) — your creative director + data analyst + operator. It reads the DB, ranks ideas, drafts scripts, renders the Remotion overlays, generates Higgsfield b-roll, runs the gates, and writes platform captions. It stops at *film-ready packet* — you film and approve.
- **Agent Opus** (`opus.pro/agent`) — a **separate AI-UGC web app, not Claude.** Paste a script/brief → it generates a 9:16 UGC video (cloned-or-AI voice, your-or-AI avatar, stock visuals, multiple hook variants). Use for the faceless B-side + hook A/B tests only, clearly AI-labeled; never as your real face on authority pieces.
- **Remotion** — the `video/` toolkit: programmatic, deterministic, on-brand data viz. One template, infinite data — your overlays as a moat instead of generic CapCut text. (See the project's `remotion` skill + `video/README.md`.)
- **Higgsfield** — atmosphere/metaphor b-roll + `virality_predictor`. Hard rule: never let it render anything a viewer could read as evidence.
- **Captions App** — the assembly + caption + sound finishing line; batch mode for the whole week at once. No API — you drive it; the packet makes it drop-in.
- **ElevenLabs** — voice for the faceless B-side only; your real voice carries authority/personal pieces.

---

## What "done" looks like each week

5/5 on every clip's checklist, 3–5 clips scheduled across TikTok/Reels/Shorts, X armed for the week's data drop, and you spent **one Saturday planning slot + one Sunday afternoon** — not your whole week. That's the burnout-proof target.
