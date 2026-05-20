import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// Bulk-merge a set of claims into an existing product_entity: flips status
// to 'matched' and points matched_entity_id at the chosen target. Called
// from /admin/claims/groups when the founder picks a target entity for a
// group via the merge-picker modal.
//
// Sanity check: the target entity must exist and must not be retracted.

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
    return NextResponse.json(
      { error: "claim_ids required" },
      { status: 400 },
    );
  }
  const entityId = body?.entity_id;
  if (!entityId || typeof entityId !== "string") {
    return NextResponse.json(
      { error: "entity_id required" },
      { status: 400 },
    );
  }

  const sb = createAdminClient();

  const { data: ent, error: entErr } = await sb
    .from("product_entities")
    .select("id, is_retracted")
    .eq("id", entityId)
    .maybeSingle();
  if (entErr) {
    return NextResponse.json({ error: entErr.message }, { status: 500 });
  }
  if (!ent) {
    return NextResponse.json({ error: "entity not found" }, { status: 404 });
  }
  if (ent.is_retracted) {
    return NextResponse.json(
      { error: "entity is retracted" },
      { status: 400 },
    );
  }

  const { error } = await sb
    .from("claims")
    .update({ status: "matched", matched_entity_id: entityId })
    .in("id", ids);
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
  return NextResponse.json({ ok: true, updated: ids.length });
}
