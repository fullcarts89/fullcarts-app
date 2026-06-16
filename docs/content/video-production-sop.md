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
- Shoot the locked script in one continuous take (2–3 takes). Export per the rules in §0. Send the **SRT** (gives exact reveal timings).

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

## Lessons from the CPI Take (what cost time — avoid)
1. **Length undecided** → it ballooned to 2:29 before we set ≤60s. Decide first.
2. **Captions burned into the film** → forced a re-shoot/re-export + re-render. Always export caption-free.
3. **VO number flub ($13)** → read numbers back before filming.
4. **Synth SFX "beep"** → use the real SFX library from the first pass.
5. **Killed a render mid-job to add a tweak** → wasted ~12 min. Never again; batch tweaks, let jobs finish.
6. **Chart polish rounds (axes, overlaps)** → bake the "axes + labels + clear text zones" rule into every chart up front.
7. **Full-res every iteration** → use `--scale 0.6` for reviews, full-res only on the approved final.
8. **Re-deriving the chunked-upload path/command every single video** (this happened *again* Jun 2026, ~5 rounds) → §5 is now the canned, copy-paste answer with the real path convention. Never re-ask where the film is or rebuild the `split` line from scratch.
