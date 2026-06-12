# FullCarts video workspace (Remotion)

Remotion compositions for social video. First comp: `FolgersReveal`
(TikTok/Reels, 1080×1920 @ 30fps) — the Folgers 51 oz → 43.5 oz coffee video.

**Read `docs/content/video-production-playbook.md` first** — pipeline,
founder taste calibration, and the expensive lessons from the first build.

## Workflow

1. Record + edit the talking-head video in Captions; export **MP4 + SRT**.
   Captions burns its own captions — this comp renders no caption layer.
2. Transcode HEVC → H.264 and drop media into `public/folgers/` per
   `public/folgers/ASSETS.md` (asset checklist + measured annotation coords).
3. **Verify the SRT against the export** (silence-gap analysis — see the
   playbook; exports drift after re-edits).
4. `npm install && npm run dev` → Remotion Studio. Set `baseVideo` to
   `folgers/base.mp4` in the props panel.
5. Beat maps: `src/FolgersReveal/cues.ts` (overlay windows), `punches.ts`
   (zoom punch-ins on the base layer), `Sfx.tsx` (sound cues + levels).
   Sound files go in `public/sfx/` named slots (`public/sfx/README.md`);
   missing slots render silent.
6. Verify with stills (`npx remotion still FolgersReveal out/check.png
   --frame=N`), then `npm run render` → `out/folgers-reveal.mp4` and
   `npm run thumb` → `out/folgers-thumb.png`.

The comp renders end-to-end with zero media present (labeled drop-slots),
so layout/animation work never blocks on captures.

### Rendering on a Claude remote box

`remotion.media` is blocked and the proxy breaks TLS for Google Fonts:

```bash
npx remotion render FolgersReveal out/folgers-reveal.mp4 \
  --props='{"baseVideo":"folgers/base.mp4","coverImage":"folgers/cover-face.png"}' \
  --browser-executable=/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell \
  --ignore-certificate-errors
```

Run `npx remotion ffmpeg` / `ffprobe` from this directory (fails from repo
root). Full render ≈ 8 min; stills ≈ 30s.

## Structure

- `src/FolgersReveal/Main.tsx` — assembly: base video (with punch-in scale),
  cutaway panels, overlays, SFX track
- `src/FolgersReveal/cues.ts` — the beat map (all overlay timing)
- `src/FolgersReveal/punches.ts` — zoom punch-in/creep map (face shots only)
- `src/FolgersReveal/Sfx.tsx` — SFX cues + levels + the drone bed curve
- `src/FolgersReveal/Overlays.tsx` — the style-board signature system:
  CaughtTitle, ShrinkOverlay, StatCard, CiteCard, SourceHeader, FCMini,
  ThoughtBubble (board: `docs/content/contentstyleboard.html`)
- `src/FolgersReveal/Cutaway.tsx` — full-screen branded panel (logo + kicker
  + 48px grid)
- `src/FolgersReveal/EvidenceFrame.tsx` — Ken Burns + highlight ellipse +
  source citation over REAL screenshots only
- `src/FolgersReveal/ChartAnnotation.tsx` — peak dot + fall arrow
- `src/FolgersReveal/Thumbnail.tsx` — cover still (`npm run thumb`)
- `src/FolgersReveal/schema.ts` — Zod props: every fact/asset is a prop, so
  the comp doubles as the reusable "Reveal" template
- `src/theme.ts` — tokens from `FULLCARTS_DESIGN_EXPORT.md`

## Policy

Per `docs/plans/2026-06-08-social-content-strategy.md`: anything carrying a
claim (charts, listings, packaging, database pages) must be a real artifact.
Remotion is the typography/assembly layer — it annotates evidence, never
generates it. Numbers shown (e.g. the StatCard count) are queried live from
the database at build time, never invented. AI-generated imagery and audio
are both out — the founder sources real library SFX.
