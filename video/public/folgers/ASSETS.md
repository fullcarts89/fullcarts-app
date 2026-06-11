# Folgers Reveal — asset manifest

Everything in the **proof layer must be a REAL artifact** — see the
AI-vs-evidence policy in `docs/plans/2026-06-08-social-content-strategy.md`.
Remotion only frames, pans, and annotates; it never fabricates evidence.

## Status (2026-06-11)

| File | What | Status |
|---|---|---|
| `voiceover.srt` | Real Captions SRT (6 paragraph-level cues — paginated to 6-word pages at runtime) | ✅ in repo (two text fixes: `fullcart.org`→`fullcarts.org`, dropped one "Um,"; cue-6 end retimed 99.22→97.66 to match the final export — see below) |
| `listing-then.png` | Walmart **delisted** "OFFLINE-Folgers Classic Roast (51 oz.)" listing | ✅ in repo |
| `listing-now.png` | Walmart current 43.5-Ounce listing ($25.89) | ✅ in repo |
| `listing-sams.png` | Sam's Club current 43.5 oz listing ($17.88) — second-retailer receipt | ✅ in repo |
| `price-chart.png` | Real coffee futures 12-month chart (2025 peak ~440 → 251 now) | ✅ in repo |
| `fullcarts-overview.mov` | fullcarts.org homepage screen recording (H.264) | ✅ in repo |
| `folgers-page.mov` | fullcarts.org Folgers page screen recording (H.264) | ✅ in repo |
| `base.mp4` | Captions talking-head export (Captions_A80B95, 720×1280 HEVC @30fps, **1:37.70**). Carries the audio. Drop it here locally and set the `baseVideo` prop to `folgers/base.mp4`. Gitignored (too heavy). The final export runs 1.5s shorter than the original SRT (the "Um," cut + tail trim compressed cue 6); silence-gap analysis confirmed cues 1–5 align within ±0.25s, so only the SRT's cue-6 end time was retimed. | ✅ delivered (keep a local copy — gitignored) |

## Verified facts (as of 2026-06-11 — captured same day)

- **51 oz → 43.5 oz = −14.7%** ("almost fifteen percent" ✓). DB event:
  entity `56ed2d06-7cd3-43c4-99f6-9cc7d8fca24d` (Folgers / Coffee),
  evidence_count 31, active.
- **19-month low ✓** — arabica hit a 19-month nearest-futures low this week
  (July '26 ~245.9 ¢/lb; Brazil bumper-crop forecasts, USDA FAS record
  71.9M bags). Article: barchart.com/story/news/2310618 ("Coffee Prices Sink
  on Expectations of a Record Brazil Coffee Crop").
- **"Fallen almost forty percent" ✓ (conservative)** — chart shows ~440 peak
  → 251.10 now ≈ −43%. Understating is fine; overstating is not.

## Known wrinkle: visible listing prices

`listing-then.png` shows **$11.24** (stale price on the delisted 51 oz item)
vs **$25.89** (Walmart now) / **$17.88** (Sam's Club now). The script says
the shelf price "barely moved" — if the old price is legible, viewers may
read "$11 → $26?!" and miss the point. The owner kept the screenshot as-is
(re-sent after this was flagged); mitigation if it tests badly: keep the Ken
Burns crop tight on the size text. The highlight rings already target the
sizes, not the prices.

## Ring placement (eyeball in Studio, scrubbing the cue)

- `listing-then.png`: ring at (46%, 10%) on "(51 oz.)" in the title
- `listing-now.png`: ring at (36%, 8%) on "43.5-Ounce"
- `listing-sams.png`: ring at (88%, 31%) on "43.5 oz." in the title
- `price-chart.png`: ring at (93%, 84%) on the current-price marker

## Reminders

- No AI imagery anywhere in this video — account is in the fully-real phase
  per the staged rollout policy.
- The can-flip shot stays in the Captions edit (base.mp4), not a Remotion
  overlay — physical product handling reads most human uncut.
- Entity `56ed2d06` is still named just "Coffee" — if renaming via
  `/admin/entities`, note `set_entity_field` does NOT cascade to
  `published_changes` (only merge/reassign got the 071 fix); run the CLAUDE.md
  sanity query after.
