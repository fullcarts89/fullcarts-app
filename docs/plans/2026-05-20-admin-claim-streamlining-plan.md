# Phase A — Admin claim-grouping + zero-event entity cleanup — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a bulk-review admin tool that turns the 2,527-claim pending queue into a tractable workflow, then sweep ~18,566 orphaned (zero-event) entities, and finally install a forward invariant so this class of bug can't return.

**Architecture:**
- Deliverable 1 (`/admin/claims/groups`): Next.js App Router server component that loads all pending claims, groups them in-memory by `(normalized_brand, fuzzy_name_key, size_bucket)`, renders one card per group. Selection + bulk actions in a small client component that POSTs to new `/api/admin/bulk-*` API routes. Pattern mirrors existing `/admin/duplicates` (PR #91).
- Deliverable 2 (`retract_zero_event_entities.py`): Idempotent Python script that finds entities with no live events, calls the existing `set_entity_retracted` RPC (migration 062), records each action in `data_quality_flags` (migration 063) for audit.
- Deliverable 3 (migration 069 + page guards): `AFTER UPDATE` Postgres trigger on `published_changes.is_retracted` that auto-retracts the parent entity if no other live events remain. Belt-and-braces `notFound()` guards on `/products/[id]` and `/brands/[name]` so the page layer also fails closed.

**Tech Stack:** Next.js 16 (App Router, React 19, server components), TypeScript 5, Tailwind CSS 4, Supabase (PostgREST + service-role admin client), Python 3.9 (target — never use `X | Y` or lowercase generics), pytest for pipeline tests, `tsx` runtime + `tsc --noEmit` for web unit tests, Vercel for deploys, Supabase Management API for migrations.

**Source of truth:** [docs/plans/2026-05-20-admin-claim-streamlining-design.md](./2026-05-20-admin-claim-streamlining-design.md)

---

## Pre-flight (T0)

**What this does in plain English:** Make sure we're on a clean branch with all the credentials we need, before touching code.

**Step 1:** Verify working tree is clean and we're on the worktree branch.
```bash
git status
git rev-parse --abbrev-ref HEAD
```
Expected: clean tree, on branch `claude/jovial-cerf-6bb9cc` (or similar worktree branch).

**Step 2:** Verify env vars are loadable from `web/.env.local`.
```bash
grep -E '^(SUPABASE_URL|SUPABASE_SERVICE_ROLE_KEY|NEXT_PUBLIC_SUPABASE_URL)' web/.env.local | wc -l
```
Expected: `3`.

**Step 3:** Verify Supabase admin RPC is reachable.
```bash
SUP_KEY=$(grep SUPABASE_SERVICE_ROLE_KEY web/.env.local | cut -d= -f2)
curl -sI "https://ntyhbapphnzlariakgrw.supabase.co/rest/v1/claims?status=eq.pending&select=id" \
  -H "apikey: $SUP_KEY" -H "Authorization: Bearer $SUP_KEY" \
  -H "Prefer: count=exact" -H "Range: 0-0" | grep -i content-range
```
Expected: `content-range: 0-999/<NNNN>` where `NNNN` ≈ 2,527.

**Step 4:** Confirm `web/node_modules` is populated (for type-check + `tsx`).
```bash
test -d /Users/thoroxnard/Documents/Fullcarts/web/node_modules || (cd /Users/thoroxnard/Documents/Fullcarts/web && pnpm install)
```

**Step 5:** No commit yet — this is just verification.

---

# Deliverable 1: /admin/claims/groups admin tool

## Task 1: Normalization helpers + tests

**What this does in plain English:** Write the pure functions that decide which claims belong to the same group. Three helpers: normalize a brand string, build a fuzzy product-name key, and bucket the size change.

**Files:**
- Create: `web/src/app/admin/claims/groups/lib.ts`
- Create: `web/src/app/admin/claims/groups/__tests__/lib.test.ts`

**Step 1: Write the failing test (TDD red).**

Create `web/src/app/admin/claims/groups/__tests__/lib.test.ts`:
```typescript
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
```

**Step 2: Run the test to verify failure.**
```bash
cd web && pnpm exec tsx src/app/admin/claims/groups/__tests__/lib.test.ts 2>&1 | tail -5
```
Expected: error about missing `../lib` module.

**Step 3: Implement the helpers.**

Create `web/src/app/admin/claims/groups/lib.ts`:
```typescript
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
  while (BRAND_SUFFIX_RE.test(s)) s = s.replace(BRAND_SUFFIX_RE, "");
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
```

**Step 4: Run the test to verify pass.**
```bash
cd web && pnpm exec tsx src/app/admin/claims/groups/__tests__/lib.test.ts 2>&1 | tail -25
```
Expected: every `PASS`, ending with `All assertions passed`.

**Step 5: Type-check.**
```bash
cd web && pnpm exec tsc --noEmit 2>&1 | tail -5
```
Expected: no errors.

**Step 6: Commit.**
```bash
git add web/src/app/admin/claims/groups/lib.ts web/src/app/admin/claims/groups/__tests__/lib.test.ts
git commit -m "feat(admin): grouping helpers for claim-review streamlining"
```

---

## Task 2: Grouping function + tests

**What this does in plain English:** Take a list of pending claims and produce groups. Each group is a bunch of claims that share the same normalized brand + fuzzy name + size bucket. Most-claims-first ordering.

**Files:**
- Modify: `web/src/app/admin/claims/groups/lib.ts` (append)
- Modify: `web/src/app/admin/claims/groups/__tests__/lib.test.ts` (append)

**Step 1: Append failing test.**

Append to `__tests__/lib.test.ts`:
```typescript
import { groupPendingClaims } from "../lib";
import type { PendingClaim } from "../lib";

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
    mk({ id: "b", brand: "Cadbury UK" }),       // same brand once normalized
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
  // Same heuristic group, three sub-clusters: ent-1 (2), ent-2 (1), unmatched (1)
  expect("1 outer group", groups.length, 1);
  expect("3 sub-clusters", groups[0].sub_clusters.length, 3);
  expect("largest sub-cluster first", groups[0].sub_clusters[0].claims.length, 2);
}
```

**Step 2: Run test (expect fail).**
```bash
cd web && pnpm exec tsx src/app/admin/claims/groups/__tests__/lib.test.ts 2>&1 | tail -5
```
Expected: error about missing `groupPendingClaims`.

**Step 3: Append implementation.**

Append to `web/src/app/admin/claims/groups/lib.ts`:
```typescript
export interface PendingClaim {
  id: string;
  brand: string | null;
  product_name: string | null;
  old_size: number | null;
  new_size: number | null;
  size_unit: string | null;
  confidence_overall: number;
  matched_entity_id: string | null;
  source_type: string | null;          // reddit / news / gdelt / ...
  image_storage_path: string | null;
  raw_payload_title: string | null;    // for display when product_name is null
  raw_item_url: string | null;         // outbound link to source
}

export interface SubCluster {
  matched_entity_id: string | null;
  claims: PendingClaim[];
}

export interface ClaimGroup {
  key: string;          // stable composite key
  brand: string;        // normalized
  brand_display: string; // first non-empty brand string from the claims
  name_key: string;     // fuzzy name key
  name_display: string; // representative product_name for the header
  size_change: string;  // canonical bucket string
  count: number;        // total claims across all sub-clusters
  sub_clusters: SubCluster[]; // sorted largest-first
  claims: PendingClaim[];     // flat list across all sub-clusters, highest-confidence first
  source_breakdown: Record<string, number>; // {reddit: 5, news: 2, ...}
  confidence_range: [number, number]; // min, max overall confidence
}

export function groupPendingClaims(claims: PendingClaim[]): ClaimGroup[] {
  const buckets = new Map<string, PendingClaim[]>();
  for (const c of claims) {
    const key = [
      normalizeBrand(c.brand),
      fuzzyNameKey(c.product_name),
      sizeBucket(c.old_size, c.new_size, c.size_unit),
    ].join("|");
    const list = buckets.get(key);
    if (list) list.push(c);
    else buckets.set(key, [c]);
  }

  const groups: ClaimGroup[] = [];
  for (const [key, list] of buckets) {
    const [b, _n, sz] = key.split("|");
    const sortedByConf = [...list].sort((a, c) => c.confidence_overall - a.confidence_overall);
    const brandDisplay = list.find((c) => c.brand)?.brand || "(no brand)";
    const nameDisplay = list.find((c) => c.product_name)?.product_name || "(no name)";

    const subBuckets = new Map<string, PendingClaim[]>();
    for (const c of list) {
      const sk = c.matched_entity_id || "__unmatched__";
      const sub = subBuckets.get(sk);
      if (sub) sub.push(c);
      else subBuckets.set(sk, [c]);
    }
    const subClusters: SubCluster[] = [...subBuckets.entries()]
      .map(([sk, items]) => ({
        matched_entity_id: sk === "__unmatched__" ? null : sk,
        claims: items,
      }))
      .sort((a, c) => c.claims.length - a.claims.length);

    const sourceBreakdown: Record<string, number> = {};
    for (const c of list) {
      const s = c.source_type || "unknown";
      sourceBreakdown[s] = (sourceBreakdown[s] || 0) + 1;
    }

    const confs = list.map((c) => c.confidence_overall);
    const confRange: [number, number] = [Math.min(...confs), Math.max(...confs)];

    groups.push({
      key,
      brand: b,
      brand_display: brandDisplay,
      name_key: _n,
      name_display: nameDisplay,
      size_change: sz,
      count: list.length,
      sub_clusters: subClusters,
      claims: sortedByConf,
      source_breakdown: sourceBreakdown,
      confidence_range: confRange,
    });
  }

  return groups.sort((a, c) => c.count - a.count);
}
```

**Step 4: Run test to verify pass.**
```bash
cd web && pnpm exec tsx src/app/admin/claims/groups/__tests__/lib.test.ts 2>&1 | tail -10
```
Expected: all `PASS`.

**Step 5: Type-check.**
```bash
cd web && pnpm exec tsc --noEmit 2>&1 | tail -5
```

**Step 6: Commit.**
```bash
git add web/src/app/admin/claims/groups/lib.ts web/src/app/admin/claims/groups/__tests__/lib.test.ts
git commit -m "feat(admin): groupPendingClaims — heuristic cluster builder"
```

---

## Task 3: /admin/claims/groups server route

**What this does in plain English:** The actual admin URL that loads all pending claims from the database and runs them through the grouper. No interactivity yet — just shows the groups.

**Files:**
- Create: `web/src/app/admin/claims/groups/page.tsx`

**Step 1: Implement the page.**

Create `web/src/app/admin/claims/groups/page.tsx`:
```tsx
import Link from "next/link";
import { createAdminClient } from "@/lib/supabase/admin";
import { groupPendingClaims } from "./lib";
import type { PendingClaim, ClaimGroup } from "./lib";
import GroupCard from "./GroupCard";

export const dynamic = "force-dynamic";

async function loadAllPendingClaims(): Promise<PendingClaim[]> {
  const sb = createAdminClient();
  const PAGE = 1000;
  const all: PendingClaim[] = [];
  // Paginate past PostgREST's 1k cap.
  for (let from = 0; ; from += PAGE) {
    const { data, error } = await sb
      .from("claims")
      .select(
        "id,brand,product_name,old_size,new_size,old_size_unit,confidence," +
          "matched_entity_id,image_storage_path,raw_item_id," +
          "raw_items!inner(source_type,source_url,raw_payload)",
      )
      .eq("status", "pending")
      .order("id")
      .range(from, from + PAGE - 1);
    if (error) throw new Error(`claims load: ${error.message}`);
    const batch = (data ?? []) as Array<{
      id: string;
      brand: string | null;
      product_name: string | null;
      old_size: number | null;
      new_size: number | null;
      old_size_unit: string | null;
      confidence: { overall?: number } | null;
      matched_entity_id: string | null;
      image_storage_path: string | null;
      raw_item_id: string;
      raw_items: {
        source_type: string | null;
        source_url: string | null;
        raw_payload: { title?: string } | null;
      };
    }>;
    for (const row of batch) {
      all.push({
        id: row.id,
        brand: row.brand,
        product_name: row.product_name,
        old_size: row.old_size,
        new_size: row.new_size,
        size_unit: row.old_size_unit,
        confidence_overall: row.confidence?.overall ?? 0,
        matched_entity_id: row.matched_entity_id,
        source_type: row.raw_items?.source_type ?? null,
        image_storage_path: row.image_storage_path,
        raw_payload_title: row.raw_items?.raw_payload?.title ?? null,
        raw_item_url: row.raw_items?.source_url ?? null,
      });
    }
    if (batch.length < PAGE) break;
  }
  return all;
}

export default async function ClaimsGroupsPage() {
  const claims = await loadAllPendingClaims();
  const groups: ClaimGroup[] = groupPendingClaims(claims);
  const totalClaims = claims.length;
  const totalGroups = groups.length;
  const singletons = groups.filter((g) => g.count === 1).length;

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]">
      <header className="border-b border-[var(--bg-tertiary)] px-6 py-4 space-y-3">
        <div className="flex items-baseline gap-4">
          <h1 className="font-[var(--font-headline)] text-2xl font-bold tracking-tight">
            Claim Groups
          </h1>
          <Link
            href="/admin/claims?status=pending"
            className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] underline-offset-4 hover:underline"
          >
            ← Single-card review
          </Link>
        </div>
        <p className="text-sm text-[var(--text-secondary)]">
          {totalClaims.toLocaleString()} pending claims grouped into{" "}
          {totalGroups.toLocaleString()} clusters
          {singletons > 0 && (
            <span> · {singletons.toLocaleString()} singletons (1-claim groups)</span>
          )}
          . Largest groups first. Each cluster shares brand + fuzzy product name +
          size change.
        </p>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-6 space-y-4">
        {groups.length === 0 ? (
          <div className="border border-[var(--bg-tertiary)] rounded-lg p-8 text-center text-[var(--text-secondary)]">
            No pending claims to group.
          </div>
        ) : (
          groups.map((g) => <GroupCard key={g.key} group={g} />)
        )}
      </main>
    </div>
  );
}
```

**Step 2: Create a placeholder GroupCard so the page compiles.**

Create `web/src/app/admin/claims/groups/GroupCard.tsx`:
```tsx
import type { ClaimGroup } from "./lib";

export default function GroupCard({ group }: { group: ClaimGroup }) {
  return (
    <article className="border border-[var(--bg-tertiary)] rounded-lg bg-[var(--bg-secondary)] p-4">
      <header className="flex items-baseline gap-3 mb-2">
        <span className="font-mono text-xs text-[var(--text-tertiary)]">
          {group.count}×
        </span>
        <span className="font-medium">{group.brand_display}</span>
        <span className="text-[var(--text-secondary)]">·</span>
        <span className="text-[var(--text-secondary)]">{group.name_display}</span>
        <span className="text-[var(--text-secondary)]">·</span>
        <span className="font-mono text-sm text-[var(--red-text)]">
          {group.size_change}
        </span>
      </header>
      <p className="text-xs text-[var(--text-tertiary)]">
        Sources:{" "}
        {Object.entries(group.source_breakdown)
          .map(([k, v]) => `${k}=${v}`)
          .join(", ")}{" "}
        · Confidence {(group.confidence_range[0] * 100).toFixed(0)}–
        {(group.confidence_range[1] * 100).toFixed(0)}%
      </p>
    </article>
  );
}
```

**Step 3: Type-check and build.**
```bash
cd web && pnpm exec tsc --noEmit 2>&1 | tail -5
```
Expected: no errors.

**Step 4: Local smoke test.**
```bash
cd web && pnpm dev
```
In a separate terminal, after dev server is listening on http://localhost:3000:
```bash
curl -sI http://localhost:3000/admin/claims/groups | head -3
```
Expected: 200 (or 307 redirect to /admin/login if you're not signed in locally — that's fine, it means the route exists and the middleware works).

Stop the dev server.

**Step 5: Commit.**
```bash
git add web/src/app/admin/claims/groups/page.tsx web/src/app/admin/claims/groups/GroupCard.tsx
git commit -m "feat(admin): /admin/claims/groups route + minimal GroupCard"
```

---

## Task 4: Full GroupCard with representative-claim preview

**What this does in plain English:** Replace the placeholder GroupCard with the real card — shows the highest-confidence claim's image and title as a preview, plus an "Show all N" toggle to expand the full list.

**Files:**
- Modify: `web/src/app/admin/claims/groups/GroupCard.tsx` (full rewrite)
- Create: `web/src/app/admin/claims/groups/GroupCardClient.tsx` (client component for expand toggle + selection state)

**Step 1: Build the client wrapper.**

Create `web/src/app/admin/claims/groups/GroupCardClient.tsx`:
```tsx
"use client";

import { useState } from "react";
import type { ClaimGroup, PendingClaim } from "./lib";
import { ClaimImage } from "@/components/admin/ClaimImage";

// Renders one expandable card per group. Selection (the per-group
// "Select" checkbox the bulk toolbar listens to) is managed by the
// parent GroupsClient (Task 5); this component just exposes the
// expand toggle and per-group action buttons.

interface Props {
  group: ClaimGroup;
  selected: boolean;
  onSelectChange: (next: boolean) => void;
  onAction: (action: "approve_all" | "discard_all" | "merge_into" | "edit_then_approve", group: ClaimGroup) => void;
  busy: boolean;
}

function ClaimRow({ c }: { c: PendingClaim }) {
  return (
    <div className="flex gap-3 py-2 border-t border-[var(--bg-tertiary)] text-sm">
      <div className="w-16 h-16 bg-[var(--bg-primary)] flex-shrink-0 rounded overflow-hidden">
        {c.image_storage_path ? (
          <ClaimImage src="" storagePath={c.image_storage_path} alt={c.product_name || ""} />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-[var(--text-tertiary)] text-xs">
            —
          </div>
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-medium truncate">{c.raw_payload_title || c.product_name || "(no title)"}</div>
        <div className="text-xs text-[var(--text-tertiary)] flex gap-2 mt-0.5">
          <span>{c.source_type || "?"}</span>
          <span>·</span>
          <span>conf {(c.confidence_overall * 100).toFixed(0)}%</span>
          {c.matched_entity_id && (
            <>
              <span>·</span>
              <span className="font-mono">→ {c.matched_entity_id.slice(0, 8)}</span>
            </>
          )}
        </div>
        {c.raw_item_url && (
          <a
            href={c.raw_item_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-[var(--blue-base)] hover:underline"
          >
            source ↗
          </a>
        )}
      </div>
    </div>
  );
}

export default function GroupCardClient({ group, selected, onSelectChange, onAction, busy }: Props) {
  const [expanded, setExpanded] = useState(false);
  const rep = group.claims[0];

  return (
    <article className="border border-[var(--bg-tertiary)] rounded-lg bg-[var(--bg-secondary)]">
      <header className="flex items-center gap-3 px-4 py-3 border-b border-[var(--bg-tertiary)]">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={selected}
            onChange={(e) => onSelectChange(e.target.checked)}
            className="w-4 h-4"
          />
        </label>
        <span className="font-mono text-xs text-[var(--text-tertiary)]">{group.count}×</span>
        <span className="font-medium">{group.brand_display}</span>
        <span className="text-[var(--text-secondary)]">·</span>
        <span className="text-[var(--text-secondary)] truncate">{group.name_display}</span>
        <span className="text-[var(--text-secondary)]">·</span>
        <span className="font-mono text-sm text-[var(--red-text)]">{group.size_change}</span>
        <span className="ml-auto text-xs text-[var(--text-tertiary)]">
          conf {(group.confidence_range[0] * 100).toFixed(0)}–{(group.confidence_range[1] * 100).toFixed(0)}%
          {" · "}
          {Object.entries(group.source_breakdown).map(([k, v]) => `${k}=${v}`).join(", ")}
        </span>
      </header>

      <div className="p-4">
        {rep && <ClaimRow c={rep} />}
        {group.count > 1 && (
          <button
            type="button"
            onClick={() => setExpanded((x) => !x)}
            className="mt-2 text-sm text-[var(--blue-base)] hover:underline"
          >
            {expanded ? "Hide" : `Show all ${group.count}`}
          </button>
        )}
        {expanded && (
          <div className="mt-2">
            {group.claims.slice(1).map((c) => (
              <ClaimRow key={c.id} c={c} />
            ))}
          </div>
        )}
      </div>

      <footer className="flex gap-2 px-4 py-3 border-t border-[var(--bg-tertiary)] flex-wrap">
        <button
          type="button"
          disabled={busy}
          onClick={() => onAction("approve_all", group)}
          className="px-3 py-1.5 text-sm rounded border border-[var(--green-border)] bg-[var(--green-bg)] text-[var(--green-base)] hover:opacity-80 disabled:opacity-50"
        >
          Approve all {group.count}
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => onAction("discard_all", group)}
          className="px-3 py-1.5 text-sm rounded border border-[var(--red-border)] bg-[var(--red-bg)] text-[var(--red-text)] hover:opacity-80 disabled:opacity-50"
        >
          Discard all
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => onAction("merge_into", group)}
          className="px-3 py-1.5 text-sm rounded border border-[var(--blue-border)] bg-[var(--blue-bg)] text-[var(--blue-base)] hover:opacity-80 disabled:opacity-50"
        >
          Merge into entity →
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => onAction("edit_then_approve", group)}
          className="px-3 py-1.5 text-sm rounded border border-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] disabled:opacity-50"
        >
          Edit then approve…
        </button>
      </footer>
    </article>
  );
}
```

**Step 2: Type-check.**
```bash
cd web && pnpm exec tsc --noEmit 2>&1 | tail -5
```

**Step 3: Commit (this card is wired up in Task 5).**
```bash
git add web/src/app/admin/claims/groups/GroupCardClient.tsx
git commit -m "feat(admin): GroupCardClient — expandable card with per-group action buttons"
```

---

## Task 5: GroupsClient + page rewrite to use client wrapper

**What this does in plain English:** Add the parent client component that holds selection state across all groups, has the sticky bulk-action toolbar at the bottom, and dispatches actions to the right API route. Replace the page's `GroupCard` import with the new client wrapper.

**Files:**
- Create: `web/src/app/admin/claims/groups/GroupsClient.tsx`
- Modify: `web/src/app/admin/claims/groups/page.tsx`
- Delete: `web/src/app/admin/claims/groups/GroupCard.tsx` (placeholder no longer used)

**Step 1: Build the parent client component.**

Create `web/src/app/admin/claims/groups/GroupsClient.tsx`:
```tsx
"use client";

import { useState, useTransition, useCallback } from "react";
import type { ClaimGroup } from "./lib";
import GroupCardClient from "./GroupCardClient";
import EntityPicker from "./EntityPicker";

interface Props {
  groups: ClaimGroup[];
}

type Action = "approve_all" | "discard_all" | "merge_into" | "edit_then_approve";

interface EditDraft {
  brand: string;
  product_name: string;
  category: string;
}

export default function GroupsClient({ groups: initial }: Props) {
  const [groups, setGroups] = useState(initial);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [busy, startTransition] = useTransition();
  const [pickerFor, setPickerFor] = useState<ClaimGroup | null>(null);
  const [editFor, setEditFor] = useState<ClaimGroup | null>(null);
  const [editDraft, setEditDraft] = useState<EditDraft>({ brand: "", product_name: "", category: "" });

  const toggle = useCallback((key: string, next: boolean) => {
    setSelected((prev) => {
      const n = new Set(prev);
      if (next) n.add(key);
      else n.delete(key);
      return n;
    });
  }, []);

  async function runBulkApi(route: string, body: object): Promise<void> {
    const res = await fetch(`/api/admin/${route}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const t = await res.text();
      throw new Error(`${route}: ${res.status} ${t}`);
    }
  }

  function removeGroupsFromState(keys: string[]) {
    const ks = new Set(keys);
    setGroups((gs) => gs.filter((g) => !ks.has(g.key)));
    setSelected((sel) => {
      const n = new Set(sel);
      for (const k of ks) n.delete(k);
      return n;
    });
  }

  function handleAction(action: Action, group: ClaimGroup) {
    if (action === "merge_into") {
      setPickerFor(group);
      return;
    }
    if (action === "edit_then_approve") {
      setEditFor(group);
      setEditDraft({
        brand: group.brand_display === "(no brand)" ? "" : group.brand_display,
        product_name: group.name_display === "(no name)" ? "" : group.name_display,
        category: "",
      });
      return;
    }
    if (!confirm(`${action.replace("_", " ")} for ${group.count} claims?`)) return;
    const ids = group.claims.map((c) => c.id);
    const route = action === "approve_all" ? "bulk-approve-claims" : "bulk-discard-claims";
    startTransition(async () => {
      try {
        await runBulkApi(route, { claim_ids: ids });
        removeGroupsFromState([group.key]);
      } catch (e) {
        alert(`Failed: ${String(e)}`);
      }
    });
  }

  function handleBulkAction(action: "approve_all" | "discard_all") {
    if (selected.size === 0) return;
    const groupsToActOn = groups.filter((g) => selected.has(g.key));
    const totalClaims = groupsToActOn.reduce((acc, g) => acc + g.count, 0);
    if (!confirm(`${action.replace("_", " ")} for ${totalClaims} claims across ${groupsToActOn.length} groups?`)) return;
    const ids = groupsToActOn.flatMap((g) => g.claims.map((c) => c.id));
    const route = action === "approve_all" ? "bulk-approve-claims" : "bulk-discard-claims";
    startTransition(async () => {
      try {
        await runBulkApi(route, { claim_ids: ids });
        removeGroupsFromState(groupsToActOn.map((g) => g.key));
      } catch (e) {
        alert(`Failed: ${String(e)}`);
      }
    });
  }

  function handleMergeConfirmed(entityId: string) {
    if (!pickerFor) return;
    const g = pickerFor;
    setPickerFor(null);
    const ids = g.claims.map((c) => c.id);
    startTransition(async () => {
      try {
        await runBulkApi("bulk-merge-claims", { claim_ids: ids, entity_id: entityId });
        removeGroupsFromState([g.key]);
      } catch (e) {
        alert(`Failed: ${String(e)}`);
      }
    });
  }

  function handleEditConfirmed() {
    if (!editFor) return;
    const g = editFor;
    const draft = editDraft;
    setEditFor(null);
    const ids = g.claims.map((c) => c.id);
    startTransition(async () => {
      try {
        await runBulkApi("bulk-edit-approve-claims", {
          claim_ids: ids,
          patch: {
            brand: draft.brand || null,
            product_name: draft.product_name || null,
            category: draft.category || null,
          },
        });
        removeGroupsFromState([g.key]);
      } catch (e) {
        alert(`Failed: ${String(e)}`);
      }
    });
  }

  return (
    <>
      {groups.map((g) => (
        <GroupCardClient
          key={g.key}
          group={g}
          selected={selected.has(g.key)}
          onSelectChange={(n) => toggle(g.key, n)}
          onAction={handleAction}
          busy={busy}
        />
      ))}

      {selected.size > 0 && (
        <div className="fixed bottom-0 inset-x-0 border-t border-[var(--bg-tertiary)] bg-[var(--bg-secondary)] px-6 py-3 flex items-center gap-3">
          <span className="text-sm">
            {selected.size} group{selected.size === 1 ? "" : "s"} selected
          </span>
          <div className="ml-auto flex gap-2">
            <button
              type="button"
              disabled={busy}
              onClick={() => handleBulkAction("approve_all")}
              className="px-3 py-1.5 text-sm rounded border border-[var(--green-border)] bg-[var(--green-bg)] text-[var(--green-base)] hover:opacity-80 disabled:opacity-50"
            >
              Approve selected
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => handleBulkAction("discard_all")}
              className="px-3 py-1.5 text-sm rounded border border-[var(--red-border)] bg-[var(--red-bg)] text-[var(--red-text)] hover:opacity-80 disabled:opacity-50"
            >
              Discard selected
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => setSelected(new Set())}
              className="px-3 py-1.5 text-sm rounded border border-[var(--bg-tertiary)] text-[var(--text-secondary)]"
            >
              Clear
            </button>
          </div>
        </div>
      )}

      {pickerFor && (
        <EntityPicker
          brand={pickerFor.brand_display}
          nameHint={pickerFor.name_display}
          onCancel={() => setPickerFor(null)}
          onPick={handleMergeConfirmed}
        />
      )}

      {editFor && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-6">
          <div className="bg-[var(--bg-secondary)] border border-[var(--bg-tertiary)] rounded-lg p-6 w-full max-w-md space-y-3">
            <h3 className="font-medium">
              Edit {editFor.count} claims, then approve
            </h3>
            <p className="text-xs text-[var(--text-tertiary)]">
              Fields you leave blank stay as-is on each claim.
            </p>
            <label className="block text-sm">
              Brand
              <input
                type="text"
                value={editDraft.brand}
                onChange={(e) => setEditDraft((d) => ({ ...d, brand: e.target.value }))}
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
            <label className="block text-sm">
              Product name
              <input
                type="text"
                value={editDraft.product_name}
                onChange={(e) => setEditDraft((d) => ({ ...d, product_name: e.target.value }))}
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
            <label className="block text-sm">
              Category
              <input
                type="text"
                value={editDraft.category}
                onChange={(e) => setEditDraft((d) => ({ ...d, category: e.target.value }))}
                className="w-full px-2 py-1 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded mt-1"
              />
            </label>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setEditFor(null)} className="px-3 py-1.5 text-sm">
                Cancel
              </button>
              <button
                type="button"
                onClick={handleEditConfirmed}
                disabled={busy}
                className="px-3 py-1.5 text-sm rounded border border-[var(--green-border)] bg-[var(--green-bg)] text-[var(--green-base)] disabled:opacity-50"
              >
                Apply + Approve all {editFor.count}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
