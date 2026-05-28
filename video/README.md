# FullCarts Video Factory

Remotion-based renderer for FullCarts short-form social content. Every
video is a React component that takes a `ShrinkEvent` record (the shape of
the planned `content_candidates` view) and renders a 9:16 video using the
exact same design tokens as the web app.

## What's in here

| Composition | Pillar (per `docs/plans/2026-05-13-social-content-engine.md`) | Length | Format |
|---|---|---|---|
| `GotchaReveal` | Gotcha Reveal (the workhorse) | 30s | 1080x1920 @ 30fps |

The Cadbury Dairy Milk Mini Eggs shrink (80g → 72g, March 2024, -10%) is
wired up as the default proof-of-concept record at
`src/data/cadbury-mini-eggs.ts`.

## Install

```bash
cd video
npm install
```

## Preview in the studio

```bash
npm run dev
```

Opens the Remotion Studio in a browser. Scrub the timeline, tweak props
live, export still frames.

## Render the video

```bash
npm run build         # → out/gotcha-reveal.mp4
npm run build:still   # → out/gotcha-reveal-poster.png (frame 180)
```

## Use a real product image

`ShrinkEvent.productImageUrl` accepts a full URL. When set, the Reveal
scene loads it via Remotion's `<Img>`; when null, a styled SVG fallback
renders so the project always builds clean. URLs typically come from
`product_entities.image_url` (Supabase storage at
`https://<project>.supabase.co/storage/v1/object/public/claim-images/...`,
per `web/src/app/products/[id]/lib.ts`).

## Render a different product

Two ways:

**1. Edit `src/data/cadbury-mini-eggs.ts`** (or add a new record alongside
it and point `Root.tsx` at it).

**2. Pass JSON props at the CLI** — production path once
`pipeline/scripts/generate_social_content.py` is wired up:

```bash
npx remotion render GotchaReveal out/oreo.mp4 --props=./events/oreo.json
```

Where `oreo.json` matches the `ShrinkEvent` shape in `src/data/types.ts`.

## Pipeline hook (next step)

The intended production loop:

```
Supabase content_candidates row
  → pipeline/scripts/generate_social_content.py
    emits  events/<slug>.json  (ShrinkEvent shape)
  → npx remotion render GotchaReveal out/<slug>.mp4 --props=events/<slug>.json
  → scheduler (Buffer / Postiz) uploads
```

This scaffold is the renderer half of that loop. The script half lives
in the `pipeline/` package and is the next thing to build.

## Why Remotion (and not JSON2Video)

- Same React, same fonts (`Space_Grotesk`, `JetBrains_Mono`), same hex
  tokens as `web/` — videos and the site look like one product.
- Animations are code, so the same `AnimatedCounter` easing as
  `CounterAnimation.tsx` on the homepage.
- Renders headless on any CI runner (no SaaS subscription per render).

JSON2Video remains a fine fallback if a no-infra render is needed
immediately. Higgsfield is for occasional AI b-roll only — not the
engine for data content.
