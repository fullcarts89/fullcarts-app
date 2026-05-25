# FullCarts Social Content Engine — Faceless Strategy

**Date:** May 13, 2026
**Goal:** Turn the FullCarts database into viral social media content without showing a face, using automation to minimize manual effort.

---

## The Playbook: What Works in This Niche

### Proven accounts in shrinkflation/consumer advocacy

| Creator | Platform | What Happened |
|---------|----------|---------------|
| **Neal Chauhan** (@neal.chauhan) | TikTok | Shrinkflation series hit 20M+ views, 1.5M likes, 10K comments in under a week. Built 33K followers fast. Covered by CP24 and CTV News. |
| **Melissa Simonson** (@realmelissasimo) | TikTok | Documented 50 clear shrinkflation instances. Created #shrinktok. Before/after comparisons. |
| **Addison Jarman** (@addison.jarman) | TikTok | Single shrinkflation explainer hit 500K+ views. |
| **@invasivespeciesguy** | TikTok | 300K views on a single Quaker granola bars video. |
| **Wrigg** | TikTok | Exposed grocery issues; Kentucky Legend ham actually pulled products from Walmart in response. |

**Key stat:** #shrinkflation has 86M+ views on TikTok. 75% of Americans have noticed shrinkflation. 48% abandoned a brand because of it. This is a validated, high-demand niche.

### What makes content go viral in this niche

**Format winners (from OpusClip analysis of 34,635 clips):**

1. **Product/Outcome Showcase** — Show the shocking result FIRST (old vs new side by side), then explain. #1 performer, averaging 6,037 views/clip.
2. **Text-based Reels with surprising data** — Animated text carries the message. 3x better than generic advice content.
3. **Stock footage + narration/text overlay** — Footage that triggers outrage/surprise stops the scroll.
4. **Carousel posts (Instagram)** — Instagram is pushing these hard. Perfect for before/after data.

**Hook formulas that drive engagement:**

| Hook | Why It Works |
|------|-------------|
| "Nobody is talking about this..." | Curiosity gap — brain must resolve the unknown |
| "Companies don't want you to know this..." | Conspiracy framing triggers outrage + curiosity |
| "I compared [product] from 2020 to 2025 and..." | Promise of proof — results-first |
| "Stop buying [product] until you see this..." | Urgency + consumer protection |
| "Did you know that [shocking stat]?" | Pattern interrupt with data |
| "[Brand] just got caught doing this..." | Accountability framing |

**Algorithm rules:**
- 3-second retention above 65% = 4-7x more impressions
- First 1.5 seconds determine distribution
- First-hour engagement drives 80% of reach
- Optimal: 30-45 seconds, 8-12 hashtags, posted at 7am or 4pm ET weekdays
- 70%+ completion rate in first hour = algorithmic boost regardless of follower count

---

## Recommended Tech Stack

### Tier 1: Minimum Viable (~$20/mo)

For getting started immediately with image-based posts:

| Component | Tool | Cost | Role |
|-----------|------|------|------|
| Caption generation | Claude API (Haiku) | ~$5/mo | Generate platform-specific captions from DB records |
| Image generation | **Placid** | $19/mo (500 images) | Branded before/after graphics from templates |
| Scheduling | Buffer free | $0 | 3 channels, 10 posts each |
| **Total** | | **~$24/mo** | |

### Tier 2: Add Video (~$65/mo)

Add short-form video for TikTok/Reels:

| Component | Tool | Cost | Role |
|-----------|------|------|------|
| Caption generation | Claude API (Haiku) | ~$5/mo | Captions + video scripts |
| Image generation | Placid | $19/mo | Static graphics for Instagram/X |
| Video generation | **JSON2Video** | $19.95/mo | Render 15-30s videos from JSON templates, includes Azure TTS |
| Voiceover (premium) | **ElevenLabs** (optional) | $5-22/mo | Higher quality voice if Azure TTS isn't good enough |
| Scheduling | Buffer Essentials | $18/mo (3 channels) | Instagram + TikTok + X |
| **Total** | | **~$62-84/mo** | |

