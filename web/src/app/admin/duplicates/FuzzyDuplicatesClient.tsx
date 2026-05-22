"use client";

import { useCallback, useState, useTransition } from "react";
import type { FuzzyDuplicateGroup } from "./lib";
import ExtractEventsModal from "./ExtractEventsModal";
import styles from "./styles.module.css";
import fuzzyStyles from "./fuzzy.module.css";

/** Call the merge endpoint via plain fetch. Deliberately NOT importing the
 *  mergePair server action: server actions in Next.js auto-refresh the
 *  current route after completion, reflowing the page mid-triage. A POST
 *  to a route handler has no such side-effect. */
async function callMergePair(
  sourceId: string,
  targetId: string,
): Promise<{ logId: number; claimsMoved: number; eventsMoved: number; variantsMoved: number }> {
  const r = await fetch("/api/admin/merge-pair", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ sourceId, targetId }),
  });
  if (!r.ok) {
    const detail = await r.json().catch(() => ({ error: r.statusText }));
    throw new Error(detail.error || "merge failed");
  }
  return r.json();
}

/** Reverse-parse a size signature like "20fl oz→16.9fl oz" into its
 *  numeric/unit components for the reassign API call. The format comes
 *  from sizeBucket() in admin/claims/groups/lib.ts:
 *  `${fmt(oldSize, unit)}→${fmt(newSize, unit)}`. */
function parseSizeSignature(sig: string): { before: number; after: number; unit: string } | null {
  const m = sig.match(/^([0-9]+(?:\.[0-9]+)?)\s*([^→]*?)→\s*([0-9]+(?:\.[0-9]+)?)\s*(.*)$/);
  if (!m) return null;
  const before = parseFloat(m[1]);
  const after = parseFloat(m[3]);
  if (!Number.isFinite(before) || !Number.isFinite(after)) return null;
  const unit = (m[2] || m[4] || "").trim();
  return { before, after, unit };
}

export interface SourceLink {
  url: string;
  source_type: string | null;
  domain: string | null;
  publisher: string | null;
  title: string | null;
  date: string | null;
  /** published_changes.id this source backs. Used by the "↩ wrong" action —
   *  retracting the event also flips every claim feeding it (including
   *  this source) back to pending. */
  event_id: string | null;
}

interface Props {
  groups: FuzzyDuplicateGroup[];
  /** Per-member sources, keyed `${entity_id}|${size_signature}`. Each list
   *  is already URL-deduped and date-desc sorted. May be missing keys if
   *  the entity has no published-changes evidence (skimpflation rows are
   *  excluded from event_evidence_summary). */
  sourcesByKey: Record<string, SourceLink[]>;
}

const MAX_SOURCES_INLINE = 5;

/**
 * Aggressive-tier review surface — sits below the exact-match section.
 * Each group lists 2+ entities sharing the SAME brand + SAME exact
 * (size_before, size_after, size_unit). Fuzzy name match is a hint:
 * ✓ name match = high-confidence merge candidate, ⚠ names diverge =
 * could be a real product line, verify before merging.
 * Default target = members[0] (highest event_count); admin picks via radio.
 */
