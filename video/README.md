# FullCarts video workspace (Remotion)

Remotion compositions for social video. First comp: `FolgersReveal`
(TikTok/Reels, 1080×1920 @ 30fps) — the Folgers 51 oz → 43.5 oz coffee video.

## Workflow

1. Record + edit the talking-head video in Captions; export **MP4 + SRT**.
2. Drop media into `public/folgers/` per `public/folgers/ASSETS.md`
   (the checklist of real screenshots/recordings to capture is there too).
3. `npm install && npm run dev` → Remotion Studio. Set `baseVideo` to
   `folgers/base.mp4` in the props panel (or in `src/FolgersReveal/schema.ts`).
4. Lock the beat timings: `src/FolgersReveal/cues.ts` holds every overlay
   window in seconds — align each to the real SRT timestamps.
5. `npm run render` → `out/folgers-reveal.mp4`.

The comp renders end-to-end with zero media present (labeled drop-slots +
placeholder SRT), so layout/animation work never blocks on captures.

## Structure

- `src/FolgersReveal/Main.tsx` — assembly: base video, captions, overlays
- `src/FolgersReveal/cues.ts` — the beat map (all timing lives here)
- `src/FolgersReveal/schema.ts` — Zod props: every fact/asset is a prop, so
  the comp doubles as the reusable "Reveal" template for future products
- `src/FolgersReveal/Captions.tsx` — TikTok-style captions from the SRT,
  keyword highlighting in alert red
- `src/FolgersReveal/EvidenceFrame.tsx` — Ken Burns + highlight ring +
  visible source citation over REAL screenshots only
- `src/theme.ts` — tokens from `FULLCARTS_DESIGN_EXPORT.md`

## Policy

Per `docs/plans/2026-06-08-social-content-strategy.md`: anything carrying a
claim (charts, listings, packaging, database pages) must be a real artifact.
Remotion is the typography/assembly layer — it annotates evidence, never
generates it.
