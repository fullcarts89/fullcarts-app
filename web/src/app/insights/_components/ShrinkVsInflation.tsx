// Server component. The headline correlation: BLS "All food" package
// downsizings per year (blue bars, left axis) against food-price
// inflation YoY% (amber line, right axis). The peak-inflation year is
// highlighted and the turning points are annotated below the chart.
//
// Pure SVG, no client JS — same pattern as ThreeLineChart (text lives
// in HTML around a non-text, preserveAspectRatio="none" SVG so labels
// never stretch). Annotation numbers are derived from the data, never
// hard-coded, so they stay correct as new BLS releases land.
import styles from "../styles.module.css";
import type { ShrinkInflationYear } from "../types";
import { niceAxis } from "../lib";

interface Props {
  data: ShrinkInflationYear[];
}

const VB_W = 1000;
const VB_H = 240;

export default function ShrinkVsInflation({ data }: Props) {
  const usable = data.filter((d) => d.downsizings != null);
  if (usable.length < 3) {
    return (
      <div className={styles.empty}>
        Not enough BLS history to plot the trend yet
      </div>
    );
  }

  const dzValues = usable.map((d) => d.downsizings!).filter((v) => Number.isFinite(v));
  const infValues = data
    .map((d) => d.inflationPct)
    .filter((v): v is number => v != null && Number.isFinite(v));
  const leftAxis = niceAxis(dzValues);
  const rightAxis = niceAxis(infValues);

  const n = data.length;
  const slot = VB_W / n;
  const barW = slot * 0.46;
  const xCenter = (i: number) => i * slot + slot / 2;
  const yLeft = (v: number) => {
    const range = leftAxis.max - leftAxis.min || 1;
    return ((leftAxis.max - v) / range) * VB_H;
  };
  const yRight = (v: number) => {
    const range = rightAxis.max - rightAxis.min || 1;
    return ((rightAxis.max - v) / range) * VB_H;
  };

  // Peak-inflation year (the spike we highlight) + the latest year (the
  // "where it stands now" annotation). Both fully data-driven.
  let peakIdx = 0;
  data.forEach((d, i) => {
    if ((d.inflationPct ?? -Infinity) > (data[peakIdx].inflationPct ?? -Infinity)) {
      peakIdx = i;
    }
  });
  const peak = data[peakIdx];
  const peakPrev = data[peakIdx - 1];
  const latest = data[data.length - 1];
  const peakMultiple =
    peakPrev && peakPrev.downsizings && peak.downsizings
      ? peak.downsizings / peakPrev.downsizings
      : null;

  // Inflation polyline across year centers.
  let infPath = "";
  let pen = false;
  data.forEach((d, i) => {
    if (d.inflationPct == null) {
      pen = false;
      return;
    }
    infPath += `${pen ? "L" : "M"}${xCenter(i).toFixed(2)},${yRight(d.inflationPct).toFixed(2)} `;
    pen = true;
  });

  const gridYs = [0, 1, 2, 3, 4].map((i) => (i / 4) * VB_H);

  return (
    <div className={styles["chart-card"]}>
      <div className={styles["chart-legend"]}>
        <span className={styles["legend-item"]}>
          <span className={`${styles["legend-swatch"]} ${styles.bls}`} /> BLS food
          downsizings / yr (left axis)
        </span>
        <span className={styles["legend-item"]}>
          <span className={`${styles["legend-swatch"]} ${styles.fred}`} /> Food
          price inflation YoY% (right axis)
        </span>
      </div>

      <div className={styles["chart-wrap"]}>
        <div className={`${styles["chart-y-axis-label"]} ${styles.left}`}>
          Downsizings
        </div>
        <div className={`${styles["chart-y-axis-label"]} ${styles.right}`}>
          Inflation %
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
          aria-label="BLS food package downsizings vs food-price inflation, by year"
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
          {data.map((d, i) =>
            d.downsizings == null ? null : (
              <rect
                key={d.year}
                className={`${styles["svi-bar"]} ${
                  i === peakIdx ? styles["svi-bar-hot"] : ""
                } ${d.partial ? styles["svi-bar-partial"] : ""}`}
                x={(xCenter(i) - barW / 2).toFixed(2)}
                y={yLeft(d.downsizings).toFixed(2)}
                width={barW.toFixed(2)}
                height={(VB_H - yLeft(d.downsizings)).toFixed(2)}
              />
            ),
          )}
          {infPath && (
            <path className={styles["svi-inflation-line"]} d={infPath.trim()} />
          )}
        </svg>
      </div>

      <div className={styles["svi-x-axis"]}>
        {data.map((d) => (
          <span key={d.year}>
            &apos;{String(d.year).slice(2)}
            {d.partial ? "*" : ""}
          </span>
        ))}
      </div>

      <div className={styles["svi-annotations"]}>
        {peak.inflationPct != null && peakMultiple && (
          <div className={`${styles["svi-annot"]} ${styles.hot}`}>
            <span className={styles["svi-annot-year"]}>{peak.year}</span>
            food inflation spiked to{" "}
            <strong>{peak.inflationPct.toFixed(0)}%</strong> — downsizings{" "}
            {peakPrev!.downsizings!.toLocaleString()}→
            {peak.downsizings!.toLocaleString()}{" "}
            <strong>({peakMultiple.toFixed(1)}×)</strong>
          </div>
        )}
        {latest.inflationPct != null && (
          <div className={styles["svi-annot"]}>
            <span className={styles["svi-annot-year"]}>{latest.year}</span>
            inflation cooled to{" "}
            <strong>{latest.inflationPct.toFixed(0)}%</strong> — downsizings
            fell to <strong>{latest.downsizings!.toLocaleString()}</strong>
            {latest.partial ? " (YTD*)" : ""}
          </div>
        )}
      </div>
    </div>
  );
}
