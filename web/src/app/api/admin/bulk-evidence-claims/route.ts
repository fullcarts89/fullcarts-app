import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// Bulk-flip a set of claims to status='evidence' with the given
// evidence_tags. Called from /admin/claims/groups GroupsClient for
// "send to evidence wall" on a group or per-claim.
//
// Prod constraint `claims_status_requires_match` (not in migration
// files — added manually) forbids status='evidence' when
// matched_entity_id is null. Migration 066 INTENDED to allow null but
// the prod constraint disagrees. We work around it by auto-deriving an
// entity for any unmatched claim before flipping status, mirroring the
// bulk-approve-claims pattern.

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  if (!(await isAdminRequest())) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const rawIds = body?.claim_ids;
  const ids = Array.isArray(rawIds)
    ? rawIds.filter((x): x is string => typeof x === "string")
    : [];
  if (ids.length === 0) {
    return NextResponse.json({ error: "claim_ids required" }, { status: 400 });
  }

  const rawTags = body?.tags;
  const tags = Array.isArray(rawTags)
    ? rawTags.filter((x): x is string => typeof x === "string" && x.length > 0)
    : [];
  if (tags.length === 0) {
    return NextResponse.json({ error: "tags required" }, { status: 400 });
  }

  const sb = createAdminClient();

  // Load current state to figure out which claims still need an entity.
  const { data: claims, error: claimsErr } = await sb
    .from("claims")
    .select("id, brand, product_name, category, matched_entity_id")
    .in("id", ids);
  if (claimsErr) {
    return NextResponse.json({ error: claimsErr.message }, { status: 500 });
  }
  if (!claims || claims.length === 0) {
    return NextResponse.json({ error: "no claims found" }, { status: 404 });
  }

  type ClaimRow = {
    id: string;
    brand: string | null;
    product_name: string | null;
    category: string | null;
    matched_entity_id: string | null;
  };
  const rows = claims as ClaimRow[];
  const needsEntity = rows.filter((c) => !c.matched_entity_id);

  let derivedEntityId: string | null = null;
  let createdEntity = false;

  if (needsEntity.length > 0) {
    const seed = needsEntity[0];
    const brand = typeof seed.brand === "string" ? seed.brand.trim() : "";
    const productName =
      typeof seed.product_name === "string" ? seed.product_name.trim() : "";
    if (!brand || !productName) {
      return NextResponse.json(
        {
          error:
            "cannot tag as evidence: at least one claim has no entity AND no brand or product name to derive one; use Merge into entity → first or Edit the claim to fill in brand+name",
        },
        { status: 400 },
      );
    }

    // Case-insensitive find by (brand, canonical_name).
    const { data: existing, error: findErr } = await sb
      .from("product_entities")
      .select("id")
      .ilike("brand", brand)
      .ilike("canonical_name", productName)
      .eq("is_retracted", false)
      .limit(1);
    if (findErr) {
      return NextResponse.json({ error: findErr.message }, { status: 500 });
    }

    if (existing && existing.length > 0) {
      derivedEntityId = existing[0].id as string;
    } else {
      const insertRow: Record<string, unknown> = {
        brand,
        canonical_name: productName,
      };
      if (typeof seed.category === "string" && seed.category) {
        insertRow.category = seed.category;
      }
      const { data: created, error: createErr } = await sb
        .from("product_entities")
        .insert(insertRow)
        .select("id")
        .single();
      if (createErr) {
        return NextResponse.json({ error: createErr.message }, { status: 500 });
      }
      derivedEntityId = created.id as string;
      createdEntity = true;
    }

    // Backfill matched_entity_id on the previously-unmatched claims.
    const unmatchedIds = needsEntity.map((c) => c.id);
    const { error: setMatchErr } = await sb
      .from("claims")
      .update({ matched_entity_id: derivedEntityId })
      .in("id", unmatchedIds);
    if (setMatchErr) {
      return NextResponse.json(
        { error: setMatchErr.message },
        { status: 500 },
      );
    }
  }

  // Now flip status and tags on every claim in the batch.
  const { error: updErr } = await sb
    .from("claims")
    .update({ status: "evidence", evidence_tags: tags })
    .in("id", ids);
  if (updErr) {
    return NextResponse.json({ error: updErr.message }, { status: 500 });
  }

  return NextResponse.json({
    ok: true,
    updated: ids.length,
    matched_count: needsEntity.length,
    entity_id: derivedEntityId,
    created_entity: createdEntity,
  });
}
