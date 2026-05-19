// Corporate-parent tree section. Shows the top N manufacturers across
// our brand catalog, each with a sample of their child brands so users
// can see that "Cadbury" / "Oreo" / "Wheat Thins" are all the same
// parent (Mondelez).
//
// Empty state: until the Wikidata backfill has populated
// product_entities.manufacturer, the view is empty and we render a
// placeholder explaining the lag.
import styles from "../styles.module.css";
import type { CorporateNode } from "../types";

interface Props {
  nodes: CorporateNode[];
}

function num(v: number | string | null | undefined): number {
  if (v == null) return 0;
  const n = typeof v === "string" ? parseFloat(v) : v;
  return Number.isFinite(n) ? n : 0;
}

export default function CorporateTree({ nodes }: Props) {
  if (nodes.length === 0) {
    return (
      <div className={styles["corp-empty"]}>
        Manufacturer data is still being backfilled from Wikidata. Check
        back next week — coverage expands ~200 brands/week.
      </div>
    );
  }

  return (
    <div className={styles["corp-grid"]}>
      {nodes.map((n, i) => {
        const worst = num(n.worst_delta_pct);
        const events = n.total_shrinkflation_events ?? 0;
        return (
          <div key={n.manufacturer} className={styles["corp-card"]}>
            <div className={styles["corp-rank"]}>#{i + 1}</div>
            <div className={styles["corp-head"]}>
              <div className={styles["corp-name"]}>{n.manufacturer}</div>
              <div className={styles["corp-meta"]}>
                {n.distinct_brands} brand
                {n.distinct_brands === 1 ? "" : "s"} · {events} event
                {events === 1 ? "" : "s"}
              </div>
            </div>
            <div className={styles["corp-stat"]}>
              <span className={`${styles["corp-stat-v"]} ${styles.red}`}>
                {worst ? `${worst.toFixed(1)}%` : "—"}
              </span>
              <span className={styles["corp-stat-l"]}>worst single shrink</span>
            </div>
            <div className={styles["corp-children"]}>
              {(n.top_brands ?? []).map((b) => (
                <a
                  key={b.brand}
                  href={`/brands/${encodeURIComponent(b.brand.toLowerCase())}`}
                  className={styles["corp-child"]}
                >
                  <div className={styles["corp-child-thumb"]}>
                    {b.thumbnail ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={b.thumbnail}
                        alt={`${b.brand} product photo`}
                        loading="lazy"
                      />
                    ) : (
                      <div className={styles["corp-child-placeholder"]}>
                        {b.brand.slice(0, 1)}
                      </div>
                    )}
                  </div>
                  <div className={styles["corp-child-body"]}>
                    <div className={styles["corp-child-brand"]}>{b.brand}</div>
                    <div className={styles["corp-child-events"]}>
                      {b.events ?? 0} event{b.events === 1 ? "" : "s"}
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
