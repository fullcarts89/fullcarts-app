/** Row shape returned by the product_index SQL view (migration 054).
 *  Numeric columns come back as strings from PostgREST. */

export interface ProductIndexRow {
  entity_id: string;
  brand: string;
  canonical_name: string;
  category: string | null;
  image_url: string | null;
  manufacturer: string | null;
  shrinkflation_events: number;
  restoration_events: number;
  avg_shrink_per_event: string | number | null;
  worst_delta_pct: string | number | null;
  first_detected: string | null;
  last_detected: string | null;
}

/** Product + a canonical rank assigned server-side (rank = position in
 *  most-events-desc order). Used so the rank badge stays stable even
 *  when the client re-sorts by another axis. */
export interface RankedProduct extends ProductIndexRow {
  rank: number;
}