export default function FuzzyDuplicatesClient({ groups, sourcesByKey }: Props) {
  const [limit, setLimit] = useState<number>(Math.min(50, groups.length));
  // Lifted to top-level: tracks every entity merged this session, across all
  // groups. Lifting keeps group order anchored (no router.refresh / no resort
  // on merge) AND correctly hides an entity that happens to belong to multiple
  // size-signature groups once it's merged in any of them.
  const [mergedIds, setMergedIds] = useState<Set<string>>(new Set());
  const markMerged = useCallback((id: string) => {
    setMergedIds((prev) => {
      if (prev.has(id)) return prev;
      const next = new Set(prev);
      next.add(id);
      return next;
    });
  }, []);

  // Tracks (entity_id, size_signature) pairs whose events have been moved
  // off this session. Keyed `${entity_id}|${signature}`. Same anchoring
  // principle: don't reflow the page; just mark the chip as moved.
  const [extractedKeys, setExtractedKeys] = useState<Map<string, { targetBrand: string; targetName: string; eventsMoved: number }>>(new Map());
  const markExtracted = useCallback(
    (entityId: string, sig: string, result: { targetBrand: string; targetName: string; eventsMoved: number }) => {
      setExtractedKeys((prev) => {
        const next = new Map(prev);
        next.set(entityId + "|" + sig, result);
        return next;
      });
    },
    [],
  );

  // Tracks event_ids that have been retracted via the "↩ wrong" action on
  // a source row. Used to grey out all sources sharing that event_id
  // without reflowing the page.
  const [sentBackEventIds, setSentBackEventIds] = useState<Set<string>>(new Set());
  const markSentBack = useCallback((eventId: string) => {
    setSentBackEventIds((prev) => {
      if (prev.has(eventId)) return prev;
      const next = new Set(prev);
      next.add(eventId);
      return next;
    });
  }, []);

  // Modal state — single instance at top level so it overlays the whole
  // duplicates view, independent of group/member identity.
  const [extractRequest, setExtractRequest] = useState<
    | {
        entity: { id: string; brand: string; canonical_name: string };
        sizeSignature: string;
        sizeBefore: number;
        sizeAfter: number;
        sizeUnit: string;
        eventCountAtSize: number;
      }
    | null
  >(null);

  const requestExtract = useCallback(
    (
      entity: { id: string; brand: string; canonical_name: string },
      sizeSignature: string,
      eventCountAtSize: number,
    ) => {
      const parsed = parseSizeSignature(sizeSignature);
      if (!parsed) {
        // Defensive: if a chip somehow has a non-parseable string, refuse
        // rather than ship garbage to the API.
        // eslint-disable-next-line no-console
        console.error("could not parse size signature", sizeSignature);
        return;
      }
      setExtractRequest({
        entity,
        sizeSignature,
        sizeBefore: parsed.before,
        sizeAfter: parsed.after,
        sizeUnit: parsed.unit,
        eventCountAtSize,
      });
    },
    [],
  );

  const visible = groups.slice(0, limit);

  if (groups.length === 0) {
    return (
      <div className={styles.empty}>
        No fuzzy duplicate groups detected.
      </div>
    );
  }

  return (
    <>
      <div className={styles.controls}>
        <div className={styles.controls_left}>
          <span className={styles.controls_label}>
            target = highest event_count by default; change per group via radio
          </span>
        </div>
        <div className={styles.controls_right}>
          <span className={styles.controls_label}>show:</span>
          {[50, 100, 200].map((n) => (
            <button
              key={n}
              type="button"
              onClick={() => setLimit(Math.min(n, groups.length))}
              className={
                limit === Math.min(n, groups.length)
                  ? styles.btn_pill_active
                  : styles.btn_pill
              }
            >
              {n}
            </button>
          ))}
          <button
            type="button"
            onClick={() => setLimit(groups.length)}
            className={
              limit >= groups.length ? styles.btn_pill_active : styles.btn_pill
            }
          >
            all ({groups.length})
          </button>
        </div>
      </div>

      <div className={fuzzyStyles.list}>
        {visible.map((g) => (
          <FuzzyGroupRow
            key={g.group_key}
            group={g}
            sourcesByKey={sourcesByKey}
            mergedIds={mergedIds}
            onMerged={markMerged}
            extractedKeys={extractedKeys}
            onRequestExtract={requestExtract}
            sentBackEventIds={sentBackEventIds}
            onSentBack={markSentBack}
          />
        ))}
      </div>
      {extractRequest && (
        <ExtractEventsModal
          sourceEntity={extractRequest.entity}
          sizeSignature={extractRequest.sizeSignature}
          sizeBefore={extractRequest.sizeBefore}
          sizeAfter={extractRequest.sizeAfter}
          sizeUnit={extractRequest.sizeUnit}
          eventCountAtSize={extractRequest.eventCountAtSize}
          onClose={() => setExtractRequest(null)}
          onDone={(result) => {
            markExtracted(extractRequest.entity.id, extractRequest.sizeSignature, {
              targetBrand: result.targetBrand,
              targetName: result.targetName,
              eventsMoved: result.eventsMoved,
            });
            setExtractRequest(null);
          }}
        />
      )}
    </>
  );
}

