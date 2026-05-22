import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// POST /api/admin/merge-pair
// Body: { sourceId: string, targetId: string }
//
// Thin wrapper around the merge_entities RPC for the aggressive-tier UI.
// We use a route handler instead of a server action because server actions
// in Next.js trigger an automatic router cache refresh on completion, which
// re-renders the page and scrolls/reflows the duplicate-review list. The
// founder needs the page to stay anchored mid-triage.
//
// The audit trail (entity_merge_log) still gets written by the RPC; no
// behavioural difference from mergePair other than no auto-refresh.

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  if (!(await isAdminRequest())) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const sourceId = body?.sourceId;
  const targetId = body?.targetId;
  if (typeof sourceId !== "string" || typeof targetId !== "string") {
    return NextResponse.json(
      { error: "sourceId and targetId required" },
      { status: 400 },
    );
  }
  if (sourceId === targetId) {
    return NextResponse.json(
      { error: "source and target must differ" },
      { status: 400 },
    );
  }

  const sb = createAdminClient();
  const { data, error } = await sb.rpc("merge_entities", {
    p_source_id: sourceId,
    p_target_id: targetId,
    p_merged_by: "duplicates_batch",
  });
  if (error) {
    return NextResponse.json(
      { error: `merge_entities failed: ${error.message}` },
      { status: 500 },
    );
  }
  const row = (
    data as Array<{
      log_id: number;
      claims_moved: number;
      events_moved: number;
      variants_moved: number;
    }>
  )[0];
  return NextResponse.json({
    logId: row.log_id,
    claimsMoved: row.claims_moved,
    eventsMoved: row.events_moved,
    variantsMoved: row.variants_moved,
  });
}
