// Pure grouping logic for the duplicate-entity batch-merge admin page.
//
// Mirrors the SQL profiler (pipeline/scripts/profile_matched_claims.py)
// so admins can run the same analysis live in-browser, then act on it
// without leaving the page.

import { fuzzyNameKey, sizeBucket } from "@/app/admin/claims/groups/lib";

export interface EntityRow {
  id: string;
  brand: string;
  canonical_name: string;
  image_url: string | null;
  category: string | null;
  created_at: string;
  event_count: number;
}

export interface MergePair {
  source: EntityRow;
  target: EntityRow;
  /** Number of other rows in the same collision group, including target.
   *  > 2 means three or more entities share the slug (e.g. M&M's case
   *  variants). Useful sort/triage signal. */
  group_size: number;
  /** Same `(brand, slug)` key that grouped them. */
  group_key: string;
}

/** Aggressive case+punctuation strip — `Wheat Thins` and `wheat-thins`
 *  both become `wheatthins`. */
export function slugify(name: string): string {
  return name.toLowerCase().trim().replace(/[^a-z0-9]+/g, "");
}

/** Group by `(brand, slug(canonical_name))`, emit one `MergePair` per
 *  non-target entity in each group. Target = highest event_count in the
 *  group (deterministic tie-breaker: lexicographic id). */
export function findDuplicatePairs(entities: EntityRow[]): MergePair[] {
  const groups = new Map<string, EntityRow[]>();
  for (const ent of entities) {
    const brandNorm = (ent.brand ?? "").toLowerCase().trim();
    const slug = slugify(ent.canonical_name ?? "");
    if (!brandNorm || !slug) continue;
    const key = `${brandNorm}::${slug}`;
    const bucket = groups.get(key);
    if (bucket) bucket.push(ent);
    else groups.set(key, [ent]);
  }

  const pairs: MergePair[] = [];
  for (const [key, members] of groups) {
    if (members.length < 2) continue;
    const ranked = [...members].sort((a, b) => {
      const cdiff = (b.event_count ?? 0) - (a.event_count ?? 0);
      if (cdiff !== 0) return cdiff;
      return a.id.localeCompare(b.id);
    });
    const target = ranked[0];
    for (const source of ranked.slice(1)) {
      pairs.push({ source, target, group_size: members.length, group_key: key });
    }
  }

  // Sort: largest groups first (3+ variants), then by target event count
  // (touching a target with more events has more downstream impact).
  pairs.sort((a, b) => {
    if (b.group_size !== a.group_size) return b.group_size - a.group_size;
    return (b.target.event_count ?? 0) - (a.target.event_count ?? 0);
  });

  return pairs;
}

// ─── Fuzzy duplicate detection (Phase B) ──────────────────────────────
//
// The exact-slug pass above catches case + punctuation variants only.
// Real-world dupes drift further: "Gatorade Glacier Freeze",
// "Gatorade Frost Glacier Freeze", "Gatorade Zero Glacier Freeze" all
// collapse under `fuzzyNameKey`. We keep the noise floor low by also
// requiring a SHARED published-changes size signature — the strongest
// signal that two entities describe the same real product.

/** Per-entity event size signatures (e.g. "200g→180g"). Helper for
 *  the fuzzy matcher; kept module-private to mirror the Phase A grouper. */
function entityEventSignatures(
  entityId: string,
  events: Array<{
    entity_id: string | null;
    size_before: number | null;
    size_after: number | null;
    size_unit: string | null;
  }>,
): Set<string> {
  const out = new Set<string>();
  for (const e of events) {
    if (e.entity_id !== entityId) continue;
    if (e.size_before == null || e.size_after == null) continue;
    out.add(sizeBucket(e.size_before, e.size_after, e.size_unit));
  }
  return out;
}

