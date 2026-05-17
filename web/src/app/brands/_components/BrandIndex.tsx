"use client";
// Client component. Receives the full ranked brand list as props
// (~1.2k rows from brand_index, prefetched server-side). Provides:
//   - category chip filter (single-select; categories normalised
//     case-insensitively to merge "Snacks" / "snacks" duplicates)
//   - search by brand name (case-insensitive substring)
//   - sort pills: most events / worst avg / most products / A-Z
//   - tier-grouped grid when sort=events & no filters (Chronic /
//     Repeat / Occasional / Single-incident), with the Single-Incident
//     tier collapsed by default behind a toggle
//   - flat grid otherwise
import { Fragment, useMemo, useState } from "react";
import styles from "../styles.module.css";
import type { RankedBrand } from "../types";

type SortKey = "events" | "avg" | "products" | "name";
type Tier = 1 | 2 | 3 | 4;

// Number of brand cards shown per tier before user expands. Three rows
// of four at 1280px width — enough to make the tier's character clear
// without dominating the page.
const TIER_PREVIEW = 12;

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
  return `/brands/${encodeURIComponent(brand.toLowerCase())}`;
}

function tierOf(events: number): Tier {
  if (events >= 11) return 1;
  if (events >= 6) return 2;
  if (events >= 2) return 3;
  return 4;
}

const TIER_META: Record<Tier, { label: string; sub: string }> = {
  1: { label: "Chronic Offenders", sub: "11+ events" },
  2: { label: "Repeat Offenders", sub: "6–10 events" },
  3: { label: "Occasional", sub: "2–5 events" },
  4: { label: "Single Incident", sub: "1 event" },
};

/** Normalise a category to title-case canonical form so "Snacks" and
 *  "snacks" merge into one chip. */
function normCat(raw: string | null): string | null {
  if (!raw) return null;
  const s = raw.trim();
  if (!s) return null;
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
}

export default function BrandIndex({ brands }: Props) {
  const [sort, setSort] = useState<SortKey>("events");
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string | null>(null);
  // Track which tiers are expanded. Each tier previews TIER_PREVIEW
  // cards by default; toggle expands to all brands in that tier.
  const [expandedTiers, setExpandedTiers] = useState<Set<Tier>>(new Set());
  const toggleTier = (t: Tier) =>
    setExpandedTiers((prev) => {
      const next = new Set(prev);
      if (next.has(t)) next.delete(t);
      else next.add(t);
      return next;
    });

  // Category chip strip data: normalised category → brand count.
  // Cap rendered chips to the top N most-populated categories; the
  // long tail of niche categories is reachable via the name search
  // instead. Also track the total category count for the meta line.
  const CHIP_LIMIT = 12;
  const { categoryChips, totalCategories } = useMemo(() => {
    const counts = new Map<string, number>();
    for (const b of brands) {
      const c = normCat(b.primary_category);
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
  }, [brands]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return brands.filter((b) => {
      if (q && !b.brand.toLowerCase().includes(q)) return false;
      if (category && normCat(b.primary_category) !== category) return false;
      return true;
    });
  }, [brands, query, category]);

  const sorted = useMemo(
    () => [...filtered].sort(compareBy(sort)),
    [filtered, sort],
  );

  const tiersActive =
    sort === "events" && !query.trim() && category === null;

  // Bucket by tier when tiering is active
  const byTier = useMemo(() => {
    const m: Record<Tier, RankedBrand[]> = { 1: [], 2: [], 3: [], 4: [] };
    for (const b of sorted) m[tierOf(b.shrinkflation_events)].push(b);
    return m;
  }, [sorted]);

  return (
    <>
      {/* Category chip strip */}
      <div className={styles["cat-strip"]}>
        <button
          type="button"
          className={`${styles["cat-chip"]} ${category === null ? styles.active : ""}`}
          onClick={() => setCategory(null)}
        >
          All <span className={styles["cat-chip-count"]}>{brands.length}</span>
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

      {/* Search + sort */}
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
        {query.trim() || category ? (
          <>
            <strong>{filtered.length}</strong> of {brands.length} brands
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
            <strong>{brands.length}</strong> brands tracked across{" "}
            <strong>{totalCategories}</strong> categories
          </>
        )}
      </div>

      {sorted.length === 0 ? (
        <div className={styles.empty}>No brands match your filters</div>
      ) : tiersActive ? (
        <div className={styles.grid}>
          {([1, 2, 3, 4] as Tier[]).map((t) => {
            const tierBrands = byTier[t];
            if (tierBrands.length === 0) return null;
            const isExpanded = expandedTiers.has(t);
            const shown = isExpanded
              ? tierBrands
              : tierBrands.slice(0, TIER_PREVIEW);
            const hasMore = tierBrands.length > TIER_PREVIEW;
            return (
              <Fragment key={t}>
                <div className={styles.tier}>
                  <span
                    className={`${styles["tier-label"]} ${styles[`tier-${t}`]}`}
                  >
                    {TIER_META[t].label}
                  </span>
                  <span className={styles["tier-meta"]}>
                    {TIER_META[t].sub} · {tierBrands.length} brand
                    {tierBrands.length === 1 ? "" : "s"}
                    {hasMore && !isExpanded && (
                      <>
                        {" "}· showing top {TIER_PREVIEW}
                      </>
                    )}
                  </span>
                </div>
                {shown.map((b) => renderCard(b))}
                {hasMore && (
                  <div className={styles["tier-toggle"]}>
                    <button
                      type="button"
                      className={`${styles["tier-toggle-btn"]} ${isExpanded ? styles.open : ""}`}
                      onClick={() => toggleTier(t)}
                    >
                      {isExpanded
                        ? `Show top ${TIER_PREVIEW}`
                        : `Show all ${tierBrands.length} ${TIER_META[t].label.toLowerCase()}`}{" "}
                      <span className={styles.arrow}>↓</span>
                    </button>
                  </div>
                )}
              </Fragment>
            );
          })}
        </div>
      ) : (
        <div className={styles.grid}>{sorted.map((b) => renderCard(b))}</div>
      )}
    </>
  );

  function renderCard(b: RankedBrand) {
    const events = b.shrinkflation_events;
    const products = b.product_count;
    const avg = num(b.avg_shrink_per_event);
    const lastDay = (b.last_detected || "").slice(0, 10);
    return (
      <a key={b.brand} href={brandHref(b.brand)} className={styles.card}>
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
              <span className={styles["card-placeholder-name"]}>{b.brand}</span>
            </div>
          )}
        </div>
        <div className={styles["card-body"]}>
          <span className={styles["card-brand"]}>{b.brand}</span>
          <div className={styles["card-stats"]}>
            <div className={styles["card-stat"]}>
              <span className={`${styles.v} ${styles.red}`}>{events}</span>
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
          <div className={styles["card-foot"]}>Last seen {lastDay}</div>
        </div>
      </a>
    );
  }
}
