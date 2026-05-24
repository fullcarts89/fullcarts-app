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

export async function approveClaim(claimId: string) {
  const supabase = createAdminClient();

  // The claims_match_required CHECK (migration 066) forbids status='matched'
  // with a NULL matched_entity_id, so the single-card Approve can't just flip
  // status. Point the claim at an entity in the same update: find-or-create by
  // case-insensitive (brand, canonical_name), mirroring the bulk-approve route
  // (Branch B) and pipeline/scripts/promote_claims.py.
  const { data: claim, error: claimErr } = await supabase
    .from("claims")
    .select("brand, product_name, category")
    .eq("id", claimId)
    .maybeSingle();
  if (claimErr) {
    throw new Error(`Failed to load claim: ${claimErr.message}`);
  }
  if (!claim) {
    throw new Error("Claim not found");
  }

  const brand = typeof claim.brand === "string" ? claim.brand.trim() : "";
  const productName =
    typeof claim.product_name === "string" ? claim.product_name.trim() : "";
  if (!brand || !productName) {
    throw new Error(
      "Cannot approve: claim has no brand or product name. Use Edit to fill them in first.",
    );
  }

  // Case-insensitive find by (brand, canonical_name). ilike with a no-wildcard
  // pattern is the simplest equivalent to LOWER(?)=LOWER(?).
  const { data: existing, error: findErr } = await supabase
    .from("product_entities")
    .select("id")
    .ilike("brand", brand)
    .ilike("canonical_name", productName)
    .eq("is_retracted", false)
    .limit(1);
  if (findErr) {
    throw new Error(`Failed to find entity: ${findErr.message}`);
  }

  let entityId: string;
  if (existing && existing.length > 0) {
    entityId = existing[0].id as string;
  } else {
    const insertRow: Record<string, unknown> = {
      brand,
      canonical_name: productName,
    };
    if (typeof claim.category === "string" && claim.category) {
      insertRow.category = claim.category;
    }
    const { data: created, error: createErr } = await supabase
      .from("product_entities")
      .insert(insertRow)
      .select("id")
      .single();
    if (createErr) {
      throw new Error(`Failed to create entity: ${createErr.message}`);
    }
    entityId = created.id as string;
  }

  const { error: updErr } = await supabase
    .from("claims")
    .update({ status: "matched", matched_entity_id: entityId })
    .eq("id", claimId);
  if (updErr) {
    throw new Error(`Failed to approve claim: ${updErr.message}`);
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
