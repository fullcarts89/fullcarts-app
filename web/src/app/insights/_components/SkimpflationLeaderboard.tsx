// Server component. Card grid of top USDA skimpflation findings.
// Each card shows up to 2 most-impactful nutrient deltas — protein
// drop, fiber drop, sugar rise, sodium rise — picked by magnitude.
import styles from "../styles.module.css";
import { num } from "../lib";
import type { SkimpRow } from "../types";

interface Props {
  rows: SkimpRow[];
  totalCount: number;
}

interface Pill {
  label: string;
  pct: number;
  direction: "up" | "down";
}

function topPills(r: SkimpRow): Pill[] {
  const candidates: Pill[] = [
    { label: "Protein", pct: num(r.protein_drop_pct), direction: "down" as const },
    { label: "Fiber",   pct: num(r.fiber_drop_pct),   direction: "down" as const },
    { label: "Sugar",   pct: num(r.sugar_rise_pct),   direction: "up" as const },
    { label: "Sodium",  pct: num(r.sodium_rise_pct),  direction: "up" as const },
  ].filter((p) => p.pct > 0);
  candidates.sort((a, b) => b.pct - a.pct);
  return candidates.slice(0, 2);
}

export default function SkimpflationLeaderboard({ rows, totalCount }: Props) {
  if (rows.length === 0) {
    return (
      <div className={styles["skimp-card-wrap"]}>
        <div className={styles["skimp-eyebrow"]}>USDA FoodData Central</div>
        <div className={styles.empty} style={{ marginTop: 16 }}>
          No skimpflation results yet
        </div>
      </div>
    );
  }
  return (
    <div className={styles["skimp-card-wrap"]}>
      <div className={styles["skimp-eyebrow"]}>
        USDA FDC · {totalCount} flagged · top {rows.length}
      </div>
      <div className={styles["skimp-grid"]}>
        {rows.map((r) => {
          const pills = topPills(r);
          return (
            <div key={r.gtin_upc} className={styles["skimp-row"]}>
              <div className={styles["skimp-product"]}>
                {r.description || "(unnamed product)"}
              </div>
              {r.brand_name && (
                <div className={styles["skimp-brand"]}>{r.brand_name}</div>
              )}
              <div className={styles["skimp-deltas"]}>
                {pills.map((p, i) => (
                  <span
                    key={i}
                    className={`${styles["skimp-pill"]} ${
                      p.direction === "down" ? styles.down : styles.up
                    }`}
                  >
                    {p.label} {p.direction === "down" ? "−" : "+"}
                    {p.pct.toFixed(0)}%
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
