import { z } from "zod";

/**
 * Mirrors a row from the `content_candidates` view planned in
 * docs/plans/2026-05-13-social-content-engine.md, which joins
 * published_changes + product_entities + (optionally) variant_observations.
 *
 * Every short-form video accepts one of these as its only input prop.
 */
export const shrinkEventSchema = z.object({
  brand: z.string(),
  productName: z.string(),
  category: z.string().nullable(),
  manufacturer: z.string().nullable(),

  sizeBefore: z.number(),
  sizeAfter: z.number(),
  sizeUnit: z.string(),
  sizeDeltaPct: z.number(),

  observedDateBefore: z.string(),
  observedDateAfter: z.string(),

  priceBefore: z.number().nullable(),
  priceAfter: z.number().nullable(),
  pricePerUnitBefore: z.number().nullable(),
  pricePerUnitAfter: z.number().nullable(),

  productImageUrl: z.string().nullable(),

  evidenceCount: z.number().int(),
  productSlug: z.string(),
});

export type ShrinkEvent = z.infer<typeof shrinkEventSchema>;
