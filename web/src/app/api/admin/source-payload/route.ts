import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// Admin-only endpoint that returns the raw_items.raw_payload JSON behind
// a single claim, plus the surrounding claim row. Used by the per-source
// "Inspect" expander on /products/[id] and /brands/[name] when the
// surface metadata in event_evidence_summary isn't enough to triage a
// retract decision.
//
// GET /api/admin/source-payload?claim_id=<uuid>
//
// Returns 401 for non-admins (the inspector UI is admin-gated already, this
// is defense-in-depth so a leaked URL can't expose internal payloads).

export async function GET(request: NextRequest) {
  if (!(await isAdminRequest())) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const claimId = request.nextUrl.searchParams.get("claim_id");
  if (!claimId || !/^[0-9a-f-]{36}$/i.test(claimId)) {
    return NextResponse.json(
      { error: "Missing or malformed claim_id" },
      { status: 400 },
    );
  }

  const sb = createAdminClient();
  const { data, error } = await sb
    .from("claims")
    .select(
      "id, status, brand, product_name, change_description, observed_date, " +
        "evidence_tags, image_storage_path, " +
        "raw_items ( id, source_type, source_url, source_date, raw_payload )",
    )
    .eq("id", claimId)
    .limit(1)
    .single();

  if (error || !data) {
    return NextResponse.json(
      { error: error?.message ?? "Claim not found" },
      { status: 404 },
    );
  }

  return NextResponse.json(data, {
    headers: { "Cache-Control": "no-store" },
  });
}
