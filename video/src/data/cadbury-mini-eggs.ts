import type { ShrinkEvent } from "./types";

/**
 * Real shrink event used as the proof-of-concept for the Gotcha Reveal short.
 * Values lifted from the mockup at
 * web/public/mockups/products-cadbury-dairy-milk-mini-eggs.html (the
 * Jan 2021 -> Mar 2024 hop: 80g -> 72g, -10%).
 *
 * In production this would be a row pulled from the `content_candidates`
 * view by pipeline/scripts/generate_social_content.py.
 */
export const cadburyMiniEggs: ShrinkEvent = {
  brand: "Cadbury",
  productName: "Dairy Milk Mini Eggs",
  category: "Confectionery",
  manufacturer: "Mondelez International",

  sizeBefore: 80,
  sizeAfter: 72,
  sizeUnit: "g",
  sizeDeltaPct: -10,

  observedDateBefore: "2021-01-15",
  observedDateAfter: "2024-03-26",

  priceBefore: 4.0,
  priceAfter: 4.0,
  pricePerUnitBefore: 0.05,
  pricePerUnitAfter: 0.0556,

  productImageUrl: null,

  evidenceCount: 9,
  productSlug: "cadbury-dairy-milk-mini-eggs",
};
