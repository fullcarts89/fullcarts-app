"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { mergeBatch } from "./actions";
import styles from "./styles.module.css";

interface Props {
  selectedPairs: Array<{ sourceId: string; targetId: string }>;
  onClear(): void;
  totalShown: number;
}

/**
 * Sticky toolbar showing selection count + a "Merge selected" batch
 * button. Confirmation is mandatory and surfaces the per-pair count so
 * the admin sees exactly what they're about to apply.
 *
 * Result rendering: succeeded/failed counts plus a brief failures list
 * (first 5 errors). Full per-pair detail goes to the console for now.
 */
export default function BatchToolbar({ selectedPairs, onClear, totalShown }: Props) {
  const [isPending, startTransition] = useTransition();
  const [result, setResult] = useState<{
    succeeded: number;
    failed: number;
    errors: string[];
  } | null>(null);
  const router = useRouter();

  function onBatchMerge() {
    if (selectedPairs.length === 0) return;
    if (
      !window.confirm(
        `Apply ${selectedPairs.length} merges? Each one moves all claims, events, and variants from source into target, then retracts the source. Reversible per-row.`,
      )
    ) {
      return;
    }
    setResult(null);
    startTransition(async () => {
      try {
        const out = await mergeBatch(selectedPairs);
        const errors = out.details
          .filter((d) => !d.ok)
          .slice(0, 5)
          .map((d) => `${d.sourceId.slice(0, 8)} → ${d.targetId.slice(0, 8)}: ${d.error}`);
        setResult({ succeeded: out.succeeded, failed: out.failed, errors });
        if (out.failed > 0) {
          console.error("Batch merge — failed pairs:", out.details.filter((d) => !d.ok));
        }
        onClear();
        router.refresh();
      } catch (e) {
        setResult({
          succeeded: 0,
          failed: selectedPairs.length,
          errors: [e instanceof Error ? e.message : "unknown"],
        });
      }
    });
  }

  return (
    <div className={styles.toolbar}>
      <div className={styles.toolbar_left}>
        <span className={styles.toolbar_count}>
          {selectedPairs.length} selected
          <span className={styles.toolbar_total}> · {totalShown} shown</span>
        </span>
        {selectedPairs.length > 0 && (
          <button
            type="button"
            onClick={onClear}
            disabled={isPending}
            className={styles.toolbar_clear}
          >
            clear
          </button>
        )}
      </div>
      <div className={styles.toolbar_right}>
        {result && (
          <span
            className={
              result.failed > 0
                ? styles.toolbar_result_warn
                : styles.toolbar_result_ok
            }
          >
            {result.succeeded} merged
            {result.failed > 0 && ` · ${result.failed} failed`}
          </span>
        )}
        <button
          type="button"
          onClick={onBatchMerge}
          disabled={isPending || selectedPairs.length === 0}
          className={styles.toolbar_apply}
        >
          {isPending ? "merging…" : `Merge ${selectedPairs.length} selected`}
        </button>
      </div>
      {result && result.errors.length > 0 && (
        <div className={styles.toolbar_errors}>
          {result.errors.map((e, i) => (
            <div key={i} className={styles.toolbar_error}>
              {e}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
