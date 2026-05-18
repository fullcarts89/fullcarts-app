/** Pure helpers for /insights. Same conventions as the brand/product
 *  routes: input → derived shape, no side effects. */
import type {
  BlsRow,
  CartItem,
  ChartPoint,
  EventWithSources,
  FredCpiRow,
  GoogleTrendsRow,
} from "./types";

export function num(s: string | number | null | undefined): number {
  if (s == null) return 0;
  const n = typeof s === "string" ? parseFloat(s) : s;
  return Number.isFinite(n) ? n : 0;
}

export function isoDay(s: string | null | undefined): string {
  if (!s) return "";
  return s.slice(0, 10);
}

/** YYYY-MM from a date string. Returns "" if input doesn't parse. */
export function isoMonth(s: string | null | undefined): string {
  if (!s) return "";
  return s.slice(0, 7);
}

const MONTHS_SHORT = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

export function monthLabel(yyyyMm: string): string {
  const parts = yyyyMm.split("-");
  if (parts.length < 2) return yyyyMm;
  const m = parseInt(parts[1], 10) - 1;
  const yy = parts[0].slice(2);
  return `${MONTHS_SHORT[m] || ""} '${yy}`;
}

/** Quarter key from a date — e.g. "2026-01-01" → "2026-Q1". */
function quarterKey(dateIso: string): string {
  const parts = dateIso.split("-");
  if (parts.length < 2) return dateIso;
  const m = parseInt(parts[1], 10);
  const q = Math.floor((m - 1) / 3) + 1;
  return `${parts[0]}-Q${q}`;
}

/** "2026-Q2" → "Q2 '26". */
export function quarterLabel(qk: string): string {
  const parts = qk.split("-Q");
  if (parts.length !== 2) return qk;
  return `Q${parts[1]} '${parts[0].slice(2)}`;
}

/** Latest quarter-total downsizing count from bls_shrinkflation.
 *  Filters to the "All food" parent series so we never mix apples-to-
 *  pears against a subcategory subtotal. Falls back to the max count
 *  per period if no row matches "All food" (e.g. partial release). */
export function headlineBls(rows: BlsRow[]): {
  count: number;
  quarter: string;
  prevQuarterCount: number;
  prevQuarterDeltaPct: number;
  yearAgoCount: number;
  yearAgoDeltaPct: number;
} {
  // Filter to "All food" rows only. Case-insensitive prefix match
  // tolerates capitalization drift ("All food", "all food", "All Food").
  const allFood = rows.filter((r) =>
    typeof r.series === "string" && r.series.toLowerCase().startsWith("all food"),
  );
  const source = allFood.length > 0 ? allFood : rows;

  const byPeriod = new Map<string, number>();
  for (const r of source) {
    const period = isoDay(r.period);
    const c = r.downsizing_count;
    if (period && c != null) {
      // If our filtered set has multiple rows per period (shouldn't,
      // but defensively), prefer the larger count.
      const prev = byPeriod.get(period) || 0;
      if (c > prev) byPeriod.set(period, c);
    }
  }
  const sorted = Array.from(byPeriod.entries()).sort((a, b) =>
    b[0].localeCompare(a[0]),
  );

  if (sorted.length === 0) {
    return {
      count: 0,
      quarter: "",
      prevQuarterCount: 0,
      prevQuarterDeltaPct: 0,
      yearAgoCount: 0,
      yearAgoDeltaPct: 0,
    };
  }

  const [latestPeriod, latestCount] = sorted[0];
  const prevQuarterCount = sorted[1]?.[1] ?? 0;
  // Year-ago = 4 quarters back, but we have monthly periods from BLS.
  // Take the row roughly 12 months earlier.
  const latestYearMonth = latestPeriod.slice(0, 7);
  const [year, month] = latestYearMonth.split("-").map((s) => parseInt(s, 10));
  const yaYear = year - 1;
  const yaMonth = String(month).padStart(2, "0");
  const yearAgoKey = `${yaYear}-${yaMonth}-01`;
  const yearAgoCount = byPeriod.get(yearAgoKey) ?? 0;

  const dq = prevQuarterCount > 0
    ? ((latestCount - prevQuarterCount) / prevQuarterCount) * 100
    : 0;
  const dya = yearAgoCount > 0
    ? ((latestCount - yearAgoCount) / yearAgoCount) * 100
    : 0;

  return {
    count: latestCount,
    quarter: quarterKey(latestPeriod),
    prevQuarterCount,
    prevQuarterDeltaPct: dq,
    yearAgoCount,
    yearAgoDeltaPct: dya,
  };
}

