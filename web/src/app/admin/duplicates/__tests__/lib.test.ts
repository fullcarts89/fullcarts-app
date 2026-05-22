// Pure unit tests for the duplicate-grouping logic. The page route depends
// entirely on findDuplicatePairs being correct — tests lock the contract.
//
// No DB / no React. Tests run via `tsx`; CI just type-checks them through
// tsc --noEmit since there's no jest setup in this repo yet. The
// assertions still belong here because they document the function's
// behaviour for future readers.

import { findDuplicatePairs, findFuzzyDuplicateGroups, slugify } from "../lib";
import type { EntityRow } from "../lib";

function ent(overrides: Partial<EntityRow>): EntityRow {
  return {
    id: "ent-default",
    brand: "Acme",
    canonical_name: "Foo Bar",
    image_url: null,
    category: null,
    created_at: "2024-01-01",
    event_count: 0,
    ...overrides,
  };
}

// ─── slugify ───────────────────────────────────────────────────────────
{
  const cases: Array<[string, string]> = [
    ["Wheat Thins", "wheatthins"],
    ["Wheat-Thins Original", "wheatthinsoriginal"],
    ["  Wheat   Thins  ", "wheatthins"],
    ["Cadbury Dairy Milk (200g)", "cadburydairymilk200g"],
    ["M&M's Plain", "mmsplain"],
    ["", ""],
    ["---", ""],
  ];
  for (const [input, expected] of cases) {
    const actual = slugify(input);
    if (actual !== expected) {
      throw new Error(
        `slugify(${JSON.stringify(input)}) === ${JSON.stringify(actual)}, expected ${JSON.stringify(expected)}`,
      );
    }
  }
}

// ─── findDuplicatePairs ────────────────────────────────────────────────

// 1. Unique entities → no pairs.
{
  const pairs = findDuplicatePairs([
    ent({ id: "a", canonical_name: "Foo" }),
    ent({ id: "b", canonical_name: "Bar" }),
  ]);
  if (pairs.length !== 0) throw new Error(`unique: expected 0 pairs, got ${pairs.length}`);
}

// 2. Exact-duplicate group of 2 → target = higher event_count.
{
  const pairs = findDuplicatePairs([
    ent({ id: "a", canonical_name: "Wheat Thins", event_count: 10 }),
    ent({ id: "b", canonical_name: "Wheat Thins", event_count: 2 }),
  ]);
  if (pairs.length !== 1) throw new Error(`exact: expected 1 pair, got ${pairs.length}`);
  if (pairs[0].target.id !== "a")
    throw new Error(`exact: target should be id=a (higher events), got ${pairs[0].target.id}`);
  if (pairs[0].source.id !== "b")
    throw new Error(`exact: source should be id=b, got ${pairs[0].source.id}`);
}

// 3. Fuzzy-duplicate group of 3 → emits 2 non-target pairs.
{
  const pairs = findDuplicatePairs([
    ent({ id: "a", canonical_name: "Wheat Thins", event_count: 5 }),
    ent({ id: "b", canonical_name: "wheat-thins", event_count: 1 }),
    ent({ id: "c", canonical_name: "WheatThins", event_count: 0 }),
  ]);
  if (pairs.length !== 2) throw new Error(`fuzzy: expected 2 pairs, got ${pairs.length}`);
  if (pairs.some((p) => p.target.id !== "a"))
    throw new Error(`fuzzy: all targets should be id=a`);
}

// 4. Different brands → no merge even on same slug.
{
  const pairs = findDuplicatePairs([
    ent({ id: "a", brand: "Mondelez", canonical_name: "Wheat Thins" }),
    ent({ id: "b", brand: "Nabisco", canonical_name: "Wheat Thins" }),
  ]);
  if (pairs.length !== 0)
    throw new Error(`brand-scoped: expected 0 pairs, got ${pairs.length}`);
}

