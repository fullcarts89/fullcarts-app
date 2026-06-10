# FullCarts Approved-Claims Registry

**Date:** June 10, 2026 · **Data as-of:** 2026-06-10 (re-pull before each batch — see "Refresh" below)
**Parent:** `content-rules.md` (non-negotiable #1 = data-driven, #3 = credible)
**Purpose:** The single source of truth for what you may state on camera. Everything in **§1 is verified against the live database or web research** and safe to say verbatim. **§3 is forbidden** — disprovable claims that would undercut the whole authority position. When in doubt, a claim must trace to this file or it doesn't ship.

---

## §1 — Approved claims (verified, say verbatim)

### Database scale
- ✅ **"2,200+ documented shrink events"** (live: 2,228, non-retracted)
- ✅ **"across 900+ brands"** (live: 938)
- ✅ **"nearly 1,900 products"** (live: 1,881)
- ✅ Specific entries are all confirmed in-DB (use exact figures, not rounded):
  - Folgers Coffee **51 → 43.5 oz (−14.7%)** · 31 evidence
  - Gatorade **32 → 28 fl oz (−12.5%)** · 28 · and **20 → 16.9 fl oz (−15.5%)** · 23
  - Cadbury Dairy Milk Freddo Faces Easter Egg **122 → 99 g (−18.9%)** · 72
  - Chobani Flips yogurt **5.3 → 4.5 oz (−15.1%)** · 21
  - Crest Toothpaste **4.1 → 3.8 oz (−7.3%)** · 21
  - Kleenex Tissues **65 → 60 ct (−7.7%)** · 20
  - Nescafé Azera Americano **100 → 90 g (−10%)** · 20

### Evidence depth & sourcing
- ✅ **"Built on 5 million+ raw evidence items"** (live: 5,445,213 `raw_items`)
- ✅ **"Cross-checked across 9 independent sources"** — Reddit, news, GDELT, Kroger, OpenFoodFacts, Open Prices, USDA (+ size-change feeds)
- ✅ **"Backed by U.S. government data — USDA, BLS, and the Federal Reserve (FRED CPI)"** (live: ~2.0M USDA product records, 959 BLS shrinkflation points, 8,352 FRED CPI rows)
- ✅ **"Every entry is source-cited — look it up yourself at fullcarts.org"** (reproducibility = your moat)
- ✅ **"Free, public, no ads — I'm not selling you anything"** (independence)
- ✅ **"Continuously updated"** (727 events added in 2025+; latest 2026-05-16)

### The superlative (use a qualified form — see verdict in §2)
- ✅ **"The largest free, public, searchable shrinkflation database"**
- ✅ **"…that I know of"** (zero-exposure version)
- ✅ **"~2,200 source-cited shrink events across 900+ brands"** (falsifiable specific — strongest, pair with the superlative)

---

## §2 — Conditional / judgment claims

### "I work in data for a big tech company" (the day-job signature)
- **Only state what is literally true.** Insinuate, never name the employer. Approved forms: *"I do data for a company billions of people have used,"* *"I analyze data for a living,"* *"I work in data at a major tech company."*
- **Do not** inflate title/seniority or imply your employer endorses or is involved with FullCarts.
- **Check your employment agreement / social-media policy first** — the real risk is contractual, not audience-side.
- **Standing disclaimer required** wherever this is used: *"Personal project. Views my own."*
- **Frequency:** ~1 in 4–5 videos + bio (per strategy doc).

### "Largest public database" — verdict
Defensible: no public, structured, product-level shrinkflation database approaches 2,200 events / 1,881 products / 938 brands (nearest public competitors: ShrinkWatch ~40, Neage.jp ~400, Verbraucherzentrale ~1,000; "The Shrink List" shows 0/0 live). Larger datasets exist only behind academic paywalls (NielsenIQ), which the word *public* excludes. Use the qualified forms in §1; never the bare "largest shrinkflation database."

---

## §3 — FORBIDDEN claims (disprovable — never say these)

- ❌ **"3,000+ changes"** — it's 2,228. Inflation here is the fastest way to lose the authority position.
- ❌ **"Data going back to 1985 / decades of history"** — only **13 events predate 2020** (one stray 1985 outlier). The corpus is 2020→present. Say "thousands of changes, continuously updated," not historical depth.
- ❌ **"Cited by / partnered with Consumer Reports"** (or any press) — `consumer_reports_findings` is empty (0 rows). Bank real press only after it actually happens.
- ❌ **"The largest shrinkflation database"** (no qualifier) — false vs. paywalled academic datasets.
- ❌ Naming your employer, or implying employer endorsement.
- ❌ Any number not traceable to this registry or a fresh DB pull.

---

## Refresh

The DB grows weekly, so these numbers drift **up**. Before each batch, re-pull and update §1:

```sql
SELECT
  (SELECT count(*) FROM published_changes WHERE is_retracted IS NOT TRUE) AS total_events,
  (SELECT count(DISTINCT brand) FROM published_changes WHERE is_retracted IS NOT TRUE) AS total_brands,
  (SELECT count(DISTINCT entity_id) FROM published_changes WHERE is_retracted IS NOT TRUE) AS total_products,
  (SELECT count(*) FROM raw_items) AS raw_items;
```

Round **down** to the safe banner number (2,228 → "2,200+"). Never round up.
