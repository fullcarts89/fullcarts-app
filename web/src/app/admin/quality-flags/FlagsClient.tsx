"use client";

import { useMemo, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import FlagRow from "./FlagRow";
import { resolveBatch } from "./actions";
import { FLAG_KIND_META } from "./types";
import type { FlagRow as FlagRowType } from "./types";
import styles from "./styles.module.css";

interface Props {
  flags: FlagRowType[];
  statusCounts: { open: number; resolved: number; all: number };
  currentStatus: "open" | "resolved" | "all";
  currentKind: string | null;
  currentSeverity: string | null;
  /** Distinct flag_kind values in the queue, with open counts. */
  kindBreakdown: Array<{ kind: string; open: number }>;
}

export default function FlagsClient({
  flags,
  statusCounts,
  currentStatus,
  currentKind,
  currentSeverity,
  kindBreakdown,
}: Props) {
  const router = useRouter();
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [batchPending, startBatch] = useTransition();
  const [batchResult, setBatchResult] = useState<string | null>(null);

  // Only show open flags as selectable for batch-resolve.
  const selectableIds = useMemo(
    () => new Set(flags.filter((f) => !f.resolved_at).map((f) => f.id)),
    [flags],
  );

  function toggle(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function selectAllOpen() {
    setSelectedIds(new Set(selectableIds));
  }

  function clearAll() {
    setSelectedIds(new Set());
  }

  function onBatchResolve() {
    if (selectedIds.size === 0) return;
    if (
      !window.confirm(
        `Resolve ${selectedIds.size} flag${selectedIds.size === 1 ? "" : "s"}? Each will be marked resolved by 'admin' with no note. Reversible per-row.`,
      )
    ) {
      return;
    }
    setBatchResult(null);
    startBatch(async () => {
      const out = await resolveBatch(Array.from(selectedIds), null);
      const msg =
        out.failed === 0
          ? `Resolved ${out.succeeded}.`
          : `Resolved ${out.succeeded}, ${out.failed} failed.${out.failures[0] ? ` First error: ${out.failures[0]}` : ""}`;
      setBatchResult(msg);
      clearAll();
      router.refresh();
    });
  }

  function setQuery(next: { status?: string; kind?: string | null; severity?: string | null }) {
    const url = new URL(window.location.href);
    if (next.status !== undefined && next.status !== "open") {
      url.searchParams.set("status", next.status);
    } else if (next.status === "open") {
      url.searchParams.delete("status");
    }
    if (next.kind !== undefined) {
      if (next.kind) url.searchParams.set("kind", next.kind);
      else url.searchParams.delete("kind");
    }
    if (next.severity !== undefined) {
      if (next.severity) url.searchParams.set("severity", next.severity);
      else url.searchParams.delete("severity");
    }
    router.push(url.pathname + (url.search || ""));
  }

  return (
    <>
      <div className={styles.filters}>
        <div className={styles.filter_group}>
          {(["open", "resolved", "all"] as const).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setQuery({ status: s })}
              className={
                currentStatus === s ? styles.btn_pill_active : styles.btn_pill
              }
            >
              {s}
              <span className={styles.pill_count}>
                {statusCounts[s].toLocaleString()}
              </span>
            </button>
          ))}
        </div>
        <div className={styles.filter_group}>
          <span className={styles.filter_label}>kind:</span>
          <button
            type="button"
            onClick={() => setQuery({ kind: null })}
            className={
              currentKind === null ? styles.btn_pill_active : styles.btn_pill
            }
          >
            all
          </button>
          {kindBreakdown.map(({ kind, open }) => (
            <button
              key={kind}
              type="button"
              onClick={() => setQuery({ kind })}
              className={
                currentKind === kind ? styles.btn_pill_active : styles.btn_pill
              }
            >
              {FLAG_KIND_META[kind]?.label ?? kind}
              <span className={styles.pill_count}>{open}</span>
            </button>
          ))}
        </div>
        <div className={styles.filter_group}>
          <span className={styles.filter_label}>severity:</span>
          {([null, "high", "med", "low"] as const).map((s) => (
            <button
              key={s ?? "all"}
              type="button"
              onClick={() => setQuery({ severity: s })}
              className={
                currentSeverity === s ? styles.btn_pill_active : styles.btn_pill
              }
            >
              {s ?? "all"}
            </button>
          ))}
        </div>
      </div>

      {selectableIds.size > 0 && (
        <div className={styles.toolbar}>
          <div className={styles.toolbar_left}>
            <span className={styles.toolbar_count}>
              {selectedIds.size} selected
              <span className={styles.toolbar_total}>
                {" "}· {selectableIds.size} open on this page
              </span>
            </span>
            {selectedIds.size > 0 ? (
              <button type="button" onClick={clearAll} className={styles.toolbar_clear}>
                clear
              </button>
            ) : (
              <button type="button" onClick={selectAllOpen} className={styles.toolbar_clear}>
                select all open
              </button>
            )}
          </div>
          <div className={styles.toolbar_right}>
            {batchResult && (
              <span className={styles.toolbar_result}>{batchResult}</span>
            )}
            <button
              type="button"
              onClick={onBatchResolve}
              disabled={batchPending || selectedIds.size === 0}
              className={styles.toolbar_apply}
            >
              {batchPending ? "resolving…" : `Resolve ${selectedIds.size} selected`}
            </button>
          </div>
        </div>
      )}

      <div className={styles.list}>
        {flags.length === 0 ? (
          <div className={styles.empty}>
            {currentStatus === "open"
              ? "No open flags. Either nothing's been detected or you've cleared the queue. Run the backfill script to populate from historical data."
              : "No flags match the current filters."}
          </div>
        ) : (
          flags.map((f) => (
            <FlagRow
              key={f.id}
              flag={f}
              selected={selectedIds.has(f.id)}
              onToggleSelect={() => toggle(f.id)}
            />
          ))
        )}
      </div>
    </>
  );
}
