# FullCarts Content Visual Identity (Signature Style)

**Date:** June 11, 2026
**Canonical web system:** `FULLCARTS_DESIGN_EXPORT.md` (source of truth for tokens).
**Applied in code:** the `video/` Remotion toolkit (`src/lib/theme.ts`, `fonts.ts`).
**Purpose:** the signature look for *content* (video, captions, thumbnails) so every post reads as
unmistakably yours. This is the "editing/graphics" half of the signature-visual-style lever (the
on-camera **set/look/framing** is a separate to-do).

---

## The 4 signature signals (protect these — they ARE the brand)
1. **Monospace numbers.** Every number/%/size/date in **JetBrains Mono**. Data = mono = "receipts."
2. **Alert-red on graphite, cream text.** `#dc2626` accent on `#0a0b0d`, text `#f5f4f0`.
3. **The count-up.** Key stats tick up (StatCard) — the data reveal beat.
4. **The before→after bar.** The two-bar shrink visual (ShrinkOverlay).

Keep these constant and the feed reads as one body of work.

## Typography
| Font | Use |
|---|---|
| **Space Grotesk** 700 | headlines, the wordmark, `CAUGHT:` / brand names |
| **Inter** 400–600 | body / supporting copy |
| **JetBrains Mono** 500/700 | all numbers, %, sizes, dates, labels (uppercase + letter-spacing for labels) |

## Color (meaning-coded)
- Base: graphite `#0a0b0d` · card `#161719` · text cream `#f5f4f0` · secondary `#a0a0a5`
- **Alert red `#dc2626`** = the cut / shrinkflation (primary accent)
- **Signal green `#10b981`** = restoration / verified / good news
- Data blue `#3b82f6` (neutral) · amber `#f59e0b` (warning). Red = bad, green = good — always.

## Captions (burned-in, the most-seen element) — RED HIGHLIGHT
- **Space Grotesk bold, cream `#f5f4f0`, heavy black outline** (legible over any footage).
- **Highlight the key word/number in alert red `#dc2626`.**
- Max **2 lines**, ~3–5 words/line, **lower-center**, timed exactly to speech.
- No more than one highlight per line. In Captions App: set this as the saved template.

## Iconography
`lucide-react` line icons (TrendingDown, AlertCircle, Package, Database, Shield…) in rounded
red-tinted containers. Functional line icons — the default visual vocabulary.

## Illustration (allowed — with a hard boundary)
Light illustration is OK for **metaphor / atmosphere / explainer** moments. Style: **flat,
monoline/geometric, brand palette** (cream + alert-red on graphite) — matches the lucide line look,
never cartoonish or stocky.

> **HARD BOUNDARY (the three-bucket policy — non-negotiable):** illustration is **Bucket 2** only.
> **Never illustrate a specific product, package, logo, chart, graph, or number** — those must stay a
> **real photo or screenshot**. An illustrated metaphor is fine; an illustrated "data chart" or fake
> package is the exact thing that got videos flagged. The one-question test still rules: *could a
> viewer mistake this for evidence?* If yes → real, not illustrated. Label AI-made visuals.
> Source illustration via Higgsfield (labeled) or an illustrator; the `video/` toolkit doesn't make it.

## Texture & motion
- **Data-grid texture** (`GridTexture`, ~6–8% opacity) behind title cards / thumbnails / stat cards.
- **Motion:** spring entrances, count-up on numbers, bar-grow on the before→after. Restrained — the
  data is the star, not the animation.

## Signature components (the `video/` toolkit)
| Element | Composition | Render |
|---|---|---|
| Series cold-open `CAUGHT: [BRAND]` | **`CaughtTitle`** | alpha .mov (overlay the face hook) |
| Before→after lower-third | `ShrinkOverlay` | alpha .mov |
| Full-frame big number / count-up | `StatCard` | mp4 |
| Ranked rundown chip | `RundownChip` | alpha .mov |
| Citation bar on a REAL screenshot | `SourceFrame` | alpha .mov |
| Cover/thumbnail overlay | **`Thumbnail`** | **still PNG** (drop over a face frame) |
| FC wordmark | `Brandmark` | (in every comp) |

## Thumbnail / cover
Consistent across the profile so the grid reads as a series: **your face** (cover frame) + the
`Thumbnail` overlay → `CAUGHT: [brand]` top, a huge mono **`−X%`** in alert red, grid texture, brandmark.
Render: `npx remotion still Thumbnail out/thumb.png --frame=15 --props=src/props/thumb-folgers.json`.

## Emoji / stickers
Restrained. A single 🛒 / ☕ in CTAs is fine; no sticker spam — it undercuts the credible, documentary tone.
