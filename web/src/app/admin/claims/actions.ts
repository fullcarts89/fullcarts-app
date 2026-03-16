"use server";

import { createAdminClient } from "@/lib/supabase/admin";

export async function updateClaimStatus(
  claimId: string,
  newStatus: string,
  evidenceTags?: string[],
) {
  const supabase = createAdminClient();

  const update: Record<string, unknown> = { status: newStatus };
  if (evidenceTags !== undefined) {
    update.evidence_tags = evidenceTags;
  }

  const { error } = await supabase
    .from("claims")
    .update(update)
    .eq("id", claimId);

  if (error) {
    throw new Error(`Failed to update claim: ${error.message}`);
  }
}

export async function updateClaimFields(
  claimId: string,
  fields: {
    brand?: string | null;
    product_name?: string | null;
    category?: string | null;
    old_size?: number | null;
    old_size_unit?: string | null;
    new_size?: number | null;
    new_size_unit?: string | null;
    change_description?: string | null;
  },
) {
  const supabase = createAdminClient();

  const { error } = await supabase
    .from("claims")
    .update(fields)
    .eq("id", claimId);

  if (error) {
    throw new Error(`Failed to update claim fields: ${error.message}`);
  }
}
