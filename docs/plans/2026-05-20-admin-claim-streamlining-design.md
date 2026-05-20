# Phase A — Admin claim-review streamlining + zero-event entity cleanup

**Date:** 2026-05-20
**Status:** Approved design, ready for implementation plan
**Predecessors:** Phase 2D (admin entity tooling, PR #75/#87/#88/#91/#92/#93/#94/#95)
**Successor:** Phase B (forward data-quality detectors — separate phase)

## The rule that drives everything

> **No entity, brand, or page on the public site may exist without at least one non-retracted `published_changes` event backing it.**
>
> If the last live event of an entity is retracted, the entity is retracted in the same transaction.
> If a brand's last live entity is retracted, the brand falls off all aggregates and its `/brands/[name]` page returns 404.
> No exceptions, no grace periods, no soft variants.

Everything in this phase derives from this single invariant.

## Why now

The Quality Street Tin case (entity `e6d6e92e-aef8-4ddb-b2d1-e2fcd07284ee`, surfaced on 2026-05-20) showed the gap. The entity had:

- One `published_changes` row: `2.5kg → 0.6kg`, auto-retracted by migration 061's sanity guards (unit-parse error).
- One still-attached `matched` claim.
- `product_entities.is_retracted=false`.

Result: the `/products/[entity]` page rendered with no clickable evidence because `event_evidence_summary` correctly filters retracted events. Users arriving via a direct link saw an empty shell.

**Platform-wide scale (queried 2026-05-20):**

| Counter | Value |
|---|---|
| Active (non-retracted) `product_entities` | 20,872 |
| Entities with at least one live event | 2,306 |
| **Active entities that render empty `/products/[id]` pages** | **~18,566 (89%)** |

`product_index` correctly hides these from `/products`, but any direct link (related-products rail, share, search result, manual URL, old bookmark) still resolves to the empty page.

A second, related problem: the founder's `/admin/claims` pending queue is at 2,527 (up from ~1,735 because the data-quality-flags marathon dumped ~792 back to pending). Single-card review of 2,527 claims is impractical. Most pending claims are duplicates of each other by `(brand, product_name, size_change)` and could be approved or discarded in bulk.

## Three deliverables in implementation order

### Deliverable 1 — Admin claim-grouping tool (ship FIRST)

New route `/admin/claims/groups`, linked from the existing `/admin/claims?status=pending` header as "View as groups (N clusters)".

**Why ship first:** Deliverable 2 will retract ~18,566 entities, which cascade-detaches their matched claims back to `pending`. Without the grouping tool ready, the queue could 5–20× and the founder would be reviewing it single-card. Grouping tool comes online before the cleanup runs.

**Grouping key (server-side, in-memory):**
```
group_key = (
  normalize_brand(claim.brand),         # lowercase, trim, strip suffixes (" plc", " inc", " ltd")
  fuzzy_name_key(claim.product_name),   # token-sorted, strip size/qty noise (numbers + units)
  size_bucket(old_size, new_size, unit) # canonical "200g→180g" with normalized units
)
```

If `claim.matched_entity_id` is non-null, sub-cluster within group by entity (so already-matched claims for the same entity stay together regardless of brand-string drift like "Cadbury" vs "Cadbury UK").

**Group card UI** (visual pattern: `/admin/duplicates` and `/admin/quality-flags`):

- Header: `Cadbury · Dairy Milk · 200g → 180g · 12 claims`
- Representative claim card (image + title + extracted fields), styled like existing `/admin/claims` cards
- "Show all 12" toggle expanding to the full list (mini cards stacked)
- Per-group bulk actions:
  - **Approve all** — flips every claim in the group to `matched`, sets `matched_entity_id` if a single entity dominates
  - **Discard all** — flips every claim to `discarded`
  - **Merge into existing entity →** — entity-picker (fuzzy match by brand + name), then sets `matched_entity_id` on all and approves
  - **Edit shared fields then approve all** — single inline form (brand / product_name / category) writes to every claim in the group, then approves
- Sticky bottom toolbar: "Select N groups" + cross-group bulk action

**Out of scope for this deliverable:**
- Embedding-based semantic grouping (heuristic should catch 80%+; revisit only if it fails in practice)
- Re-creating entities mid-review (existing `/admin/entities` flow handles that)

**Performance budget:** 2,527 pending claims fits comfortably in memory in the server component. No new DB indexes. Sort groups by `count DESC` so the largest clusters appear first.

### Deliverable 2 — Cleanup pass (ship SECOND, one-shot script)

`pipeline/scripts/retract_zero_event_entities.py` (idempotent, dry-run capable).

**Algorithm:**
1. SELECT every `product_entities` row where `is_retracted=false` AND no `published_changes` row exists with `entity_id=entities.id` AND `is_retracted=false`. Expected: ~18,566.
2. For each, call `set_entity_retracted(entity_id)` RPC. This RPC (from migration 062) cascades the retraction to attached `published_changes` rows and flips associated `matched` claims back to `status='pending'` per the existing cascade behaviour.
3. Write a `data_quality_flags` row per retract: `flag_kind='zero_event_entity_swept'`, `severity='info'`, `resolved_at=NOW()` (already resolved at creation — this is audit trail, not a queue entry).
4. Output a markdown summary suitable for GitHub Actions job output: total swept, breakdown by brand, top 20 affected brands by entity count.

**Safety:**
- `--dry-run` flag prints what would be retracted without writing
- `--limit N` flag for incremental rollout
- All writes go through `set_entity_retracted` so the existing audit trail in `entity_edit_log` captures every retraction with reason `bulk_zero_event_sweep`

**Reversibility:**
- Per-entity via `/admin/entities` "untoggle retract" button
- Bulk via a one-shot `restore_zero_event_entities_v1.py` script that filters `entity_edit_log` for `reason='bulk_zero_event_sweep'` and reverses each — built only if needed

### Deliverable 3 — Forward invariant (ship THIRD, DB trigger + page guards)

Belt-and-braces: trigger at the DB layer, guard at the page layer. Each catches the case the other misses.

**DB layer — migration 069:**
```sql
CREATE OR REPLACE FUNCTION trg_retract_orphaned_entity()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.is_retracted = true AND OLD.is_retracted = false THEN
    IF NOT EXISTS (
      SELECT 1 FROM published_changes
      WHERE entity_id = NEW.entity_id
        AND is_retracted = false
        AND id != NEW.id
    ) THEN
      PERFORM set_entity_retracted(NEW.entity_id);
    END IF;
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER published_changes_orphan_check
AFTER UPDATE OF is_retracted ON published_changes
FOR EACH ROW EXECUTE FUNCTION trg_retract_orphaned_entity();
```

**Page layer:**
- `web/src/app/products/[id]/page.tsx`: early `notFound()` if `event_evidence_summary` returns zero rows for `entity_id`
- `web/src/app/brands/[name]/page.tsx`: early `notFound()` if `brand_index` returns zero rows for `brand` (already excludes retracted entities — the guard is mostly belt for if brand_index ever changes)

**Why both layers:** The trigger is atomic and catches every future retraction. The page guard catches any legacy state, any view/index drift, and any future code path that creates an entity-without-event. Belt-and-braces is cheap here — both are <10 lines of code.

## Sequencing rationale

1. Grouping tool first → founder has a usable review surface before the queue explodes
2. Cleanup script second → with grouping tool live, the post-cleanup queue boom is manageable
3. Forward invariant third → trigger goes in once we know cleanup math is right (so we don't trigger-loop during cleanup)

## Out of scope (deferred)

- **Embedding-based semantic grouping** — heuristic version first, revisit only if it misses too much
- **Forward data-quality detectors beyond `zero_event_entity_swept`** — Phase B (cross-brand-fragmentation detector, stuck-matched-claim detector, etc.)
- **Brand canonicalization in `promote_claims.find_or_create_entity`** — separate cleanup, prevents future case-variant duplicates at insert time
- **Embedding-based duplicate-entity detection** — `/admin/duplicates` (PR #91) is heuristic-only; semantic upgrade is its own phase
- **Cross-brand consolidation** (Wheat Thins under 6 brand strings) — needs Wikidata work from Phase 2C
- **Re-deriving public surfaces to ensure they filter on `has_live_events`** — the cleanup retracts the underlying entities, so existing surfaces auto-filter via `is_retracted=false`. If an audit reveals a surface that bypasses this, it's its own bug, not Phase A scope.

## Risks

1. **Cleanup unparking ~10–20k claims into pending** — addressed by ship order (grouping tool first).
2. **DB trigger correctness** — recovery is per-entity via `/admin/entities`. Mitigation: ship after running cleanup script in `--dry-run` against full DB and reviewing output.
3. **404s breaking external links** — acceptable cost. Pages were empty anyway. If anyone bookmarked an empty page, they were already seeing nothing useful.
4. **ISR cache staleness post-cleanup** — Vercel ISR is 1h on most routes. Worst case: an hour of stale empty-page renders before next request. Can be force-busted by hitting `/api/revalidate` if it exists, otherwise wait.
5. **Grouping heuristic false negatives** — e.g., "Cadbury Dairy Milk 200g" and "Cadbury Dairy Milk Chocolate Bar 200g" might end up in different groups due to name-token differences. Founder can still bulk-action each group separately; just less efficient than ideal. Embedding upgrade is the answer if this becomes a real pain point.

## Success criteria

- `/admin/claims/groups` exists, groups the current 2,527 pending claims into <500 clusters, founder can bulk-action a group in <5 seconds
- After cleanup: `event_evidence_summary` count ≈ count of active entities (within ~50)
- After cleanup: 100% of `/products/[id]` pages return either 200-with-content or 404, never 200-with-empty
- DB trigger fires correctly: retracting the last event of an entity (in a test or via `/admin/quality-flags` resolve) cascades to retracting the entity itself
- The founder reviews and clears the post-cleanup pending queue in ≤4 hours (vs. estimated 8 hours single-card)

## Implementation plan

To be created next via the `writing-plans` skill. Will break into concrete task list with file paths, migration numbers, test plan, and rollout order.