```

**Step 2: Stub EntityPicker so the file compiles (real impl in Task 7).**

Create `web/src/app/admin/claims/groups/EntityPicker.tsx`:
```tsx
"use client";

export default function EntityPicker(_props: {
  brand: string;
  nameHint: string;
  onCancel: () => void;
  onPick: (entityId: string) => void;
}) {
  return null;
}
```

**Step 3: Rewrite page.tsx to use GroupsClient.**

Replace `web/src/app/admin/claims/groups/page.tsx` lines that import + render GroupCard:
- Change `import GroupCard from "./GroupCard";` to `import GroupsClient from "./GroupsClient";`
- Change the `groups.map((g) => <GroupCard ...`) block to:
```tsx
<GroupsClient groups={groups} />
```

**Step 4: Delete the placeholder GroupCard.tsx.**
```bash
rm web/src/app/admin/claims/groups/GroupCard.tsx
```

**Step 5: Type-check.**
```bash
cd web && pnpm exec tsc --noEmit 2>&1 | tail -10
```
Expected: no errors.

**Step 6: Commit.**
```bash
git add -A web/src/app/admin/claims/groups/
git commit -m "feat(admin): GroupsClient — selection state + bulk action toolbar"
```

---

## Task 6: Bulk action API routes

**What this does in plain English:** Four new endpoints under `/api/admin/` that do the actual database writes for: approve all, discard all, merge into entity, edit-then-approve. All admin-only (the middleware enforces this).

**Files:**
- Create: `web/src/app/api/admin/bulk-approve-claims/route.ts`
- Create: `web/src/app/api/admin/bulk-discard-claims/route.ts`
- Create: `web/src/app/api/admin/bulk-merge-claims/route.ts`
- Create: `web/src/app/api/admin/bulk-edit-approve-claims/route.ts`

**Step 1: Reference the existing pattern.**
Read `web/src/app/api/admin/retract-event/route.ts` once to see the auth + body-parse + error-shape convention. (No commit, just for context.)

**Step 2: Implement `bulk-approve-claims`.**

Create `web/src/app/api/admin/bulk-approve-claims/route.ts`:
```typescript
import { NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { requireAdminCookie } from "@/lib/admin-auth";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  if (!requireAdminCookie()) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  let body: { claim_ids?: unknown };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "bad json" }, { status: 400 });
  }
  const ids = Array.isArray(body.claim_ids) ? body.claim_ids.filter((x): x is string => typeof x === "string") : [];
  if (ids.length === 0) return NextResponse.json({ error: "claim_ids required" }, { status: 400 });

  const sb = createAdminClient();
  const { error } = await sb
    .from("claims")
    .update({ status: "matched" })
    .in("id", ids);
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ ok: true, updated: ids.length });
}
```

**Step 3: Implement `bulk-discard-claims`.**

Create `web/src/app/api/admin/bulk-discard-claims/route.ts`:
```typescript
import { NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { requireAdminCookie } from "@/lib/admin-auth";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  if (!requireAdminCookie()) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  let body: { claim_ids?: unknown };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "bad json" }, { status: 400 });
  }
  const ids = Array.isArray(body.claim_ids) ? body.claim_ids.filter((x): x is string => typeof x === "string") : [];
  if (ids.length === 0) return NextResponse.json({ error: "claim_ids required" }, { status: 400 });

  const sb = createAdminClient();
  const { error } = await sb
    .from("claims")
    .update({ status: "discarded" })
    .in("id", ids);
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ ok: true, updated: ids.length });
}
```

**Step 4: Implement `bulk-merge-claims`.**

Create `web/src/app/api/admin/bulk-merge-claims/route.ts`:
```typescript
import { NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { requireAdminCookie } from "@/lib/admin-auth";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  if (!requireAdminCookie()) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  let body: { claim_ids?: unknown; entity_id?: unknown };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "bad json" }, { status: 400 });
  }
  const ids = Array.isArray(body.claim_ids) ? body.claim_ids.filter((x): x is string => typeof x === "string") : [];
  const entityId = typeof body.entity_id === "string" ? body.entity_id : null;
  if (ids.length === 0) return NextResponse.json({ error: "claim_ids required" }, { status: 400 });
  if (!entityId) return NextResponse.json({ error: "entity_id required" }, { status: 400 });

  const sb = createAdminClient();
  // Sanity: target entity must exist and not be retracted.
  const { data: ent, error: entErr } = await sb
    .from("product_entities")
    .select("id,is_retracted")
    .eq("id", entityId)
    .single();
  if (entErr || !ent) return NextResponse.json({ error: "entity not found" }, { status: 404 });
  if (ent.is_retracted) return NextResponse.json({ error: "entity is retracted" }, { status: 400 });

  const { error } = await sb
    .from("claims")
    .update({ status: "matched", matched_entity_id: entityId })
    .in("id", ids);
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ ok: true, updated: ids.length, entity_id: entityId });
}
```

**Step 5: Implement `bulk-edit-approve-claims`.**

Create `web/src/app/api/admin/bulk-edit-approve-claims/route.ts`:
```typescript
import { NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { requireAdminCookie } from "@/lib/admin-auth";

export const dynamic = "force-dynamic";

interface Patch {
  brand?: string | null;
  product_name?: string | null;
  category?: string | null;
}

export async function POST(req: Request) {
  if (!requireAdminCookie()) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  let body: { claim_ids?: unknown; patch?: unknown };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "bad json" }, { status: 400 });
  }
  const ids = Array.isArray(body.claim_ids) ? body.claim_ids.filter((x): x is string => typeof x === "string") : [];
  const patchRaw = (body.patch && typeof body.patch === "object" ? body.patch : {}) as Record<string, unknown>;
  const patch: Patch = {};
  if (typeof patchRaw.brand === "string" && patchRaw.brand) patch.brand = patchRaw.brand;
  if (typeof patchRaw.product_name === "string" && patchRaw.product_name) patch.product_name = patchRaw.product_name;
  if (typeof patchRaw.category === "string" && patchRaw.category) patch.category = patchRaw.category;
  if (ids.length === 0) return NextResponse.json({ error: "claim_ids required" }, { status: 400 });

  const sb = createAdminClient();
  const update = { status: "matched", ...patch };
  const { error } = await sb.from("claims").update(update).in("id", ids);
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ ok: true, updated: ids.length, patch });
}
```

**Step 6: Verify `requireAdminCookie` exists and signature matches.**
```bash
grep -n "requireAdminCookie\|export function requireAdmin" web/src/lib/admin-auth.ts
```
Expected: function exists with signature returning boolean (or similar). If the actual function name differs, adjust all four route files to match.

**Step 7: Type-check.**
```bash
cd web && pnpm exec tsc --noEmit 2>&1 | tail -10
```

**Step 8: Commit.**
```bash
git add web/src/app/api/admin/bulk-approve-claims/ \
       web/src/app/api/admin/bulk-discard-claims/ \
       web/src/app/api/admin/bulk-merge-claims/ \
       web/src/app/api/admin/bulk-edit-approve-claims/