export interface FuzzyDuplicateGroup {
  /** Composite key: brand + fuzzy name key. Stable across renders. */
  group_key: string;
  brand: string;
  /** Normalised name key — useful for diagnostics / display. */
  shared_name_key: string;
  /** True when at least one (size_before, size_after, size_unit) signature
   *  is shared by ≥2 members. Strong "same product" signal — the UI
   *  highlights these groups as safe to merge. False groups still surface
   *  but flag the admin to double-check sizes before merging. */
  has_size_overlap: boolean;
  /** ≥2 entities, sorted highest event_count first (merge target = [0]).
   *  `event_sizes` is every size signature seen on this entity;
   *  `matched_sizes` is the subset shared with ≥1 other group member
   *  (empty array when has_size_overlap is false). */
  members: Array<EntityRow & { event_sizes: string[]; matched_sizes: string[] }>;
}

/**
 * Medium-tier fuzzy duplicate detector. Returns groups (≥2 members)
 * where BOTH:
 *   1. Same `brand` string (case-sensitive — Phase B's aggressive tier
 *      handles brand-string drift separately).
 *   2. Same `fuzzyNameKey(canonical_name)` (token-sort + strip
 *      size/unit/punct).
 *
 * Size overlap is REPORTED (via `has_size_overlap`) but not REQUIRED —
 * the founder can see at a glance which groups are safe to merge
 * (size overlap = very likely same product) vs which need a manual
 * size check (no overlap = could be different size variants of the
 * same product line).
 *
 * Result ordering: size-overlap groups first (highest signal), then by
 * member count descending.
 */
export function findFuzzyDuplicateGroups(
  entities: EntityRow[],
  events: Array<{
    entity_id: string | null;
    size_before: number | null;
    size_after: number | null;
    size_unit: string | null;
  }>,
): FuzzyDuplicateGroup[] {
  // Bucket by (brand, fuzzyNameKey(canonical_name)).
  const buckets = new Map<string, EntityRow[]>();
  for (const e of entities) {
    if (!e.brand) continue;
    const nk = fuzzyNameKey(e.canonical_name);
    if (!nk) continue;
    const key = e.brand + "|" + nk;
    const list = buckets.get(key);
    if (list) list.push(e);
    else buckets.set(key, [e]);
  }

  const out: FuzzyDuplicateGroup[] = [];
  for (const [key, members] of buckets) {
    if (members.length < 2) continue;

    // Compute per-member size signatures.
    const sigs = new Map<string, Set<string>>();
    for (const m of members) sigs.set(m.id, entityEventSignatures(m.id, events));

    // Compute overlap (sizes appearing on ≥2 members). Reported via
    // has_size_overlap but no longer required — Medium tier surfaces all
    // same-brand+same-fuzzy-name groups and lets the founder decide.
    const sizeOccurrence = new Map<string, number>();
    for (const sig of sigs.values()) {
      for (const s of sig) sizeOccurrence.set(s, (sizeOccurrence.get(s) ?? 0) + 1);
    }
    const overlapSizes = new Set<string>();
    for (const [s, n] of sizeOccurrence) if (n >= 2) overlapSizes.add(s);

    // Highest event_count first (target = members[0]). Lex id tie-break
    // to match the exact-matcher's deterministic ordering.
    const sorted = [...members].sort((a, b) => {
      const cdiff = (b.event_count ?? 0) - (a.event_count ?? 0);
      if (cdiff !== 0) return cdiff;
      return a.id.localeCompare(b.id);
    });
    const [brand, sharedNameKey] = key.split("|");
    out.push({
      group_key: key,
      brand,
      shared_name_key: sharedNameKey,
      has_size_overlap: overlapSizes.size > 0,
      members: sorted.map((m) => {
        const sig = sigs.get(m.id) ?? new Set<string>();
        return {
          ...m,
          event_sizes: [...sig].sort(),
          matched_sizes: [...sig].filter((s) => overlapSizes.has(s)).sort(),
        };
      }),
    });
  }
  // Size-overlap groups float to top (highest confidence merge candidates),
  // then larger groups before smaller ones within each tier.
  return out.sort((a, b) => {
    if (a.has_size_overlap !== b.has_size_overlap) return a.has_size_overlap ? -1 : 1;
    return b.members.length - a.members.length;
  });
}
