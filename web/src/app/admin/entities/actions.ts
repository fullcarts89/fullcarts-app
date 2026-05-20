"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase/admin";

const EDITABLE_FIELDS = ["brand", "canonical_name", "category", "manufacturer"] as const;
type EditableField = (typeof EDITABLE_FIELDS)[number];

export async function setEntityRetracted(entityId: string, retracted: boolean) {
  const supabase = createAdminClient();

  const { data, error } = await supabase.rpc("set_entity_retracted", {
    p_entity_id: entityId,
    p_retracted: retracted,
  });

  if (error) {
    throw new Error(`Failed to ${retracted ? "retract" : "restore"} entity: ${error.message}`);
  }

  revalidatePath("/admin/entities");

  const eventsAffected = (data as Array<{ events_affected: number }> | null)?.[0]?.events_affected ?? 0;
  return { eventsAffected };
}

/**
 * Phase 2D step 2 — inline edit. Backed by migration 065's set_entity_field
 * RPC which couples the column update and the entity_edit_log write into a
 * single transaction.
 *
 * Returns { logId } — null when the new value matched the existing one
 * (the RPC treats that as a no-op).
 */
export async function editEntityField(
  entityId: string,
  field: string,
  value: string | null,
): Promise<{ logId: number | null }> {
  if (!(EDITABLE_FIELDS as readonly string[]).includes(field)) {
    throw new Error(`editEntityField: unsupported field "${field}"`);
  }
  const supabase = createAdminClient();
  const { data, error } = await supabase.rpc("set_entity_field", {
    p_entity_id: entityId,
    p_field: field as EditableField,
    p_value: value,
    p_edited_by: "admin",
  });
  if (error) {
    throw new Error(`editEntityField failed: ${error.message}`);
  }
  revalidatePath("/admin/entities");
  return { logId: (data as number | null) ?? null };
}

/**
 * Phase 2D step 3 — send a retracted entity's claims back to the pending
 * admin queue. After the entity has been pulled offline, this lets the
 * admin reroute its claims through human review instead of letting them
 * stay attached to a dead entity. The migration 064 trigger logs every
 * status transition automatically.
 *
 * Only allowed on retracted entities — guards against accidental
 * mass-unmatching of live data.
 */
export async function resetClaimsToPending(entityId: string): Promise<{ claimsReset: number }> {
  const supabase = createAdminClient();

  // Guard: refuse on non-retracted entities.
  const { data: entity, error: lookupErr } = await supabase
    .from("product_entities")
    .select("is_retracted")
    .eq("id", entityId)
    .single();
  if (lookupErr || !entity) {
    throw new Error(`resetClaimsToPending: entity not found (${entityId})`);
  }
  if (!entity.is_retracted) {
    throw new Error(
      "resetClaimsToPending: entity must be retracted first. Retract it, then send claims back.",
    );
  }

  // Count first so we can return how many got reset. The UPDATE's response
  // shape doesn't expose a row count when chained through supabase-js,
  // so we issue the head-count separately. Same transaction context isn't
  // critical here — the trigger from migration 064 logs every status flip
  // and the worst race (a claim added between the count and the update)
  // is one stale number.
  const { count, error: countErr } = await supabase
    .from("claims")
    .select("*", { count: "exact", head: true })
    .eq("matched_entity_id", entityId);
  if (countErr) {
    throw new Error(`resetClaimsToPending count failed: ${countErr.message}`);
  }

  const { error } = await supabase
    .from("claims")
    .update({
      status: "pending",
      matched_entity_id: null,
      matched_variant_id: null,
    })
    .eq("matched_entity_id", entityId);
  if (error) {
    throw new Error(`resetClaimsToPending failed: ${error.message}`);
  }

  revalidatePath("/admin/entities");
  revalidatePath("/admin/claims");
  return { claimsReset: count ?? 0 };
}

/**
 * Phase 2D step 4 — merge source entity into target. Backed by the
 * merge_entities RPC from migration 065. Returns the row counts moved
 * so the UI can confirm.
 */
export async function mergeEntities(
  sourceId: string,
  targetId: string,
): Promise<{ logId: number; claimsMoved: number; eventsMoved: number; variantsMoved: number }> {
  if (sourceId === targetId) {
    throw new Error("mergeEntities: source and target must differ");
  }
  const supabase = createAdminClient();
  const { data, error } = await supabase.rpc("merge_entities", {
    p_source_id: sourceId,
    p_target_id: targetId,
    p_merged_by: "admin",
  });
  if (error) {
    throw new Error(`mergeEntities failed: ${error.message}`);
  }
  const row = (data as Array<{
    log_id: number;
    claims_moved: number;
    events_moved: number;
    variants_moved: number;
  }>)[0];
  revalidatePath("/admin/entities");
  return {
    logId: row.log_id,
    claimsMoved: row.claims_moved,
    eventsMoved: row.events_moved,
    variantsMoved: row.variants_moved,
  };
}
