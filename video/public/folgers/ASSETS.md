# Folgers Reveal — asset manifest

Everything in the **proof layer must be a REAL artifact** — see the
AI-vs-evidence policy in `docs/plans/2026-06-08-social-content-strategy.md`.
Remotion only frames, pans, and annotates; it never fabricates evidence.

## Status (2026-06-11)

| File | What | Status |
|---|---|---|
| `voiceover.srt` | Real Captions SRT (1:39.2, 6 paragraph-level cues — paginated to 6-word pages at runtime) | ✅ in repo (two text fixes: `fullcart.org`→`fullcarts.org`, dropped one "Um,") |
| `listing-then.png` | Walmart **delisted** "OFFLINE-Folgers Classic Roast (51 oz.)" listing | ✅ in repo |
| `listing-now.png` | Walmart current 43.5-Ounce listing | ✅ in repo |
| `price-chart.png` | Real coffee futures 12-month chart (2025 peak ~440 → 251 now) | ✅ in repo |
| `fullcarts-overview.mov` | fullcarts.org homepage screen recording (H.264) | ✅ in repo |
| `folgers-page.mov` | fullcarts.org Folgers page screen recording (H.264) | ✅ in repo |
| `base.mp4` | **Captions talking-head export — the only missing piece.** Carries the audio. Drop it here locally and set the `baseVideo` prop to `folgers/base.mp4`. Gitignored (too heavy). | ⬜ local-only |

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

## Known wrinkle: the two listing prices

`listing-then.png` shows **$11.24** (stale price on the delisted 51 oz item)
and `listing-now.png` shows **$25.89**. The script says the shelf price
"barely moved" — if both prices are legible in the same video, viewers may
read "$11 → $26?!" and miss the point. Mitigations (pick in Studio): keep the
Ken Burns crop tight on the size text, or crop the old price out of
`listing-then.png`. The highlight rings already target the sizes, not the
prices.

## Ring placement (eyeball in Studio, scrubbing the cue)

- `listing-then.png`: ring at (46%, 10%) on "(51 oz.)" in the title
- `listing-now.png`: ring at (36%, 8%) on "43.5-Ounce"
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
