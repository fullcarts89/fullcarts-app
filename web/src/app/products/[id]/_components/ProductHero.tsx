// Server component. Renders the split product hero: image card on the
// left (real image or styled placeholder), info block on the right
// (name, brand/category/manufacturer chips, tagline, 4-stat strip).
import Link from "next/link";
import styles from "../styles.module.css";
import SafeImage from "../../../_components/SafeImage";
import type { EventRow, PackVariant, ProductEntity } from "../types";
import {
  biggestSingleDrop,
  buildTrajectory,
  cumulativeShrinkPct,
  isoDay,
} from "../lib";

interface Props {
  entity: ProductEntity;
  events: EventRow[];
  variants: PackVariant[];
}

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function monthYear(iso: string): string {
  const d = iso.slice(0, 10);
  const parts = d.split("-");
  if (parts.length !== 3) return d;
  const m = parseInt(parts[1], 10) - 1;
  return `${MONTHS[m] || ""} ${parts[0]}`;
}

export default function ProductHero({ entity, events, variants }: Props) {
  const trajectory = buildTrajectory(events);
  const cumulative = cumulativeShrinkPct(trajectory);
  const biggest = biggestSingleDrop(events);

  // Date bookends from the event list.
  const dates = events
    .map((e) => isoDay(e.observed_date))
    .filter(Boolean)
    .sort();
  const firstYear = dates[0]?.slice(0, 4) || "";
  const lastUpdate = dates[dates.length - 1] || "";

  // First UPC we have, for the chip strip.
  const primaryUpc = variants.find((v) => v.upc)?.upc || null;

  // First and last sizes for the tagline.
  const firstStep = trajectory[0];
  const lastStep = trajectory[trajectory.length - 1];
  const unit = events[0]?.size_unit || "";

  const eventCount = events.length;

  return (
    <header className={styles["product-hero"]}>
      <div className={styles["hero-image"]}>
        {entity.image_url ? (
          <>
            <SafeImage
              src={entity.image_url}
              alt={`${entity.brand} ${entity.canonical_name}${
                lastStep ? ` · current size ${lastStep.size}${unit}` : ""
              } package photo`}
              fill
              priority
              sizes="(min-width: 980px) 400px, 100vw"
            />
            <span className={styles["img-tag"]}>Tracked</span>
          </>
        ) : (
          <>
            <div className={styles["ps-tag"]}>
              {entity.brand}
              {entity.category ? ` · ${entity.category}` : ""}
            </div>
            <div className={styles["ps-name"]}>{entity.canonical_name}</div>
            <div className={styles["ps-brand-mark"]}>{entity.brand}</div>
            <span className={styles["img-tag"]}>Placeholder</span>
          </>
        )}
      </div>

      <div className={styles["hero-info"]}>
        <div className={styles["hero-pill"]}>
          Tracked product · {eventCount} documented{" "}
          {eventCount === 1 ? "shrink" : "shrinks"}
        </div>
        <h1>{entity.canonical_name}</h1>
        <div className={styles["hero-meta"]}>
          <Link href={`/brands/${encodeURIComponent(entity.brand.toLowerCase())}`}>
            {entity.brand}
          </Link>
          {entity.category && <span className={styles.chip}>{entity.category}</span>}
          {entity.manufacturer && (
            <span className={`${styles.chip} ${styles.parent}`}>
              {entity.manufacturer}
            </span>
          )}
          {primaryUpc && <span>Barcode {primaryUpc}</span>}
        </div>

        {firstStep && lastStep && firstStep !== lastStep ? (
          <p className={styles["hero-tagline"]}>
            First documented at{" "}
            <strong>
              {firstStep.size}
              {unit}
            </strong>{" "}
            in {firstStep.date.slice(0, 4)}. As of {monthYear(lastStep.date)},
            the same product is{" "}
            <strong>
              {lastStep.size}
              {unit}
            </strong>{" "}
            — a{" "}
            <strong>cumulative {Math.abs(cumulative).toFixed(0)}% reduction</strong>{" "}
            across {eventCount} documented event
            {eventCount === 1 ? "" : "s"}.
          </p>
        ) : (
          <p className={styles["hero-tagline"]}>
            {eventCount} documented size change
            {eventCount === 1 ? "" : "s"} since {firstYear}. See the full event
            list below.
          </p>
        )}

        <div className={styles["stat-grid"]}>
          <div className={styles.stat}>
            <div className={styles["stat-label"]}>Total events</div>
            <div className={styles["stat-value"]}>
              {eventCount}
            </div>
            <div className={styles["stat-meta"]}>
              documented {eventCount === 1 ? "shrink" : "shrinks"}
            </div>
          </div>
          <div className={styles.stat}>
            <div className={styles["stat-label"]}>Cumulative shrink</div>
            <div
              className={`${styles["stat-value"]} ${styles.red}`}
              title={
                cumulative < 0
                  ? undefined
                  : "Not enough events to compute a cumulative shrink — we need at least two size observations."
              }
              aria-label={
                cumulative < 0
                  ? `${cumulative.toFixed(0)}%`
                  : "Not enough events to compute cumulative shrink"
              }
            >
              {cumulative < 0 ? `${cumulative.toFixed(0)}%` : "—"}
            </div>
            <div className={styles["stat-meta"]}>
              {firstStep && lastStep
                ? `${firstStep.size}${unit} → ${lastStep.size}${unit}`
                : "no trajectory"}
            </div>
          </div>
          <div className={styles.stat}>
            <div className={styles["stat-label"]}>Biggest single drop</div>
            <div
              className={`${styles["stat-value"]} ${styles.red}`}
              title={
                biggest
                  ? undefined
                  : "We haven't recorded a size drop for this product yet."
              }
              aria-label={
                biggest
                  ? `${biggest.pct.toFixed(0)}%`
                  : "No size drop recorded yet"
              }
            >
              {biggest ? `${biggest.pct.toFixed(0)}%` : "—"}
            </div>
            <div className={styles["stat-meta"]}>
              {biggest
                ? `${biggest.before}${unit} → ${biggest.after}${unit} · ${monthYear(biggest.date)}`
                : "no measured drop"}
            </div>
          </div>
          <div className={styles.stat}>
            <div className={styles["stat-label"]}>First detected</div>
            <div
              className={styles["stat-value"]}
              title={
                firstYear
                  ? undefined
                  : "No detection date on file — this product may have been added manually."
              }
            >
              {firstYear || "—"}
            </div>
            <div className={styles["stat-meta"]}>
              last update {lastUpdate || "—"}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
