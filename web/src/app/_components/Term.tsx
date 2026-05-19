// Inline glossary. Wraps a jargon term with a hover/focus tooltip that
// explains it. Renders as <abbr> so screen readers announce the
// expansion, with a dotted underline + popover on hover or focus.
//
// Use sparingly — only on the first occurrence of each term per page.
// One source of truth for definitions, so the tooltip text stays
// consistent across /insights, /about, and per-product pages.

import styles from "./Term.module.css";

export interface TermProps {
  /** The visible label, e.g. "R-CPI-SC". */
  label: string;
  /** The expansion + 1–2 sentence definition the tooltip surfaces. */
  define: string;
  /** Optional className override for layout-specific styling. */
  className?: string;
}

// Canonical definitions for the jargon that appears repeatedly across
// the site. Keep the strings short — a tooltip that overflows the
// viewport is worse than no tooltip at all.
export const GLOSSARY: Record<string, string> = {
  "R-CPI-SC":
    "Research CPI excluding product Size Changes — the BLS's only official US measure of shrinkflation. Counts how many CPI-tracked items shrank between quarterly surveys.",
  Skimpflation:
    "When the recipe quietly gets cheaper — less protein, more filler, swapped fats — without the package size changing. Detected by comparing nutrition labels across USDA quarterly releases.",
  "Pack variant":
    "A specific SKU (size + barcode) under a product. One canonical product can have several pack variants — a 12oz can, a 6-pack, a value size — each tracked separately.",
  GDELT:
    "The Global Database of Events, Language, and Tone — an open archive of every news article worldwide. We query it daily for shrinkflation coverage we'd otherwise miss.",
  "Food CPI":
    "The Food-at-Home Consumer Price Index, published monthly by the BLS and surfaced via FRED. The macro inflation backdrop we plot shrinkflation events against.",
  ISR: "Incremental Static Regeneration — pages are pre-built then refreshed in the background on a schedule, so visitors always get instant loads and freshness without per-request cost.",
};

export default function Term({ label, define, className }: TermProps) {
  const def = define || GLOSSARY[label];
  return (
    <abbr
      title={def}
      tabIndex={0}
      className={[styles.term, className].filter(Boolean).join(" ")}
    >
      {label}
    </abbr>
  );
}
