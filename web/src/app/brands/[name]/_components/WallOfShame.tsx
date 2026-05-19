// Server component. Showcases the most-damning events with strong
// visual evidence. Selection logic favors events that have a real
// archived photo (Reddit user side-by-sides, then article hero images)
// over text-only events, so the cards always carry visible proof.
//
// Card anatomy: photo / source caption / size diagram / title / size+%
// / source-type badge + date.
import styles from "../styles.module.css";
import type { EventRow, EventSource, ProductEntity } from "../types";
import { isoDay, leadImageFromSources, num } from "../lib";
import SizeDiagram from "./SizeDiagram";

interface Props {
  events: EventRow[];
  entities: ProductEntity[];
}

const TOP_N = 8;
const POOL_N = 30;

/** 0 = best (Reddit-archived photo). 1 = article hero. 2 = no image.
 *  Used to rank the showcase pool toward events with visible evidence. */
function evidenceScore(e: EventRow): number {
  for (const s of e.sources) if (s.claim_image_path) return 0;
  for (const s of e.sources) if (s.image) return 1;
  return 2;
}

/** Pick the first source whose image we end up showing, so the caption
 *  matches the photo. Mirrors leadImageFromSources priority order. */
function leadSource(sources: EventSource[]): EventSource | null {
  for (const s of sources) if (s.claim_image_path) return s;
  for (const s of sources) if (s.image) return s;
  return sources[0] || null;
}

function sourceLabel(s: EventSource | null): string {
  if (!s) return "Source";
  if (s.source_type === "reddit") return "Reddit";
  if (s.publisher) return s.publisher;
  if (s.domain) return s.domain;
  return "News";
}

export default function WallOfShame({ events, entities }: Props) {
  const byEntity = new Map<string, ProductEntity>();
  for (const e of entities) byEntity.set(e.id, e);

  // Pool the top POOL_N biggest drops, rank by evidence quality,
  // take the first TOP_N, then re-sort that subset by biggest drop
  // so the displayed order still reads "biggest first".
  const pool = [...events]
    .sort((a, b) => num(a.size_delta_pct) - num(b.size_delta_pct))
    .slice(0, POOL_N);
  const ranked = [...pool].sort((a, b) => {
    const sa = evidenceScore(a);
    const sb = evidenceScore(b);
    if (sa !== sb) return sa - sb;
    return num(a.size_delta_pct) - num(b.size_delta_pct);
  });
  const top = ranked
    .slice(0, TOP_N)
    .sort((a, b) => num(a.size_delta_pct) - num(b.size_delta_pct));

  if (top.length === 0) return null;

  return (
    <section className={styles.block}>
      <div className={styles["section-head"]}>
        <h2>Biggest individual shrinks</h2>
        <div className={styles.meta}>
          Top {top.length} of {events.length} events · best evidence first
        </div>
      </div>
      <div className={styles["shame-grid"]}>
        {top.map((e) => {
          const entity = e.entity_id ? byEntity.get(e.entity_id) : null;
          const lead = leadImageFromSources(e.sources);
          const leadSrc = leadSource(e.sources);
          const imgUrl = lead.url || entity?.image_url || null;
          const linkUrl = leadSrc?.url || null;
          const sourceType = leadSrc?.source_type || "news";
          const delta = num(e.size_delta_pct);
          const sizeBefore = num(e.size_before);
          const sizeAfter = num(e.size_after);
          const unit = e.size_unit || "";
          const productName = entity?.canonical_name || e.product_name;
          const captionDate = isoDay(leadSrc?.date || e.observed_date);
          const captionLabel = sourceLabel(leadSrc);

          const cardInner = (
            <>
              <div className={styles["shame-img"]}>
                {imgUrl ? (
                  <img
                    src={imgUrl}
                    alt={`${e.brand} ${productName} — ${sizeBefore}${unit} to ${sizeAfter}${unit}`}
                    loading="lazy"
                  />
                ) : (
                  <div className={styles["placeholder-stub"]}>
                    <span className={styles["ps-tag"]}>No archive</span>
                    <span className={styles["ps-name"]}>{productName}</span>
                    <span className={styles["ps-brand-mark"]}>{e.brand}</span>
                  </div>
                )}
              </div>
              {imgUrl && (
                <div className={styles["shame-caption"]}>
                  <span className={styles["sc-type"]}>{captionLabel}</span>
                  <span>·</span>
                  <span>{captionDate}</span>
                </div>
              )}
              <SizeDiagram
                before={sizeBefore}
                after={sizeAfter}
                unit={unit}
              />
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
                        ? "News ↗"
                        : "News ↗"}
                  </span>
                  <span>{isoDay(e.observed_date)}</span>
                </div>
              </div>
            </>
          );

          // Prefer the product scorecard (citation page) over the
          // external source. Source URL is still exposed via the
          // "View source ↗" pill at the bottom of the card.
          const cardHref = e.entity_id
            ? `/products/${e.entity_id}`
            : linkUrl;
          const isExternal = !e.entity_id && !!linkUrl;
          return cardHref ? (
            <a
              key={e.event_id}
              className={styles["shame-card"]}
              href={cardHref}
              target={isExternal ? "_blank" : undefined}
              rel={isExternal ? "noopener" : undefined}
              aria-label={
                e.entity_id
                  ? `${e.brand} ${productName} — product scorecard`
                  : `${e.brand} ${productName} — view source (opens in new tab)`
              }
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
