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

/** A published_change row with its earliest known source date —
 *  used to build the chart's events line keyed on "when the shrink
 *  was first publicly noticed" rather than the AI-extracted
 *  observed_date (which has a known fallback-to-today bug). */
export interface EventWithSources {
  event_id: string;
  observed_date: string | null;
  sources: Array<{ date: string | null }>;
}

export interface CategoryRow {
  category: string;
  product_count: number;
  total_events: number;
  shrink_events: number;
  avg_shrink_pct: string | number | null;
}

/** Claim row tagged for the evidence wall / themed sections.
 *  Pulled from `claims` filtered by status='evidence' and a specific
 *  evidence_tag (Skimpflation, Spot the Difference, etc.). */
export interface TaggedClaim {
  id: string;
  brand: string | null;
  product_name: string | null;
  category: string | null;
  old_size: string | number | null;
  old_size_unit: string | null;
  new_size: string | number | null;
  new_size_unit: string | null;
  change_description: string | null;
  observed_date: string | null;
  image_storage_path: string | null;
  evidence_tags: string[] | null;
  raw_item_id: string | null;
  matched_entity_id?: string | null;
  source_url?: string | null;
  source_image?: string | null;
}

/** Repeat-offender card: per-entity rollup of shrinkflation events.
 *  worst_drop_pct is the most-negative single delta we've documented
 *  for the product (not the sum of all deltas — chained percentage
 *  changes don't add linearly and produce nonsensical "240%" values). */
export interface LeaderboardRow {
  entity_id: string;
  name: string;
  brand: string;
  category: string | null;
  image_url: string | null;
  shrink_count: number;
  worst_drop_pct: number;
}

export interface RestorationRow {
  id: string;
  entity_id: string | null;
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

/** One x/y point for the macro chart. y is null when the series has
 *  no observation for that month. Originally a three-line chart;
 *  trendsInterest (Google Trends, 0-100) was added in 057. */
export interface ChartPoint {
  month: string;
  events: number | null;
  blsDownsizings: number | null;
  cpiYoyPct: number | null;
  /** Google Trends search interest, 0-100, normalised across the window. */
  trendsInterest: number | null;
}

/** A single row from google_trends_data. value comes back as
 *  string | number depending on Postgres → JSON serialization. */
export interface GoogleTrendsRow {
  keyword: string;
  observation_date: string;
  value: string | number | null;
}

/** One year in the "shrinkflation tracks inflation" chart: BLS "All
 *  food" downsizing count for the calendar year (bar) and FRED food-CPI
 *  YoY% (line). `partial` flags a year BLS hasn't fully reported yet so
 *  the bar is visibly marked rather than silently undercounting. */
export interface ShrinkInflationYear {
  year: number;
  downsizings: number | null;
  inflationPct: number | null;
  partial: boolean;
}

/** One manufacturer entry from the corporate_tree view (migration 056).
 *  top_brands is a JSONB array of up to three brand entries with their
 *  thumbnails, biggest single-shrink %, and event count. */
export interface CorporateNode {
  manufacturer: string;
  distinct_brands: number;
  total_shrinkflation_events: number | null;
  worst_delta_pct: number | string | null;
  top_brands: Array<{
    brand: string;
    events: number | null;
    worst: number | string | null;
    thumbnail: string | null;
  }> | null;
}

/** One product line in the grocery-cart widget. Real product, real
 *  measured shrink across the date span we're showing. */
export interface CartItem {
  entity_id: string;
  brand: string;
  product_name: string;
  category: string | null;
  image_url: string | null;
  /** Earliest observed size (numeric). */
  size_before: number;
  /** Latest observed size (numeric). */
  size_after: number;
  size_unit: string;
  /** Negative — the % the product shrank from earliest to latest. */
  shrink_pct: number;
  /** ISO date of the earliest event (== "year you started buying it"). */
  date_before: string;
  /** ISO date of the latest event. */
  date_after: string;
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
