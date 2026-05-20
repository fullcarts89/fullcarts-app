import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// Bulk-approve a set of claims while patching shared fields (brand /
// product_name / category / size fields) in the same UPDATE. Called from
// /admin/claims/groups when the founder uses the "edit then approve"
// flow to normalise a group before approval (e.g. canonicalising brand
// spelling or correcting a missing old_size). Only patch fields that
// are present-and-non-empty are written; the rest of each row stays
// as-is. Status flips to 'matched' by default.
//
// Per-claim "Edit (don't approve)" path: pass approve=false in the body
// and status will be left untouched (the patch still applies).
//
// When approve=true and a claim has matched_entity_id=null, the
// claims_match_required constraint blocks the UPDATE. We work around
// it by auto-deriving an entity from the EDITED brand+product_name
// (patch values take precedence over the existing claim values, since
// the user is correcting them in this same call) and back-filling
// matched_entity_id before the status flip.

export const dynamic = "force-dynamic";

interface Patch {
  brand?: string;
  product_name?: string;
  category?: string;
  old_size?: number;
  old_size_unit?: string;
  new_size?: number;
  new_size_unit?: string;
  change_description?: string;
}

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
    return NextResponse.json(
      { error: "claim_ids required" },
      { status: 400 },
    );
  }

  const patchRaw =
    body?.patch && typeof body.patch === "object"
      ? (body.patch as Record<string, unknown>)
      : {};
  const patch: Patch = {};
  if (typeof patchRaw.brand === "string" && patchRaw.brand) {
    patch.brand = patchRaw.brand;
  }
  if (typeof patchRaw.product_name === "string" && patchRaw.product_name) {
    patch.product_name = patchRaw.product_name;
  }
  if (typeof patchRaw.category === "string" && patchRaw.category) {
    patch.category = patchRaw.category;
  }
  // Numeric size fields: accept either number or numeric-string. Reject NaN.
  if (patchRaw.old_size != null && patchRaw.old_size !== "") {
    const n =
      typeof patchRaw.old_size === "number"
        ? patchRaw.old_size
        : parseFloat(String(patchRaw.old_size));
    if (!Number.isNaN(n)) patch.old_size = n;
  }
  if (typeof patchRaw.old_size_unit === "string" && patchRaw.old_size_unit) {
    patch.old_size_unit = patchRaw.old_size_unit;
  }
  if (patchRaw.new_size != null && patchRaw.new_size !== "") {
    const n =
      typeof patchRaw.new_size === "number"
        ? patchRaw.new_size
        : parseFloat(String(patchRaw.new_size));
    if (!Number.isNaN(n)) patch.new_size = n;
  }
  if (typeof patchRaw.new_size_unit === "string" && patchRaw.new_size_unit) {
    patch.new_size_unit = patchRaw.new_size_unit;
  }
  if (
    typeof patchRaw.change_description === "string" &&
    patchRaw.change_description
  ) {
    patch.change_description = patchRaw.change_description;
  }

  const approve = body?.approve !== false; // default true
  const update: Record<string, unknown> = approve
    ? { status: "matched", ...patch }
    : { ...patch };
  if (Object.keys(update).length === 0) {
    return NextResponse.json(
      { error: "patch is empty and approve=false" },
      { status: 400 },
    );
  }

  const sb = createAdminClient();

  // When approving, ensure every claim has a matched_entity_id (the DB
  // constraint requires it). Auto-derive from the edited values if any
  // claim is still unmatched.
  if (approve) {
    type ClaimRow = {
      id: string;
      brand: string | null;
      product_name: string | null;
      category: string | null;
      matched_entity_id: string | null;
    };
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
    const rows = claims as ClaimRow[];
    const needsEntity = rows.filter((c) => !c.matched_entity_id);

    if (needsEntity.length > 0) {
      const seed = needsEntity[0];
      // Patch values override existing claim values for the derivation —
      // the user is correcting brand/name in this same call.
      const brand = (patch.brand ?? seed.brand ?? "").trim();
      const productName = (patch.product_name ?? seed.product_name ?? "").trim();
      if (!brand || !productName) {
        return NextResponse.json(
          {
            error:
              "cannot approve: at least one claim has no entity AND no brand/product name to derive one. Fill in Brand and Product name in the Edit form.",
          },
          { status: 400 },
        );
      }

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
      if (existing && existing.length > 0) {
        entityId = existing[0].id as string;
      } else {
        const insertRow: Record<string, unknown> = {
          brand,
          canonical_name: productName,
        };
        const cat = patch.category ?? seed.category;
        if (typeof cat === "string" && cat) insertRow.category = cat;
        const { data: created, error: createErr } = await sb
          .from("product_entities")
          .insert(insertRow)
          .select("id")
          .single();
        if (createErr) {
          return NextResponse.json(
            { error: createErr.message },
            { status: 500 },
          );
        }
        entityId = created.id as string;
      }

      const unmatchedIds = needsEntity.map((c) => c.id);
      const { error: setMatchErr } = await sb
        .from("claims")
        .update({ matched_entity_id: entityId })
        .in("id", unmatchedIds);
      if (setMatchErr) {
        return NextResponse.json(
          { error: setMatchErr.message },
          { status: 500 },
        );
      }
    }
  }

  const { error } = await sb.from("claims").update(update).in("id", ids);
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
  return NextResponse.json({ ok: true, updated: ids.length });
}
