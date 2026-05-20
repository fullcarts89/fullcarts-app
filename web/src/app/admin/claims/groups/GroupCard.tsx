import type { ClaimGroup } from "./lib";

export default function GroupCard({ group }: { group: ClaimGroup }) {
  return (
    <article className="border border-[var(--bg-tertiary)] rounded-lg bg-[var(--bg-secondary)] p-4">
      <header className="flex items-baseline gap-3 mb-2">
        <span className="font-mono text-xs text-[var(--text-tertiary)]">
          {group.count}×
        </span>
        <span className="font-medium">{group.brand_display}</span>
        <span className="text-[var(--text-secondary)]">·</span>
        <span className="text-[var(--text-secondary)]">{group.name_display}</span>
        <span className="text-[var(--text-secondary)]">·</span>
        <span className="font-mono text-sm text-[var(--red-text)]">
          {group.size_change}
        </span>
      </header>
      <p className="text-xs text-[var(--text-tertiary)]">
        Sources:{" "}
        {Object.entries(group.source_breakdown)
          .map(([k, v]) => `${k}=${v}`)
          .join(", ")}{" "}
        · Confidence {(group.confidence_range[0] * 100).toFixed(0)}–
        {(group.confidence_range[1] * 100).toFixed(0)}%
      </p>
    </article>
  );
}