/** A single fuzzy group: header + per-member rows. The target row is
 *  highlighted in green and locked (no merge button — it's the target). */
function FuzzyGroupRow({
  group,
  sourcesByKey,
  mergedIds,
  onMerged,
  extractedKeys,
  onRequestExtract,
  sentBackEventIds,
  onSentBack,
}: {
  group: FuzzyDuplicateGroup;
  sourcesByKey: Record<string, SourceLink[]>;
  /** Lifted state — entities merged this session, across the whole page. */
  mergedIds: Set<string>;
  onMerged: (id: string) => void;
  extractedKeys: Map<string, { targetBrand: string; targetName: string; eventsMoved: number }>;
  onRequestExtract: (
    entity: { id: string; brand: string; canonical_name: string },
    sizeSignature: string,
    eventCountAtSize: number,
  ) => void;
  sentBackEventIds: Set<string>;
  onSentBack: (eventId: string) => void;
}) {
  const [targetId, setTargetId] = useState<string>(group.members[0].id);

  const target = group.members.find((m) => m.id === targetId) ?? group.members[0];
  // Count source rows (= members minus target) still requiring action.
  const remainingSources = group.members.filter(
    (m) => m.id !== target.id && !mergedIds.has(m.id),
  ).length;
  const allMerged = remainingSources === 0;

  return (
    <div className={fuzzyStyles.group}>
      <div className={fuzzyStyles.group_header}>
        <div className={fuzzyStyles.group_brand}>{group.brand}</div>
        <div className={fuzzyStyles.group_sep}>·</div>
        <div className={fuzzyStyles.group_matched_chips}>
          <span className={fuzzyStyles.chip_matched}>{group.size_signature}</span>
        </div>
        <div className={fuzzyStyles.group_sep}>·</div>
        <div className={fuzzyStyles.group_count}>
          {group.members.length} entities
        </div>
        <div className={fuzzyStyles.group_sep}>·</div>
        {group.has_fuzzy_name_match ? (
          <div
            className={fuzzyStyles.group_matched_label}
            title="≥2 members reduce to the same fuzzy name key — high-confidence same-product candidate."
            style={{ color: "var(--green-base)" }}
          >
            ✓ name match
          </div>
        ) : (
          <div
            className={fuzzyStyles.group_matched_label}
            title="Names diverge — could still be the same product (AI extraction noise) OR a product line announcing a uniform shrink. Check member names below before merging."
            style={{ color: "var(--amber-base)" }}
          >
            ⚠ names diverge — verify before merging
          </div>
        )}
        {allMerged && (
          <div
            className={fuzzyStyles.group_matched_label}
            style={{ color: "var(--green-base)" }}
            title="All source members of this group have been merged into the target this session. Reload the page to drop this group from the list."
          >
            ✓ group fully merged
          </div>
        )}
      </div>

      <div className={fuzzyStyles.members}>
        {group.members.map((m) => {
          const isTarget = m.id === target.id;
          const isMerged = mergedIds.has(m.id);
          const sourceKey = m.id + "|" + group.size_signature;
          const sources = sourcesByKey[sourceKey] ?? [];
          return (
            <MemberRow
              key={m.id}
              member={m}
              groupKey={group.group_key}
              isTarget={isTarget}
              isMerged={isMerged}
              targetName={target.canonical_name}
              targetId={target.id}
              sources={sources}
              extractedKeys={extractedKeys}
              sentBackEventIds={sentBackEventIds}
              onPickTarget={() => setTargetId(m.id)}
              onMerged={() => onMerged(m.id)}
              onRequestExtract={onRequestExtract}
              onSentBack={onSentBack}
            />
          );
        })}
      </div>
    </div>
  );
}