// 5. Sort: larger groups before smaller; within size, higher target events first.
{
  const pairs = findDuplicatePairs([
    // Pair (size 2)
    ent({ id: "p1", brand: "X", canonical_name: "Pair", event_count: 50 }),
    ent({ id: "p2", brand: "X", canonical_name: "pair", event_count: 1 }),
    // Trio (size 3)
    ent({ id: "t1", brand: "Y", canonical_name: "Trio", event_count: 5 }),
    ent({ id: "t2", brand: "Y", canonical_name: "trio", event_count: 4 }),
    ent({ id: "t3", brand: "Y", canonical_name: "TRIO", event_count: 3 }),
  ]);
  if (pairs.length !== 3) throw new Error(`sort: expected 3 pairs, got ${pairs.length}`);
  if (pairs[0].group_size !== 3 || pairs[1].group_size !== 3)
    throw new Error(`sort: trio pairs should come first`);
  if (pairs[2].group_size !== 2)
    throw new Error(`sort: pair group should come last`);
}

// 6. Deterministic tie-break: equal event_count → smaller id wins target.
{
  const pairs = findDuplicatePairs([
    ent({ id: "zzz", canonical_name: "Tie", event_count: 5 }),
    ent({ id: "aaa", canonical_name: "Tie", event_count: 5 }),
  ]);
  if (pairs[0].target.id !== "aaa")
    throw new Error(`tie-break: target should be id=aaa (lex earlier), got ${pairs[0].target.id}`);
}

// ─── findFuzzyDuplicateGroups — aggressive size-signature tier ─────────

type EventRow = {
  entity_id: string | null;
  size_before: number | null;
  size_after: number | null;
  size_unit: string | null;
};

function ev(
  entity_id: string,
  size_before: number,
  size_after: number,
  size_unit = "g",
): EventRow {
  return { entity_id, size_before, size_after, size_unit };
}

// 1. Gatorade-class: same brand + same size signature + DIVERGENT
//    canonical names ("Bottle" vs "Gatorade Bottle" vs "Sports Drink").
//    Aggressive tier surfaces with has_fuzzy_name_match=false.
{
  const entities = [
    ent({ id: "a", brand: "Gatorade", canonical_name: "Bottle", event_count: 1 }),
    ent({ id: "b", brand: "Gatorade", canonical_name: "Gatorade Bottle", event_count: 1 }),
    ent({ id: "c", brand: "Gatorade", canonical_name: "Sports Drink", event_count: 1 }),
  ];
  const events = [
    ev("a", 32, 28, "fl oz"),
    ev("b", 32, 28, "fl oz"),
    ev("c", 32, 28, "fl oz"),
  ];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 1)
    throw new Error(`gatorade-class: expected 1 group, got ${groups.length}`);
  const g = groups[0];
  if (g.brand !== "Gatorade") throw new Error(`gatorade-class: wrong brand`);
  if (g.size_signature !== "32fl oz→28fl oz")
    throw new Error(`gatorade-class: wrong size_signature: ${g.size_signature}`);
  if (g.has_fuzzy_name_match)
    throw new Error(`gatorade-class: names should diverge → has_fuzzy_name_match=false`);
  if (g.members.length !== 3) throw new Error(`gatorade-class: expected 3 members`);
}

// 2. Convergent-name case: same brand + same size + same fuzzy name key
//    → has_fuzzy_name_match=true. "Glacier Freeze 200g" and
//    "Freeze Glacier" both reduce to "freeze glacier".
{
  const entities = [
    ent({ id: "a", brand: "Gatorade", canonical_name: "Glacier Freeze 200g", event_count: 4 }),
    ent({ id: "b", brand: "Gatorade", canonical_name: "Freeze Glacier", event_count: 1 }),
  ];
  const events = [ev("a", 591, 532, "ml"), ev("b", 591, 532, "ml")];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 1)
    throw new Error(`convergent: expected 1 group, got ${groups.length}`);
  if (!groups[0].has_fuzzy_name_match)
    throw new Error(`convergent: expected has_fuzzy_name_match=true`);
  if (groups[0].size_signature !== "591ml→532ml")
    throw new Error(`convergent: wrong size_signature: ${groups[0].size_signature}`);
}

// 3. Different brands → NEVER grouped (no cross-brand merges).
{
  const entities = [
    ent({ id: "a", brand: "Gatorade", canonical_name: "Sports Drink" }),
    ent({ id: "b", brand: "Powerade", canonical_name: "Sports Drink" }),
  ];
  const events = [ev("a", 32, 28, "fl oz"), ev("b", 32, 28, "fl oz")];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 0)
    throw new Error(`diffbrand: expected 0 groups, got ${groups.length}`);
}

