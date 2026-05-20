import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// Bulk-flip a set of claims to status='matched'. Called from
// /admin/claims/groups GroupsClient for "approve all" on a group or
// a multi-group selection.
//
// The DB enforces `claims_match_required` (see migration 066): a row
// can only sit at status='matched' if it also has a non-null
// matched_entity_id. So we cannot just flip status — we must point
// each claim at an entity in the same UPDATE.
//
// Two modes:
//   Branch A — caller passed an explicit entity_id (cross-group bulk
//     where the UI has already resolved the target). We sanity-check
//     the entity and route every claim there.
//   Branch B — single-group case with no entity_id. We load the first
//     claim's brand+product_name (the grouper guarantees all claims in
//     a batch share these), then find-or-create a product_entity by
//     case-insensitive (brand, canonical_name) match, mirroring
//     pipeline/scripts/promote_claims.py.

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  if (!(await isAdminRequest())) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const raw = body?.claim_ids;
  const ids = Array.isArray(raw)
    ? raw.filter((x): x is string => typeof x === "string")
    : [];
  if (ids.length === 0) {
    return NextResponse.json(
      { error: "claim_ids required" },
      { status: 400 },
    );
  }

  const explicitEntityId =
    typeof body?.entity_id === "string" && body.entity_id
      ? (body.entity_id as string)
      : null;

  const sb = createAdminClient();

  // Branch A: explicit entity_id — verify and route there.
  if (explicitEntityId) {
    const { data: ent, error: entErr } = await sb
      .from("product_entities")
      .select("id, is_retracted")
      .eq("id", explicitEntityId)
      .maybeSingle();
    if (entErr) {
      return NextResponse.json({ error: entErr.message }, { status: 500 });
    }
    if (!ent) {
      return NextResponse.json(
        { error: "entity not found" },
        { status: 404 },
      );
    }
    if (ent.is_retracted) {
      return NextResponse.json(
        { error: "entity is retracted" },
        { status: 400 },
      );
    }

    const { error: updErr } = await sb
      .from("claims")
      .update({ status: "matched", matched_entity_id: explicitEntityId })
      .in("id", ids);
    if (updErr) {
      return NextResponse.json({ error: updErr.message }, { status: 500 });
    }
    return NextResponse.json({
      ok: true,
      updated: ids.length,
      entity_id: explicitEntityId,
    });
  }

  // Branch B: auto-derive entity from the first claim's brand+product_name.
  const { data: firstClaim, error: claimErr } = await sb
    .from("claims")
    .select("id, brand, product_name, category")
    .eq("id", ids[0])
    .maybeSingle();
  if (claimErr) {
    return NextResponse.json({ error: claimErr.message }, { status: 500 });
  }
  if (!firstClaim) {
    return NextResponse.json({ error: "claim not found" }, { status: 404 });
  }

  const brand =
    typeof firstClaim.brand === "string" ? firstClaim.brand.trim() : "";
  const productName =
    typeof firstClaim.product_name === "string"
      ? firstClaim.product_name.trim()
      : "";
  if (!brand || !productName) {
    return NextResponse.json(
      {
        error:
          "cannot auto-approve: claim group has no brand or product name; use Merge into entity → and pick one manually",
      },
      { status: 400 },
    );
  }

  // Case-insensitive find by (brand, canonical_name). PostgREST's `ilike`
  // with a no-wildcard pattern is the simplest equivalent to LOWER(?)=LOWER(?).
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

  let entityId: string;
  let createdEntity = false;
  if (existing && existing.length > 0) {
    entityId = existing[0].id as string;
  } else {
    const insertRow: Record<string, unknown> = {
      brand,
      canonical_name: productName,
    };
    if (typeof firstClaim.category === "string" && firstClaim.category) {
      insertRow.category = firstClaim.category;
    }
    const { data: created, error: createErr } = await sb
      .from("product_entities")
      .insert(insertRow)
      .select("id")
      .single();
    if (createErr) {
      return NextResponse.json({ error: createErr.message }, { status: 500 });
    }
    entityId = created.id as string;
    createdEntity = true;
  }

  const { error: updErr } = await sb
    .from("claims")
    .update({ status: "matched", matched_entity_id: entityId })
    .in("id", ids);
  if (updErr) {
    return NextResponse.json({ error: updErr.message }, { status: 500 });
  }

  return NextResponse.json({
    ok: true,
    updated: ids.length,
    entity_id: entityId,
    created_entity: createdEntity,
  });
}
