import { NextRequest, NextResponse } from "next/server";
import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

/** Invalidate every public surface that derives from product_entities.brand
 *  so a fresh ISR render picks up the rebrand / merge / reassign. Called
 *  from this route and the two other mutation routes that touch entities. */
function revalidatePublicSurfaces() {
  revalidatePath("/");
  revalidatePath("/brands");
  revalidatePath("/brands/[name]", "page");
  revalidatePath("/products");
  revalidatePath("/products/[id]", "page");
  revalidatePath("/insights");
}

// POST /api/admin/merge-brand
// Body: { sourceBrand: string, targetBrand: string, dryRun?: boolean }
//
// Bulk-rebrand every ACTIVE entity whose brand exactly equals sourceBrand
// (case-sensitive — match the picker's exact-string contract). Each row
// goes through the existing set_entity_field RPC so the change lands in
// entity_edit_log per-entity and is reversible one row at a time.
//
// `dryRun: true` returns the affected count + first 50 affected names
// without writing — used by the modal to preview the impact before commit.
//
// Returns:
//   { affectedCount, affected[]: { id, brand, canonical_name }, written: boolean }

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  if (!(await isAdminRequest())) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const sourceBrand = (body?.sourceBrand ?? "").trim();
  const targetBrand = (body?.targetBrand ?? "").trim();
  const dryRun = !!body?.dryRun;
  if (!sourceBrand || !targetBrand) {
    return NextResponse.json(
      { error: "sourceBrand and targetBrand required" },
      { status: 400 },
    );
  }
  if (sourceBrand === targetBrand) {
    return NextResponse.json(
      { error: "sourceBrand and targetBrand must differ" },
      { status: 400 },
    );
  }

  const sb = createAdminClient();

  // Find every active entity with this exact brand string. Case-sensitive on
  // purpose — if the admin wants to also fold case variants ("Mars" vs
  // "mars") they should run the merge twice (or pre-fix via /admin/entities
  // click-to-edit).
  const { data: rows, error: findErr } = await sb
    .from("product_entities")
    .select("id, brand, canonical_name")
    .eq("is_retracted", false)
    .eq("brand", sourceBrand)
    .order("canonical_name");
  if (findErr) {
    return NextResponse.json({ error: findErr.message }, { status: 500 });
  }
  const affected = (rows ?? []) as Array<{ id: string; brand: string; canonical_name: string }>;

  if (dryRun) {
    return NextResponse.json({
      affectedCount: affected.length,
      affected: affected.slice(0, 50),
      written: false,
    });
  }

  // Apply per entity via set_entity_field. The RPC validates the field
  // (must be one of brand/canonical_name/category/manufacturer) and writes
  // entity_edit_log atomically. We loop here rather than a single UPDATE
  // because the per-row audit log is the only way to undo a brand merge
  // safely — we explicitly trade write-amplification for reversibility.
  let written = 0;
  const failed: Array<{ id: string; error: string }> = [];
  const writtenIds: string[] = [];
  for (const row of affected) {
    const { error: rpcErr } = await sb.rpc("set_entity_field", {
      p_entity_id: row.id,
      p_field: "brand",
      p_value: targetBrand,
      p_edited_by: "brand_merge",
    });
    if (rpcErr) {
      failed.push({ id: row.id, error: rpcErr.message });
      continue;
    }
    written++;
    writtenIds.push(row.id);
  }

  // Cascade the brand change to published_changes.brand for every event
  // attached to these entities. The denormalized brand column is the
  // join key /brands/[name] uses, so without this sync the rebranded
  // entities would disappear from the target brand page (and stay on
  // the source brand page) until a manual fix. Migration 071 added the
  // same sync to the merge_entities and reassign_events_by_size RPCs.
  if (writtenIds.length > 0) {
    const { error: syncErr } = await sb
      .from("published_changes")
      .update({ brand: targetBrand })
      .in("entity_id", writtenIds);
    if (syncErr) {
      // Non-fatal: the entity rebrand succeeded; the cascade is recoverable
      // via the migration 071 backfill statement. Surface it in `failed`
      // so the modal can show the warning.
      failed.push({ id: "published_changes_cascade", error: syncErr.message });
    }
  }

  if (written > 0) revalidatePublicSurfaces();

  return NextResponse.json({
    affectedCount: affected.length,
    affected: affected.slice(0, 50),
    writtenCount: written,
    failed,
    written: true,
  });
}