git commit -m "feat(admin): bulk claim API routes — approve/discard/merge/edit-approve"
```

---

## Task 7: Real EntityPicker

**What this does in plain English:** Replace the stub EntityPicker with a real searchable picker — type to search entities by brand+name, click one to confirm the merge.

**Files:**
- Modify: `web/src/app/admin/claims/groups/EntityPicker.tsx` (full rewrite)
- Create: `web/src/app/api/admin/search-entities/route.ts`

**Step 1: Implement the search endpoint.**

Create `web/src/app/api/admin/search-entities/route.ts`:
```typescript
import { NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { requireAdminCookie } from "@/lib/admin-auth";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  if (!requireAdminCookie()) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  const url = new URL(req.url);
  const q = (url.searchParams.get("q") || "").trim();
  if (q.length < 2) return NextResponse.json({ rows: [] });

  const sb = createAdminClient();
  const { data, error } = await sb
    .from("product_entities")
    .select("id,brand,canonical_name,category")
    .eq("is_retracted", false)
    .or(`brand.ilike.%${q}%,canonical_name.ilike.%${q}%`)
    .limit(20);
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ rows: data || [] });
}
```

**Step 2: Implement the real EntityPicker.**

Replace `web/src/app/admin/claims/groups/EntityPicker.tsx`:
```tsx
"use client";

