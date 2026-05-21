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

// ─── findFuzzyDuplicateGroups ──────────────────────────────────────────

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

// 1. Same brand + same fuzzy name key + shared size → forms a group
//    with has_size_overlap=true.
//    Note: fuzzyNameKey is token-sort + strip size/unit/punct, so
//    "Glacier Freeze 200g" and "Freeze Glacier" both reduce to
//    "freeze glacier".
{
  const entities = [
    ent({ id: "a", brand: "Gatorade", canonical_name: "Glacier Freeze 200g", event_count: 4 }),
    ent({ id: "b", brand: "Gatorade", canonical_name: "Freeze Glacier", event_count: 1 }),
  ];
  const events = [ev("a", 200, 180), ev("b", 200, 180)];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 1) throw new Error(`fuzzy/share: expected 1 group, got ${groups.length}`);
  const g = groups[0];
  if (g.brand !== "Gatorade") throw new Error(`fuzzy/share: brand should be Gatorade`);
  if (!g.has_size_overlap) throw new Error(`fuzzy/share: expected has_size_overlap=true`);
  if (g.members.length !== 2) throw new Error(`fuzzy/share: expected 2 members`);
  if (!g.members[0].matched_sizes.includes("200g→180g"))
    throw new Error(`fuzzy/share: expected matched size 200g→180g, got ${JSON.stringify(g.members[0].matched_sizes)}`);
}

// 2. Same brand + same fuzzy name but NO size overlap → STILL flagged
//    (Medium tier), but has_size_overlap=false and matched_sizes empty.
{
  const entities = [
    ent({ id: "a", brand: "Gatorade", canonical_name: "Glacier Freeze" }),
    ent({ id: "b", brand: "Gatorade", canonical_name: "Freeze Glacier" }),
  ];
  const events = [ev("a", 200, 180), ev("b", 591, 532)];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 1)
    throw new Error(`fuzzy/nooverlap: expected 1 group (Medium tier surfaces), got ${groups.length}`);
  if (groups[0].has_size_overlap)
    throw new Error(`fuzzy/nooverlap: expected has_size_overlap=false`);
  if (groups[0].members[0].matched_sizes.length !== 0)
    throw new Error(`fuzzy/nooverlap: expected matched_sizes to be empty`);
}

// 2b. Sort: size-overlap groups float above no-overlap groups.
{
  const entities = [
    // Group α: no overlap
    ent({ id: "a1", brand: "Acme", canonical_name: "Foo Bar" }),
    ent({ id: "a2", brand: "Acme", canonical_name: "Bar Foo" }),
    // Group β: overlap
    ent({ id: "b1", brand: "Beta", canonical_name: "Wibble" }),
    ent({ id: "b2", brand: "Beta", canonical_name: "wibble" }),
  ];
  const events = [
    ev("a1", 100, 90),
    ev("a2", 200, 180), // different size — no overlap in group α
    ev("b1", 50, 40),
    ev("b2", 50, 40), // overlap in group β
  ];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 2)
    throw new Error(`fuzzy/sort-tier: expected 2 groups, got ${groups.length}`);
  if (!groups[0].has_size_overlap || groups[1].has_size_overlap)
    throw new Error(`fuzzy/sort-tier: size-overlap group must come first`);
}

// 3. Same brand + different fuzzy names → not flagged even with same size event.
{
  const entities = [
    ent({ id: "a", brand: "Gatorade", canonical_name: "Glacier Freeze" }),
    ent({ id: "b", brand: "Gatorade", canonical_name: "Lemon Lime" }),
  ];
  const events = [ev("a", 200, 180), ev("b", 200, 180)];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 0)
    throw new Error(`fuzzy/diffname: expected 0 groups, got ${groups.length}`);
}

// 4. Different brands → never flagged even if name + size align.
{
  const entities = [
    ent({ id: "a", brand: "Gatorade", canonical_name: "Glacier Freeze" }),
    ent({ id: "b", brand: "Powerade", canonical_name: "Glacier Freeze" }),
  ];
  const events = [ev("a", 200, 180), ev("b", 200, 180)];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 0)
    throw new Error(`fuzzy/diffbrand: expected 0 groups, got ${groups.length}`);
}

