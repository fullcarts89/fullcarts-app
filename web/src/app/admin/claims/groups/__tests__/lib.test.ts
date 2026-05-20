// Pure unit tests for the grouping helpers. Pattern matches
// web/src/app/admin/duplicates/__tests__/lib.test.ts — assertions in
// top-level blocks, run via `tsx`, type-checked via `tsc --noEmit`.

import { normalizeBrand, fuzzyNameKey, sizeBucket, groupPendingClaims } from "../lib";
import type { PendingClaim } from "../lib";

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

function mk(overrides: Partial<PendingClaim>): PendingClaim {
  return {
    id: `c-${Math.random()}`,
    brand: "Cadbury",
    product_name: "Dairy Milk",
    old_size: 200,
    new_size: 180,
    size_unit: "g",
    confidence_overall: 0.9,
    matched_entity_id: null,
    source_type: "reddit",
    image_storage_path: null,
    raw_payload_title: null,
    raw_item_url: null,
    ...overrides,
  };
}

// ─── groupPendingClaims ───
{
  const groups = groupPendingClaims([
    mk({ id: "a" }),
    mk({ id: "b", brand: "Cadbury Ltd" }),      // same brand once corporate suffix stripped
    mk({ id: "c", product_name: "Milk Dairy" }), // same name once token-sorted
    mk({ id: "d", brand: "Mondelez" }),          // different brand
  ]);
  expect("3 cadbury + 1 mondelez = 2 groups", groups.length, 2);
  expect("biggest group first", groups[0].claims.length, 3);
  expect("group key is canonical", groups[0].brand, "cadbury");
  expect("group size bucket", groups[0].size_change, "200g→180g");
}

// matched_entity_id sub-clusters within a group
{
  const groups = groupPendingClaims([
    mk({ id: "a", matched_entity_id: "ent-1" }),
    mk({ id: "b", matched_entity_id: "ent-1" }),
    mk({ id: "c", matched_entity_id: "ent-2" }),
    mk({ id: "d", matched_entity_id: null }),
  ]);
  expect("1 outer group", groups.length, 1);
  expect("3 sub-clusters", groups[0].sub_clusters.length, 3);
  expect("largest sub-cluster first", groups[0].sub_clusters[0].claims.length, 2);
}

if (failed > 0) {
  console.error(`\n${failed} assertion(s) failed`);
  process.exit(1);
}
console.log(`\nAll assertions passed`);
