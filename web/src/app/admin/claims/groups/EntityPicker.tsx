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
  brand: string;
  nameHint: string;
  groupSizeChange: string;
  onCancel: () => void;
  onPick: (entity: { id: string; brand: string; canonical_name: string }) => void;
}

export default function EntityPicker({ brand, nameHint, groupSizeChange, onCancel, onPick }: Props) {
  const initialQuery = brand === "(no brand)" ? nameHint : `${brand} ${nameHint}`;
  const [q, setQ] = useState(initialQuery);
  const [rows, setRows] = useState<EntityRow[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const handle = setTimeout(async () => {
      if (q.trim().length < 2) {
        setRows([]);
        return;
      }
      setLoading(true);
      try {
        const r = await fetch(`/api/admin/search-entities?q=${encodeURIComponent(q.trim())}`);
        const j = await r.json();
        const ranked = (j.rows || []).slice().sort((a: EntityRow, b: EntityRow) => {
          const aMatch = a.event_sizes.includes(groupSizeChange) ? 1 : 0;
          const bMatch = b.event_sizes.includes(groupSizeChange) ? 1 : 0;
          if (aMatch !== bMatch) return bMatch - aMatch;
          return b.event_count - a.event_count;
        });
        setRows(ranked);
      } finally {
        setLoading(false);
      }
    }, 200);
    return () => clearTimeout(handle);
  }, [q, groupSizeChange]);

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-6 z-50">
      <div className="bg-[var(--bg-secondary)] border border-[var(--bg-tertiary)] rounded-lg p-6 w-full max-w-2xl space-y-3">
        <header className="flex items-baseline gap-3">
          <h3 className="font-medium">Merge claims into entity</h3>
          <span className="text-xs text-[var(--text-tertiary)]">type to search by brand or name</span>
        </header>
        <input
          autoFocus
          type="text"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded"
        />
        <div className="max-h-80 overflow-y-auto border border-[var(--bg-tertiary)] rounded">
          {loading && <div className="p-3 text-sm text-[var(--text-tertiary)]">searching…</div>}
          {!loading && rows.length === 0 && <div className="p-3 text-sm text-[var(--text-tertiary)]">No matches</div>}
          {rows.map((r) => {
            const isSizeMatch = r.event_sizes.includes(groupSizeChange);
            return (
              <div
                key={r.id}
                className="flex items-baseline border-b border-[var(--bg-tertiary)] hover:bg-[var(--bg-tertiary)]"
              >
                <button
                  type="button"
                  onClick={() =>
                    onPick({ id: r.id, brand: r.brand, canonical_name: r.canonical_name })
                  }
                  className="flex-1 min-w-0 text-left px-3 py-2"
                >
                  <div className="flex items-baseline justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-medium truncate flex items-center gap-2">
                        {r.brand} <span className="text-[var(--text-secondary)]">·</span> {r.canonical_name}
                        {isSizeMatch && (
                          <span className="px-1.5 py-0.5 text-xs rounded bg-[var(--green-bg)] text-[var(--green-base)] border border-[var(--green-border)] font-mono">
                            ✓ size match
                          </span>
                        )}
                      </div>
                      {r.category && <div className="text-xs text-[var(--text-tertiary)]">{r.category}</div>}
                      {r.event_sizes.length > 0 && (
                        <div className="text-xs text-[var(--text-tertiary)] mt-0.5 truncate">
                          events at:{" "}
                          {r.event_sizes.slice(0, 4).map((s, i) => (
                            <span
                              key={s}
                              className={`font-mono ${s === groupSizeChange ? "text-[var(--green-base)]" : ""}`}
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
                <a
                  href={`/products/${r.id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="px-3 py-2 text-xs text-[var(--blue-base)] hover:underline flex-shrink-0"
                >
                  ↗ view
                </a>
              </div>
            );
          })}
        </div>
        <div className="flex justify-end gap-2">
          <button type="button" onClick={onCancel} className="px-3 py-1.5 text-sm">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