import { useEffect, useState } from "react";

interface EntityRow {
  id: string;
  brand: string;
  canonical_name: string;
  category: string | null;
}

interface Props {
  brand: string;
  nameHint: string;
  onCancel: () => void;
  onPick: (entityId: string) => void;
}

export default function EntityPicker({ brand, nameHint, onCancel, onPick }: Props) {
  const initialQuery = brand === "(no brand)" ? nameHint : `${brand} ${nameHint}`;
  const [q, setQ] = useState(initialQuery);
  const [rows, setRows] = useState<EntityRow[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const handle = setTimeout(async () => {
      if (q.trim().length < 2) {
        setRows([]);
        return;
      }
      setLoading(true);
      try {
        const r = await fetch(`/api/admin/search-entities?q=${encodeURIComponent(q.trim())}`);
        const j = await r.json();
        setRows(j.rows || []);
      } finally {
        setLoading(false);
      }
    }, 200);
    return () => clearTimeout(handle);
  }, [q]);

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-6 z-50">
      <div className="bg-[var(--bg-secondary)] border border-[var(--bg-tertiary)] rounded-lg p-6 w-full max-w-2xl space-y-3">
        <header className="flex items-baseline gap-3">
          <h3 className="font-medium">Merge claims into entity</h3>
          <span className="text-xs text-[var(--text-tertiary)]">type to search by brand or name</span>
        </header>
        <input
          autoFocus
          type="text"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--bg-tertiary)] rounded"
        />
        <div className="max-h-80 overflow-y-auto border border-[var(--bg-tertiary)] rounded">
          {loading && <div className="p-3 text-sm text-[var(--text-tertiary)]">searching…</div>}
          {!loading && rows.length === 0 && <div className="p-3 text-sm text-[var(--text-tertiary)]">No matches</div>}
          {rows.map((r) => (
            <button
              key={r.id}
              type="button"
              onClick={() => onPick(r.id)}
              className="block w-full text-left px-3 py-2 hover:bg-[var(--bg-tertiary)] border-b border-[var(--bg-tertiary)]"
            >
              <div className="text-sm font-medium">
                {r.brand} <span className="text-[var(--text-secondary)]">·</span> {r.canonical_name}
              </div>
              {r.category && <div className="text-xs text-[var(--text-tertiary)]">{r.category}</div>}
            </button>
          ))}
        </div>
        <div className="flex justify-end gap-2">
          <button type="button" onClick={onCancel} className="px-3 py-1.5 text-sm">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
