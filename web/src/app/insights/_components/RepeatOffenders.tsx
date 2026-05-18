// Server component. Top-N product cards by event count, linking to
// the /products/[id] detail page. Uses entity image_url if present,
// falls back to a numbered placeholder thumbnail.
import styles from "../styles.module.css";
import { fmtPct, num } from "../lib";
import type { LeaderboardRow } from "../types";

interface Props {
  rows: LeaderboardRow[];
}

export default function RepeatOffenders({ rows }: Props) {
  if (rows.length === 0) {
    return <div className={styles.empty}>No leaderboard data yet</div>;
  }
  return (
    <div className={styles["repeat-grid"]}>
      {rows.map((r, idx) => {
        const cum = num(r.cumulative_shrink_pct);
        return (
          <a
            key={r.entity_id}
            className={styles["repeat-card"]}
            href={`/products/${r.entity_id}`}
          >
            <div className={styles["repeat-thumb"]}>
              {r.image_url && <img src={r.image_url} alt={r.name} loading="lazy" />}
              <div className={styles["rt-rank"]}>{idx + 1}</div>
            </div>
            <div className={styles["repeat-brand"]}>{r.brand}</div>
            <div className={styles["repeat-name"]}>{r.name}</div>
            <div className={styles["repeat-stats"]}>
              <span className={styles.events}>
                {r.shrink_count} event{r.shrink_count === 1 ? "" : "s"}
              </span>
              <span className={styles.delta}>
                {cum !== 0 ? fmtPct(cum) : "—"}
              </span>
            </div>
          </a>
        );
      })}
    </div>
  );
}
