// Pure unit tests for the grouping helpers. Pattern matches
// web/src/app/admin/duplicates/__tests__/lib.test.ts — assertions in
// top-level blocks, run via `tsx`, type-checked via `tsc --noEmit`.

import { normalizeBrand, fuzzyNameKey, sizeBucket } from "../lib";

let failed = 0;
function expect(label: string, got: unknown, want: unknown): void {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (!ok) {
    failed++;
    console.error(`FAIL  ${label}\n  got:  ${JSON.stringify(got)}\n  want: ${JSON.stringify(want)}`);
  } else {
    console.log(`PASS  ${label}`);
  }
}

// ─── normalizeBrand ───
expect("brand lowercased", normalizeBrand("Cadbury"), "cadbury");
expect("brand trimmed", normalizeBrand("  Cadbury  "), "cadbury");
expect("brand strips ' plc'", normalizeBrand("Mondelez plc"), "mondelez");
expect("brand strips ' inc'", normalizeBrand("Kroger Inc"), "kroger");
expect("brand strips ' ltd'", normalizeBrand("Some Co Ltd."), "some co");
expect("brand handles null", normalizeBrand(null), "");
expect("brand collapses internal spaces", normalizeBrand("Cadbury  UK"), "cadbury uk");

// ─── fuzzyNameKey ───
expect("name lowercased + sorted tokens", fuzzyNameKey("Dairy Milk"), "dairy milk");
expect("name token-sort", fuzzyNameKey("Milk Dairy"), "dairy milk");
expect("name strips size+unit", fuzzyNameKey("Dairy Milk 200g"), "dairy milk");
expect("name strips multipack", fuzzyNameKey("Dairy Milk 6x40g"), "dairy milk");
expect("name strips punctuation", fuzzyNameKey("Dairy-Milk, Original!"), "dairy milk original");
expect("name handles null", fuzzyNameKey(null), "");

// ─── sizeBucket ───
expect("size bucket basic", sizeBucket(200, 180, "g"), "200g→180g");
expect("size bucket normalizes unit case", sizeBucket(200, 180, "G"), "200g→180g");
expect("size bucket strips trailing zeros", sizeBucket(200.0, 180.0, "g"), "200g→180g");
expect("size bucket handles ml", sizeBucket(500, 450, "ml"), "500ml→450ml");
expect("size bucket handles missing values", sizeBucket(null, 180, "g"), "?→180g");
expect("size bucket both null", sizeBucket(null, null, null), "?→?");

if (failed > 0) {
  console.error(`\n${failed} assertion(s) failed`);
  process.exit(1);
}
console.log(`\nAll assertions passed`);
