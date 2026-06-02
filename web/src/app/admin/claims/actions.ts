"use server";

import { createAdminClient } from "@/lib/supabase/admin";

// Find-or-create the canonical entity for a claim and link it via
// matched_entity_id. Returns the entity id. Needed because the prod-only
// CHECK constraint `claims_status_requires_match` forbids status='evidence'
// and status='matched' when matched_entity_id is NULL (migration 066 intended
// to allow NULL for evidence, but the live constraint disagrees — see
// web/src/app/api/admin/bulk-evidence-claims/route.ts). Mirrors the bulk
// route's find-or-create by case-insensitive (brand, canonical_name).
async function ensureClaimMatchedEntity(
  supabase: ReturnType<typeof createAdminClient>,
  claimId: string,
): Promise<string> {
  const { data: claim, error: claimErr } = await supabase
    .from("claims")
    .select("brand, product_name, category, matched_entity_id")
    .eq("id", claimId)
    .maybeSingle();
  if (claimErr) {
    throw new Error(`Failed to load claim: ${claimErr.message}`);
  }
  if (!claim) {
    throw new Error("Claim not found");
  }

  // Respect an entity the pipeline already linked.
  if (claim.matched_entity_id) {
    return claim.matched_entity_id as string;
  }

  const brand = typeof claim.brand === "string" ? claim.brand.trim() : "";
  const productName =
    typeof claim.product_name === "string" ? claim.product_name.trim() : "";
  if (!brand || !productName) {
    throw new Error(
      "Cannot resolve claim: it has no brand or product name to link an entity. Use Edit to fill them in first.",
    );
  }

  // Case-insensitive find by (brand, canonical_name).
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

  const { error: linkErr } = await supabase
    .from("claims")
    .update({ matched_entity_id: entityId })
    .eq("id", claimId);
  if (linkErr) {
    throw new Error(`Failed to link entity: ${linkErr.message}`);
  }

  return entityId;
}

export async function updateClaimStatus(
  claimId: string,
  newStatus: string,
  evidenceTags?: string[],
) {
  const supabase = createAdminClient();

  // Tagging a still-unmatched pending claim for the evidence wall would
  // violate `claims_status_requires_match`, so give it an entity first.
  if (newStatus === "evidence") {
    await ensureClaimMatchedEntity(supabase, claimId);
  }

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

  // The claims_status_requires_match CHECK forbids status='matched' with a
  // NULL matched_entity_id, so the single-card Approve can't just flip status.
  // Find-or-create + link the entity first, then flip.
  const entityId = await ensureClaimMatchedEntity(supabase, claimId);

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
