# Folgers "Caught:" — Full Package (Model B test)

**What you're testing:** film yourself talking → drop the clip in → Remotion composites the whole
thing (Caught cold-open, burned-in captions, the data overlays, your coffee-chart cutaway, sound
effects) into one finished MP4. Engine: the `FinalVideo` composition in `video/`. Timeline:
`video/src/props/folgers-final.json`.

The 57s proof (on a placeholder background, no film yet) is already rendered — that's what verifies
the pipeline. Now you swap in real film of yourself.

---

## Step 1 — Film yourself (9:16, ~55–60s)
- **Framing:** vertical 9:16, **face upper-center** (leave the lower-middle clear — captions + the
  data card live there). Good light, talk to camera, hold the Folgers can for the proof beat.
- **Read these lines** (the captions are timed to them — say them in this order, natural pace):

```
"Caught: Folgers."
"They shrank your coffee and blamed record prices.
 Coffee's since crashed almost 40% — and your can never came back."
"And if you've caught yourself rationing scoops to stretch the can to payday —
 and felt a little pathetic about it — that's not you being cheap. That's them."
"Folgers' big can went 51 ounces to 43.5 — that's 14.7% less.
 And here's coffee's real price: record high early 2025, a 19-month low now."
"Price per pot quietly jumped while the shelf price barely moved.
 Economists call it 'rockets and feathers' — up fast, down slow, or never."
"The costs left. The shrink stayed. You got a permanent raise — for them."
"Follow — I catch the next one. Search your coffee at fullcarts.org."
```
- One take is great; or film the hook/lock-in/payoff to camera and the proof/trick as voiceover while
  you show the can. Aim for the total to land near **57s** (or note your actual length for Step 3).

## Step 2 — Drop in your assets
Put files here (create the folders):
| File | Path | Required? |
|---|---|---|
| Your film | `video/public/film/folgers.mp4` | **yes** |
| Real coffee-price screenshot | `video/public/cutaways/coffee-chart.png` | recommended (Bucket-1 proof) |
| SFX: stamp | `video/public/sfx/caught-stamp.wav` | optional |
| SFX: counter | `video/public/sfx/number-land.wav` | optional |

- **Coffee chart:** screenshot the real chart at `tradingeconomics.com/commodity/coffee` (or FRED
  `PCOFFOTMUSDM`). Read the peak (~$4.40, early 2025) and current (~$2.70) **off your screenshot** and
  make sure your spoken "almost 40%" matches it. Never an AI chart.
- **SFX (generate in ElevenLabs → text-to-SFX):**
  - `caught-stamp`: *"a single hard rubber stamp thunk on paper, sharp and authoritative, dry, no reverb, ~0.4s"*
  - `number-land`: *"a quick mechanical odometer counter roll resolving to a soft click, clean UI sound, ~0.6s"*

## Step 3 — Match the timeline to your delivery
Open `video/src/props/folgers-final.json`:
- Set **`durationSec`** to your film's actual length (seconds).
- The **captions** are `{ text, fromSec, toSec }` — nudge the times so each line matches when you say
  it. Wrap a word in `*asterisks*` to make it **red** (e.g. `*14.7%*`).
- The **overlays** are `{ type, fromSec, toSec, props }` — move the `shrink` and `source` overlay
  times to land exactly when you say "51 to 43.5" and "here's coffee's real price."
- (Captions auto-sit in the caption lane; overlays auto-sit in their safe spots — you only edit times.)

## Step 4 — Render
```bash
cd video
npx remotion render FinalVideo out/folgers.mp4 --codec=h264 --props=src/props/folgers-final.json
```
- On your own machine (with Chrome) that's it. In a sandbox without Chrome, add
  `--browser-executable=/path/to/chrome-headless-shell`.
- Want to preview without your film first? Render the placeholder version:
  `--props=src/props/folgers-final-proof.json`.

---

## How the engine maps to the package
- `FinalVideo` plays your film as the background, then layers, by timestamp: cutaways (full-frame,
  e.g. the coffee chart) → overlays (`CaughtTitle`, `ShrinkOverlay`, `SourceFrame`) → burned-in
  captions (red-highlight, in the caption lane) → SFX (`<Audio>`) → optional music.
- Everything respects the platform safe zones automatically.
- The **decisions** (which overlay/caption/SFX, and when) live in the timeline JSON — that's the
  "packet" the operator produces; Remotion just executes it deterministically.

## Notes / gotchas
- Fonts are **embedded** in the bundle (no fetch), so renders are deterministic and won't hang.
- A 57s render takes ~2–3 min single-threaded — that's normal.
- If your film isn't exactly 9:16 it's cover-fit (center-cropped); film vertical to avoid surprises.
