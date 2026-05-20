"use client";
// Client component. Renders the per-product event list — every
// documented size change with the contributing source list available
// under a click-to-expand row. Mirrors the brand-page evt-list
// pattern but is scoped to a single entity (one row per event, no
// product header repeated). The most-recent event is expanded by
// default so the user always sees evidence on landing.
import { useState } from "react";
import styles from "../styles.module.css";
import type { EventRow, EventSource } from "../types";
import { claimImageUrl, dominantSource, isoDay, num, publisherLabel } from "../lib";
import RetractEventButton from "@/components/admin/RetractEventButton";
import RawPayloadInspector from "@/components/admin/RawPayloadInspector";

// Reddit posts whose author / body deleted-out come back as the literal
// string "[deleted]" — render nothing in that case rather than the marker.
function cleanField(v: string | null | undefined): string | null {
  if (!v) return null;
  const trimmed = v.trim();
  if (!trimmed || trimmed === "[deleted]" || trimmed === "[removed]") return null;
  return trimmed;
}

interface Props {
  events: EventRow[];
}

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];
const SOURCES_PREVIEW = 12;

function monthLabel(iso: string): { year: string; month: string } {
  const day = iso.slice(0, 10);
  const parts = day.split("-");
  if (parts.length !== 3) return { year: day, month: "" };
  return {
    year: parts[0],
    month: MONTHS[parseInt(parts[1], 10) - 1] || "",
  };
}

function publisherClass(s: EventSource): string {
  if (s.source_type === "reddit") return styles.reddit;
  if (s.source_type === "news" || s.source_type === "gdelt") {
    return styles.news;
  }
  return "";
}

export default function ChangeHistory({ events }: Props) {
  const [openIds, setOpenIds] = useState<Set<string>>(
    () => new Set(events[0] ? [events[0].event_id] : []),
  );

  const toggle = (id: string) => {
    setOpenIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  if (events.length === 0) {
    return (
      <div className={styles["traj-empty"]}>
        We haven&rsquo;t logged a shrink for this product yet — but we&rsquo;re watching.
      </div>
    );
  }

  return (
    <div className={styles["history-list"]}>
      {events.map((e) => {
        const open = openIds.has(e.event_id);
        const { year, month } = monthLabel(e.observed_date);
        const before = num(e.size_before);
        const after = num(e.size_after);
        const delta = num(e.size_delta_pct);
        const max = Math.max(before, after, 1);
        const beforePct = Math.max(2, Math.round((before / max) * 100));
        const afterPct = Math.max(2, Math.round((after / max) * 100));
        const lead = dominantSource(e.sources);
        const sourcesShown = e.sources.slice(0, SOURCES_PREVIEW);
        const remaining = e.sources.length - sourcesShown.length;

        return (
          <div
            key={e.event_id}
            className={`${styles["history-row"]} ${open ? styles.open : ""}`}
          >
            <button
              type="button"
              className={styles["history-summary"]}
              onClick={() => toggle(e.event_id)}
              aria-expanded={open}
              aria-controls={`history-detail-${e.event_id}`}
            >
              <div className={styles["history-date"]}>
                <span className={styles.year}>{year}</span>
                <span className={styles.month}>{month}</span>
              </div>
              <div>
                <div className={styles["history-sizes"]}>
                  <span className={styles.before}>
                    {e.size_before}
                    {e.size_unit}
                  </span>
                  <span className={styles.arrow}>→</span>
                  <span className={styles.after}>
                    {e.size_after}
                    {e.size_unit}
                  </span>
                  {delta !== 0 && (
                    <span className={styles.delta}>{delta.toFixed(1)}%</span>
                  )}
                </div>
                {lead?.title && (
                  <div className={styles["history-headline"]}>
                    &ldquo;{lead.title}&rdquo;
                    {lead.publisher && <> — {lead.publisher}</>}
                  </div>
                )}
              </div>
              <div className={styles["history-diagram"]}>
                <div className={styles["hd-row"]}>
                  <div className={styles["hd-track"]}>
                    <div
                      className={styles["hd-bar"]}
                      style={{ width: `${beforePct}%` }}
                    />
                  </div>
                  <div className={styles["hd-label"]}>
                    {e.size_before}
                    {e.size_unit}
                  </div>
                </div>
                <div className={styles["hd-row"]}>
                  <div className={styles["hd-track"]}>
                    <div
                      className={`${styles["hd-bar"]} ${styles.after}`}
                      style={{ width: `${afterPct}%` }}
                    />
                  </div>
                  <div className={`${styles["hd-label"]} ${styles.after}`}>
                    {e.size_after}
                    {e.size_unit}
                  </div>
                </div>
              </div>
              <div className={styles["history-evidence"]}>
                <span className={styles.count}>{e.evidence_count}</span>{" "}
                source{e.evidence_count === 1 ? "" : "s"}
              </div>
              <div className={styles["history-toggle"]}>▾</div>
            </button>

            <div id={`history-detail-${e.event_id}`} className={styles["history-expanded"]} role="region">
              <div className={styles["src-list"]}>
                {sourcesShown.map((s, i) => {
                  const thumb =
                    claimImageUrl(s.claim_image_path) || s.image || null;
                  const author = cleanField(s.author);
                  const excerpt = cleanField(s.body_excerpt);
                  const hasUrl = !!s.url;
                  return (
                    <a
                      key={`${s.claim_id}-${i}`}
                      className={styles["src-row"]}
                      href={s.url || "#"}
                      target={hasUrl ? "_blank" : undefined}
                      rel={hasUrl ? "noopener noreferrer" : undefined}
                      aria-label={`${s.title || "Source"} on ${publisherLabel(s)}${hasUrl ? " (opens in new tab)" : ""}`}
                      onClick={(e) => {
                        if (!hasUrl) e.preventDefault();
                      }}
                    >
                      <div
                        className={
                          thumb
                            ? styles["src-thumb"]
                            : `${styles["src-thumb"]} ${styles.empty}`
                        }
                        aria-hidden="true"
                      >
                        {thumb ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img src={thumb} alt="" loading="lazy" />
                        ) : (
                          "·"
                        )}
                      </div>
                      <div
                        className={`${styles["src-pub"]} ${publisherClass(s)}`}
                      >
                        {publisherLabel(s)}
                      </div>
                      <div className={styles["src-body"]}>
                        <div className={styles["src-title"]}>
                          {s.title || s.url || "(no title)"}
                        </div>
                        {author && (
                          <div className={styles["src-author"]}>{author}</div>
                        )}
                        {excerpt && (
                          <div className={styles["src-excerpt"]}>
                            “{excerpt}
                            {excerpt.length >= 240 ? "…" : ""}”
                          </div>
                        )}
                      </div>
                      <div className={styles["src-meta"]}>
                        <span className={styles["src-date"]}>
                          {isoDay(s.date)}
                        </span>
                        {hasUrl && (
                          <span className={styles["src-ext"]} aria-hidden="true">
                            ↗ open
                          </span>
                        )}
                        <RawPayloadInspector claimId={s.claim_id} />
                      </div>
                    </a>
                  );
                })}
                {remaining > 0 && (
                  <div className={styles["src-date"]} style={{ padding: 16, textAlign: "left" }}>
                    + {remaining} more source{remaining === 1 ? "" : "s"}
                  </div>
                )}
              </div>
              <RetractEventButton eventId={e.event_id} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
