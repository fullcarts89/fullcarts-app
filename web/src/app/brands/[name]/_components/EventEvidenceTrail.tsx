"use client";
// Client component. Renders one row per event with the dominant headline
// + count badge, sorted by evidence_count desc. Click expands the row to
// show every contributing source. All data comes from event_evidence_summary
// view — no DB queries from the browser.
import { useState } from "react";
import styles from "../styles.module.css";
import type { EventRow, EventSource } from "../types";
import { isoDay, num, publisherLabel } from "../lib";

interface Props {
  events: EventRow[];
}

const SOURCES_PREVIEW = 12;

function dominantSource(sources: EventSource[]): EventSource | null {
  if (sources.length === 0) return null;
  // Pick the title that recurs most often across sources (syndicated wire
  // stories repeat the same headline). Ties fall back to the most recent.
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
  if (type === "gdelt") return "News";
  return type ? type.toUpperCase() : "News";
}

export default function EventEvidenceTrail({ events }: Props) {
  const [openId, setOpenId] = useState<string | null>(null);

  if (events.length === 0) return null;

  return (
    <section className={styles.block}>
      <div className={styles["section-head"]}>
        <h2>Evidence trail</h2>
        <div className={styles.meta}>
          {events.length} unique event{events.length === 1 ? "" : "s"} · most
          covered first · click to expand
        </div>
      </div>
      <div className={styles["evt-list"]}>
        {events.map((e) => {
          const dom = dominantSource(e.sources);
          const sourceType = dom?.source_type || "news";
          const delta = num(e.size_delta_pct);
          const sizeBefore = num(e.size_before);
          const sizeAfter = num(e.size_after);
          const unit = e.size_unit || "";
          // Dedupe by URL — the promote/merge logic occasionally appends
          // two evidence entries for the same article, which would render
          // as repeated rows otherwise. Keep first occurrence.
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
          const isOpen = openId === e.event_id;

          return (
            <div
              key={e.event_id}
              className={`${styles["evt-row"]} ${isOpen ? styles.open : ""}`}
            >
              <div
                className={styles["evt-summary"]}
                onClick={() => setOpenId(isOpen ? null : e.event_id)}
                role="button"
                tabIndex={0}
                onKeyDown={(ev) => {
                  if (ev.key === "Enter" || ev.key === " ") {
                    ev.preventDefault();
                    setOpenId(isOpen ? null : e.event_id);
                  }
                }}
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
                      <span className={styles["net-name"]}>{dom.domain}</span>
                    )}
                    {e.sources.length > 1 && (
                      <span className={styles["net-more"]}>
                        +{e.sources.length - 1} more
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
              </div>
              <div className={styles["evt-expanded"]}>
                <div className={styles["src-list"]}>
                  {shownSources.map((s, idx) => {
                    // Some events have duplicate claim_ids in their sources
                    // (a wrinkle of the promote+dedup history) — fold the
                    // index into the key so React stays happy. Same-URL
                    // duplicates are deduped above so the list is clean
                    // visually.
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
    </section>
  );
}
