# Aggressive dedupe tier — invert the clustering key

**Date:** 2026-05-22
**Context:** Phase B medium tier (PR #100) surfaced 8 same-brand+same-fuzzy-name groups. Founder reviewed prod and noted Gatorade — visibly fragmented across many AI-extracted canonical names — was not in the list.

## The diagnosis

Medium tier requires `(brand, fuzzyNameKey(canonical_name))` to match across two entities, and reports a `has_size_overlap` flag as a hint. The Gatorade case fails this gate because the AI extraction produced names that diverge under `fuzzyNameKey`:

| Canonical name | fuzzy key |
|---|---|
| Bottle | `bottle` |
| Gatorade Bottle | `bottle gatorade` |
| Gatorade Bottles | `bottles gatorade` |
| Gatorade Sports Drink | `drink gatorade sports` |
| Sports Drink | `drink sports` |
| Sports Drink Bottle | `bottle drink sports` |
| Gatorade Beverage | `beverage gatorade` |

Six of these seven entities all carry the exact same `published_changes` event: `32fl oz → 28fl oz`. The size signature is the strongest "same product" signal we have — it's literally the news the entity exists to record — but the current tier blocks the merge because it gates on the noisier name signal.

## Catalog-wide impact of inverting the key

Running `(brand, size_before, size_after, size_unit)` as the clustering key across all 2,208 active entities and 2,363 live events surfaces:

- **181 signatures shared by ≥2 active entities**
- **466 entities implicated** (~21% of the active catalog)

Top of the list (truncated):

| Brand | Size change | Entities |
|---|---|---|
| Kleenex | 65 → 60 ct | 9 |
| Milky Way | 11.24 → 10.65 oz | 9 |
| Gatorade | 32 → 28 fl oz | 7 |
| Kraft | 475 → 425 ml | 6 |
| Crest | 4.1 → 3.8 oz | 6 |
| Charmin | 264 → 244 ct | 6 |
| Cadbury | 200 → 180 g | 5 |
| Lurpak | 250 → 200 g | 5 |
| Domino's | 10 → 8 ct | 5 |
| Herbal Essences | 400 → 275 ml | 5 |

Some groups are genuinely the same product (Kleenex small box, Gatorade 32oz bottle, Cadbury sharing bar). Some are a product *line* announcing a uniform shrink (Herbal Essences across 5 scents; Quaker oatmeal across flavors) where the entities are correctly distinct. The admin must triage per group; the tool's job is to surface candidates, not auto-decide.

## The design

**Replace the medium tier**, not extend it. The new tier strictly dominates the old:
- Every (brand, exact size signature) group with ≥2 members is a candidate the medium tier could not surface unless the names also fuzzy-matched.
- The few medium-tier candidates that had no size overlap (the amber rows) were always lower-confidence than the new tier's name-converging cases.

### Clustering contract change

| | Old (medium) | New (aggressive) |
|---|---|---|
| Group key | `(brand, fuzzyNameKey)` | `(brand, size_before, size_after, size_unit)` |
| Reported hint | `has_size_overlap` (✓ size match / ⚠ no size overlap) | `has_fuzzy_name_match` (✓ name match / ⚠ names diverge) |
| Default sort | ✓ size-match groups first | ✓ name-match groups first |

### Entities can appear in multiple groups now

With the old key, an entity had one fuzzy name and so appeared in one group. With size signatures as keys, an entity with two events at different size signatures (e.g. Gatorade Sports Drink: `32→28fl oz` AND `20→16.9fl oz`) will appear in two groups. That's correct: each size signature is a separate merge decision. After the admin merges within one group, the entity row remains in the other group, now with one fewer event.

### What stays unchanged

- The exact-slug section at the top of `/admin/duplicates` (PR #91).
- The merge mechanism (`mergePair` server action → `merge_entities` RPC → `entity_merge_log`).
- The default target rule (highest event_count, lex id tie-break) and the per-group radio override.
- The page-level data load (`page.tsx` already pulls events + entities).
- The CSS / row layout. Only the header copy changes.

## Implementation surface

| File | Change |
|---|---|
| `web/src/app/admin/duplicates/lib.ts` | Rewrite `findFuzzyDuplicateGroups` body. Rename `has_size_overlap` → `has_fuzzy_name_match`, `shared_name_key` → `size_signature`. Add `event_sizes` and `matched_sizes` arrays per member (kept for backwards UI compatibility — `matched_sizes` is now always equal to `[size_signature]` since the size IS the group key). |
| `web/src/app/admin/duplicates/FuzzyDuplicatesClient.tsx` | Update group header. Display: brand · size_signature · N entities · (✓ name match / ⚠ names diverge). |
| `web/src/app/admin/duplicates/page.tsx` | Update subtitle + stat label copy. |
| `web/src/app/admin/duplicates/__tests__/lib.test.ts` | Replace medium-tier tests with new aggressive-tier tests. Cover: Gatorade case (same size, divergent names) → 1 group ⚠; product-line case (same fuzzy name, different sizes) → multiple groups, name-match ✓; an entity with two distinct size events appearing in two groups. |

## YAGNI list (not building this round)

- Stop-word stripping in `fuzzyNameKey` (option 2 in the question, founder declined). The name signal is now an admin hint, not a gate, so it doesn't need to be perfect.
- Lemmatization for plural/singular collapse.
- A bulk "merge all in group" button. Per-row radio + per-row merge is sufficient for 181 groups; we can revisit if review time exceeds an hour.
- Promoting this clustering logic into the `promote_claims` insertion path (preventing future duplicates at write time). Worth doing eventually, but a separate change.

## Verification plan

- Unit tests cover the three core scenarios.
- `pnpm tsc --noEmit` clean.
- Local dev server: navigate `/admin/duplicates`, confirm the new section shows ~181 groups with Gatorade `32→28fl oz` visible near the top of the name-match ✓ section.
- Spot-check one merge end-to-end on a low-stakes group before mass review.

## Rollout

- Single PR. No DB migration. No env or secret change.
- Vercel preview link to the founder for visual confirmation, then merge → prod deploy via the documented CLI invocation.
- Founder then works through the 181-group triage queue using the live tool.
