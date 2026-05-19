// Server component. Green-themed positive callout listing recent
// restoration events (a product whose size was increased back toward
// or beyond its prior level). Empty state preserved when the dataset
// is empty.
import styles from "../styles.module.css";
import { isoDay } from "../lib";
import type { RestorationRow } from "../types";

interface Props {
  rows: RestorationRow[];
}

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function monthYear(iso: string): string {
  const day = iso.slice(0, 10);
  const parts = day.split("-");
  if (parts.length !== 3) return day;
  const m = parseInt(parts[1], 10) - 1;
  return `${MONTHS[m] || ""} ${parts[0]}`;
}

function deltaPct(before: number, after: number): number {
  if (before <= 0) return 0;
  return ((after - before) / before) * 100;
}

export default function RestorationCorner({ rows }: Props) {
  if (rows.length === 0) {
    return (
      <div className={styles["restore-card"]}>
        <div className={styles["restore-eyebrow"]}>
          Restorations · the wins
        </div>
        <div className={styles["restore-empty"]}>
          No restorations on record yet. When a brand puts product back in the package, it shows up here.
        </div>
      </div>
    );
  }
  return (
    <div className={styles["restore-card"]}>
      <div className={styles["restore-eyebrow"]}>
        Restorations · the wins
      </div>
      <div className={styles["restore-list"]}>
        {rows.map((r) => {
          const before = parseFloat(r.size_before);
          const after = parseFloat(r.size_after);
          const d = deltaPct(before, after);
          return (
            <div key={r.id} className={styles["restore-row"]}>
              <div className={styles["restore-date"]}>
                {monthYear(isoDay(r.observed_date))}
              </div>
              <div>
                <div className={styles["restore-product"]}>{r.product_name}</div>
                <div className={styles["restore-brand"]}>{r.brand}</div>
              </div>
              <div className={styles["restore-sizes"]}>
                <span className={styles.before}>
                  {r.size_before}
                  {r.size_unit}
                </span>
                <span className={styles.arrow}>→</span>
                <span className={styles.after}>
                  {r.size_after}
                  {r.size_unit}
                </span>
                {d > 0 && (
                  <span className={styles.delta}>+{d.toFixed(0)}%</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
