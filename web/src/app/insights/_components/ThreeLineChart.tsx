// Server component. Macro time-series chart: FullCarts events
// (red, filled area below), BLS downsizings (blue dashed), FRED
// food-at-home CPI YoY% (amber), and Google Trends interest for
// "shrinkflation" (purple, dashed). Events + BLS share the left
// axis (both counts); CPI and Trends each ride the right axis
// because their scales are dimensionless.
//
// Pure SVG, no client JS. Skips a series entirely when it has no
// usable points. Empty state if all three series are empty.
import styles from "../styles.module.css";
import type { ChartPoint } from "../types";
import { monthLabel, niceAxis } from "../lib";

interface Props {
  points: ChartPoint[];
}

const VB_W = 1000;
const VB_H = 240;
const X_TICK_COUNT = 7;

function buildPath(
  points: ChartPoint[],
  valueOf: (p: ChartPoint) => number | null,
  xOf: (i: number) => number,
  yOf: (v: number) => number,
): string {
  let d = "";
  let pen = false;
  points.forEach((p, i) => {
    const v = valueOf(p);
    if (v == null) {
      pen = false;
      return;
    }
    const cmd = pen ? "L" : "M";
    d += `${cmd}${xOf(i).toFixed(2)},${yOf(v).toFixed(2)} `;
    pen = true;
  });
  return d.trim();
}

function buildAreaPath(
  points: ChartPoint[],
  valueOf: (p: ChartPoint) => number | null,
  xOf: (i: number) => number,
  yOf: (v: number) => number,
): string {
  // Closed polygon: line at top, dropping to bottom of viewport at
  // each end of the contiguous span. Treats null gaps the same as
  // the line itself — emits a separate sub-polygon per contiguous run.
  let d = "";
  let runStart = -1;
  const flush = (end: number) => {
    if (runStart < 0 || end < runStart) return;
    d += `M${xOf(runStart).toFixed(2)},${VB_H} `;
    for (let i = runStart; i <= end; i++) {
      const v = valueOf(points[i]);
      if (v == null) continue;
      d += `L${xOf(i).toFixed(2)},${yOf(v).toFixed(2)} `;
    }
    d += `L${xOf(end).toFixed(2)},${VB_H} Z `;
  };
  for (let i = 0; i < points.length; i++) {
    const v = valueOf(points[i]);
    if (v == null) {
      flush(i - 1);
      runStart = -1;
    } else if (runStart < 0) {
      runStart = i;
    }
  }
  flush(points.length - 1);
  return d.trim();
}

