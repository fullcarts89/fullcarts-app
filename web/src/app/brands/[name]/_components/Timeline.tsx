// Server component. Year-bar chart of events. Year range derives from
// ranking.first_detected and ranking.last_detected; bar counts derive from
// `events`. Bar heights are normalised against the max year-count so a
// brand with 30 events in its busiest year looks the same as one with 3.
import styles from "../styles.module.css";
import type { BrandRanking, EventRow } from "../types";
import { timelineBuckets } from "../lib";

interface Props {
  ranking: BrandRanking;
  events: EventRow[];
}

const MAX_BAR_PX = 180;
const ZERO_BAR_PX = 2;

export default function Timeline({ ranking, events }: Props) {
  const buckets = timelineBuckets(
    events,
    ranking.first_detected,
    ranking.last_detected,
  );
  if (buckets.length === 0) return null;

  const max = buckets.reduce((m, b) => Math.max(m, b.count), 0);
  const yearSpan = buckets.length;

  return (
    <section className={styles.block}>
      <div className={styles["section-head"]}>
        <h2>{yearSpan} years of shrinking</h2>
        <div className={styles.meta}>Events per year</div>
      </div>
      <div className={styles.timeline}>
        {buckets.map((b) => {
          const isZero = b.count === 0;
          const heightPx = isZero
            ? ZERO_BAR_PX
            : max > 0
              ? Math.max(6, Math.round((b.count / max) * MAX_BAR_PX))
              : ZERO_BAR_PX;
          const yy = String(b.year).slice(-2);
          return (
            <div key={b.year} className={styles["bar-wrap"]}>
              <div
                className={`${styles.bar} ${isZero ? styles.zero : ""}`}
                style={{ height: `${heightPx}px` }}
              >
                <div
                  className={`${styles["bar-count"]} ${isZero ? styles.zero : ""}`}
                >
                  {b.count}
                </div>
              </div>
              <div className={styles["bar-year"]}>{yy}</div>
            </div>
          );
        })}
      </div>
      <div className={styles["timeline-caveat"]}>
        Gaps for early years mean no documented claims, not no shrinkflation
        events. Reddit&apos;s r/shrinkflation was founded in 2013 and news
        coverage of shrinkflation only became routine after 2021.
      </div>
    </section>
  );
}
