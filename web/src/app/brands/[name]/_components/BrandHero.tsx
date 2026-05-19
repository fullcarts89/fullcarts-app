// Server component. All numbers derive from `ranking` (brand_rankings view).
// `manufacturer` is the most-common product_entities.manufacturer value; null
// if no entity has one populated, in which case the "Owned by" line is omitted.
import styles from "../styles.module.css";
import type { BrandRanking } from "../types";
import { num, isoDay } from "../lib";

interface Props {
  ranking: BrandRanking;
  manufacturer: string | null;
}

export default function BrandHero({ ranking, manufacturer }: Props) {
  const events = ranking.shrinkflation_events;
  const products = ranking.product_count;
  const avgShrink = num(ranking.avg_shrink_per_event);
  const firstYear = ranking.first_detected.slice(0, 4);
  const lastUpdate = isoDay(ranking.last_detected);

  return (
    <header className={styles.hero}>
      <div className={styles["hero-rank"]}>Wall of Shame · Documented Brand</div>
      <h1>{ranking.brand}</h1>
      <p className={styles["hero-sub"]}>
        {manufacturer && (
          <>
            Owned by <strong>{manufacturer}</strong>.{" "}
          </>
        )}
        We&apos;ve documented{" "}
        <strong>
          {events} shrinkflation event{events === 1 ? "" : "s"}
        </strong>{" "}
        across <strong>{products} products</strong> since {firstYear}, with an
        average size reduction of{" "}
        <strong>{Math.abs(avgShrink).toFixed(1)}%</strong> per event.
      </p>
      <div className={styles["stat-grid"]}>
        <div className={styles.stat}>
          <div className={styles["stat-label"]}>Total events</div>
          <div className={styles["stat-value"]}>{events}</div>
          <div className={styles["stat-meta"]}>documented shrinkflations</div>
        </div>
        <div className={styles.stat}>
          <div className={styles["stat-label"]}>Products tracked</div>
          <div className={styles["stat-value"]}>{products}</div>
          <div className={styles["stat-meta"]}>in our catalog</div>
        </div>
        <div className={styles.stat}>
          <div className={styles["stat-label"]}>Avg shrinkage</div>
          <div className={`${styles["stat-value"]} ${styles.red}`}>
            {avgShrink.toFixed(1)}%
          </div>
          <div className={styles["stat-meta"]}>per event</div>
        </div>
        <div className={styles.stat}>
          <div className={styles["stat-label"]}>First detected</div>
          <div className={styles["stat-value"]}>{firstYear}</div>
          <div className={styles["stat-meta"]}>last update {lastUpdate}</div>
        </div>
      </div>
    </header>
  );
}
