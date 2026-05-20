import { NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// Returns the distinct list of categories currently in use on
// non-retracted product_entities, alphabetised. Used by the
// /admin/claims/groups bulk-edit category dropdown so the choices
// stay aligned with what's actually live in the DB.

export const dynamic = "force-dynamic";

export async function GET() {
  if (!(await isAdminRequest())) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const sb = createAdminClient();
  const { data, error } = await sb
    .from("product_entities")
    .select("category")
    .eq("is_retracted", false)
    .not("category", "is", null)
    .limit(10000);
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  const seen = new Set<string>();
  for (const row of data ?? []) {
    const cat = (row as { category?: unknown }).category;
    if (typeof cat === "string") {
      const trimmed = cat.trim();
      if (trimmed) seen.add(trimmed);
    }
  }
  const categories = Array.from(seen).sort((a, b) =>
    a.localeCompare(b, undefined, { sensitivity: "base" }),
  );
  return NextResponse.json({ categories });
}
