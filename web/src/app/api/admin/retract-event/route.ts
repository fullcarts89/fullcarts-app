import { NextRequest, NextResponse } from "next/server";
import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// Retract a published event and send every claim that backs it back to
// `pending` so the founder can re-decide in /admin/claims.
//
// Cascade:
//   1. published_changes.is_retracted = true (event vanishes from public views,
//      which all filter on is_retracted = false).
//   2. claims feeding the event flip to status='pending' with matched_*
//      pointers nulled, so the row reappears in the admin queue and a future
//      promote_claims run treats it as fresh.
//
// Backing claims come from two places:
//   - change_candidates.supporting_claims[]  (originator claim of the event)
//   - published_changes.evidence_summary[]   (claims folded in by later
//                                             promote_claims runs)

export async function POST(request: NextRequest) {
  if (!(await isAdminRequest())) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const eventId = body?.event_id;
  if (!eventId || typeof eventId !== "string") {
    return NextResponse.json(
      { error: "Missing event_id" },
      { status: 400 },
    );
  }

  const sb = createAdminClient();

  const { data: event, error: eventErr } = await sb
    .from("published_changes")
    .select("id, entity_id, candidate_id, evidence_summary, is_retracted")
    .eq("id", eventId)
    .maybeSingle();

  if (eventErr) {
    return NextResponse.json({ error: eventErr.message }, { status: 500 });
  }
  if (!event) {
    return NextResponse.json({ error: "Event not found" }, { status: 404 });
  }

  const claimIds = new Set<string>();

  if (event.candidate_id) {
    const { data: candidate, error: candErr } = await sb
      .from("change_candidates")
      .select("supporting_claims")
      .eq("id", event.candidate_id)
      .maybeSingle();
    if (candErr) {
      return NextResponse.json({ error: candErr.message }, { status: 500 });
    }
    for (const id of candidate?.supporting_claims ?? []) {
      if (typeof id === "string") claimIds.add(id);
    }
  }

  if (Array.isArray(event.evidence_summary)) {
    for (const entry of event.evidence_summary) {
      const cid = (entry as { claim_id?: unknown })?.claim_id;
      if (typeof cid === "string") claimIds.add(cid);
    }
  }

  const { error: retractErr } = await sb
    .from("published_changes")
    .update({ is_retracted: true, retracted_at: new Date().toISOString() })
    .eq("id", eventId);
  if (retractErr) {
    return NextResponse.json({ error: retractErr.message }, { status: 500 });
  }

  let claimsReverted = 0;
  if (claimIds.size > 0) {
    const { data: updated, error: claimErr } = await sb
      .from("claims")
      .update({
        status: "pending",
        matched_entity_id: null,
        matched_variant_id: null,
      })
      .in("id", Array.from(claimIds))
      .select("id");
    if (claimErr) {
      return NextResponse.json({ error: claimErr.message }, { status: 500 });
    }
    claimsReverted = updated?.length ?? 0;
  }

  // Drop ISR caches for every public surface that lists events so the
  // retracted row disappears on the next view rather than after the
  // ambient 1-hour revalidate window.
  revalidatePath("/");
  revalidatePath("/brands");
  revalidatePath("/products");
  revalidatePath("/insights");
  if (event.entity_id) {
    revalidatePath(`/products/${event.entity_id}`);
  }
  revalidatePath("/brands/[name]", "page");

  return NextResponse.json({
    ok: true,
    event_id: eventId,
    claims_reverted: claimsReverted,
  });
}
