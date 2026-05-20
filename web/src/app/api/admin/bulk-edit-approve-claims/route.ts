import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// Bulk-approve a set of claims while patching shared fields (brand /
// product_name / category) in the same UPDATE. Called from
// /admin/claims/groups when the founder uses the "edit then approve"
// flow to normalise a group before approval (e.g. canonicalising brand
// spelling). Only patch fields that are present-and-non-empty are
// written; the rest of each row stays as-is. Status always flips to
// 'matched'.

export const dynamic = "force-dynamic";

interface Patch {
  brand?: string;
  product_name?: string;
  category?: string;
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

  const update: Record<string, unknown> = { status: "matched", ...patch };

  const sb = createAdminClient();
  const { error } = await sb.from("claims").update(update).in("id", ids);
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
  return NextResponse.json({ ok: true, updated: ids.length });
}