/** Compute the YoY % change for the FRED CPI series. Returns one
 *  point per month where a year-ago observation exists. */
function fredYoy(rows: FredCpiRow[]): Map<string, number> {
  const byMonth = new Map<string, number>();
  for (const r of rows) {
    const ym = isoMonth(r.observation_date);
    const v = num(r.value);
    if (ym && v > 0) byMonth.set(ym, v);
  }
  const out = new Map<string, number>();
  for (const [ym, v] of byMonth) {
    const [y, m] = ym.split("-");
    const prevYear = (parseInt(y, 10) - 1).toString();
    const yaKey = `${prevYear}-${m}`;
    const ya = byMonth.get(yaKey);
    if (ya && ya > 0) {
      out.set(ym, ((v - ya) / ya) * 100);
    }
  }
  return out;
}

/** Build a monthly time series merging all three chart inputs:
 *  - FullCarts events per month, keyed on the earliest source date
 *    among contributing claims (when the shrink was first publicly
 *    noticed — far more reliable than published_changes.observed_date,
 *    which falls back to date.today() when the AI can't extract one)
 *  - BLS quarterly downsizings spread evenly across the 3 months
 *  - FRED CPI YoY% per month
 *
 *  Window: trailing `windowMonths` ending at the latest observation
 *  across all three series. No trimming — source dates are reliable. */
