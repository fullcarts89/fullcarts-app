/** Row shapes returned by Supabase queries on the product detail route.
 *  Numeric columns come back as strings from PostgREST (PG numeric →
 *  JS string) — components coerce them where needed. */

export interface ProductEntity {
  id: string;
  brand: string;
  canonical_name: string;
  category: string | null;
  image_url: string | null;
  manufacturer: string | null;
}

export interface EventSource {
  claim_id: string;
  source_type: string;
  url: string | null;
  domain: string | null;
  publisher: string | null;
  title: string | null;
  image: string | null;
  claim_image_path: string | null;
  date: string | null;
  // Added by migration 067 for source-row triage. Reddit/news posts may
  // have neither field; UI renders them only when populated.
  author: string | null;
  body_excerpt: string | null;
}

export interface EventRow {
  event_id: string;
  entity_id: string | null;
  brand: string;
  product_name: string;
  size_before: string;
  size_after: string;
  size_unit: string;
  size_delta_pct: string;
  severity: string | null;
  observed_date: string;
  evidence_count: number;
  sources: EventSource[];
}

export interface PackVariant {
  id: string;
  variant_name: string | null;
  current_size: string | null;
  size_unit: string | null;
  upc: string | null;
  is_active: boolean | null;
}

export interface VariantObservation {
  variant_id: string;
  observed_date: string;
  source_type: string;
  size: string | null;
  size_unit: string | null;
  price: string | null;
  retailer: string | null;
}

export interface RelatedProduct {
  entity_id: string;
  canonical_name: string;
  image_url: string | null;
  event_count: number;
  worst_delta_pct: number;
}

/** One row from consumer_reports_findings — a CR article that called
 *  out this product by name. */
export interface ConsumerReportRef {
  id: string;
  source_url: string;
  title: string;
  published_at: string | null;
  excerpt: string | null;
  brand: string | null;
  product_name: string | null;
}

/** One per-UPC pair of usda_product_history rows (earliest + latest
 *  releases that carry nutrition data). All numeric columns come
 *  through as `string | number | null` because Supabase serializes
 *  Postgres NUMERIC as strings. */
export interface UsdaNutritionRow {
  gtin_upc: string;
  release_date: string;
  description: string | null;
  brand_name: string | null;
  calories_kcal: string | number | null;
  protein_g: string | number | null;
  total_fat_g: string | number | null;
  saturated_fat_g: string | number | null;
  carbs_g: string | number | null;
  fiber_g: string | number | null;
  sugars_g: string | number | null;
  calcium_mg: string | number | null;
  sodium_mg: string | number | null;
  cholesterol_mg: string | number | null;
}

/** Distilled before/after for one nutrient. Built client-server-side
 *  from two UsdaNutritionRow snapshots (earliest + latest release). */
export interface NutrientDelta {
  /** Display label (e.g. "Protein", "Added sugar"). */
  label: string;
  /** Short label for tight cells. */
  sublabel?: string;
  /** Unit string (g, mg, kcal). */
  unit: string;
  /** Numeric value at the earlier release. */
  before: number;
  /** Numeric value at the later release. */
  after: number;
  /** Per-100g delta % (after - before) / before * 100. Positive = up, negative = down. */
  delta_pct: number;
  /** Direction we expect for "this is bad / skimpflation". */
  bad_direction: "down" | "up";
}

/** Full skimpflation data shown in the overlay. Null if we have no
 *  nutrition history for any UPC linked to the entity. */
export interface SkimpData {
  upc: string;
  description: string | null;
  releases_compared: number;
  before_date: string;
  after_date: string;
  nutrients: NutrientDelta[];
  /** Aggregate skimp score — the sum of "bad direction" deltas.
   *  We hide the overlay entirely when this is below MIN_SCORE so we
   *  don't surface noise. */
  skimp_score: number;
}

/** One step on the size-over-time chart. Built from chronologically
 *  sorted shrinkflation events. */
export interface TrajectoryStep {
  /** ISO date the size took effect. */
  date: string;
  /** Numeric size in the unit shown. */
  size: number;
  /** % drop from the previous step. Null for the first step. */
  deltaPct: number | null;
}
