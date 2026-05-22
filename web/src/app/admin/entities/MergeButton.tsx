"use client";

import { useEffect, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { mergeEntities } from "./actions";

interface EntityRow {
  id: string;
  brand: string;
  canonical_name: string;
  category: string | null;
  event_count: number;
  event_sizes: string[];
}

const UUID_RE = /^[0-9a-f-]{36}$/i;

/**
 * Phase 2D step 4 — merge entity B (this row) INTO entity A. The button
 * expands into a debounced search picker keyed by /api/admin/search-entities;
 * typing "Mars" surfaces matching entities ranked by event count so the
 * admin can pick the target by brand or canonical name instead of copying
 * UUIDs. A direct UUID paste still works as a fallback.
 *
 * Defensive UX:
 *  - Two-step (button -> picker -> Confirm) so a stray click can't fire.
 *  - Source id renders in the prompt so the admin can sanity-check direction.
 *  - Source entity is excluded from search results so you can't merge
 *    something into itself.
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
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<EntityRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [target, setTarget] = useState<{ id: string; label: string } | null>(null);
  const [isPending, startTransition] = useTransition();
  const [resultMsg, setResultMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Debounced search. Bail out if the input is a pasted UUID (we pre-fill
  // target directly in that case) or under 2 chars.
  useEffect(() => {
    if (!open) return;
    const q = query.trim();
    if (UUID_RE.test(q)) {
      // Direct paste path — accept the UUID as target without searching.
      if (q !== sourceId) {
        setTarget({ id: q, label: q });
        setResults([]);
      } else {
        setError("target must differ from source");
        setTarget(null);
      }
      return;
    }
    if (q.length < 2) {
      setResults([]);
      return;
    }
    const handle = setTimeout(async () => {
      setLoading(true);
      try {
        const r = await fetch(`/api/admin/search-entities?q=${encodeURIComponent(q)}`);
        const j = await r.json();
        const rows = ((j.rows || []) as EntityRow[]).filter((x) => x.id !== sourceId);
        setResults(rows);
      } finally {
        setLoading(false);
      }
    }, 200);
    return () => clearTimeout(handle);
  }, [query, open, sourceId]);

  function submit() {
    setError(null);
    setResultMsg(null);
    if (!target) {
      setError("pick a target entity");
      return;
    }
    if (target.id === sourceId) {
      setError("target must differ from source");
      return;
    }
    startTransition(async () => {
      try {
        const out = await mergeEntities(sourceId, target.id);
        setResultMsg(
          `Merged. ${out.claimsMoved} claims, ${out.eventsMoved} events, ${out.variantsMoved} variants moved.`,
        );
        setOpen(false);
        setTarget(null);
        setQuery("");
        router.refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "merge failed");
      }
    });
  }

  function cancel() {
    setOpen(false);
    setQuery("");
    setTarget(null);
    setResults([]);
    setError(null);
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
        {resultMsg && (
          <div className="mt-1 text-xs text-[var(--green-base)] font-mono">{resultMsg}</div>
        )}
      </>
    );
  }

  return (
    <div className="flex flex-col items-end gap-1 min-w-[24rem] max-w-[32rem]">
      <div className="text-xs text-[var(--text-tertiary)] font-mono break-all">
        merging FROM: {sourceLabel}
      </div>
      <div className="text-xs text-[var(--text-tertiary)] font-mono break-all">
        source id: {sourceId}
      </div>
      <input
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          // Typing replaces any earlier pick unless it's a direct UUID paste.
          if (!UUID_RE.test(e.target.value.trim())) setTarget(null);
        }}
        placeholder="search by brand or name, or paste a target UUID"
        disabled={isPending}
        autoFocus
        className="w-full px-2 py-1 text-xs font-mono bg-[var(--bg-primary)] border border-[var(--amber-base)] rounded focus:outline-none"
      />

      {/* Selected-target preview — confirms the pick before they hit Confirm. */}
      {target && (
        <div className="w-full text-xs font-mono text-[var(--green-base)] border border-[var(--green-border)] bg-[var(--green-bg)] rounded px-2 py-1">
          → target: {target.label}
        </div>
      )}

      {/* Search results dropdown. Hidden when a UUID-paste already picked. */}
      {!target && results.length > 0 && (
        <div className="w-full max-h-64 overflow-y-auto border border-[var(--bg-tertiary)] rounded bg-[var(--bg-primary)]">
          {results.map((r) => (
            <button
              key={r.id}
              type="button"
              onClick={() =>
                setTarget({ id: r.id, label: `${r.brand} | ${r.canonical_name}` })
              }
              className="w-full text-left px-2 py-1 text-xs hover:bg-[var(--bg-tertiary)] border-b border-[var(--bg-tertiary)] last:border-b-0"
            >
              <div className="flex items-baseline justify-between gap-2">
                <div className="min-w-0 flex-1 truncate">
                  <span className="font-medium">{r.brand}</span>
                  <span className="text-[var(--text-tertiary)]"> · </span>
                  <span>{r.canonical_name}</span>
                </div>
                <span className="font-mono text-[10px] text-[var(--green-base)] flex-shrink-0">
                  {r.event_count} {r.event_count === 1 ? "event" : "events"}
                </span>
              </div>
              {r.category && (
                <div className="text-[10px] text-[var(--text-tertiary)] mt-0.5">{r.category}</div>
              )}
            </button>
          ))}
        </div>
      )}

      {!target && !loading && query.trim().length >= 2 && results.length === 0 && (
        <div className="text-xs text-[var(--text-tertiary)] font-mono">no matches</div>
      )}
      {loading && (
        <div className="text-xs text-[var(--text-tertiary)] font-mono">searching…</div>
      )}

      {error && <div className="text-xs text-[var(--red-base)] font-mono">{error}</div>}
      <div className="flex gap-2">
        <button
          type="button"
          onClick={submit}
          disabled={isPending || !target}
          className="px-2 py-1 text-xs rounded border border-[var(--amber-base)] bg-[var(--amber-bg)] text-[var(--amber-base)] hover:brightness-125 disabled:opacity-50"
        >
          {isPending ? "merging…" : "Confirm merge"}
        </button>
        <button
          type="button"
          onClick={cancel}
          disabled={isPending}
          className="px-2 py-1 text-xs rounded border border-[var(--bg-tertiary)] text-[var(--text-secondary)]"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