// 4. Same brand + DIFFERENT size signatures → no grouping
//    (the size signature is the cluster key).
{
  const entities = [
    ent({ id: "a", brand: "Gatorade", canonical_name: "Bottle" }),
    ent({ id: "b", brand: "Gatorade", canonical_name: "Bottle" }),
  ];
  const events = [ev("a", 32, 28, "fl oz"), ev("b", 950, 828, "ml")];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 0)
    throw new Error(`diffsize: expected 0 groups (different size signatures), got ${groups.length}`);
}

// 5. Singleton bucket → not flagged.
{
  const entities = [
    ent({ id: "a", brand: "Cadbury", canonical_name: "Dairy Milk" }),
    ent({ id: "b", brand: "Cadbury", canonical_name: "Whole Nut" }),
  ];
  const events = [ev("a", 200, 180), ev("b", 400, 360)];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 0)
    throw new Error(`singleton: expected 0 groups, got ${groups.length}`);
}

// 6. Members sorted by event_count desc; lex id tie-break.
{
  const entities = [
    ent({ id: "a", brand: "Cadbury", canonical_name: "Dairy Milk", event_count: 2 }),
    ent({ id: "b", brand: "Cadbury", canonical_name: "Dairy-Milk 200g", event_count: 9 }),
    ent({ id: "c", brand: "Cadbury", canonical_name: "Milk Dairy", event_count: 5 }),
  ];
  const events = [ev("a", 200, 180), ev("b", 200, 180), ev("c", 200, 180)];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 1)
    throw new Error(`member-sort: expected 1 group, got ${groups.length}`);
  const ids = groups[0].members.map((m) => m.id);
  if (ids[0] !== "b" || ids[1] !== "c" || ids[2] !== "a")
    throw new Error(`member-sort: expected [b,c,a], got ${JSON.stringify(ids)}`);
}

// 7. matched_sizes equals [size_signature] for every member; event_sizes
//    lists ALL signatures the entity carries.
{
  const entities = [
    ent({ id: "a", brand: "Cadbury", canonical_name: "Dairy Milk" }),
    ent({ id: "b", brand: "Cadbury", canonical_name: "milk-dairy" }),
  ];
  // Shared: 200g→180g. Unique to a: 400→360g. Unique to b: 100→90g.
  const events = [
    ev("a", 200, 180),
    ev("a", 400, 360),
    ev("b", 200, 180),
    ev("b", 100, 90),
  ];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 1)
    throw new Error(`size-chips: expected 1 group on shared 200g→180g, got ${groups.length}`);
  const g = groups[0];
  if (g.size_signature !== "200g→180g")
    throw new Error(`size-chips: signature should be 200g→180g, got ${g.size_signature}`);
  const a = g.members.find((m) => m.id === "a");
  const b = g.members.find((m) => m.id === "b");
  if (!a || !b) throw new Error(`size-chips: missing members`);
  if (a.matched_sizes.length !== 1 || a.matched_sizes[0] !== "200g→180g")
    throw new Error(
      `size-chips: a.matched_sizes should be [200g→180g], got ${JSON.stringify(a.matched_sizes)}`,
    );
  if (a.event_sizes.length !== 2)
    throw new Error(`size-chips: a should have 2 event_sizes, got ${a.event_sizes.length}`);
  if (b.event_sizes.length !== 2)
    throw new Error(`size-chips: b should have 2 event_sizes, got ${b.event_sizes.length}`);
}

// 8. Entity with 2 distinct shared signatures appears in 2 groups.
//    "Gatorade Sports Drink" has BOTH 32→28 fl oz AND 20→16.9 fl oz;
//    matched by "Gatorade Bottle" (32→28) and "Gatorade Fit" (20→16.9).
{
  const entities = [
    ent({ id: "sd", brand: "Gatorade", canonical_name: "Gatorade Sports Drink" }),
    ent({ id: "bt", brand: "Gatorade", canonical_name: "Gatorade Bottle" }),
    ent({ id: "ft", brand: "Gatorade", canonical_name: "Gatorade Fit" }),
  ];
  const events = [
    ev("sd", 32, 28, "fl oz"),
    ev("sd", 20, 16.9, "fl oz"),
    ev("bt", 32, 28, "fl oz"),
    ev("ft", 20, 16.9, "fl oz"),
  ];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 2)
    throw new Error(`multi-group: expected 2 groups (one per signature), got ${groups.length}`);
  const sigs = groups.map((g) => g.size_signature).sort();
  if (!sigs.includes("32fl oz→28fl oz") || !sigs.includes("20fl oz→16.9fl oz"))
    throw new Error(`multi-group: signatures wrong: ${JSON.stringify(sigs)}`);
  // sd appears in both groups
  const sdInGroups = groups.filter((g) => g.members.some((m) => m.id === "sd")).length;
  if (sdInGroups !== 2)
    throw new Error(`multi-group: sd should appear in 2 groups, got ${sdInGroups}`);
}

