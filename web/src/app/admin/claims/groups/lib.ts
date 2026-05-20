// Pure helpers for grouping pending claims. Tested in __tests__/lib.test.ts.
// No DB / no React deps — keep this file dependency-free so the grouper
// stays fast and trivially testable.

const BRAND_SUFFIX_RE = /\s+(plc|inc|ltd|llc|gmbh|sa|co|corp|corporation|limited)\.?$/i;
const SIZE_NOISE_RE = /\b\d+(\.\d+)?\s*(g|kg|ml|l|oz|lb|fl\s*oz|ct|count|pack|x)\b/gi;
const MULTIPACK_RE = /\b\d+\s*x\s*\d+(\.\d+)?\s*(g|kg|ml|l|oz)\b/gi;
const PUNCT_RE = /[^\w\s]/g;

export function normalizeBrand(b: string | null | undefined): string {
  if (!b) return "";
  let s = String(b).trim().toLowerCase();
  s = s.replace(BRAND_SUFFIX_RE, "");
  return s.replace(/\s+/g, " ").trim();
}

export function fuzzyNameKey(n: string | null | undefined): string {
  if (!n) return "";
  let s = String(n).toLowerCase();
  s = s.replace(MULTIPACK_RE, " ");
  s = s.replace(SIZE_NOISE_RE, " ");
  s = s.replace(PUNCT_RE, " ");
  const tokens = s.split(/\s+/).filter(Boolean).sort();
  return tokens.join(" ");
}

function fmt(n: number | null | undefined, unit: string): string {
  if (n == null) return "?";
  const stripped = Number.isInteger(n) ? String(n) : String(parseFloat(n.toFixed(3)));
  return `${stripped}${unit}`;
}

export function sizeBucket(
  oldSize: number | null | undefined,
  newSize: number | null | undefined,
  unit: string | null | undefined,
): string {
  const u = (unit || "").toLowerCase().trim();
  return `${fmt(oldSize, u)}→${fmt(newSize, u)}`;
}

export interface PendingClaim {
  id: string;
  brand: string | null;
  product_name: string | null;
  old_size: number | null;
  new_size: number | null;
  size_unit: string | null;
  confidence_overall: number;
  matched_entity_id: string | null;
  source_type: string | null;          // reddit / news / gdelt / ...
  image_storage_path: string | null;
  raw_payload_title: string | null;    // for display when product_name is null
  raw_item_url: string | null;         // outbound link to source
}

export interface SubCluster {
  matched_entity_id: string | null;
  claims: PendingClaim[];
}

export interface ClaimGroup {
  key: string;          // stable composite key
  brand: string;        // normalized
  brand_display: string; // first non-empty brand string from the claims
  name_key: string;     // fuzzy name key
  name_display: string; // representative product_name for the header
  size_change: string;  // canonical bucket string
  count: number;        // total claims across all sub-clusters
  sub_clusters: SubCluster[]; // sorted largest-first
  claims: PendingClaim[];     // flat list across all sub-clusters, highest-confidence first
  source_breakdown: Record<string, number>; // {reddit: 5, news: 2, ...}
  confidence_range: [number, number]; // min, max overall confidence
}

export function groupPendingClaims(claims: PendingClaim[]): ClaimGroup[] {
  const buckets = new Map<string, PendingClaim[]>();
  for (const c of claims) {
    const key = [
      normalizeBrand(c.brand),
      fuzzyNameKey(c.product_name),
      sizeBucket(c.old_size, c.new_size, c.size_unit),
    ].join("|");
    const list = buckets.get(key);
    if (list) list.push(c);
    else buckets.set(key, [c]);
  }

  const groups: ClaimGroup[] = [];
  for (const [key, list] of buckets) {
    const [b, n, sz] = key.split("|");
    const sortedByConf = [...list].sort((a, c) => c.confidence_overall - a.confidence_overall);
    const brandDisplay = list.find((c) => c.brand)?.brand || "(no brand)";
    const nameDisplay = list.find((c) => c.product_name)?.product_name || "(no name)";

    const subBuckets = new Map<string, PendingClaim[]>();
    for (const c of list) {
      const sk = c.matched_entity_id || "__unmatched__";
      const sub = subBuckets.get(sk);
      if (sub) sub.push(c);
      else subBuckets.set(sk, [c]);
    }
    const subClusters: SubCluster[] = [...subBuckets.entries()]
      .map(([sk, items]) => ({
        matched_entity_id: sk === "__unmatched__" ? null : sk,
        claims: items,
      }))
      .sort((a, c) => c.claims.length - a.claims.length);

    const sourceBreakdown: Record<string, number> = {};
    for (const c of list) {
      const s = c.source_type || "unknown";
      sourceBreakdown[s] = (sourceBreakdown[s] || 0) + 1;
    }

    const confs = list.map((c) => c.confidence_overall);
    const confRange: [number, number] = [Math.min(...confs), Math.max(...confs)];

    groups.push({
      key,
      brand: b,
      brand_display: brandDisplay,
      name_key: n,
      name_display: nameDisplay,
      size_change: sz,
      count: list.length,
      sub_clusters: subClusters,
      claims: sortedByConf,
      source_breakdown: sourceBreakdown,
      confidence_range: confRange,
    });
  }

  return groups.sort((a, c) => c.count - a.count);
}
