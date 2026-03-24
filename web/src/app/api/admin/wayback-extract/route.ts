import { NextRequest } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { extractSizeFromHtml, detectRetailer } from "@/lib/wayback-extract";
import crypto from "crypto";

const CDX_API = "https://web.archive.org/cdx/search/cdx";
const ARCHIVE_BASE = "https://web.archive.org/web";
const SCRAPER_VERSION = "wayback-web-v1.0";

// Rate-limit: ~0.5 req/s for fetching archived pages
const FETCH_DELAY_MS = 2000;

type SnapshotInput = {
  timestamp: string;
  sourceUrl: string;
  retailer: string;
  digest: string;
};

type ExtractionEvent = {
  type: "progress" | "result" | "cached" | "error" | "done";
  index?: number;
  total?: number;
  timestamp?: string;
  retailer?: string;
  archiveUrl?: string;
  size?: number | null;
  unit?: string | null;
  method?: string | null;
  sourceUrl?: string;
  error?: string;
  results?: Array<{
    timestamp: string;
    retailer: string;
    archiveUrl: string;
    sourceUrl: string;
    size: number | null;
    unit: string | null;
    method: string | null;
  }>;
};

/**
 * Select evenly-spaced snapshots: oldest, newest, and N evenly spaced in between.
 * Returns at most `max` snapshots per group.
 */
function selectSpacedSnapshots<T>(snapshots: T[], max: number): T[] {
  if (snapshots.length <= max) return snapshots;
  if (max <= 0) return [];
  if (max === 1) return [snapshots[0]];
  if (max === 2) return [snapshots[0], snapshots[snapshots.length - 1]];

  const result: T[] = [snapshots[0]]; // oldest
  const innerCount = max - 2;
  const step = (snapshots.length - 1) / (innerCount + 1);
  for (let i = 1; i <= innerCount; i++) {
    result.push(snapshots[Math.round(step * i)]);
  }
  result.push(snapshots[snapshots.length - 1]); // newest
  return result;
}

/**
 * Query the CDX API for snapshots of a URL.
 */
async function queryCdx(
  url: string,
): Promise<Array<{ timestamp: string; digest: string; length: string }>> {
  const params = new URLSearchParams({
    url,
    output: "json",
    fl: "timestamp,statuscode,digest,length",
    filter: "statuscode:200",
    collapse: "timestamp:6",
    limit: "100",
  });

  try {
    const resp = await fetch(`${CDX_API}?${params.toString()}`, {
      headers: { "User-Agent": "FullCarts/1.0 (shrinkflation research)" },
      signal: AbortSignal.timeout(15000),
    });
    if (!resp.ok) return [];
    const data = await resp.json();
    if (!data || data.length < 2) return [];

    const headers = data[0] as string[];
    const seen = new Set<string>();
    const results: Array<{ timestamp: string; digest: string; length: string }> = [];

    for (let i = 1; i < data.length; i++) {
      const record: Record<string, string> = {};
      headers.forEach((h: string, j: number) => (record[h] = data[i][j]));
      if (record.statuscode !== "200") continue;
      if (seen.has(record.digest)) continue;
      seen.add(record.digest);
      results.push({
        timestamp: record.timestamp,
        digest: record.digest,
        length: record.length || "0",
      });
    }
    return results;
  } catch {
    return [];
  }
}

/**
 * Generate direct product page URLs likely to have Wayback coverage.
 * Unlike search URLs, these are actual product pages that get crawled.
 */
function generateProductUrls(
  productName: string,
  brand: string,
): Array<{ retailer: string; url: string }> {
  const urls: Array<{ retailer: string; url: string }> = [];
  const query = `${brand} ${productName}`.trim();
  if (!query) return urls;

  // Open Food Facts search — these search result pages ARE well-archived
  // because OFF is a wiki-style site with stable, crawlable pages
  urls.push({
    retailer: "Open Food Facts",
    url: `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(query)}&search_simple=1&action=process`,
  });

  // For major retailers, use CDX wildcard search via the matchType param.
  // We'll handle this in the main flow by querying CDX with url prefix matching.

  return urls;
}

/**
 * Retailer product-page path prefixes.
 * Used with a brand slug to build a tight CDX prefix like
 * `walmart.com/ip/Kellogg*` instead of scanning all of `/ip/`.
 */
