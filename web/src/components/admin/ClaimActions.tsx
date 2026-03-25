"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import { updateClaimStatus } from "@/app/admin/claims/actions";

const EVIDENCE_TAGS = [
  "Skimpflation",
  "Stretchflation",
  "Slack Fill",
  "Paper Thin",
  "Spot the Difference",
  "So Smol",
  "Not as Advertised",
] as const;

export function ClaimActions({
  claimId,
  currentStatus,
  currentTags,
}: {
  claimId: string;
  currentStatus: string;
  currentTags?: string[];
}) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [showTags, setShowTags] = useState(false);
  const [selectedTags, setSelectedTags] = useState<Set<string>>(new Set());

  function handleAction(newStatus: string, tags?: string[]) {
    startTransition(async () => {
      await updateClaimStatus(claimId, newStatus, tags);
      router.refresh();
    });
  }

  function toggleTag(tag: string) {
    setSelectedTags((prev) => {
      const next = new Set(prev);
      if (next.has(tag)) next.delete(tag);
      else next.add(tag);
      return next;
    });
  }

  if (showTags) {
    return (
      <div className="space-y-2">
        <div className="flex gap-1.5 flex-wrap">
          {EVIDENCE_TAGS.map((tag) => (
            <button
              key={tag}
              onClick={() => toggleTag(tag)}
              className={`px-2.5 py-1 text-xs font-medium rounded border transition-all ${
                selectedTags.has(tag)
                  ? "bg-[var(--amber-base)] text-black border-[var(--amber-base)]"
                  : "bg-[var(--amber-bg)] text-[var(--amber-base)] border-[var(--amber-base)]/20 hover:brightness-125"
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() =>
              handleAction("evidence", Array.from(selectedTags))
            }
            disabled={isPending || selectedTags.size === 0}
            className="px-3 py-1 text-xs font-medium rounded border border-[var(--amber-base)]/20 bg-[var(--amber-bg)] text-[var(--amber-base)] hover:brightness-125 transition-all disabled:opacity-50"
          >
            {isPending ? "..." : "Confirm"}
          </button>
          <button
            onClick={() => {
              setShowTags(false);
              setSelectedTags(new Set());
            }}
            className="px-3 py-1 text-xs font-medium rounded border border-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-2 pt-1">
      {currentStatus === "pending" && (
        <>
          <button
            onClick={() => handleAction("approved")}
            disabled={isPending}
            className="px-3 py-1 text-xs font-medium rounded border border-[var(--green-border)] bg-[var(--green-bg)] text-[var(--green-base)] hover:brightness-125 transition-all disabled:opacity-50"
          >
            {isPending ? "..." : "Approve"}
          </button>
          <button
            onClick={() => setShowTags(true)}
            disabled={isPending}
            className="px-3 py-1 text-xs font-medium rounded border border-[var(--amber-base)]/20 bg-[var(--amber-bg)] text-[var(--amber-base)] hover:brightness-125 transition-all disabled:opacity-50"
          >
            Evidence Wall
          </button>
          <button
            onClick={() => handleAction("discarded")}
            disabled={isPending}
            className="px-3 py-1 text-xs font-medium rounded border border-[var(--red-border)] bg-[var(--red-bg)] text-[var(--red-base)] hover:brightness-125 transition-all disabled:opacity-50"
          >
            {isPending ? "..." : "Discard"}
          </button>
        </>
      )}
      {currentStatus === "discarded" && (
        <>
          <button
            onClick={() => handleAction("pending")}
            disabled={isPending}
            className="px-3 py-1 text-xs font-medium rounded border border-[var(--blue-border)] bg-[var(--blue-bg)] text-[var(--blue-base)] hover:brightness-125 transition-all disabled:opacity-50"
          >
            {isPending ? "..." : "Restore to Pending"}
          </button>
          <button
            onClick={() => setShowTags(true)}
            disabled={isPending}
            className="px-3 py-1 text-xs font-medium rounded border border-[var(--amber-base)]/20 bg-[var(--amber-bg)] text-[var(--amber-base)] hover:brightness-125 transition-all disabled:opacity-50"
          >
            Evidence Wall
          </button>
        </>
      )}
      {(currentStatus === "approved" || currentStatus === "evidence") && (
        <div className="flex items-center gap-2">
          {currentTags && currentTags.length > 0 && (
            <div className="flex gap-1">
              {currentTags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-0.5 text-xs font-medium rounded bg-[var(--amber-bg)] text-[var(--amber-base)] border border-[var(--amber-base)]/20"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
          <button
            onClick={() => handleAction("pending", [])}
            disabled={isPending}
            className="px-3 py-1 text-xs font-medium rounded border border-[var(--blue-border)] bg-[var(--blue-bg)] text-[var(--blue-base)] hover:brightness-125 transition-all disabled:opacity-50"
          >
            {isPending ? "..." : "Move to Pending"}
          </button>
        </div>
      )}
    </div>
  );
}
