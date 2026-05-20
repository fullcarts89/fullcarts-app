// Pure unit tests for the duplicate-grouping logic. The page route depends
// entirely on findDuplicatePairs being correct — tests lock the contract.
//
// No DB / no React. Tests run via `tsx`; CI just type-checks them through
// tsc --noEmit since there's no jest setup in this repo yet. The
// assertions still belong here because they document the function's
// behaviour for future readers.

import { findDuplicatePairs, slugify } from "../lib";
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

console.log("admin/duplicates/lib: 6 assertions passed");
