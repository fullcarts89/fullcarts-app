// Server component. Big-number callout for the latest BLS quarterly
// downsizing count, with QoQ + YoY deltas. Empty fallback if BLS data
// is missing for the latest quarter.
import styles from "../styles.module.css";
import { fmtPct, quarterLabel } from "../lib";
import Term, { GLOSSARY } from "../../_components/Term";

interface Props {
  count: number;
  quarter: string;
  prevQuarterDeltaPct: number;
  yearAgoDeltaPct: number;
}

export default function BlsHeadline({
  count,
  quarter,
  prevQuarterDeltaPct,
  yearAgoDeltaPct,
}: Props) {
  if (count === 0 || !quarter) {
    return (
      <div className={styles["headline-stat"]}>
        <div>
          <div className={styles["hs-pill"]}>BLS</div>
          <div className={styles["hs-big"]}>—</div>
        </div>
        <div className={styles["hs-body"]}>
          <h2>BLS downsizing count unavailable</h2>
          <p>
            The Bureau of Labor Statistics&apos; R-CPI-SC release lags by ~6
            weeks each quarter. We&apos;ll display the live count here once the
            next release lands.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles["headline-stat"]}>
      <div>
        <div className={styles["hs-pill"]}>
          BLS · {quarterLabel(quarter)}
        </div>
        <div className={styles["hs-big"]}>{count.toLocaleString()}</div>
      </div>
      <div className={styles["hs-body"]}>
        <h2>products downsized last quarter</h2>
        <p>
          The Bureau of Labor Statistics&apos; research index (called{" "}
          <Term label="R-CPI-SC" define={GLOSSARY["R-CPI-SC"]} />) counts
          every product the government tracks whose package quietly shrank
          between quarterly surveys.{" "}
          {prevQuarterDeltaPct !== 0 && (
            <>
              {quarterLabel(quarter)}&apos;s count is{" "}
              <strong>
                {fmtPct(prevQuarterDeltaPct, true)} vs the previous quarter
              </strong>
              {yearAgoDeltaPct !== 0 && (
                <>
                  {" "}
                  ({fmtPct(yearAgoDeltaPct, true)} vs the same quarter last year)
                </>
              )}
              .{" "}
            </>
          )}
          This is the most authoritative measure of US shrinkflation that
          exists, and we plot it alongside our own catch list below.
        </p>
        <div className={styles["hs-source"]}>
          Source: BLS · r-cpi-sc-counts.xlsx
        </div>
      </div>
    </div>
  );
}
