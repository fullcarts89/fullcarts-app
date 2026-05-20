"use client";

import { useEffect, useState } from "react";

interface EntityRow {
  id: string;
  brand: string;
  canonical_name: string;
  category: string | null;
  event_count: number;
}

interface Props {
  brand: string;
  nameHint: string;
  onCancel: () => void;
  onPick: (entityId: string) => void;
}

export default function EntityPicker({ brand, nameHint, onCancel, onPick }: Props) {
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
        setRows(j.rows || []);
      } finally {
        setLoading(false);
      }
    }, 200);
    return () => clearTimeout(handle);
  }, [q]);

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
          {rows.map((r) => (
            <div
              key={r.id}
              className="flex items-baseline border-b border-[var(--bg-tertiary)] hover:bg-[var(--bg-tertiary)]"
            >
              <button
                type="button"
                onClick={() => onPick(r.id)}
                className="flex-1 min-w-0 text-left px-3 py-2"
              >
                <div className="flex items-baseline justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium truncate">
                      {r.brand} <span className="text-[var(--text-secondary)]">·</span> {r.canonical_name}
                    </div>
                    {r.category && <div className="text-xs text-[var(--text-tertiary)]">{r.category}</div>}
                  </div>
                  <span
                    className={`font-mono text-xs flex-shrink-0 ${
                      r.event_count > 0
                        ? "text-[var(--green-base)]"
                        : "text-[var(--text-tertiary)]"
                    }`}
                  >
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
          ))}
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
