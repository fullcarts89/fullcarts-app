// Server component. Top 8 biggest individual shrinks for this brand.
// Card image picks the entity's image_url first; falls back to the lead
// source's archived/socialimage. Card link goes to that source's article URL
// when available; otherwise the card is unclickable.
import styles from "../styles.module.css";
import type { EventRow, ProductEntity } from "../types";
import { isoDay, leadImageFromSources, num } from "../lib";

interface Props {
  events: EventRow[];
  entities: ProductEntity[];
}

const TOP_N = 8;

export default function WallOfShame({ events, entities }: Props) {
  const byEntity = new Map<string, ProductEntity>();
  for (const e of entities) byEntity.set(e.id, e);

  const top = [...events]
    .sort((a, b) => num(a.size_delta_pct) - num(b.size_delta_pct))
    .slice(0, TOP_N);

  if (top.length === 0) return null;

  return (
    <section className={styles.block}>
      <div className={styles["section-head"]}>
        <h2>Biggest individual shrinks</h2>
        <div className={styles.meta}>
          Top {top.length} of {events.length} events · sorted by % drop
        </div>
      </div>
      <div className={styles["shame-grid"]}>
        {top.map((e) => {
          const entity = e.entity_id ? byEntity.get(e.entity_id) : null;
          const lead = leadImageFromSources(e.sources);
          const imgUrl = entity?.image_url || lead.url;
          const linkUrl = e.sources[0]?.url || null;
          const sourceType = e.sources[0]?.source_type || "news";
          const delta = num(e.size_delta_pct);
          const sizeBefore = num(e.size_before);
          const sizeAfter = num(e.size_after);
          const unit = e.size_unit || "";
          const productName = entity?.canonical_name || e.product_name;
          const showImageTag = sourceType !== "reddit" && lead.url && !entity?.image_url;

          const cardInner = (
            <>
              <div className={styles["shame-img"]}>
                {imgUrl ? (
                  <>
                    <img src={imgUrl} alt="" loading="lazy" />
                    {showImageTag && (
                      <span className={styles["img-tag"]}>News</span>
                    )}
                  </>
                ) : (
                  <div className={styles["placeholder-stub"]}>
                    <span className={styles["ps-tag"]}>No archive</span>
                    <span className={styles["ps-name"]}>{productName}</span>
                    <span className={styles["ps-brand-mark"]}>{e.brand}</span>
                  </div>
                )}
              </div>
              <div className={styles["shame-body"]}>
                <div className={styles["shame-title"]}>{productName}</div>
                <div className={styles["shame-stat"]}>
                  <span className={styles["shame-delta"]}>
                    {delta.toFixed(1)}%
                  </span>
                  <span className={styles["shame-sizes"]}>
                    {sizeBefore}
                    {unit} → {sizeAfter}
                    {unit}
                  </span>
                </div>
                <div className={styles["shame-meta"]}>
                  <span
                    className={`${styles["shame-source"]} ${styles[sourceType] || ""}`}
                  >
                    {sourceType === "reddit"
                      ? "Reddit ↗"
                      : sourceType === "gdelt"
                        ? "GDELT News ↗"
                        : "News ↗"}
                  </span>
                  <span>{isoDay(e.observed_date)}</span>
                </div>
              </div>
            </>
          );

          return linkUrl ? (
            <a
              key={e.event_id}
              className={styles["shame-card"]}
              href={linkUrl}
              target="_blank"
              rel="noopener"
            >
              {cardInner}
            </a>
          ) : (
            <div key={e.event_id} className={styles["shame-card"]}>
              {cardInner}
            </div>
          );
        })}
      </div>
    </section>
  );
}
