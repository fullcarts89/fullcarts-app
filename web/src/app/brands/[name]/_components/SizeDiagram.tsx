// Server-renderable. Renders a small two-bar diagram showing the
// proportional size change for an event. Bar widths are scaled
// against the larger of (before, after) so the visual ratio is
// accurate regardless of unit. Works for any unit (g, ml, ct, etc.).
import styles from "../styles.module.css";

interface Props {
  before: number;
  after: number;
  unit: string;
}

export default function SizeDiagram({ before, after, unit }: Props) {
  if (!Number.isFinite(before) || !Number.isFinite(after) || before <= 0) {
    return null;
  }
  const max = Math.max(before, after, 1);
  const beforePct = Math.max(2, Math.round((before / max) * 100));
  const afterPct = Math.max(2, Math.round((after / max) * 100));
  return (
    <div className={styles["size-diagram"]}>
      <div className={styles["sd-row"]}>
        <div className={styles["sd-track"]}>
          <div
            className={styles["sd-bar-before"]}
            style={{ width: `${beforePct}%` }}
          />
        </div>
        <div className={styles["sd-label"]}>
          {before}
          {unit}
        </div>
      </div>
      <div className={styles["sd-row"]}>
        <div className={styles["sd-track"]}>
          <div
            className={styles["sd-bar-after"]}
            style={{ width: `${afterPct}%` }}
          />
        </div>
        <div className={`${styles["sd-label"]} ${styles.after}`}>
          {after}
          {unit}
        </div>
      </div>
    </div>
  );
}
