import { createAdminClient } from "@/lib/supabase/admin";
import { ClaimImage } from "@/components/admin/ClaimImage";
import { ClaimActions } from "@/components/admin/ClaimActions";
import { ClaimEditor } from "@/components/admin/ClaimEditor";
import { ClaimFilters } from "@/components/admin/ClaimFilters";
import { SourceContent } from "@/components/admin/SourceContent";
import { PipelineStats } from "@/components/admin/PipelineStats";
import { WaybackLookup } from "@/components/admin/WaybackLookup";

type Claim = {
  id: string;
  brand: string | null;
  product_name: string | null;
  category: string | null;
  old_size: number | null;
  old_size_unit: string | null;
  new_size: number | null;
  new_size_unit: string | null;
  old_price: number | null;
  new_price: number | null;
  change_description: string | null;
  confidence: { brand: number; product_name: number; size_change: number; overall: number };
  status: string;
  observed_date: string | null;
  raw_item_id: string;
  upc: string | null;
  evidence_tags: string[] | null;
  image_storage_path: string | null;
};

type RawItem = {
  id: string;
  source_type: string;
  source_url: string | null;
  source_date: string | null;
  raw_payload: {
    title?: string;
    selftext?: string;
    url?: string;
    permalink?: string;
    score?: number;
    thumbnail?: string;
    source_name?: string;
    domain?: string;
    pubdate?: string;
    seendate?: string;
    created_utc?: number;
    preview?: { images?: Array<{ source?: { url?: string } }> };
    media_metadata?: Record<string, { s?: { u?: string } }>;
    // Kroger analyzer raw_items: written by analyze_kroger_changes.py
    new_date?: string;
  };
};

function getImageUrl(payload: RawItem["raw_payload"]): string | null {
  const url = payload.url || "";
  if (/i\.redd\.it|i\.imgur\.com|preview\.redd\.it|\.jpg|\.jpeg|\.png|\.webp/i.test(url)) {
    return url;
  }
  const meta = payload.media_metadata;
  if (meta && typeof meta === "object") {
    for (const v of Object.values(meta)) {
      const u = v?.s?.u;
      if (u) return u.replace(/&amp;/g, "&");
    }
  }
  const preview = payload.preview?.images?.[0]?.source?.url;
  if (preview) return preview.replace(/&amp;/g, "&");
  return null;
}

function ConfidenceBadge({ value, label }: { value: number; label: string }) {
  const color =
    value >= 0.8 ? "bg-[var(--green-bg)] text-[var(--green-base)] border-[var(--green-border)]" :
    value >= 0.5 ? "bg-[var(--amber-bg)] text-[var(--amber-base)] border-amber-500/20" :
    "bg-[var(--red-bg)] text-[var(--red-text)] border-[var(--red-border)]";
  return (
    <span className={`inline-block px-2 py-0.5 text-xs font-mono rounded border ${color}`}>
      {label}: {(value * 100).toFixed(0)}%
    </span>
  );
}

function SizeChange({ claim }: { claim: Claim }) {
  if (!claim.old_size && !claim.new_size) return null;
  const old = claim.old_size ? `${claim.old_size}${claim.old_size_unit || ""}` : "?";
  const newS = claim.new_size ? `${claim.new_size}${claim.new_size_unit || ""}` : "?";
  let pct = "";
  if (claim.old_size && claim.new_size) {
    const delta = ((claim.new_size - claim.old_size) / claim.old_size) * 100;
    pct = ` (${delta > 0 ? "+" : ""}${delta.toFixed(1)}%)`;
  }
  return (
    <div className="font-mono text-sm">
      <span className="text-[var(--text-secondary)]">{old}</span>
      <span className="mx-2 text-[var(--red-text)]">&rarr;</span>
      <span className="text-[var(--text-primary)]">{newS}</span>
      {pct && <span className="text-[var(--red-text)] text-xs ml-1">{pct}</span>}
    </div>
  );
}

