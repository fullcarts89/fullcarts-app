import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// Bulk-flip a set of claims to status='evidence' with the given
// evidence_tags. Called from /admin/claims/groups GroupsClient for
// "send to evidence wall" on a group or a multi-group selection.
//
// Mirrors the single-card flow in ClaimActions.tsx but skips the
// per-claim round-trip. status='evidence' is NOT covered by the
// claims_match_required constraint (see migration 066), so we can
// flip status without touching matched_entity_id.

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

  const rawTags = body?.tags;
  const tags = Array.isArray(rawTags)
    ? rawTags.filter((x): x is string => typeof x === "string" && x.length > 0)
    : [];
  if (tags.length === 0) {
    return NextResponse.json(
      { error: "tags required" },
      { status: 400 },
    );
  }

  const sb = createAdminClient();
  const { error } = await sb
    .from("claims")
    .update({ status: "evidence", evidence_tags: tags })
    .in("id", ids);
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
  return NextResponse.json({ ok: true, updated: ids.length });
}