export function buildChart(
  events: EventWithSources[],
  bls: BlsRow[],
  fred: FredCpiRow[],
  trends: GoogleTrendsRow[] = [],
  windowMonths: number = 39,
): ChartPoint[] {
  // FullCarts events per month, keyed on the earliest source.date
  // among each event's contributing claims. Skip events with no
  // sources (rare; shouldn't happen with current promote flow).
  const eventsByMonth = new Map<string, number>();
  for (const e of events) {
    let earliest: string | null = null;
    for (const s of e.sources) {
      if (!s.date) continue;
      if (!earliest || s.date < earliest) earliest = s.date;
    }
    // Fall back to observed_date only if no source dates exist.
    const dayIso = earliest || e.observed_date;
    if (!dayIso) continue;
    const ym = isoMonth(dayIso);
    if (!ym) continue;
    eventsByMonth.set(ym, (eventsByMonth.get(ym) || 0) + 1);
  }

  // BLS — filter to the "All food" parent series, then spread the
  // quarterly count across the 3 months in that quarter. Mirrors the
  // headline-stat picker so the two stay consistent.
  const blsAllFood = bls.filter((r) =>
    typeof r.series === "string" && r.series.toLowerCase().startsWith("all food"),
  );
  const blsSource = blsAllFood.length > 0 ? blsAllFood : bls;
  const blsByPeriod = new Map<string, number>();
  for (const r of blsSource) {
    const period = isoDay(r.period);
    const c = r.downsizing_count;
    if (period && c != null) {
      const prev = blsByPeriod.get(period) || 0;
      if (c > prev) blsByPeriod.set(period, c);
    }
  }
  const blsByMonth = new Map<string, number>();
  for (const [period, count] of blsByPeriod) {
    const [y, mStr] = period.split("-");
    const m = parseInt(mStr, 10);
    // Spread across the 3 months starting at this quarter's first month
    const perMonth = count / 3;
    for (let i = 0; i < 3; i++) {
      const mm = String(m + i).padStart(2, "0");
      blsByMonth.set(`${y}-${mm}`, perMonth);
    }
  }

  // FRED CPI YoY%
  const cpiByMonth = fredYoy(fred);

  // Google Trends — keep only the canonical 'shrinkflation' keyword
  // and key on YYYY-MM. Values come back as strings from PostgREST.
  const trendsByMonth = new Map<string, number>();
  for (const r of trends) {
    if (r.keyword !== "shrinkflation") continue;
    const ym = isoMonth(r.observation_date);
    if (!ym) continue;
    const v = num(r.value);
    if (v <= 0) continue;
    trendsByMonth.set(ym, v);
  }

  // Window: pick the latest month across all four sources, then trim
  // the unreliable trailing months from the events series.
  const allMonths = new Set<string>();
  for (const m of eventsByMonth.keys()) allMonths.add(m);
  for (const m of blsByMonth.keys()) allMonths.add(m);
  for (const m of cpiByMonth.keys()) allMonths.add(m);
  for (const m of trendsByMonth.keys()) allMonths.add(m);
  const sortedMonths = Array.from(allMonths).sort();
  if (sortedMonths.length === 0) return [];

  const latest = sortedMonths[sortedMonths.length - 1];
  // Build chronological list of windowMonths ending at `latest`.
  const points: ChartPoint[] = [];
  const [yEnd, mEnd] = latest.split("-").map((s) => parseInt(s, 10));
  let y = yEnd;
  let m = mEnd;
  for (let i = 0; i < windowMonths; i++) {
    const key = `${y}-${String(m).padStart(2, "0")}`;
    points.unshift({
      month: key,
      events: eventsByMonth.has(key) ? eventsByMonth.get(key)! : null,
      blsDownsizings: blsByMonth.has(key) ? blsByMonth.get(key)! : null,
      cpiYoyPct: cpiByMonth.has(key) ? cpiByMonth.get(key)! : null,
      trendsInterest: trendsByMonth.has(key) ? trendsByMonth.get(key)! : null,
    });
    m -= 1;
    if (m === 0) {
      m = 12;
      y -= 1;
    }
  }
  return points;
}

/** Round a number range outward to a tick-friendly axis. Returns
 *  `[min, max]` plus a list of evenly-spaced tick values. */
export function niceAxis(
  values: number[],
  forceZero: boolean = true,
  tickCount: number = 5,
): { min: number; max: number; ticks: number[] } {
  const finite = values.filter((v) => Number.isFinite(v));
  if (finite.length === 0) return { min: 0, max: 1, ticks: [0, 1] };
  const rawMin = forceZero ? 0 : Math.min(...finite);
  const rawMax = Math.max(...finite, rawMin + 1);
  const span = rawMax - rawMin || 1;
  const step = Math.ceil(span / (tickCount - 1));
  const max = rawMin + step * (tickCount - 1);
  const ticks: number[] = [];
  for (let i = 0; i < tickCount; i++) ticks.push(rawMin + step * i);
  return { min: rawMin, max, ticks };
}

/** Two-digit fixed for delta pills. */
export function fmtPct(n: number, signed: boolean = false): string {
  if (!Number.isFinite(n) || n === 0) return "0%";
  const sign = signed && n > 0 ? "+" : "";
  return `${sign}${n.toFixed(1)}%`;
}

/** Sentence-case a snake_case signal_type. */
export function humanSignal(s: string | null | undefined): string {
  if (!s) return "Unverified";
  const words = s.split("_");
  return words
    .map((w, i) => (i === 0 ? w.charAt(0).toUpperCase() + w.slice(1) : w))
    .join(" ");
}

/** Outlets that publish shrinkflation coverage without a hard paywall
 *  (or with a generous free-article quota). Matched case-insensitively
 *  against news_feed.outlet. Tracked here rather than in the DB so
 *  the list can iterate without a migration. */