const RETAILER_PRODUCT_PATHS: Record<string, string> = {
  "www.walmart.com": "https://www.walmart.com/ip/",
  "www.kroger.com": "https://www.kroger.com/p/",
  "www.target.com": "https://www.target.com/p/",
  "www.amazon.com": "https://www.amazon.com/",
};

/**
 * Slugify a brand name for URL prefix matching.
 * Retailer URLs use the brand as the first segment of the slug,
 * e.g. "Kellogg's" → "Kellogg" in walmart.com/ip/Kellogg-s-...
 *
 * We take the first word of the brand (before apostrophes, spaces,
 * hyphens) to keep the prefix broad enough to catch URL variations.
 */
function slugifyBrand(brand: string): string {
  // Remove possessives, special chars, take first meaningful word
  const cleaned = brand
    .replace(/['']s?\b/g, "")   // Remove 's and possessives
    .replace(/[^a-zA-Z0-9\s-]/g, "")
    .trim();
  // Take first word (brands like "Frito-Lay" → "Frito", "Betty Crocker" → "Betty")
  const firstWord = cleaned.split(/[\s-]+/)[0];
  return firstWord || cleaned;
}

/**
 * Parse a CDX JSON response into typed rows.
 */
function parseCdxResponse(
  data: string[][],
): Array<{ url: string; timestamp: string; digest: string; length: string }> {
  if (!data || data.length < 2) return [];
  const headers = data[0];
  const results: Array<{
    url: string;
    timestamp: string;
    digest: string;
    length: string;
  }> = [];

  for (let i = 1; i < data.length; i++) {
    const record: Record<string, string> = {};
    headers.forEach((h, j) => (record[h] = data[i][j]));
    if (record.statuscode !== "200") continue;
    results.push({
      url: record.original || "",
      timestamp: record.timestamp,
      digest: record.digest,
      length: record.length || "0",
    });
  }
  return results;
}

/**
 * Search CDX for product pages across a retailer using brand-scoped prefixes.
 *
 * Strategy:
 *  1. Build a tight prefix using brand slug (e.g. `walmart.com/ip/Kellogg`)
 *     instead of scanning the entire product catalog
 *  2. Use CDX `filter=original:.*keyword.*` for each product keyword (AND'd)
 *  3. Collapse by month, dedup by digest
 *
 * This is dramatically faster than scanning all of `/ip/` because the CDX
 * index only needs to scan URLs starting with the brand name.
 */
async function searchRetailerCdx(
  retailerDomain: string,
  productName: string,
  brand: string,
): Promise<Array<{ url: string; timestamp: string; digest: string; length: string }>> {
  const basePath = RETAILER_PRODUCT_PATHS[retailerDomain];
  if (!basePath) return [];

  // Build brand-scoped prefix
  const brandSlug = slugifyBrand(brand);
  if (!brandSlug || brandSlug.length < 2) return [];
  const prefix = `${basePath}${brandSlug}`;

  // Extract product keywords (excluding brand words already in prefix)
  const stopWords = ["with", "from", "that", "this", "size", "family", "pack", "brand", "original", "value", "giant"];
  const brandWords = brand.toLowerCase().replace(/[^a-z0-9\s]/g, "").split(/\s+/);
  const productKeywords = productName
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, "")
    .split(/\s+/)
    .filter((w) => w.length > 2 && !stopWords.includes(w) && !brandWords.includes(w));

  // Sort by length (most specific first) and take top 3
  const keywords = productKeywords
    .sort((a, b) => b.length - a.length)
    .slice(0, 3);

  // Build CDX query with brand-scoped prefix + product keyword filters
  const params = new URLSearchParams({
    url: prefix,
    matchType: "prefix",
    output: "json",
    fl: "timestamp,original,statuscode,digest,length",
    collapse: "timestamp:6",
    from: "20150101",
    limit: "100",
  });

  let filterUrl = `${params.toString()}&filter=statuscode:200`;
  for (const kw of keywords) {
    filterUrl += `&filter=original:.*${encodeURIComponent(kw)}.*`;
  }

  try {
    const resp = await fetch(`${CDX_API}?${filterUrl}`, {
      headers: { "User-Agent": "FullCarts/1.0 (shrinkflation research)" },
      signal: AbortSignal.timeout(20000),
    });
    if (!resp.ok) return [];
    const data = await resp.json();
    const rows = parseCdxResponse(data);

    // Dedup by digest and filter out non-product pages
    const skipPatterns = ["/search", "/s?", "/browse/", "/category/", "/aisle/", "/shop/"];
    const seen = new Set<string>();
    const filtered: typeof rows = [];

    for (const row of rows) {
      if (skipPatterns.some((p) => row.url.includes(p))) continue;
      if (seen.has(row.digest)) continue;
      seen.add(row.digest);
      filtered.push(row);
    }

    return filtered;
  } catch {
    return [];
  }
}