interface MemberRowProps {
  member: FuzzyDuplicateGroup["members"][number];
  groupKey: string;
  isTarget: boolean;
  isMerged: boolean;
  targetId: string;
  targetName: string;
  sources: SourceLink[];
  extractedKeys: Map<string, { targetBrand: string; targetName: string; eventsMoved: number }>;
  sentBackEventIds: Set<string>;
  onPickTarget(): void;
  onMerged(): void;
  onRequestExtract: (
    entity: { id: string; brand: string; canonical_name: string },
    sizeSignature: string,
    eventCountAtSize: number,
  ) => void;
  onSentBack: (eventId: string) => void;
}

function MemberRow({
  member,
  groupKey,
  isTarget,
  isMerged,
  targetId,
  targetName,
  sources,
  extractedKeys,
  sentBackEventIds,
  onPickTarget,
  onMerged,
  onRequestExtract,
  onSentBack,
}: MemberRowProps) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);

  function onMerge() {
    if (isTarget) return;
    if (
      !window.confirm(
        `Merge "${member.canonical_name}" INTO "${targetName}"?\n\n` +
          "All claims, events, and pack variants on the source will move to the target. " +
          "The source will be retracted (reversible).",
      )
    ) {
      return;
    }
    setError(null);
    setResult(null);
    startTransition(async () => {
      try {
        const out = await callMergePair(member.id, targetId);
        setResult(
          `Merged. ${out.claimsMoved} claims, ${out.eventsMoved} events, ${out.variantsMoved} variants moved.`,
        );
        // Mark merged in shared state only. The route handler does NOT
        // trigger Next.js router refresh, so the page does not reflow.
        // On next manual navigation to /admin/duplicates the page re-fetches
        // and drops the retracted source naturally.
        onMerged();
      } catch (e) {
        setError(e instanceof Error ? e.message : "merge failed");
      }
    });
  }

  // Render the SAME layout for merged and unmerged rows so a merge doesn't
  // visually compress the row and shift content below upward by ~150px. The
  // merged version dims, strikes through the name, disables interactions,
  // and swaps the merge button slot for a "✓ merged" badge.
  const rowClass = isMerged
    ? `${fuzzyStyles.member} ${fuzzyStyles.member_done}`
    : `${fuzzyStyles.member} ${isTarget ? fuzzyStyles.member_target : fuzzyStyles.member_source}`;
  return (
    <div className={rowClass}>
      <label className={fuzzyStyles.member_radio}>
        <input
          type="radio"
          name={`target-${groupKey}`}
          checked={isTarget}
          onChange={onPickTarget}
          disabled={isMerged}
          aria-label={`Use ${member.canonical_name} as merge target`}
        />
      </label>

      <div className={fuzzyStyles.member_thumb_wrap}>
        {member.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={member.image_url}
            alt=""
            className={fuzzyStyles.member_thumb}
            loading="lazy"
          />
        ) : (
          <div className={`${fuzzyStyles.member_thumb} ${fuzzyStyles.member_thumb_empty}`} />
        )}
      </div>

      <div className={fuzzyStyles.member_meta}>
        <div className={fuzzyStyles.member_name_row}>
          <span
            className={
              isMerged
                ? `${fuzzyStyles.member_name} ${fuzzyStyles.member_name_struck}`
                : fuzzyStyles.member_name
            }
          >
            {member.canonical_name}
          </span>
          <a
            href={`/products/${member.id}`}
            target="_blank"
            rel="noreferrer"
            className={fuzzyStyles.member_view}
          >
            ↗ view
          </a>
          {isTarget && <span className={fuzzyStyles.target_badge}>target</span>}
          {isMerged && (
            <span
              className={fuzzyStyles.merged_badge}
              title={`Merged into "${targetName}" this session`}
            >
              ✓ merged → {targetName}
            </span>
          )}
        </div>
        <div className={fuzzyStyles.member_chips}>
          <span
            className={
              member.event_count > 0
                ? fuzzyStyles.chip_events
                : fuzzyStyles.chip_events_zero
            }
          >
            {member.event_count} events
          </span>
          {member.event_sizes.length === 0 ? (
            <span className={fuzzyStyles.chip_size_none}>no sized events</span>
          ) : (
            member.event_sizes.map((s) => {
              const matched = member.matched_sizes.includes(s);
              const extractKey = member.id + "|" + s;
              const extracted = extractedKeys.get(extractKey);
              if (extracted) {
                return (
                  <span
                    key={s}
                    className={fuzzyStyles.chip_size_extracted}
                    title={`Moved ${extracted.eventsMoved} event(s) at ${s} to ${extracted.targetBrand} | ${extracted.targetName}`}
                  >
                    ✓ {s} → {extracted.targetBrand}
                  </span>
                );
              }
              const baseClass = matched ? fuzzyStyles.chip_size_match : fuzzyStyles.chip_size;
              return (
                <button
                  key={s}
                  type="button"
                  disabled={isMerged}
                  onClick={() =>
                    onRequestExtract(
                      { id: member.id, brand: member.brand, canonical_name: member.canonical_name },
                      s,
                      // The chip itself doesn't know how many events at this size; for
                      // the matched_sizes case it's at least the group's shared
                      // signature. Use a conservative 0 (UI shows "1+ events").
                      member.matched_sizes.includes(s) ? 1 : Math.max(1, member.event_count),
                    )
                  }
                  className={`${baseClass} ${fuzzyStyles.chip_size_button}`}
                  title={`Move events at ${s} to a different entity`}
                >
                  {s}
                </button>
              );
            })
          )}
          <span className={fuzzyStyles.member_id}>{member.id.slice(0, 8)}</span>
        </div>

        <MemberSources
          sources={sources}
          entityId={member.id}
          sentBackEventIds={sentBackEventIds}
          onSentBack={onSentBack}
        />
      </div>

      <div className={fuzzyStyles.member_actions}>
        {isMerged ? (
          <div className={fuzzyStyles.target_note} title={result ?? undefined}>
            ✓ merged
          </div>
        ) : isTarget ? (
          <div className={fuzzyStyles.target_note}>keep</div>
        ) : (
          <>
            <button
              type="button"
              onClick={onMerge}
              disabled={isPending}
              className={fuzzyStyles.btn_merge}
            >
              {isPending ? "merging…" : `Merge into target →`}
            </button>
            {error && <div className={fuzzyStyles.err}>{error}</div>}
            {result && <div className={fuzzyStyles.ok}>{result}</div>}
          </>
        )}
      </div>
    </div>
  );
}

