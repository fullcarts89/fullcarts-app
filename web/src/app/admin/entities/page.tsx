import Link from "next/link";
import { createAdminClient } from "@/lib/supabase/admin";
import { RetractButton } from "./RetractButton";
import { EditableField } from "./EditableField";
import { MergeButton } from "./MergeButton";
import { SendClaimsToPendingButton } from "./SendClaimsToPendingButton";

type EntityRow = {
  id: string;
  brand: string;
  canonical_name: string;
  category: string | null;
  manufacturer: string | null;
  image_url: string | null;
  is_retracted: boolean;
  created_at: string;
};

const PER_PAGE = 30;

const STATUS_FILTERS = [
  { key: "active", label: "Active" },
  { key: "retracted", label: "Retracted" },
  { key: "all", label: "All" },
] as const;

type StatusFilter = (typeof STATUS_FILTERS)[number]["key"];

export default async function AdminEntitiesPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string; status?: string; q?: string }>;
}) {
  const params = await searchParams;
  const page = Math.max(1, parseInt(params.page || "1", 10));
  const statusFilter: StatusFilter = (STATUS_FILTERS.find((s) => s.key === params.status)?.key ??
    "active") as StatusFilter;
  const search = (params.q || "").trim();
  const offset = (page - 1) * PER_PAGE;

  const supabase = createAdminClient();

  // Status counts (parallel, used for the tab badges)
  const [activeCountRes, retractedCountRes, totalCountRes] = await Promise.all([
    supabase
      .from("product_entities")
      .select("*", { count: "exact", head: true })
      .eq("is_retracted", false),
    supabase
      .from("product_entities")
      .select("*", { count: "exact", head: true })
      .eq("is_retracted", true),
    supabase.from("product_entities").select("*", { count: "exact", head: true }),
  ]);

  const statusCounts = {
    active: activeCountRes.count ?? 0,
    retracted: retractedCountRes.count ?? 0,
    all: totalCountRes.count ?? 0,
  };

  // Main list query
  let query = supabase
    .from("product_entities")
    .select(
      "id, brand, canonical_name, category, manufacturer, image_url, is_retracted, created_at",
      { count: "exact" }
    )
    .order("created_at", { ascending: false });

  if (statusFilter === "active") query = query.eq("is_retracted", false);
  else if (statusFilter === "retracted") query = query.eq("is_retracted", true);

  if (search) {
    // PostgREST `or` filter — substring match on brand or canonical_name
    const safe = search.replace(/[,()*]/g, " ");
    query = query.or(`brand.ilike.%${safe}%,canonical_name.ilike.%${safe}%`);
  }

  const { data: entitiesRaw, count } = await query.range(offset, offset + PER_PAGE - 1);
  const entities = (entitiesRaw ?? []) as EntityRow[];

  // Event counts for the rows we're rendering — single batched query.
  const ids = entities.map((e) => e.id);
  const eventCountByEntity = new Map<string, number>();
  if (ids.length > 0) {
    const { data: eventRows } = await supabase
      .from("published_changes")
      .select("entity_id")
      .in("entity_id", ids);
    for (const row of (eventRows ?? []) as Array<{ entity_id: string }>) {
      eventCountByEntity.set(row.entity_id, (eventCountByEntity.get(row.entity_id) ?? 0) + 1);
    }
  }

  const totalPages = Math.max(1, Math.ceil((count ?? 0) / PER_PAGE));

  function makeUrl(next: { page?: number; status?: StatusFilter; q?: string }) {
    const sp = new URLSearchParams();
    const nextStatus = next.status ?? statusFilter;
    const nextQ = next.q ?? search;
    const nextPage = next.page ?? 1;
    if (nextStatus !== "active") sp.set("status", nextStatus);
    if (nextQ) sp.set("q", nextQ);
    if (nextPage > 1) sp.set("page", String(nextPage));
    const qs = sp.toString();
    return `/admin/entities${qs ? `?${qs}` : ""}`;
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]">
      <header className="border-b border-[var(--bg-tertiary)] px-6 py-4 space-y-3">
        <div className="flex items-baseline gap-4">
          <h1 className="font-[var(--font-headline)] text-2xl font-bold tracking-tight">
            Entity Browser
          </h1>
          <Link
            href="/admin/claims"
            className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] underline-offset-4 hover:underline"
          >
            ← Claims Review
          </Link>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Status tabs */}
          <div className="flex gap-2">
            {STATUS_FILTERS.map((s) => (
              <a
                key={s.key}
                href={makeUrl({ status: s.key, page: 1 })}
                className={`px-3 py-1.5 text-sm rounded-md border transition-colors ${
                  statusFilter === s.key
                    ? "bg-[var(--bg-tertiary)] border-[var(--text-tertiary)] text-[var(--text-primary)]"
                    : "border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                }`}
              >
                {s.label}
                <span className="ml-1.5 text-xs text-[var(--text-tertiary)] font-mono">
                  {statusCounts[s.key]}
                </span>
              </a>
            ))}
          </div>

          {/* Search */}
          <form action="/admin/entities" method="get" className="flex items-center gap-2">
            {statusFilter !== "active" && (
              <input type="hidden" name="status" value={statusFilter} />
            )}
            <input
              type="search"
              name="q"
              defaultValue={search}
              placeholder="Search brand or product..."
              className="px-3 py-1.5 text-sm bg-[var(--bg-secondary)] border border-[var(--bg-tertiary)] rounded-md focus:outline-none focus:border-[var(--text-tertiary)] min-w-[20rem]"
            />
            {search && (
              <a
                href={makeUrl({ q: "", page: 1 })}
                className="text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] font-mono"
              >
                clear
              </a>
            )}
          </form>

          <span className="ml-auto text-sm text-[var(--text-secondary)]">
            {count ?? 0} entities &middot; Page {page}/{totalPages}
          </span>
        </div>
      </header>

      <div className="p-6">
        <div className="overflow-x-auto border border-[var(--bg-tertiary)] rounded-md">
          <table className="w-full text-sm">
            <thead className="bg-[var(--bg-secondary)] border-b border-[var(--bg-tertiary)]">
              <tr className="text-left text-xs uppercase tracking-wider text-[var(--text-secondary)]">
                <th className="px-3 py-2 w-12"></th>
                <th className="px-3 py-2">Brand</th>
                <th className="px-3 py-2">Canonical Name</th>
                <th className="px-3 py-2">Category</th>
                <th className="px-3 py-2 text-right">Events</th>
                <th className="px-3 py-2 text-right">Created</th>
                <th className="px-3 py-2 text-right">Status</th>
              </tr>
            </thead>
            <tbody>
              {entities.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-3 py-12 text-center text-[var(--text-secondary)]"
                  >
                    No entities match these filters.
                  </td>
                </tr>
              )}
              {entities.map((e) => {
                const events = eventCountByEntity.get(e.id) ?? 0;
                return (
                  <tr
                    key={e.id}
                    className={`border-b border-[var(--bg-tertiary)] last:border-b-0 ${
                      e.is_retracted ? "opacity-60" : ""
                    }`}
                  >
                    <td className="px-3 py-2">
                      {e.image_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img
                          src={e.image_url}
                          alt=""
                          className="w-10 h-10 object-cover rounded border border-[var(--bg-tertiary)]"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded border border-[var(--bg-tertiary)] bg-[var(--bg-secondary)]" />
                      )}
                    </td>
                    <td className="px-3 py-2 font-medium">
                      <EditableField
                        entityId={e.id}
                        field="brand"
                        value={e.brand}
                      />
                      <Link
                        href={`/brands/${encodeURIComponent(e.brand.toLowerCase())}`}
                        className="ml-1 text-xs text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]"
                        target="_blank"
                        rel="noreferrer"
                        title="Open public brand page"
                      >
                        ↗
                      </Link>
                    </td>
                    <td className="px-3 py-2">
                      <EditableField
                        entityId={e.id}
                        field="canonical_name"
                        value={e.canonical_name}
                      />
                      <Link
                        href={`/products/${e.id}`}
                        className="ml-1 text-xs text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]"
                        target="_blank"
                        rel="noreferrer"
                        title="Open public product page"
                      >
                        ↗
                      </Link>
                      <div className="text-xs text-[var(--text-tertiary)] mt-0.5">
                        mfr:{" "}
                        <EditableField
                          entityId={e.id}
                          field="manufacturer"
                          value={e.manufacturer}
                          placeholder="(none)"
                        />
                      </div>
                    </td>
                    <td className="px-3 py-2 text-[var(--text-secondary)]">
                      <EditableField
                        entityId={e.id}
                        field="category"
                        value={e.category}
                      />
                    </td>
                    <td className="px-3 py-2 text-right font-mono">
                      {events > 0 ? events : <span className="text-[var(--text-tertiary)]">0</span>}
                    </td>
                    <td className="px-3 py-2 text-right text-[var(--text-secondary)] font-mono text-xs">
                      {e.created_at.slice(0, 10)}
                    </td>
                    <td className="px-3 py-2 text-right">
                      <div className="flex flex-col items-end gap-1.5">
                        <RetractButton
                          entityId={e.id}
                          isRetracted={e.is_retracted}
                          entityLabel={`${e.brand} — ${e.canonical_name}`}
                          eventCount={events}
                        />
                        {e.is_retracted && (
                          <SendClaimsToPendingButton
                            entityId={e.id}
                            entityLabel={`${e.brand} — ${e.canonical_name}`}
                          />
                        )}
                        <MergeButton
                          sourceId={e.id}
                          sourceLabel={`${e.brand} — ${e.canonical_name}`}
                        />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-4 flex items-center justify-between text-sm">
            <a
              href={makeUrl({ page: Math.max(1, page - 1) })}
              className={`px-3 py-1.5 rounded border ${
                page <= 1
                  ? "border-[var(--bg-tertiary)] text-[var(--text-tertiary)] pointer-events-none"
                  : "border-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              }`}
            >
              ← Previous
            </a>
            <span className="text-[var(--text-secondary)] font-mono">
              {page} / {totalPages}
            </span>
            <a
              href={makeUrl({ page: Math.min(totalPages, page + 1) })}
              className={`px-3 py-1.5 rounded border ${
                page >= totalPages
                  ? "border-[var(--bg-tertiary)] text-[var(--text-tertiary)] pointer-events-none"
                  : "border-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              }`}
            >
              Next →
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
