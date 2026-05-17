/** Aggregators and formatters used by both server- and client-rendered
 *  sections of the brand page. Everything here is pure: input data
 *  in, derived shape out, no side effects. */
import type { EventRow, ProductEntity, ProductRollup, EventSource } from "./types";

const STORAGE_BUCKET_URL =
  (process.env.NEXT_PUBLIC_SUPABASE_URL || "") +
  "/storage/v1/object/public/claim-images/";

export function num(s: string | number | null | undefined): number {
  if (s == null) return 0;
  const n = typeof s === "string" ? parseFloat(s) : s;
  return Number.isFinite(n) ? n : 0;
}

export function pctLabel(n: number): string {
  if (n === 0) return "—";
  return `${n.toFixed(1)}%`;
}

/** "2023-06-15" — strip the time component if any. */
export function isoDay(s: string | null | undefined): string {
  if (!s) return "";
  return s.slice(0, 10);
}

/** Build the public storage URL for a claim-archived image. */
export function claimImageUrl(storagePath: string | null | undefined): string | null {
  if (!storagePath) return null;
  return STORAGE_BUCKET_URL + storagePath;
}

/** Pick the first usable image for an event, in priority order:
 *  1. Any source's archived Reddit image (highest curation quality)
 *  2. Any source's article hero image (GDELT socialimage)
 *  3. null — caller can fall back to entity.image_url */
export function leadImageFromSources(sources: EventSource[]): {
  url: string | null;
  source_type: string | null;
} {
  for (const s of sources) {
    const claimUrl = claimImageUrl(s.claim_image_path);
    if (claimUrl) return { url: claimUrl, source_type: s.source_type };
  }
  for (const s of sources) {
    if (s.image) return { url: s.image, source_type: s.source_type };
  }
  return { url: null, source_type: null };
}

/** Domain → human-readable publisher name, for the per-source row.
 *  Falls back to capitalising the host's first label. */
export function publisherLabel(s: EventSource): string {
  if (s.publisher) return s.publisher;
  const host = s.domain || "";
  if (!host) return "Unknown";
  const first = host.split(".")[0] || host;
  return first.charAt(0).toUpperCase() + first.slice(1);
}

/** Group events by year for the timeline. Fills zero-event years
 *  between firstDetected and last so the chart has a continuous axis. */
export function timelineBuckets(
  events: EventRow[],
  firstDetected: string,
  lastDetected: string,
): { year: number; count: number }[] {
  const counts = new Map<number, number>();
  for (const e of events) {
    const y = parseInt(isoDay(e.observed_date).slice(0, 4), 10);
    if (!Number.isFinite(y)) continue;
    counts.set(y, (counts.get(y) || 0) + 1);
  }
  const startYear = parseInt(firstDetected.slice(0, 4), 10);
  const endYear = parseInt(lastDetected.slice(0, 4), 10);
  if (!Number.isFinite(startYear) || !Number.isFinite(endYear)) return [];

  const out: { year: number; count: number }[] = [];
  for (let y = startYear; y <= endYear; y++) {
    out.push({ year: y, count: counts.get(y) || 0 });
  }
  return out;
}

/** Aggregate events by entity_id to produce per-product rollups for
 *  the product grid. Only entities with at least one published event
 *  are returned — the OFF / Kroger / etc. monitoring placeholders stay
 *  in the database but don't clutter the public brand page. */
export function rollupProducts(
  entities: ProductEntity[],
  events: EventRow[],
): ProductRollup[] {
  const byEntity = new Map<string, EventRow[]>();
  for (const e of events) {
    if (!e.entity_id) continue;
    const arr = byEntity.get(e.entity_id) || [];
    arr.push(e);
    byEntity.set(e.entity_id, arr);
  }

  return entities
    .map((ent) => {
      const evs = byEntity.get(ent.id) || [];
      let worst = 0; // most-negative size_delta_pct
      let leadType: string | null = null;
      for (const e of evs) {
        const d = num(e.size_delta_pct);
        if (d < worst) worst = d;
        if (!leadType && e.sources.length > 0) {
          leadType = e.sources[0].source_type;
        }
      }
      return {
        entity_id: ent.id,
        canonical_name: ent.canonical_name,
        image_url: ent.image_url,
        event_count: evs.length,
        worst_delta_pct: worst,
        lead_source_type: leadType,
      };
    })
    .filter((p) => p.event_count > 0);
}

/** Most-common manufacturer across the brand's entities, for the
 *  "Owned by X" hero subtitle. Returns null if no entity has one. */
export function dominantManufacturer(
  entities: (ProductEntity & { manufacturer?: string | null })[],
): string | null {
  const counts = new Map<string, number>();
  for (const e of entities) {
    const m = e.manufacturer || null;
    if (!m) continue;
    counts.set(m, (counts.get(m) || 0) + 1);
  }
  let best: string | null = null;
  let bestCount = 0;
  for (const [m, c] of counts) {
    if (c > bestCount) {
      best = m;
      bestCount = c;
    }
  }
  return best;
}