/** Per-member source list — up to 5 inline. Each row links out to the
 *  underlying reddit post / news article / GDELT URL in a new tab, with
 *  a per-row "↩ wrong" admin action that retracts the backing event and
 *  flips its claims to pending. */
function MemberSources({
  sources,
  entityId,
  sentBackEventIds,
  onSentBack,
}: {
  sources: SourceLink[];
  entityId: string;
  sentBackEventIds: Set<string>;
  onSentBack: (eventId: string) => void;
}) {
  if (sources.length === 0) {
    return (
      <div className={fuzzyStyles.member_sources_empty}>no source evidence</div>
    );
  }
  // Group sibling sources by event_id so the "↩ wrong" confirm can say how
  // many sources will go to pending alongside the clicked one.
  const eventSourceCount = new Map<string, number>();
  for (const s of sources) {
    if (s.event_id) {
      eventSourceCount.set(s.event_id, (eventSourceCount.get(s.event_id) ?? 0) + 1);
    }
  }
  const visible = sources.slice(0, MAX_SOURCES_INLINE);
  const overflow = sources.length - visible.length;
  return (
    <div className={fuzzyStyles.member_sources}>
      {visible.map((s) => (
        <SourceLinkRow
          key={s.url}
          source={s}
          siblingsForEvent={s.event_id ? eventSourceCount.get(s.event_id) ?? 1 : 1}
          isSentBack={!!s.event_id && sentBackEventIds.has(s.event_id)}
          onSentBack={onSentBack}
        />
      ))}
      {overflow > 0 && (
        <a
          href={`/products/${entityId}`}
          target="_blank"
          rel="noreferrer"
          className={fuzzyStyles.source_overflow}
        >
          +{overflow} more →
        </a>
      )}
    </div>
  );
}

