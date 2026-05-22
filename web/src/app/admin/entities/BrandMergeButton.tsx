"use client";

import { useEffect, useState, useTransition } from "react";
import { useRouter } from "next/navigation";

interface BrandRow {
  brand: string;
  entity_count: number;
}

interface AffectedEntity {
  id: string;
  brand: string;
  canonical_name: string;
}

/**
 * Bulk rebrand: take every active entity whose brand string equals X and
 * set their brand to Y. Different from the per-entity merge⇒ button —
 * here we keep the entities (and their distinct canonical_names) but
 * change the brand attribution.
 *
 * Example: every "Celebrations | …" entity has its real-world brand owner
 * as Mars. Merging brand "Celebrations" → "Mars" rebrands them all to
 * "Mars | Celebrations Chocolate Assortment", "Mars | Celebrations bottle",
 * etc.
 *
 * Each row goes through set_entity_field server-side, so entity_edit_log
 * records every change and any single row can be reverted via the existing
 * click-to-edit on /admin/entities.
 */
export function BrandMergeButton() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="px-3 py-1.5 text-sm rounded-md border border-[var(--amber-base)] bg-[var(--amber-bg)] text-[var(--amber-base)] hover:brightness-125"
        title="Bulk-rename a brand string — affects every active entity carrying it"
      >
        Merge brand →
      </button>
      {open && <BrandMergeModal onClose={() => setOpen(false)} />}
    </>
  );
}

