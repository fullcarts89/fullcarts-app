"use client";

import { useState, useTransition, useCallback } from "react";
import type { ClaimGroup, PendingClaim } from "./lib";
import GroupCardClient from "./GroupCardClient";
import EntityPicker from "./EntityPicker";

interface Props {
  groups: ClaimGroup[];
  categories: string[];
}

type Action = "approve_all" | "discard_all" | "merge_into" | "edit_then_approve" | "move_to_evidence";

interface EditDraft {
  brand: string;
  product_name: string;
  category: string;
  old_size: string;       // string for input binding; coerced server-side
  old_size_unit: string;
  new_size: string;
  new_size_unit: string;
  change_description: string;
}

const EMPTY_DRAFT: EditDraft = {
  brand: "",
  product_name: "",
  category: "",
  old_size: "",
  old_size_unit: "",
  new_size: "",
  new_size_unit: "",
  change_description: "",
};

const EVIDENCE_TAGS = [
  "Skimpflation",
  "Stretchflation",
  "Slack Fill",
  "Paper Thin",
  "Spot the Difference",
  "So Smol",
  "Not as Advertised",
] as const;

export default function GroupsClient({ groups: initial, categories }: Props) {
  const [groups, setGroups] = useState(initial);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [busy, startTransition] = useTransition();
  const [pickerFor, setPickerFor] = useState<ClaimGroup | null>(null);
  const [editFor, setEditFor] = useState<ClaimGroup | null>(null);
  const [editDraft, setEditDraft] = useState<EditDraft>(EMPTY_DRAFT);
  const [editClaimFor, setEditClaimFor] = useState<{ group: ClaimGroup; claim: PendingClaim } | null>(null);
  const [evidenceFor, setEvidenceFor] = useState<ClaimGroup | null>(null);
  const [evidenceTags, setEvidenceTags] = useState<Set<string>>(new Set());

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

  function handleAction(action: Action, group: ClaimGroup) {
    if (action === "merge_into") {
      setPickerFor(group);
      return;
    }
    if (action === "edit_then_approve") {
      setEditFor(group);
      setEditDraft({
        ...EMPTY_DRAFT,
        brand: group.brand_display === "(no brand)" ? "" : group.brand_display,
        product_name: group.name_display === "(no name)" ? "" : group.name_display,
      });
      return;
    }
    if (action === "move_to_evidence") {
      setEvidenceFor(group);
      setEvidenceTags(new Set());
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

  function handleMergeConfirmed(entityId: string) {
    if (!pickerFor) return;
    const g = pickerFor;
    setPickerFor(null);
    const ids = g.claims.map((c) => c.id);
    startTransition(async () => {
      try {
        await runBulkApi("bulk-merge-claims", { claim_ids: ids, entity_id: entityId });
        removeGroupsFromState([g.key]);
      } catch (e) {
        alert(`Failed: ${String(e)}`);
      }
    });
  }

  function buildPatch(d: EditDraft) {
    const patch: Record<string, unknown> = {};
    if (d.brand) patch.brand = d.brand;
    if (d.product_name) patch.product_name = d.product_name;
    if (d.category) patch.category = d.category;
    if (d.old_size) {
      const n = parseFloat(d.old_size);
      if (!Number.isNaN(n)) patch.old_size = n;
    }
    if (d.old_size_unit) patch.old_size_unit = d.old_size_unit;
    if (d.new_size) {
      const n = parseFloat(d.new_size);
      if (!Number.isNaN(n)) patch.new_size = n;
    }
    if (d.new_size_unit) patch.new_size_unit = d.new_size_unit;
    if (d.change_description) patch.change_description = d.change_description;
    return patch;
  }

  function handleEditConfirmed() {
    if (!editFor) return;
    const g = editFor;
    setEditFor(null);
    const patch = buildPatch(editDraft);
    const ids = g.claims.map((c) => c.id);
    startTransition(async () => {
      try {
        await runBulkApi("bulk-edit-approve-claims", { claim_ids: ids, patch, approve: true });
        removeGroupsFromState([g.key]);
      } catch (e) {
        alert(`Failed: ${String(e)}`);
      }
    });
  }

  function handleClaimEdit(claimId: string, group: ClaimGroup) {
    const claim = group.claims.find((c) => c.id === claimId);
    if (!claim) return;
    setEditClaimFor({ group, claim });
    setEditDraft({
      brand: claim.brand || "",
      product_name: claim.product_name || "",
      category: "",                                   // not loaded on PendingClaim today; leave blank
      old_size: claim.old_size != null ? String(claim.old_size) : "",
      old_size_unit: claim.size_unit || "",
      new_size: claim.new_size != null ? String(claim.new_size) : "",
      new_size_unit: claim.size_unit || "",
      change_description: "",                         // not loaded on PendingClaim
    });
  }

  function handleClaimEditConfirmed(approve: boolean) {
    if (!editClaimFor) return;
    const { group, claim } = editClaimFor;
    setEditClaimFor(null);
    const patch = buildPatch(editDraft);
    startTransition(async () => {
      try {
        await runBulkApi("bulk-edit-approve-claims", { claim_ids: [claim.id], patch, approve });
        // Update local state: remove if approved, else update the claim's fields in place.
        if (approve) {
          setGroups((gs) =>
            gs
              .map((g) => {
                if (g.key !== group.key) return g;
                const remaining = g.claims.filter((c) => c.id !== claim.id);
                return { ...g, claims: remaining, count: remaining.length };
              })
              .filter((g) => g.count > 0),
          );
        } else {
          setGroups((gs) =>
            gs.map((g) => {
              if (g.key !== group.key) return g;
              return {
                ...g,
                claims: g.claims.map((c) =>
                  c.id === claim.id
                    ? {
                        ...c,
                        brand: (patch.brand as string) ?? c.brand,
                        product_name: (patch.product_name as string) ?? c.product_name,
                        old_size: (patch.old_size as number) ?? c.old_size,
                        new_size: (patch.new_size as number) ?? c.new_size,
                        size_unit:
                          (patch.old_size_unit as string) ??
                          (patch.new_size_unit as string) ??
                          c.size_unit,
                      }
                    : c,
                ),
              };
            }),
          );
        }
      } catch (e) {
        alert(`Failed: ${String(e)}`);
      }
    });
  }

  function handleEvidenceConfirmed() {
    if (!evidenceFor || evidenceTags.size === 0) return;
    const g = evidenceFor;
    const tags = Array.from(evidenceTags);
    setEvidenceFor(null);
    const ids = g.claims.map((c) => c.id);
    startTransition(async () => {
      try {
        await runBulkApi("bulk-evidence-claims", { claim_ids: ids, tags });
        removeGroupsFromState([g.key]);
      } catch (e) {
        alert(`Failed: ${String(e)}`);
      }
    });
  }

  function handleClaimAction(
    claimId: string,
    action: "approve" | "discard" | "evidence",
    group: ClaimGroup,
  ) {
    if (action === "evidence") {
      // Same modal flow as group-level, but pre-target a single claim
      setEvidenceFor({ ...group, claims: group.claims.filter((c) => c.id === claimId), count: 1 });
      setEvidenceTags(new Set());
      return;
    }
    if (!confirm(`${action} this single claim?`)) return;
    const route = action === "approve" ? "bulk-approve-claims" : "bulk-discard-claims";
    startTransition(async () => {
      try {
        await runBulkApi(route, { claim_ids: [claimId] });
        // Remove this single claim from the group's local state; if group becomes empty, remove it.
        setGroups((gs) =>
          gs
            .map((g) => {
              if (g.key !== group.key) return g;
              const remainingClaims = g.claims.filter((c) => c.id !== claimId);
              return { ...g, claims: remainingClaims, count: remainingClaims.length };
            })
            .filter((g) => g.count > 0),
        );
      } catch (e) {
        alert(`Failed: ${String(e)}`);
      }
    });
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
          busy={busy}
          onClaimAction={handleClaimAction}
          onClaimEdit={handleClaimEdit}
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
              disabled={busy}
              onClick={() => handleBulkAction("approve_all")}
              className="px-3 py-1.5 text-sm rounded border border-[var(--green-border)] bg-[var(--green-bg)] text-[var(--green-base)] hover:opacity-80 disabled:opacity-50"
            >
              Approve selected
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => handleBulkAction("discard_all")}
              className="px-3 py-1.5 text-sm rounded border border-[var(--red-border)] bg-[var(--red-bg)] text-[var(--red-text)] hover:opacity-80 disabled:opacity-50"
            >
              Discard selected
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => setSelected(new Set())}
              className="px-3 py-1.5 text-sm rounded border border-[var(--bg-tertiary)] text-[var(--text-secondary)]"
            >
              Clear
            </button>
          </div>
        </div>
      )}

      {pickerFor && (
        <EntityPicker
          brand={pickerFor.brand_display}
          nameHint={pickerFor.name_display}
          groupSizeChange={pickerFor.size_change}
          onCancel={() => setPickerFor(null)}
          onPick={handleMergeConfirmed}
        />
      )}

      {editFor && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-6">
          <div className="bg-[var(--bg-secondary)] border border-[var(--bg-tertiary)] rounded-lg p-6 w-full max-w-md space-y-3">
            <h3 className="font-medium">
              Edit {editFor.count} claims, then approve
            </h3>
            <p className="text-xs text-[var(--text-tertiary)]">
              Fields you leave blank stay as-is on each claim.
            </p>
            <label className="block text-sm">
              Brand
              <input
                type="text"
                value={editDraft.brand}
                onChange={(e) => setEditDraft((d) => ({ ...d, brand: e.target.value }))}
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
            <label className="block text-sm">
              Product name
              <input
                type="text"
                value={editDraft.product_name}
                onChange={(e) => setEditDraft((d) => ({ ...d, product_name: e.target.value }))}
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
            <label className="block text-sm">
              Category
              <select
                value={editDraft.category}
                onChange={(e) => setEditDraft((d) => ({ ...d, category: e.target.value }))}
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              >
                <option value="">(keep existing)</option>
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <div className="grid grid-cols-2 gap-2">
              <label className="block text-sm">
                Old size
                <input
                  type="number"
                  step="any"
                  value={editDraft.old_size}
                  onChange={(e) => setEditDraft((d) => ({ ...d, old_size: e.target.value }))}
                  className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
                />
              </label>
              <label className="block text-sm">
                Old unit
                <input
                  type="text"
                  value={editDraft.old_size_unit}
                  onChange={(e) => setEditDraft((d) => ({ ...d, old_size_unit: e.target.value }))}
                  placeholder="g / ml / oz / ct"
                  className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
                />
              </label>
              <label className="block text-sm">
                New size
                <input
                  type="number"
                  step="any"
                  value={editDraft.new_size}
                  onChange={(e) => setEditDraft((d) => ({ ...d, new_size: e.target.value }))}
                  className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
                />
              </label>
              <label className="block text-sm">
                New unit
                <input
                  type="text"
                  value={editDraft.new_size_unit}
                  onChange={(e) => setEditDraft((d) => ({ ...d, new_size_unit: e.target.value }))}
                  placeholder="g / ml / oz / ct"
                  className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
                />
              </label>
            </div>
            <label className="block text-sm">
              Change description
              <input
                type="text"
                value={editDraft.change_description}
                onChange={(e) => setEditDraft((d) => ({ ...d, change_description: e.target.value }))}
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setEditFor(null)} className="px-3 py-1.5 text-sm">
                Cancel
              </button>
              <button
                type="button"
                onClick={handleEditConfirmed}
                disabled={busy}
                className="px-3 py-1.5 text-sm rounded border border-[var(--green-border)] bg-[var(--green-bg)] text-[var(--green-base)] disabled:opacity-50"
              >
                Apply + Approve all {editFor.count}
              </button>
            </div>
          </div>
        </div>
      )}

      {editClaimFor && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-6 z-50">
          <div className="bg-[var(--bg-secondary)] border border-[var(--bg-tertiary)] rounded-lg p-6 w-full max-w-md space-y-3">
            <h3 className="font-medium">
              Edit claim from group: {editClaimFor.group.brand_display} · {editClaimFor.group.name_display}
            </h3>
            <p className="text-xs text-[var(--text-tertiary)]">
              Changes apply only to this one claim.
            </p>
            <label className="block text-sm">
              Brand
              <input
                type="text"
                value={editDraft.brand}
                onChange={(e) => setEditDraft((d) => ({ ...d, brand: e.target.value }))}
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
            <label className="block text-sm">
              Product name
              <input
                type="text"
                value={editDraft.product_name}
                onChange={(e) => setEditDraft((d) => ({ ...d, product_name: e.target.value }))}
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
            <label className="block text-sm">
              Category
              <select
                value={editDraft.category}
                onChange={(e) => setEditDraft((d) => ({ ...d, category: e.target.value }))}
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              >
                <option value="">(keep existing)</option>
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <div className="grid grid-cols-2 gap-2">
              <label className="block text-sm">
                Old size
                <input
                  type="number"
                  step="any"
                  value={editDraft.old_size}
                  onChange={(e) => setEditDraft((d) => ({ ...d, old_size: e.target.value }))}
                  className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
                />
              </label>
              <label className="block text-sm">
                Old unit
                <input
                  type="text"
                  value={editDraft.old_size_unit}
                  onChange={(e) => setEditDraft((d) => ({ ...d, old_size_unit: e.target.value }))}
                  placeholder="g / ml / oz / ct"
                  className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
                />
              </label>
              <label className="block text-sm">
                New size
                <input
                  type="number"
                  step="any"
                  value={editDraft.new_size}
                  onChange={(e) => setEditDraft((d) => ({ ...d, new_size: e.target.value }))}
                  className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
                />
              </label>
              <label className="block text-sm">
                New unit
                <input
                  type="text"
                  value={editDraft.new_size_unit}
                  onChange={(e) => setEditDraft((d) => ({ ...d, new_size_unit: e.target.value }))}
                  placeholder="g / ml / oz / ct"
                  className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
                />
              </label>
            </div>
            <label className="block text-sm">
              Change description
              <input
                type="text"
                value={editDraft.change_description}
                onChange={(e) => setEditDraft((d) => ({ ...d, change_description: e.target.value }))}
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setEditClaimFor(null)} className="px-3 py-1.5 text-sm">
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleClaimEditConfirmed(false)}
                disabled={busy}
                className="px-3 py-1.5 text-sm rounded border border-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] disabled:opacity-50"
              >
                Save (keep pending)
              </button>
              <button
                type="button"
                onClick={() => handleClaimEditConfirmed(true)}
                disabled={busy}
                className="px-3 py-1.5 text-sm rounded border border-[var(--green-border)] bg-[var(--green-bg)] text-[var(--green-base)] disabled:opacity-50"
              >
                Save + Approve
              </button>
            </div>
          </div>
        </div>
      )}

      {evidenceFor && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-6 z-50">
          <div className="bg-[var(--bg-secondary)] border border-[var(--bg-tertiary)] rounded-lg p-6 w-full max-w-md space-y-3">
            <h3 className="font-medium">Move {evidenceFor.count} claims to evidence wall</h3>
            <p className="text-xs text-[var(--text-tertiary)]">
              Pick one or more tags. Claims will move to status=&apos;evidence&apos; with these tags.
            </p>
            <div className="flex gap-1.5 flex-wrap">
              {EVIDENCE_TAGS.map((tag) => {
                const selected = evidenceTags.has(tag);
                return (
                  <button
                    key={tag}
                    type="button"
                    onClick={() =>
                      setEvidenceTags((prev) => {
                        const next = new Set(prev);
                        if (next.has(tag)) next.delete(tag);
                        else next.add(tag);
                        return next;
                      })
                    }
                    className={`px-2.5 py-1 text-xs font-medium rounded border transition-all ${
                      selected
                        ? "bg-[var(--amber-base)] text-black border-[var(--amber-base)]"
                        : "bg-[var(--amber-bg)] text-[var(--amber-base)] border-[var(--amber-base)]/20 hover:brightness-125"
                    }`}
                  >
                    {tag}
                  </button>
                );
              })}
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setEvidenceFor(null)} className="px-3 py-1.5 text-sm">
                Cancel
              </button>
              <button
                type="button"
                onClick={handleEvidenceConfirmed}
                disabled={busy || evidenceTags.size === 0}
                className="px-3 py-1.5 text-sm rounded border border-[var(--amber-base)]/20 bg-[var(--amber-bg)] text-[var(--amber-base)] disabled:opacity-50"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
