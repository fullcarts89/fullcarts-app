// Server component. Recent news_feed rows about tracked products,
// outlet + headline + summary + linked-product count. External link
// to the original article.
import styles from "../styles.module.css";
import { isoDay } from "../lib";
import type { NewsFeedRow } from "../types";

interface Props {
  rows: NewsFeedRow[];
}

export default function NewsFeed({ rows }: Props) {
  if (rows.length === 0) {
    return <div className={styles.empty}>No news articles indexed yet</div>;
  }
  return (
    <div className={styles["news-list"]}>
      {rows.map((r) => (
        <a
          key={r.id}
          className={styles["news-row"]}
          href={r.url}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`${r.title} — ${r.outlet || "external article"} (opens in new tab)`}
        >
          <div className={styles["news-outlet"]}>
            {r.outlet || "Unknown outlet"}
          </div>
          <div>
            <div className={styles["news-title"]}>{r.title}</div>
            {r.summary && (
              <div className={styles["news-summary"]}>{r.summary}</div>
            )}
          </div>
          <div className={styles["news-products"]}>
            <span className={styles.n}>{r.linked_products_count}</span>{" "}
            tracked product{r.linked_products_count === 1 ? "" : "s"}
          </div>
          <div className={styles["news-date"]}>{isoDay(r.published_at)}</div>
        </a>
      ))}
    </div>
  );
}
