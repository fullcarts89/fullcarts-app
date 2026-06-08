# FullCarts Social Content Strategy — Manual Engine + Brief Automation

**Date:** June 8, 2026
**Supersedes:** `2026-05-13-social-content-engine.md` (the fully-automated render-pipeline plan)
**Goal:** Turn the FullCarts database into engaging social content across Instagram, TikTok, and X — produced by hand, but *fed* by a single piece of automation that decides **what to make and why it'll land this week**.

---

## What changed since May 13

The original plan proposed a fully-automated production pipeline: `content_candidates` → Claude captions → Placid images → JSON2Video clips → auto-scheduled. That pipeline was never built. The intervening month went into **data-quality hardening** (dedup, retraction discipline, entity merge, image archival, quality-flag queue), which knocked out the exact prerequisites the May 13 plan flagged as blockers — so the foundation is now trustworthy enough to put on a public account.

Two deliberate decisions reshape the strategy:

1. **Automated *production* is out.** Every post is hand-made in normal creator tools (CapCut, Canva). API-rendered stat cards / TTS videos are abandoned — they capped out on reach and risked the "robotic / AI-generated" failure mode. Effort is now the scarce resource, so the plan is built around a realistic human output rate.
2. **Automated *ideation* is the one piece worth keeping.** The sole automation is a **content-brief generator**: it tells you what to post about, backed by FullCarts data and pegged to the outside world. It generates *ideas*, never finished content.

---

## Why faceless ≠ automated (the format correction)

The May 13 plan's own evidence undercut its thesis. Every viral example it cited — Neal Chauhan (20M views), Melissa Simonson (#shrinktok), Addison Jarman (500K) — is **a person physically handling a real product on camera.** None went viral with rendered stat cards. "Faceless" got conflated with "automated graphics," and those are different decisions. The viral-native version of faceless in this niche is **hands + real products + voiceover** — no on-camera identity, but the visceral physical proof intact.

The database is the **sourcing + credibility moat** (it never runs out of *verified, sourced* stories, and every claim has a BLS/USDA/receipt trail a reporter can trust) — it works backstage, while physical proof works on stage.

---

## Platform roles (stop spreading evenly)