### Tier 3: Full Automation via MCP (~$40/mo + server)

Claude orchestrates the entire pipeline:

| Component | Tool | Cost | Role |
|-----------|------|------|------|
| Data source | Supabase (existing) | $0 | Product data already collected |
| Caption + scripting | Claude with MCP | Per-use | Reads DB, generates all content |
| Image generation | Placid API | $19/mo | Branded graphics |
| Video generation | JSON2Video API | $19.95/mo | Short-form videos |
| Scheduling | **Postiz** (self-hosted) | Free | 30+ platforms, MCP server for Claude |
| **Total** | | **~$40/mo** + hosting | |

---

## Voice & tone

**Reference: the Dungeon Crawler Carl series by Matt Dinniman.** Specifically, the bureaucratic-cheerful tone of the AI system narrator — corporate atrocity delivered as a customer service announcement — paired with the working-class incredulity of a protagonist watching corporations do unspeakable things while smiling about it.

This is a deliberate pivot from the earlier "consumer advocate, never snarky" framing. The data already does the consumer-advocate work. The voice now adds the dimension of treating shrinkflation as what it actually is: a slow-motion corporate caper with a customer service phone number.

### Why DCC fits shrinkflation content

- DCC's core thematic territory is "corporations doing horrible things while smiling about it." That IS the shrinkflation beat.
- The book's system-notification cold opens are tailor-made for the on-screen "fake popup" visual gag that's already dominating TikTok formats.
- The contrast between corporate-cheer and working-class-incredulity carries information without lecturing. We get five seconds of joke and three seconds of receipts and the audience walks away with the data.
- It gives the engine a concrete pattern to generate against. "Funny + witty" is too vague to produce reliably; "system-notification corporate doublespeak + working-class narrator reaction" is something Haiku can hit consistently with a few examples in the skill.

### Core voice characteristics

| Element | What it means | Example phrasing |
|---|---|---|
| Corporate-doublespeak parody | Describe horrible things in the cheerful tone of a corporate press release or system notification | "successfully reformulated," "your fourth automatic enrollment in our weight reduction program," "thank you for your continued participation" |
| Working-class incredulity | The narrator's grounded reaction to the corporate-cheerful framing | "Eight grams. That's nine Mini Eggs they just walked off with. And you tipped them." |
| Bureaucratic specificity | Use exact, mundane numbers to make the absurdity land | "Mass surrendered: 28g. Refund issued: $0.00." |
| Math-as-rhetorical-device | Bare-fact contrasts that need no commentary | "Cocoa cost: +12%. Bag size: −28%. Math is a useful subject." |
| Closing pivot to receipts | Always pivot from the joke to the source citation in the last 3-4 seconds | "BBC News, The Grocer, and seven other sources confirm." |

### Hard rules (do not violate)

1. **No profanity in captions.** TikTok and Reels demote text profanity, which kills distribution. Mild spice ("hell," "damn") OK in voiceover audio. f-word and s-word banned on both surfaces.
2. **No direct references to DCC characters, names, or quoted lines.** Inspired-by, not derivative-of. Voice characteristics are not IP; quoting Princess Donut is.
3. **No editorial accusations beyond what the data supports.** "Stolen" as comic hyperbole describing a documented size reduction = fine. "Cadbury committed fraud" = not fine.
4. **Every video ends with a source citation.** The humor wraps the data, but the data is the deliverable. Name at least one outlet ("BBC News") plus the total count ("nine sources").
5. **No emojis in captions.** Visual gags belong on-screen, not in caption text.

### Hook bank (replaces the older hook list in the prompt template)

- "Attention valued consumer: your [product] has been successfully reformulated."
- "[Brand] would like to congratulate you on the silent renegotiation of your snack agreement."
- "Welcome to your [Nth] automatic enrollment in [Brand]'s weight reduction program."
- "[Brand] has updated the terms of your relationship. They did not ask. You did not notice. We did."
- "Today on Things [Brand] would like you not to notice..."
- "The [Brand] press release said 'cost pressures.' The bag said something different. We brought a translator."

### Reference example: Cadbury Mini Eggs 80g → 72g (2024)

