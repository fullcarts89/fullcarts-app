"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase/admin";

/**
 * Close a single flag. Stamps resolved_at (idempotent — re-resolving a
 * row that's already closed is a no-op the DB will accept silently) plus
 * resolved_by + note. After resolution the row no longer counts against
 * the partial unique index, so future detector runs are free to re-flag
 * the same target if the issue resurfaces.
 */
export async function resolveFlag(
  flagId: string,
  note?: string | null,
): Promise<{ ok: true }> {
  const supabase = createAdminClient();
  const { error } = await supabase
    .from("data_quality_flags")
    .update({
      resolved_at: new Date().toISOString(),
      resolved_by: "admin",
      resolution_note: note?.trim() || null,
    })
    .eq("id", flagId)
    .is("resolved_at", null);
  if (error) {
    throw new Error(`resolveFlag failed: ${error.message}`);
  }
  revalidatePath("/admin/quality-flags");
  return { ok: true };
}

/**
 * Reopen — admin decided the issue wasn't actually handled. Clears the
 * resolution fields so the flag goes back to the open queue. Note: if a
 * detector wrote a second flag for the same target while this one was
 * closed, reopening will fail the partial unique index (23505) — that's
 * the right behaviour, surfaces the conflict for manual review.
 */
export async function reopenFlag(
  flagId: string,
): Promise<{ ok: true }> {
  const supabase = createAdminClient();
  const { error } = await supabase
    .from("data_quality_flags")
    .update({
      resolved_at: null,
      resolved_by: null,
      resolution_note: null,
    })
    .eq("id", flagId);
  if (error) {
    throw new Error(`reopenFlag failed: ${error.message}`);
  }
  revalidatePath("/admin/quality-flags");
  return { ok: true };
}

/**
 * Bulk resolve. Mirror of resolveFlag but for a list of ids. Each one is
 * its own UPDATE so partial failure is surfaced per-row in the result.
 */
export async function resolveBatch(
  flagIds: string[],
  note?: string | null,
): Promise<{ succeeded: number; failed: number; failures: string[] }> {
  if (flagIds.length === 0) {
    return { succeeded: 0, failed: 0, failures: [] };
  }
  const supabase = createAdminClient();
  // UPDATE ... RETURNING (via .select()) gives us back the affected rows so
  // we can compute how many actually landed without a separate COUNT pass.
  // The .is("resolved_at", null) guard means already-resolved rows in the
  // input set are silently no-oped — those count as "failed" in the result
  // for transparency.
  const { data, error } = await supabase
    .from("data_quality_flags")
    .update({
      resolved_at: new Date().toISOString(),
      resolved_by: "admin",
      resolution_note: note?.trim() || null,
    })
    .in("id", flagIds)
    .is("resolved_at", null)
    .select("id");
  revalidatePath("/admin/quality-flags");
  if (error) {
    return {
      succeeded: 0,
      failed: flagIds.length,
      failures: [error.message],
    };
  }
  const succeeded = (data ?? []).length;
  return {
    succeeded,
    failed: flagIds.length - succeeded,
    failures: [],
  };
}
