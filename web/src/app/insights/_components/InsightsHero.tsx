// Server component. Top of page: eyebrow pill with the page update
// date, headline ("The size of shrinkflation, measured"), and a lede
// paragraph that anchors the page against BLS and FRED. Numbers are
// pulled live from dashboard_stats().
import styles from "../styles.module.css";
import type { DashboardStats } from "../types";

interface Props {
  stats: DashboardStats;
  lastUpdated: string;
}

export default function InsightsHero({ stats, lastUpdated }: Props) {
  return (
    <header className={styles.hero}>
      <div className={styles["hero-eyebrow"]}>
        By the numbers · Updated {lastUpdated}
      </div>
      <h1>
        The size of <span className={styles.red}>shrinkflation</span>, measured.
      </h1>
      <p className={styles["hero-lede"]}>
        We cross-reference our database of{" "}
        <strong>
          {stats.total_changes.toLocaleString()} documented events
        </strong>{" "}
        against the government&apos;s official size-change tracker (the{" "}
        <strong>Bureau of Labor Statistics</strong>&apos; R-CPI-SC index) and
        the <strong>Federal Reserve&apos;s</strong> Food-at-Home price index,
        so you can see whether brands are shrinking products on schedule
        with — or ahead of — official inflation.
      </p>
    </header>
  );
}
