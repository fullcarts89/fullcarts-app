"use client";
// Client component. Combines the year-bar timeline with the evidence
// trail into one interactive section. Clicking a year filters the
// list below to events from that year. Default state: the latest year
// that has events is selected.
//
// Each visible event row shows badge+count, product+sizes+delta,
// dominant headline, source attribution, date — and expands inline
// to reveal every contributing source on click.
import { useMemo, useState } from "react";
import styles from "../styles.module.css";
import type { BrandRanking, EventRow, EventSource } from "../types";
import { isoDay, num, publisherLabel, timelineBuckets } from "../lib";

interface Props {
  ranking: BrandRanking;
  events: EventRow[];
}

const MAX_BAR_PX = 180;
const ZERO_BAR_PX = 2;
const SOURCES_PREVIEW = 12;
const YEAR_EVENTS_PREVIEW = 5;

function eventYear(e: EventRow): number {
  const y = parseInt(isoDay(e.observed_date).slice(0, 4), 10);
  return Number.isFinite(y) ? y : 0;
}

function dominantSource(sources: EventSource[]): EventSource | null {
  if (sources.length === 0) return null;
  const counts = new Map<string, number>();
  for (const s of sources) {
    if (!s.title) continue;
    counts.set(s.title, (counts.get(s.title) || 0) + 1);
  }
  let bestTitle: string | null = null;
  let bestCount = 0;
  for (const [t, c] of counts) {
    if (c > bestCount) {
      bestTitle = t;
      bestCount = c;
    }
  }
  if (!bestTitle) return sources[0];
  return sources.find((s) => s.title === bestTitle) || sources[0];
}

function badgeClass(type: string | undefined): string {
  if (type === "reddit") return styles.reddit;
  return styles.gdelt;
}

function badgeLabel(type: string | undefined): string {
  if (type === "reddit") return "Reddit";
  if (type === "gdelt" || type === "news") return "News";
  return type ? type.toUpperCase() : "News";
}

