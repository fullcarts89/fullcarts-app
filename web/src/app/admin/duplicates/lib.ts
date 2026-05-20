// Pure grouping logic for the duplicate-entity batch-merge admin page.
//
// Mirrors the SQL profiler (pipeline/scripts/profile_matched_claims.py)
// so admins can run the same analysis live in-browser, then act on it
// without leaving the page.

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
