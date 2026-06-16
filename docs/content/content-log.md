# FullCarts Content Log — what actually shipped

**The single source of truth for posted content.** The *batch* docs (`docs/content/batches/`) are the
*plan*; this log is what went **live**. The operator reads it at brief time to **avoid repeats**, and
its performance columns drive the follows-driven 10-post review.

## How it works
- **You** add a row every time you post (or tell the operator the URL and it logs it).
- **Dedup key = `brand + product + change`** (e.g. `Folgers · Coffee · 51→43.5oz`). The operator
  excludes any candidate already in this log as `posted`, so the same size-change is never reused.
  (A *different* change for the same brand is fine — that's a new episode, not a repeat.)
- **Angle reuse is allowed across brands; an exact datapoint is not.** If you want to re-feature a
  hot brand, use a *new* product/change or a genuinely new angle, and note it.
- Fill **Views / Follows** in a day or two after posting — that's the data for the iteration review.

## Schedule note
Update the banner counts + this log each batch. Review every ~10 posted rows by **Follows** (not
Views), find the outlier, and bias the next batch toward what won (hook? series? brand? feeling?).

---

## Log

| # | Posted | Series | Brand | Product | Change (dedup key) | Platforms | Hook (Snap one-liner) | URL | Views | Follows | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-06-16 | 5 Stealth Shrinks (carousel) | Multiple (coffee) | Ground coffee | Dunkin' · Peet's · Community · Eight O'Clock · Folgers 11.3→9.6oz (−15%) | TBD | "5 coffee cans that quietly got smaller 👀 swipe →" | _link_ | — | — | First real post. Photo-forward `Carousel` from `coffee-5-carousel.json`. All 5 coffee datapoints now USED — exclude from future carousels. Fill Platforms/URL/Views/Follows when known. |
| 2 | 2026-06-16 | Caught: | Folgers | Coffee | 51→43.5oz (−14.7%) | TBD | "blamed record prices… coffee crashed 40%, your can never came back" | _link_ | — | — | Hero episode. Per-oz 22¢→59.5¢; real coffee-chart screenshot. Datapoint USED. Fill Platforms/URL/Views/Follows. |
| 3 | 2026-06-16 | The Take (Newsjack) | Multiple | CPI / Chobani Flips | Food-at-home +3.2%, dairy +6.1% YoY; Chobani Flips 5.3→4.5oz (−15.1%) proof | TBD | "groceries 'only' up 3.2% — that number is lying to you" | _link_ | — | — | CPI newsjack (Clip 2, 06-10 batch). Real FRED screenshot. Chobani Flips datapoint USED. Fill Platforms/URL/Views/Follows. |
| 4 | 2026-06-16 | The Take (Opinion) | — | "Share size" packaging | n/a (angle, not a single datapoint) | TBD | "'sharing size' is a lie — it's the same shrink with a friendlier label" | _link_ | — | — | Opinion/commentary piece. No single dedup datapoint — angle is reusable but don't repeat the exact bit. Fill Platforms/URL/Views/Follows. |

> Keep rows append-only; don't overwrite history (the audit trail is the point).

## Quick dedup check (optional cross-check against the DB)
The log is the authority for *what you posted*. To sanity-check you're not about to repeat, the
operator scans this table for the candidate's `brand + product + change` before adding it to a brief.
