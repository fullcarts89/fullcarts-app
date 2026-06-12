# FullCarts video production playbook

Lessons from the Folgers Reveal build (2026-06-11/12) — the first full video
through the Remotion pipeline, including ~6 founder review rounds. Read this
BEFORE starting the next video. Companion docs:

- `video/README.md` — workspace commands + remote-render specifics
- `video/public/folgers/ASSETS.md` — the per-video asset manifest pattern
  (copy this structure for each new video)
- `docs/content/contentstyleboard.html` — THE signature style board: colors,
  type, the overlay components in context, thumbnail pattern, sound palette.
  Realised in code in `video/src/FolgersReveal/Overlays.tsx`
- `docs/content/folgers-emphasis-map.md` — the zoom/SFX beat-map format
- `video/public/sfx/README.md` — the 13 named SFX slots
- `FULLCARTS_DESIGN_EXPORT.md` — the site design system the video must read as
- `docs/plans/2026-06-08-social-content-strategy.md` — AI-vs-evidence policy

## The pipeline (what worked)

1. Founder records + edits in Captions; exports **MP4 + SRT**. Captions burns
   its own captions — Remotion renders NO caption layer (we built one, then
   removed it).
2. **Verify the SRT against the actual export** before trusting any timing:
   the Folgers export ran 1.5s shorter than its SRT (an "Um," cut + tail trim
   after the SRT was generated). Silence-gap analysis (ffmpeg silencedetect,
   compare gaps to SRT cue boundaries) showed cues 1–5 aligned ±0.25s and
   only the tail had drifted → retimed only the last cue. Always run this check.
3. Transcode the export **HEVC → H.264** (`-c:v libx264 -crf 18`): Captions
   exports HEVC; open-source Chromium (Studio preview + headless render boxes)
   has NO proprietary codecs. `OffthreadVideo` decodes via ffmpeg so renders
   survive, but the `getVideoMetadata` probe and Studio preview need H.264.
4. Build/adjust the comp; **verify with stills, not full renders** (`remotion
   still --frame=N`, ~30s each vs ~8 min for a render). Full render only when
   a review round is ready.
5. Deliver via git (`git add -f video/out/*.mp4`, push, raw.githubusercontent
   link) — chat file delivery proved flaky for the founder at ~70-90 MB, and
   outbound upload hosts are network-blocked. **Strip the heavy renders from
   the branch before merge** (or squash-merge drops them).

## Founder taste calibration (the expensive lessons)

These took six review rounds to learn. Start here next time:

- **No empty black space.** Full-screen cutaways must be FILLED: evidence
  frame up top, a signature card (ShrinkOverlay / StatCard / CiteCard) in the
  lower half. The first cutaway draft was a frame floating in darkness — rejected.
- **Cut away ≥30% of the runtime** (Folgers landed ~42%). The talking head
  alone is the failure mode; full-screen branded panels, not floating cards
  over the face.
- **SFX restraint beats SFX coverage.** We started at 13 sound types / 23
  cues and converged on **7 sounds**, **3 stamps** (sonic logo — never more),
  **3 thunks** (only the highest-stakes punch-ins), whooshes INTO cutaways
  only, and the 4 data sounds (roll/ding/deflate/pop). "Too much variety" was
  the exact complaint. One motif used consistently > many clever sounds.
- **Zoom punch-ins: yes, broadly.** The founder loved these. But cut any zoom
  adjacent to a transition whoosh (redundant), and don't sound every zoom.
- **Sustained sounds read much hotter than transients** at equal peak: the
  1s slot-machine roll needed volume 0.15 where stamps sit at 0.6–0.7.
- **The drone bed**: constant, low-register, textural; bed level 0.075 after
  loudnorm to −16 LUFS (0.12 was "a little too loud"). Dips with the feather
  gag, dies completely at the CTA. Beds from libraries are often mastered
  ~9dB quiet — loudnorm them or they vanish.
- **AI sound generation was rejected** ("these are not good SFX") — founder
  sources library sounds (Pixabay/Freesound), uploads a zip, we trim/normalize
  into the slots. AI imagery is banned outright (evidence policy); treat AI
  audio as banned too.
- **Real numbers only, queried live**: the 2,228 StatCard count came from
  `published_changes` at build time. Never reuse a stale count.
- **One retailer receipt beat is enough** — the third listing (Sam's Club)
  read as repetitive and was cut. Then/now at one retailer carries the reveal.
- **Humor is welcome** (the dad-burp thought bubble) — one gag, placed in the
  CTA wind-down, not during evidence beats.

## Annotation discipline (rings, dots, arrows)

- **Measure on the actual pixels.** Eyeballed % coords were wrong twice.
  Crop the screenshot region with ffmpeg, read the crop, compute %.
- **Verify on the RENDERED frame**, full-res crop — the math lied once
  (ellipse stroke clipped the "1" in "51"). Founder checks on a phone;
  a stroke touching text WILL get flagged.
- **Freeze Ken Burns under precision annotations** (`zoomTo=1, pan 0`): the
  ring is static while the image drifts — they fight. Drift is for un-annotated
  beats only.
- EvidenceFrame heights must match the screenshot aspect at the inner width
  so ring %s map 1:1 (formula in `EvidenceFrame.tsx`).

## Audio engineering notes

- Peak-normalize all one-shots to −1dBFS before slotting (founder files
  varied by 21dB — ding/tap would have been inaudible).
- Trims need edge fades; `afade` is NOT in Remotion's ffmpeg build — use
  `volume='if(lt(t,..)...)':eval=frame` expressions.
- **Verify the mix numerically**: decode the final encode, windowed RMS at
  cue times vs known VO-silence gaps (from the silencedetect map). This
  caught nothing being broken — but it's how you prove the bed level and that
  cues landed without being able to listen.
- Check subprocess results: one ffmpeg encode failed silently during a
  concurrent render (npx contention) and the script reported success anyway.
  Run `npx remotion ffmpeg` from `video/` (fails from repo root).

## Remote render box specifics (Claude environment)

- `remotion.media` (Chrome download) is network-blocked → render with
  `--browser-executable=/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell`
- Google Fonts fail TLS through the proxy → add `--ignore-certificate-errors`
- ~8 min per full render (3,030 frames 1080×1920); stills ~30s
- Blocked hosts encountered: remotion.media, upload.higgsfield.ai, barchart,
  mixkit/pixabay/freesound CDNs. Founder uploads what the box can't fetch.

## New-take / new-video checklist

1. Founder exports MP4 + SRT from Captions → drop in chat
2. Transcode H.264 → `video/public/<video>/base.mp4` (gitignored; founder
   keeps the original — this box is ephemeral)
3. Silence-gap verify SRT vs export; retime drifted cues
4. Re-lock `cues.ts` + `punches.ts` + `Sfx.tsx` timestamps to the new VO
   (for a re-take of the same script: boundaries shift, structure holds)
5. Extract cover face frame (the skeptical/expressive one) → thumbnail
6. Stills pass on every annotated beat → founder review → full render
7. Multi-take stitching: founder names the assembly BY QUOTE per take; cut
   on silence boundaries; disguise seams with alternating punch-in scale
   (the agent cannot judge delivery — take selection is the founder's)
