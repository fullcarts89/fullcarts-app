/** Pure helpers used by the product-detail route. Same conventions as
 *  the brand-page lib: input → derived shape, no side effects. */
import type {
  EventRow,
  EventSource,
  TrajectoryStep,
} from "./types";

const STORAGE_BUCKET_URL =
  (process.env.NEXT_PUBLIC_SUPABASE_URL || "") +
  "/storage/v1/object/public/claim-images/";

export function num(s: string | number | null | undefined): number {
  if (s == null) return 0;
  const n = typeof s === "string" ? parseFloat(s) : s;
  return Number.isFinite(n) ? n : 0;
}

export function isoDay(s: string | null | undefined): string {
  if (!s) return "";
  return s.slice(0, 10);
}

export function claimImageUrl(
  storagePath: string | null | undefined,
): string | null {
  if (!storagePath) return null;
  return STORAGE_BUCKET_URL + storagePath;
}

/** Picks the first usable image for an event: archived Reddit photo
 *  first (curated, side-by-side comparison material), then news hero
 *  image. */
export function leadImageFromEvent(e: EventRow): {
  url: string | null;
  source_type: string | null;
} {
  for (const s of e.sources) {
    const u = claimImageUrl(s.claim_image_path);
    if (u) return { url: u, source_type: s.source_type };
  }
  for (const s of e.sources) {
    if (s.image) return { url: s.image, source_type: s.source_type };
  }
  return { url: null, source_type: null };
}

export function publisherLabel(s: EventSource): string {
  if (s.publisher) return s.publisher;
  const host = s.domain || "";
  if (!host) return "Unknown";
  const first = host.split(".")[0] || host;
  return first.charAt(0).toUpperCase() + first.slice(1);
}

/** Convert the unsorted event list into a chronologically ordered
 *  step list for the trajectory chart. Skips events with non-numeric
 *  sizes. Returns an empty array if fewer than two valid steps exist. */
export function buildTrajectory(events: EventRow[]): TrajectoryStep[] {
  const usable = events
    .filter((e) => {
      const a = num(e.size_after);
      return a > 0;
    })
    .sort((a, b) => isoDay(a.observed_date).localeCompare(isoDay(b.observed_date)));

  if (usable.length === 0) return [];

  const steps: TrajectoryStep[] = [];
  // First step uses the *before* of the earliest event, so the chart
  // shows the starting size, not the first observed drop.
  const first = usable[0];
  const firstBefore = num(first.size_before);
  if (firstBefore > 0) {
    steps.push({
      date: isoDay(first.observed_date),
      size: firstBefore,
      deltaPct: null,
    });
  }
  for (const e of usable) {
    steps.push({
      date: isoDay(e.observed_date),
      size: num(e.size_after),
      deltaPct: num(e.size_delta_pct),
    });
  }
  // Collapse runs with identical sizes — happens when an event documents
  // no change (corrupt data). Keep the first, drop later dupes.
  const dedup: TrajectoryStep[] = [];
  for (const s of steps) {
    const prev = dedup[dedup.length - 1];
    if (prev && Math.abs(prev.size - s.size) < 0.01) continue;
    dedup.push(s);
  }
  return dedup;
}

/** Sum the per-event % deltas to get cumulative loss. Negative if
 *  product has shrunk overall. Uses (latest - earliest) / earliest
 *  for accuracy — chained % deltas don't add linearly. */
export function cumulativeShrinkPct(steps: TrajectoryStep[]): number {
  if (steps.length < 2) return 0;
  const start = steps[0].size;
  const end = steps[steps.length - 1].size;
  if (start <= 0) return 0;
  return ((end - start) / start) * 100;
}

/** Most negative (biggest) single drop across the event list. */
export function biggestSingleDrop(events: EventRow[]): {
  pct: number;
  date: string;
  before: number;
  after: number;
} | null {
  let best: ReturnType<typeof biggestSingleDrop> = null;
  for (const e of events) {
    const d = num(e.size_delta_pct);
    if (d >= 0) continue;
    if (!best || d < best.pct) {
      best = {
        pct: d,
        date: isoDay(e.observed_date),
        before: num(e.size_before),
        after: num(e.size_after),
      };
    }
  }
  return best;
}

/** Total contributing sources across all events. */
export function totalEvidenceCount(events: EventRow[]): number {
  return events.reduce((sum, e) => sum + (e.evidence_count || 0), 0);
}

/** Sort events newest → oldest for the change-history list. */
export function eventsByDateDesc(events: EventRow[]): EventRow[] {
  return [...events].sort((a, b) =>
    isoDay(b.observed_date).localeCompare(isoDay(a.observed_date)),
  );
}

export function eventsByDateAsc(events: EventRow[]): EventRow[] {
  return [...events].sort((a, b) =>
    isoDay(a.observed_date).localeCompare(isoDay(b.observed_date)),
  );
}

/** Dominant headline + publisher for an event — pick the source whose
 *  title appears most often (syndication signal). */
export function dominantSource(sources: EventSource[]): EventSource | null {
  if (sources.length === 0) return null;
  const counts = new Map<string, number>();
  for (const s of sources) {
    if (!s.title) continue;
    counts.set(s.title, (counts.get(s.title) || 0) + 1);
  }
  let bestTitle: string | null = null;
  let bestCount = 0;
  for (const [t, c] of counts) {
    if (c > bestCount) {
      bestTitle = t;
      bestCount = c;
    }
  }
  if (!bestTitle) return sources[0];
  return sources.find((s) => s.title === bestTitle) || sources[0];
}

/** Y-axis tick layout. Rounds the size range outward to a nice
 *  human-readable padding so labels don't crash into the steps. */
export function trajectoryAxis(steps: TrajectoryStep[]): {
  min: number;
  max: number;
  ticks: number[];
} {
  if (steps.length === 0) return { min: 0, max: 100, ticks: [0, 50, 100] };
  const sizes = steps.map((s) => s.size);
  const rawMin = Math.min(...sizes);
  const rawMax = Math.max(...sizes);
  const span = rawMax - rawMin || rawMax || 1;
  const pad = Math.max(span * 0.25, 1);
  const min = Math.max(0, Math.floor((rawMin - pad) / 5) * 5);
  const max = Math.ceil((rawMax + pad) / 5) * 5;
  const step = Math.max(1, Math.round((max - min) / 4));
  const ticks = [min, min + step, min + 2 * step, min + 3 * step, max];
  return { min, max, ticks };
}