function BrandMergeModal({ onClose }: { onClose: () => void }) {
  const [sourceBrand, setSourceBrand] = useState<string | null>(null);
  const [targetBrand, setTargetBrand] = useState<string | null>(null);
  const [previewCount, setPreviewCount] = useState<number | null>(null);
  const [previewSample, setPreviewSample] = useState<AffectedEntity[]>([]);
  const [isPending, startTransition] = useTransition();
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Whenever both brands are chosen, run a dry-run to show what'll change.
  useEffect(() => {
    if (!sourceBrand || !targetBrand) {
      setPreviewCount(null);
      setPreviewSample([]);
      return;
    }
    if (sourceBrand === targetBrand) {
      setPreviewCount(null);
      setPreviewSample([]);
      return;
    }
    let stale = false;
    (async () => {
      try {
        const r = await fetch("/api/admin/merge-brand", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ sourceBrand, targetBrand, dryRun: true }),
        });
        const j = await r.json();
        if (stale) return;
        if (!r.ok) {
          setError(j.error || "preview failed");
          setPreviewCount(null);
          return;
        }
        setError(null);
        setPreviewCount(j.affectedCount ?? 0);
        setPreviewSample(j.affected ?? []);
      } catch (e) {
        if (!stale) setError(e instanceof Error ? e.message : "preview failed");
      }
    })();
    return () => {
      stale = true;
    };
  }, [sourceBrand, targetBrand]);

  function commit() {
    if (!sourceBrand || !targetBrand) return;
    setError(null);
    setResult(null);
    startTransition(async () => {
      try {
        const r = await fetch("/api/admin/merge-brand", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ sourceBrand, targetBrand }),
        });
        const j = await r.json();
        if (!r.ok) throw new Error(j.error || "merge failed");
        setResult(
          `Rebranded ${j.writtenCount} of ${j.affectedCount} entities from "${sourceBrand}" → "${targetBrand}".${
            (j.failed?.length ?? 0) > 0 ? ` ${j.failed.length} failed.` : ""
          }`,
        );
        router.refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "merge failed");
      }
    });
  }

  return (
    <div
      className="fixed inset-0 bg-black/70 flex items-center justify-center p-6 z-50"
      onClick={onClose}
    >
      <div
        className="bg-[var(--bg-secondary)] border border-[var(--bg-tertiary)] rounded-lg p-6 w-full max-w-2xl space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="space-y-1">
          <div className="text-sm text-[var(--text-tertiary)] font-mono uppercase tracking-wide">
            Bulk-rebrand
          </div>
          <h3 className="text-base font-medium">
            Change every entity&rsquo;s brand string from one value to another
          </h3>
          <p className="text-xs text-[var(--text-tertiary)]">
            Use this when an AI extraction tagged a sub-product as its own brand (e.g. tagged
            &ldquo;Celebrations&rdquo; as the brand when Mars is the real parent).
            Each affected entity gets a per-row entity_edit_log entry so changes are reversible.
          </p>
        </header>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs font-mono uppercase tracking-wide text-[var(--text-tertiary)] mb-1">
              Source brand
            </div>
            <BrandPicker
              placeholder="e.g. Celebrations"
              onPick={setSourceBrand}
              excludeRetracted
              minEntities={1}
            />
            {sourceBrand && (
              <div className="mt-1 text-xs font-mono text-[var(--text-primary)]">
                → {sourceBrand}
              </div>
            )}
          </div>
          <div>
            <div className="text-xs font-mono uppercase tracking-wide text-[var(--text-tertiary)] mb-1">
              Target brand
            </div>
            <BrandPicker
              placeholder="e.g. Mars"
              onPick={setTargetBrand}
              allowFreeType
            />
            {targetBrand && (
              <div className="mt-1 text-xs font-mono text-[var(--text-primary)]">
                → {targetBrand}
              </div>
            )}
          </div>
        </div>

        {sourceBrand && targetBrand && previewCount !== null && (
          <div className="border border-[var(--bg-tertiary)] rounded p-3 bg-[var(--bg-primary)] space-y-2">
            <div className="text-sm">
              <strong>{previewCount}</strong> entit{previewCount === 1 ? "y" : "ies"} will be
              rebranded from <code>{sourceBrand}</code> →{" "}
              <code className="text-[var(--green-base)]">{targetBrand}</code>
            </div>
            {previewSample.length > 0 && (
              <div className="text-xs text-[var(--text-tertiary)] font-mono max-h-32 overflow-y-auto border border-[var(--bg-tertiary)] rounded p-2">
                {previewSample.map((e) => (
                  <div key={e.id} className="truncate">
                    {e.brand} | {e.canonical_name}
                  </div>
                ))}
                {previewCount > previewSample.length && (
                  <div className="text-[var(--text-secondary)]">
                    … and {previewCount - previewSample.length} more
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {result && (
          <div className="text-sm text-[var(--green-base)] font-mono border border-[var(--green-border)] bg-[var(--green-bg)] rounded p-2">
            {result}
          </div>
        )}
        {error && (
          <div className="text-sm text-[var(--red-base)] font-mono border border-[var(--red-base)] rounded p-2">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            disabled={isPending}
            className="px-3 py-1.5 text-sm text-[var(--text-tertiary)] hover:text-[var(--text-primary)]"
          >
            {result ? "Close" : "Cancel"}
          </button>
          {!result && (
            <button
              type="button"
              onClick={commit}
              disabled={
                isPending ||
                !sourceBrand ||
                !targetBrand ||
                sourceBrand === targetBrand ||
                (previewCount ?? 0) === 0
              }
              className="px-4 py-1.5 text-sm rounded border border-[var(--amber-base)] bg-[var(--amber-bg)] text-[var(--amber-base)] hover:brightness-125 disabled:opacity-40"
            >
              {isPending
                ? "rebranding…"
                : `Rebrand ${previewCount ?? 0} entit${previewCount === 1 ? "y" : "ies"} →`}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function BrandPicker({
  placeholder,
  onPick,
  excludeRetracted,
  allowFreeType,
  minEntities,
}: {
  placeholder: string;
  onPick: (brand: string | null) => void;
  excludeRetracted?: boolean;
  allowFreeType?: boolean;
  minEntities?: number;
}) {
  void excludeRetracted; // accepted from caller for clarity; server query already filters
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<BrandRow[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const handle = setTimeout(async () => {
      setLoading(true);
      try {
        const r = await fetch(`/api/admin/distinct-brands?q=${encodeURIComponent(q.trim())}`);
        const j = await r.json();
        const filtered = ((j.rows || []) as BrandRow[]).filter(
          (b) => !minEntities || b.entity_count >= minEntities,
        );
        setRows(filtered);
      } finally {
        setLoading(false);
      }
    }, 200);
    return () => clearTimeout(handle);
  }, [q, minEntities]);

  return (
    <div className="relative">
      <input
        type="text"
        value={q}
        onChange={(e) => {
          setQ(e.target.value);
          setOpen(true);
          if (allowFreeType) onPick(e.target.value.trim() || null);
        }}
        onFocus={() => setOpen(true)}
        placeholder={placeholder}
        className="w-full px-2 py-1.5 text-sm bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded font-mono"
      />
      {open && (rows.length > 0 || loading) && (
        <div className="absolute left-0 right-0 top-full mt-1 max-h-56 overflow-y-auto border border-[var(--bg-tertiary)] rounded bg-[var(--bg-primary)] z-10">
          {loading && rows.length === 0 && (
            <div className="p-2 text-xs text-[var(--text-tertiary)]">searching…</div>
          )}
          {rows.map((r) => (
            <button
              key={r.brand}
              type="button"
              onClick={() => {
                onPick(r.brand);
                setQ(r.brand);
                setOpen(false);
              }}
              className="w-full text-left px-2 py-1 text-sm hover:bg-[var(--bg-tertiary)] border-b border-[var(--bg-tertiary)] last:border-b-0 flex items-baseline justify-between"
            >
              <span className="font-mono">{r.brand}</span>
              <span className="font-mono text-[10px] text-[var(--green-base)]">
                {r.entity_count} {r.entity_count === 1 ? "entity" : "entities"}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
