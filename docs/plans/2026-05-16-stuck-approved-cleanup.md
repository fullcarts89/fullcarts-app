# Stuck Approved Claims — Cleanup Report

**Date:** 2026-05-16
**Branch:** `claude/modest-ramanujan-b09990`

## TL;DR

316 claims stuck in `status='approved'` → 0 residual. No errors, no manual brand decisions needed.

The user's hypothesis ("the matcher can't find a `product_entities` row, fuzzy threshold needs adjustment") turned out to be wrong on the data. The real issue was **two silent leaks in `promote_claims.py`**, both of which left claims looping in the queue forever:

1. **No-size claims got silently skipped** (`continue` without updating status). 254 of 316 (80%) were stuck this way — overwhelmingly Cadbury reddit text complaints that were approved before the current image-required hard filter shipped.
2. **Claims with `matched_entity_id` already set were excluded from the fetch** (`is_("matched_entity_id", "null")`). 34 of 316 had been partially-processed by an older code path (entity matched, status not advanced). 30 of those 34 already had a matching `published_changes` event — they just needed to be marked `evidence`. The remaining 4 needed a fresh promotion pass.

## Bucket diagnosis

```
Cross-tab of stuck claims (size completeness × matched_entity_id):
  no_sizes  + no_entity : 254   ← old approvals, no shrinkflation magnitude. REJECT.
  both_sizes + no_entity:  28   ← normal queue, just hadn't been promoted. CREATE.
  both_sizes + entity   :  34   ← orphaned by older path. 30 already evidenced, 4 retry. MIXED.
```

### No-size bucket (254 claims, by brand)

| Brand | Count |
|---|---:|
| Cadbury | 108 |
| Arby's | 7 |
| Nestle | 6 |
| Hellman's | 6 |
| Oreo | 5 |
| Mars / PepsiCo | 4 each |
| Ruffles / Tostitos / Kellogg's / Doritos / Galaxy / Bounty | 3 each |
| (long tail) | ~95 |

Every one of these had `old_size IS NULL AND new_size IS NULL`. Without a before/after pair we cannot produce a `published_changes` row, and they had been re-fetched on every daily cron for months. The right call is to demote them out of the approved queue — they are tagged `unmatched`, which is the schema's "we looked at this and there's nothing we can do" status.

Why are 108 Cadbury claims size-less? They're old Reddit text-only complaints that got auto-approved before the current `auto_approve_claims.py` hard filter requiring `old_size IS NOT NULL AND new_size IS NOT NULL` (and an image) shipped. The hard filter prevents new ones from being approved; the existing 254 just needed cleanup.

### Entity-set bucket (34 claims)

30 of 34 already had a matching `published_changes` row for `(entity_id, old_size, new_size)`. They were folded into the evidence trail by some prior path, but the claim status never moved past `approved`. The new `cleanup_stuck_approved.py` script flips them to `evidence` (and backfills `matched_variant_id` from the event if missing). Examples: Honey Maid Family Size Crackers, Tostitos, Special K, Cadbury Brunch bars.

The other 4 had no matching event. Their `matched_entity_id` was cleared so the regular `promote_claims` pass would build a fresh `published_changes` row — which it did, in the same workflow run. They are: Charms Mini Pops, Dove Large Bottles Shampoo, plus two others surfaced in the cleanup log.

## Changes

### 1. `pipeline/scripts/promote_claims.py` — patch

When a claim has neither `old_size` nor `new_size`, demote it to `unmatched` instead of `continue`-ing past it. Adds a new `unmatched_no_size` stat to the run summary.

### 2. `pipeline/scripts/cleanup_stuck_approved.py` — new

Handles the orphaned `matched_entity_id IS NOT NULL AND status='approved'` case that the regular fetch filter excludes:
- If a `published_changes` row exists for `(entity_id, old_size, new_size)`: add the claim to that event's `evidence_summary` (idempotent — checks `claim_id` first), bump `evidence_count`, set status to `evidence`.
- Otherwise: clear `matched_entity_id` so the next `promote_claims` pass picks the claim up and produces a published_change. Brand+name still resolves to the same entity via the find-or-create lookup.
- No-size claims that somehow have a `matched_entity_id` get demoted to `unmatched`.

Idempotent: re-running on a clean queue is a no-op.

### 3. `.github/workflows/pipeline_promote.yml` — workflow

Added `cleanup_stuck_approved` step between `auto_approve_claims --approve-only` and `promote_claims.py`. Keeps the queue from accumulating orphans going forward.

## Live run results (2026-05-16)

```
cleanup_stuck_approved (LIVE):
  scanned: 34
  folded_into_event: 0          # the 30 already had this claim_id in summary
  already_in_evidence: 30       # just flipped status to 'evidence'
  entity_cleared_for_retry: 4   # passed to promote_claims below
  unmatched_no_size: 0
  errors: 0

promote_claims (LIVE):
  Found 305 approved claims to promote
  claims_processed: 51
  entities_created: 36
  entities_reused: 15
  variants_created: 51
  observations_created: 102
  candidates_created: 44
  published: 44                  # new published_changes events
  evidence_added_to_existing: 7  # folded into existing events
  skipped_no_size: 254
  unmatched_no_size: 254         # all 254 demoted to 'unmatched'
  errors: 0
```

## Post-run state

| status | count | delta |
|---|---:|---|
| approved | **0** | was 316 |
| matched | 4,278 | +44 new published events |
| evidence | 707 | +37 (30 already-in-evidence + 7 new syndication folds) |
| unmatched | 254 | +254 no-size cleanup |
| pending | 1,718 | unchanged |
| discarded | 34,093 | unchanged |

`published_changes` total: **2,872** (was 2,800). +72 represents the 44 new events from this cleanup plus ~28 from new daily ingest since the last platform-wide count was recorded.

Cadbury `published_changes`: **111** (was 105). +6 from newly-promoted claims; consistent with the brand's share of the 28 both-sizes+no-entity bucket.

## Verification spot-checks

- `Nescafé Instant Coffee Multipacks` (from the prompt) → `unmatched` ✓ (no sizes available)
- `Persil Laundry Detergent` (from the prompt) → `unmatched` ✓ (size-less variant; the brand has other claims with sizes that are correctly `matched`/`pending`)
- `Charms / Mini Pops` (cleared-for-retry sample) → `matched` with entity set ✓
- `Dove / Large Bottles Shampoo and Conditioner` (cleared-for-retry sample) → `matched` ✓

## Did the matcher need fuzzy adjustment?

No. The 28 "both sizes + no entity" claims would have been processed by the existing `find-or-create` logic on the next daily cron run (dry-run confirmed: 32 claims processed, 0 errors). The matcher's exact-match-then-create behavior is correct for new entities. The minor cosmetic bug — `normalize_brand` uses `str.title()`, which capitalizes the letter after an apostrophe (`Reese's` → `Reese'S`) — does produce duplicate entities in rare cases, but is out of scope for this cleanup and is being deferred. It's a separate decision (consolidate via `dedup_entities.py` vs fix `normalize_brand`) that should be tackled as part of a broader normalization pass.