function SourceBadge({ sourceType, sourceName }: { sourceType: string; sourceName?: string }) {
  const config: Record<string, { label: string; color: string }> = {
    reddit: { label: "Reddit", color: "bg-orange-500/10 text-orange-400 border-orange-500/20" },
    news: { label: sourceName || "News", color: "bg-[var(--blue-bg)] text-[var(--blue-base)] border-[var(--blue-border)]" },
    gdelt: { label: sourceName || "GDELT", color: "bg-purple-500/10 text-purple-400 border-purple-500/20" },
    usda_nutrition: { label: "USDA", color: "bg-[var(--green-bg)] text-[var(--green-base)] border-[var(--green-border)]" },
    kroger_change: { label: "Kroger", color: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20" },
    usda_size_change: { label: "USDA", color: "bg-[var(--green-bg)] text-[var(--green-base)] border-[var(--green-border)]" },
    openfoodfacts: { label: "OFF", color: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" },
  };
  const c = config[sourceType] || { label: sourceType, color: "bg-[var(--bg-tertiary)] text-[var(--text-secondary)] border-[var(--bg-tertiary)]" };
  return (
    <span className={`inline-block px-2 py-0.5 text-xs font-medium rounded border ${c.color}`}>
      {c.label}
    </span>
  );
}

function formatDate(raw: RawItem | undefined): string | null {
  if (!raw) return null;
  // Try source_date first
  if (raw.source_date) return raw.source_date.slice(0, 10);
  const p = raw.raw_payload;
  // Reddit: created_utc
  if (p.created_utc) {
    try {
      return new Date(p.created_utc * 1000).toISOString().slice(0, 10);
    } catch { /* ignore */ }
  }
  // News: pubdate
  if (p.pubdate) {
    try {
      return new Date(p.pubdate).toISOString().slice(0, 10);
    } catch { /* ignore */ }
  }
  // GDELT: seendate
  if (p.seendate) return p.seendate.slice(0, 10);
  // Kroger analyzer claims: new_date is the observation date of the change
  if (p.new_date) return String(p.new_date).slice(0, 10);
  return null;
}

const CONFIDENCE_TIERS = [
  { key: "all", label: "All", min: 0, max: 1 },
  { key: "high", label: "80%+", min: 0.8, max: 1 },
  { key: "mid", label: "60-79%", min: 0.6, max: 0.79 },
  { key: "low", label: "40-59%", min: 0.4, max: 0.59 },
  { key: "weak", label: "<40%", min: 0, max: 0.39 },
];

async function loadCategories(): Promise<string[]> {
  const sb = createAdminClient();
  const { data, error } = await sb
    .from("product_entities")
    .select("category")
    .eq("is_retracted", false)
    .not("category", "is", null)
    .limit(10000);
  if (error) throw new Error(`categories load: ${error.message}`);
  const set = new Set<string>();
  for (const r of (data ?? []) as Array<{ category: string | null }>) {
    if (r.category && r.category.trim()) set.add(r.category.trim());
  }
  return [...set].sort((a, b) => a.localeCompare(b, undefined, { sensitivity: "base" }));
}


export default async function ClaimsReviewPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string; status?: string; conf?: string; category?: string; source?: string; sort?: string }>;
}) {
  const params = await searchParams;
  const page = parseInt(params.page || "1", 10);
  const statusFilter = params.status || "pending";
  const confFilter = params.conf || "all";
  const categoryFilter = params.category || "";
  const sourceFilter = params.source || "";
  // Sort order for the claim list. "confidence" (default) keeps the legacy
  // highest-confidence-first behavior; "newest"/"oldest" sort by extracted_at
  // (always populated + indexed, unlike the nullable observed_date).
  const sortFilter = ["confidence", "newest", "oldest"].includes(params.sort || "")
    ? (params.sort as string)
    : "confidence";
  const perPage = 20;
  const offset = (page - 1) * perPage;

  const tier = CONFIDENCE_TIERS.find((t) => t.key === confFilter) || CONFIDENCE_TIERS[0];

  const supabase = createAdminClient();

  // Pipeline stats queries (run in parallel with claims query).
  // The Evidence tile counts evidence-wall-tagged claims via `evidence_tags`,
  // not `status='evidence'`. promote_claims writes status='evidence' for
  // fold-ins (claims merged into an existing event during dedup), which
  // would otherwise drown out the genuine evidence-wall claims in this tab.
  // The predicate matches `evidence_tags` non-null AND non-empty.
  const [evidenceCountRes, otherStatusCountsRaw, dailyStatsRes, latestClaimRes, categories] = await Promise.all([
    supabase
      .from("claims")
      .select("*", { count: "exact", head: true })
      .not("evidence_tags", "is", null)
      .not("evidence_tags", "eq", "{}"),
    Promise.all(
      (["pending", "matched", "discarded"] as const).map((s) =>
        supabase.from("claims").select("*", { count: "exact", head: true }).eq("status", s)
      )
    ),
    supabase.rpc("pipeline_daily_stats", { days_back: 14 }),
    supabase
      .from("claims")
      .select("extracted_at")
      .order("extracted_at", { ascending: false })
      .limit(1),
    loadCategories(),
  ]);

  const statusCounts = {
    pending: otherStatusCountsRaw[0].count ?? 0,
    matched: otherStatusCountsRaw[1].count ?? 0,
    evidence: evidenceCountRes.count ?? 0,
    discarded: otherStatusCountsRaw[2].count ?? 0,
  };

  // Pivot DB function results (per date+source rows) into per-date objects
  const dailyMap: Record<string, { total: number; reddit: number; news: number; gdelt: number }> = {};
  for (const row of dailyStatsRes.data || []) {
    const date = (row.extraction_date as string).slice(0, 10);
    if (!dailyMap[date]) dailyMap[date] = { total: 0, reddit: 0, news: 0, gdelt: 0 };
    const count = Number(row.claim_count);
    dailyMap[date].total += count;
    const src = row.source_type as string;
    if (src === "reddit") dailyMap[date].reddit += count;
    else if (src === "news") dailyMap[date].news += count;
    else if (src === "gdelt") dailyMap[date].gdelt += count;
  }
  const dailyCounts = Object.entries(dailyMap)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, counts]) => ({ date, ...counts }));

  // Pipeline health: healthy if extraction ran within 48h. The page is
  // a server component (async function), so Date.now() runs once per
  // render on the server — the react-hooks/purity rule doesn't apply
  // outside client components.
  const latestExtractedAt = latestClaimRes.data?.[0]?.extracted_at;
  const hoursAgo = latestExtractedAt
    // eslint-disable-next-line react-hooks/purity
    ? Math.floor((Date.now() - new Date(latestExtractedAt as string).getTime()) / 3600000)
    : Infinity;
  const pipelineHealthy = hoursAgo < 48;
  const lastExtractionAgo =
    hoursAgo === Infinity
      ? "never"
      : hoursAgo < 1
        ? "just now"
        : hoursAgo < 24
          ? `${hoursAgo}h ago`
          : `${Math.floor(hoursAgo / 24)}d ago`;

  // Build query with filters. When a source filter is active we INNER JOIN
  // raw_items so PostgREST will filter the claim rows by raw_items.source_type.
  const baseSelect =
    "id,brand,product_name,category,old_size,old_size_unit,new_size,new_size_unit," +
    "old_price,new_price,change_description,confidence,status,observed_date," +
    "raw_item_id,upc,evidence_tags,image_storage_path";
  const selectExpr = sourceFilter
    ? `${baseSelect},raw_items!inner(source_type)`
    : baseSelect;

  // Evidence tab is special: filter by `evidence_tags` non-empty instead of
  // by `status='evidence'`. That keeps PR-#63 fold-ins (which also land at
  // status='evidence' from promote_claims) out of the tab without needing
  // a separate status value in the claims_status_check constraint.
  let query = supabase
    .from("claims")
    .select(selectExpr, { count: "exact" });

  if (sortFilter === "newest") {
    query = query.order("extracted_at", { ascending: false });
  } else if (sortFilter === "oldest") {
    query = query.order("extracted_at", { ascending: true });
  } else {
    query = query
      // eslint-disable-next-line @typescript-eslint/no-explicit-any -- supabase-js doesn't type JSONB ->path columns
      .order("confidence->overall" as any, { ascending: false });
  }

  if (statusFilter === "evidence") {
    query = query.not("evidence_tags", "is", null).not("evidence_tags", "eq", "{}");
  } else {
    query = query.eq("status", statusFilter);
  }

  if (sourceFilter) {
    // Cast through `any` here: the supabase-js generic for an embedded INNER
    // JOIN filter inflates the type tree past TypeScript's inference depth
    // (TS2589) — without this the entire claims query type goes "excessively
    // deep". Behavior is the standard PostgREST `raw_items.source_type=eq.X`.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    query = (query as any).eq("raw_items.source_type", sourceFilter);
  }

  if (confFilter !== "all") {
    query = query
      // eslint-disable-next-line @typescript-eslint/no-explicit-any -- JSONB path same as above
      .gte("confidence->overall" as any, tier.min)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .lte("confidence->overall" as any, tier.max);
  }

  if (categoryFilter) {
    query = query.eq("category", categoryFilter);
  }

  // The dynamic `selectExpr` (which may include an embedded raw_items inner
  // join) defeats supabase-js generic inference and returns `GenericStringError`
  // unless we widen here. The underlying rows are still Claim[].
  const { data: rawClaims, count } = await query.range(offset, offset + perPage - 1);
  const claims = (rawClaims || []) as unknown as Claim[];

  // Fetch raw_items for these claims
  const rawItemIds = claims.map((c) => c.raw_item_id);
  const { data: rawItems } = rawItemIds.length > 0
    ? await supabase
        .from("raw_items")
        .select("id,source_type,source_url,source_date,raw_payload")
        .in("id", rawItemIds)
    : { data: [] as RawItem[] };

  const rawMap = new Map<string, RawItem>();
  (rawItems || []).forEach((r: RawItem) => rawMap.set(r.id, r));

  const totalPages = Math.ceil((count || 0) / perPage);

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]">
      <header className="border-b border-[var(--bg-tertiary)] px-6 py-4 space-y-3">
        <div className="flex items-baseline gap-4">
          <h1 className="font-[var(--font-headline)] text-2xl font-bold tracking-tight">
            Claim Review
          </h1>
          <a
            href="/admin/entities"
            className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] underline-offset-4 hover:underline"
          >
            Entity Browser →
          </a>
          <a
            href="/admin/quality-flags"
            className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] underline-offset-4 hover:underline"
          >
            Quality Flags →
          </a>
          <a
            href="/admin/claims/groups"
            className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] underline-offset-4 hover:underline"
          >
            Group view →
          </a>
        </div>
        {/* Status tabs */}
        <div className="flex gap-3">
          {["pending", "matched", "evidence", "discarded"].map((s) => (
            <a
              key={s}
              href={`/admin/claims?status=${s}&page=1${confFilter !== "all" ? `&conf=${confFilter}` : ""}${categoryFilter ? `&category=${categoryFilter}` : ""}${sourceFilter ? `&source=${encodeURIComponent(sourceFilter)}` : ""}${sortFilter !== "confidence" ? `&sort=${sortFilter}` : ""}`}
              className={`px-3 py-1.5 text-sm rounded-md border transition-colors ${
                statusFilter === s
                  ? "bg-[var(--bg-tertiary)] border-[var(--text-tertiary)] text-[var(--text-primary)]"
                  : "border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              }`}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </a>
          ))}
          <span className="ml-auto text-sm text-[var(--text-secondary)]">
            {count || 0} claims &middot; Page {page}/{totalPages || 1}
          </span>
        </div>
        {/* Confidence + Category filters */}
        <ClaimFilters status={statusFilter} conf={confFilter} category={categoryFilter} source={sourceFilter} sort={sortFilter} />
      </header>

      <PipelineStats
        statusCounts={statusCounts}
        dailyCounts={dailyCounts}
        pipelineHealthy={pipelineHealthy}
        lastExtractionAgo={lastExtractionAgo}
      />

      <main id="main-content" className="max-w-5xl mx-auto px-6 py-6 space-y-4">
        {claims.map((claim) => {
          const raw = rawMap.get(claim.raw_item_id);
          const payload = raw?.raw_payload;
          const imageUrl = payload ? getImageUrl(payload) : null;
          const permalink = payload?.permalink
            ? `https://www.reddit.com${payload.permalink}`
            : raw?.source_url;
          const title =
            payload?.title ||
            [claim.brand, claim.product_name].filter(Boolean).join(" ") ||
            "Untitled";

          return (
            <article
              key={claim.id}
              className="border border-[var(--bg-tertiary)] rounded-lg bg-[var(--bg-secondary)] overflow-hidden"
            >
              <div className="flex flex-col sm:flex-row">
                {/* Image column */}
                <div className="w-full sm:w-64 h-48 sm:min-h-48 bg-[var(--bg-primary)] flex-shrink-0 relative">
                  {imageUrl || claim.image_storage_path ? (
                    <ClaimImage
                      src={imageUrl || ""}
                      storagePath={claim.image_storage_path}
                      alt={title}
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full text-[var(--text-tertiary)] text-sm">
                      No image
                    </div>
                  )}
                </div>

                {/* Content column */}
                <div className="flex-1 p-4 space-y-3 min-w-0">
                  {/* Source badge + date + title */}
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <SourceBadge
                        sourceType={raw?.source_type || "unknown"}
                        sourceName={payload?.source_name || payload?.domain}
                      />
                      {formatDate(raw) && (
                        <span className="text-xs font-mono text-[var(--text-tertiary)]">
                          {formatDate(raw)}
                        </span>
                      )}
                      {payload?.score != null && (
                        <span className="text-xs text-[var(--text-tertiary)]">
                          {payload.score} pts
                        </span>
                      )}
                    </div>
                    <a
                      href={permalink || "#"}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[var(--blue-base)] hover:underline text-sm font-medium block"
                    >
                      {title}
                    </a>
                    <SourceContent
                      selftext={payload?.selftext || ""}
                      sourceType={raw?.source_type || "unknown"}
                    />
                  </div>

                  {/* Extracted data */}
                  <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm">
                    <div>
                      <span className="text-[var(--text-tertiary)]">Brand: </span>
                      <span className="font-medium">{claim.brand || "—"}</span>
                    </div>
                    <div>
                      <span className="text-[var(--text-tertiary)]">Product: </span>
                      <span className="font-medium">{claim.product_name || "—"}</span>
                    </div>
                    <div>
                      <span className="text-[var(--text-tertiary)]">Category: </span>
                      <span>{claim.category || "—"}</span>
                    </div>
                    <SizeChange claim={claim} />
                  </div>

                  {/* Change description */}
                  {claim.change_description && (
                    <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                      {claim.change_description}
                    </p>
                  )}

                  {/* Confidence badges + actions */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <ConfidenceBadge value={claim.confidence.overall} label="Overall" />
                    <ConfidenceBadge value={claim.confidence.brand} label="Brand" />
                    <ConfidenceBadge value={claim.confidence.size_change} label="Size" />
                    <ClaimEditor
                      claimId={claim.id}
                      initialValues={{
                        brand: claim.brand || "",
                        product_name: claim.product_name || "",
                        category: claim.category || "",
                        old_size: claim.old_size != null ? String(claim.old_size) : "",
                        old_size_unit: claim.old_size_unit || "",
                        new_size: claim.new_size != null ? String(claim.new_size) : "",
                        new_size_unit: claim.new_size_unit || "",
                        change_description: claim.change_description || "",
                      }}
                      categories={categories}
                    />
                    <WaybackLookup
                      productName={claim.product_name || ""}
                      brand={claim.brand || ""}
                      sourceUrl={raw?.source_url || null}
                      upc={claim.upc || null}
                      claimOldSize={claim.old_size}
                      claimOldUnit={claim.old_size_unit}
                    />
                    <div className="ml-auto">
                      <ClaimActions claimId={claim.id} currentStatus={claim.status} currentTags={claim.evidence_tags || undefined} />
                    </div>
                  </div>
                </div>
              </div>
            </article>
          );
        })}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center gap-2 pt-4">
            {page > 1 && (
              <a
                href={`/admin/claims?status=${statusFilter}&page=${page - 1}${confFilter !== "all" ? `&conf=${confFilter}` : ""}${categoryFilter ? `&category=${categoryFilter}` : ""}${sourceFilter ? `&source=${encodeURIComponent(sourceFilter)}` : ""}${sortFilter !== "confidence" ? `&sort=${sortFilter}` : ""}`}
                className="px-4 py-2 text-sm rounded border border-[var(--bg-tertiary)] hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                Previous
              </a>
            )}
            {page < totalPages && (
              <a
                href={`/admin/claims?status=${statusFilter}&page=${page + 1}${confFilter !== "all" ? `&conf=${confFilter}` : ""}${categoryFilter ? `&category=${categoryFilter}` : ""}${sourceFilter ? `&source=${encodeURIComponent(sourceFilter)}` : ""}${sortFilter !== "confidence" ? `&sort=${sortFilter}` : ""}`}
                className="px-4 py-2 text-sm rounded border border-[var(--bg-tertiary)] hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                Next
              </a>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
