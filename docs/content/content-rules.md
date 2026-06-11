# FullCarts Content Rules — The 5 Non-Negotiables

**Date:** June 10, 2026
**Parent strategy:** `docs/plans/2026-06-10-face-forward-content-strategy.md`
**Purpose:** The standing rules every FullCarts post must obey, in any format, on any platform. If a draft fails any one of these, it does not ship. The content-brief generator scores against them; the pre-publish checklist enforces them.

---

## The 5 non-negotiables

Every post — TikTok, Reel, Short, X post, carousel — must hit **all five**. Not most. All.

### 1. Data-driven
Anchored to a **specific FullCarts datapoint** *or* a **credible macroeconomic event**. There is always a real number on screen, and that number is always sourced.

- ✅ "Gatorade went 32oz → 28oz. That's a 12.5% cut at the same shelf price." (FullCarts entry)
- ✅ "CPI for groceries just printed +X% — here's the category that actually got smaller, not just pricier." (BLS event)
- ❌ "Brands are shrinking everything lately." (no number, no source)

**Sources that count:** the FullCarts database (`product_entities` / `published_changes` / `skimpflation_events`), BLS shrinkflation series, FRED CPI, USDA food-price outlooks, a real retailer listing, a real receipt. **The number must trace to a real artifact** (see the three-bucket evidence policy below).

> **Every stat and credibility claim must trace to `docs/content/approved-claims.md`** (the verified registry). If it's not in §1 of that file or a fresh DB pull, it doesn't go on camera. §3 lists forbidden, disprovable claims (e.g. "3,000+", "decades of data", "cited by Consumer Reports") — saying any of these undoes the entire authority position.

### 2. Interesting
A genuine hook that earns the next 3 seconds — built on **contrast**, not vagueness. Name the
topic in the first sentence (speed to value), then open a curiosity loop by stating or implying
the gap between what the viewer believes and what's true. Written to the viewer ("you/your").

- ✅ "You're paying the same price for this Doritos bag as 2019 — minus a fistful of chips."
- ✅ "There's a second grocery price hike that doesn't show up in any inflation number."
- ❌ "Guess how much smaller this got." / "You won't believe this." — context-free vague hooks
  that only work off your face; the words add nothing. **Banned as the hook.**

The first 3 seconds carry 50–60% of all drop-off. Full method + swipe file + checklist:
the **Hook System** (`.claude/skills/fullcarts-content/references/hooks.md`).

### 3. Credible (authority framing)
Framed from your earned authority — **always the database, sparingly the day-job** — and always *in service of the viewer*, never as a status flex.

- **Database (use freely):** "I run the largest public shrinkflation database — and this one's a record."
- **Day-job (use ~1 in 4–5 videos):** "I do data for a company billions of people have used. Reading numbers is my job — and this number's hiding something."
- Pair with humility when natural: "I almost scrolled past this one myself."
- **Never name your employer.** Insinuate only. Keep the "views my own" disclaimer in bio.

### 4. Relatable
Spoken to a real person who doesn't want to get ripped off at the grocery store. Second person ("you"), kitchen-table language, the universal *"I knew that box felt lighter"* feeling. Not "consumers," not "the market."

- ✅ "You're not crazy — your cereal box really did get thinner. Here's the proof."
- ❌ "Consumers face eroding unit economics across the CPG sector."

Go deeper than "you/your" when you can: name the **unspoken truth** the viewer won't say out loud
(self-blame, "am I crazy," parental guilt) and resolve it with proof — the **Emotional Lock-In**
(`content-angles.md` §4 + `hooks.md`).

### 5. Reaction-evoking
Engineered to pull a reaction — a comment, a share, a "send this to whoever buys the groceries." A kicker, an outrage beat, a direct question, a "tag someone who eats these."

- ✅ "Same price. Two fewer servings. Tell me that's not a stealth price hike. 👇"
- ✅ "Would you still buy it at the new size? Comment 🛒 yes / 💀 no."
- ❌ ending on the number with no ask and no kicker.

---

## The pre-publish checklist

Run this on every draft before it goes in the queue. **5/5 required.**

