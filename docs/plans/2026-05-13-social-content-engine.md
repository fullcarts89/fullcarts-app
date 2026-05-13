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

Voice: Direct, slightly outraged but factual. Consumer advocate tone.
Never snarky or mean-spirited. Always cite the data.

Given this product data, write posts for 3 platforms:

Product: {product_name}
Brand: {brand}
Old Size: {old_size} {size_unit}
New Size: {new_size} {size_unit}
Change: {pct_change}%
Category: {category}
Source: {evidence_summary}

RULES:
- Lead with the most shocking number or comparison
- Use one of these hook patterns: "Did you know...", "[Brand] just got caught...",
  "Stop buying [X] until you see this...", "Nobody is talking about..."
- Include #shrinkflation #fullcarts and 3-5 relevant hashtags
- End with a CTA: "Follow for more" or "Link in bio for the full database"

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