Real event from the database. 22-second script, side-by-side format. Use this as the canonical voice exemplar.

```json
{
  "hook": "Attention valued consumer: your Cadbury Mini Eggs have been successfully reformulated.",
  "beats": [
    {
      "t": "0-4s",
      "voiceover": "Attention valued consumer. Your Cadbury Mini Eggs have been successfully reformulated. The bag is now eight grams lighter. The price is not.",
      "on_screen": "⚠ SYSTEM UPDATE\nCADBURY MINI EGGS\nReformulation: COMPLETE\nMass surrendered: 8g\nRefund issued: $0.00",
      "b_roll": "fake_system_popup_corporate_cheerful_font"
    },
    {
      "t": "4-10s",
      "voiceover": "This is your fourth automatic enrollment in our weight reduction program since 2011. You did not consent. You did not need to. You bought the bag.",
      "on_screen": "ENROLLMENT HISTORY\n2015 · 100g → 96g\n2018 · 96g → 84g\n2021 · 84g → 80g\n2024 · 80g → 72g",
      "b_roll": "stacked_receipts_red_strikes"
    },
    {
      "t": "10-15s",
      "voiceover": "Total weight removed: twenty-eight grams. That's roughly nine Mini Eggs that have been gently, professionally, lovingly stolen from each bag over thirteen years.",
      "on_screen": "28g GONE\n≈ 9 Mini Eggs per bag",
      "b_roll": "candy_count_animation_disappearing"
    },
    {
      "t": "15-20s",
      "voiceover": "Mondelēz International says it's the cost of cocoa. Cocoa is up twelve percent. The bag is down twenty-eight. Math is a useful subject.",
      "on_screen": "COCOA COST: +12%\nBAG SIZE: −28%\nMATH: hard, apparently",
      "b_roll": "two_bars_one_obviously_bigger"
    },
    {
      "t": "20-24s",
      "voiceover": "BBC News, The Grocer, and seven other sources confirm. Full receipts at fullcarts dot org slash Cadbury.",
      "on_screen": "9 sources · 0 denials\nfullcarts.org/cadbury",
      "b_roll": "end_card_with_source_logos"
    }
  ],
  "caption_tiktok": "Cadbury would like to congratulate you on the successful reformulation of your Mini Eggs bag. It is now 8g lighter. You were not consulted. This is the fourth time. Receipts in bio. #shrinkflation #cadbury #miniegg #greedflation",
  "caption_reels": "Mondelēz International has 'reformulated' Cadbury Mini Eggs four times since 2011. Each time the bag got smaller. The price did not. They blame cocoa (up 12 percent). The bag is down 28 percent. Nine sources, including BBC News and The Grocer. Link in bio for the full enrollment history. #shrinkflation #cadbury #miniegg"
}
```

When the `fullcarts-voice` skill is built in PR #1 of the content engine, this example moves to `.claude/skills/fullcarts-voice/examples/` so Haiku has done-for-you scripts to imitate, not just abstract rules. Target minimum 3-5 examples there — one per pillar (Gotcha Reveal, By the Numbers, Worst Offenders, Skimpflation, Restoration).

---

## Content Pipeline Architecture

### How a database record becomes a social media post

```
┌─────────────────────────────────────────────────────────┐
│ SUPABASE: content_candidates view                       │
│ (scored by content_score: image + magnitude + recency)  │
└───────────────┬─────────────────────────────────────────┘
                │ Query top-scored records
                ▼
┌─────────────────────────────────────────────────────────┐
│ CLAUDE API: Generate content for each record            │
│                                                         │
│  Input:  { brand, product, old_size, new_size,          │
│            pct_change, category, image_url }             │
│                                                         │
│  Output: { x_caption, ig_caption, tiktok_script,        │
│            hook_text, cta_text, hashtags }               │
└───────────────┬─────────────────────────────────────────┘
                │
        ┌───────┴───────┐
        ▼               ▼
┌──────────────┐ ┌──────────────────┐
│ PLACID API   │ │ JSON2VIDEO API   │
│              │ │                  │
│ Render image │ │ Render 15-30s    │
│ from template│ │ video with TTS   │
│ (Instagram,  │ │ (TikTok, Reels)  │
│  X posts)    │ │                  │
└──────┬───────┘ └────────┬─────────┘
       │                  │
       └────────┬─────────┘
                ▼
┌─────────────────────────────────────────────────────────┐
│ BUFFER API or POSTIZ MCP                                │
│ Schedule posts across Instagram, TikTok, X              │
│ Optimal times: 7am ET or 4pm ET weekdays                │
└─────────────────────────────────────────────────────────┘
```

