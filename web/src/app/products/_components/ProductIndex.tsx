"use client";
// Client component. Receives the full ranked product list as props
// (a few thousand rows from product_index, prefetched server-side).
// Mirrors /brands/_components/BrandIndex.tsx so the two index pages
// feel identical:
//   - category chip filter (case-insensitive merge, top 12 chips)
//   - search by brand or product name (case-insensitive substring)
//   - sort pills: most events / worst single shrink / worst avg / A-Z
//   - tier-grouped grid when sort=events & no filters
//   - flat grid otherwise
import { Fragment, useMemo, useState } from "react";
import styles from "../styles.module.css";
import type { RankedProduct } from "../types";

type SortKey = "events" | "worst" | "avg" | "name";
type Tier = 1 | 2 | 3 | 4;

const TIER_PREVIEW = 12;
const CHIP_LIMIT = 12;

interface Props {
  products: RankedProduct[];
}

function num(s: string | number | null | undefined): number {
  if (s == null) return 0;
  const n = typeof s === "string" ? parseFloat(s) : s;
  return Number.isFinite(n) ? n : 0;
}

function compareBy(sort: SortKey) {
  return (a: RankedProduct, b: RankedProduct) => {
    switch (sort) {
      case "events":
        return b.shrinkflation_events - a.shrinkflation_events;
      case "worst":
        // most-negative first
        return num(a.worst_delta_pct) - num(b.worst_delta_pct);
      case "avg":
        return num(a.avg_shrink_per_event) - num(b.avg_shrink_per_event);
      case "name":
        return (
          a.brand.localeCompare(b.brand) ||
          a.canonical_name.localeCompare(b.canonical_name)
        );
    }
  };
}

function tierOf(events: number): Tier {
  if (events >= 6) return 1;
  if (events >= 3) return 2;
  if (events >= 2) return 3;
  return 4;
}

const TIER_META: Record<Tier, { label: string; sub: string }> = {
  1: { label: "Chronic Offenders", sub: "6+ events" },
  2: { label: "Repeat Offenders", sub: "3–5 events" },
  3: { label: "Occasional", sub: "2 events" },
  4: { label: "Single Incident", sub: "1 event" },
};

function normCat(raw: string | null): string | null {
  if (!raw) return null;
  const s = raw.trim();
  if (!s) return null;
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
}