```

**Step 3: Type-check.**
```bash
cd web && pnpm exec tsc --noEmit 2>&1 | tail -5
```

**Step 4: Commit.**
```bash
git add web/src/app/admin/claims/groups/EntityPicker.tsx web/src/app/api/admin/search-entities/
git commit -m "feat(admin): real EntityPicker — debounced search across active entities"
```

---

## Task 8: Link from /admin/claims pending tab header

**What this does in plain English:** Add a visible "View as groups (N clusters)" link at the top of the existing /admin/claims page so the founder can jump from single-card to grouped view.

**Files:**
- Modify: `web/src/app/admin/claims/page.tsx` (header section only)

**Step 1: Edit header.**

Inside the `<header className="border-b border-[var(--bg-tertiary)] px-6 py-4 space-y-3">` block of `web/src/app/admin/claims/page.tsx`, in the `<div className="flex items-baseline gap-4">` that already contains the Entity Browser + Quality Flags links, add a third link:
```tsx
<a
  href="/admin/claims/groups"
  className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] underline-offset-4 hover:underline"
>
  Group view →
</a>
```

**Step 2: Type-check.**
```bash
cd web && pnpm exec tsc --noEmit 2>&1 | tail -5
```

**Step 3: Commit.**
```bash
git add web/src/app/admin/claims/page.tsx
git commit -m "feat(admin): link to /admin/claims/groups from pending tab header"
```

---

## Task 9: Local manual verification

**What this does in plain English:** Spin up the dev server, sign in as admin, walk through the new flow.

**Step 1: Start dev server.**
```bash
cd web && pnpm dev
```
Expected: "Local: http://localhost:3000".

**Step 2: Open browser → http://localhost:3000/admin/login → enter password (from `app_settings` table, founder knows it).**

**Step 3: Visit http://localhost:3000/admin/claims/groups.**

Expected:
- Header shows total pending + cluster count (e.g., "2,527 pending claims grouped into ~400 clusters").
- First card is the largest group (highest count).
- Per-group action buttons render: Approve all / Discard all / Merge into entity → / Edit then approve…
- Header checkbox + count + size change all read correctly.

**Step 4: Smoke-test ONE action of each kind (on the SMALLEST groups, so we don't muck up the real review queue):**
- Approve all → group disappears, network tab shows 200 from `/api/admin/bulk-approve-claims`.
- Discard all → group disappears, ditto.
- Merge into entity → picker opens, search for a known entity, click → group disappears.
- Edit then approve → modal opens, fill brand/name, click apply → group disappears.

**Step 5: Refresh /admin/claims/groups and confirm groups don't reappear.**

**Step 6: Stop the dev server.**

**Step 7: No commit — verification only.**

If any step fails, log the failure, fix the code, repeat.

---

## Task 10: Push branch + open PR + deploy preview

**What this does in plain English:** Get the new tool onto a preview URL so the founder can try it without disturbing prod.

**Step 1: Push.**
```bash
git push -u origin claude/jovial-cerf-6bb9cc
```

**Step 2: Open PR.**
```bash
gh pr create --title "feat(admin): /admin/claims/groups bulk-review tool" --body "$(cat <<'EOF'
## Summary
- New `/admin/claims/groups` route: heuristic grouping of pending claims (normalized brand + fuzzy name + size bucket)
- Per-group bulk actions: approve / discard / merge-into-entity / edit-then-approve
- Cross-group selection toolbar
- Four new admin API routes for the bulk writes
- Link added from /admin/claims pending tab header

