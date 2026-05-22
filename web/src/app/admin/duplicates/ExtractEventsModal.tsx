"use client";

import { useEffect, useState } from "react";

interface EntityRow {
  id: string;
  brand: string;
  canonical_name: string;
  category: string | null;
  event_count: number;
  event_sizes: string[];
}

interface Props {
  sourceEntity: { id: string; brand: string; canonical_name: string };
  sizeSignature: string;
  sizeBefore: number;
  sizeAfter: number;
  sizeUnit: string;
  /** Hint shown in the header, e.g. "3 events at this size" */
  eventCountAtSize: number;
  onClose(): void;
  onDone(result: {
    targetEntityId: string;
    targetBrand: string;
    targetName: string;
    eventsMoved: number;
    claimsMoved: number;
  }): void;
}

type Mode = "existing" | "new";

/**
 * Modal that walks the admin through extracting all events at a single
 * size signature off the source entity onto a target. Two modes:
 *
 * - existing: search /api/admin/search-entities and pick a known entity.
 *   Source entity is excluded from results so you can't pick it back.
 * - new: form for brand + canonical_name + category. We create the entity
 *   inline as part of the reassign call.
 *
 * On success, `onDone` is called with the target ID + counts so the parent
 * client can mark the size chip as moved without reflowing the page.
 */
