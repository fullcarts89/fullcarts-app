// Server component. Top-N product cards by event count, linking to
// the /products/[id] detail page. The delta shown on each card is
// the biggest single drop (most-negative size_delta_pct across the
// product's events) — not the sum of deltas, which exploded past
// 100% on heavily-flagged products because chained percentage
// changes don't add linearly.
import styles from "../styles.module.css";
import SafeImage from "../../_components/SafeImage";
import { fmtPct } from "../lib";
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
      {rows.map((r, idx) => (
        <a
          key={r.entity_id}
          className={styles["repeat-card"]}
          href={`/products/${r.entity_id}`}
        >
          <div className={styles["repeat-thumb"]}>
            {r.image_url && (
              <SafeImage
                src={r.image_url}
                alt={`${r.brand} ${r.name} package`}
                fill
                sizes="(min-width: 1024px) 200px, (min-width: 640px) 25vw, 50vw"
              />
            )}
            <div className={styles["rt-rank"]}>{idx + 1}</div>
          </div>
          <div className={styles["repeat-brand"]}>{r.brand}</div>
          <div className={styles["repeat-name"]}>{r.name}</div>
          <div className={styles["repeat-stats"]}>
            <span className={styles.events}>
              {r.shrink_count} event{r.shrink_count === 1 ? "" : "s"}
            </span>
            <span className={styles.delta} title="Biggest single drop">
              {r.worst_drop_pct !== 0 ? fmtPct(r.worst_drop_pct) : "—"}
            </span>
          </div>
        </a>
      ))}
    </div>
  );
}
