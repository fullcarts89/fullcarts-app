"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { editEntityField } from "./actions";

/**
 * Phase 2D step 2 — inline edit. Single text cell that flips to an
 * editable input on click. Save dispatches `editEntityField` and revalidates.
 *
 * Escape cancels. Enter saves. Blur saves only if dirty. The "edited"
 * indicator is implicit — the table revalidates and the new value renders.
 */
export function EditableField({
  entityId,
  field,
  value,
  placeholder,
}: {
  entityId: string;
  field: "brand" | "canonical_name" | "category" | "manufacturer";
  value: string | null;
  placeholder?: string;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value ?? "");
  const [isPending, startTransition] = useTransition();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  function commit() {
    const next = draft.trim() === "" ? null : draft.trim();
    if (next === (value ?? null)) {
      setEditing(false);
      return;
    }
    setError(null);
    startTransition(async () => {
      try {
        await editEntityField(entityId, field, next);
        setEditing(false);
        router.refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "save failed");
      }
    });
  }

  function handleKey(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault();
      commit();
    } else if (e.key === "Escape") {
      e.preventDefault();
      setDraft(value ?? "");
      setEditing(false);
      setError(null);
    }
  }

  if (editing) {
    return (
      <span className="inline-flex flex-col gap-0.5">
        <input
          type="text"
          autoFocus
          disabled={isPending}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKey}
          onBlur={commit}
          placeholder={placeholder}
          className="px-2 py-0.5 text-sm bg-[var(--bg-primary)] border border-[var(--amber-base)] rounded focus:outline-none min-w-[12rem]"
        />
        {error && (
          <span className="text-xs text-[var(--red-base)] font-mono">{error}</span>
        )}
      </span>
    );
  }

  return (
    <button
      type="button"
      onClick={() => setEditing(true)}
      className="text-left hover:underline underline-offset-2 decoration-dotted decoration-[var(--text-tertiary)] cursor-text"
      title="Click to edit"
    >
      {value ?? <span className="text-[var(--text-tertiary)]">—</span>}
    </button>
  );
}