### Content generation prompt template

```
You are the social media voice for FullCarts (@fullcarts), a shrinkflation
watchdog that uses real data to hold brands accountable.

Voice: Bureaucratic-cheerful corporate-doublespeak parody paired with
working-class incredulity. See the "Voice & tone" section above for the
full rules, hook bank, and reference example (Cadbury Mini Eggs).
The data is the deliverable; the humor is the wrapper that gets it shared.
Every output ends with a source count and at least one named outlet.

Given this product data, write posts for 3 platforms:

Product: {product_name}
Brand: {brand}
Old Size: {old_size} {size_unit}
New Size: {new_size} {size_unit}
Change: {pct_change}%
Category: {category}
Source: {evidence_summary}

RULES:
- Open with a hook from the "Voice & tone → Hook bank" section above
  (e.g. "Attention valued consumer: your [product] has been successfully reformulated.")
- Lead the body with the most concrete number contrast (cocoa +12% vs bag −28%)
- Treat the brand's PR rationale as something to deadpan, not refute directly
- Close with the source count + at least one named outlet
- Include #shrinkflation #fullcarts and 6-10 relevant hashtags. No emojis.
- End with the bio link CTA: "Receipts in bio" or "Full enrollment history at fullcarts.org/..."

FORMAT:
X (under 260 chars): [caption]
Instagram (2-3 sentences + hashtags): [caption]
TikTok script (hook in first 5 words, 30 seconds total): [script with voiceover text]
```

---

## Content Pillar Schedule (Weekly)

| Day | Platform | Pillar | Format | Automation Level |
|-----|----------|--------|--------|-----------------|
| **Mon** | Instagram + TikTok | Gotcha Reveal | Carousel / short video | Full — template + data |
| **Tue** | X | By the Numbers | Text + image | Full — stat query + Placid |
| **Wed** | Instagram + TikTok | Gotcha Reveal | Carousel / short video | Full — template + data |
| **Thu** | Instagram | Worst Offenders OR Skimpflation | Carousel | Full — ranking query + Placid |
| **Fri** | X + Instagram | Gotcha Reveal | Image + text | Full — template + data |
| **Sat** | — | Queue prep | — | Manual review of generated content |
| **Sun** | Newsletter | Weekly roundup | Email | Semi-auto — Claude drafts, you review |

**Monthly specials:**
- 1st: "Monthly Shrinkflation Report" (macro stats from FRED + BLS)
- Mid-month: "Brand Spotlight" deep-dive
- End of month: "Restoration of the Month" (positive story)

---

## Format Library — Segment Types Beyond the Event List

The overplayed shrinkflation format is anecdotal and accusatory ("look how small, they're robbing us"). FullCarts' differentiator is a sourced, quantified, time-series database with economic and corporate-ownership context — so the formats that win are the ones a creator with a phone and a hunch literally **cannot make**. Every segment below converts a database record into one of three jobs: **hit the wallet** (turn a size delta into a number that stings), **give an action** (tell the viewer what to buy instead), or **reveal something invisible** (surface structure only the database knows). All obey the Voice & tone hard rules — named outlet + source count in the close, no emojis in captions, inspired-by not derivative, no accusation beyond the data.

### A. Hit the wallet (quantify)

