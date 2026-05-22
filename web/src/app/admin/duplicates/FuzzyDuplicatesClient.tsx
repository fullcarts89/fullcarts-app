"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { mergePair } from "./actions";
import type { FuzzyDuplicateGroup } from "./lib";
import styles from "./styles.module.css";
import fuzzyStyles from "./fuzzy.module.css";

interface Props {
  groups: FuzzyDuplicateGroup[];
}

/**
 * Aggressive-tier review surface — sits below the exact-match section.
 * Each group lists 2+ entities sharing the SAME brand + SAME exact
 * (size_before, size_after, size_unit). Fuzzy name match is a hint:
 * ✓ name match = high-confidence merge candidate, ⚠ names diverge =
 * could be a real product line, verify before merging.
 * Default target = members[0] (highest event_count); admin picks via radio.
 */
export default function FuzzyDuplicatesClient({ groups }: Props) {
  const [limit, setLimit] = useState<number>(Math.min(50, groups.length));
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
          <FuzzyGroupRow key={g.group_key} group={g} />
        ))}
      </div>
    </>
  );
}

/** A single fuzzy group: header + per-member rows. The target row is
 *  highlighted in green and locked (no merge button — it's the target). */
function FuzzyGroupRow({ group }: { group: FuzzyDuplicateGroup }) {
  const [targetId, setTargetId] = useState<string>(group.members[0].id);
  // Track which sources have already been merged so the row collapses
  // after a successful merge.
  const [mergedSources, setMergedSources] = useState<Set<string>>(new Set());

  const target = group.members.find((m) => m.id === targetId) ?? group.members[0];

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
      </div>

      <div className={fuzzyStyles.members}>
        {group.members.map((m) => {
          const isTarget = m.id === target.id;
          const isMerged = mergedSources.has(m.id);
          return (
            <MemberRow
              key={m.id}
              member={m}
              groupKey={group.group_key}
              isTarget={isTarget}
              isMerged={isMerged}
              targetName={target.canonical_name}
              targetId={target.id}
              onPickTarget={() => setTargetId(m.id)}
              onMerged={() =>
                setMergedSources((prev) => {
                  const next = new Set(prev);
                  next.add(m.id);
                  return next;
                })
              }
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
  onPickTarget(): void;
  onMerged(): void;
}

function MemberRow({
  member,
  groupKey,
  isTarget,
  isMerged,
  targetId,
  targetName,
  onPickTarget,
  onMerged,
}: MemberRowProps) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const router = useRouter();

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
        const out = await mergePair(member.id, targetId);
        setResult(
          `Merged. ${out.claimsMoved} claims, ${out.eventsMoved} events, ${out.variantsMoved} variants moved.`,
        );
        onMerged();
        router.refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "merge failed");
      }
    });
  }

  if (isMerged) {
    return (
      <div className={`${fuzzyStyles.member} ${fuzzyStyles.member_merged}`}>
        <div className={fuzzyStyles.member_merged_label}>✓ merged</div>
        <div className={fuzzyStyles.member_merged_detail}>
          {member.canonical_name} → {targetName}
          {result && <span className={fuzzyStyles.member_merged_counts}> · {result}</span>}
        </div>
      </div>
    );
  }

  return (
    <div
      className={`${fuzzyStyles.member} ${isTarget ? fuzzyStyles.member_target : fuzzyStyles.member_source}`}
    >
      <label className={fuzzyStyles.member_radio}>
        <input
          type="radio"
          name={`target-${groupKey}`}
          checked={isTarget}
          onChange={onPickTarget}
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
          <span className={fuzzyStyles.member_name}>{member.canonical_name}</span>
          <a
            href={`/products/${member.id}`}
            target="_blank"
            rel="noreferrer"
            className={fuzzyStyles.member_view}
          >
            ↗ view
          </a>
          {isTarget && <span className={fuzzyStyles.target_badge}>target</span>}
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
              return (
                <span
                  key={s}
                  className={matched ? fuzzyStyles.chip_size_match : fuzzyStyles.chip_size}
                >
                  {s}
                </span>
              );
            })
          )}
          <span className={fuzzyStyles.member_id}>{member.id.slice(0, 8)}</span>
        </div>
      </div>

      <div className={fuzzyStyles.member_actions}>
        {isTarget ? (
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
