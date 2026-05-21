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
  /** ≥2 entities, sorted highest event_count first (merge target = [0]).
   *  `event_sizes` is every size signature seen on this entity;
   *  `matched_sizes` is the subset that's shared with ≥1 other group member. */
  members: Array<EntityRow & { event_sizes: string[]; matched_sizes: string[] }>;
}

/**
 * Conservative fuzzy duplicate detector. Returns groups (≥2 members)
 * where ALL of the following hold:
 *   1. Same `brand` string (case-sensitive — Phase B's aggressive tier
 *      handles brand-string drift separately).
 *   2. Same `fuzzyNameKey(canonical_name)` (token-sort + strip
 *      size/unit/punct).
 *   3. At least one `(size_before, size_after, size_unit)` signature
 *      appears on ≥2 members in the group.
 *
 * Result ordering: most-members-first (largest dedup payoff up top).
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

    // Size-overlap requirement: any signature appearing on ≥2 members
    // counts as an overlap. Drop the group if none.
    const sizeOccurrence = new Map<string, number>();
    for (const sig of sigs.values()) {
      for (const s of sig) sizeOccurrence.set(s, (sizeOccurrence.get(s) ?? 0) + 1);
    }
    const overlapSizes = new Set<string>();
    for (const [s, n] of sizeOccurrence) if (n >= 2) overlapSizes.add(s);
    if (overlapSizes.size === 0) continue;

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
  // Largest groups first — most dedup payoff at the top.
  return out.sort((a, b) => b.members.length - a.members.length);
}