| Segment | Job it does | Data source | Example hook (voice-compliant) | Pillar |
|---|---|---|---|---|
| **The Effective Price Hike** | Reframe the shrink as the stealth *price increase* it actually is (price held, size dropped → hidden +% per unit). The truest, most repeatable reframe. | `published_changes` size delta + price from Kroger / Walmart / Open Prices observations | "Attention valued consumer: [Brand] did not raise the price of your [product]. They raised the price of your [product]." | By the Numbers |
| **The Annual Receipt** | Per-year wallet cost at a stated consumption rate (your example). | size delta + price/unit × on-screen consumption assumption | "Your involuntary annual contribution to [Brand], assuming one bag a week: $X. No receipt was issued." *(on-screen: "assumes 1/week")* | By the Numbers |
| **What Your Money Used to Buy** | Purchasing-power erosion over time. | `variant_observations` time series + price | "In 2019, five dollars bought you 200 grams. Management has since revised your allocation downward." | By the Numbers |

### B. Give an action (alternatives — rare in this niche, so own it)

| Segment | Job it does | Data source | Example hook (voice-compliant) | Pillar |
|---|---|---|---|---|
| **Who Didn't Shrink** | Name the category holdout that held its size. Positive, shareable, and structurally uncopyable — needs the whole category in one database. | `product_index` / `brand_index` filtered by category, delta ≈ 0 | "In a category where everyone enrolled in the weight reduction program, one brand declined to participate. We checked twice." | NEW — "The Holdout" |
| **Unit-Price Winner** | Best price-per-unit in a category right now. | latest `variant_observations` price + size by category | "Per gram, here is who is currently robbing you the least. Faint praise, fully sourced." | NEW — "The Holdout" |

### C. Reveal what they can't see (your unique data = the moat)

| Segment | Job it does | Data source | Example hook (voice-compliant) | Pillar |
|---|---|---|---|---|
| **The Illusion of Choice** | Reveal that "rival" brands that all shrank share one parent. Highest "wait, *what?*" payload; pure database flex. | `corporate_tree` (Wikidata manufacturer backfill) | "Six brands. Six separate shrink announcements. One corporate return address." | NEW — "Same Parent" |
| **They Swapped the Recipe** | It didn't just shrink — cheaper ingredients went in (less cocoa, palm oil, real fruit out). The second, under-covered story. | `skimpflation_events` + `nutrient_deltas` + `consumer_reports_findings` | "[Brand] is pleased to announce your [product] now contains meaningfully less of the expensive part." | Skimpflation |
| **Death by a Thousand Cuts** | Animate one product's multi-step shrink trajectory across years. The drip is more damning than any single event. | `variant_observations` / per-entity `published_changes` history (the trajectory step-chart) | "This is your fourth automatic enrollment since 2011. Each time, slightly less. Each time, you bought the bag." | Gotcha Reveal |
| **Restoration Corner** | Brands that shrank then *restored* size — rare, positive, proves accountability works. | `restorations` view | "In a stunning reversal, [Brand] has returned the [N] grams it previously borrowed. We are as surprised as you are." | Restoration of the Month |
| **Your Cart vs. the Official Number** | Contrast measured shrink with CPI; note the government's own downsizing log. Positions FullCarts as the source that counts what CPI doesn't. | `fred_cpi_data` + `bls_shrinkflation` | "Official inflation this year: three percent. The government's own downsizing log: see attached. Your cart has notes." | Monthly Shrinkflation Report |

### D. Format & engagement mechanics (structure, not topic)

| Mechanic | What it adds | Data / source hook |
|---|---|---|
| **The Corporate Announcement** | Make the DCC voice *structural*: every video framed as a chipper system-notification "customer service announcement," undercut by the data. The brand's signature beat, not just tone. | the system-popup cold open already in the Cadbury exemplar |
| **Show the Receipts** | Put the evidence locker on screen — Wayback snapshots, source count, named outlet. Turns the mandatory source outro into a credibility flex. | `event_evidence_summary`, Wayback rows, source logos |
| **Verified Viewer Tip** | Route the `/tips` intake into content: community + free pipeline + credibility. | `tips` table → matched to a verified `published_changes` row |
| **Guess the Shrink** | Interactive: show the before, freeze, audience guesses the after, reveal. Comment-bait, cheap, repeatable. | any high-magnitude `content_candidates` record |

### How this plugs into the engine

