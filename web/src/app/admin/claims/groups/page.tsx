import Link from "next/link";
import { createAdminClient } from "@/lib/supabase/admin";
import { groupPendingClaims } from "./lib";
import type { PendingClaim, ClaimGroup } from "./lib";
import GroupsClient from "./GroupsClient";

export const dynamic = "force-dynamic";

async function loadAllPendingClaims(): Promise<PendingClaim[]> {
  const sb = createAdminClient();
  const PAGE = 1000;
  const all: PendingClaim[] = [];
  // Paginate past PostgREST's 1k cap.
  for (let from = 0; ; from += PAGE) {
    const { data, error } = await sb
      .from("claims")
      .select(
        "id,brand,product_name,old_size,new_size,old_size_unit,confidence," +
          "matched_entity_id,image_storage_path,raw_item_id," +
          "raw_items!inner(source_type,source_url,raw_payload)",
      )
      .eq("status", "pending")
      .order("id")
      .range(from, from + PAGE - 1);
    if (error) throw new Error(`claims load: ${error.message}`);
    const batch = (data ?? []) as unknown as Array<{
      id: string;
      brand: string | null;
      product_name: string | null;
      old_size: number | null;
      new_size: number | null;
      old_size_unit: string | null;
      confidence: { overall?: number } | null;
      matched_entity_id: string | null;
      image_storage_path: string | null;
      raw_item_id: string;
      raw_items: {
        source_type: string | null;
        source_url: string | null;
        raw_payload: { title?: string } | null;
      };
    }>;
    for (const row of batch) {
      all.push({
        id: row.id,
        brand: row.brand,
        product_name: row.product_name,
        old_size: row.old_size,
        new_size: row.new_size,
        size_unit: row.old_size_unit,
        confidence_overall: row.confidence?.overall ?? 0,
        matched_entity_id: row.matched_entity_id,
        source_type: row.raw_items?.source_type ?? null,
        image_storage_path: row.image_storage_path,
        raw_payload_title: row.raw_items?.raw_payload?.title ?? null,
        raw_item_url: row.raw_items?.source_url ?? null,
      });
    }
    if (batch.length < PAGE) break;
  }
  return all;
}

export default async function ClaimsGroupsPage() {
  const claims = await loadAllPendingClaims();
  const groups: ClaimGroup[] = groupPendingClaims(claims);
  const totalClaims = claims.length;
  const totalGroups = groups.length;
  const singletons = groups.filter((g) => g.count === 1).length;

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]">
      <header className="border-b border-[var(--bg-tertiary)] px-6 py-4 space-y-3">
        <div className="flex items-baseline gap-4">
          <h1 className="font-[var(--font-headline)] text-2xl font-bold tracking-tight">
            Claim Groups
          </h1>
          <Link
            href="/admin/claims?status=pending"
            className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] underline-offset-4 hover:underline"
          >
            ← Single-card review
          </Link>
        </div>
        <p className="text-sm text-[var(--text-secondary)]">
          {totalClaims.toLocaleString()} pending claims grouped into{" "}
          {totalGroups.toLocaleString()} clusters
          {singletons > 0 && (
            <span> · {singletons.toLocaleString()} singletons (1-claim groups)</span>
          )}
          . Largest groups first. Each cluster shares brand + fuzzy product name +
          size change.
        </p>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-6 space-y-4">
        {groups.length === 0 ? (
          <div className="border border-[var(--bg-tertiary)] rounded-lg p-8 text-center text-[var(--text-secondary)]">
            No pending claims to group.
          </div>
        ) : (
          <GroupsClient groups={groups} />
        )}
      </main>
    </div>
  );
}