export default function TimelineExplorer({ ranking, events }: Props) {
  const buckets = useMemo(
    () => timelineBuckets(events, ranking.first_detected, ranking.last_detected),
    [events, ranking.first_detected, ranking.last_detected],
  );

  const yearsWithEvents = useMemo(
    () => buckets.filter((b) => b.count > 0).map((b) => b.year),
    [buckets],
  );

  const defaultYear =
    yearsWithEvents.length > 0
      ? yearsWithEvents[yearsWithEvents.length - 1]
      : null;

  const [activeYear, setActiveYear] = useState<number | null>(defaultYear);
  const [openEventId, setOpenEventId] = useState<string | null>(null);
  const [showAllInYear, setShowAllInYear] = useState(false);

  const yearEvents = useMemo(() => {
    if (activeYear == null) return [];
    return events
      .filter((e) => eventYear(e) === activeYear)
      .sort((a, b) => b.evidence_count - a.evidence_count);
  }, [events, activeYear]);

  if (buckets.length === 0) return null;

  const max = buckets.reduce((m, b) => Math.max(m, b.count), 0);
  const yearSpan = buckets.length;

  return (
    <section className={styles.block}>
      <div className={styles["section-head"]}>
        <h2>{yearSpan} years of shrinking</h2>
        <div className={styles.meta}>
          Click a year · {events.length} unique event
          {events.length === 1 ? "" : "s"} total
        </div>
      </div>

      <div className={styles.timeline}>
        {buckets.map((b) => {
          const isZero = b.count === 0;
          const isActive = activeYear === b.year && !isZero;
          const heightPx = isZero
            ? ZERO_BAR_PX
            : max > 0
              ? Math.max(6, Math.round((b.count / max) * MAX_BAR_PX))
              : ZERO_BAR_PX;
          const yy = String(b.year).slice(-2);
          const wrapClasses = [
            styles["bar-wrap"],
            !isZero && styles.clickable,
            isActive && styles.active,
          ]
            .filter(Boolean)
            .join(" ");
          const yearLabel = isZero
            ? `${b.year}: no documented events`
            : `${b.year}: ${b.count} ${b.count === 1 ? "event" : "events"}`;
          return isZero ? (
            <div key={b.year} className={wrapClasses} aria-label={yearLabel}>
              <div
                className={`${styles.bar} ${styles.zero}`}
                style={{ height: `${heightPx}px` }}
              >
                <div className={`${styles["bar-count"]} ${styles.zero}`}>
                  {b.count}
                </div>
              </div>
              <div className={styles["bar-year"]}>{yy}</div>
            </div>
          ) : (
            <button
              key={b.year}
              type="button"
              className={wrapClasses}
              aria-pressed={isActive}
              aria-label={yearLabel}
              onClick={() => {
                setActiveYear(b.year);
                setOpenEventId(null);
                setShowAllInYear(false);
              }}
            >
              <div
                className={styles.bar}
                style={{ height: `${heightPx}px` }}
              >
                <div className={styles["bar-count"]}>{b.count}</div>
              </div>
              <div className={styles["bar-year"]}>{yy}</div>
            </button>
          );
        })}
      </div>
      <div className={styles["timeline-caveat"]}>
        Gaps for early years mean no documented claims, not no shrinkflation
        events. Reddit&apos;s r/shrinkflation was founded in 2013 and news
        coverage of shrinkflation only became routine after 2021.
      </div>

      {activeYear == null ? (
        <div className={styles["year-empty"]}>
          Pick a year above to explore its events.
        </div>
      ) : (
        <>
          <div className={styles["year-heading"]}>
            <span className={styles["yh-year"]}>{activeYear}</span>
            <span className={styles["yh-count"]}>
              {yearEvents.length} event{yearEvents.length === 1 ? "" : "s"} ·
              most covered first
            </span>
          </div>
          <div className={styles["evt-list"]}>
            {(showAllInYear
              ? yearEvents
              : yearEvents.slice(0, YEAR_EVENTS_PREVIEW)
            ).map((e) => {
              const dom = dominantSource(e.sources);
              const sourceType = dom?.source_type || "news";
              const delta = num(e.size_delta_pct);
              const sizeBefore = num(e.size_before);
              const sizeAfter = num(e.size_after);
              const unit = e.size_unit || "";
              const seenUrls = new Set<string>();
              const uniqueSources = e.sources.filter((s) => {
                const k = s.url || s.claim_id;
                if (seenUrls.has(k)) return false;
                seenUrls.add(k);
                return true;
              });
              const sortedSources = uniqueSources.sort((a, b) =>
                (b.date || "").localeCompare(a.date || ""),
              );
              const shownSources = sortedSources.slice(0, SOURCES_PREVIEW);
              const isOpen = openEventId === e.event_id;

              const expandedId = `evt-sources-${e.event_id}`;
              return (
                <div
                  key={e.event_id}
                  className={`${styles["evt-row"]} ${isOpen ? styles.open : ""}`}
                >
                  <button
                    type="button"
                    className={styles["evt-summary"]}
                    aria-expanded={isOpen}
                    aria-controls={expandedId}
                    onClick={() =>
                      setOpenEventId(isOpen ? null : e.event_id)
                    }
                  >
                    <div className={styles["evt-badge-col"]}>
                      <span
                        className={`${styles["evt-badge"]} ${badgeClass(sourceType)}`}
                      >
                        {badgeLabel(sourceType)}
                        <span className={styles["evt-badge-count"]}>
                          {e.evidence_count}
                        </span>
                      </span>
                    </div>
                    <div className={styles["evt-main"]}>
                      <div className={styles["evt-product"]}>
                        {e.product_name}
                        <span className={styles["evt-size"]}>
                          {sizeBefore}
                          {unit} → {sizeAfter}
                          {unit}
                        </span>
                        <span className={styles["evt-delta"]}>
                          {delta.toFixed(1)}%
                        </span>
                      </div>
                      {dom?.title && (
                        <div className={styles["evt-headline"]}>
                          &ldquo;{dom.title}&rdquo;
                        </div>
                      )}
                      <div className={styles["evt-attribution"]}>
                        {dom?.domain && (
                          <span className={styles["net-name"]}>
                            {dom.domain}
                          </span>
                        )}
                        {sortedSources.length > 1 && (
                          <span className={styles["net-more"]}>
                            +{sortedSources.length - 1} more
                          </span>
                        )}
                        <span className={styles["evt-date"]}>
                          · {isoDay(e.observed_date)}
                        </span>
                      </div>
                    </div>
                    <div className={styles["evt-toggle"]}>
                      <span className={styles["evt-toggle-chev"]}>▾</span>
                    </div>
                  </button>
                  <div id={expandedId} className={styles["evt-expanded"]}>
                    {e.entity_id && (
                      <a
                        className={styles["evt-product-link"]}
                        href={`/products/${e.entity_id}`}
                      >
                        View this product&rsquo;s full scorecard →
                      </a>
                    )}
                    <div className={styles["src-list"]}>
                      {shownSources.map((s, idx) => {
                        const key = `${s.claim_id}-${idx}`;
                        const inner = (
                          <>
                            <div className={styles["src-pub"]}>
                              {publisherLabel(s)}
                            </div>
                            <div className={styles["src-title"]}>
                              {s.title || "(no title)"}
                            </div>
                            <div className={styles["src-date"]}>
                              {isoDay(s.date)}
                            </div>
                          </>
                        );
                        return s.url ? (
                          <a
                            key={key}
                            className={styles["src-row"]}
                            href={s.url}
                            target="_blank"
                            rel="noopener"
                          >
                            {inner}
                          </a>
                        ) : (
                          <div key={key} className={styles["src-row"]}>
                            {inner}
                          </div>
                        );
                      })}
                      {sortedSources.length > SOURCES_PREVIEW && (
                        <div
                          style={{
                            padding: "12px 16px",
                            fontFamily: "var(--font-mono)",
                            fontSize: 11,
                            color: "var(--text-tertiary)",
                            textTransform: "uppercase",
                            letterSpacing: "0.1em",
                          }}
                        >
                          +{sortedSources.length - SOURCES_PREVIEW} more sources
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          {yearEvents.length > YEAR_EVENTS_PREVIEW && (
            <div className={styles["expand-row"]}>
              <span>
                Showing{" "}
                {showAllInYear ? yearEvents.length : YEAR_EVENTS_PREVIEW} of{" "}
                {yearEvents.length}
              </span>
              <button
                type="button"
                className={`${styles["expand-btn"]} ${showAllInYear ? styles.collapse : ""}`}
                onClick={() => setShowAllInYear((x) => !x)}
              >
                {showAllInYear
                  ? "Show top 5"
                  : `Show all ${yearEvents.length} events`}{" "}
                <span className={styles.arrow}>↓</span>
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}