const FREE_OUTLETS = [
  "bbc",
  "bbc news",
  "reuters",
  "ap",
  "associated press",
  "apnews",
  "npr",
  "the guardian",
  "guardian",
  "cnn",
  "cnn business",
  "usa today",
  "yahoo finance",
  "yahoo",
  "nbc news",
  "nbc",
  "cbs news",
  "cbs",
  "abc news",
  "abc",
  "fox business",
  "the conversation",
  "marketwatch",
  "axios",
  "the verge",
  "ars technica",
  "vox",
  "consumer reports",
  "the grocer",
  "today",
  "good morning america",
  "money.com",
  "investopedia",
  "the hill",
  "business insider",
];

/** Outlets we explicitly want to drop (hard paywall or unreliable
 *  free quota). Anything not in FREE_OUTLETS and not in this set is
 *  dropped too — the allowlist is the source of truth, but this
 *  documents the active exclusions for future readers. */
const PAYWALLED_OUTLETS = [
  "wsj",
  "the wall street journal",
  "wall street journal",
  "the new york times",
  "nyt",
  "ft",
  "financial times",
  "bloomberg",
  "the washington post",
  "washington post",
  "the economist",
  "economist",
];

export function isFreeOutlet(outlet: string | null | undefined): boolean {
  if (!outlet) return false;
  const normalized = outlet.toLowerCase().trim();
  if (PAYWALLED_OUTLETS.some((p) => normalized.includes(p))) return false;
  return FREE_OUTLETS.some((f) => normalized.includes(f));
}

/** Strip HTML tags and entities from a string. Google News RSS's
 *  <description> field is HTML, not plain text — typically a single
 *  <a href="..."> wrapping the article URL. We only want plain text
 *  for the news card summary, so drop tags entirely and decode the
 *  handful of entities Google News emits. */
