"use client";

import { useState } from "react";
import type { ClaimGroup, PendingClaim } from "./lib";
import EntityPicker from "./EntityPicker";

// Unified Resolve modal — replaces the previous Edit / Merge / Evidence
// modals in /admin/claims/groups. Works in two modes:
//   - Group mode (claim undefined): fields default blank ("leave as-is
//     per claim"); the modal acts on every claim in `group`.
//   - Per-claim mode (claim provided): fields pre-fill from the single
//     claim's current values; the modal acts on just that claim.
//
// The three sections are all optional except the Action choice:
//   1. Edit fields — patch brand/name/category/size/etc. Blank = keep.
//   2. Target entity — pick an existing entity OR leave blank to
//      auto-derive (find-or-create by edited brand+name).
//   3. Action — Approve or Tag-as-Evidence (with tag chips).
//
// The modal owns all API calls. The parent handles only local-state
// reconciliation via the `onResolved` callback.

const EVIDENCE_TAGS = [
  "Skimpflation",
  "Stretchflation",
  "Slack Fill",
  "Paper Thin",
  "Spot the Difference",
  "So Smol",
  "Not as Advertised",
] as const;

interface EditDraft {
  brand: string;
  product_name: string;
  category: string;
  old_size: string; // string for input binding; coerced server-side
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

function draftFromClaim(c: PendingClaim): EditDraft {
  return {
    brand: c.brand || "",
    product_name: c.product_name || "",
    category: "", // not loaded on PendingClaim today
    old_size: c.old_size != null ? String(c.old_size) : "",
    old_size_unit: c.size_unit || "",
    new_size: c.new_size != null ? String(c.new_size) : "",
    new_size_unit: c.size_unit || "",
    change_description: "",
  };
}

// Group-mode pre-fill: pull values that DEFINITELY apply to every claim in
// the group (the grouper key guarantees they share brand/name canonicalisation
// and exact size_change). Category and change_description vary per claim, so
// leave them blank (founder fills in when they want to overwrite all claims'
// values, otherwise blank = leave each claim's value as-is).
function draftFromGroup(g: ClaimGroup): EditDraft {
  const rep = g.claims[0];
  return {
    brand: g.brand_display && g.brand_display !== "(no brand)" ? g.brand_display : "",
    product_name:
      g.name_display && g.name_display !== "(no name)" ? g.name_display : "",
    category: "",
    old_size: rep && rep.old_size != null ? String(rep.old_size) : "",
    old_size_unit: rep ? rep.size_unit || "" : "",
    new_size: rep && rep.new_size != null ? String(rep.new_size) : "",
    new_size_unit: rep ? rep.size_unit || "" : "",
    change_description: "",
  };
}

function buildPatch(d: EditDraft): Record<string, unknown> {
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

interface SelectedEntity {
  id: string;
  brand: string;
  canonical_name: string;
}

export interface ResolveModalProps {
  group: ClaimGroup;
  claim?: PendingClaim;
  categories: string[];
  onCancel: () => void;
  onResolved: (result: { mode: "approve" | "evidence"; claimIds: string[] }) => void;
  setBusy: (b: boolean) => void;
}

export default function ResolveModal({
  group,
  claim,
  categories,
  onCancel,
  onResolved,
  setBusy,
}: ResolveModalProps) {
  const [fields, setFields] = useState<EditDraft>(() =>
    claim ? draftFromClaim(claim) : draftFromGroup(group),
  );
  const [selectedEntity, setSelectedEntity] = useState<SelectedEntity | null>(null);
  const [action, setAction] = useState<"approve" | "evidence">("approve");
  const [evidenceTags, setEvidenceTags] = useState<Set<string>>(new Set());
  const [showPicker, setShowPicker] = useState(false);
  const [pending, setPending] = useState(false);

  const claimIds = claim ? [claim.id] : group.claims.map((c) => c.id);
  const targetCount = claim ? 1 : group.count;

  async function runApi(route: string, body: object): Promise<void> {
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

  async function handleConfirm() {
    const patch = buildPatch(fields);
    const hasPatch = Object.keys(patch).length > 0;
    setPending(true);
    setBusy(true);
    try {
      if (action === "approve") {
        // One call — bulk-edit-approve-claims handles patch + entity in
        // a single transaction.
        await runApi("bulk-edit-approve-claims", {
          claim_ids: claimIds,
          patch,
          approve: true,
          ...(selectedEntity ? { entity_id: selectedEntity.id } : {}),
        });
        onResolved({ mode: "approve", claimIds });
      } else {
        // Evidence path. If there's a patch, write it first without
        // changing status; then flip status + tags + (optional) entity.
        if (hasPatch) {
          await runApi("bulk-edit-approve-claims", {
            claim_ids: claimIds,
            patch,
            approve: false,
          });
        }
        await runApi("bulk-evidence-claims", {
          claim_ids: claimIds,
          tags: Array.from(evidenceTags),
          ...(selectedEntity ? { entity_id: selectedEntity.id } : {}),
        });
        onResolved({ mode: "evidence", claimIds });
      }
    } catch (e) {
      alert(`Failed: ${String(e)}`);
    } finally {
      setPending(false);
      setBusy(false);
    }
  }

  const confirmDisabled =
    pending || (action === "evidence" && evidenceTags.size === 0);

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-6 z-40">
      <div className="bg-[var(--bg-secondary)] border border-[var(--bg-tertiary)] rounded-lg p-6 w-full max-w-2xl space-y-4 max-h-[90vh] overflow-y-auto">
        <header>
          <h3 className="font-medium">
            Resolve {claim ? "1 claim" : `${targetCount} claims`} —{" "}
            {group.brand_display} · {group.name_display}
          </h3>
          <p className="text-xs text-[var(--text-tertiary)] mt-1">
            Optional: edit fields and/or pick an entity. Then choose what to do.
          </p>
        </header>

        {/* SECTION 1: EDIT */}
        <section className="space-y-2">
          <h4 className="text-sm font-medium text-[var(--text-secondary)]">
            Edit fields{claim ? "" : " (applied to every claim)"}
          </h4>
          <p className="text-xs text-[var(--text-tertiary)]">
            Leave any field blank to keep it as-is.
          </p>
          <label className="block text-sm">
            Brand
            <input
              type="text"
              value={fields.brand}
              onChange={(e) => setFields((d) => ({ ...d, brand: e.target.value }))}
              className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
            />
          </label>
          <label className="block text-sm">
            Product name
            <input
              type="text"
              value={fields.product_name}
              onChange={(e) =>
                setFields((d) => ({ ...d, product_name: e.target.value }))
              }
              className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
            />
          </label>
          <label className="block text-sm">
            Category
            <select
              value={fields.category}
              onChange={(e) =>
                setFields((d) => ({ ...d, category: e.target.value }))
              }
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
                value={fields.old_size}
                onChange={(e) =>
                  setFields((d) => ({ ...d, old_size: e.target.value }))
                }
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
            <label className="block text-sm">
              Old unit
              <input
                type="text"
                value={fields.old_size_unit}
                onChange={(e) =>
                  setFields((d) => ({ ...d, old_size_unit: e.target.value }))
                }
                placeholder="g / ml / oz / ct"
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
            <label className="block text-sm">
              New size
              <input
                type="number"
                step="any"
                value={fields.new_size}
                onChange={(e) =>
                  setFields((d) => ({ ...d, new_size: e.target.value }))
                }
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
            <label className="block text-sm">
              New unit
              <input
                type="text"
                value={fields.new_size_unit}
                onChange={(e) =>
                  setFields((d) => ({ ...d, new_size_unit: e.target.value }))
                }
                placeholder="g / ml / oz / ct"
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
          </div>
          <label className="block text-sm">
            Change description
            <input
              type="text"
              value={fields.change_description}
              onChange={(e) =>
                setFields((d) => ({ ...d, change_description: e.target.value }))
              }
              className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
            />
          </label>
        </section>

        {/* SECTION 2: ENTITY */}
        <section className="space-y-2">
          <h4 className="text-sm font-medium text-[var(--text-secondary)]">
            Target entity
          </h4>
          {selectedEntity ? (
            <div className="flex items-center gap-2 text-sm">
              <span className="font-medium">{selectedEntity.brand}</span>
              <span>·</span>
              <span>{selectedEntity.canonical_name}</span>
              <button
                type="button"
                onClick={() => setSelectedEntity(null)}
                className="ml-auto text-xs text-[var(--text-tertiary)] hover:text-[var(--text-primary)] underline"
              >
                change
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-sm text-[var(--text-tertiary)]">
              <span>Auto-find or create from edited brand+name.</span>
              <button
                type="button"
                onClick={() => setShowPicker(true)}
                className="text-xs text-[var(--blue-base)] hover:underline"
              >
                Pick existing entity →
              </button>
            </div>
          )}
        </section>

        {/* SECTION 3: ACTION */}
        <section className="space-y-2">
          <h4 className="text-sm font-medium text-[var(--text-secondary)]">
            Action
          </h4>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="radio"
              name="resolve-action"
              checked={action === "approve"}
              onChange={() => setAction("approve")}
            />
            <span>
              Approve{" "}
              <span className="text-[var(--text-tertiary)]">
                — move to matched, attach to entity
              </span>
            </span>
          </label>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="radio"
              name="resolve-action"
              checked={action === "evidence"}
              onChange={() => setAction("evidence")}
            />
            <span>
              Tag as Evidence{" "}
              <span className="text-[var(--text-tertiary)]">
                — pin to evidence wall with tags
              </span>
            </span>
          </label>
          {action === "evidence" && (
            <div className="flex gap-1.5 flex-wrap pt-1">
              {EVIDENCE_TAGS.map((tag) => {
                const isSel = evidenceTags.has(tag);
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
                      isSel
                        ? "bg-[var(--amber-base)] text-black border-[var(--amber-base)]"
                        : "bg-[var(--amber-bg)] text-[var(--amber-base)] border-[var(--amber-base)]/20 hover:brightness-125"
                    }`}
                  >
                    {tag}
                  </button>
                );
              })}
            </div>
          )}
        </section>

        <div className="flex justify-end gap-2 pt-2 border-t border-[var(--bg-tertiary)]">
          <button
            type="button"
            onClick={onCancel}
            disabled={pending}
            className="px-3 py-1.5 text-sm disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            disabled={confirmDisabled}
            className={`px-3 py-1.5 text-sm rounded border disabled:opacity-50 ${
              action === "evidence"
                ? "border-[var(--amber-base)]/20 bg-[var(--amber-bg)] text-[var(--amber-base)]"
                : "border-[var(--green-border)] bg-[var(--green-bg)] text-[var(--green-base)]"
            }`}
          >
            {pending ? "Working..." : "Confirm"}
          </button>
        </div>

        {showPicker && (
          <EntityPicker
            brand={fields.brand || group.brand_display}
            nameHint={fields.product_name || group.name_display}
            groupSizeChange={group.size_change}
            onCancel={() => setShowPicker(false)}
            onPick={(entity) => {
              setSelectedEntity(entity);
              setShowPicker(false);
            }}
          />
        )}
      </div>
    </div>
  );
}
