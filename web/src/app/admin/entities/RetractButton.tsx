"use client";

import { useState, useTransition } from "react";
import { setEntityRetracted } from "./actions";

export function RetractButton({
  entityId,
  isRetracted,
  entityLabel,
  eventCount,
}: {
  entityId: string;
  isRetracted: boolean;
  entityLabel: string;
  eventCount: number;
}) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  const handleClick = () => {
    const verb = isRetracted ? "restore" : "retract";
    const eventNote = !isRetracted && eventCount > 0
      ? `\n\nThis will also retract ${eventCount} published event${eventCount === 1 ? "" : "s"} tied to this entity.`
      : "";
    if (!confirm(`${verb.charAt(0).toUpperCase() + verb.slice(1)} "${entityLabel}"?${eventNote}`)) return;

    setError(null);
    startTransition(async () => {
      try {
        await setEntityRetracted(entityId, !isRetracted);
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      }
    });
  };

  const base =
    "px-2.5 py-1 text-xs font-mono rounded border transition-colors disabled:opacity-50";
  const styled = isRetracted
    ? "bg-[var(--green-bg)] text-[var(--green-base)] border-[var(--green-border)] hover:brightness-110"
    : "bg-[var(--red-bg)] text-[var(--red-base)] border-[var(--red-border)] hover:brightness-110";

  return (
    <div className="flex flex-col items-end gap-1">
      <button
        type="button"
        onClick={handleClick}
        disabled={isPending}
        className={`${base} ${styled}`}
      >
        {isPending ? "..." : isRetracted ? "Restore" : "Retract"}
      </button>
      {error && (
        <span className="text-xs text-[var(--red-base)] font-mono max-w-[12rem] text-right">
          {error}
        </span>
      )}
    </div>
  );
}
