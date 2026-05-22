import { NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// GET /api/admin/distinct-brands?q=...&include_retracted=0
//
// Returns the top 20 brand strings matching the query, ranked by active
// entity count desc. Used by the BrandMergeModal pickers on /admin/entities
// so the admin can pick source + target by name without memorizing strings.
//
// Brand matching is case-INsensitive in the query filter (so typing "mars"
// surfaces "Mars", "MARS Inc", "Mars Wrigley") but the returned brand
// string is the exact canonical casing from the row — that matters because
// merge_brand keys on the exact string when finding entities to rebrand.

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  if (!(await isAdminRequest())) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  const url = new URL(req.url);
  const q = (url.searchParams.get("q") || "").trim();

  const sb = createAdminClient();
  // Pull all candidate entities matching the query (or all if no query).
  // We paginate just in case a popular brand has thousands of entities, but
  // for the typical case 1000 rows is plenty.
  let builder = sb
    .from("product_entities")
    .select("brand")
    .eq("is_retracted", false)
    .not("brand", "is", null);
  if (q.length >= 1) {
    builder = builder.ilike("brand", `%${q}%`);
  }
  const { data, error } = await builder.limit(5000);
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  // Aggregate counts client-side. (Doing a GROUP BY through PostgREST is
  // awkward; client aggregation across ≤5k rows is fine.)
  const counts = new Map<string, number>();
  for (const row of (data ?? []) as Array<{ brand: string | null }>) {
    const b = (row.brand || "").trim();
    if (!b) continue;
    counts.set(b, (counts.get(b) ?? 0) + 1);
  }
  const rows = Array.from(counts.entries())
    .map(([brand, entity_count]) => ({ brand, entity_count }))
    .sort((a, b) => b.entity_count - a.entity_count)
    .slice(0, 20);

  return NextResponse.json({ rows });
}