export default function ProductIndex({ products }: Props) {
  const [sort, setSort] = useState<SortKey>("events");
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string | null>(null);
  const [expandedTiers, setExpandedTiers] = useState<Set<Tier>>(new Set());
  const toggleTier = (t: Tier) =>
    setExpandedTiers((prev) => {
      const next = new Set(prev);
      if (next.has(t)) next.delete(t);
      else next.add(t);
      return next;
    });

  const { categoryChips, totalCategories } = useMemo(() => {
    const counts = new Map<string, number>();
    for (const p of products) {
      const c = normCat(p.category);
      if (!c) continue;
      counts.set(c, (counts.get(c) || 0) + 1);
    }
    const sorted = [...counts.entries()]
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count);
    return {
      categoryChips: sorted.slice(0, CHIP_LIMIT),
      totalCategories: sorted.length,
    };
  }, [products]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return products.filter((p) => {
      if (q) {
        const hay =
          p.brand.toLowerCase() + " " + p.canonical_name.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      if (category && normCat(p.category) !== category) return false;
      return true;
    });
  }, [products, query, category]);

  const sorted = useMemo(
    () => [...filtered].sort(compareBy(sort)),
    [filtered, sort],
  );

  const tiersActive =
    sort === "events" && !query.trim() && category === null;

  const byTier = useMemo(() => {
    const m: Record<Tier, RankedProduct[]> = { 1: [], 2: [], 3: [], 4: [] };
    for (const p of sorted) m[tierOf(p.shrinkflation_events)].push(p);
    return m;
  }, [sorted]);

  return (
    <>
      <div className={styles["cat-strip"]}>
        <button
          type="button"
          className={`${styles["cat-chip"]} ${category === null ? styles.active : ""}`}
          onClick={() => setCategory(null)}
        >
          All{" "}
          <span className={styles["cat-chip-count"]}>{products.length}</span>
        </button>
        {categoryChips.map((c) => (
          <button
            key={c.name}
            type="button"
            className={`${styles["cat-chip"]} ${category === c.name ? styles.active : ""}`}
            onClick={() =>
              setCategory(category === c.name ? null : c.name)
            }
          >
            {c.name}{" "}
            <span className={styles["cat-chip-count"]}>{c.count}</span>
          </button>
        ))}
      </div>

      <div className={styles.controls}>
        <input
          className={styles["search-input"]}
          placeholder="Filter by brand or product name…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoComplete="off"
        />
        <div className={styles["sort-pills"]}>
          {(
            [
              ["events", "Most events"],
              ["worst", "Worst single shrink"],
              ["avg", "Worst avg shrink"],
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
        {query.trim() || category ? (
          <>
            <strong>{filtered.length}</strong> of {products.length} products
            {category && (
              <>
                {" "}in <strong>{category}</strong>
              </>
            )}
            {query.trim() && (
              <>
                {" "}matching <strong>&ldquo;{query.trim()}&rdquo;</strong>
              </>
            )}
          </>
        ) : (
          <>
            <strong>{products.length.toLocaleString()}</strong> products
            tracked across <strong>{totalCategories}</strong> categories
          </>
        )}
      </div>

      {sorted.length === 0 ? (
        <div className={styles.empty}>No products match your filters</div>
      ) : tiersActive ? (
        <div className={styles.grid}>
          {([1, 2, 3, 4] as Tier[]).map((t) => {
            const tierProducts = byTier[t];
            if (tierProducts.length === 0) return null;
            const isExpanded = expandedTiers.has(t);
            const shown = isExpanded
              ? tierProducts
              : tierProducts.slice(0, TIER_PREVIEW);
            const hasMore = tierProducts.length > TIER_PREVIEW;
            return (
              <Fragment key={t}>
                <div className={styles.tier}>
                  <span
                    className={`${styles["tier-label"]} ${styles[`tier-${t}`]}`}
                  >
                    {TIER_META[t].label}
                  </span>
                  <span className={styles["tier-meta"]}>
                    {TIER_META[t].sub} · {tierProducts.length.toLocaleString()} product
                    {tierProducts.length === 1 ? "" : "s"}
                    {hasMore && !isExpanded && (
                      <>
                        {" "}· showing top {TIER_PREVIEW}
                      </>
                    )}
                  </span>
                </div>
                {shown.map((p) => renderCard(p))}
                {hasMore && (
                  <div className={styles["tier-toggle"]}>
                    <button
                      type="button"
                      className={`${styles["tier-toggle-btn"]} ${isExpanded ? styles.open : ""}`}
                      onClick={() => toggleTier(t)}
                    >
                      {isExpanded
                        ? `Show top ${TIER_PREVIEW}`
                        : `Show all ${tierProducts.length.toLocaleString()} ${TIER_META[t].label.toLowerCase()}`}{" "}
                      <span className={styles.arrow}>↓</span>
                    </button>
                  </div>
                )}
              </Fragment>
            );
          })}
        </div>
      ) : (
        <div className={styles.grid}>{sorted.map((p) => renderCard(p))}</div>
      )}
    </>
  );

  function renderCard(p: RankedProduct) {
    const events = p.shrinkflation_events;
    const worst = num(p.worst_delta_pct);
    const avg = num(p.avg_shrink_per_event);
    const lastDay = (p.last_detected || "").slice(0, 10);
    return (
      <a
        key={p.entity_id}
        href={`/products/${p.entity_id}`}
        className={styles.card}
      >
        <span
          className={`${styles["card-rank"]} ${p.rank <= 10 ? styles.top10 : ""}`}
        >
          #{p.rank}
        </span>
        <div className={styles["card-img"]}>
          {p.image_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={p.image_url} alt="" loading="lazy" />
          ) : (
            <div className={styles["card-placeholder"]}>
              <span className={styles["card-placeholder-name"]}>
                {p.canonical_name}
              </span>
            </div>
          )}
        </div>
        <div className={styles["card-body"]}>
          <span className={styles["card-brand-tag"]}>{p.brand}</span>
          <span className={styles["card-name"]}>{p.canonical_name}</span>
          <div className={styles["card-stats"]}>
            <div className={styles["card-stat"]}>
              <span className={`${styles.v} ${styles.red}`}>{events}</span>
              <span className={styles.l}>events</span>
            </div>
            <div className={styles["card-stat"]}>
              <span className={`${styles.v} ${styles.red}`}>
                {worst ? `${worst.toFixed(1)}%` : "—"}
              </span>
              <span className={styles.l}>worst</span>
            </div>
            <div className={styles["card-stat"]}>
              <span className={`${styles.v} ${styles.red}`}>
                {avg ? `${avg.toFixed(1)}%` : "—"}
              </span>
              <span className={styles.l}>avg</span>
            </div>
          </div>
          <div className={styles["card-foot"]}>
            {lastDay ? `Last seen ${lastDay}` : "—"}
          </div>
        </div>
      </a>
    );
  }
}
