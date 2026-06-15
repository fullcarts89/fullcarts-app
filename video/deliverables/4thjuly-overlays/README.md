# 4th of July — "Generosity Tax" rundown overlays

Five on-brand lower-third overlays for the green-screen share-size video, synced to the
`4th of July SRT`. Drop each PNG on a track ABOVE your keyed footage at its in-point.

- **Format:** transparent PNG, **1080 x 1920** (9:16) — same frame as your footage; place 1:1, no scaling.
- **Position:** pre-placed in the lower-third safe zone (clears the caption lane + the right action rail).
- **Brand tag omitted on purpose** — the product photo behind you already shows the brand (Lay's keeps its name since "Classic" alone is ambiguous).
- These are **static** stills (this environment can't run the animated Remotion render). For the
  animated slide-in `.mov`, render the committed props locally:
  `cd video && npx remotion render RundownChip out/share-<item>.mov --codec=prores --prores-profile=4444 --props=src/props/share-<item>.json`

## Timeline (machine-readable: SYNC.csv)

| # | File | In | Hold | Out | On-screen |
|---|---|---|---|---|---|
| 1 | 01_chexmix.png   | 0:10.8 | 7.0s  | 0:17.8 | Bold Party Blend · 15 → 13.5 oz · −10% |
| 2 | 02_tostitos.png  | 0:20.0 | 5.8s  | 0:25.8 | Hint of Lime · 13 → 11 oz · −15.4% |
| 3 | 03_nathans.png   | 0:27.6 | 9.9s  | 0:37.5 | Beef Franks (each) · 56 → 43 g · −23.2% |
| 4 | 04_honeymaid.png | 0:39.2 | 10.0s | 0:49.2 | Graham Crackers · 25.6 → 19.2 oz · −25% |
| 5 | 05_lays.png      | 0:50.2 | 12.4s | 1:02.6 | Lay's Classic · 235 → 145 g · −38.3% |

No overlay on the hook (0:00–0:10.8) or the take/CTA (1:02.8–1:20.1) — face only.
All figures are photo-verified from the bags you sent.
