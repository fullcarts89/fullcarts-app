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