export default function ThreeLineChart({ points }: Props) {
  const hasEvents = points.some((p) => p.events != null);
  const hasBls = points.some((p) => p.blsDownsizings != null);
  const hasCpi = points.some((p) => p.cpiYoyPct != null);
  const hasTrends = points.some((p) => p.trendsInterest != null);

  if (!hasEvents && !hasBls && !hasCpi && !hasTrends) {
    return (
      <div className={styles.empty}>
        Not enough data to plot the chart yet
      </div>
    );
  }

  // Left axis: events + BLS share scale (both are counts of products).
  const leftValues: number[] = [];
  for (const p of points) {
    if (p.events != null) leftValues.push(p.events);
    if (p.blsDownsizings != null) leftValues.push(p.blsDownsizings);
  }
  const leftAxis = niceAxis(leftValues);

  // Right axis: combined CPI YoY% and Trends interest. Both are
  // dimensionless and roughly share a 0-100 range, so they can share
  // the right-axis ticks without misleading the eye.
  const rightValues: number[] = [];
  for (const p of points) {
    if (p.cpiYoyPct != null) rightValues.push(p.cpiYoyPct);
    if (p.trendsInterest != null) rightValues.push(p.trendsInterest);
  }
  const rightAxis = niceAxis(rightValues);

  // x position: evenly spaced across the window.
  const xStep = points.length > 1 ? VB_W / (points.length - 1) : VB_W;
  const x = (i: number) => i * xStep;

  const yLeft = (v: number) => {
    const range = leftAxis.max - leftAxis.min || 1;
    return ((leftAxis.max - v) / range) * VB_H;
  };
  const yRight = (v: number) => {
    const range = rightAxis.max - rightAxis.min || 1;
    return ((rightAxis.max - v) / range) * VB_H;
  };

  // Grid lines: 5 horizontal evenly spaced.
  const gridYs: number[] = [];
  for (let i = 0; i <= 4; i++) gridYs.push((i / 4) * VB_H);

  // Build paths.
  const eventsArea = buildAreaPath(points, (p) => p.events, x, yLeft);
  const eventsLine = buildPath(points, (p) => p.events, x, yLeft);
  const blsLine = buildPath(points, (p) => p.blsDownsizings, x, yLeft);
  const cpiLine = buildPath(points, (p) => p.cpiYoyPct, x, yRight);
  const trendsLine = buildPath(points, (p) => p.trendsInterest, x, yRight);

  // X-axis labels: spread X_TICK_COUNT ticks across the points list.
  const xTicks: { month: string; label: string }[] = [];
  for (let i = 0; i < X_TICK_COUNT; i++) {
    const idx = Math.round((i / (X_TICK_COUNT - 1)) * (points.length - 1));
    const p = points[idx];
    if (p) xTicks.push({ month: p.month, label: monthLabel(p.month) });
  }

  return (
    <div className={styles["chart-card"]}>
      <div className={styles["chart-legend"]}>
        <span className={styles["legend-item"]}>
          <span className={`${styles["legend-swatch"]} ${styles.events}`} />{" "}
          FullCarts events (left axis)
        </span>
        <span className={styles["legend-item"]}>
          <span className={`${styles["legend-swatch"]} ${styles.bls}`} /> BLS
          downsizings (left axis, dashed)
        </span>
        <span className={styles["legend-item"]}>
          <span className={`${styles["legend-swatch"]} ${styles.fred}`} /> FRED
          food CPI YoY% (right axis)
        </span>
        {hasTrends && (
          <span className={styles["legend-item"]}>
            <span className={`${styles["legend-swatch"]} ${styles.trends}`} />{" "}
            Google Trends &ldquo;shrinkflation&rdquo; (right axis, dashed)
          </span>
        )}
      </div>

      <div className={styles["chart-wrap"]}>
        <div className={`${styles["chart-y-axis-label"]} ${styles.left}`}>
          Events / month
        </div>
        <div className={`${styles["chart-y-axis-label"]} ${styles.right}`}>
          CPI YoY %
        </div>
        <div className={styles["chart-y-left"]}>
          {leftAxis.ticks.map((t) => (
            <div key={t} className={styles.yt}>
              {Math.round(t).toLocaleString()}
            </div>
          ))}
        </div>
        <div className={styles["chart-y-right"]}>
          {rightAxis.ticks.map((t) => (
            <div key={t} className={styles.yt}>
              {t.toFixed(0)}%
            </div>
          ))}
        </div>

        <svg
          className={styles["chart-svg"]}
          viewBox={`0 0 ${VB_W} ${VB_H}`}
          preserveAspectRatio="none"
          aria-label="Events vs BLS vs CPI"
        >
          {gridYs.map((gy, i) => (
            <line
              key={i}
              className={styles["chart-grid-line"]}
              x1="0"
              y1={gy}
              x2={VB_W}
              y2={gy}
            />
          ))}
          {hasEvents && eventsArea && (
            <path className={`${styles["chart-area"]} ${styles.events}`} d={eventsArea} />
          )}
          {hasEvents && eventsLine && (
            <path className={`${styles["chart-line"]} ${styles.events}`} d={eventsLine} />
          )}
          {hasBls && blsLine && (
            <path className={`${styles["chart-line"]} ${styles.bls}`} d={blsLine} />
          )}
          {hasCpi && cpiLine && (
            <path className={`${styles["chart-line"]} ${styles.fred}`} d={cpiLine} />
          )}
          {hasTrends && trendsLine && (
            <path className={`${styles["chart-line"]} ${styles.trends}`} d={trendsLine} />
          )}
        </svg>
      </div>

      <div className={styles["chart-x-axis"]}>
        {xTicks.map((t, i) => (
          <span key={i}>{t.label}</span>
        ))}
      </div>
    </div>
  );
}
