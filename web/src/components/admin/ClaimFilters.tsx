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

function navigate(status: string, conf: string, category: string) {
  const parts = [`status=${status}`, "page=1"];
  if (conf && conf !== "all") parts.push(`conf=${conf}`);
  if (category) parts.push(`category=${category}`);
  window.location.href = `/admin/claims?${parts.join("&")}`;
}

export function ClaimFilters({
  status,
  conf,
  category,
}: {
  status: string;
  conf: string;
  category: string;
}) {
  const selectClass =
    "bg-[var(--bg-primary)] text-[var(--text-primary)] border border-[var(--bg-tertiary)] rounded-md px-3 py-1.5 text-sm focus:outline-none focus:border-[var(--text-tertiary)] transition-colors";

  return (
    <div className="flex gap-3 flex-wrap">
      <select
        value={conf}
        onChange={(e) => navigate(status, e.target.value, category)}
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
        onChange={(e) => navigate(status, conf, e.target.value)}
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