```
[ ] 1. DATA — a specific, sourced number is on screen, traceable to a real artifact
[ ] 2. INTEREST — first sentence = clear topic (speed to value); hook opens a contrast loop,
       written to "you", NOT a vague open loop ("guess how much…"). See hooks.md checklist.
[ ] 3. CREDIBILITY — database framing present; day-job signature used (if this is a ~1-in-5 video); employer NOT named
[ ] 4. RELATABLE — written in second person, kitchen-table language, "you" not "consumers"
[ ] 5. REACTION — ends on a kicker + an explicit engagement ask (comment/share/tag)

Evidence policy (hard gate — see three buckets below):
[ ] Every claim-carrying visual is REAL (product, charts, dashboard, headlines). No AI impersonating evidence.
[ ] Any AI used is connective/atmosphere only, and the platform AI-label is toggled on.

Platform hygiene:
[ ] Captions burned in (85% watch sound-off)
[ ] 9:16, 30–60s, one cut every 2–4s
[ ] CTA present
[ ] "Views my own" disclaimer in bio (standing)
```

---

## The repeatable brief template

The brief generator (and you, by hand, when needed) produces ideas in this shape. Every brief is pre-scored against the 5 non-negotiables so a passing brief becomes a passing post.

```
IDEA:        Gatorade 32oz → 28oz (-12.5%), same shelf price
WHY NOW:     PepsiCo beverage price hikes trending in news_brand_mentions (4 hits this week);
             summer = peak sports-drink season (seasonal calendar)
PROOF:       2 source URLs (retailer listing + receipt), observed 2026-05, image ✓, FullCarts entry ✓
HOOK:        "Same bottle. Same price. One's missing a full glass of Gatorade."
CREDIBILITY: database lead; day-job signature OPTIONAL this video (not the 1-in-5 slot)
RELATABLE:   "if you grab one after a workout, you're paying the old price for less"
REACTION:    "Would you still buy it? 🛒/💀"
SUGGESTED:   TikTok Reveal + X receipt post (Entertainment + Newsjack)
SCORE:       91   (data 65 × convergence 1.4)   |   5/5 non-negotiables ✓
```

A human reads the ranked digest, picks ~3–5, and Claude drafts the full scripts (see `production-playbook.md` and `first-batch.md`).

---

## AI vs. real-evidence policy — the three buckets (carried forward, non-negotiable)

> **Real evidence proves the claim. AI only decorates around it. AI may illustrate — it must never testify.**

The moment a visual is tied to a specific number, product, brand, or fact, it must be a **real artifact**. This policy exists because two launch videos got flagged (and appeals auto-rejected) for AI impersonating data. With the face-forward pivot, **you are now the primary real-evidence asset** — your authentic on-camera presence is the hardest thing in the kit to fake, and that's a feature.

**Bucket 1 — MUST be real (the proof layer):** the product on camera, a kitchen-scale reading, real commodity/price charts (ICE coffee, FRED CPI screenshots), FullCarts dashboard/page screenshots, real news headlines, real before/after comparisons. **And now: your face and voice.**

**Bucket 2 — CAN be AI (connective layer, labeled):** abstract intros/outros, transitions, mood/atmosphere shots, clearly-stylized metaphor (never a fake chart, never fake packaging), background textures, kinetic typography. Always toggle the platform AI-content label.

**Bucket 3 — NEVER AI (the impersonators):** recreated packaging or logos, fabricated charts/graphs/maps/"data dashboards," anything a viewer would read as *"this is the evidence."*

**The one-question test for any clip:** *"Could a viewer mistake this for evidence of a fact, product, or number?"* — Yes → must be real. No → AI is fine, labeled.

**New / low-trust account rule:** go fully AI-free (real footage + real screenshots only) until the account earns history, then reintroduce labeled bucket-2 decoration only. Never bucket 3.

---

## Voice & tone

- **Direct, factual, lightly outraged on the viewer's behalf** — consumer advocate, never snarky or mean-spirited toward people.
- **Confident, not arrogant** — the receipts flex for you.
- **Plain language** — explain the data like you're showing a friend at the store, not presenting to a board.
- **Document, don't editorialize past the numbers** — neutral framing on brands keeps you out of harassment/legal territory; the data does the indicting.
