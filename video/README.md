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
| **CaughtTitle** | the "Caught:" series cold-open (`CAUGHT: [BRAND]`) — overlay the face hook | transparent | **alpha** overlay |
| **Thumbnail** | cover overlay (CAUGHT + brand + big mono −X%) — drop over a face cover frame | transparent | **still PNG** |

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

# Series cold-open (alpha overlay)
npx remotion render CaughtTitle out/caught-folgers.mov \
  --codec=prores --prores-profile=4444 --props=src/props/caught-folgers.json

# Thumbnail/cover → still PNG (drop over a face cover frame)
npx remotion still Thumbnail out/thumb-folgers.png \
  --frame=15 --props=src/props/thumb-folgers.json
```

Visual identity (fonts, color, the red-highlight caption spec, illustration boundary) lives in
`docs/content/visual-identity.md`.

Drop the `.mov` overlays onto a track above your footage in Captions App — the transparent
areas show your video through; the `.mp4` card is a full-screen beat.

## Adding a new event

1. Copy a file in `src/props/`, change the numbers (use exact figures, pulled from the DB —
   see `docs/content/approved-claims.md`).
2. Render with the matching composition id.
3. That's it — no code edits. The `fullcarts-content` skill automates this step each week.

## Assembled cut (`FinalVideo`) — face-forward house recipe

For a full piece, render the **whole edit in one pass** (film + animated cutaways + outro), not just
overlays. Engine: the `FinalVideo` composition + a timeline JSON (`src/props/<brand>-final.json`).

- **Sequence:** face + one hook line ("'X' is a lie") → back-to-back **full-frame animated evidence
  cutaways**, one per product, *no face between them* → face take → `OutroCard` follow-close.
- **Cutaways = `ShrinkCutaway`:** real product photo(s) (1–2; two = before/after) + before→after numbers
  + −%. **Always the real photos — a number graphic alone isn't trustworthy.** For paired photos the
  creator says which is *before*.
- **Layout law:** evidence fills the **top 2/3**; the **bottom 1/3 stays clean** for the creator's
  talking head + captions (they overlay both in their app).
- Overlay cues sync to the SRT word timings (evidence appears only when the product is named).

### Rendering in the cloud sandbox

Remotion *does* run in the cloud sandbox — point it at the pre-installed headless-shell binary (the plain
chrome binary fails: "old headless removed"):

```bash
npx remotion render FinalVideo out/<brand>-final.mp4 \
  --browser-executable=/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell \
  --props=src/props/<brand>-final.json --crf 23
```

ffmpeg (frame grabs, compression) is available via `pip install imageio-ffmpeg`
(`imageio_ffmpeg.get_ffmpeg_exe()`). So the operator can deliver the **finished MP4 in-session**, not
just overlays.
