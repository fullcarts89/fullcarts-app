// Server component. Aggregates variant_observations from retailer
// sources (Kroger / Walmart / OFF / Open Prices) into per-retailer
// cards. Latest observation wins for "current price/size"; OFF cards
// also enumerate every distinct size seen historically.
//
// Empty state: no retailer monitoring yet — most products have only
// claim-derived observations until the variant gets activated.
import styles from "../styles.module.css";
import type { PackVariant, VariantObservation } from "../types";
import { isoDay, num } from "../lib";

interface Props {
  variants: PackVariant[];
  observations: VariantObservation[];
}

interface RetailerCard {
  key: string;
  name: string;
  status: "live" | "archive";
  latestPrice: number | null;
  latestSize: string | null;
  latestUnit: string | null;
  latestDate: string | null;
  upc: string | null;
  /** distinct sizes seen historically — used by the OFF archive card */
  historicalSizes: string[];
  /** count of distinct observations contributing */
  observationCount: number;
}

const RETAILERS: { key: string; match: string[]; name: string; status: "live" | "archive" }[] = [
  { key: "kroger",         match: ["kroger", "kroger_api"],                 name: "Kroger",          status: "live" },
  { key: "walmart",        match: ["walmart", "walmart_api"],               name: "Walmart",         status: "live" },
  { key: "openfoodfacts",  match: ["openfoodfacts", "off", "off_daily"],    name: "Open Food Facts", status: "archive" },
  { key: "open_prices",    match: ["open_prices"],                          name: "Open Prices",     status: "archive" },
];

function variantUpc(variantId: string, variants: PackVariant[]): string | null {
  const v = variants.find((x) => x.id === variantId);
  return v?.upc || null;
}

export default function RetailersGrid({ variants, observations }: Props) {
  // Bucket observations by retailer key.
  const byRetailer = new Map<string, VariantObservation[]>();
  for (const obs of observations) {
    const t = obs.source_type;
    const r = RETAILERS.find((R) => R.match.includes(t));
    if (!r) continue;
    const arr = byRetailer.get(r.key) || [];
    arr.push(obs);
    byRetailer.set(r.key, arr);
  }

  const cards: RetailerCard[] = [];
  for (const r of RETAILERS) {
    const obs = byRetailer.get(r.key) || [];
    if (obs.length === 0) continue;
    const sorted = [...obs].sort((a, b) =>
      isoDay(b.observed_date).localeCompare(isoDay(a.observed_date)),
    );
    const latest = sorted[0];
    const distinctSizes = Array.from(
      new Set(
        sorted
          .map((o) => (o.size ? `${o.size}${o.size_unit || ""}` : null))
          .filter((s): s is string => Boolean(s)),
      ),
    );
    const latestPriceNum = num(latest.price);
    cards.push({
      key: r.key,
      name: r.name,
      status: r.status,
      latestPrice: latestPriceNum > 0 ? latestPriceNum : null,
      latestSize: latest.size,
      latestUnit: latest.size_unit,
      latestDate: isoDay(latest.observed_date),
      upc: variantUpc(latest.variant_id, variants),
      historicalSizes: distinctSizes,
      observationCount: obs.length,
    });
  }

  if (cards.length === 0) {
    return (
      <div className={styles["retailer-empty"]}>
        We&rsquo;re not actively watching this product at retailers yet. Once
        it shows up in our weekly Kroger or Open Food Facts sweeps, prices
        and per-unit cost will appear here.
      </div>
    );
  }

  return (
    <div className={styles.retailers}>
      {cards.map((c) => (
        <div key={c.key} className={styles["retailer-card"]}>
          <div className={styles["retailer-head"]}>
            <div className={styles["retailer-name"]}>{c.name}</div>
            <span
              className={`${styles["retailer-pill"]} ${
                c.status === "live" ? styles.live : styles.archive
              }`}
            >
              {c.status}
            </span>
          </div>

          {c.latestPrice !== null && (
            <div className={styles["retailer-row"]}>
              <span className={styles.k}>Latest price</span>
              <span className={`${styles.v} ${styles.price}`}>
                ${c.latestPrice.toFixed(2)}
              </span>
            </div>
          )}

          {c.latestSize && (
            <div className={styles["retailer-row"]}>
              <span className={styles.k}>Size</span>
              <span className={styles.v}>
                {c.latestSize}
                {c.latestUnit || ""}
              </span>
            </div>
          )}

          {c.status === "archive" && c.historicalSizes.length > 1 && (
            <div className={styles["retailer-row"]}>
              <span className={styles.k}>Sizes recorded</span>
              <span className={styles.v}>{c.historicalSizes.join(" · ")}</span>
            </div>
          )}

          {c.upc && (
            <div className={styles["retailer-row"]}>
              <span className={styles.k}>Barcode</span>
              <span className={`${styles.v} ${styles.upc}`}>{c.upc}</span>
            </div>
          )}

          <div className={styles["retailer-foot"]}>
            {c.latestDate && <>Last seen: {c.latestDate}</>}
            {" · "}
            {c.observationCount} observation
            {c.observationCount === 1 ? "" : "s"}
          </div>
        </div>
      ))}
    </div>
  );
}
