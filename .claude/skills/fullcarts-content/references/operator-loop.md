# Operator Loop — exact steps, queries, commands

Project ref: `ntyhbapphnzlariakgrw`. Use the Supabase MCP `execute_sql` for read queries.
Toolkit lives in `video/` (see its README). All commands run from repo root unless noted.

---

## Step 1 — Refresh the facts (start of every batch)

```sql
SELECT
  (SELECT count(*) FROM published_changes WHERE is_retracted IS NOT TRUE) AS total_events,
  (SELECT count(DISTINCT brand) FROM published_changes WHERE is_retracted IS NOT TRUE) AS total_brands,
  (SELECT count(DISTINCT entity_id) FROM published_changes WHERE is_retracted IS NOT TRUE) AS total_products,
  (SELECT count(*) FROM raw_items) AS raw_items;
```
Round the banner number **down** ("2,228 → 2,200+"). Update `approved-claims.md` §1 and
`profile-copy.md` if it moved. Never round up.

## Step 2 — Brief (rank candidates by convergence)

Base candidates — high-magnitude, well-evidenced, image-backed, recent:

```sql
SELECT brand, product_name, size_before, size_after, size_unit,
  round((1-(size_after::numeric/nullif(size_before,0)))*100,1) AS pct_smaller,
  evidence_count, observed_date
FROM published_changes
WHERE is_retracted IS NOT TRUE
  AND size_before IS NOT NULL AND size_after IS NOT NULL
  AND size_after < size_before
  AND (size_after::numeric/nullif(size_before,0)) BETWEEN 0.5 AND 0.97
ORDER BY evidence_count DESC NULLS LAST, pct_smaller DESC
LIMIT 25;
```

Convergence multiplier — does a candidate brand collide with the outside world this week?
**Run every candidate through the full Convergence Peg Library (`docs/content/content-angles.md` §5) —
all peg types, not just commodity stories.** Cross-check `news_brand_mentions` (recent news/GDELT hits
joined to our brands) and the macro tables (`fred_cpi_data`, `bls_shrinkflation`) for a scheduled print;
also test the non-commodity pegs (record-profits, parent-company convergence via `corporate_tree`,
tariffs, labeling laws, CEO quotes, accountability, reactive newsjack). A candidate that also spikes in
the news, sits in the category a fresh CPI/USDA print just moved, or lands on **≥2 pegs at once** ranks
first. Calendar moments (Halloween candy, back-to-school, Super Bowl, holiday baking, summer ice cream)
lift candidates in that category. *External facts a peg leans on (prices, profits, quotes, laws) are
NOT approved-claims — trace each to a real source and show it via `SourceFrame`; re-verify on render day.*

**Dedup against what already shipped:** read `docs/content/content-log.md` and **drop any candidate
whose `brand + product + change` is already logged as posted.** A *different* size-change for the same
brand is a new episode, not a repeat — that's allowed.

**Score** = base (magnitude, recency, evidence_count, image) × convergence (news/macro/calendar).
Pick **3–5** with a spread across content buckets: ~2 educational, 1 newsjack, 1 reveal, rotate
in 1 personal. Confirm a CPI/USDA print on the calendar this week → that's an automatic newsjack slot.

## Step 3 — Script (house template)

For each pick, draft to the template in `docs/content/first-batch.md`:
`HOOK (face, 0–3s) → PROOF (real product + FullCarts/source screenshot) → CONTEXT (+ overlay,
day-job signature on ~1-in-5) → PAYOFF (kicker) → CTA`. Write per-platform captions + 4–6 hashtags.

**Write the hook with the Hook Engine** (`references/hook-engine.md`): fill the slot tokens from the
brief row, pick lead frames off the selection matrix (signature × peg), bind every blank, snap-check,
and gate each. Keep the top candidate as the spoken hook and bank the rest as caption hooks + Agent
Opus A/B variants. A frame that stays a vague open loop after binding is killed, not shipped.
Read it back as the creator would say it at the store; cut anything stiff.

## Step 4 — Gate

Run all three gates from `references/gates.md`. Any fail → fix or drop. Do not proceed on a 4/5.

## Step 5 — Assets

**Pick the overlay by format** (toolkit compositions; full table in `video/README.md`):
| Script format | Composition | Render |
|---|---|---|
| Reveal / Gotcha | `ShrinkOverlay` (`mode:"restoration"` for good-news) | alpha .mov |
| By-the-numbers / DB counter / CPI headline | `StatCard` | .mp4 |
| Rundown (per item) | `RundownChip` ×N | alpha .mov |
| On a REAL screenshot (BLS/FRED/FullCarts) | `SourceFrame` | alpha .mov |

**Render** — copy a props file in `video/src/props/`, set exact figures from the DB, then:
```bash
cd video
# alpha overlays for compositing in Captions App:
npx remotion render ShrinkOverlay out/<slug>.mov --codec=prores --prores-profile=4444 --props=src/props/<slug>.json
npx remotion render RundownChip  out/<slug>.mov --codec=prores --prores-profile=4444 --props=src/props/<slug>.json
npx remotion render SourceFrame  out/<slug>.mov --codec=prores --prores-profile=4444 --props=src/props/<slug>.json
# full-frame card:
npx remotion render StatCard     out/<slug>.mp4 --codec=h264 --props=src/props/<slug>.json
```
(First render downloads Chrome Headless Shell — needs network; if blocked, the human renders locally.)

**Higgsfield b-roll (optional, Bucket-2 only):** use the Higgsfield MCP for abstract intro /
atmosphere / metaphor shots. NEVER a chart, packaging, or anything readable as evidence. Tell the
human to toggle the platform AI-label.

**Real screenshots the human must grab** (Bucket-1): list them explicitly per clip (e.g. "screen-record
the FullCarts Gatorade page", "screenshot the FRED CPI chart"). The kit can't fake these — by design.

## Step 6 — Production packet (emit one per clip)

```
CLIP:        <title>            BUCKET: <educational|newsjack|reveal|personal|entertainment>
PLATFORMS:   TikTok + Reels + Shorts (+ X receipt if applicable)
POST TIME:   <day, optimal slot>

SCRIPT:      <full hook→proof→context→payoff→CTA, exactly as to be said>
SHOT LIST:   1) face hook  2) hands-on product  3) <real screenshot to grab>  ...
ON-SCREEN:   <text overlays + the timestamp each appears>
SFX:         <stamp on CAUGHT · counter-roll on the number · deflate+pop on −X% · etc. (visual-identity.md)>
OVERLAYS:    video/out/<slug>.mov  (drop at 0:NN, the moment the number is said)
B-ROLL:      <higgsfield file(s) or "none">  [AI-label ON]
CAPTIONS:    <platform caption text>         HASHTAGS: <4–6>
B-SIDE:      <Agent Opus brief, if a faceless variant is wanted; else "n/a">
GATES:       5/5 ✓ · claims ✓ · evidence-buckets ✓
```

## Step 7 — Hand off + log
Deliver the packets. The human films, assembles in Captions App, posts. You stop here.
**When each clip goes live, append a row to `docs/content/content-log.md`** (date · series · brand ·
product · change · platforms · hook · URL); backfill Views/Follows after a day or two. That log is
what Step 2 dedups against, and what the **every-~10-posts follows-driven review** reads to decide
what to double down on.
