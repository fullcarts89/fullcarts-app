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
Most people watch on mute, so captions are the primary read.
- **Space Grotesk bold, cream `#f5f4f0`, heavy black outline** (legible over any footage).
- **Highlight the key word/number in alert red `#dc2626`** (word-by-word/karaoke highlight aids mute comprehension).
- Max **2 lines**, ~3–5 words/line, timed exactly to speech. No more than one highlight per line.
- **Placement — the caption lane:** **centered**, in the band **y ≈ 780–1010** (≈ 40–53% down),
  `maxWidth ≈ 720` (clears the right rail). This sits **below the face, above the lower-third data
  overlays and the platform UI** — the eyes-rest zone for sound-off, with no collisions. Keep it a
  **fixed lane every video** (don't let captions jump around). In Captions App: set this as the saved
  style + position. (Lane defined in `video/src/lib/safezone.ts` as `CAPTION`; preview it with `SafeZonePreview`.)

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

## Safe zones (overlays never bleed off-frame)
Overlays sit **fully inside** the frame — they don't run off-edge or fly in from outside. The apps
cover parts of the screen with their own UI, so critical content (the **−X%**, numbers, brand,
burned-in captions) stays inside the safe rectangle. Values are the **union** of all three platforms
(1080×1920), encoded in `video/src/lib/safezone.ts`:

| Inset | px | What's there |
|---|---|---|
| **Top** | 240 | platform tabs / search (Reels & Shorts top chrome) |
| **Bottom** | 450 | caption + @handle + music ticker + nav (TikTok deepest) |
| **Right** | 170 | like / comment / share / save action rail (Reels widest) |
| **Left** | 60 | device / caption margin |

→ **Safe area = x: 60 → 910, y: 240 → 1470.** Lower-thirds sit with their bottom on y=1470 (above the
caption); the title card sits at y=240; centered content (StatCard) keeps `maxWidth ≤ 740` so it
clears the rail on the right. All toolkit comps are positioned to this; verify new ones with the
`SafeZonePreview` composition (renders the overlay over a mock of the TikTok/Reels/Shorts UI).

## Texture & motion
- **Data-grid texture** (`GridTexture`, ~6–8% opacity) behind title cards / thumbnails / stat cards.
- **Motion — smooth, never jittery.** Every element eases in on a **high-damping spring** (gentle
  ease-out, *no bounce, no snap*): cards rise + fade, numbers/badges scale-pop, the before→after bar
  and the "Caught" bar wipe, source bars drop. Entrances ~0.4–0.6s, **staggered** ~0.1–0.3s so beats
  land in sequence (card → number → badge), not all at once. Count-ups are eased (fast then settle).
  Restrained — the data is the star, the motion just guides the eye. The live feel is previewed in the
  style board (it animates); the real output uses the `video/` toolkit's shared spring (`lib/anim.ts`).

## Signature components (the `video/` toolkit)
| Element | Composition | Render |
|---|---|---|
| Series cold-open `CAUGHT: [BRAND]` | **`CaughtTitle`** | alpha .mov (overlay the face hook) |
| Before→after lower-third | `ShrinkOverlay` | alpha .mov |
| Full-frame big number / count-up | `StatCard` | mp4 |
| Ranked rundown chip | `RundownChip` | alpha .mov |
| Citation bar on a REAL screenshot | `SourceFrame` | alpha .mov |
| Cover/thumbnail overlay | **`Thumbnail`** | **still PNG** (drop over a face frame) |
| Before→after evidence card (cropped cans + size/price) | **`BeforeAfter`** | still PNG (proof cutaway) |
| "Watch it shrink" — product scales down + ghost outline + ticking number | **`ShrinkReveal`** | full-frame cutaway |
| Kinetic typography for punch lines (red-highlight) | **`KineticQuote`** | full-frame cutaway |
| FC wordmark | `Brandmark` | (in every comp) |

## Shot density — cut away often, face is the anchor
The screen should be **mostly branded motion + evidence**, with your face as the *anchor* (the open,
the lock-in/emotional beat, the CTA) — not the default shot. Target roughly **~35% face / ~65%
visuals**. Map **every script beat to something on screen** (a reveal, a stat count-up, a kinetic
line, the chart, the before/after) so the viewer never just squints at a static talking head. New
visual types get built as reusable Remotion comps and added to the table above.

## Thumbnail / cover
Consistent across the profile so the grid reads as a series: **your face** (cover frame) + the
`Thumbnail` overlay → `CAUGHT: [brand]` top, a huge mono **`−X%`** in alert red, grid texture, brandmark.
Render: `npx remotion still Thumbnail out/thumb.png --frame=15 --props=src/props/thumb-folgers.json`.

## Emoji / stickers
Restrained. A single 🛒 / ☕ in CTAs is fine; no sticker spam — it undercuts the credible, documentary tone.

## Sound design (the sonic identity)
**"A calm data terminal that occasionally slams down a receipt."** Restrained, mechanical/digital,
evidence-flavored. The punch comes from **two accents** (the CAUGHT stamp + the number land), not
constant SFX. This protects the credible/documentary tone — the opposite of bubbly meme audio.

| Moment | Sound | Why |
|---|---|---|
| **"Caught:" cold-open** | one hard **stamp / shutter-thunk** as CAUGHT lands | the **sonic logo** — "caught red-handed." Most recognizable cue; keep it identical every episode |
| **Number reveal / count-up** | fast **odometer/counter roll** → soft **ding/thunk** on stop | the data reveal; mono numbers made audible |
| **Before→after bar shrinks** | short **descending "deflate"** + a tight **pop** on the −X% badge | you *hear* the product get smaller |
| **Data / typing beats** | subtle **mechanical-keyboard typing** under "I do data for a living" | reinforces the data brand; diegetic, not cartoon |
| **Proof / "documented, sourced"** | **receipt-print** or stamp tick | the receipts brand, audible |
| **Cut / transition** | clean low **whoosh**, sparse (not every cut) | movement without noise |
| **CTA** | soft positive **UI tap / ding** | gentle close, not salesy |
| **Underbed** | low, tense, minimal **drone/beat**, ducked −18 dB under VO | authority; the voice stays the star |

**Avoid:** glitter/sparkle, riser "vine-booms," meme SFX, busy stingers.
**Source:** generate the signature ones (CAUGHT stamp, counter) in **ElevenLabs SFX** (text-to-SFX);
use Captions App's library for the rest. Keep SFX ~−12 to −18 dB under the voice.

## Visual reference
`web/public/mockups/content-style-board.html` — open in a browser to see every element above
rendered in-brand (color, type, all overlays in 9:16 context, captions, the sound table).

