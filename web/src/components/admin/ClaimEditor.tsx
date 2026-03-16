"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { updateClaimFields } from "@/app/admin/claims/actions";

type EditableFields = {
  brand: string;
  product_name: string;
  category: string;
  old_size: string;
  old_size_unit: string;
  new_size: string;
  new_size_unit: string;
  change_description: string;
};

export function ClaimEditor({
  claimId,
  initialValues,
}: {
  claimId: string;
  initialValues: EditableFields;
}) {
  const [editing, setEditing] = useState(false);
  const [fields, setFields] = useState<EditableFields>(initialValues);
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  function handleChange(key: keyof EditableFields, value: string) {
    setFields((prev) => ({ ...prev, [key]: value }));
  }

  function handleSave() {
    startTransition(async () => {
      await updateClaimFields(claimId, {
        brand: fields.brand || null,
        product_name: fields.product_name || null,
        category: fields.category || null,
        old_size: fields.old_size ? parseFloat(fields.old_size) : null,
        old_size_unit: fields.old_size_unit || null,
        new_size: fields.new_size ? parseFloat(fields.new_size) : null,
        new_size_unit: fields.new_size_unit || null,
        change_description: fields.change_description || null,
      });
      setEditing(false);
      router.refresh();
    });
  }

  function handleCancel() {
    setFields(initialValues);
    setEditing(false);
  }

  if (!editing) {
    return (
      <button
        onClick={() => setEditing(true)}
        className="px-2 py-0.5 text-xs font-medium rounded border border-[var(--bg-tertiary)] text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] hover:border-[var(--text-tertiary)] transition-colors"
        title="Edit claim details"
      >
        Edit
      </button>
    );
  }

  return (
    <div className="space-y-2 pt-2 border-t border-[var(--bg-tertiary)]">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <Field label="Brand" value={fields.brand} onChange={(v) => handleChange("brand", v)} />
        <Field label="Product" value={fields.product_name} onChange={(v) => handleChange("product_name", v)} />
        <Field label="Category" value={fields.category} onChange={(v) => handleChange("category", v)} />
        <div className="flex gap-2">
          <Field label="Old size" value={fields.old_size} onChange={(v) => handleChange("old_size", v)} className="flex-1" />
          <Field label="Unit" value={fields.old_size_unit} onChange={(v) => handleChange("old_size_unit", v)} className="w-16" />
        </div>
        <div className="flex gap-2">
          <Field label="New size" value={fields.new_size} onChange={(v) => handleChange("new_size", v)} className="flex-1" />
          <Field label="Unit" value={fields.new_size_unit} onChange={(v) => handleChange("new_size_unit", v)} className="w-16" />
        </div>
      </div>
      <Field
        label="Description"
        value={fields.change_description}
        onChange={(v) => handleChange("change_description", v)}
        multiline
      />
      <div className="flex gap-2 pt-1">
        <button
          onClick={handleSave}
          disabled={isPending}
          className="px-3 py-1 text-xs font-medium rounded border border-[var(--green-border)] bg-[var(--green-bg)] text-[var(--green-base)] hover:brightness-125 transition-all disabled:opacity-50"
        >
          {isPending ? "Saving..." : "Save"}
        </button>
        <button
          onClick={handleCancel}
          disabled={isPending}
          className="px-3 py-1 text-xs font-medium rounded border border-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  className,
  multiline,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  className?: string;
  multiline?: boolean;
}) {
  const inputClass =
    "w-full px-2 py-1 text-sm rounded border border-[var(--bg-tertiary)] bg-[var(--bg-primary)] text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:border-[var(--text-tertiary)]";

  return (
    <div className={className}>
      <label className="block text-xs text-[var(--text-tertiary)] mb-0.5">{label}</label>
      {multiline ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={2}
          className={inputClass}
        />
      ) : (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={inputClass}
        />
      )}
    </div>
  );
}
