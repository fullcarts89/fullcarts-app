// Row shape of `data_quality_flags` (migration 063). One of claim_id /
// entity_id / event_id is non-null per the table-level CHECK constraint.

export interface FlagRow {
  id: string;
  claim_id: string | null;
  entity_id: string | null;
  event_id: string | null;
  flag_kind: string;
  severity: "low" | "med" | "high";
  detail: Record<string, unknown>;
  detected_by: string;
  detected_at: string;
  resolved_at: string | null;
  resolved_by: string | null;
  resolution_note: string | null;
}

// Static metadata about each flag_kind the pipeline writes. Used to
// render readable labels + colours without scattering switch statements.
// Add to this when new detectors ship.
export const FLAG_KIND_META: Record<
  string,
  { label: string; explainer: string; tone: "amber" | "purple" | "red" | "blue" }
> = {
  short_brand: {
    label: "Short / placeholder brand",
    explainer:
      "AI extraction returned a brand string under 2 chars or in the placeholder set ('Unknown', 'Various', 'Poor', etc.). Likely a bad entity that should be retracted or merged into the real brand.",
    tone: "amber",
  },
  stuck_approved_claim: {
    label: "Stuck unresolved claim",
    explainer:
      "Claim has been in status='matched' with matched_entity_id NULL for > 7 days — promote_claims has had multiple chances to resolve and still can't.",
    tone: "purple",
  },
  fuzzy_brand_collision: {
    label: "Duplicate entity",
    explainer:
      "Two or more entities share the same brand and a normalised canonical_name. Use /admin/duplicates to batch-merge.",
    tone: "blue",
  },
  size_outlier: {
    label: "Size outlier event",
    explainer:
      "An event with a size_after/size_before ratio outside [0.5, 2.0] — well past normal shrinkflation magnitude. Often an AI unit-parse error.",
    tone: "red",
  },
  sku_mashup: {
    label: "SKU mash-up",
    explainer:
      "Entity has events whose size_before values span more than 3×. Probably multiple SKUs collapsed into one entity (a 200g pack and a 500g pack treated as the same product).",
    tone: "purple",
  },
  mixed_units: {
    label: "Mixed units in history",
    explainer:
      "Entity has events using more than one size_unit (g + oz, ml + L). Breaks the /products/[id] time series rendering.",
    tone: "amber",
  },
};

export const SEVERITY_META: Record<
  FlagRow["severity"],
  { label: string; tone: "amber" | "red" | "tertiary" }
> = {
  high: { label: "high", tone: "red" },
  med: { label: "med", tone: "amber" },
  low: { label: "low", tone: "tertiary" },
};
