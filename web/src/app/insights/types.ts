/** Row shapes returned by Supabase queries on the /insights route.
 *  Numeric columns come back as strings from PostgREST (PG numeric →
 *  JS string) — helpers in lib.ts coerce them where needed. */

export interface BlsRow {
  series: string;
  period: string;
  downsizing_count: number | null;
  upsizing_count: number | null;
}

export interface FredCpiRow {
  observation_date: string;
  value: string | number | null;
}

export interface TimelineRow {
  month: string;
  events: number;
  shrink_events: number;
  restoration_events: number;
  avg_shrink_pct: string | number | null;
}

export interface CategoryRow {
  category: string;
  product_count: number;
  total_events: number;
  shrink_events: number;
  avg_shrink_pct: string | number | null;
}

export interface SkimpRow {
  gtin_upc: string;
  brand_name: string | null;
  description: string | null;
  skimp_score: string | number | null;
  protein_drop_pct: string | number | null;
  fiber_drop_pct: string | number | null;
  sugar_rise_pct: string | number | null;
  sodium_rise_pct: string | number | null;
}

export interface LeaderboardRow {
  entity_id: string;
  name: string;
  brand: string;
  category: string | null;
  image_url: string | null;
  shrink_count: number;
  cumulative_shrink_pct: string | number | null;
}

export interface RestorationRow {
  id: string;
  brand: string;
  product_name: string;
  size_before: string;
  size_after: string;
  size_unit: string;
  observed_date: string;
  published_at: string;
}

export interface NewsFeedRow {
  id: string;
  url: string;
  title: string;
  outlet: string | null;
  published_at: string | null;
  summary: string | null;
  linked_products_count: number;
}

export interface EvidenceWallRow {
  id: string;
  brand: string | null;
  product_name: string | null;
  category: string | null;
  signal_type: string | null;
  severity: number | null;
  date_spotted: string | null;
  size_delta_pct: string | number | null;
  image_url: string | null;
  tag: string | null;
  source_url: string | null;
}

/** One x/y point for the three-line chart. y is null when the series
 *  has no observation for that month. */
export interface ChartPoint {
  month: string;
  events: number | null;
  blsDownsizings: number | null;
  cpiYoyPct: number | null;
}

export interface DashboardStats {
  total_products: number;
  total_changes: number;
  shrinkflation_events: number;
  categories_tracked: number;
  avg_shrink_pct: number | null;
  worst_shrink_pct: number | null;
  pending_review: number;
}
