/** Pure helpers for /insights. Same conventions as the brand/product
 *  routes: input → derived shape, no side effects. */
import type {
  BlsRow,
  ChartPoint,
  FredCpiRow,
  TimelineRow,
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

/** Latest non-zero quarter-total downsizing count from bls_shrinkflation.
 *  We sum across all series rows for the latest period — the dataset
 *  contains per-category subtotals plus an "All food" series; summing
 *  every row would double-count, so we filter to a single series first.
 *  Default is the "All food" series; falls back to summing distinct
 *  rows if that series is missing. */
export function headlineBls(rows: BlsRow[]): {
  count: number;
  quarter: string;
  prevQuarterCount: number;
  prevQuarterDeltaPct: number;
  yearAgoCount: number;
  yearAgoDeltaPct: number;
} {
  // Group by period and pick the highest count per period (one series).
  // Filtering by series name is brittle — the "All food" label varies
  // ("All food", "all food", etc.). Take the max count per period
  // (which is "All food" by construction since subtotals are smaller).
  const byPeriod = new Map<string, number>();
  for (const r of rows) {
    const period = isoDay(r.period);
    const c = r.downsizing_count;
    if (period && c != null) {
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
 *  - FullCarts events per month from shrinkflation_timeline
 *  - BLS quarterly downsizings spread evenly across the 3 months
 *  - FRED CPI YoY% per month
 *
 *  Window: last `windowMonths` months ending at the latest month
 *  present in any series. */
export function buildChart(
  timeline: TimelineRow[],
  bls: BlsRow[],
  fred: FredCpiRow[],
  windowMonths: number = 39,
): ChartPoint[] {
  // FullCarts events per month
  const eventsByMonth = new Map<string, number>();
  for (const r of timeline) {
    const ym = isoMonth(r.month);
    if (ym) eventsByMonth.set(ym, r.shrink_events || 0);
  }

  // BLS — pick the largest count per period (the "All food" series),
  // then spread the quarterly count across the 3 months in that quarter.
  const blsByPeriod = new Map<string, number>();
  for (const r of bls) {
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

  // Window: pick the latest month across all three sources.
  const allMonths = new Set<string>();
  for (const m of eventsByMonth.keys()) allMonths.add(m);
  for (const m of blsByMonth.keys()) allMonths.add(m);
  for (const m of cpiByMonth.keys()) allMonths.add(m);
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
