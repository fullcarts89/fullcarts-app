"use client";
// "Shrinking grocery cart" widget. Given a user-supplied weekly grocery
// spend, computes how much of that spend is *just air* — the equivalent
// dollar value of food that's been removed from the bags without the
// price changing.
//
// Math:
//   For each item in the basket, the shrink_pct represents how much
//   product mass was removed. Per item, the "air dollars" are:
//     air = price_per_unit_today * (size_before / size_after - 1)
//   We don't know per-item prices, so we model the basket as evenly
//   weighted (1/N of total spend per item) and use the aggregate:
//     air_dollars = total_spend * mean(|shrink_pct| / (100 + shrink_pct))
//   That's the same math as "if all sizes went back to before, how
//   much MORE product would you get for the same money", expressed
//   in dollars.
import { useMemo, useState } from "react";
import styles from "../styles.module.css";
import type { CartItem } from "../types";

interface Props {
  basket: CartItem[];
}

const DEFAULT_SPEND = 100;

function clamp(n: number, lo: number, hi: number): number {
  return Math.min(hi, Math.max(lo, n));
}

function fmtMoney(n: number): string {
  return `$${n.toFixed(2)}`;
}

function fmtPct(n: number): string {
  return `${n > 0 ? "+" : n < 0 ? "−" : ""}${Math.abs(n).toFixed(1)}%`;
}

function fmtSize(n: number, unit: string): string {
  const r = n >= 100 ? Math.round(n) : Math.round(n * 10) / 10;
  return `${r}${unit}`;
}

function yearOf(iso: string): string {
  return iso.slice(0, 4);
}

export default function ShrinkingCart({ basket }: Props) {
  const [spend, setSpend] = useState(DEFAULT_SPEND);

  // Aggregate "air dollar" rate across the basket. shrink_pct is
  // negative; we want the positive fraction.
  const summary = useMemo(() => {
    if (basket.length === 0) {
      return { airRate: 0, basketAvgShrink: 0, span: { earliest: "—", latest: "—" } };
    }
    let totalRate = 0;
    let earliest = basket[0].date_before;
    let latest = basket[0].date_after;
    for (const it of basket) {
      // "air dollars" per dollar spent on this item
      const rate = it.size_before / it.size_after - 1;
      totalRate += rate;
      if (it.date_before < earliest) earliest = it.date_before;
      if (it.date_after > latest) latest = it.date_after;
    }
    const airRate = totalRate / basket.length;
    const basketAvgShrink =
      basket.reduce((s, it) => s + it.shrink_pct, 0) / basket.length;
    return {
      airRate,
      basketAvgShrink,
      span: { earliest: yearOf(earliest), latest: yearOf(latest) },
    };
  }, [basket]);

  if (basket.length === 0) {
    return (
      <div className={styles["cart-empty"]}>
        Not enough size-comparison data yet to build the basket. Check back
        once more events have been promoted.
      </div>
    );
  }

  const airDollars = spend * summary.airRate;
  const realDollars = spend - airDollars;

  function handleSpend(e: React.ChangeEvent<HTMLInputElement>) {
    const raw = parseFloat(e.target.value);
    if (Number.isFinite(raw)) {
      setSpend(clamp(raw, 1, 100_000));
    } else if (e.target.value === "") {
      setSpend(0);
    }
  }

  return (
    <div className={styles["cart-card"]}>
      <div className={styles["cart-head"]}>
        <span className={styles["cart-eyebrow"]}>The math, on your basket</span>
        <div className={styles["cart-title"]}>
          What does {summary.span.earliest}&apos;s grocery cart cost in{" "}
          {summary.span.latest}?
        </div>
      </div>
      <p className={styles["cart-lead"]}>
        Built from <strong>{basket.length}</strong> real products we&apos;ve
        tracked across {summary.span.earliest}–{summary.span.latest}. Each
        item&apos;s package shrank by an average of{" "}
        <strong>{fmtPct(summary.basketAvgShrink)}</strong> with no price drop
        — so a fraction of every grocery dollar buys nothing but air.
      </p>

      <div className={styles["cart-input-row"]}>
        <label htmlFor="cart-spend" className={styles["cart-input-label"]}>
          Your weekly grocery spend
        </label>
        <div className={styles["cart-input-wrap"]}>
          <span className={styles["cart-input-prefix"]}>$</span>
          <input
            id="cart-spend"
            type="number"
            inputMode="decimal"
            min={1}
            max={10000}
            step={1}
            value={spend || ""}
            onChange={handleSpend}
            className={styles["cart-input"]}
          />
        </div>
      </div>

      <div className={styles["cart-result-row"]}>
        <div className={styles["cart-result-block"]}>
          <div className={styles["cart-result-label"]}>Real food in the bag</div>
          <div className={styles["cart-result-value"]}>
            {fmtMoney(realDollars)}
          </div>
          <div className={styles["cart-result-meta"]}>
            of your {fmtMoney(spend)} buys actual product
          </div>
        </div>
        <div className={`${styles["cart-result-block"]} ${styles["cart-result-bad"]}`}>
          <div className={styles["cart-result-label"]}>Just air</div>
          <div className={styles["cart-result-value"]}>
            {fmtMoney(airDollars)}
          </div>
          <div className={styles["cart-result-meta"]}>
            {(summary.airRate * 100).toFixed(1)}% of every dollar buys nothing
          </div>
        </div>
      </div>

      <div className={styles["cart-basket"]}>
        <div className={styles["cart-basket-head"]}>
          The basket · {basket.length} products
        </div>
        <div className={styles["cart-basket-grid"]}>
          {basket.map((it) => (
            <a
              key={it.entity_id}
              href={`/products/${it.entity_id}`}
              className={styles["cart-item"]}
            >
              <div className={styles["cart-item-img"]}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={it.image_url ?? ""} alt="" loading="lazy" />
              </div>
              <div className={styles["cart-item-body"]}>
                <div className={styles["cart-item-brand"]}>{it.brand}</div>
                <div className={styles["cart-item-name"]}>
                  {it.product_name}
                </div>
                <div className={styles["cart-item-size"]}>
                  <span className={styles["cart-item-before"]}>
                    {fmtSize(it.size_before, it.size_unit)}
                  </span>
                  <span className={styles["cart-item-arrow"]}>→</span>
                  <span className={styles["cart-item-after"]}>
                    {fmtSize(it.size_after, it.size_unit)}
                  </span>
                </div>
                <div className={styles["cart-item-delta"]}>
                  {fmtPct(it.shrink_pct)}
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>

      <div className={styles["cart-credit"]}>
        Methodology: sizes pulled from the earliest and latest documented
        events for each product · weighting assumes even spend across the
        basket · upper bound, since some categories shrink more than your
        actual mix
      </div>
    </div>
  );
}
