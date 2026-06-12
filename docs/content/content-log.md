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
| _ex_ | 2026-06-12 | Caught: | Folgers | Coffee | 51→43.5oz (−14.7%) | TT/RE/SH | "blamed record prices… coffee crashed 40%, your can never came back" | _link_ | — | — | debut · coffee-chart real screenshot |

> Delete the `_ex_` example row once your first real post is logged. Keep rows append-only;
> don't overwrite history (the audit trail is the point).

## Quick dedup check (optional cross-check against the DB)
The log is the authority for *what you posted*. To sanity-check you're not about to repeat, the
operator scans this table for the candidate's `brand + product + change` before adding it to a brief.
