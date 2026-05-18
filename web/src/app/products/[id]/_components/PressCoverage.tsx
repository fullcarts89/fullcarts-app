// Press coverage section. Surfaces every Consumer Reports finding
// matched to this entity (via match_consumer_reports.py). One card per
// CR article reference; clicking opens the original article.
import styles from "../styles.module.css";
import type { ConsumerReportRef } from "../types";

interface Props {
  refs: ConsumerReportRef[];
}

function formatDate(iso: string | null): string {
  if (!iso) return "";
  return iso.slice(0, 10);
}

export default function PressCoverage({ refs }: Props) {
  if (refs.length === 0) return null;
  return (
    <div className={styles["press-grid"]}>
      {refs.map((r) => (
        <a
          key={r.id}
          href={r.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className={styles["press-card"]}
        >
          <div className={styles["press-pill"]}>Consumer Reports</div>
          <div className={styles["press-title"]}>{r.title}</div>
          {r.excerpt && (
            <div className={styles["press-excerpt"]}>“{r.excerpt}”</div>
          )}
          <div className={styles["press-foot"]}>
            {formatDate(r.published_at) || "Date unknown"}
            <span className={styles["press-link"]}>Read on CR ↗</span>
          </div>
        </a>
      ))}
    </div>
  );
}
