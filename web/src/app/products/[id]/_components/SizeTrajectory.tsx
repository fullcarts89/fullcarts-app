// Server component. Renders the chronological size-over-time chart
// as inline SVG. Step polygon shows the size dropping at each
// documented event; labels float above each step. Pure stateless —
// every coordinate is computed from the steps prop.
import styles from "../styles.module.css";
import type { TrajectoryStep } from "../types";
import { trajectoryAxis } from "../lib";

interface Props {
  steps: TrajectoryStep[];
  unit: string;
}

const VB_WIDTH = 900;
const VB_HEIGHT = 200;

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function monthShort(iso: string): string {
  const parts = iso.slice(0, 10).split("-");
  if (parts.length !== 3) return iso.slice(0, 7);
  const m = parseInt(parts[1], 10) - 1;
  return `${MONTHS[m] || ""} ${parts[0]}`;
}

export default function SizeTrajectory({ steps, unit }: Props) {
  if (steps.length < 2) {
    return (
      <div className={styles["traj-empty"]}>
        Not enough size observations to draw a trajectory yet
      </div>
    );
  }

  const { min, max, ticks } = trajectoryAxis(steps);
  const range = max - min || 1;

  // x positions: spread evenly across the chart's width, OR by date
  // span when possible (more accurate visually for long histories).
  // Falls back to even spacing if dates can't be parsed.
  const times = steps.map((s) => new Date(s.date).getTime());
  const tMin = Math.min(...times);
  const tMax = Math.max(...times);
  const useTimeAxis = Number.isFinite(tMin) && Number.isFinite(tMax) && tMax > tMin;

  const x = (i: number): number => {
    if (useTimeAxis) {
      return ((times[i] - tMin) / (tMax - tMin)) * VB_WIDTH;
    }
    return (i / (steps.length - 1)) * VB_WIDTH;
  };
  const y = (size: number): number => ((max - size) / range) * VB_HEIGHT;

  // Step polygon points: zig-zag horizontal then drop at each event.
  const polygonPts: string[] = [`0,${y(steps[0].size)}`];
  for (let i = 1; i < steps.length; i++) {
    polygonPts.push(`${x(i)},${y(steps[i - 1].size)}`); // horizontal to event
    polygonPts.push(`${x(i)},${y(steps[i].size)}`);     // vertical drop
  }
  // Close polygon along bottom for the filled area.
  const areaClose = `${VB_WIDTH},${VB_HEIGHT} 0,${VB_HEIGHT}`;
  const lastY = y(steps[steps.length - 1].size);
  const lineExtend = `${VB_WIDTH},${lastY}`;
  const areaPts = [...polygonPts, lineExtend, areaClose].join(" ");
  const linePts = [...polygonPts, lineExtend].join(" ");

  // Grid line Y positions correspond to the ticks.
  const gridYs = ticks.map((t) => y(t));

  // Bookend dates for the x-axis row beneath the chart.
  const firstDate = steps[0].date;
  const lastDate = steps[steps.length - 1].date;
  const startYear = firstDate.slice(0, 4);
  const endYear = lastDate.slice(0, 4);

  // Summary footer numbers.
  const start = steps[0];
  const end = steps[steps.length - 1];
  const netPct = start.size > 0 ? ((end.size - start.size) / start.size) * 100 : 0;
  const netDelta = end.size - start.size;

  return (
    <>
      <div className={styles["traj-wrap"]}>
        <div className={styles["traj-chart"]}>
          <div className={styles["traj-y-axis"]}>
            {ticks.map((t) => (
              <div key={t} className={styles.yt}>
                {t}
                {unit}
              </div>
            ))}
          </div>
          <svg
            className={styles["traj-svg"]}
            viewBox={`0 0 ${VB_WIDTH} ${VB_HEIGHT}`}
            preserveAspectRatio="none"
            aria-label="Size over time"
          >
            {gridYs.map((gy, i) => (
              <line
                key={i}
                className={styles["traj-grid-line"]}
                x1="0"
                y1={gy}
                x2={VB_WIDTH}
                y2={gy}
              />
            ))}
            <polygon className={styles["traj-step-area"]} points={areaPts} />
            <polyline className={styles["traj-step-line"]} points={linePts} />
            {steps.map((s, i) => {
              const cx = x(i);
              const cy = y(s.size);
              const isFirst = i === 0;
              const isLast = i === steps.length - 1;
              const labelAnchor = isLast ? "end" : "start";
              const labelX = isLast ? cx - 6 : cx + 6;
              return (
                <g key={i}>
                  <circle
                    className={`${styles["traj-dot"]} ${
                      isFirst ? styles.first : ""
                    }`}
                    cx={cx}
                    cy={cy}
                    r="5"
                  />
                  <text
                    className={styles["traj-label"]}
                    x={labelX}
                    y={cy - 8}
                    textAnchor={labelAnchor}
                  >
                    {s.size}
                    {unit}
                  </text>
                  <text
                    className={styles["traj-label-date"]}
                    x={labelX}
                    y={cy + 8}
                    textAnchor={labelAnchor}
                  >
                    {monthShort(s.date)}
                  </text>
                  {s.deltaPct !== null && s.deltaPct < 0 && (
                    <text
                      className={styles["traj-delta"]}
                      x={labelX + (isLast ? -52 : 52)}
                      y={cy - 8}
                      textAnchor={labelAnchor}
                    >
                      {s.deltaPct.toFixed(0)}%
                    </text>
                  )}
                </g>
              );
            })}
          </svg>
        </div>
        <div className={styles["traj-x-axis"]}>
          <span>{startYear}</span>
          <span>{endYear}</span>
        </div>
        <div className={styles["traj-summary"]}>
          <div className={styles["traj-stat"]}>
            <div className={styles["traj-stat-label"]}>Started at</div>
            <div className={styles["traj-stat-value"]}>
              {start.size}
              {unit}
            </div>
            <div className={styles["traj-stat-meta"]}>
              First documented · {monthShort(start.date)}
            </div>
          </div>
          <div className={styles["traj-stat"]}>
            <div className={styles["traj-stat-label"]}>Ended at</div>
            <div className={`${styles["traj-stat-value"]} ${styles.red}`}>
              {end.size}
              {unit}
            </div>
            <div className={styles["traj-stat-meta"]}>
              Latest observation · {monthShort(end.date)}
            </div>
          </div>
          <div className={styles["traj-stat"]}>
            <div className={styles["traj-stat-label"]}>Net loss</div>
            <div className={`${styles["traj-stat-value"]} ${styles.red}`}>
              {netDelta.toFixed(0)}
              {unit} ({netPct.toFixed(0)}%)
            </div>
            <div className={styles["traj-stat-meta"]}>
              {startYear === endYear
                ? `Within ${startYear}`
                : `${startYear} → ${endYear}`}{" "}
              · {steps.length - 1} drop{steps.length - 1 === 1 ? "" : "s"}
            </div>
          </div>
        </div>
      </div>
      <div className={styles.caveat}>
        From documented events only — earlier or in-between sizes may exist but
        weren&apos;t reported
      </div>
    </>
  );
}
