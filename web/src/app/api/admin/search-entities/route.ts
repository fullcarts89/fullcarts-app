import { NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";
import { sizeBucket } from "@/app/admin/claims/groups/lib";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  if (!(await isAdminRequest())) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const url = new URL(req.url);
  const q = (url.searchParams.get("q") || "").trim();
  if (q.length < 2) return NextResponse.json({ rows: [] });

  const sb = createAdminClient();

  // Step 1: fetch up to 20 matching active entities.
  const { data: ents, error } = await sb
    .from("product_entities")
    .select("id,brand,canonical_name,category")
    .eq("is_retracted", false)
    .or(`brand.ilike.%${q}%,canonical_name.ilike.%${q}%`)
    .limit(20);
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  const rows = (ents || []) as Array<{ id: string; brand: string; canonical_name: string; category: string | null }>;
  if (rows.length === 0) return NextResponse.json({ rows: [] });

  // Step 2: tally live events per returned entity, plus collect each event's canonical size bucket.
  const ids = rows.map((r) => r.id);
  const { data: events } = await sb
    .from("published_changes")
    .select("entity_id,size_before,size_after,size_unit")
    .eq("is_retracted", false)
    .in("entity_id", ids);

  const counts = new Map<string, number>();
  const sizesByEntity = new Map<string, Set<string>>();
  for (const e of (events || []) as Array<{
    entity_id: string | null;
    size_before: number | null;
    size_after: number | null;
    size_unit: string | null;
  }>) {
    if (!e.entity_id) continue;
    counts.set(e.entity_id, (counts.get(e.entity_id) || 0) + 1);
    if (e.size_before != null && e.size_after != null) {
      const bucket = sizeBucket(e.size_before, e.size_after, e.size_unit);
      const set = sizesByEntity.get(e.entity_id);
      if (set) set.add(bucket);
      else sizesByEntity.set(e.entity_id, new Set([bucket]));
    }
  }

  const enriched = rows
    .map((r) => ({
      ...r,
      event_count: counts.get(r.id) || 0,
      event_sizes: [...(sizesByEntity.get(r.id) || new Set<string>())].sort(),
    }))
    .filter((r) => r.event_count > 0)
    .sort((a, b) => b.event_count - a.event_count);

  return NextResponse.json({ rows: enriched });
}