function safeHostname(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url.slice(0, 32);
  }
}

function SourceLinkRow({
  source,
  siblingsForEvent,
  isSentBack,
  onSentBack,
}: {
  source: SourceLink;
  siblingsForEvent: number;
  isSentBack: boolean;
  onSentBack: (eventId: string) => void;
}) {
  const outlet =
    source.publisher ||
    source.domain ||
    (source.source_type === "reddit" ? "reddit" : null) ||
    safeHostname(source.url);
  const title = (source.title || "").trim();
  const titleTrimmed = title.length > 90 ? title.slice(0, 90) + "…" : title;
  const dateLabel = source.date ? source.date.slice(0, 10) : null;
  const kind = (source.source_type || "src").toLowerCase();
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function sendBack(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    if (!source.event_id) return;
    const siblingNote =
      siblingsForEvent > 1
        ? `\n\nThis event has ${siblingsForEvent} sources backing it; all ${siblingsForEvent} claims will be flipped to pending.`
        : "";
    if (
      !window.confirm(
        `Send this event back to /admin/claims (status='pending')?` +
          siblingNote +
          `\n\nThe event will be retracted from public views; you can re-decide each claim individually in the admin queue.`,
      )
    ) {
      return;
    }
    setBusy(true);
    setErr(null);
    try {
      const r = await fetch("/api/admin/retract-event", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ event_id: source.event_id }),
      });
      if (!r.ok) {
        const det = await r.json().catch(() => ({ error: r.statusText }));
        throw new Error(det.error || "retract failed");
      }
      onSentBack(source.event_id);
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "retract failed");
    } finally {
      setBusy(false);
    }
  }

  if (isSentBack) {
    return (
      <div
        className={`${fuzzyStyles.source_row} ${fuzzyStyles.source_row_sent}`}
        title="This event was sent back to pending — the claim is now in the /admin/claims queue."
      >
        <span className={`${fuzzyStyles.source_kind} ${fuzzyStyles[`source_kind_${kind}`] ?? ""}`}>
          {kind}
        </span>
        <span className={fuzzyStyles.source_outlet}>{outlet}</span>
        {titleTrimmed && (
          <span className={fuzzyStyles.source_title}>{titleTrimmed}</span>
        )}
        {dateLabel && <span className={fuzzyStyles.source_date}>{dateLabel}</span>}
        <span className={fuzzyStyles.source_sent_label}>✓ sent to pending</span>
      </div>
    );
  }

  return (
    <div className={fuzzyStyles.source_row_wrap}>
      <a
        href={source.url}
        target="_blank"
        rel="noreferrer"
        className={fuzzyStyles.source_row}
        title={source.url}
      >
        <span className={`${fuzzyStyles.source_kind} ${fuzzyStyles[`source_kind_${kind}`] ?? ""}`}>
          {kind}
        </span>
        <span className={fuzzyStyles.source_outlet}>{outlet}</span>
        {titleTrimmed && (
          <span className={fuzzyStyles.source_title}>{titleTrimmed}</span>
        )}
        {dateLabel && <span className={fuzzyStyles.source_date}>{dateLabel}</span>}
        <span className={fuzzyStyles.source_arrow}>↗</span>
      </a>
      {source.event_id && (
        <button
          type="button"
          onClick={sendBack}
          disabled={busy}
          className={fuzzyStyles.source_send_back}
          title={
            siblingsForEvent > 1
              ? `Retract the event (${siblingsForEvent} sources) and send the claims back to /admin/claims for re-review`
              : `Retract the event and send the claim back to /admin/claims for re-review`
          }
        >
          {busy ? "…" : "↩ send to pending"}
        </button>
      )}
      {err && <span className={fuzzyStyles.source_send_err}>{err}</span>}
    </div>
  );
}
