# Production Packet — "General Mills: Too Dumb to Notice"

**Series:** Caught: · **Hero:** Cinnamon Toast Crunch **12 oz → 10 oz (−16.7%)** · **Length:** ~30s · **Update day:** Wednesday
**Deliverables:** 5 green-screen-ready background clips (1080×1920, 30fps, H.264). **No captions, no SFX baked in** — add those last in CapCut.

---

## ✅ Fact-check (all verified against the live DB this batch — 2026-06-17)

| Claim | Live DB | Status |
|---|---|---|
| Cinnamon Toast Crunch 12 → 10 oz (−16.7%) | exact non-retracted row exists | ✅ + matches your photo |
| "documented over 23 others" | **28 General Mills shrink events** (27 others) | ✅ conservatively true |
| Database scale | **2,323** non-retracted events | ✅ → say **"2,300+"** |

**Corrected from the storyboard:** "I logged **4,200** labels" → render/say **"2,300+"**. 4,200 is not traceable (real = 2,323) and "3,000+" is on the forbidden-claims list; an inflated number is the one thing that can sink the authority position. Everything else in the storyboard checks out on the 12 oz hero.

---

## The 5 beats (composite your green-screen face over each background)

| # | Beat | Time | Background clip | What it shows |
|---|---|---|---|---|
| 1 | HOOK | 0–3s | `GMHook.mp4` | Push into the **real net-weight corner**, animated red ring around **"12 OZ"**. ("They hide it in the corner.") |
| 2 | PROOF | 3–10s | `GMProof.mp4` | **Both real boxes, same shelf** (your photo) + **−16.7%** badge + `12 oz → 10 oz · same price` strip. |
| 3 | TACTIC | 10–18s | `GMTactic.mp4` | Full close-up of the net weight with a **zoom-pulse** ("they count on this"). Drop your finger-tap on top. |
| 4 | AUTHORITY | 18–25s | `fullcarts-web.mp4` | Your **real fullcarts.org screen-recording** scrolling — proof behind the talking head. |
| 5 | CTA | 25–30s | `GMcta.mp4` | End card: *Check your pantry / Then check mine* · **@full_carts_** · **comment LABELS** · fullcarts.org · 2,300+. |

All evidence sits in the **upper 2/3**; the lower third is intentionally clear for your head + the captions you add.

---

## CapCut assembly notes
1. Drop each background on the base track in beat order; align cut points to your VO using the SRT.
2. Layer your green-screen face on top (chroma key) for HOOK / TACTIC / AUTHORITY; PROOF + CTA can run full-frame or with your face.
3. Add your **captions** (the storyboard's on-screen TEXT cues) and **SFX** (record scratch, thud, tap/heartbeat, typing, shutter) — left out per your request.
4. CTA keyword is **LABELS** (matches your recorded VO; note it differs from the house "CAUGHT" keyword — fine as a one-off).

## Source assets
- `video/public/ctc_evidence.jpg` — your shelf photo (both boxes)
- `video/public/ctc_corner.jpg` — cropped net-weight strip
- `video/public/clips/fullcarts-web.mp4` — your website recording, verticalized
- Comps: `GMHook`, `GMProof`, `GMTactic`, `GMcta` in `video/src/Root.tsx`; new `NetWeightZoom` component.
