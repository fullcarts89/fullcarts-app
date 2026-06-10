import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// Flip claims back to status='pending' and clear evidence_tags. Backs the
// single-card "Restore to Pending" (discarded tab) and "Move to Pending"
// (matched / evidence tab) buttons on /admin/claims.
//
// A route handler rather than a Server Action: Server Actions auto-revalidate
// the calling route on completion, which re-renders the heavy /admin/claims
// page and leaves the card's button stuck on "..." for the whole render. See
// the merge-pair / bulk-*-claims routes for the same reasoning.
//
// Parity with the retired updateClaimStatus(id, "pending", []) Server Action:
// set status + empty evidence_tags only. matched_entity_id is left intact
// (pending neither requires nor forbids it).

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
    return NextResponse.json({ error: "claim_ids required" }, { status: 400 });
  }

  const sb = createAdminClient();
  const { error } = await sb
    .from("claims")
    .update({ status: "pending", evidence_tags: [] })
    .in("id", ids);
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
  return NextResponse.json({ ok: true, updated: ids.length });
}