/**
 * Fetch an archived page from Wayback Machine using the id_ modifier.
 */
async function fetchArchivedPage(archiveUrl: string): Promise<string | null> {
  try {
    const resp = await fetch(archiveUrl, {
      headers: { "User-Agent": "FullCarts/1.0 (shrinkflation research)" },
      signal: AbortSignal.timeout(60000),
    });
    if (!resp.ok) return null;
    return await resp.text();
  } catch {
    return null;
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function md5(input: string): string {
  return crypto.createHash("md5").update(input).digest("hex").slice(0, 12);
}

function sha256(input: string): string {
  return crypto.createHash("sha256").update(input).digest("hex");
}

/**
 * POST /api/admin/wayback-extract
 *
 * Accepts a list of snapshots (or product metadata for auto-discovery),
 * fetches archived HTML, extracts sizes, streams results via SSE.
 *
 * Request body:
 *   {
 *     snapshots?: Array<{ timestamp, sourceUrl, retailer, digest }>,
 *     productName?: string,
 *     brand?: string,
 *     customUrl?: string,
 *     upc?: string,
 *     claimOldSize?: number,
 *     claimOldUnit?: string,
 *     maxPerRetailer?: number  // default 5
 *   }
 *
 * If snapshots are provided, extract from those directly.
 * If only productName/brand, discover snapshots via CDX first.
 * If upc is provided, prioritize URLs containing that UPC.
 * If claimOldSize is provided, score results by size proximity.
 */
export async function POST(request: NextRequest) {
  const body = await request.json();
  const {
    snapshots: inputSnapshots,
    productName = "",
    brand = "",
    customUrl = "",
    upc = "",
    claimOldSize = 0,
    claimOldUnit = "",
    maxPerRetailer = 5,
  } = body as {
    snapshots?: SnapshotInput[];
    productName?: string;
    brand?: string;
    customUrl?: string;
    upc?: string;
    claimOldSize?: number;
    claimOldUnit?: string;
    maxPerRetailer?: number;
  };

  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      function send(event: ExtractionEvent) {
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify(event)}\n\n`),
        );
      }

      try {
        const supabase = createAdminClient();

        // ── Step 1: Resolve snapshots ────────────────────────────────
        let allSnapshots: SnapshotInput[] = [];

        if (inputSnapshots && inputSnapshots.length > 0) {
          allSnapshots = inputSnapshots;
        } else {
          // Auto-discover snapshots from product metadata
          send({ type: "progress", index: 0, total: 0 });

          // Collect URLs to check
          const urlsToQuery: Array<{ retailer: string; url: string }> = [];

          if (customUrl.trim()) {
            urlsToQuery.push({
              retailer: detectRetailer(customUrl.trim()),
              url: customUrl.trim(),
            });
          }

          // Add Open Food Facts search (well-archived)
          urlsToQuery.push(
            ...generateProductUrls(productName, brand),
          );

          // Query CDX for each direct URL
          const directResults = await Promise.allSettled(
            urlsToQuery.map(async ({ retailer, url }) => {
              const snaps = await queryCdx(url);
              return snaps.map((s) => ({
                timestamp: s.timestamp,
                sourceUrl: url,
                retailer,
                digest: s.digest,
              }));
            }),
          );

          for (const r of directResults) {
            if (r.status === "fulfilled") {
              allSnapshots.push(...r.value);
            }
          }

          // Search major retailers via brand-scoped CDX prefix queries
          const retailers = [
            { domain: "www.walmart.com", name: "Walmart" },
            { domain: "www.amazon.com", name: "Amazon" },
            { domain: "www.kroger.com", name: "Kroger" },
            { domain: "www.target.com", name: "Target" },
          ];

          // If UPC is available, also search for URLs containing the UPC.
          // Kroger and Target URLs often embed the UPC (e.g. /p/.../0003800014371).
          // This is the most precise way to find the exact SKU.
          const upcSearches: Promise<SnapshotInput[]>[] = [];
          if (upc.trim()) {
            const cleanUpc = upc.trim().replace(/^0+/, ""); // strip leading zeros for matching
            for (const { domain, name } of retailers) {
              const basePath = RETAILER_PRODUCT_PATHS[domain];
              if (!basePath) continue;
              upcSearches.push(
                (async () => {
                  try {
                    const params = new URLSearchParams({
                      url: basePath,
                      matchType: "prefix",
                      output: "json",
                      fl: "timestamp,original,statuscode,digest,length",
                      collapse: "timestamp:6",
                      from: "20150101",
                      limit: "50",
                    });
                    const filterUrl = `${params.toString()}&filter=statuscode:200&filter=original:.*${encodeURIComponent(cleanUpc)}.*`;
                    const resp = await fetch(`${CDX_API}?${filterUrl}`, {
                      headers: { "User-Agent": "FullCarts/1.0 (shrinkflation research)" },
                      signal: AbortSignal.timeout(20000),
                    });
                    if (!resp.ok) return [];
                    const data = await resp.json();
                    return parseCdxResponse(data).map((f) => ({
                      timestamp: f.timestamp,
                      sourceUrl: f.url,
                      retailer: name,
                      digest: f.digest,
                    }));
                  } catch {
                    return [];
                  }
                })(),
              );
            }
          }

          // Run brand-scoped searches and UPC searches in parallel
          const [retailerResults, ...upcResults] = await Promise.all([
            Promise.allSettled(
              retailers.map(async ({ domain, name }) => {
                const found = await searchRetailerCdx(
                  domain,
                  productName,
                  brand,
                );
                return found.map((f) => ({
                  timestamp: f.timestamp,
                  sourceUrl: f.url,
                  retailer: name,
                  digest: f.digest,
                }));
              }),
            ),
            ...upcSearches,
          ]);

          for (const r of retailerResults) {
            if (r.status === "fulfilled") {
              allSnapshots.push(...r.value);
            }
          }
          // Add UPC-matched snapshots (these are highest priority)
          for (const upcSnaps of upcResults) {
            if (Array.isArray(upcSnaps)) {
              allSnapshots.push(...upcSnaps);
            }
          }
        }

        // ── Step 2: Select evenly-spaced snapshots per SKU (URL) ─────
        // Group by sourceUrl so each product page (SKU) gets its own
        // set of time-spaced snapshots. This prevents mixing different
        // sizes (e.g., 12oz standard vs 16.9oz family) in the timeline.
        const byUrl: Record<string, SnapshotInput[]> = {};
        for (const snap of allSnapshots) {
          // Normalize URL: strip query params and trailing slashes
          const key = snap.sourceUrl.split("?")[0].replace(/\/+$/, "");
          if (!byUrl[key]) byUrl[key] = [];
          byUrl[key].push(snap);
        }

        // Pick 3 snapshots per URL (oldest, middle, newest — enough to
        // detect a size change within that SKU) and cap total at 20.
        const snapsPerUrl = 3;
        const maxTotal = 20;

        const selectedSnapshots: SnapshotInput[] = [];
        for (const [, snaps] of Object.entries(byUrl)) {
          snaps.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
          const deduped: SnapshotInput[] = [];
          const seenDigests = new Set<string>();
          for (const s of snaps) {
            if (!seenDigests.has(s.digest)) {
              seenDigests.add(s.digest);
              deduped.push(s);
            }
          }
          selectedSnapshots.push(
            ...selectSpacedSnapshots(deduped, snapsPerUrl),
          );
        }

        // Sort by timestamp and cap total
        selectedSnapshots.sort((a, b) =>
          a.timestamp.localeCompare(b.timestamp),
        );
        if (selectedSnapshots.length > maxTotal) {
          // Keep evenly spaced across the full set
          const trimmed = selectSpacedSnapshots(selectedSnapshots, maxTotal);
          selectedSnapshots.length = 0;
          selectedSnapshots.push(...trimmed);
        }

        const total = selectedSnapshots.length;

        if (total === 0) {
          send({
            type: "done",
            results: [],
          });
          controller.close();
          return;
        }

        // ── Step 3: Check cache in raw_items ─────────────────────────
        const sourceIds = selectedSnapshots.map(
          (s) => `wayback_${s.timestamp}_${md5(s.sourceUrl)}`,
        );

        const { data: cached } = await supabase
          .from("raw_items")
          .select("source_id, raw_payload")
          .eq("source_type", "wayback")
          .in("source_id", sourceIds);

        const cacheMap = new Map<string, Record<string, unknown>>();
        if (cached) {
          for (const row of cached) {
            cacheMap.set(
              row.source_id,
              row.raw_payload as Record<string, unknown>,
            );
          }
        }

        // ── Step 4: Extract sizes (with rate limiting) ───────────────
        const allResults: ExtractionEvent["results"] = [];

        for (let i = 0; i < selectedSnapshots.length; i++) {
          const snap = selectedSnapshots[i];
          const archiveUrl = `${ARCHIVE_BASE}/${snap.timestamp}id_/${snap.sourceUrl}`;
          const sourceId = `wayback_${snap.timestamp}_${md5(snap.sourceUrl)}`;

          send({
            type: "progress",
            index: i + 1,
            total,
            timestamp: snap.timestamp,
            retailer: snap.retailer,
          });

          // Check cache first
          const cachedPayload = cacheMap.get(sourceId);
          if (cachedPayload) {
            const r = {
              timestamp: snap.timestamp,
              retailer: snap.retailer,
              archiveUrl,
              sourceUrl: snap.sourceUrl,
              size: cachedPayload.extracted_size as number | null,
              unit: cachedPayload.extracted_unit as string | null,
              method: cachedPayload.extraction_method as string | null,
            };
            allResults.push(r);
            send({ type: "cached", ...r, index: i + 1, total });
            continue;
          }

          // Fetch and extract
          const html = await fetchArchivedPage(archiveUrl);
          if (!html) {
            send({
              type: "error",
              index: i + 1,
              total,
              timestamp: snap.timestamp,
              retailer: snap.retailer,
              error: "Failed to fetch archived page",
            });
            // Still rate-limit even on failures
            if (i < selectedSnapshots.length - 1) await sleep(FETCH_DELAY_MS);
            continue;
          }

          const extraction = extractSizeFromHtml(html, snap.sourceUrl);

          const r = {
            timestamp: snap.timestamp,
            retailer: snap.retailer,
            archiveUrl,
            sourceUrl: snap.sourceUrl,
            size: extraction.size,
            unit: extraction.unit,
            method: extraction.method,
          };
          allResults.push(r);
          send({ type: "result", ...r, index: i + 1, total });

          // Persist to raw_items
          const urlHash = md5(snap.sourceUrl);
          const payload = {
            snapshot_timestamp: snap.timestamp,
            url_hash: urlHash,
            archived_url: archiveUrl,
            original_url: snap.sourceUrl,
            retailer: detectRetailer(snap.sourceUrl),
            brand: brand || "Unknown",
            product_name: productName || "Unknown Product",
            upc: null,
            category: null,
            extracted_size: extraction.size,
            extracted_unit: extraction.unit,
            extraction_method: extraction.method,
            html_length: html.length,
            cdx_digest: snap.digest,
            cdx_length: null,
          };

          const contentHash = sha256(JSON.stringify(payload));

          await supabase.from("raw_items").upsert(
            {
              source_type: "wayback",
              source_id: sourceId,
              source_url: archiveUrl,
              source_date: snap.timestamp.length >= 8
                ? `${snap.timestamp.slice(0, 4)}-${snap.timestamp.slice(4, 6)}-${snap.timestamp.slice(6, 8)}T00:00:00Z`
                : null,
              raw_payload: payload,
              content_hash: contentHash,
              scraper_version: SCRAPER_VERSION,
            },
            { onConflict: "source_type,source_id", ignoreDuplicates: true },
          );

          // Rate limit between fetches
          if (i < selectedSnapshots.length - 1) await sleep(FETCH_DELAY_MS);
        }

        // ── Step 5: Send completion ──────────────────────────────────
        send({ type: "done", results: allResults });
      } catch (err) {
        send({
          type: "error",
          error: err instanceof Error ? err.message : "Unknown error",
        });
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
