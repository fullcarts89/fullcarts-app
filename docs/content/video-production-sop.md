# Video Production SOP — talking-head + Remotion data overlays

Derived from the **CPI Take** build (Jun 2026). This is the repeatable path from idea → finished MP4,
plus the **decide-upfront checklist** that kills the back-and-forth. Pair with `production-playbook.md`
(weekly rhythm), `references/hooks.md` (hook system), and `music-beds.md` (audio lanes).

---

## 0. Decide UPFRONT (the anti-back-and-forth checklist)
Lock these *before* filming or rendering — most of the CPI Take rounds came from settling these late:

- [ ] **Length target** — default **≤60s** (hook-first). State it in the brief.
- [ ] **Format / series** — Shrink Check, Caught:, The Take, etc.
- [ ] **Hook** — write + approve **The Snap** first (it's the whole ballgame). Don't film until it's locked.
- [ ] **Beat map** — which lines are FACE vs which get a VISUAL cutaway (and what each visual shows).
- [ ] **Shot map** — assign each beat a **camera setup/angle** (medium → wide → top-down → close-up → high-angle → low-angle). The angle change *is* the visual re-hook (see §4 Shot grammar + `references/retention-spine.md` beat 3). Decide physical-multi-angle vs single-take + FinalVideo punch-ins **before** filming.
- [ ] **Numbers** — every on-camera stat traced to `approved-claims.md` §1 or a fresh DB pull. Read them back so there's **no VO flub** (e.g. the "$13 vs $1,300" miss).
- [ ] **SFX intent** — what sound on what cut (riser? whoosh on cut-IN only? impact?). Use real files in `video/public/audio/sfx/`, not synths.
- [ ] **Film export rules** — **1080×1920, H.264, 30fps, and NO burned-in captions** (captions are added last, after the cut). This single rule saved a full re-render.
- [ ] **File handover is pre-agreed (§5)** — films live at `~/Documents/Social Videos/<batch>/<clip>/Film_no captions.mov`; chunk with the canned `split` one-liner. Never re-ask where the file is or re-derive the command.

## 1. Brief (data) — operator
- Refresh banner counts; pull candidates (`references/operator-loop.md` SQL); dedup against `content-log.md`; run the 3 gates.

## 2. Hook + script — operator
- Snap hook (context → lean → snap) + "it's not you" lock-in. Keep total ≤60s. Per-platform captions/hashtags.

## 3. Overlay assets — Remotion (`video/`)
- One composition per data beat; **every chart gets labelled X/Y axes + value ticks**; brand tokens from `src/lib/theme.ts` (graphite/cream/alert-red, Space Grotesk/JetBrains Mono); Brandmark on each.
- Each cutaway is full-frame 1080×1920 (renders to `.mp4`). Music bed baked per `music-beds.md` lane (volume ~0.15–0.2 under VO).
- Expose timing knobs (`startDelay`, `sweepFrames`) so reveals sync to the VO/SRT.

## 4. Film — human

### Shot grammar — one angle per beat (the re-hook is the camera move)
Don't shoot the whole script from one locked-off angle — a static frame is where attention dies.
**Give every retention beat its own camera setup**, all in the *same location* (your counter/kitchen
with the real product). The cut between angles re-grabs attention exactly at the sag — it's the
*physical* version of the re-hook in `../../.claude/skills/fullcarts-content/references/retention-spine.md`
(beat 3). Map:

| Spine beat (`retention-spine.md`) | Camera setup | Why this angle |
|---|---|---|
| 1 · **Hook** | **Medium, eye-level** | bold, direct — state the product + that it shrank, to camera |
| 2 · **Agitate / lock-in** | **Wide** | relatable, "I'm in your kitchen" — leads into the context |
| 3 · **Re-hook / context** | **Top-down** over the product + receipt | resets the eye **and** doubles as honest product proof (real item on the counter) |
| 4 · **The turn** ("it's not you") | **Close-up** — **pause the music** | audio pattern-interrupt synced to the reveal; intimacy on the "it's not you" line |
| 5 · **Payoff** (the %, the Generosity Tax) | **High-angle wide — restart the music** | music kicks back as the emotional payoff lands |
| 6 · **Peak-cut ending** | **Close-up, slight low angle** | subtly authoritative; end on the number, **no summary** — the hook already did that. Just leave. |

**The audio move (do it):** at beat 4 **cut the music**, deliver the turn dry, then **restart it** on
the payoff (beat 5). The silence is a pattern-interrupt that makes the "it's not you, it's them" land.

**Two ways to get the angles (pick in §0):**
- **Physical multi-angle (hero pieces):** re-position the phone and re-deliver each beat as its own
  short clip. Most authentic; trades the single clean VO take for visual variety — keep VO energy
  consistent across setups so the assembled audio doesn't jump.
- **Single take + FinalVideo (fast turnarounds / B-side):** shoot one continuous take, then approximate
  the angle changes with `FinalVideo`'s camera track (zoom / punch-in / **fake-angle rehook** — see
  `SESSION-HANDOFF.md`). Lower effort, keeps one clean VO, but reads less varied than real angles.

