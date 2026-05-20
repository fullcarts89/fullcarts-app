"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase/admin";

/**
 * Apply a single duplicate-merge. Thin wrapper around the existing
 * `merge_entities` RPC from migration 065 so the bulk page and the
 * per-row /admin/entities button share the same audit trail
 * (entity_merge_log).
 */
export async function mergePair(
  sourceId: string,
  targetId: string,
): Promise<{
  logId: number;
  claimsMoved: number;
  eventsMoved: number;
  variantsMoved: number;
}> {
  if (sourceId === targetId) {
    throw new Error("mergePair: source and target must differ");
  }
  const supabase = createAdminClient();
  const { data, error } = await supabase.rpc("merge_entities", {
    p_source_id: sourceId,
    p_target_id: targetId,
    p_merged_by: "duplicates_batch",
  });
  if (error) {
    throw new Error(`merge_entities failed: ${error.message}`);
  }
  const row = (
    data as Array<{
      log_id: number;
      claims_moved: number;
      events_moved: number;
      variants_moved: number;
    }>
  )[0];
  revalidatePath("/admin/duplicates");
  revalidatePath("/admin/entities");
  return {
    logId: row.log_id,
    claimsMoved: row.claims_moved,
    eventsMoved: row.events_moved,
    variantsMoved: row.variants_moved,
  };
}

/**
 * Loop apply. Returns a per-pair result list so the UI can flag any
 * individual failure without aborting the whole batch. The function
 * itself never throws — partial success is reported in the result.
 *
 * Why not transactional: each merge_entities call is already its own
 * transaction. Wrapping the loop in a SQL transaction would mean one
 * bad pair rolls back 49 good ones, which is the wrong trade-off here.
 * If a pair errors (e.g. someone retracted the source between page
 * load and confirm), the rest still land and the result tells you
 * which ones to investigate.
 */
export async function mergeBatch(
  pairs: Array<{ sourceId: string; targetId: string }>,
): Promise<{
  succeeded: number;
  failed: number;
  details: Array<{
    sourceId: string;
    targetId: string;
    ok: boolean;
    error?: string;
    counts?: { claims: number; events: number; variants: number };
  }>;
}> {
  const supabase = createAdminClient();
  const details: Array<{
    sourceId: string;
    targetId: string;
    ok: boolean;
    error?: string;
    counts?: { claims: number; events: number; variants: number };
  }> = [];
  let succeeded = 0;
  let failed = 0;

  for (const { sourceId, targetId } of pairs) {
    if (sourceId === targetId) {
      failed++;
      details.push({
        sourceId,
        targetId,
        ok: false,
        error: "source equals target",
      });
      continue;
    }
    const { data, error } = await supabase.rpc("merge_entities", {
      p_source_id: sourceId,
      p_target_id: targetId,
      p_merged_by: "duplicates_batch",
    });
    if (error) {
      failed++;
      details.push({ sourceId, targetId, ok: false, error: error.message });
      continue;
    }
    const row = (
      data as Array<{
        claims_moved: number;
        events_moved: number;
        variants_moved: number;
      }>
    )[0];
    succeeded++;
    details.push({
      sourceId,
      targetId,
      ok: true,
      counts: {
        claims: row.claims_moved,
        events: row.events_moved,
        variants: row.variants_moved,
      },
    });
  }

  revalidatePath("/admin/duplicates");
  revalidatePath("/admin/entities");
  return { succeeded, failed, details };
}