// 9. Result ordering: name-match groups float above name-diverge groups.
//    Within tier: larger member count first.
{
  const entities = [
    // Diverge group (3 entities): Gatorade 32→28 fl oz (names don't fuzzy-match)
    ent({ id: "d1", brand: "Gatorade", canonical_name: "Bottle" }),
    ent({ id: "d2", brand: "Gatorade", canonical_name: "Gatorade Beverage" }),
    ent({ id: "d3", brand: "Gatorade", canonical_name: "Sports Drink" }),
    // Match group (2 entities): Cadbury 200→180 g (names DO fuzzy-match)
    ent({ id: "m1", brand: "Cadbury", canonical_name: "Dairy Milk" }),
    ent({ id: "m2", brand: "Cadbury", canonical_name: "dairy-milk 200g" }),
  ];
  const events = [
    ev("d1", 32, 28, "fl oz"),
    ev("d2", 32, 28, "fl oz"),
    ev("d3", 32, 28, "fl oz"),
    ev("m1", 200, 180),
    ev("m2", 200, 180),
  ];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 2)
    throw new Error(`tier-sort: expected 2 groups, got ${groups.length}`);
  if (!groups[0].has_fuzzy_name_match || groups[1].has_fuzzy_name_match)
    throw new Error(`tier-sort: name-match group must come first`);
  if (groups[0].brand !== "Cadbury")
    throw new Error(`tier-sort: first group should be Cadbury (name-match), got ${groups[0].brand}`);
}

// 10. Member-count sort within same tier.
{
  const entities = [
    // Trio name-match (Cadbury Dairy Milk × 3)
    ent({ id: "t1", brand: "Cadbury", canonical_name: "Dairy Milk" }),
    ent({ id: "t2", brand: "Cadbury", canonical_name: "Dairy-Milk 200g" }),
    ent({ id: "t3", brand: "Cadbury", canonical_name: "Milk Dairy" }),
    // Pair name-match (Galaxy Smooth Milk × 2)
    ent({ id: "p1", brand: "Galaxy", canonical_name: "Smooth Milk" }),
    ent({ id: "p2", brand: "Galaxy", canonical_name: "smooth-milk 110g" }),
  ];
  const events = [
    ev("t1", 200, 180),
    ev("t2", 200, 180),
    ev("t3", 200, 180),
    ev("p1", 110, 100),
    ev("p2", 110, 100),
  ];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 2)
    throw new Error(`size-sort: expected 2 groups, got ${groups.length}`);
  if (groups[0].members.length !== 3)
    throw new Error(`size-sort: trio should come first`);
  if (groups[1].members.length !== 2)
    throw new Error(`size-sort: pair should come second`);
}

// 11. Events with missing entity_id / null sizes are skipped silently.
{
  const entities = [
    ent({ id: "a", brand: "Cadbury", canonical_name: "Dairy Milk" }),
    ent({ id: "b", brand: "Cadbury", canonical_name: "dairy milk" }),
  ];
  const events: EventRow[] = [
    { entity_id: null, size_before: 200, size_after: 180, size_unit: "g" }, // skip
    { entity_id: "a", size_before: null, size_after: 180, size_unit: "g" }, // skip
    { entity_id: "a", size_before: 200, size_after: null, size_unit: "g" }, // skip
    ev("a", 200, 180),
    ev("b", 200, 180),
  ];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 1)
    throw new Error(`null-skip: expected 1 group, got ${groups.length}`);
  // Each member's event_sizes should contain exactly the one valid event.
  if (groups[0].members[0].event_sizes.length !== 1)
    throw new Error(`null-skip: bad event_sizes count`);
}

console.log("admin/duplicates/lib: 17 assertions passed");
