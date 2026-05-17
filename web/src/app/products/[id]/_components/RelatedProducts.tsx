// Server component. Same-brand product cards, sorted by event count.
// Caps at 8. Each card links to its own /products/[id] page. If the
// other product has no image_url, falls back to the same placeholder
// pattern used in the brand-page ProductGrid.
import styles from "../styles.module.css";
import type { RelatedProduct } from "../types";

interface Props {
  brand: string;
  products: RelatedProduct[];
}

const SHOW_N = 8;

export default function RelatedProducts({ brand, products }: Props) {
  const top = products.slice(0, SHOW_N);
  if (top.length === 0) return null;

  return (
    <div className={styles["related-grid"]}>
      {top.map((p) => (
        <a
          key={p.entity_id}
          className={styles["related-card"]}
          href={`/products/${p.entity_id}`}
        >
          {p.image_url ? (
            <div className={styles["related-thumb"]}>
              <img src={p.image_url} alt={p.canonical_name} loading="lazy" />
            </div>
          ) : (
            <div
              className={`${styles["related-thumb"]} ${styles.placeholder}`}
            >
              <span className={styles["ps-tag-sm"]}>{brand}</span>
              <span className={styles["ps-name-sm"]}>{p.canonical_name}</span>
            </div>
          )}
          <div className={styles["related-name"]}>{p.canonical_name}</div>
          <div className={styles["related-stats"]}>
            <span className={styles.ev}>
              {p.event_count} event{p.event_count === 1 ? "" : "s"}
            </span>
            <span className={styles.delta}>
              {p.worst_delta_pct === 0
                ? "—"
                : `${p.worst_delta_pct.toFixed(0)}%`}
            </span>
          </div>
        </a>
      ))}
    </div>
  );
}
