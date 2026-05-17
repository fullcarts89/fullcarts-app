"use client";

const CONFIDENCE_TIERS = [
  { key: "all", label: "All confidence" },
  { key: "high", label: "80%+" },
  { key: "mid", label: "60–79%" },
  { key: "low", label: "40–59%" },
  { key: "weak", label: "Under 40%" },
];

const CATEGORIES = [
  "snacks", "candy", "beverages", "chips", "fast food", "condiments",
  "cookies", "household", "bread", "meat", "cereal", "personal care",
  "dairy", "crackers", "pasta", "ice cream", "produce", "canned goods",
  "baking", "pet", "medicine", "coffee", "frozen meals", "yogurt", "other",
];

// Each option is (filter value, display label). The filter value is the
// raw_items.source_type (or a comma-joined set, e.g. "kroger_api,kroger_change").
const SOURCES: ReadonlyArray<{ value: string; label: string }> = [
  { value: "", label: "All sources" },
  { value: "reddit", label: "Reddit" },
  { value: "news", label: "News" },
  { value: "gdelt", label: "GDELT" },
  { value: "openfoodfacts", label: "Open Food Facts" },
  { value: "usda_size_change", label: "USDA" },
  { value: "kroger_change", label: "Kroger" },
];

function navigate(status: string, conf: string, category: string, source: string) {
  const parts = [`status=${status}`, "page=1"];
  if (conf && conf !== "all") parts.push(`conf=${conf}`);
  if (category) parts.push(`category=${category}`);
  if (source) parts.push(`source=${encodeURIComponent(source)}`);
  window.location.href = `/admin/claims?${parts.join("&")}`;
}

export function ClaimFilters({
  status,
  conf,
  category,
  source,
}: {
  status: string;
  conf: string;
  category: string;
  source: string;
}) {
  const selectClass =
    "bg-[var(--bg-primary)] text-[var(--text-primary)] border border-[var(--bg-tertiary)] rounded-md px-3 py-1.5 text-sm focus:outline-none focus:border-[var(--text-tertiary)] transition-colors";

  return (
    <div className="flex gap-3 flex-wrap">
      <select
        value={source}
        onChange={(e) => navigate(status, conf, category, e.target.value)}
        className={selectClass}
      >
        {SOURCES.map((s) => (
          <option key={s.value} value={s.value}>
            {s.label}
          </option>
        ))}
      </select>
      <select
        value={conf}
        onChange={(e) => navigate(status, e.target.value, category, source)}
        className={selectClass}
      >
        {CONFIDENCE_TIERS.map((t) => (
          <option key={t.key} value={t.key}>
            {t.label}
          </option>
        ))}
      </select>
      <select
        value={category}
        onChange={(e) => navigate(status, conf, e.target.value, source)}
        className={selectClass}
      >
        <option value="">All categories</option>
        {CATEGORIES.map((cat) => (
          <option key={cat} value={cat}>
            {cat}
          </option>
        ))}
      </select>
    </div>
  );
}
