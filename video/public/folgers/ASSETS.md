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
| `listing-sams.png` | Sam's Club current 43.5 oz listing ($17.88) — second-retailer receipt | ⚠️ CUT from the edit (founder feedback 2026-06-11: third can shot read as repetitive). File stays in repo for reuse. |
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

## Annotation placement (MEASURED on the actual pixels, 2026-06-11 v2)

- `listing-then.png` (1155×646): ellipse at (78.5%, 15.3%) rx21 ry8.5 around
  the "(51 oz.)" line-wrap at the end of the title
- `listing-now.png` (1298×561): ellipse at (60.2%, 8.9%) rx8.5 ry7.5 on
  "43.5-Ounce" in the title
- `price-chart.png` (1913×993): peak dot at (40.0%, 10.6%) on the all-time-high
  spike; fall arrow drawn from the dot to the current-price marker at (89%, 80%)
- The original eyeballed ring coords were wrong on screen (the 51 oz ring
  pointed at dead space) — measure crops with ffmpeg before trusting %s.

## Edit revision notes (founder feedback 2026-06-11)

- Remotion caption layer REMOVED — the Captions app burns its own captions.
  `voiceover.srt` stays as the comp's duration/timing source only.
- Evidence beats are now full-screen branded cutaways (~40% of runtime off
  the talking head): database, reveal, futures chart, rockets & feathers.
- Rockets & feathers rebuilt as stroke-drawn streak/feather paths (still
  axis-free / number-free so it can't read as data).
- Cover image: `FolgersThumb` comp → `npm run thumb` → `out/folgers-thumb.png`.

## Style-board integration (contentstyleboard.html, received 2026-06-11)

- Signature components live in `src/FolgersReveal/Overlays.tsx`: CaughtTitle
  cold-open (0.4–6.0s), ShrinkOverlay (the bars+badge data card, reveal beat),
  StatCard (2,228 documented shrinks — REAL count queried from
  published_changes 2026-06-11), CiteCard + SourceHeader (chart + article
  beats), FCMini. Board phone mocks are 248px = 1080 real (×4.355).
- Safe zones per the board: keep badges/key numbers out of the right ~12%
  (like rail) and bottom ~15% (caption UI). Overlay cards inset right:140.
- Thumbnail = board cover pattern: face frame + scrim + CAUGHT/brand +
  big mono −X% + FC mark. Face frame: `cover-face.png` (extracted from
  base.mp4 @1.5s — the skeptical side-eye; local-only, gitignored).
- `article.png` — **drop slot, not yet captured**: barchart.com 19-month-low
  headline screenshot. When present (set `articleImage` prop) the hook beat
  becomes a full SourceFrame cutaway; until then the 19-MONTH LOW slam
  renders. barchart.com is blocked from the render box's network, so the
  founder screenshots it manually.
- SFX palette (CAUGHT stamp, counter roll, deflate+pop, etc.) is the
  founder's job in the Captions edit — see the board's sound table.

## Reminders

- No AI imagery anywhere in this video — account is in the fully-real phase
  per the staged rollout policy.
- The can-flip shot stays in the Captions edit (base.mp4), not a Remotion
  overlay — physical product handling reads most human uncut.
- Entity `56ed2d06` is still named just "Coffee" — if renaming via
  `/admin/entities`, note `set_entity_field` does NOT cascade to
  `published_changes` (only merge/reassign got the 071 fix); run the CLAUDE.md
  sanity query after.
