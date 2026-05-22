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

// ─── Aggressive duplicate detection (Phase B+) ─────────────────────────
//
// The exact-slug pass above catches case + punctuation variants only.
// The medium tier (now retired — see git history of this file at PR #100)
// keyed on (brand, fuzzyNameKey) and reported size overlap as a hint —
// but Gatorade-class drift, where AI extraction produced wildly
// different names ("Bottle", "Gatorade Bottle", "Sports Drink",
// "Gatorade Beverage", …) for the same real product, slipped past the
// name gate. The aggressive tier inverts the contract: same brand
// AND identical published_changes size signature is the cluster key,
// and fuzzy name match becomes the green/amber HINT.
//
// Trade-off: this surfaces real product LINES (e.g. five Herbal
// Essences scents that all shrank from 400→275ml in the same
// announcement) alongside true duplicates. The admin must triage per
// group — the tool's job is to surface candidates, not auto-decide.
// The name-match hint helps them spot the easy wins at a glance.

export interface FuzzyDuplicateGroup {
  /** Composite key: brand + size signature. Stable across renders. */
  group_key: string;
  brand: string;
  /** The size signature that defines this group, e.g. "32→28fl oz".
   *  Displayed in the header. */
  size_signature: string;
  /** True when ≥2 members reduce to the same `fuzzyNameKey` — strong
   *  same-product signal. False = names diverge: could still be the
   *  same product (Gatorade case) OR a product LINE announcing a
   *  uniform shrink. UI flips green/amber on this flag. */
  has_fuzzy_name_match: boolean;
  /** ≥2 entities, sorted highest event_count first (merge target = [0]).
   *  `event_sizes` is every size signature seen on this entity (info
   *  only); `matched_sizes` is `[size_signature]` — the group-defining
   *  signature, kept as a singleton for UI back-compat with the chip
   *  renderer. */
  members: Array<EntityRow & { event_sizes: string[]; matched_sizes: string[] }>;
}

/**
 * Aggressive-tier fuzzy duplicate detector. Returns groups (≥2 members)
 * sharing BOTH:
 *   1. Same `brand` string (case-sensitive — brand-string drift is a
 *      separate concern handled by future canonicalization in
 *      `promote_claims.find_or_create_entity`).
 *   2. Same `published_changes` size signature
 *      (size_before, size_after, size_unit).
 *
 * The fuzzy name match is REPORTED (`has_fuzzy_name_match`) but not
 * REQUIRED — that's what lets us catch the Gatorade-class drift the
 * medium tier missed.
 *
 * An entity with N distinct size signatures appears in up to N groups
 * (one per signature). After merge, the source entity is retracted
 * and disappears from all subsequent groups on next page load.
 *
 * Result ordering: name-match groups first (highest confidence merge
 * candidates — looks like the same product AND same shrink), then by
 * member count descending within each tier.
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
  const entById = new Map<string, EntityRow>();
  for (const e of entities) entById.set(e.id, e);

  // Per-entity set of size signatures (for `event_sizes` info chip).
  const entSigs = new Map<string, Set<string>>();
  // Bucket (brand + "|" + signature) -> Set<entityId>.
  const buckets = new Map<string, Set<string>>();
  for (const ev of events) {
    if (!ev.entity_id) continue;
    const ent = entById.get(ev.entity_id);
    if (!ent || !ent.brand) continue;
    if (ev.size_before == null || ev.size_after == null) continue;
    const sig = sizeBucket(ev.size_before, ev.size_after, ev.size_unit);

    let sset = entSigs.get(ev.entity_id);
    if (!sset) { sset = new Set<string>(); entSigs.set(ev.entity_id, sset); }
    sset.add(sig);

    const key = ent.brand + "|" + sig;
    let bucket = buckets.get(key);
    if (!bucket) { bucket = new Set<string>(); buckets.set(key, bucket); }
    bucket.add(ev.entity_id);
  }

  const out: FuzzyDuplicateGroup[] = [];
  for (const [key, idSet] of buckets) {
    if (idSet.size < 2) continue;

    const sep = key.indexOf("|");
    const brand = key.slice(0, sep);
    const sig = key.slice(sep + 1);
    const members = [...idSet]
      .map((id) => entById.get(id)!)
      .filter(Boolean);

    // Name-match hint: ≥2 members reduce to the same fuzzy key.
    const nameKeyCounts = new Map<string, number>();
    for (const m of members) {
      const nk = fuzzyNameKey(m.canonical_name);
      if (!nk) continue;
      nameKeyCounts.set(nk, (nameKeyCounts.get(nk) ?? 0) + 1);
    }
    let hasNameMatch = false;
    for (const n of nameKeyCounts.values()) {
      if (n >= 2) { hasNameMatch = true; break; }
    }

    const sorted = [...members].sort((a, b) => {
      const cdiff = (b.event_count ?? 0) - (a.event_count ?? 0);
      if (cdiff !== 0) return cdiff;
      return a.id.localeCompare(b.id);
    });

    out.push({
      group_key: key,
      brand,
      size_signature: sig,
      has_fuzzy_name_match: hasNameMatch,
      members: sorted.map((m) => {
        const sigs = entSigs.get(m.id) ?? new Set<string>();
        return {
          ...m,
          event_sizes: [...sigs].sort(),
          matched_sizes: [sig],
        };
      }),
    });
  }

  // Name-match groups first (✓ green), then names-diverge groups (⚠ amber).
  // Within each tier: larger member count first (highest-leverage merges).
  return out.sort((a, b) => {
    if (a.has_fuzzy_name_match !== b.has_fuzzy_name_match) {
      return a.has_fuzzy_name_match ? -1 : 1;
    }
    return b.members.length - a.members.length;
  });
}
