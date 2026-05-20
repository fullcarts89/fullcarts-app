/** Row shapes returned by Supabase queries on this route.
 *  Numeric columns come back as strings from PostgREST (PG numeric →
 *  JS string) — components coerce them where needed. */

export interface BrandRanking {
  brand: string;
  product_count: number;
  shrinkflation_events: number;
  restoration_events: number;
  total_shrinkage_pct: string;
  avg_shrink_per_event: string;
  first_detected: string;
  last_detected: string;
}

export interface ProductEntity {
  id: string;
  brand: string;
  canonical_name: string;
  image_url: string | null;
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

/** Per-entity rollup computed from the events list for the product grid. */
export interface ProductRollup {
  entity_id: string;
  canonical_name: string;
  image_url: string | null;
  event_count: number;
  worst_delta_pct: number;
  /** Best source-type tag for the entity's lead image, used to render
   *  "News" / "Reddit" badge on the product thumb. */
  lead_source_type: string | null;
}
