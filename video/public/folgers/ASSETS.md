# Folgers Reveal — asset manifest & capture checklist

Drop files into this directory with these exact names, then set the matching
prop (Remotion Studio right panel, or edit `src/FolgersReveal/schema.ts`
defaults). Everything in the **proof layer must be a REAL artifact** — see the
AI-vs-evidence policy in `docs/plans/2026-06-08-social-content-strategy.md`.
Remotion only frames, pans, and annotates; it never fabricates evidence.

## Verified facts (as of 2026-06-11 — re-verify on capture day)

- **51 oz → 43.5 oz = −14.7%** ("almost fifteen percent" ✓). DB event:
  entity `56ed2d06-7cd3-43c4-99f6-9cc7d8fca24d` (Folgers / Coffee),
  evidence_count 31, active.
- **19-month low ✓** — arabica hit a 19-month nearest-futures low this week
  (July '26 contract ~245.9 ¢/lb; Brazil bumper-crop forecasts, USDA FAS
  record 71.9M bags). Sources: Barchart / Trading Economics, June 9–10 2026.
- **"Fallen almost forty percent" ✓ (conservative)** — vs the Feb 2025 peak
  (~430–440 ¢/lb) the fall is ~43%. Understating is fine; overstating is not.

## Captures needed (in priority order)

| File | What | How |
|---|---|---|
| `base.mp4` + `voiceover.srt` | Talking-head + SRT | Export from Captions. Overwrite the placeholder SRT. |
| `listing-now.png` | Current 43.5 oz listing | walmart.com → search "Folgers Classic Roast 43.5 oz" → full product page screenshot with the size + price visible. |
| `listing-then.png` | Archived 51 oz listing | web.archive.org → paste the same Walmart listing URL → pick a 2022–2023 snapshot showing 51 oz. Keep the Wayback toolbar in frame (it IS the credibility). Also archive it into the DB: `python -m pipeline wayback --url <listing-url> --brand Folgers --product "Classic Roast"` (no Folgers wayback rows exist yet). |
| `price-chart.png` | Real coffee futures chart | tradingeconomics.com/commodity/coffee → 5Y view so the Feb-2025 peak AND the current 19-month low are both in frame. Screenshot, don't recreate. |
| `db-recording.mp4` | fullcarts.org proof | Screen-record `fullcarts.org/products/56ed2d06-7cd3-43c4-99f6-9cc7d8fca24d` — slow scroll from hero through the evidence trail. ⚠️ That entity's name is literally "Coffee" — consider renaming via `/admin/entities` click-to-edit first. **Caveat:** `set_entity_field` does NOT cascade to `published_changes` (only merge/reassign paths got the 071 fix), so after renaming run the sanity check from CLAUDE.md / re-sync, or keep the rename for after capture. |
| (optional) `headline.png` | News headline on the price drop | e.g. the Barchart "arabica falls to 19-month low" story. |

## Highlight-ring placement

`listing-then.png` / `listing-now.png` get a red ring at (50%, 42%) by
default — move it onto the actual size text per screenshot via the `ring`
prop in `Main.tsx` once the captures exist.

## Reminders

- Crop personal info (account name, cart) out of retailer screenshots.
- No AI imagery anywhere in this video — account is in the fully-real phase
  per the staged rollout policy.
- The can-flip shot stays in the Captions edit (base.mp4), not a Remotion
  overlay — physical product handling reads most human uncut.
