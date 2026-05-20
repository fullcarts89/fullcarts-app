"use client";

import { useState } from "react";
import type { ClaimGroup, PendingClaim } from "./lib";
import { ClaimImage } from "@/components/admin/ClaimImage";

// Renders one expandable card per group. Selection (the per-group
// "Select" checkbox the bulk toolbar listens to) is managed by the
// parent GroupsClient (Task 5); this component just exposes the
// expand toggle and per-group action buttons.

interface Props {
  group: ClaimGroup;
  selected: boolean;
  onSelectChange: (next: boolean) => void;
  onAction: (
    action: "approve_all" | "discard_all" | "merge_into" | "edit_then_approve",
    group: ClaimGroup,
  ) => void;
  busy: boolean;
}

function ClaimRow({ c }: { c: PendingClaim }) {
  return (
    <div className="flex gap-3 py-2 border-t border-[var(--bg-tertiary)] text-sm">
      <div className="relative w-16 h-16 bg-[var(--bg-primary)] flex-shrink-0 rounded overflow-hidden">
        {c.image_storage_path ? (
          <ClaimImage src="" storagePath={c.image_storage_path} alt={c.product_name || ""} />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-[var(--text-tertiary)] text-xs">
            —
          </div>
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-medium truncate">{c.raw_payload_title || c.product_name || "(no title)"}</div>
        <div className="text-xs text-[var(--text-tertiary)] flex gap-2 mt-0.5">
          <span>{c.source_type || "?"}</span>
          <span>·</span>
          <span>conf {(c.confidence_overall * 100).toFixed(0)}%</span>
          {c.matched_entity_id && (
            <>
              <span>·</span>
              <span className="font-mono">→ {c.matched_entity_id.slice(0, 8)}</span>
            </>
          )}
        </div>
        {c.raw_item_url && (
          <a
            href={c.raw_item_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-[var(--blue-base)] hover:underline"
          >
            source ↗
          </a>
        )}
      </div>
    </div>
  );
}

export default function GroupCardClient({ group, selected, onSelectChange, onAction, busy }: Props) {
  const [expanded, setExpanded] = useState(false);
  const rep = group.claims[0];

  return (
    <article className="border border-[var(--bg-tertiary)] rounded-lg bg-[var(--bg-secondary)]">
      <header className="flex items-center gap-3 px-4 py-3 border-b border-[var(--bg-tertiary)]">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={selected}
            onChange={(e) => onSelectChange(e.target.checked)}
            className="w-4 h-4"
          />
        </label>
        <span className="font-mono text-xs text-[var(--text-tertiary)]">{group.count}×</span>
        <span className="font-medium">{group.brand_display}</span>
        <span className="text-[var(--text-secondary)]">·</span>
        <span className="text-[var(--text-secondary)] truncate">{group.name_display}</span>
        <span className="text-[var(--text-secondary)]">·</span>
        <span className="font-mono text-sm text-[var(--red-text)]">{group.size_change}</span>
        <span className="ml-auto text-xs text-[var(--text-tertiary)]">
          conf {(group.confidence_range[0] * 100).toFixed(0)}–{(group.confidence_range[1] * 100).toFixed(0)}%
          {" · "}
          {Object.entries(group.source_breakdown).map(([k, v]) => `${k}=${v}`).join(", ")}
        </span>
      </header>

      <div className="p-4">
        {rep && <ClaimRow c={rep} />}
        {group.count > 1 && (
          <button
            type="button"
            onClick={() => setExpanded((x) => !x)}
            className="mt-2 text-sm text-[var(--blue-base)] hover:underline"
          >
            {expanded ? "Hide" : `Show all ${group.count}`}
          </button>
        )}
        {expanded && (
          <div className="mt-2">
            {group.claims.slice(1).map((c) => (
              <ClaimRow key={c.id} c={c} />
            ))}
          </div>
        )}
      </div>

      <footer className="flex gap-2 px-4 py-3 border-t border-[var(--bg-tertiary)] flex-wrap">
        <button
          type="button"
          disabled={busy}
          onClick={() => onAction("approve_all", group)}
          className="px-3 py-1.5 text-sm rounded border border-[var(--green-border)] bg-[var(--green-bg)] text-[var(--green-base)] hover:opacity-80 disabled:opacity-50"
        >
          Approve all {group.count}
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => onAction("discard_all", group)}
          className="px-3 py-1.5 text-sm rounded border border-[var(--red-border)] bg-[var(--red-bg)] text-[var(--red-text)] hover:opacity-80 disabled:opacity-50"
        >
          Discard all
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => onAction("merge_into", group)}
          className="px-3 py-1.5 text-sm rounded border border-[var(--blue-border)] bg-[var(--blue-bg)] text-[var(--blue-base)] hover:opacity-80 disabled:opacity-50"
        >
          Merge into entity →
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => onAction("edit_then_approve", group)}
          className="px-3 py-1.5 text-sm rounded border border-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] disabled:opacity-50"
        >
          Edit then approve…
        </button>
      </footer>
    </article>
  );
}