## Test plan
- [ ] Sign in to admin on preview URL
- [ ] Visit /admin/claims/groups, verify header counts
- [ ] Try each of the four per-group actions on small groups
- [ ] Try cross-group bulk approve + discard
- [ ] Refresh, confirm acted-on groups stay gone

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

**Step 3: Wait for Vercel preview deploy.**
Vercel auto-deploys PRs. Find the preview URL in the PR comments (or `gh pr view --json`).

**Step 4: Verify preview deploy.**
```bash
curl -sI <preview-url>/admin/claims/groups | head -3
```
Expected: 200 or 307→/admin/login.

**Step 5: No commit — this task is git/deploy only.**

---

## Task 11: Promote D1 to prod

**What this does in plain English:** Merge the PR to main, kick a prod deploy. The grouping tool is now live for the founder to start clearing the queue.

**Step 1: Merge PR (founder approves first).**
```bash
gh pr merge --squash --delete-branch
```

**Step 2: Switch to main and pull.**
```bash
git checkout main && git pull
```

**Step 3: Trigger prod deploy.**
```bash
cd /Users/thoroxnard/Documents/Fullcarts/web && \
  ./node_modules/.bin/vercel deploy --prod --cwd .. \
  --token=<PAT> --yes --scope fullcarts89s-projects 2>&1 | tail -10
```
Expected: line `Production: https://...` near the end. The `--cwd ..` is critical because the Vercel project's Root Directory is `web/` (without it, the CLI looks for `web/web/` and fails silently with exit 0).

**Step 4: Verify prod.**
```bash
curl -sI https://www.fullcarts.org/admin/claims/groups | head -3
```
Expected: 307 redirect to /admin/login (route exists, middleware works).

---

# Deliverable 2: zero-event entity cleanup

## Task 12: retract_zero_event_entities.py + tests

**What this does in plain English:** Write the one-shot cleanup script that retracts every entity that has no live event behind it. Includes a `--dry-run` mode that just prints what would happen.

**Files:**
- Create: `pipeline/scripts/retract_zero_event_entities.py`
- Create: `pipeline/tests/test_retract_zero_event_entities.py`

**Step 1: Write the failing test.**

Create `pipeline/tests/test_retract_zero_event_entities.py`:
```python
# Tests for retract_zero_event_entities.find_orphaned_entities — pure
# logic over a fake Supabase client. Network-level behaviour is
# exercised via --dry-run against real DB in the script's own runtime
# (see plan task 13), not here.

from unittest.mock import MagicMock

from pipeline.scripts import retract_zero_event_entities as mod


def make_sb(active_entities, live_events):
    """active_entities: list of {id}. live_events: list of {entity_id}."""
    sb = MagicMock()

    def from_(table):
        chain = MagicMock()
        if table == "product_entities":
            chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = active_entities
        elif table == "published_changes":
            chain.select.return_value.eq.return_value.not_.return_value.range.return_value.execute.return_value.data = live_events
        return chain

    sb.from_.side_effect = from_
    return sb


def test_orphaned_finds_entities_with_no_live_event():
    sb = make_sb(
        active_entities=[{"id": "e1"}, {"id": "e2"}, {"id": "e3"}],
        live_events=[{"entity_id": "e1"}],
    )
    out = mod.find_orphaned_entities(sb)
    assert set(out) == {"e2", "e3"}


def test_orphaned_empty_when_all_have_events():
    sb = make_sb(
        active_entities=[{"id": "e1"}],
        live_events=[{"entity_id": "e1"}],
    )
    out = mod.find_orphaned_entities(sb)
    assert out == []
```

**Step 2: Run test, expect ImportError.**
```bash
cd pipeline && python -m pytest tests/test_retract_zero_event_entities.py -v 2>&1 | tail -5
```
Expected: import error / module not found.

**Step 3: Implement the script.**

Create `pipeline/scripts/retract_zero_event_entities.py`:
```python
"""One-shot cleanup: retract every active product_entity that has no
non-retracted published_changes row behind it. Idempotent; can be
re-run safely. Writes an audit row to data_quality_flags per action.

Usage:
    python3 -m pipeline.scripts.retract_zero_event_entities --dry-run
    python3 -m pipeline.scripts.retract_zero_event_entities --limit 100
    python3 -m pipeline.scripts.retract_zero_event_entities         # run for real, no limit
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from supabase import create_client

from pipeline.lib import data_quality_flags

PAGE = 1000
FLAG_KIND = "zero_event_entity_swept"


def find_orphaned_entities(sb) -> List[str]:
    """Return entity_ids of active entities with no live event behind them."""
    # 1. All active entity ids
    active_ids: List[str] = []
    from_ = 0
    while True:
        resp = (
            sb.from_("product_entities")
            .select("id")
            .eq("is_retracted", False)
            .order("id")
            .range(from_, from_ + PAGE - 1)
            .execute()
        )
        rows = resp.data or []
        active_ids.extend(r["id"] for r in rows)
        if len(rows) < PAGE:
            break
        from_ += PAGE

    # 2. entity_ids that have at least one live event
    with_event = set()
    from_ = 0
    while True:
        resp = (
            sb.from_("published_changes")
            .select("entity_id")
            .eq("is_retracted", False)
            .not_("entity_id", "is", None)
            .range(from_, from_ + PAGE - 1)
            .execute()
        )
        rows = resp.data or []
        for r in rows:
            if r.get("entity_id"):
                with_event.add(r["entity_id"])
        if len(rows) < PAGE:
            break
        from_ += PAGE

    # 3. set diff = orphans
    return [eid for eid in active_ids if eid not in with_event]


def retract_one(sb, entity_id):
    # type: (...) -> Optional[int]
    """Retract one entity via set_entity_retracted RPC. Return events_affected."""
    resp = sb.rpc("set_entity_retracted", {
        "p_entity_id": entity_id,
        "p_retracted": True,
    }).execute()
    rows = resp.data or []
    if not rows:
        return None
    return rows[0].get("events_affected")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--limit", type=int, default=None)
    args = p.parse_args()

    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    sb = create_client(url, key)

    print(f"[retract_zero_event_entities] scanning...")
    orphans = find_orphaned_entities(sb)
    print(f"[retract_zero_event_entities] {len(orphans)} orphaned active entities found")

    if args.limit is not None:
        orphans = orphans[:args.limit]
        print(f"[retract_zero_event_entities] limit={args.limit} -> processing {len(orphans)}")

    if args.dry_run:
        print(f"[retract_zero_event_entities] DRY RUN, no writes")
        sample = orphans[:20]
        for eid in sample:
            print(f"  would retract {eid}")
        if len(orphans) > len(sample):
            print(f"  ... and {len(orphans) - len(sample)} more")
        return 0

    failures = 0
    for i, eid in enumerate(orphans):
        try:
            events = retract_one(sb, eid)
            data_quality_flags.raise_flag(
                sb,
                flag_kind=FLAG_KIND,
                severity="low",
                detected_by="retract_zero_event_entities",
                entity_id=eid,
                detail={"events_affected": events, "reason": "no live event"},
            )
        except Exception as e:
            failures += 1
            print(f"  ! failed {eid}: {e}", file=sys.stderr)
        if (i + 1) % 500 == 0:
            print(f"  ...{i + 1}/{len(orphans)} done")

    print(f"\n=== summary ===")
    print(f"retracted: {len(orphans) - failures}")
    print(f"failed:    {failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
```