// 5. Members sorted by event_count descending (target = members[0]).
//    All three variants reduce to "dairy milk" under token-sort + size strip.
{
  const entities = [
    ent({ id: "a", brand: "Cadbury", canonical_name: "Dairy Milk", event_count: 2 }),
    ent({ id: "b", brand: "Cadbury", canonical_name: "Dairy-Milk 200g", event_count: 9 }),
    ent({ id: "c", brand: "Cadbury", canonical_name: "Milk Dairy", event_count: 5 }),
  ];
  const events = [ev("a", 200, 180), ev("b", 200, 180), ev("c", 200, 180)];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 1)
    throw new Error(`fuzzy/sort: expected 1 group, got ${groups.length}`);
  const ids = groups[0].members.map((m) => m.id);
  if (ids[0] !== "b" || ids[1] !== "c" || ids[2] !== "a")
    throw new Error(`fuzzy/sort: expected [b,c,a], got ${JSON.stringify(ids)}`);
}

// 6. matched_sizes only includes sizes shared with ≥1 other member.
//    event_sizes lists ALL of the entity's signatures, matched or not.
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
    throw new Error(`fuzzy/matched: expected 1 group, got ${groups.length}`);
  const a = groups[0].members.find((m) => m.id === "a");
  const b = groups[0].members.find((m) => m.id === "b");
  if (!a || !b) throw new Error(`fuzzy/matched: missing members`);
  if (a.matched_sizes.length !== 1 || a.matched_sizes[0] !== "200g→180g")
    throw new Error(
      `fuzzy/matched: a.matched should be [200g→180g], got ${JSON.stringify(a.matched_sizes)}`,
    );
  if (b.matched_sizes.length !== 1 || b.matched_sizes[0] !== "200g→180g")
    throw new Error(
      `fuzzy/matched: b.matched should be [200g→180g], got ${JSON.stringify(b.matched_sizes)}`,
    );
  if (a.event_sizes.length !== 2)
    throw new Error(`fuzzy/matched: a should have 2 event_sizes, got ${a.event_sizes.length}`);
  if (b.event_sizes.length !== 2)
    throw new Error(`fuzzy/matched: b should have 2 event_sizes, got ${b.event_sizes.length}`);
}

// 7. Singleton bucket (only 1 entity matching fuzzy key) → not flagged.
{
  const entities = [
    ent({ id: "a", brand: "Cadbury", canonical_name: "Dairy Milk" }),
    ent({ id: "b", brand: "Cadbury", canonical_name: "Whole Nut" }),
  ];
  const events = [ev("a", 200, 180), ev("b", 200, 180)];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 0)
    throw new Error(`fuzzy/singleton: expected 0 groups, got ${groups.length}`);
}

// 8. Result ordering: groups with more members come first.
//    All names within a group must reduce to the same fuzzy key.
{
  const entities = [
    // Pair group (Cadbury Dairy Milk × 2)
    ent({ id: "p1", brand: "Cadbury", canonical_name: "Dairy Milk", event_count: 3 }),
    ent({ id: "p2", brand: "Cadbury", canonical_name: "milk-dairy 200g", event_count: 1 }),
    // Trio group (Gatorade Glacier Freeze × 3)
    ent({ id: "t1", brand: "Gatorade", canonical_name: "Glacier Freeze", event_count: 2 }),
    ent({ id: "t2", brand: "Gatorade", canonical_name: "Freeze-Glacier", event_count: 1 }),
    ent({ id: "t3", brand: "Gatorade", canonical_name: "Freeze Glacier 591ml", event_count: 1 }),
  ];
  const events = [
    ev("p1", 200, 180),
    ev("p2", 200, 180),
    ev("t1", 591, 532, "ml"),
    ev("t2", 591, 532, "ml"),
    ev("t3", 591, 532, "ml"),
  ];
  const groups = findFuzzyDuplicateGroups(entities, events);
  if (groups.length !== 2)
    throw new Error(`fuzzy/order: expected 2 groups, got ${groups.length}`);
  if (groups[0].members.length !== 3)
    throw new Error(`fuzzy/order: first group should have 3 members`);
  if (groups[1].members.length !== 2)
    throw new Error(`fuzzy/order: second group should have 2 members`);
}

console.log("admin/duplicates/lib: 14 assertions passed");
