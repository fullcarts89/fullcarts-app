"use client";
// Client component. Receives `products` as props (all data prefetched
// server-side from product_entities + event aggregates). Adds interactive
// sort pills, name search, and a top-25 + show-all toggle. Cards link
// to the per-product detail page at /products/[entity_id].
import { useMemo, useState } from "react";
import styles from "../styles.module.css";
import type { ProductRollup } from "../types";

type SortKey = "image" | "worst" | "events" | "name";
const INITIAL_LIMIT = 25;

interface Props {
  products: ProductRollup[];
  brand: string;
}

function compareBy(sort: SortKey) {
  return (a: ProductRollup, b: ProductRollup) => {
    switch (sort) {
      case "image": {
        const ha = a.image_url ? 1 : 0;
        const hb = b.image_url ? 1 : 0;
        if (hb !== ha) return hb - ha;
        return a.worst_delta_pct - b.worst_delta_pct;
      }
      case "worst":
        return a.worst_delta_pct - b.worst_delta_pct;
      case "events":
        return b.event_count - a.event_count;
      case "name":
        return a.canonical_name.localeCompare(b.canonical_name);
    }
  };
}

export default function ProductGrid({ products, brand }: Props) {
  const [sort, setSort] = useState<SortKey>("image");
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState(false);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    const filtered = q
      ? products.filter((p) =>
          p.canonical_name.toLowerCase().includes(q),
        )
      : products;
    return [...filtered].sort(compareBy(sort));
  }, [products, sort, query]);

  const showAll = expanded || visible.length <= INITIAL_LIMIT;
  const shown = showAll ? visible : visible.slice(0, INITIAL_LIMIT);

  return (
    <section className={styles.block}>
      <div className={styles["section-head"]}>
        <h2>All {brand} products</h2>
        <div className={styles.meta}>
          {products.length} distinct products with documented changes
        </div>
      </div>
      <div className={styles.controls}>
        <input
          className={styles["search-input"]}
          placeholder="Filter products…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoComplete="off"
        />
        <div className={styles["sort-pills"]}>
          {(
            [
              ["image", "With photo first"],
              ["worst", "Worst shrink"],
              ["events", "Most events"],
              ["name", "A–Z"],
            ] as [SortKey, string][]
          ).map(([k, label]) => (
            <button
              key={k}
              type="button"
              className={`${styles["sort-pill"]} ${sort === k ? styles.active : ""}`}
              onClick={() => setSort(k)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {visible.length === 0 ? (
        <div className={styles["products-empty"]}>No matching products</div>
      ) : (
        <div className={styles["products-grid"]}>
          {shown.map((p) => (
            <a
              key={p.entity_id}
              className={styles["product-card"]}
              href={`/products/${p.entity_id}`}
            >
              {p.image_url ? (
                <div className={styles["product-thumb"]}>
                  <img src={p.image_url} alt={`${brand} ${p.canonical_name} package`} loading="lazy" />
                  {p.lead_source_type && p.lead_source_type !== "reddit" && (
                    <span className={styles["img-tag-sm"]}>News</span>
                  )}
                </div>
              ) : (
                <div
                  className={`${styles["product-thumb"]} ${styles["placeholder-stub-sm"]}`}
                >
                  <span className={styles["ps-tag-sm"]}>No archive</span>
                  <span className={styles["ps-name-sm"]}>{p.canonical_name}</span>
                  <span className={styles["ps-mark-sm"]}>{brand}</span>
                </div>
              )}
              <div className={styles["product-name"]}>{p.canonical_name}</div>
              <div className={styles["product-stats"]}>
                <span className={styles.events}>
                  {p.event_count} event{p.event_count === 1 ? "" : "s"}
                </span>
                <span className={styles.delta}>
                  {p.worst_delta_pct === 0
                    ? "—"
                    : `${p.worst_delta_pct.toFixed(1)}%`}
                </span>
              </div>
            </a>
          ))}
        </div>
      )}

      {visible.length > INITIAL_LIMIT && (
        <div className={styles["expand-row"]}>
          <span>
            Showing {shown.length} of {visible.length}
          </span>
          <button
            type="button"
            className={`${styles["expand-btn"]} ${expanded ? styles.collapse : ""}`}
            onClick={() => setExpanded((x) => !x)}
          >
            {expanded ? "Show fewer" : "Show all"}{" "}
            <span className={styles.arrow}>↓</span>
          </button>
        </div>
      )}
    </section>
  );
}
