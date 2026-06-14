# FullCarts Music Beds & Copyright Rules

**Date:** June 14, 2026
**Parent:** `docs/content/posting-schedule.md` (this assigns a music lane to every slot in its weekly
schedule + carousel series) · `docs/content/visual-identity.md` §"Sound design" (this extends the
sonic identity to *licensed beds*).
**Purpose:** a copyright-clean, six-lane **soundboard** so every weekly slot has a pre-cleared music bed
mapped to its emotional arc — and a single source of truth for **how to use music without takedowns,
mutes, or lost monetization** on a *brand* account that cross-posts one cut everywhere.

> **Why this matters for FullCarts specifically:** FullCarts is a **brand**, and the whole model
> (`posting-schedule.md`) is *render once → cross-post TikTok + Reels + Shorts + X*. Per-platform
> trending-sound licenses don't survive a cross-post, business accounts get a restricted catalog, and
> ads/monetization strip popular music. So our **default bed is royalty-free that we license once** and
> can legally reuse on every platform, in ads, and monetized. Trending sounds are a *discovery add-on*,
> applied natively per platform — never the thing we depend on.

---

## The copyright rules (read once, internalize)

1. **The in-app library is a per-platform license — it does NOT travel.** A song added from inside
   TikTok / Reels / Shorts' native music picker is only licensed *on that platform*. Export the video and
   re-upload it elsewhere and the license is gone → mute / takedown / strike. This is the #1 way brand
   accounts get burned, and it directly conflicts with our render-once-cross-post model.
2. **Brand/business accounts get a smaller "Commercial Music Library."** TikTok and Instagram restrict
   *business* accounts to cleared tracks; many trending songs show "not available for business use."
3. **Monetization + paid ads = no popular music.** Boosting a post or relying on Shorts/Reels payouts with
   a commercial track → revenue gets claimed by the rights holder (YouTube Content ID is automatic).
4. **X (Twitter) has no music licensing deals at all.** No in-app shield → popular music just gets muted
   or removed. On X, **royalty-free only.**
5. **There is no "under X seconds is fair use" rule.** A myth. Clip length grants no license.
6. **Keep the license receipt.** Screenshot/download the license confirmation for every royalty-free track
   (catalogs rotate; this is your proof if a false Content-ID claim lands — dispute with the receipt).

**The rule of thumb:** if a sound isn't (a) royalty-free and licensed to us, or (b) added natively from
*that platform's* in-app library for *that platform's* copy, it does not ship.

---

## The six lanes (royalty-free soundboard)

Pick from libraries we hold a license to. **Free:** Uppbeat, YouTube Audio Library. **Paid (recommended
for a brand that cross-posts + may run ads):** Epidemic Sound, Artlist, Soundstripe. Track titles rotate —
treat named picks as starting points, **verify the track is live + license covers social/ads, save the
receipt.** Save **2 favorites per lane** = the weekly grab-and-go set (no re-searching).

| # | Lane | Vibe / BPM | Beat lands on… | Royalty-free picks + search terms | Trending-sound equivalents* |
|---|---|---|---|---|---|
| 1 | **Educational** | confident driving trap, 90–110 | the −X% size-drop overlay | Uppbeat: *Aaron Paris – Pull Up*, *Mountaineer – Pushin* · Epidemic: mood *Driving + Hopeful*, genre *Hip Hop* · Artlist: "documentary trap", "stats beat" | Not Like Us · Money So Big · Like That · 20 Min |
| 2 | **Upbeat / positive** | bright indie-pop claps, 110–125 | "they brought it back" | Uppbeat: *Mood Maze – Sunshine*, *Pryces – Good Times* · Epidemic: mood *Happy + Quirky*, *Indie Pop* · Artlist: "feel good indie" | 1901 · Memory Reboot · Thank You · Million Dollar Baby |
| 3 | **Emotional storytelling** | moody synth/lo-fi build→drop, 80–100 | the reveal after the setup | Uppbeat: *Pryces – Nightfall*, *Ben Beiny – Reflections* · Epidemic: mood *Mysterious + Dark*, *Synthwave* · Artlist: "emotional build up" | Hotline Bling · Dark Red · Walking on a Dream · Runaway |
| 4 | **Sadder** | sparse piano / slowed+reverb, 60–80 | let it breathe under before/after | Uppbeat: search "sad piano", "solitude" · Epidemic: mood *Sad / Sentimental*, *Piano* + "slowed+reverb" tag · Artlist: "emotional piano", "nostalgic acoustic" | Another Love · Home · Je Te Laisserai des Mots · New Home (Slowed) |
| 5 | **Day in the life** | chill lo-fi / bedroom pop, 85–105 | (no drop — sits under VO) | Uppbeat: *Mooncalf – Lo-Fi*, *Ramol – Easy* · Epidemic: mood *Laid Back + Happy*, *Lo-Fi* · Artlist: "lofi vlog", "bedroom pop" | I Wanna Be Yours · Surround Sound · Paper Planes · Space Cadet |
| 6 | **Newsjack / urgent** | tense, ticking, broadcast, 100–120 | the headline stat | Uppbeat: search "breaking news", "tension", "ticking clock" · Epidemic: mood *Tense + Serious*, *Cinematic* · Artlist: "news urgent", "investigation" | (use royalty-free — broadcast tension rarely matches a trending pop song) |

