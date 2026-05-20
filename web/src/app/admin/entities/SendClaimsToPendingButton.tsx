"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { resetClaimsToPending } from "./actions";

/**
 * Phase 2D step 3 — send a retracted entity's claims back to the
 * pending review queue. Only renders on retracted rows; the server
 * action also enforces the precondition.
 *
 * One-click + confirmation prompt with the claim count.
 */
export function SendClaimsToPendingButton({
  entityId,
  entityLabel,
}: {
  entityId: string;
  entityLabel: string;
}) {
  const [isPending, startTransition] = useTransition();
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  function handle() {
    setError(null);
    setResult(null);
    if (
      !window.confirm(
        `Send every claim attached to "${entityLabel}" back to the pending admin queue?\n\nThis flips status to 'pending' and clears matched_entity_id on each row. Use this when the entity is wrong and the underlying claims should be re-reviewed.`,
      )
    ) {
      return;
    }
    startTransition(async () => {
      try {
        const out = await resetClaimsToPending(entityId);
        setResult(`${out.claimsReset} claims sent to pending`);
        router.refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "send-back failed");
      }
    });
  }

  return (
    <div className="flex flex-col items-end gap-0.5">
      <button
        type="button"
        onClick={handle}
        disabled={isPending}
        className="px-2 py-1 text-xs rounded border border-[var(--blue-border)] bg-[var(--blue-bg)] text-[var(--blue-base)] hover:brightness-125 disabled:opacity-50"
        title="Reset attached claims to pending"
      >
        {isPending ? "…" : "↺ pending"}
      </button>
      {result && (
        <span className="text-xs text-[var(--green-base)] font-mono">{result}</span>
      )}
      {error && (
        <span className="text-xs text-[var(--red-base)] font-mono break-all">{error}</span>
      )}
    </div>
  );
}
