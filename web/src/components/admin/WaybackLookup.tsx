"use client";

import { useState } from "react";

const CDX_API = "https://web.archive.org/cdx/search/cdx";
const ARCHIVE_BASE = "https://web.archive.org/web";

type Snapshot = {
  timestamp: string;
  retailer: string;
  sourceUrl: string;
  archiveUrl: string;
  digest: string;
};

type RetailerResult = {
  retailer: string;
  snapshots: Snapshot[];
  oldest: string;
  newest: string;
};

/** Generate retail URLs from a product name + brand for cross-retailer lookup. */
function generateRetailUrls(productName: string, brand: string): Array<{ retailer: string; url: string }> {
  const query = `${brand} ${productName}`.trim();
  if (!query) return [];

  const urls: Array<{ retailer: string; url: string }> = [];

  // Open Food Facts search (clean HTML, good archive coverage)
  urls.push({
    retailer: "Open Food Facts",
    url: `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(query)}&search_simple=1&action=process`,
  });
  // Walmart search
  urls.push({
    retailer: "Walmart",
    url: `https://www.walmart.com/search?q=${encodeURIComponent(query)}`,
  });
  // Amazon search
  urls.push({
    retailer: "Amazon",
    url: `https://www.amazon.com/s?k=${encodeURIComponent(query)}`,
  });
  // Kroger search
  urls.push({
    retailer: "Kroger",
    url: `https://www.kroger.com/search?query=${encodeURIComponent(query)}`,
  });
  // Target search
  urls.push({
    retailer: "Target",
    url: `https://www.target.com/s?searchTerm=${encodeURIComponent(query)}`,
  });

  return urls;
}

/** Detect retailer from URL. */
function detectRetailer(url: string): string {
  const u = url.toLowerCase();
  if (u.includes("walmart.com")) return "Walmart";
  if (u.includes("amazon.com")) return "Amazon";
  if (u.includes("kroger.com")) return "Kroger";
  if (u.includes("target.com")) return "Target";
  if (u.includes("openfoodfacts.org")) return "Open Food Facts";
  if (u.includes("fdc.nal.usda.gov")) return "USDA FDC";
  return "Other";
}

/** Query the CDX API for snapshots of a URL. */
async function queryCdx(url: string): Promise<Array<{ timestamp: string; digest: string }>> {
  const params = new URLSearchParams({
    url,
    output: "json",
    fl: "timestamp,statuscode,digest",
    filter: "statuscode:200",
    collapse: "timestamp:6", // ~monthly
    limit: "100",
  });

  try {
    const resp = await fetch(`${CDX_API}?${params.toString()}`);
    if (!resp.ok) return [];
    const data = await resp.json();
    if (!data || data.length < 2) return [];

    const headers = data[0] as string[];
    const seen = new Set<string>();
    const results: Array<{ timestamp: string; digest: string }> = [];

    for (let i = 1; i < data.length; i++) {
      const record: Record<string, string> = {};
      headers.forEach((h, j) => (record[h] = data[i][j]));
      if (seen.has(record.digest)) continue;
      seen.add(record.digest);
      results.push({ timestamp: record.timestamp, digest: record.digest });
    }
    return results;
  } catch {
    return [];
  }
}

function formatTimestamp(ts: string): string {
  if (ts.length >= 8) return `${ts.slice(0, 4)}-${ts.slice(4, 6)}-${ts.slice(6, 8)}`;
  return ts;
}

const RETAILER_COLORS: Record<string, string> = {
  Walmart: "#0071dc",
  Amazon: "#ff9900",
  Kroger: "#e31837",
  Target: "#cc0000",
  "Open Food Facts": "#201a17",
  "USDA FDC": "#336b3d",
  Other: "#6b7280",
};

