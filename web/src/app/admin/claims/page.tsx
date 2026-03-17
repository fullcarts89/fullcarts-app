import { createAdminClient } from "@/lib/supabase/admin";
import { ClaimImage } from "@/components/admin/ClaimImage";
import { ClaimActions } from "@/components/admin/ClaimActions";
import { ClaimEditor } from "@/components/admin/ClaimEditor";
import { ClaimFilters } from "@/components/admin/ClaimFilters";
import { SourceContent } from "@/components/admin/SourceContent";

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
    "bg-[var(--red-bg)] text-[var(--red-base)] border-[var(--red-border)]";
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
      <span className="mx-2 text-[var(--red-base)]">&rarr;</span>
      <span className="text-[var(--text-primary)]">{newS}</span>
      {pct && <span className="text-[var(--red-base)] text-xs ml-1">{pct}</span>}
    </div>
  );
}

function SourceBadge({ sourceType, sourceName }: { sourceType: string; sourceName?: string }) {
  const config: Record<string, { label: string; color: string }> = {
    reddit: { label: "Reddit", color: "bg-orange-500/10 text-orange-400 border-orange-500/20" },
    news: { label: sourceName || "News", color: "bg-[var(--blue-bg)] text-[var(--blue-base)] border-[var(--blue-border)]" },
    gdelt: { label: sourceName || "GDELT", color: "bg-purple-500/10 text-purple-400 border-purple-500/20" },
    usda_nutrition: { label: "USDA", color: "bg-[var(--green-bg)] text-[var(--green-base)] border-[var(--green-border)]" },
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
  return null;
}

const CONFIDENCE_TIERS = [
  { key: "all", label: "All", min: 0, max: 1 },
  { key: "high", label: "80%+", min: 0.8, max: 1 },
  { key: "mid", label: "60-79%", min: 0.6, max: 0.79 },
  { key: "low", label: "40-59%", min: 0.4, max: 0.59 },
  { key: "weak", label: "<40%", min: 0, max: 0.39 },
];


export default async function ClaimsReviewPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string; status?: string; conf?: string; category?: string }>;
}) {
  const params = await searchParams;
  const page = parseInt(params.page || "1", 10);
  const statusFilter = params.status || "pending";
  const confFilter = params.conf || "all";
  const categoryFilter = params.category || "";
  const perPage = 20;
  const offset = (page - 1) * perPage;

  const tier = CONFIDENCE_TIERS.find((t) => t.key === confFilter) || CONFIDENCE_TIERS[0];

  const supabase = createAdminClient();

  // Build query with filters
  let query = supabase
    .from("claims")
    .select("id,brand,product_name,category,old_size,old_size_unit,new_size,new_size_unit,old_price,new_price,change_description,confidence,status,observed_date,raw_item_id,evidence_tags,image_storage_path", { count: "exact" })
    .eq("status", statusFilter)
    .order("confidence->overall" as any, { ascending: false });

  if (confFilter !== "all") {
    query = query
      .gte("confidence->overall" as any, tier.min)
      .lte("confidence->overall" as any, tier.max);
  }

  if (categoryFilter) {
    query = query.eq("category", categoryFilter);
  }

  const { data: claims, count } = await query.range(offset, offset + perPage - 1);

  // Fetch raw_items for these claims
  const rawItemIds = (claims || []).map((c: Claim) => c.raw_item_id);
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
        <h1 className="font-[var(--font-headline)] text-2xl font-bold tracking-tight">
          Claim Review
        </h1>
        {/* Status tabs */}
        <div className="flex gap-3">
          {["pending", "approved", "evidence", "discarded"].map((s) => (
            <a
              key={s}
              href={`/admin/claims?status=${s}&page=1${confFilter !== "all" ? `&conf=${confFilter}` : ""}${categoryFilter ? `&category=${categoryFilter}` : ""}`}
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
        <ClaimFilters status={statusFilter} conf={confFilter} category={categoryFilter} />
      </header>

      <main className="max-w-5xl mx-auto px-6 py-6 space-y-4">
        {(claims || []).map((claim: Claim) => {
          const raw = rawMap.get(claim.raw_item_id);
          const payload = raw?.raw_payload;
          const imageUrl = payload ? getImageUrl(payload) : null;
          const permalink = payload?.permalink
            ? `https://www.reddit.com${payload.permalink}`
            : raw?.source_url;
          const title = payload?.title || "Untitled";

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
                href={`/admin/claims?status=${statusFilter}&page=${page - 1}${confFilter !== "all" ? `&conf=${confFilter}` : ""}${categoryFilter ? `&category=${categoryFilter}` : ""}`}
                className="px-4 py-2 text-sm rounded border border-[var(--bg-tertiary)] hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                Previous
              </a>
            )}
            {page < totalPages && (
              <a
                href={`/admin/claims?status=${statusFilter}&page=${page + 1}${confFilter !== "all" ? `&conf=${confFilter}` : ""}${categoryFilter ? `&category=${categoryFilter}` : ""}`}
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
