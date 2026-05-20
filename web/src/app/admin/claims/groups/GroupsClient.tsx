"use client";

import { useState, useTransition, useCallback } from "react";
import type { ClaimGroup, PendingClaim } from "./lib";
import GroupCardClient from "./GroupCardClient";
import ResolveModal from "./ResolveModal";

interface Props {
  groups: ClaimGroup[];
  categories: string[];
}

type GroupAction = "approve_all" | "discard_all" | "resolve";
type ClaimAction = "approve" | "discard" | "resolve";

export default function GroupsClient({ groups: initial, categories }: Props) {
  const [groups, setGroups] = useState(initial);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [busy, startTransition] = useTransition();
  const [modalBusy, setModalBusy] = useState(false);
  const [resolveFor, setResolveFor] = useState<
    { group: ClaimGroup; claim?: PendingClaim } | null
  >(null);

  const interactiveBusy = busy || modalBusy;

  const toggle = useCallback((key: string, next: boolean) => {
    setSelected((prev) => {
      const n = new Set(prev);
      if (next) n.add(key);
      else n.delete(key);
      return n;
    });
  }, []);

  async function runBulkApi(route: string, body: object): Promise<void> {
    const res = await fetch(`/api/admin/${route}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const t = await res.text();
      throw new Error(`${route}: ${res.status} ${t}`);
    }
  }

  function removeGroupsFromState(keys: string[]) {
    const ks = new Set(keys);
    setGroups((gs) => gs.filter((g) => !ks.has(g.key)));
    setSelected((sel) => {
      const n = new Set(sel);
      for (const k of ks) n.delete(k);
      return n;
    });
  }

  function removeClaimIdsFromState(claimIds: string[]) {
    const idSet = new Set(claimIds);
    setGroups((gs) =>
      gs
        .map((g) => {
          const remaining = g.claims.filter((c) => !idSet.has(c.id));
          if (remaining.length === g.claims.length) return g; // no overlap
          return { ...g, claims: remaining, count: remaining.length };
        })
        .filter((g) => g.count > 0),
    );
  }

  function handleAction(action: GroupAction, group: ClaimGroup) {
    if (action === "resolve") {
      setResolveFor({ group });
      return;
    }
    if (!confirm(`${action.replace("_", " ")} for ${group.count} claims?`)) return;
    const ids = group.claims.map((c) => c.id);
    const route = action === "approve_all" ? "bulk-approve-claims" : "bulk-discard-claims";
    startTransition(async () => {
      try {
        await runBulkApi(route, { claim_ids: ids });
        removeGroupsFromState([group.key]);
      } catch (e) {
        alert(`Failed: ${String(e)}`);
      }
    });
  }

  function handleBulkAction(action: "approve_all" | "discard_all") {
    if (selected.size === 0) return;
    const groupsToActOn = groups.filter((g) => selected.has(g.key));
    const totalClaims = groupsToActOn.reduce((acc, g) => acc + g.count, 0);
    if (!confirm(`${action.replace("_", " ")} for ${totalClaims} claims across ${groupsToActOn.length} groups?`)) return;

    startTransition(async () => {
      const done: string[] = [];
      const failed: string[] = [];
      for (const g of groupsToActOn) {
        const ids = g.claims.map((c) => c.id);
        const route = action === "approve_all" ? "bulk-approve-claims" : "bulk-discard-claims";
        try {
          await runBulkApi(route, { claim_ids: ids });
          done.push(g.key);
        } catch (e) {
          failed.push(`${g.brand_display} · ${g.name_display}: ${String(e)}`);
        }
      }
      removeGroupsFromState(done);
      if (failed.length > 0) {
        alert(`Some groups failed:\n\n${failed.join("\n")}`);
      }
    });
  }

  function handleClaimAction(claimId: string, action: ClaimAction, group: ClaimGroup) {
    if (action === "resolve") {
      const claim = group.claims.find((c) => c.id === claimId);
      if (!claim) return;
      setResolveFor({ group, claim });
      return;
    }
    if (!confirm(`${action} this single claim?`)) return;
    const route = action === "approve" ? "bulk-approve-claims" : "bulk-discard-claims";
    startTransition(async () => {
      try {
        await runBulkApi(route, { claim_ids: [claimId] });
        removeClaimIdsFromState([claimId]);
      } catch (e) {
        alert(`Failed: ${String(e)}`);
      }
    });
  }

  function handleResolved(_result: { mode: "approve" | "evidence"; claimIds: string[] }) {
    // Both approve and evidence paths take the claims out of the pending
    // queue (status is no longer 'pending'), so we remove them from
    // local state regardless of which action ran.
    removeClaimIdsFromState(_result.claimIds);
    setResolveFor(null);
  }

  return (
    <>
      {groups.map((g) => (
        <GroupCardClient
          key={g.key}
          group={g}
          selected={selected.has(g.key)}
          onSelectChange={(n) => toggle(g.key, n)}
          onAction={handleAction}
          busy={interactiveBusy}
          onClaimAction={handleClaimAction}
        />
      ))}

      {selected.size > 0 && (
        <div className="fixed bottom-0 inset-x-0 border-t border-[var(--bg-tertiary)] bg-[var(--bg-secondary)] px-6 py-3 flex items-center gap-3">
          <span className="text-sm">
            {selected.size} group{selected.size === 1 ? "" : "s"} selected
          </span>
          <div className="ml-auto flex gap-2">
            <button
              type="button"
              disabled={interactiveBusy}
              onClick={() => handleBulkAction("approve_all")}
              className="px-3 py-1.5 text-sm rounded border border-[var(--green-border)] bg-[var(--green-bg)] text-[var(--green-base)] hover:opacity-80 disabled:opacity-50"
            >
              Approve selected
            </button>
            <button
              type="button"
              disabled={interactiveBusy}
              onClick={() => handleBulkAction("discard_all")}
              className="px-3 py-1.5 text-sm rounded border border-[var(--red-border)] bg-[var(--red-bg)] text-[var(--red-text)] hover:opacity-80 disabled:opacity-50"
            >
              Discard selected
            </button>
            <button
              type="button"
              disabled={interactiveBusy}
              onClick={() => setSelected(new Set())}
              className="px-3 py-1.5 text-sm rounded border border-[var(--bg-tertiary)] text-[var(--text-secondary)]"
            >
              Clear
            </button>
          </div>
        </div>
      )}

      {resolveFor && (
        <ResolveModal
          group={resolveFor.group}
          claim={resolveFor.claim}
          categories={categories}
          onCancel={() => setResolveFor(null)}
          onResolved={handleResolved}
          setBusy={setModalBusy}
        />
      )}
    </>
  );
}
