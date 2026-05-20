import { NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

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

  // Step 2: tally live events per returned entity.
  const ids = rows.map((r) => r.id);
  const { data: events } = await sb
    .from("published_changes")
    .select("entity_id")
    .eq("is_retracted", false)
    .in("entity_id", ids);

  const counts = new Map<string, number>();
  for (const e of (events || []) as Array<{ entity_id: string | null }>) {
    if (e.entity_id) counts.set(e.entity_id, (counts.get(e.entity_id) || 0) + 1);
  }

  const enriched = rows
    .map((r) => ({ ...r, event_count: counts.get(r.id) || 0 }))
    .sort((a, b) => b.event_count - a.event_count);

  const filtered = enriched.filter((r) => r.event_count > 0);
  return NextResponse.json({ rows: filtered });
}
