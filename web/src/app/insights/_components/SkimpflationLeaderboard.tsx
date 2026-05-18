// Server component. Renders claims that admins have manually tagged
// "Skimpflation" via the Evidence Wall flow in /admin/claims. Each
// card surfaces the change_description as the human-written summary
// of what was swapped or substituted.
//
// (Replaces the earlier USDA-driven nutrition_skimpflation RPC view.
// USDA-detected nutrition diffs will get their own pipeline step
// that creates claims with this tag, so this section becomes the
// single source of truth for skimpflation evidence.)
import styles from "../styles.module.css";
import { isoDay } from "../lib";
import type { TaggedClaim } from "../types";

interface Props {
  rows: TaggedClaim[];
}

export default function SkimpflationLeaderboard({ rows }: Props) {
  if (rows.length === 0) {
    return (
      <div className={styles["skimp-card-wrap"]}>
        <div className={styles["skimp-eyebrow"]}>Tagged claims · admin-curated</div>
        <div className={styles.empty} style={{ marginTop: 16 }}>
          No claims tagged &ldquo;Skimpflation&rdquo; yet
        </div>
      </div>
    );
  }
  return (
    <div className={styles["skimp-card-wrap"]}>
      <div className={styles["skimp-eyebrow"]}>
        Tagged claims · admin-curated · {rows.length} surfaced
      </div>
      <div className={styles["skimp-grid"]}>
        {rows.map((r) => (
          <div key={r.id} className={styles["skimp-row"]}>
            <div className={styles["skimp-product"]}>
              {r.product_name || "(unnamed product)"}
            </div>
            {r.brand && <div className={styles["skimp-brand"]}>{r.brand}</div>}
            {r.change_description && (
              <div className={styles["skimp-desc"]}>{r.change_description}</div>
            )}
            {r.observed_date && (
              <div className={styles["skimp-date"]}>
                Observed {isoDay(r.observed_date)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