- **Top 3 to build first:** Effective Price Hike (truest reframe), Who Didn't Shrink (the action competitors can't copy), Illusion of Choice (highest surprise payload).
- **Two new pillar candidates** — *The Holdout* (Who Didn't Shrink / Unit-Price Winner) and *Same Parent* (Illusion of Choice) — are strong enough to earn a weekly rotation slot alongside Gotcha Reveal / By the Numbers.
- **`content_candidates` scoring should gain segment-eligibility flags** so the generator can pick the right format per record: has category siblings → Holdout-eligible; has a `corporate_tree` parent with ≥2 shrunk children → Illusion-eligible; has non-empty `nutrient_deltas` → Skimpflation-eligible; appears in `restorations` → Restoration-eligible.
- Each segment becomes a labelled example in `.claude/skills/fullcarts-voice/examples/` so Haiku generates against a concrete template per format, not abstract rules.

---

## Implementation Plan

### Week 1: Set up the image pipeline

1. **Sign up for Placid** ($19/mo) and design 3 templates:
   - **"Gotcha" template:** Product image left, size comparison right, red percentage badge, FullCarts watermark
   - **"Ranking" template:** Top 5 list layout with brand names and event counts
   - **"Stat" template:** Large number in center, context text below, dark background

2. **Create social accounts:** Instagram (@fullcarts), TikTok (@fullcarts), X (@fullcarts)

3. **Sign up for Buffer** (free tier initially)

4. **Write `pipeline/scripts/generate_social_content.py`:**
   - Queries `content_candidates` view for top-scored records
   - Calls Claude API to generate captions per platform
   - Calls Placid API to render branded images
   - Outputs a batch of ready-to-schedule posts
   - Supports `--dry-run` to preview without rendering

### Week 2: First posts + iterate

5. **Generate first batch of 10 posts** using the script
6. **Review and schedule** via Buffer (manual for first week to tune quality)
7. **Post 3-5x/week** and monitor engagement
8. **Iterate on templates and hooks** based on what performs

### Week 3: Add video pipeline

9. **Sign up for JSON2Video** ($19.95/mo)
10. **Design a video template** (JSON format):
    - 0-2s: Hook text on dark background
    - 2-5s: Product image with brand name
    - 5-10s: Before/after size comparison animation
    - 10-15s: Percentage badge with voiceover stat
    - 15-20s: CTA ("Follow @fullcarts for more")
11. **Extend the script** to also generate video for TikTok/Reels content

### Week 4+: Scale and automate

12. **Add to GitHub Actions** — weekly workflow that generates content batch
13. **Evaluate Postiz** for MCP-based scheduling (eliminates Buffer cost)
14. **Add newsletter pipeline** using the weekly roundup data
15. **Track engagement** and optimize posting times, hook styles, and template designs

---

## Gaps and Risks

| Risk | Mitigation |
|------|-----------|
| Product images still NULL | Phase 1 image backfill must complete first |
| Dedup issues inflate brand rankings | Phase 1 dedup must run before "Worst Offenders" content |
| Content feels robotic / AI-generated | Human review step on Saturday before scheduling next week. Vary hooks. |
| Platform account suspension (new accounts posting frequently) | Start slow: 3 posts/week for first 2 weeks, then ramp to daily |
| Legal risk from brand tagging | Stick to factual data. Source everything. Don't editorialize beyond the numbers. |
| Low initial reach (no followers) | First 10 posts should target high-search hashtags (#shrinkflation, #groceryprices). Engage with existing shrinkflation creators' comments. |
| Video quality from automated tools | Test JSON2Video output quality before committing. Fall back to Canva templates if needed. |

---

## Key Insight: Why This Will Work

FullCarts has something no other shrinkflation creator has: **a structured database of 3,000+ verified changes backed by government data (BLS, USDA, FRED CPI).** Every other creator is doing one-off anecdotal posts. You can produce content at scale with real evidence trails — that's the moat. The faceless format works because the DATA is the star, not a personality.

The most viral shrinkflation content (Neal Chauhan's 20M-view series) was essentially what your database already contains: before/after comparisons with specific numbers. The difference is he found them manually. You have a pipeline that finds them automatically.