| Platform | Role | Why |
|---|---|---|
| **TikTok / Reels** | Growth surface | Rewards human-hands physical-proof format; where shrinkflation goes viral (#shrinktok, 86M+ views) |
| **Instagram** | Data / proof surface | Carousels are pushed hard; natural home for before/after data + rankings |
| **X** | Credibility + newsjacking surface | Where reporters live (Chauhan → CP24/CTV pickup); reactive posting is nearly free to produce |

---

## Content TYPES, per platform

**TikTok / Reels** (make once, cross-post both)
- **The Reveal** (workhorse, ~20–35s): one product, before → after. Strongest as physical hands-on-packaging; no-film fallback is a CapCut edit of the two retailer listings side-by-side with text overlay + trending audio.
- **The Rundown** (~40–60s): "5 things that shrank this month," rapid-fire from the DB.
- **The React**: green-screen over a news headline or another creator's clip, supplying the verified number.

**Instagram**
- **Before/after carousel**: slide 1 = the shocking number, slides 2–3 = proof + source, last = CTA.
- **Rankings carousel**: monthly "Worst Offenders" leaderboard.
- **Reels**: cross-post the TikToks.
- **Stories** (low-effort glue): polls ("noticed your cereal box get thinner?"), reshares, "how we verify a claim" BTS.

**X**
- **The receipt post**: before/after image + tight caption + `fullcarts.org` link.
- **Threads**: "Every Cadbury size change since 2019 🧵" — a `/brands/[name]` timeline repurposed.
- **Reactive posts**: quote-tweet news, brand announcements, BLS/CPI releases. The bulk of X and the cheapest reach available.

> **Open production fork (not yet decided):** TikTok Reveals can be *filmed physical proof* or *edited-from-screenshots*. This changes how a Reveal is made but nothing about the pillars or schedule below.

---

## Content PILLARS (rebalanced for manual)

| Pillar | Share | Home | Note |
|---|---|---|---|
| **Gotcha Reveal** | ~45% | TikTok / Reels / IG | Single-product before/after. Core. |
| **Newsjacking** | ~20% | X-led, clip to TikTok | Promoted to a top pillar. Cheapest reach, human-only — a render pipeline can't react to today's news. |
| **Worst Offenders / Rankings** | ~15% | IG carousel | Monthly tentpole. |
| **By the Numbers / Receipts** | ~15% | X + IG | One striking stat, standalone. |
| **Restoration / Good News** | ~5% | all | When a brand reverses — brand-equity builder. |

---

## SCHEDULE (sustainable hand-made cadence)

Target: **3 hero pieces/week**, each repurposed across platforms; X carries the daily presence because reactive posting is cheap.

| Day | TikTok / Reels | Instagram | X |
|---|---|---|---|
| **Mon** | Reveal #1 | cross-post reel + Story poll | Reveal #1 → receipt post |
| **Tue** | — | — | Newsjack / engage in replies |
| **Wed** | Reveal #2 | cross-post reel | Thread: brand timeline |
| **Thu** | — | Carousel (before/after *or* ranking) | Newsjack / engage |
| **Fri** | The Rundown ("5 shrinks this week") | cross-post reel + Story | Rundown → receipt + engage |
| **Sat** | — | — | light engagement only |
| **Sun** | — | reshare top post to Story | — |

**Production rhythm:** one ~2–3 hr batch session makes the week's 3 hero pieces; then 15–20 min/day of X engagement + Stories.
**Monthly tentpoles:** 1st → Worst Offenders carousel; mid-month → brand deep-dive thread; end of month → Restoration post.
**Ramp / account safety:** the manual pace *is* the safe-launch pace — 3 hand-made pieces/week won't trip new-account spam heuristics, so the old "start slow" risk takes care of itself.

---

## The one automation: the Content-Brief Generator

A weekly (plus event-triggered) engine that decides **what to make and why it'll land now**. It generates *briefs* — ideas backed by evidence and pegged to the moment — never finished posts.

### Inputs — three of four already flow into Supabase

| Input | In the DB? | Source objects |
|---|---|---|
| **FullCarts data** (the spine) | ✅ | `content_candidates`, `skimpflation_events`, `brand_index`, restorations |
| **Current events** | ✅ | `news_brand_mentions` (news/GDELT mentions joined to *our* brands), `consumer_reports_findings` |
| **Macro factors** | ✅ | `fred_cpi_data`, `bls_shrinkflation`, `google_trends_data` |
| **Cultural trends** | ⚠️ partial | `google_trends_data` (search interest) + **one new thin signal**: a curated seasonal calendar |

### Core idea: a convergence detector

The existing `content_candidates` view ranks shrink events only by image + magnitude + recency. The brief generator adds the missing dimension — **a data point scores higher when it collides with the outside world**, and that collision *is* the "why now":

- Big shrink in our data **+** that brand spiking in `news_brand_mentions` this week → top candidate (newsjack-ready).
- **CPI / grocery-inflation print drops** → surface the macro "by the numbers" angle + the category that moved most.
- **Google Trends "shrinkflation" climbing** → push Reveal content harder that week.
- **Calendar moment** (Halloween candy, back-to-school, Super Bowl snacks, holiday baking) → surface shrinks in that category.

So: **base score = FullCarts signal** (magnitude, recency, image, repeat-offender, restoration); **multiplier = external convergence** (news / macro / trend / calendar). Proprietary data is the spine; the attention environment is the amplifier.

### The boundary we hold

The engine produces the **idea + the backing data + the why-now line + a suggested platform/format** — and stops there. Claude may phrase the angle and the why-now (that is candidate generation). It never writes the finished caption, video, or carousel. That is the line between "the only automation is candidate generation" and content production.

### Output shape (per brief)

```
IDEA:      Cadbury Dairy Milk dropped 180g → 160g (-11%)
WHY NOW:   3 news hits this week on Mondelez price hikes (news_brand_mentions);
           UK choc inflation in latest CPI print
PROOF:     2 source URLs, observed 2026-05; image ✓
SUGGESTED: TikTok Reveal + X receipt post (Gotcha pillar)
SCORE:     92  (data 64 × convergence 1.4)
```

A human reads the ranked digest, picks ~3, and produces the posts by hand.

### Build sketch

- **`pipeline/scripts/generate_content_briefs.py`** — joins the signal views, computes the convergence score, calls Claude once per top candidate to phrase the angle + why-now, emits a ranked markdown/JSON digest. Supports `--dry-run`.
- **Cadence:** weekly digest (feeds the Saturday batch-prep slot, replacing a blank query with a ranked evidence-backed idea list) **+** an event-triggered alert when a *tracked* brand breaks news or a CPI print lands (feeds newsjacking).
- **The one new signal:** a small curated content calendar (seasonal category tentpoles) joined with existing Trends data. Optional later: a live web-search zeitgeist enrichment layer.
- **Schedule fit:** slots exactly where the old plan had "Sat: queue prep."

---

## Gaps and risks

| Risk | Mitigation |
|---|---|
| Manual production can't sustain daily original posts | Plan is built around 3 hero pieces/week repurposed; X carries daily presence via cheap reactive posts |
| Cultural-trend signal is the one input not natively ingested | Start with curated calendar + existing Google Trends; defer live web-search enrichment |
| Brief feels generic if convergence is weak in a quiet week | Fall back to evergreen high-magnitude Reveals from `content_candidates`; quiet weeks are fine at 3 pieces |
| Legal risk from brand tagging | Stick to factual data; every brief carries source URLs from the evidence trail |
| New-account suspension | Manual pace self-limits to a safe ramp; lead first posts with high-search hashtags + engage existing creators' comments |
| Filmed vs. screenshot Reveal undecided | Resolve the production fork before the first batch session; doesn't block building the brief generator |

---

## Why this works

Every other shrinkflation creator finds stories by hand, one anecdote at a time. FullCarts has **3,000+ verified changes backed by government data** *and* a pipeline already ingesting the news, macro, and trend signals that tell you which of those stories the world is ready to hear *this week*. The brief generator turns that into an unfair ideation advantage; the human keeps production authentic where it has to be (physical proof on TikTok) and cheap where it can be (reactive receipts on X).
