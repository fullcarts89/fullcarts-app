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