**Step 4: Run test, expect pass.**
```bash
cd pipeline && python -m pytest tests/test_retract_zero_event_entities.py -v 2>&1 | tail -10
```
Expected: 2 passed.

**Step 5: Commit.**
```bash
git add pipeline/scripts/retract_zero_event_entities.py pipeline/tests/test_retract_zero_event_entities.py
git commit -m "feat(pipeline): retract_zero_event_entities — one-shot orphan cleanup"
```

---

## Task 13: Dry-run against prod

**What this does in plain English:** Run the script in safe-mode against the live database. No writes. Verify the count and sample matches our diagnosis (~18,566).

**Step 1: Load env and dry-run.**
```bash
export SUPABASE_URL=$(grep NEXT_PUBLIC_SUPABASE_URL web/.env.local | cut -d= -f2)
export SUPABASE_KEY=$(grep SUPABASE_SERVICE_ROLE_KEY web/.env.local | cut -d= -f2)
python3 -m pipeline.scripts.retract_zero_event_entities --dry-run 2>&1 | tail -30
```
Expected: `N orphaned active entities found` where N is ≈ 18,566 (within ±200). Sample output of 20 entity ids.

**Step 2: Sanity-check by spot-checking one.** Pick an entity id from the sample, query the DB to confirm it really has no live events.
```bash
SUP_KEY=$SUPABASE_KEY EID=<paste-id-from-sample>
curl -s "https://ntyhbapphnzlariakgrw.supabase.co/rest/v1/published_changes?entity_id=eq.$EID&is_retracted=eq.false&select=id" \
  -H "apikey: $SUP_KEY" -H "Authorization: Bearer $SUP_KEY"
```
Expected: `[]` (empty array).

**Step 3: No commit — verification only.**

If the count is way off (more than 1,000 off from 18,566), STOP and investigate before continuing.

---

## Task 14: Run for real

**What this does in plain English:** Execute the cleanup. ~18,566 entities flip to retracted. Their attached matched claims flip to pending (per the existing RPC cascade). Audit rows land in data_quality_flags.

**Step 1: Run in small chunks first.**
```bash
python3 -m pipeline.scripts.retract_zero_event_entities --limit 100 2>&1 | tail -20
```
Expected: `retracted: 100, failed: 0`.

**Step 2: Verify counts moved.**
```bash
SUP_KEY=$SUPABASE_KEY
curl -sI "https://ntyhbapphnzlariakgrw.supabase.co/rest/v1/data_quality_flags?flag_kind=eq.zero_event_entity_swept&select=id" \
  -H "apikey: $SUP_KEY" -H "Authorization: Bearer $SUP_KEY" -H "Prefer: count=exact" -H "Range: 0-0" | grep -i content-range
```
Expected: `content-range: */100`.