\* **Trending-sound equivalents** are the popular songs that *match each mood* (from the reference reels) —
use them **only** as the native in-app sound on the per-platform discovery cut (see Hybrid play), never in
the cross-posted master or on X.

> **Reconcile with the "calm data terminal" sonic identity (`visual-identity.md`).** The talking-head
> *Caught:* hero (Wed) and any authority piece stay on **original audio + the signature SFX** (CAUGHT
> stamp, odometer count-up, deflate) with at most a **low, tense underbed ducked −18 dB** — lanes 1/6 are
> the only beds that fit, mixed *under*, never a pop hook over the VO. The mood lanes (2–5) are for the
> **carousels, vlog, and entertainment cuts** where a bed carries the piece, not the voice.

---

## Lane → slot map (wires into `posting-schedule.md` + `series.md`)

### Weekly video slots
| Day | Format | Lane | Notes |
|---|---|---|---|
| **Mon** | *Shrink Check* — ≤25s, rotates 4 treatments | **1 Educational** (default) / **3** for the gut-punch treatment | driving beat; the drop hits the −X% overlay. *Same Price, Less Stuff* / *Then vs Now* lean lane 3 |
| **Wed** | *Caught:* hero | **original audio + SFX** (low **1/6** underbed −18 dB) | the voice is the star — see sonic-identity note above |
| **Thu** | *The Take* — opinion/commentary (CPI read on print weeks) | **6 Newsjack** | broadcast tension under the take/headline stat |
| **Fri** | *Receipt of the Week* (newest entry; evidence-tag review fallback) | **6 Newsjack** | same urgent bed |
| **Sun** | *Why I Built This* vlog | **5 Day in the life** | chill lo-fi under the talk-to-camera persona |

### Carousel series (the `CarouselVideo` `music` prop / `<Audio loop>` bed)
| Series (`posting-schedule.md`) | Lane |
|---|---|
| 1 — Monthly Shrink List (5 Stealth Shrinks) | **1 Educational** |
| 2 — Shrinkflation Tier List | **1 Educational** (villain energy) or **6** for a "worst revealed last" build |
| 3 — Official Inflation vs. Reality (CPI) | **6 Newsjack** |
| 4 — Worst Offenders Hall of Fame | **6 Newsjack** / **1** |
| 5 — Caught Before/After | **3 Emotional storytelling** (build → reveal) |
| net-new — *Guess the Cut* | **3 Emotional** (build under the Q→A open loop) |
| net-new — *It's Not You* (emotional cold open) | **4 Sadder** |
| Restoration / good-news variant | **2 Upbeat** |

> Still set the `music` prop with `{ src, volume }` mixed **~0.22** so VO/captions sit on top
> (`CarouselVideo`, see `posting-schedule.md` §templates). Keep the royalty-free `.mp3` in
> `video/public/audio/` so renders work **offline** (no egress; same constraint as photos/fonts).

---

## The operator workflow (per weekly batch)

The `fullcarts-content` skill, when assembling the week's packet, does for each item:
1. **Assign the lane** from the slot map above (alongside assigning the series + cold-open in `series.md`).
2. **Name the bed** from our saved 2-per-lane favorites (verified, licensed) → put the local
   `video/public/audio/<file>.mp3` path in the script packet (and the `music` prop for carousels).
3. **Flag cross-post handling** in the packet: the master cut uses the **royalty-free bed** (legal on
   TikTok + Reels + Shorts + X + ads); note where a **native trending sound** may be layered for
   discovery (the "trending-sound equivalent" for that lane) on the per-platform copy only.
4. **License receipt:** confirm the track's receipt is on file before it goes in a packet.

### Hybrid play (discovery without the takedown risk)
- **Master (cross-posted everywhere + X + any ad):** royalty-free bed from the lane. This is the default.
- **Discovery add-on (TikTok/IG only):** re-cut the same edit *natively in-app* and add the lane's
  **trending-sound equivalent** from that platform's picker. Accept those native copies won't monetize.
- **Never** put a trending/commercial song in the cross-posted master, on X, or in a boosted ad.

---

## Setup checklist (one-time)
- [ ] Pick the house library — **Epidemic Sound** (brand-safe, cross-post + ads, recommended) or
      **Uppbeat free** to start at zero cost.
- [ ] Save **2 verified tracks per lane** as favorites; download the **license receipt** for each.
- [ ] Drop the chosen `.mp3`s into `video/public/audio/` (offline renders) and note paths here.
- [ ] (Optional) Build the trending-sound shortlist per lane natively in TikTok/IG for the discovery cuts.