export function WaybackLookup({
  productName,
  brand,
  sourceUrl,
}: {
  productName: string;
  brand: string;
  sourceUrl: string | null;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [customUrl, setCustomUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<RetailerResult[] | null>(null);
  const [allSnapshots, setAllSnapshots] = useState<Snapshot[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function runLookup() {
    setLoading(true);
    setError(null);
    setResults(null);
    setAllSnapshots([]);

    try {
      // Build URL list
      const urlsToCheck: Array<{ retailer: string; url: string }> = [];

      // Custom URL first
      if (customUrl.trim()) {
        urlsToCheck.push({ retailer: detectRetailer(customUrl.trim()), url: customUrl.trim() });
      }

      // Source URL from the claim's raw_item
      if (sourceUrl) {
        urlsToCheck.push({ retailer: detectRetailer(sourceUrl), url: sourceUrl });
      }

      // Auto-generated URLs from product name + brand
      urlsToCheck.push(...generateRetailUrls(productName, brand));

      // Deduplicate by URL
      const seen = new Set<string>();
      const unique = urlsToCheck.filter(({ url }) => {
        if (seen.has(url)) return false;
        seen.add(url);
        return true;
      });

      // Query all in parallel
      const settled = await Promise.allSettled(
        unique.map(async ({ retailer, url }) => {
          const snapshots = await queryCdx(url);
          return { retailer, url, snapshots };
        })
      );

      // Aggregate results by retailer
      const retailerMap: Record<string, Snapshot[]> = {};
      const all: Snapshot[] = [];

      for (const result of settled) {
        if (result.status !== "fulfilled") continue;
        const { retailer, url, snapshots } = result.value;
        if (snapshots.length === 0) continue;

        if (!retailerMap[retailer]) retailerMap[retailer] = [];
        for (const snap of snapshots) {
          const s: Snapshot = {
            timestamp: snap.timestamp,
            retailer,
            sourceUrl: url,
            archiveUrl: `${ARCHIVE_BASE}/${snap.timestamp}/${url}`,
            digest: snap.digest,
          };
          retailerMap[retailer].push(s);
          all.push(s);
        }
      }

      // Build retailer summary
      const retailerResults: RetailerResult[] = Object.entries(retailerMap).map(
        ([retailer, snaps]) => {
          const sorted = snaps.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
          return {
            retailer,
            snapshots: sorted,
            oldest: sorted[0].timestamp,
            newest: sorted[sorted.length - 1].timestamp,
          };
        }
      );

      const sortedAll = all.sort((a, b) => a.timestamp.localeCompare(b.timestamp));

      setResults(retailerResults);
      setAllSnapshots(sortedAll);

      if (all.length === 0) {
        setError("No archived snapshots found. Try pasting a specific product page URL.");
      }
    } catch (e) {
      setError(`Lookup failed: ${e instanceof Error ? e.message : "Unknown error"}`);
    } finally {
      setLoading(false);
    }
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="px-2.5 py-1 text-xs font-medium rounded border border-purple-500/20 bg-purple-500/10 text-purple-400 hover:brightness-125 transition-all"
        title="Search Internet Archive for historical product page snapshots"
      >
        Wayback
      </button>
    );
  }

  return (
    <div className="mt-3 pt-3 border-t border-[var(--bg-tertiary)] space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-bold uppercase tracking-wider text-purple-400">
          Wayback Machine Lookup
        </h4>
        <button
          onClick={() => setIsOpen(false)}
          className="text-xs text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]"
        >
          Close
        </button>
      </div>

      <p className="text-xs text-[var(--text-tertiary)]">
        Search the Internet Archive for historical snapshots of this product across retailers.
      </p>

      {/* Custom URL input */}
      <div>
        <label className="block text-xs text-[var(--text-tertiary)] mb-1">
          Product page URL (optional — auto-searches 5 retailers by name)
        </label>
        <input
          type="url"
          value={customUrl}
          onChange={(e) => setCustomUrl(e.target.value)}
          placeholder="https://www.walmart.com/ip/Product-Name/123456"
          className="w-full px-2 py-1.5 text-sm rounded border border-[var(--bg-tertiary)] bg-[var(--bg-primary)] text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:border-purple-500/50"
        />
      </div>

      {/* Run button */}
      <button
        onClick={runLookup}
        disabled={loading}
        className="w-full px-3 py-2 text-sm font-medium rounded border border-purple-500/30 bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 transition-all disabled:opacity-50"
      >
        {loading ? "Searching Internet Archive..." : "Investigate History"}
      </button>

      {/* Error */}
      {error && (
        <div className="text-xs text-[var(--red-base)] bg-[var(--red-bg)] border border-[var(--red-border)] rounded px-3 py-2">
          {error}
        </div>
      )}

      {/* Results */}
      {results && results.length > 0 && (
        <div className="space-y-3">
          {/* Summary */}
          <div className="text-xs font-bold text-[var(--green-base)]">
            Found {allSnapshots.length} snapshot{allSnapshots.length !== 1 ? "s" : ""} across{" "}
            {results.length} source{results.length !== 1 ? "s" : ""}
          </div>

          {/* Per-retailer breakdown */}
          <div className="space-y-1">
            {results.map((r) => {
              const color = RETAILER_COLORS[r.retailer] || "#6b7280";
              const latest = r.snapshots[r.snapshots.length - 1];
              return (
                <div
                  key={r.retailer}
                  className="flex items-center gap-2 py-1.5 border-b border-[var(--bg-tertiary)] last:border-0"
                >
                  <span
                    className="inline-block px-2 py-0.5 text-[10px] font-bold rounded"
                    style={{ backgroundColor: `${color}22`, color }}
                  >
                    {r.retailer}
                  </span>
                  <div className="flex-1 min-w-0">
                    <span className="text-xs font-medium text-[var(--text-primary)]">
                      {r.snapshots.length} snapshot{r.snapshots.length !== 1 ? "s" : ""}
                    </span>
                    <span className="text-[10px] text-[var(--text-tertiary)] ml-2">
                      {formatTimestamp(r.oldest)} &rarr; {formatTimestamp(r.newest)}
                    </span>
                  </div>
                  <a
                    href={latest.archiveUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[10px] font-bold text-[var(--blue-base)] hover:underline shrink-0"
                  >
                    View Latest
                  </a>
                </div>
              );
            })}
          </div>

          {/* Timeline */}
          <details className="group">
            <summary className="text-xs font-bold uppercase tracking-wider text-[var(--text-tertiary)] cursor-pointer hover:text-[var(--text-secondary)]">
              Snapshot Timeline ({allSnapshots.length}){" "}
              <span className="group-open:hidden">+</span>
              <span className="hidden group-open:inline">&minus;</span>
            </summary>
            <div className="mt-2 max-h-60 overflow-y-auto border border-[var(--bg-tertiary)] rounded p-2 space-y-0.5">
              {allSnapshots.slice(0, 50).map((s, i) => (
                <div key={i} className="flex items-center gap-2 py-0.5 text-[11px]">
                  <span className="font-mono font-bold text-[var(--text-primary)] min-w-[70px]">
                    {formatTimestamp(s.timestamp)}
                  </span>
                  <span className="text-[var(--text-tertiary)] flex-1 truncate">
                    {s.retailer}
                  </span>
                  <a
                    href={s.archiveUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-bold text-[var(--blue-base)] hover:underline shrink-0"
                  >
                    View
                  </a>
                </div>
              ))}
              {allSnapshots.length > 50 && (
                <div className="text-[10px] text-[var(--text-tertiary)] pt-1">
                  ...and {allSnapshots.length - 50} more
                </div>
              )}
            </div>
          </details>
        </div>
      )}
    </div>
  );
}
