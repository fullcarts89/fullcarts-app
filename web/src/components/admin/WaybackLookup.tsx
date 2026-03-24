"use client";

import { useState, useCallback } from "react";

// ── Types ───────────────────────────────────────────────────────────────────

type ExtractionResult = {
  timestamp: string;
  retailer: string;
  archiveUrl: string;
  sourceUrl: string;
  size: number | null;
  unit: string | null;
  method: string | null;
};

type SizeChange = {
  from: ExtractionResult;
  to: ExtractionResult;
  oldSize: string;
  newSize: string;
  changePercent: number;
};

// ── Helpers ─────────────────────────────────────────────────────────────────

function formatTimestamp(ts: string): string {
  if (ts.length >= 8) return `${ts.slice(0, 4)}-${ts.slice(4, 6)}-${ts.slice(6, 8)}`;
  return ts;
}

function formatSize(size: number | null, unit: string | null): string {
  if (size === null || unit === null) return "—";
  return `${size} ${unit}`;
}

function detectSizeChanges(results: ExtractionResult[]): SizeChange[] {
  // Group by sourceUrl (each URL = one SKU) to avoid cross-SKU false positives
  const byUrl: Record<string, ExtractionResult[]> = {};
  for (const r of results) {
    if (r.size === null || r.unit === null) continue;
    const key = r.sourceUrl || "unknown";
    if (!byUrl[key]) byUrl[key] = [];
    byUrl[key].push(r);
  }

  const changes: SizeChange[] = [];

  for (const [, group] of Object.entries(byUrl)) {
    // Sort by date within the same SKU
    group.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
    if (group.length < 2) continue;

    for (let i = 1; i < group.length; i++) {
      const prev = group[i - 1];
      const curr = group[i];
      // Only compare same unit for meaningful changes
      if (prev.unit !== curr.unit) continue;
      if (prev.size === curr.size) continue;

      const pct = ((curr.size! - prev.size!) / prev.size!) * 100;
      changes.push({
        from: prev,
        to: curr,
        oldSize: formatSize(prev.size, prev.unit),
        newSize: formatSize(curr.size, curr.unit),
        changePercent: pct,
      });
    }
  }

  return changes;
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

// ── Component ───────────────────────────────────────────────────────────────

export function WaybackLookup({
  productName,
  brand,
  sourceUrl,
  upc,
  claimOldSize,
  claimOldUnit,
}: {
  productName: string;
  brand: string;
  sourceUrl: string | null;
  upc?: string | null;
  claimOldSize?: number | null;
  claimOldUnit?: string | null;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [customUrl, setCustomUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0, retailer: "", timestamp: "" });
  const [results, setResults] = useState<ExtractionResult[]>([]);
  const [sizeChanges, setSizeChanges] = useState<SizeChange[]>([]);
  const [error, setError] = useState<string | null>(null);

  const runLookup = useCallback(async () => {
    setLoading(true);
    setExtracting(false);
    setError(null);
    setResults([]);
    setSizeChanges([]);
    setProgress({ current: 0, total: 0, retailer: "", timestamp: "" });

    try {
      // ── Server-side discovery + extraction via SSE ────────────────
      // Let the server handle CDX discovery (with retailer-specific URL
      // patterns) and extraction in a single SSE stream.  This avoids
      // duplicating CDX queries client-side and ensures we get modern,
      // extractable snapshots.
      setExtracting(true);

      const resp = await fetch("/api/admin/wayback-extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          productName,
          brand,
          customUrl: customUrl.trim() || undefined,
          upc: upc || undefined,
          claimOldSize: claimOldSize || undefined,
          claimOldUnit: claimOldUnit || undefined,
          maxPerRetailer: 5,
        }),
      });

      if (!resp.ok) {
        throw new Error(`API returned ${resp.status}`);
      }

      // Read SSE stream
      const reader = resp.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";
      const accumulatedResults: ExtractionResult[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const event = JSON.parse(line.slice(6));

            if (event.type === "progress") {
              setProgress({
                current: event.index || 0,
                total: event.total || 0,
                retailer: event.retailer || "",
                timestamp: event.timestamp || "",
              });
            } else if (event.type === "result" || event.type === "cached") {
              const r: ExtractionResult = {
                timestamp: event.timestamp,
                retailer: event.retailer,
                archiveUrl: event.archiveUrl,
                sourceUrl: event.sourceUrl,
                size: event.size,
                unit: event.unit,
                method: event.method,
              };
              accumulatedResults.push(r);
              setResults([...accumulatedResults]);
              setSizeChanges(detectSizeChanges([...accumulatedResults]));
              setProgress({
                current: event.index || 0,
                total: event.total || 0,
                retailer: event.retailer || "",
                timestamp: event.timestamp || "",
              });
            } else if (event.type === "error" && event.error && !event.index) {
              // Global error
              setError(event.error);
            } else if (event.type === "done") {
              if (event.results) {
                setResults(event.results);
                setSizeChanges(detectSizeChanges(event.results));
              }
            }
          } catch {
            // Skip malformed SSE events
          }
        }
      }

      if (accumulatedResults.length === 0) {
        setError("No archived snapshots found. Try pasting a specific product page URL.");
      }
    } catch (e) {
      setError(`Lookup failed: ${e instanceof Error ? e.message : "Unknown error"}`);
    } finally {
      setLoading(false);
      setExtracting(false);
    }
  }, [customUrl, sourceUrl, productName, brand]);

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

  const isWorking = loading || extracting;
  const progressPercent =
    progress.total > 0 ? Math.round((progress.current / progress.total) * 100) : 0;
  const resultsWithSize = results.filter((r) => r.size !== null);

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
        Search the Internet Archive for historical snapshots and auto-extract product sizes.
      </p>

      {/* Custom URL input */}
      <div>
        <label className="block text-xs text-[var(--text-tertiary)] mb-1">
          Product page URL (optional — auto-searches retailers by name)
        </label>
        <input
          type="url"
          value={customUrl}
          onChange={(e) => setCustomUrl(e.target.value)}
          placeholder="https://www.walmart.com/ip/Product-Name/123456"
          className="w-full px-2 py-1.5 text-sm rounded border border-[var(--bg-tertiary)] bg-[var(--bg-primary)] text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:border-purple-500/50"
          disabled={isWorking}
        />
      </div>

      {/* Run button */}
      <button
        onClick={runLookup}
        disabled={isWorking}
        className="w-full px-3 py-2 text-sm font-medium rounded border border-purple-500/30 bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 transition-all disabled:opacity-50"
      >
        {isWorking ? "Investigating..." : "Investigate History"}
      </button>

      {/* Progress bar */}
      {isWorking && progress.total > 0 && (
        <div className="space-y-1">
          <div className="flex items-center justify-between text-[10px] text-[var(--text-tertiary)]">
            <span>
              Extracting {progress.current}/{progress.total}
              {progress.retailer ? ` — ${progress.retailer}` : ""}
            </span>
            <span>{progressPercent}%</span>
          </div>
          <div className="w-full h-1.5 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
            <div
              className="h-full bg-purple-500 rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          {progress.timestamp && (
            <div className="text-[10px] text-[var(--text-tertiary)]">
              Snapshot: {formatTimestamp(progress.timestamp)}
            </div>
          )}
        </div>
      )}

      {isWorking && progress.total === 0 && (
        <div className="text-xs text-[var(--text-tertiary)] animate-pulse">
          Searching Internet Archive for snapshots...
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="text-xs text-[var(--red-base)] bg-[var(--red-bg)] border border-[var(--red-border)] rounded px-3 py-2">
          {error}
        </div>
      )}

      {/* Size Changes — the headline finding */}
      {sizeChanges.length > 0 && (
        <div className="space-y-2">
          <h5 className="text-xs font-bold uppercase tracking-wider text-[var(--amber-base)]">
            Size Changes Detected ({sizeChanges.length})
          </h5>
          <div className="space-y-1">
            {sizeChanges.map((c, i) => {
              const isShrink = c.changePercent < 0;
              const color = isShrink
                ? "text-[var(--red-base)]"
                : "text-[var(--green-base)]";
              return (
                <div
                  key={i}
                  className="flex items-center gap-2 py-1.5 px-2 rounded bg-[var(--bg-secondary)] border border-[var(--bg-tertiary)]"
                >
                  <span className="text-[10px] text-[var(--text-tertiary)] font-mono min-w-[70px]">
                    {formatTimestamp(c.from.timestamp)}
                  </span>
                  <span className="text-xs font-mono font-bold text-[var(--text-primary)]">
                    {c.oldSize}
                  </span>
                  <span className="text-[var(--text-tertiary)]">&rarr;</span>
                  <span className={`text-xs font-mono font-bold ${color}`}>
                    {c.newSize}
                  </span>
                  <span className={`text-[10px] font-bold ${color}`}>
                    ({c.changePercent > 0 ? "+" : ""}
                    {c.changePercent.toFixed(1)}%)
                  </span>
                  <span className="text-[10px] text-[var(--text-tertiary)] ml-auto">
                    {c.to.retailer} &middot; {formatTimestamp(c.to.timestamp)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Extraction Results Timeline */}
      {results.length > 0 && (
        <div className="space-y-2">
          <h5 className="text-xs font-bold uppercase tracking-wider text-[var(--text-tertiary)]">
            Extracted Sizes ({resultsWithSize.length}/{results.length} snapshots)
          </h5>
          <div className="max-h-60 overflow-y-auto border border-[var(--bg-tertiary)] rounded p-2 space-y-0.5">
            {results
              .sort((a, b) => a.timestamp.localeCompare(b.timestamp))
              .map((r, i) => {
                const color = RETAILER_COLORS[r.retailer] || "#6b7280";
                // Detect if this row represents a change from the previous same-URL result
                const prevSameUrl = results
                  .filter(
                    (x) =>
                      x.sourceUrl === r.sourceUrl &&
                      x.timestamp < r.timestamp &&
                      x.size !== null &&
                      x.unit === r.unit,
                  )
                  .sort((a, b) => b.timestamp.localeCompare(a.timestamp))[0];
                const isChange =
                  r.size !== null &&
                  prevSameUrl &&
                  prevSameUrl.size !== r.size;

                return (
                  <div
                    key={i}
                    className={`flex items-center gap-2 py-1 text-[11px] rounded px-1 ${
                      isChange
                        ? "bg-[var(--amber-bg)] border border-[var(--amber-base)]/20"
                        : ""
                    }`}
                  >
                    <span className="font-mono font-bold text-[var(--text-primary)] min-w-[70px]">
                      {formatTimestamp(r.timestamp)}
                    </span>
                    <span
                      className="inline-block px-1.5 py-0.5 text-[9px] font-bold rounded min-w-[60px] text-center"
                      style={{ backgroundColor: `${color}22`, color }}
                    >
                      {r.retailer}
                    </span>
                    <span
                      className={`font-mono font-bold min-w-[60px] ${
                        r.size !== null
                          ? isChange
                            ? "text-[var(--amber-base)]"
                            : "text-[var(--green-base)]"
                          : "text-[var(--text-tertiary)]"
                      }`}
                    >
                      {formatSize(r.size, r.unit)}
                    </span>
                    {r.method && (
                      <span className="text-[9px] text-[var(--text-tertiary)] truncate">
                        via {r.method}
                      </span>
                    )}
                    <a
                      href={r.archiveUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-bold text-[var(--blue-base)] hover:underline shrink-0 ml-auto"
                    >
                      View
                    </a>
                  </div>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
}