export function stripHtml(s: string | null | undefined): string {
  if (!s) return "";
  return s
    .replace(/<[^>]+>/g, "")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/** Extract a usable image URL from a raw_items.raw_payload. Mirrors
 *  the pipeline's extraction logic (see extract_claims_vision.py).
 *  Returns null if no field has a usable image URL. */
export function imageFromRawPayload(
  payload: Record<string, unknown> | null | undefined,
): string | null {
  if (!payload) return null;

  // GDELT articles ship a single social-card image.
  const socialimage = payload["socialimage"];
  if (typeof socialimage === "string" && socialimage.startsWith("http")) {
    return socialimage;
  }

  // Reddit link posts: the URL field points directly at the image
  // when post_hint is "image".
  const url = payload["url"];
  if (typeof url === "string" && /\.(jpe?g|png|webp|gif)(\?|$)/i.test(url)) {
    return url;
  }

  // Reddit image-preview field — Reddit's CDN-resized version of the
  // post image. More reliable than `url` for legacy posts.
  const preview = payload["preview"] as Record<string, unknown> | undefined;
  if (preview && typeof preview === "object") {
    const images = preview["images"];
    if (Array.isArray(images) && images.length > 0) {
      const first = images[0] as Record<string, unknown>;
      const source = first?.["source"] as Record<string, unknown> | undefined;
      const srcUrl = source?.["url"];
      if (typeof srcUrl === "string") {
        // Reddit encodes ampersands as &amp; in the JSON.
        return srcUrl.replace(/&amp;/g, "&");
      }
    }
  }

  // Reddit gallery posts: first media_metadata entry.
  const mediaMetadata = payload["media_metadata"];
  if (mediaMetadata && typeof mediaMetadata === "object") {
    for (const value of Object.values(mediaMetadata as Record<string, unknown>)) {
      const meta = value as Record<string, unknown>;
      const s = meta?.["s"] as Record<string, unknown> | undefined;
      const u = s?.["u"];
      if (typeof u === "string") return u.replace(/&amp;/g, "&");
    }
  }

  // Thumbnail (last resort — small but better than nothing).
  const thumb = payload["thumbnail"];
  if (
    typeof thumb === "string" &&
    thumb.startsWith("http") &&
    /\.(jpe?g|png|webp|gif)/i.test(thumb)
  ) {
    return thumb;
  }

  return null;
}

/** Build the grocery-cart basket: one row per entity, picking the
 *  earliest measured "before" size and the latest measured "after"
 *  size across all the entity's shrinkflation events. Keeps only
 *  entities that have an image (the widget is visual) and a clean
 *  shrink in the 2-50% range (filters out corrupt 99%+ outliers).
 *
 *  Inputs are raw rows from a single published_changes pull. Caller
 *  is responsible for fetching entity image_url separately and
 *  joining by entity_id.
 */
export function buildCartBasket(
  rows: Array<{
    entity_id: string | null;
    brand: string | null;
    product_name: string | null;
    size_before: string | number | null;
    size_after: string | number | null;
    size_unit: string | null;
    observed_date: string | null;
  }>,
  entityById: Map<
    string,
    { canonical_name: string; brand: string; category: string | null; image_url: string | null }
  >,
  basketSize: number = 12,
): CartItem[] {
  const byEntity = new Map<
    string,
    {
      entity_id: string;
      brand: string;
      product_name: string;
      size_before: number;
      size_after: number;
      size_unit: string;
      date_before: string;
      date_after: string;
    }
  >();

  for (const r of rows) {
    if (!r.entity_id) continue;
    const before = num(r.size_before);
    const after = num(r.size_after);
    if (before <= 0 || after <= 0 || after >= before) continue;
    const unit = (r.size_unit || "").trim();
    if (!unit) continue;
    const date = isoDay(r.observed_date);
    if (!date) continue;

    const cur = byEntity.get(r.entity_id);
    if (!cur) {
      byEntity.set(r.entity_id, {
        entity_id: r.entity_id,
        brand: r.brand || "",
        product_name: r.product_name || "",
        size_before: before,
        size_after: after,
        size_unit: unit,
        date_before: date,
        date_after: date,
      });
      continue;
    }
    // Earliest known "before" size for this entity (oldest event's before)
    if (date < cur.date_before) {
      cur.date_before = date;
      cur.size_before = before;
    }
    // Latest known "after" size for this entity
    if (date > cur.date_after) {
      cur.date_after = date;
      cur.size_after = after;
    }
  }

  const items: CartItem[] = [];
  for (const agg of byEntity.values()) {
    if (agg.size_before <= 0 || agg.size_after <= 0) continue;
    if (agg.size_after >= agg.size_before) continue;
    const shrink_pct = ((agg.size_after - agg.size_before) / agg.size_before) * 100;
    // Filter the absurd ones — almost certainly data quality issues.
    // Threshold: 1.5% (real but small) to 60% (extreme but plausible).
    if (shrink_pct > -1.5 || shrink_pct < -60) continue;
    const ent = entityById.get(agg.entity_id);
    if (!ent || !ent.image_url) continue;
    items.push({
      entity_id: agg.entity_id,
      brand: ent.brand || agg.brand,
      product_name: ent.canonical_name || agg.product_name,
      category: ent.category,
      image_url: ent.image_url,
      size_before: agg.size_before,
      size_after: agg.size_after,
      size_unit: agg.size_unit,
      shrink_pct,
      date_before: agg.date_before,
      date_after: agg.date_after,
    });
  }

  // Sort by biggest shrink first, then take a diverse top N.
  items.sort((a, b) => a.shrink_pct - b.shrink_pct);
  // De-dup by brand so the basket reads as a "cart" not "Cadbury x12".
  const seenBrands = new Set<string>();
  const diverse: CartItem[] = [];
  for (const it of items) {
    const brandKey = it.brand.toLowerCase();
    if (seenBrands.has(brandKey)) continue;
    seenBrands.add(brandKey);
    diverse.push(it);
    if (diverse.length >= basketSize) break;
  }
  return diverse;
}
