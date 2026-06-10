"use client";

import { useState, useTransition } from "react";
import { useClaimList } from "@/app/admin/claims/ClaimListContext";

const EVIDENCE_TAGS = [
  "Skimpflation",
  "Stretchflation",
  "Slack Fill",
  "Paper Thin",
  "Spot the Difference",
  "So Smol",
  "Not as Advertised",
] as const;

// POST a single-claim admin mutation to a route handler. We use route
// handlers (not Server Actions) because Server Actions auto-revalidate the
// heavy /admin/claims route on completion, which left the buttons stuck on
// "..." for the whole re-render — the "rejections stall" bug. On success the
// caller removes the card optimistically; no router.refresh needed.
async function postAdmin(route: string, body: object): Promise<void> {
  const res = await fetch(`/api/admin/${route}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const j = await res.json();
      if (j?.error) msg = j.error;
    } catch {
      /* non-JSON error body */
    }
    throw new Error(msg);
  }
}

export function ClaimActions({
  claimId,
  currentStatus,
  currentTags,
}: {
  claimId: string;
  currentStatus: string;
  currentTags?: string[];
}) {
  const { remove } = useClaimList();
  const [isPending, startTransition] = useTransition();
  const [showTags, setShowTags] = useState(false);
  const [selectedTags, setSelectedTags] = useState<Set<string>>(new Set());

  // Every action takes the claim out of the current tab's filter, so on
  // success we drop the card from local state instead of refreshing the page.
  function run(route: string, extra?: object) {
    startTransition(async () => {
      try {
        await postAdmin(route, { claim_ids: [claimId], ...extra });
        remove(claimId);
      } catch (e) {
        alert(e instanceof Error ? e.message : "Action failed");
      }
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
              run("bulk-evidence-claims", { tags: Array.from(selectedTags) })
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
            onClick={() => run("bulk-approve-claims")}
            disabled={isPending}
            className="px-3 py-1 text-xs font-medium rounded border border-[var(--green-border)] bg-[var(--green-bg)] text-[var(--green-base)] hover:brightness-125 transition-all disabled:opacity-50"
            title="Mark this claim as a real shrinkflation event. The next daily promote run will create or fold it into a published_change."
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
            onClick={() => run("bulk-discard-claims")}
            disabled={isPending}
            className="px-3 py-1 text-xs font-medium rounded border border-[var(--red-border)] bg-[var(--red-bg)] text-[var(--red-text)] hover:brightness-125 transition-all disabled:opacity-50"
          >
            {isPending ? "..." : "Discard"}
          </button>
        </>
      )}
      {currentStatus === "discarded" && (
        <>
          <button
            onClick={() => run("claims-to-pending")}
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
      {(currentStatus === "matched" || currentStatus === "evidence") && (
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
            onClick={() => run("claims-to-pending")}
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