export default function ExtractEventsModal({
  sourceEntity,
  sizeSignature,
  sizeBefore,
  sizeAfter,
  sizeUnit,
  eventCountAtSize,
  onClose,
  onDone,
}: Props) {
  const [mode, setMode] = useState<Mode>("existing");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  // existing-entity mode state
  const [q, setQ] = useState(`${sourceEntity.brand} ${sourceEntity.canonical_name}`);
  const [rows, setRows] = useState<EntityRow[]>([]);
  const [loading, setLoading] = useState(false);

  // new-entity mode state
  const [newBrand, setNewBrand] = useState(sourceEntity.brand);
  const [newName, setNewName] = useState("");
  const [newCategory, setNewCategory] = useState("");

  useEffect(() => {
    if (mode !== "existing") return;
    const handle = setTimeout(async () => {
      if (q.trim().length < 2) { setRows([]); return; }
      setLoading(true);
      try {
        const r = await fetch(`/api/admin/search-entities?q=${encodeURIComponent(q.trim())}`);
        const j = await r.json();
        const ranked = ((j.rows || []) as EntityRow[])
          .filter((x) => x.id !== sourceEntity.id)
          .sort((a, b) => {
            const aMatch = a.event_sizes.includes(sizeSignature) ? 1 : 0;
            const bMatch = b.event_sizes.includes(sizeSignature) ? 1 : 0;
            if (aMatch !== bMatch) return bMatch - aMatch;
            return b.event_count - a.event_count;
          });
        setRows(ranked);
      } finally {
        setLoading(false);
      }
    }, 200);
    return () => clearTimeout(handle);
  }, [q, mode, sourceEntity.id, sizeSignature]);

  async function submitExisting(target: EntityRow) {
    await submit({
      targetEntityId: target.id,
      targetBrand: target.brand,
      targetName: target.canonical_name,
    });
  }

  async function submitNew() {
    const brand = newBrand.trim();
    const name = newName.trim();
    if (!brand || !name) {
      setError("brand and name are required");
      return;
    }
    await submit({
      newEntity: { brand, name, category: newCategory.trim() || null },
      targetBrand: brand,
      targetName: name,
    });
  }

  async function submit(spec: {
    targetEntityId?: string;
    newEntity?: { brand: string; name: string; category: string | null };
    targetBrand: string;
    targetName: string;
  }) {
    setError(null);
    setPending(true);
    try {
      const body: Record<string, unknown> = {
        sourceEntityId: sourceEntity.id,
        sizeBefore,
        sizeAfter,
        sizeUnit,
      };
      if (spec.targetEntityId) {
        body.targetEntityId = spec.targetEntityId;
      } else if (spec.newEntity) {
        body.newEntityBrand = spec.newEntity.brand;
        body.newEntityName = spec.newEntity.name;
        if (spec.newEntity.category) body.newEntityCategory = spec.newEntity.category;
      }
      const r = await fetch("/api/admin/reassign-events-by-size", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!r.ok) {
        const det = await r.json().catch(() => ({ error: r.statusText }));
        throw new Error(det.error || "reassign failed");
      }
      const data = (await r.json()) as {
        targetEntityId: string;
        eventsMoved: number;
        claimsMoved: number;
      };
      onDone({
        targetEntityId: data.targetEntityId,
        targetBrand: spec.targetBrand,
        targetName: spec.targetName,
        eventsMoved: data.eventsMoved,
        claimsMoved: data.claimsMoved,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "reassign failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-6 z-50" onClick={onClose}>
      <div
        className="bg-[var(--bg-secondary)] border border-[var(--bg-tertiary)] rounded-lg p-6 w-full max-w-2xl space-y-3"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="space-y-1">
          <div className="text-sm text-[var(--text-tertiary)] font-mono uppercase tracking-wide">
            Extract events at one size onto a different entity
          </div>
          <h3 className="text-base font-medium">
            Move {eventCountAtSize} event{eventCountAtSize === 1 ? "" : "s"} at{" "}
            <span className="font-mono text-[var(--green-base)]">{sizeSignature}</span>
            {" "}off{" "}
            <span className="font-mono">{sourceEntity.brand} | {sourceEntity.canonical_name}</span>
          </h3>
        </header>

        <div className="flex gap-1 border-b border-[var(--bg-tertiary)]">
          <button
            type="button"
            onClick={() => setMode("existing")}
            className={
              "px-3 py-1.5 text-xs font-mono uppercase tracking-wide border-b-2 " +
              (mode === "existing"
                ? "border-[var(--green-base)] text-[var(--text-primary)]"
                : "border-transparent text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]")
            }
          >
            Pick existing entity
          </button>
          <button
            type="button"
            onClick={() => setMode("new")}
            className={
              "px-3 py-1.5 text-xs font-mono uppercase tracking-wide border-b-2 " +
              (mode === "new"
                ? "border-[var(--green-base)] text-[var(--text-primary)]"
                : "border-transparent text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]")
            }
          >
            Create new entity
          </button>
        </div>

        {mode === "existing" ? (
          <>
            <input
              autoFocus
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="search by brand or name"
              className="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded text-sm"
            />
            <div className="max-h-72 overflow-y-auto border border-[var(--bg-tertiary)] rounded">
              {loading && <div className="p-3 text-sm text-[var(--text-tertiary)]">searching…</div>}
              {!loading && rows.length === 0 && (
                <div className="p-3 text-sm text-[var(--text-tertiary)]">No matches</div>
              )}
              {rows.map((r) => {
                const isSizeMatch = r.event_sizes.includes(sizeSignature);
                return (
                  <button
                    key={r.id}
                    type="button"
                    disabled={pending}
                    onClick={() => submitExisting(r)}
                    className="w-full text-left px-3 py-2 border-b border-[var(--bg-tertiary)] hover:bg-[var(--bg-tertiary)] last:border-b-0 disabled:opacity-50"
                  >
                    <div className="flex items-baseline justify-between gap-3">
                      <div className="min-w-0 flex-1">
                        <div className="text-sm truncate flex items-center gap-2">
                          <span className="font-medium">{r.brand}</span>
                          <span className="text-[var(--text-tertiary)]">·</span>
                          <span>{r.canonical_name}</span>
                          {isSizeMatch && (
                            <span className="px-1.5 py-0.5 text-[10px] rounded bg-[var(--green-bg)] text-[var(--green-base)] border border-[var(--green-border)] font-mono">
                              ✓ already at this size
                            </span>
                          )}
                        </div>
                        {r.event_sizes.length > 0 && (
                          <div className="text-xs text-[var(--text-tertiary)] mt-0.5 truncate">
                            events at:{" "}
                            {r.event_sizes.slice(0, 4).map((s, i) => (
                              <span
                                key={s}
                                className={`font-mono ${s === sizeSignature ? "text-[var(--green-base)]" : ""}`}
                              >
                                {i > 0 ? ", " : ""}{s}
                              </span>
                            ))}
                            {r.event_sizes.length > 4 && (
                              <span className="text-[var(--text-tertiary)]"> +{r.event_sizes.length - 4} more</span>
                            )}
                          </div>
                        )}
                      </div>
                      <span className="font-mono text-xs text-[var(--green-base)] flex-shrink-0">
                        {r.event_count} {r.event_count === 1 ? "event" : "events"}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </>
        ) : (
          <div className="space-y-3">
            <div className="text-xs text-[var(--text-tertiary)]">
              Creates a new <code>product_entities</code> row and moves the events onto it.
              The new entity starts with the moved events; no claims at other sizes follow.
            </div>
            <label className="block">
              <span className="text-xs font-mono uppercase tracking-wide text-[var(--text-tertiary)]">Brand</span>
              <input
                type="text"
                value={newBrand}
                onChange={(e) => setNewBrand(e.target.value)}
                className="mt-1 w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded text-sm"
              />
            </label>
            <label className="block">
              <span className="text-xs font-mono uppercase tracking-wide text-[var(--text-tertiary)]">Canonical name</span>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g. Gatorade Sports Drink (small bottle)"
                className="mt-1 w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded text-sm"
              />
            </label>
            <label className="block">
              <span className="text-xs font-mono uppercase tracking-wide text-[var(--text-tertiary)]">Category (optional)</span>
              <input
                type="text"
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                placeholder="e.g. beverages"
                className="mt-1 w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded text-sm"
              />
            </label>
            <button
              type="button"
              onClick={submitNew}
              disabled={pending || !newBrand.trim() || !newName.trim()}
              className="px-4 py-2 bg-[var(--green-bg)] text-[var(--green-base)] border border-[var(--green-border)] rounded text-sm font-mono uppercase tracking-wide disabled:opacity-40"
            >
              {pending ? "moving…" : `Create + Move ${eventCountAtSize} event${eventCountAtSize === 1 ? "" : "s"} →`}
            </button>
          </div>
        )}

        {error && (
          <div className="text-xs text-[var(--red-base)] font-mono break-words border border-[var(--red-base)] rounded px-2 py-1">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            disabled={pending}
            className="px-3 py-1.5 text-sm text-[var(--text-tertiary)] hover:text-[var(--text-primary)]"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
