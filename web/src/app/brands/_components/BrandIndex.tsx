"use client";
// Client component. Receives the full ranked brand list as props (all
// 1,167 rows from brand_index, prefetched server-side). Provides:
//   - search input that filters by brand name (case-insensitive)
//   - sort pills (most events, worst avg shrink, most products, A-Z)
//   - top-100 default + show-all toggle
// Rank badge stays canonical (computed once server-side from
// most-events-desc order), so it doesn't shift when the user re-sorts.
import { useMemo, useState } from "react";
import styles from "../styles.module.css";
import type { RankedBrand } from "../types";

type SortKey = "events" | "avg" | "products" | "name";
const INITIAL_LIMIT = 100;

interface Props {
  brands: RankedBrand[];
}

function num(s: string | number | null | undefined): number {
  if (s == null) return 0;
  const n = typeof s === "string" ? parseFloat(s) : s;
  return Number.isFinite(n) ? n : 0;
}

function compareBy(sort: SortKey) {
  return (a: RankedBrand, b: RankedBrand) => {
    switch (sort) {
      case "events":
        return b.shrinkflation_events - a.shrinkflation_events;
      case "avg":
        return num(a.avg_shrink_per_event) - num(b.avg_shrink_per_event);
      case "products":
        return b.product_count - a.product_count;
      case "name":
        return a.brand.localeCompare(b.brand);
    }
  };
}

function brandHref(brand: string): string {
  // The /brands/[name] dynamic route does decodeURIComponent().toLowerCase()
  // then ilike()-matches against the DB. So URL-encoding the lowercase
  // brand name preserves accents and special chars round-trip.
  return `/brands/${encodeURIComponent(brand.toLowerCase())}`;
}

export default function BrandIndex({ brands }: Props) {
  const [sort, setSort] = useState<SortKey>("events");
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState(false);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    const filtered = q
      ? brands.filter((b) => b.brand.toLowerCase().includes(q))
      : brands;
    return [...filtered].sort(compareBy(sort));
  }, [brands, sort, query]);

  const showAll = expanded || visible.length <= INITIAL_LIMIT;
  const shown = showAll ? visible : visible.slice(0, INITIAL_LIMIT);

  return (
    <>
      <div className={styles.controls}>
        <input
          className={styles["search-input"]}
          placeholder="Filter brands…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoComplete="off"
        />
        <div className={styles["sort-pills"]}>
          {(
            [
              ["events", "Most events"],
              ["avg", "Worst avg shrink"],
              ["products", "Most products"],
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

      <div className={styles["results-meta"]}>
        {query.trim() ? (
          <>
            <strong>{visible.length}</strong> of {brands.length} brands match
            &ldquo;{query.trim()}&rdquo;
          </>
        ) : (
          <>
            <strong>{brands.length}</strong> brands tracked
          </>
        )}
      </div>

      {visible.length === 0 ? (
        <div className={styles.empty}>No brands match your filter</div>
      ) : (
        <div className={styles.grid}>
          {shown.map((b) => {
            const events = b.shrinkflation_events;
            const products = b.product_count;
            const avg = num(b.avg_shrink_per_event);
            const lastDay = (b.last_detected || "").slice(0, 10);
            return (
              <a
                key={b.brand}
                href={brandHref(b.brand)}
                className={styles.card}
              >
                <span
                  className={`${styles["card-rank"]} ${b.rank <= 10 ? styles.top10 : ""}`}
                >
                  #{b.rank}
                </span>
                <div className={styles["card-img"]}>
                  {b.thumbnail ? (
                    <img src={b.thumbnail} alt="" loading="lazy" />
                  ) : (
                    <div className={styles["card-placeholder"]}>
                      <span className={styles["card-placeholder-name"]}>
                        {b.brand}
                      </span>
                    </div>
                  )}
                </div>
                <div className={styles["card-body"]}>
                  <span className={styles["card-brand"]}>{b.brand}</span>
                  <div className={styles["card-stats"]}>
                    <div className={styles["card-stat"]}>
                      <span className={`${styles.v} ${styles.red}`}>
                        {events}
                      </span>
                      <span className={styles.l}>events</span>
                    </div>
                    <div className={styles["card-stat"]}>
                      <span className={styles.v}>{products}</span>
                      <span className={styles.l}>products</span>
                    </div>
                    <div className={styles["card-stat"]}>
                      <span className={`${styles.v} ${styles.red}`}>
                        {avg.toFixed(1)}%
                      </span>
                      <span className={styles.l}>avg</span>
                    </div>
                  </div>
                  <div className={styles["card-foot"]}>
                    Last seen {lastDay}
                  </div>
                </div>
              </a>
            );
          })}
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
            {expanded ? "Show top 100" : `Show all ${visible.length} brands`}{" "}
            <span className={styles.arrow}>↓</span>
          </button>
        </div>
      )}
    </>
  );
}
