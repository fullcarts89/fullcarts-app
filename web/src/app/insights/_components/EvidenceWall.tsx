// Server component. Curated side-by-side evidence cards. Each card
// shows before/after sizes if we have them, falls back to a single-
// pane visual when only one is known. Signal type renders as an
// amber tag (stretchflation, paper_thin, etc.).
import styles from "../styles.module.css";
import { humanSignal, num } from "../lib";
import type { EvidenceWallRow } from "../types";

interface Props {
  rows: EvidenceWallRow[];
}

/** Try to derive a "before" size if size_delta_pct + a current size
 *  hint is in the tag field. For now we leave sizes blank when
 *  size_delta_pct alone is present — the dataset rarely has paired
 *  observations. The visual still shows the signal type. */
export default function EvidenceWall({ rows }: Props) {
  if (rows.length === 0) {
    return <div className={styles.empty}>Evidence wall is empty</div>;
  }
  return (
    <div className={styles["wall-grid"]}>
      {rows.map((r) => {
        const delta = num(r.size_delta_pct);
        const href = r.source_url || "#";
        return (
          <a
            key={r.id}
            className={styles["wall-card"]}
            href={href}
            target={r.source_url ? "_blank" : undefined}
            rel={r.source_url ? "noopener noreferrer" : undefined}
          >
            <div className={styles["wall-img"]}>
              {r.image_url && (
                <img src={r.image_url} alt={r.product_name || "Evidence"} loading="lazy" />
              )}
              {delta !== 0 && (
                <span className={styles["ps-label"]}>
                  {delta < 0 ? "" : "+"}
                  {delta.toFixed(0)}%
                </span>
              )}
              <div className={styles["ps-side"]}>
                <div className={styles["ps-tag"]}>Before</div>
                <div className={styles["ps-size"]}>?</div>
              </div>
              <div className={`${styles["ps-side"]} ${styles.after}`}>
                <div className={styles["ps-tag"]}>After</div>
                <div className={styles["ps-size"]}>?</div>
              </div>
            </div>
            <div className={styles["wall-body"]}>
              <div className={styles["wall-product"]}>
                {r.product_name || "Documented case"}
              </div>
              {r.brand && (
                <div className={styles["wall-brand"]}>{r.brand}</div>
              )}
              {r.signal_type && (
                <div className={styles["wall-signal"]}>
                  {humanSignal(r.signal_type)}
                </div>
              )}
            </div>
          </a>
        );
      })}
    </div>
  );
}