**Gate note:** the top-down "proof" angle must show the **real** product/receipt (three-bucket policy,
`gates.md`) — never a staged or AI prop. The angle sells it; the evidence underneath stays honest.

> Shot grammar adapted from Dominique Holmes (`@dominique.holmess`),
> https://www.instagram.com/reel/DU5Gr7hEwfo/ — "25k followers, two reels": medium → wide → top-down →
> close-up (music out) → high-angle wide (music in) → low-angle close, no summary.

### Capture basics
- Shoot the locked script (2–3 takes per setup). Export per the rules in §0. Send the **SRT** (gives exact reveal timings).

## 5. Get the film to the operator (chunked upload) — DO NOT re-derive this every time

**Canonical local layout (this is where the files always live — assume it, don't ask):**
```
~/Documents/Social Videos/<Batch e.g. "Jun 26">/<Clip slug e.g. "Spring Cleaning">/
    Film_no captions.mov          ← the caption-free film (per §0 export rules)
    <slug> Viral VFX script.pdf   ← the shooting script
    SRT file <slug>/              ← the .srt (exact reveal timings)
    SFX/                          ← any per-clip sound effects
```
The upload cap is **30 MB**, the film is ~150–200 MB. **One-shot command — paste as-is**, only swap the
two bracketed folder names to match the batch/clip:
```bash
cd ~/Documents/"Social Videos"/"Jun 26"/"Spring Cleaning" && split -b 25m "Film_no captions.mov" film_chunk_ && ls -lh film_chunk_* && shasum -a 256 "Film_no captions.mov"
```
- Quote each path segment with spaces (`"Jun 26"`, `"Spring Cleaning"`) — that's the bug that ate three rounds.
- `-b 25m` keeps every chunk safely under the 30 MB cap; `shasum` lets the operator verify the rebuild.
- **Path unknown / folder renamed?** Path-agnostic fallback (finds it anywhere under Documents):
  ```bash
  f=$(find ~/Documents -name "Film_no captions.mov" -print -quit) && cd "$(dirname "$f")" && split -b 25m "Film_no captions.mov" film_chunk_ && ls -lh film_chunk_*
  ```

Upload all `film_chunk_*` files + paste the `shasum` line. **Operator reassembles + verifies:**
```bash
cat film_chunk_* > "Film_no captions.mov" && shasum -a 256 "Film_no captions.mov"   # hash must match
```

## 6. Render pipeline (operator — the technical part, repeatable)
The remote env blocks Remotion's headless-shell download, so point it at the Playwright Chromium:
```bash
cd video && npm install                      # one-time per session
B=/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell

# a) render each overlay cutaway (full-frame mp4)
npx remotion render <Comp> out/<name>.mp4 --props=src/props/<name>.json --browser-executable=$B
cp out/cpi-*.mp4 public/cuts/                 # cutaways live in public/ for the assembly

# b) put the film + screenshots in public/ ; build src/props/cpi-final.json (FinalVideo timeline:
#    film, cutaways[fromSec,toSec], overlays (hook text), camera (zoom keys), sfx[atSec,volume], captions:[])

# c) FAST review render (≈half the time, fine for judging timing/SFX/layout)
npx remotion render FinalVideo out/final.mp4 --props=src/props/cpi-final.json --browser-executable=$B --crf 23 --scale 0.6
# d) FINAL render once approved: drop --scale (full 1080×1920)
```
- **Remotion ships its own ffmpeg** — `npx remotion ffmpeg …` (probe, extract frames to QC, transcode). No system ffmpeg needed.
- **FinalVideo** (`video/src/compositions/FinalVideo.tsx`) is the assembler: `film` layer + `cutaways` (full-screen, with Ken-Burns `zoom` for images) + `overlays` + `camera` punch-ins + `sfx` + `captions`. VO from the film plays under everything; music beds are baked in the cutaways.
- **QC without watching:** `npx remotion ffmpeg -ss <t> -i out/final.mp4 -frames:v 1 out/_f.png` then view the frame.
- **NEVER kill a running render** to make a change — let it finish, then iterate. (Hard rule.)

## 7. Deliver + log
- Heavy renders are gitignored (`out/`) — `git add -f` to put a copy on the branch for download; **strip before merge**.
- Deliver: attach the file + a GitHub raw link (`…/raw/<branch>/video/out/final.mp4`).
- Make the thumbnail (HTML mockup → Playwright screenshot, branded) and the per-platform captions/description.
- Append the post to `content-log.md`.

## 8. Upload-quality / crispness checklist (the publish step)

Crispness is **two halves: render quality + defeating the app's upload compression.** A great master
still looks soft if the platform app silently recompresses it on upload. Do both.

**Render side (operator) — give the upload something to preserve:**
- Export the **final master at high quality** — for the §6 *final* render use a low CRF (`--crf 18`,
  not the review default 23). The review `--scale 0.6 --crf 23` pass is for timing only.
- **Avoid double-compression:** deliver the master once; don't re-encode it through multiple tools
  before it reaches the phone. Every re-encode softens it.

**Instagram upload settings (human, in the IG app) — paths verified 2026-06; IG's UI drifts, so confirm in-app:**
1. **Settings → Media quality → "Use less cellular data" = OFF.** This data-saver **compresses your
   video and drops quality** — leave it off.
2. **Same screen → "Upload at highest quality" = ON.** Uploads at the highest resolution instead of
   auto-adjusting to the network. Slower upload, sharper result. *(Leave "Disable display of HDR media"
   at its default.)*
3. **Per-post sharpen (light touch):** uploading a reel → **Edit Video** (lower-left) → **Edit** →
   **Adjust** → scroll right → **Sharpen.**
4. **Upload on strong Wi-Fi** — "highest quality" needs bandwidth; on a weak connection IG falls back
   to a compressed upload even with the toggle on.

**Cross-platform (same principle, every app):** TikTok has **"Allow high-quality uploads" / "Upload
HD"** in its settings; defeat each platform's default upload compression natively at post time. This
is a per-platform publish step (like the trending-audio swap), not something baked into the master.

> **⚠️ Brand caveat on sharpening — go light.** Our look is **text-heavy** (captions, `StatCard` /
> chart overlays, the CAUGHT stamp). Over-sharpening rings/halos on edges and makes crisp Remotion text
> look *fried*. The overlays are already sharp from the render — sharpen the **filmed footage** subtly,
> don't crank IG's slider. QC on a chart/caption frame, not just a face frame, before posting.

> Source: Valerie Lisitsyna (`@valerie_lisitsyna`), https://www.instagram.com/reel/DWXlf4FiRi_/ —
> "crisp without 4K": IG media-quality settings + pre-upload sharpen.

## Lessons from the CPI Take (what cost time — avoid)
1. **Length undecided** → it ballooned to 2:29 before we set ≤60s. Decide first.
2. **Captions burned into the film** → forced a re-shoot/re-export + re-render. Always export caption-free.
3. **VO number flub ($13)** → read numbers back before filming.
4. **Synth SFX "beep"** → use the real SFX library from the first pass.
5. **Killed a render mid-job to add a tweak** → wasted ~12 min. Never again; batch tweaks, let jobs finish.
6. **Chart polish rounds (axes, overlaps)** → bake the "axes + labels + clear text zones" rule into every chart up front.
7. **Full-res every iteration** → use `--scale 0.6` for reviews, full-res only on the approved final.
8. **Re-deriving the chunked-upload path/command every single video** (this happened *again* Jun 2026, ~5 rounds) → §5 is now the canned, copy-paste answer with the real path convention. Never re-ask where the film is or rebuild the `split` line from scratch.
9. **Revised on-screen numbers silently contradicting the recorded VO.** When the creator changes figures mid-edit (Swiffer 28→32 ct, Febreze 8.8→16.9 oz), the *filmed voiceover still says the old numbers*. **Flag the mismatch the moment numbers change** — never ship visuals that contradict the audio. (These were a different DB product than the VO cited: Swiffer *Wet Cloths* 32→24 vs *Dusters* 28→24; Febreze *Fabric* 500→438 ml vs *Air Mist* 8.8→8.1 oz — verify which entry the new figure is.)

## Fixing the VO without a re-record (cloned-voice dub)
When numbers change but the creator won't re-record, you can dub corrected lines **only under full-frame cutaways** (face hidden → **no lip-sync problem**). Proven path (Jun 2026):
- **Clone the voice via Vidiq `vidiq_voiceover_clone_start` (YouTube URL).** The raw-audio clone (`vidiq_voiceover_clone`) is **not usable from here** — it needs the sample inlined as base64, and a 60s clip is ~520K chars (too large for a tool call). The URL variant has Vidiq fetch the audio, so size is a non-issue.
- **Source quality matters:** a **Short** gave a weak clone that drifted to a generic British accent. Prefer a **longer, clean, music-free** source (a 1–3 min talking video, or the creator's own clean VO uploaded unlisted).
- **Generate** the corrected lines (`vidiq_voiceover_generate`), then **level-match** to the film VO with `volumedetect` (target the film's mean dB; this batch: −5 dB / −1.2 dB) and splice with ffmpeg: `volume=0:enable='between(t,A,B)'` to mute the stale region + `adelay` to place the clip, `amix ...:normalize=0`. Keep the dub **inside the cutaway window only**; the real voice carries every face beat.

## Environment toolchain prep (install on demand)
- **webp images:** the bundled ffmpeg can't decode webp → `pip install pillow` and convert with PIL.
- **PDF text:** pypdf's cffi backend is broken here → `pip install pymupdf` (`fitz`).
- **Frame-accurate re-encode trims** (libx264): `pip install imageio-ffmpeg`; its binary handles `trim/concat` + `libx264`. (Remotion's own ffmpeg is for probe/extract, not re-encode.)
- **Filenames with spaces** break the `remotion ffmpeg` wrapper ("No such file") → rename before use.
- **Long signed URLs** (S3 voiceover downloads): copy exactly inside single quotes — a stray break corrupts the signature.
