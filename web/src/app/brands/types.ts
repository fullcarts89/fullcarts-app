/** Row shape returned by the brand_index SQL view (migration 052).
 *  Numeric columns come back as strings from PostgREST. */

export interface BrandIndexRow {
  brand: string;
  product_count: number;
  shrinkflation_events: number;
  restoration_events: number;
  avg_shrink_per_event: string;
  first_detected: string;
  last_detected: string;
  thumbnail: string | null;
  worst_delta_pct: string | null;
}

/** Brand + a canonical rank assigned server-side (rank = position in
 *  most-events-desc order). Used so the rank badge stays stable even
 *  when the client re-sorts by another axis. */
export interface RankedBrand extends BrandIndexRow {
  rank: number;
}
