# @fullcarts/video — Remotion overlay toolkit

Branded, data-driven overlays for FullCarts face-forward content. These are the **visual
moat**: on-brand graphics that pin real numbers to your footage, rendered from data so a new
overlay is a one-line props change — not a hand-built CapCut graphic.

Part of the content system: strategy in `docs/plans/2026-06-10-face-forward-content-strategy.md`,
rules in `docs/content/content-rules.md`, workflow in `docs/content/production-playbook.md`.

## Setup

```bash
cd video
pnpm install        # or npm install
pnpm studio         # opens Remotion Studio to preview/tweak every composition
```

Fonts (Space Grotesk, Inter, JetBrains Mono) load automatically via `@remotion/google-fonts`.
Tokens live in `src/lib/theme.ts` (graphite `#0a0b0d`, alert red `#dc2626`, signal green `#10b981`).

## The four compositions (mapped to content formats)

| Composition | Content format it serves | Background | Render as |
|---|---|---|---|
| **ShrinkOverlay** | Reveal / Gotcha (single before→after); `mode:"restoration"` = green good-news | transparent | **alpha** overlay |
| **StatCard** | By-the-Numbers hook, the DB counter (count-up), CPI newsjack headline | opaque graphite | mp4 |
| **RundownChip** | "5 things that shrank" — one chip per item | transparent | **alpha** overlay |
| **SourceFrame** | citation bar to lay **on top of a REAL screenshot** (BLS/FRED/FullCarts page) | transparent | **alpha** overlay |

> **Evidence-policy guardrail:** `SourceFrame` labels real evidence; the toolkit never generates
> a fake chart or fake packaging (three-bucket policy in `content-rules.md`). Keep it that way.

## Rendering

Each composition is data-driven — pass a JSON props file from `src/props/` (or your own):

```bash
# Alpha overlays → ProRes 4444 .mov (true transparency) for Captions App / CapCut
npx remotion render ShrinkOverlay out/gatorade.mov \
  --codec=prores --prores-profile=4444 --props=src/props/gatorade.json

npx remotion render RundownChip out/rundown-1.mov \
  --codec=prores --prores-profile=4444 --props=src/props/rundown-1.json

npx remotion render SourceFrame out/bls.mov \
  --codec=prores --prores-profile=4444 --props=src/props/bls-cpi.json

# Full-frame card → standard mp4
npx remotion render StatCard out/db-counter.mp4 \
  --codec=h264 --props=src/props/db-counter.json
```

Drop the `.mov` overlays onto a track above your footage in Captions App — the transparent
areas show your video through; the `.mp4` card is a full-screen beat.

## Adding a new event

1. Copy a file in `src/props/`, change the numbers (use exact figures, pulled from the DB —
   see `docs/content/approved-claims.md`).
2. Render with the matching composition id.
3. That's it — no code edits. The `fullcarts-content` skill automates this step each week.
