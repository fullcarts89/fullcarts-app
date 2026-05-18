// Skimpflation overlay — surfaces nutritional drift across USDA
// quarterly releases for the same UPC. Renders when we have at least
// two releases with nutrition data AND the aggregate skimp score
// crosses SKIMP_MIN_SCORE.
//
// Styling matches the mockup (purple-themed card; same dark-graphite
// system as the rest of the product page).
import styles from "../styles.module.css";
import type { SkimpData } from "../types";

interface Props {
  data: SkimpData;
}

function fmt(n: number, unit: string): string {
  // Sodium / calcium come back in mg; rounding to whole numbers reads
  // better than 12.4mg. Grams keep one decimal.
  if (unit === "mg" || unit === "kcal") return `${Math.round(n)}${unit}`;
  return `${n.toFixed(1)}${unit}`;
}

function deltaLabel(pct: number): string {
  const sign = pct > 0 ? "+" : pct < 0 ? "−" : "";
  return `${sign}${Math.abs(pct).toFixed(1)}%`;
}

function deltaClass(pct: number, bad: "up" | "down"): string {
  const moved = pct > 0 ? "up" : pct < 0 ? "down" : null;
  if (!moved) return styles["skimp-delta"];
  const isBad = bad === moved;
  return `${styles["skimp-delta"]} ${
    isBad ? styles["skimp-delta-bad"] : styles["skimp-delta-good"]
  }`;
}

export default function SkimpflationOverlay({ data }: Props) {
  const beforeYear = data.before_date.slice(0, 4);
  const afterYear = data.after_date.slice(0, 4);
  return (
    <div className={styles["skimp-card"]}>
      <div className={styles["skimp-head"]}>
        <span className={styles["skimp-eyebrow"]}>Skimpflation</span>
        <div className={styles["skimp-title"]}>
          The bag shrank — and the recipe got cheaper, too.
        </div>
      </div>
      <p className={styles["skimp-lead"]}>
        Between USDA&apos;s <strong>{beforeYear}</strong> release and{" "}
        <strong>{afterYear}</strong>, the per-100g nutrition label for this
        product shifted in {data.nutrients.length} measurable way
        {data.nutrients.length === 1 ? "" : "s"}. Aggregate skimp score:{" "}
        <strong>{data.skimp_score.toFixed(1)}</strong>.
      </p>

      <div className={styles["skimp-table"]}>
        <div className={`${styles["skimp-cell"]} ${styles["skimp-hdr"]}`}>
          Nutrient (per 100g)
        </div>
        <div className={`${styles["skimp-cell"]} ${styles["skimp-hdr"]}`}>
          Before · {data.before_date.slice(0, 7)}
        </div>
        <div className={`${styles["skimp-cell"]} ${styles["skimp-hdr"]}`}>
          After · {data.after_date.slice(0, 7)}
        </div>
        <div className={`${styles["skimp-cell"]} ${styles["skimp-hdr"]}`}>
          Delta
        </div>

        {data.nutrients.map((n) => (
          <div key={n.label} className={styles["skimp-row"]}>
            <div className={`${styles["skimp-cell"]} ${styles["skimp-nutrient"]}`}>
              {n.label}
            </div>
            <div className={`${styles["skimp-cell"]} ${styles["skimp-before"]}`}>
              {fmt(n.before, n.unit)}
            </div>
            <div className={`${styles["skimp-cell"]} ${styles["skimp-after"]}`}>
              {fmt(n.after, n.unit)}
            </div>
            <div className={`${styles["skimp-cell"]} ${deltaClass(n.delta_pct, n.bad_direction)}`}>
              {deltaLabel(n.delta_pct)}
            </div>
          </div>
        ))}
      </div>

      <div className={styles["skimp-credit"]}>
        Source: USDA FoodData Central · gtin {data.upc} · {data.releases_compared}{" "}
        releases compared
      </div>
    </div>
  );
}