**Step 3: Run the rest.**
```bash
python3 -m pipeline.scripts.retract_zero_event_entities 2>&1 | tail -10
```
Expected: `retracted: ~18,466, failed: 0` (the 100 already done are skipped — actually they ARE re-processed because the script is set-diff-based and they're already retracted; the RPC call is a no-op; the raise_flag returns None on duplicate). All idempotent.

**Step 4: Verify end-state counts.**
```bash
SUP_KEY=$SUPABASE_KEY
URL="https://ntyhbapphnzlariakgrw.supabase.co/rest/v1"
echo "Active entities (should be ~2,306):"
curl -sI "$URL/product_entities?select=id&is_retracted=eq.false" \
  -H "apikey: $SUP_KEY" -H "Authorization: Bearer $SUP_KEY" -H "Prefer: count=exact" -H "Range: 0-0" | grep -i content-range
echo "Entities with live events (should still be 2,306):"
curl -s "$URL/event_evidence_summary?select=entity_id" -H "apikey: $SUP_KEY" -H "Authorization: Bearer $SUP_KEY" -H "Range: 0-0" -H "Prefer: count=exact" 2>&1 | grep -i content-range
echo "Pending claims (likely jumped from 2,527):"
curl -sI "$URL/claims?select=id&status=eq.pending" -H "apikey: $SUP_KEY" -H "Authorization: Bearer $SUP_KEY" -H "Prefer: count=exact" -H "Range: 0-0" | grep -i content-range
```
Expected: active entities count ≈ 2,306; pending claims has grown (founder should now go use /admin/claims/groups).

**Step 5: Spot-check Quality Street Tin specifically.**
```bash
EID=e6d6e92e-aef8-4ddb-b2d1-e2fcd07284ee
curl -s "https://ntyhbapphnzlariakgrw.supabase.co/rest/v1/product_entities?id=eq.$EID&select=id,brand,canonical_name,is_retracted" \
  -H "apikey: $SUPABASE_KEY" -H "Authorization: Bearer $SUPABASE_KEY"
```
Expected: `is_retracted: true`.

**Step 6: Update project status memory.** Add a line to `~/.claude/projects/-Users-thoroxnard-Documents-Fullcarts/memory/project_status.md` recording the sweep counts. (Memory write — no git commit.)

---

# Deliverable 3: Forward invariant

## Task 15: Page-layer guards on /products and /brands

**What this does in plain English:** If somehow an entity-without-live-events slips through (legacy state, future bug, view drift), the page must 404 rather than render empty. Ships before the DB trigger so we get protection even if the trigger has a bug.

**Files:**
- Modify: `web/src/app/products/[id]/page.tsx`
- Modify: `web/src/app/brands/[name]/page.tsx`

**Step 1: Read both pages to find the right insertion point.**
```bash
head -30 web/src/app/products/\[id\]/page.tsx
head -30 web/src/app/brands/\[name\]/page.tsx
```
Goal: find the first place after data is loaded where we know event count is zero, and call `notFound()` there.

**Step 2: Add the guard to /products/[id]/page.tsx.**

After the existing `event_evidence_summary` select (line ~76), check if the result is empty and `notFound()` if so. Concretely:
```tsx
// After: const { data: events } = await sb.from("event_evidence_summary")...
if (!events || events.length === 0) {
  notFound();
}
```
Make sure `import { notFound } from "next/navigation";` is present at the top.

**Step 3: Add the guard to /brands/[name]/page.tsx.**

After the existing `event_evidence_summary` select (line ~59), same pattern:
```tsx
if (!events || events.length === 0) {
  notFound();
}
```
Add the import if missing.

**Step 4: Type-check.**
```bash
cd web && pnpm exec tsc --noEmit 2>&1 | tail -5
```

**Step 5: Local verify.**
```bash
cd web && pnpm dev
```
In browser:
- Visit http://localhost:3000/products/e6d6e92e-aef8-4ddb-b2d1-e2fcd07284ee (Quality Street tin). Expected: 404 page (Next's default not-found).
- Visit http://localhost:3000/products/<a known live entity id> — expected: full page renders.

**Step 6: Commit.**
```bash
git add web/src/app/products/\[id\]/page.tsx web/src/app/brands/\[name\]/page.tsx
git commit -m "feat(web): notFound() guard for entities/brands with zero live events"
```

---

## Task 16: Migration 069 — orphan-entity trigger

**What this does in plain English:** Database-level safety net. The moment an event is retracted, check if its parent entity has any other live events. If not, auto-retract the entity in the same transaction.

**Files:**
- Create: `db/migrations/069_orphan_entity_trigger.sql`

**Step 1: Write the migration.**

Create `db/migrations/069_orphan_entity_trigger.sql`:
```sql
-- 069_orphan_entity_trigger.sql
--
-- Forward invariant for Phase A (design doc: 2026-05-20-admin-claim-streamlining-design.md).
-- When the last live event of an entity is retracted, retract the
-- parent entity too. Reuses set_entity_retracted from migration 062.
--
-- Idempotent: trigger fires only on transitions false -> true.
-- Safe with the Phase A cleanup script — the script calls
-- set_entity_retracted directly, which cascades to events; those event
-- updates fire this trigger; the trigger then calls set_entity_retracted
-- AGAIN on the (now already-retracted) entity, which is a no-op.

CREATE OR REPLACE FUNCTION trg_retract_orphaned_entity()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    IF NEW.is_retracted = true
       AND COALESCE(OLD.is_retracted, false) = false
       AND NEW.entity_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1
              FROM published_changes
             WHERE entity_id = NEW.entity_id
               AND is_retracted = false
               AND id <> NEW.id
        ) THEN
            PERFORM set_entity_retracted(NEW.entity_id, true);
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS published_changes_orphan_check ON published_changes;

CREATE TRIGGER published_changes_orphan_check
AFTER UPDATE OF is_retracted ON published_changes
FOR EACH ROW
EXECUTE FUNCTION trg_retract_orphaned_entity();

COMMENT ON FUNCTION trg_retract_orphaned_entity() IS
    'Phase A invariant: retract parent entity when its last live event is retracted.';
```

**Step 2: Commit.**
```bash
git add db/migrations/069_orphan_entity_trigger.sql
git commit -m "feat(db): migration 069 — auto-retract entity when last live event is retracted"
```

---

## Task 17: Apply migration 069 to prod

**What this does in plain English:** Deploy the migration via Supabase Management API (the project's standard pattern per CLAUDE.md).

**Step 1: Prepare the SQL payload.** The Management API accepts a single `query` field with full SQL.

**Step 2: POST it.**
```bash
SUPA_PAT=<paste your Supabase Personal Access Token here>
PROJECT_REF=ntyhbapphnzlariakgrw
SQL=$(cat db/migrations/069_orphan_entity_trigger.sql)
curl -s -X POST "https://api.supabase.com/v1/projects/$PROJECT_REF/database/query" \
  -H "Authorization: Bearer $SUPA_PAT" \
  -H "Content-Type: application/json" \
  -H "User-Agent: claude-code/phase-A" \
  -d "$(jq -n --arg q "$SQL" '{query:$q}')"
```
Expected: `[]` or empty success response. The `User-Agent` header is critical — Cloudflare returns 1010 without it (per CLAUDE.md gotcha).

**Step 3: Verify the trigger exists.**
```bash
SQL='SELECT tgname FROM pg_trigger WHERE tgname = '\''published_changes_orphan_check'\'';'
curl -s -X POST "https://api.supabase.com/v1/projects/$PROJECT_REF/database/query" \
  -H "Authorization: Bearer $SUPA_PAT" -H "Content-Type: application/json" -H "User-Agent: claude-code/phase-A" \
  -d "$(jq -n --arg q "$SQL" '{query:$q}')"
```
Expected: `[{"tgname":"published_changes_orphan_check"}]`.

**Step 4: No commit.**

---

## Task 18: Test the trigger end-to-end

**What this does in plain English:** Do one real retraction via the existing admin "retract event" button (or directly via SQL) on an entity that has only one live event. Confirm the entity itself gets retracted by the trigger.

**Step 1: Find a candidate.** Pick a known entity that has exactly one live event.
```bash
SUP_KEY=$SUPABASE_KEY
URL="https://ntyhbapphnzlariakgrw.supabase.co/rest/v1"
# Find an entity with exactly 1 live event:
curl -s "$URL/rpc/find_single_event_entities" \
  -H "apikey: $SUP_KEY" -H "Authorization: Bearer $SUP_KEY"
```
If that RPC doesn't exist (likely), use a SQL query via Management API:
```bash
SQL="SELECT entity_id, COUNT(*) c FROM published_changes WHERE is_retracted=false GROUP BY entity_id HAVING COUNT(*)=1 LIMIT 1;"
curl -s -X POST "https://api.supabase.com/v1/projects/$PROJECT_REF/database/query" \
  -H "Authorization: Bearer $SUPA_PAT" -H "Content-Type: application/json" -H "User-Agent: claude-code/phase-A" \
  -d "$(jq -n --arg q "$SQL" '{query:$q}')"
```
Pick a test entity that the founder agrees is safe to retract (or work in staging if available).

**Step 2: Note the entity id.** Call it `$TEST_EID`.

**Step 3: Confirm entity is currently active.**
```bash
curl -s "$URL/product_entities?id=eq.$TEST_EID&select=is_retracted" \
  -H "apikey: $SUP_KEY" -H "Authorization: Bearer $SUP_KEY"
```
Expected: `[{"is_retracted":false}]`.

**Step 4: Retract the event (NOT the entity) via SQL.**
```bash
SQL="UPDATE published_changes SET is_retracted=true WHERE entity_id='$TEST_EID' AND is_retracted=false;"
curl -s -X POST "https://api.supabase.com/v1/projects/$PROJECT_REF/database/query" \
  -H "Authorization: Bearer $SUPA_PAT" -H "Content-Type: application/json" -H "User-Agent: claude-code/phase-A" \
  -d "$(jq -n --arg q "$SQL" '{query:$q}')"
```

**Step 5: Re-check the entity.**
```bash
curl -s "$URL/product_entities?id=eq.$TEST_EID&select=is_retracted" \
  -H "apikey: $SUP_KEY" -H "Authorization: Bearer $SUP_KEY"
```
Expected: `[{"is_retracted":true}]` — proving the trigger fired.

**Step 6: If you want to restore that entity for the founder**, use `/admin/entities` → search the id → toggle retract back to false. Or via SQL:
```bash
SQL="SELECT set_entity_retracted('$TEST_EID', false);"
curl -s -X POST "https://api.supabase.com/v1/projects/$PROJECT_REF/database/query" \
  -H "Authorization: Bearer $SUPA_PAT" -H "Content-Type: application/json" -H "User-Agent: claude-code/phase-A" \
  -d "$(jq -n --arg q "$SQL" '{query:$q}')"
```

**Step 7: No commit — verification only.**

---

## Task 19: Deploy frontend with guards

**What this does in plain English:** Push, open PR, merge, deploy. After this, the `notFound()` guards are live.

**Step 1: Push branch.**
```bash
git push -u origin claude/jovial-cerf-6bb9cc
```

**Step 2: Open PR.**
```bash
gh pr create --title "feat(web,db): Phase A — orphan-entity guards + trigger" --body "$(cat <<'EOF'
## Summary
- /products/[id] and /brands/[name] now return 404 when entity/brand has zero live events
- Migration 069: AFTER UPDATE trigger on published_changes that auto-retracts orphaned parent entities
- Together with the cleanup pass in this phase, makes the "nothing public without a live claim" rule enforceable forward-going

## Test plan
- [ ] Visit /products/e6d6e92e-aef8-4ddb-b2d1-e2fcd07284ee on preview — expect 404
- [ ] Visit a known-live product page — expect full render
- [ ] Confirm migration 069 applied (trigger exists in pg_trigger)
- [ ] Retraction of last-live event auto-retracts the entity

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

**Step 3: Merge after founder approval.**
```bash
gh pr merge --squash --delete-branch
git checkout main && git pull
```

**Step 4: Deploy to prod.**
```bash
cd /Users/thoroxnard/Documents/Fullcarts/web && \
  ./node_modules/.bin/vercel deploy --prod --cwd .. \
  --token=<PAT> --yes --scope fullcarts89s-projects 2>&1 | tail -10
```

**Step 5: Verify guard on prod.**
```bash
curl -sI https://www.fullcarts.org/products/e6d6e92e-aef8-4ddb-b2d1-e2fcd07284ee | head -3
```
Expected: HTTP/2 404.

---

## Task 20: Final sweep + memory update

**What this does in plain English:** Final pass: verify the public site, update memory so the next session has the current state.

**Step 1: Spot-check public surfaces.**
```bash
curl -sI https://www.fullcarts.org/ | head -3
curl -sI https://www.fullcarts.org/brands | head -3
curl -sI https://www.fullcarts.org/products | head -3
curl -sI https://www.fullcarts.org/insights | head -3
```
Expected: all 200.

**Step 2: Confirm post-Phase-A invariant.**
```bash
SQL="SELECT COUNT(*) FROM product_entities WHERE is_retracted=false AND NOT EXISTS (SELECT 1 FROM published_changes pc WHERE pc.entity_id=product_entities.id AND pc.is_retracted=false);"
curl -s -X POST "https://api.supabase.com/v1/projects/$PROJECT_REF/database/query" \
  -H "Authorization: Bearer $SUPA_PAT" -H "Content-Type: application/json" -H "User-Agent: claude-code/phase-A" \
  -d "$(jq -n --arg q "$SQL" '{query:$q}')"
```
Expected: `[{"count":0}]`.

**Step 3: Update project status memory.** Append to `~/.claude/projects/-Users-thoroxnard-Documents-Fullcarts/memory/project_status.md` a new section "Phase A shipped (2026-05-20)" with: counts before/after, PR numbers, migration 069 applied, founder-action queue size (post-cleanup pending claims).

**Step 4: Notify the founder.** Tell them:
- Cleanup is live, pending queue is now ~N claims
- Group view is live at https://www.fullcarts.org/admin/claims/groups
- They can start clearing the queue whenever they like

---

# Execution handoff

Plan complete and saved to `docs/plans/2026-05-20-admin-claim-streamlining-plan.md`. Two execution options:

**1. Subagent-Driven (this session)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Best for staying responsive to mid-flight corrections.

**2. Parallel Session (separate)** — Open a new session with `executing-plans`, batch execution with checkpoints. Best for hands-off completion of a known-good plan.

**Which approach?**
