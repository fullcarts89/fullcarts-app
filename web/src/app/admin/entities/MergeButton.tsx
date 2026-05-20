"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { mergeEntities } from "./actions";

/**
 * Phase 2D step 4 — merge entity B (this row) INTO entity A (the target
 * pasted in). The button shows a confirmation textbox where the admin
 * pastes the target entity id; on confirm we run the merge_entities RPC.
 *
 * Defensive UX:
 *  - Two-step (button -> input -> Merge) so a stray click can't fire.
 *  - Source id renders in the prompt so the admin can sanity-check direction.
 *  - Success toast shows the moved-row counts.
 */
export function MergeButton({
  sourceId,
  sourceLabel,
}: {
  sourceId: string;
  sourceLabel: string;
}) {
  const [open, setOpen] = useState(false);
  const [targetId, setTargetId] = useState("");
  const [isPending, startTransition] = useTransition();
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  function submit() {
    setError(null);
    setResult(null);
    const target = targetId.trim();
    if (!target) {
      setError("target id required");
      return;
    }
    if (target === sourceId) {
      setError("target must differ from source");
      return;
    }
    if (!/^[0-9a-f-]{36}$/i.test(target)) {
      setError("target must be a UUID");
      return;
    }
    startTransition(async () => {
      try {
        const out = await mergeEntities(sourceId, target);
        setResult(
          `Merged. ${out.claimsMoved} claims, ${out.eventsMoved} events, ${out.variantsMoved} variants moved.`,
        );
        setOpen(false);
        router.refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "merge failed");
      }
    });
  }

  if (!open) {
    return (
      <>
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="px-2 py-1 text-xs rounded border border-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--text-tertiary)]"
          title={`Merge "${sourceLabel}" INTO another entity`}
        >
          merge⇒
        </button>
        {result && (
          <div className="mt-1 text-xs text-[var(--green-base)] font-mono">{result}</div>
        )}
      </>
    );
  }

  return (
    <div className="flex flex-col items-end gap-1 min-w-[18rem]">
      <div className="text-xs text-[var(--text-tertiary)] font-mono break-all">
        merging FROM: {sourceLabel}
      </div>
      <div className="text-xs text-[var(--text-tertiary)] font-mono break-all">
        source id: {sourceId}
      </div>
      <input
        type="text"
        value={targetId}
        onChange={(e) => setTargetId(e.target.value)}
        placeholder="target entity UUID"
        disabled={isPending}
        autoFocus
        className="w-full px-2 py-1 text-xs font-mono bg-[var(--bg-primary)] border border-[var(--amber-base)] rounded focus:outline-none"
      />
      {error && <div className="text-xs text-[var(--red-base)] font-mono">{error}</div>}
      <div className="flex gap-2">
        <button
          type="button"
          onClick={submit}
          disabled={isPending}
          className="px-2 py-1 text-xs rounded border border-[var(--amber-base)] bg-[var(--amber-bg)] text-[var(--amber-base)] hover:brightness-125 disabled:opacity-50"
        >
          {isPending ? "merging…" : "Confirm merge"}
        </button>
        <button
          type="button"
          onClick={() => {
            setOpen(false);
            setTargetId("");
            setError(null);
          }}
          disabled={isPending}
          className="px-2 py-1 text-xs rounded border border-[var(--bg-tertiary)] text-[var(--text-secondary)]"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
