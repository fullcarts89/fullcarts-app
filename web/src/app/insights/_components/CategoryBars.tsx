// Server component. Horizontal bar list of the top categories by
// shrink_events. Bar widths are normalized against the top category
// so the leader is always 100%.
import styles from "../styles.module.css";
import { fmtPct, num } from "../lib";
import type { CategoryRow } from "../types";

interface Props {
  rows: CategoryRow[];
}

export default function CategoryBars({ rows }: Props) {
  if (rows.length === 0) {
    return <div className={styles.empty}>No category data yet</div>;
  }
  const top = rows[0].shrink_events || 1;
  return (
    <div className={styles["cat-list"]}>
      {rows.map((r) => {
        const events = r.shrink_events || 0;
        const widthPct = Math.max(2, Math.round((events / top) * 100));
        const avg = num(r.avg_shrink_pct);
        return (
          <div key={r.category} className={styles["cat-row"]}>
            <div className={styles["cat-name"]}>{r.category}</div>
            <div className={styles["cat-bar-wrap"]}>
              <div
                className={styles["cat-bar"]}
                style={{ width: `${widthPct}%` }}
              />
            </div>
            <div className={styles["cat-events"]}>
              {events.toLocaleString()}
            </div>
            <div className={styles["cat-shrink"]}>
              {avg !== 0 ? fmtPct(avg) : "—"}
            </div>
          </div>
        );
      })}
    </div>
  );
}
