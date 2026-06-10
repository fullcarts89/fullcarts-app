# Community Submissions Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Let the public submit a shrinkflation event from a dedicated `/submit` page; each submission becomes an ordinary `pending` claim that rides the existing approve → promote pipeline.

**Architecture:** A `/submit` page hosts a `SubmissionForm` that POSTs to `/api/submit`. The route writes two rows — a `raw_items` evidence anchor (`source_type='community_submission'`) and a `pending` `claims` row pointing at it (satisfying the `claims.raw_item_id NOT NULL` invariant). Provenance lives entirely in `raw_items.source_type`, so the existing `/admin/claims` queue surfaces and approves submissions with no new status values and no DB migration.

**Tech Stack:** Next.js App Router (server components + client form), Supabase (service-role admin client), TypeScript. Python 3.9 target elsewhere is irrelevant here. No web test runner exists — verification is `npm run lint`, `npm run build`, and `curl` smoke tests.

**Conventions to honor (from CLAUDE.md):**
- Admin mutations that must not refresh the calling page use **route handlers**, not Server Actions. `/api/submit` is a public route handler — fine.
- **Never** add values to `claims_status_check`. We only ever write `status='pending'`.
- No `X | Y` / `dict[]` typing concerns here (TS, not Python).

---

### Task 1: Submission API route handler

**Files:**
- Create: `web/src/app/api/submit/route.ts`
- Reference (copy abuse-defense patterns): `web/src/app/api/tips/route.ts`

**Step 1: Write the route handler**

```typescript
// Public community-submission endpoint.
//
// A submission becomes an ordinary `pending` claim, identical in shape to a
// scraped one. Because `claims.raw_item_id` is NOT NULL (the immutable
// evidence locker), we write TWO rows per submission — exactly like every
// scraper does:
//   1. raw_items  — source_type='community_submission', the evidence anchor
//   2. claims     — status='pending', extractor_version='community-v1'
//
// Provenance is carried by raw_items.source_type, so /admin/claims identifies
// and filters these with its existing source machinery. No new claim status.
//
// Abuse defenses mirror /api/tips: 8 KB body cap, IP hashing, 60 s per-session
// dedup. Submissions are anonymous but gated — nothing is public until an admin
// approves the claim.
import { NextRequest, NextResponse } from "next/server";
import { createHash, randomUUID } from "crypto";
import { createAdminClient } from "@/lib/supabase/admin";

export const dynamic = "force-dynamic";

const MAX_DESCRIPTION = 4000;
const MAX_FIELD = 200;
const MAX_UNIT = 16;

function clamp(s: unknown, max: number): string {
  if (typeof s !== "string") return "";
  return s.trim().slice(0, max);
}

function toNum(v: unknown): number | null {
  if (typeof v === "number" && isFinite(v)) return v;
  if (typeof v === "string" && v.trim() !== "") {
    const n = Number(v);
    if (isFinite(n)) return n;
  }
  return null;
}

function hashIp(req: NextRequest): string {
  const fwd = req.headers.get("x-forwarded-for") || "";
  const ip = fwd.split(",")[0].trim() || "0.0.0.0";
  return createHash("sha256").update(ip).digest("hex").slice(0, 24);
}

export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    const text = await req.text();
    if (text.length > 8000) {
      return NextResponse.json({ error: "Payload too large" }, { status: 413 });
    }
    body = JSON.parse(text);
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }
  if (!body || typeof body !== "object") {
    return NextResponse.json({ error: "Invalid body" }, { status: 400 });
  }

  const b = body as Record<string, unknown>;
  const brand = clamp(b.brand, MAX_FIELD);
  const product_name = clamp(b.product_name, MAX_FIELD);
  const description = clamp(b.description, MAX_DESCRIPTION);

  if (!brand) {
    return NextResponse.json({ error: "Brand is required" }, { status: 400 });
  }
  if (!product_name) {
    return NextResponse.json({ error: "Product is required" }, { status: 400 });
  }
  if (!description || description.length < 10) {
    return NextResponse.json(
      { error: "Description must be at least 10 characters" },
      { status: 400 },
    );
  }

  const old_size = toNum(b.old_size);
  const new_size = toNum(b.new_size);
  const old_size_unit = clamp(b.old_size_unit, MAX_UNIT) || null;
  const new_size_unit = clamp(b.new_size_unit, MAX_UNIT) || null;
  const old_price = toNum(b.old_price);
  const new_price = toNum(b.new_price);
  const session_id = clamp(b.session_id, 64) || randomUUID();

  // Optional evidence URL — reject obvious junk, don't be exhaustive.
  const evidence_url_raw = clamp(b.evidence_url, MAX_FIELD * 4);
  let evidence_url: string | null = null;
  if (evidence_url_raw) {
    try {
      const u = new URL(evidence_url_raw);
      if (u.protocol === "http:" || u.protocol === "https:") {
        evidence_url = u.toString();
      } else {
        throw new Error("bad protocol");
      }
    } catch {
      return NextResponse.json(
        { error: "Evidence URL must be a valid http(s) URL" },
        { status: 400 },
      );
    }
  }

  const ip_hash = hashIp(req);
  const sb = createAdminClient();

  // De-dup: same session within 60 s → 429, so a double-click can't double-post.
  // We look for a recent community raw_item from this session.
  const sixtySecondsAgo = new Date(Date.now() - 60_000).toISOString();
  const { data: recent } = await sb
    .from("raw_items")
    .select("id, fetched_at")
    .eq("source_type", "community_submission")
    .eq("source_id", `session:${session_id}`)
    .gte("fetched_at", sixtySecondsAgo)
    .limit(1);
  if (recent && recent.length > 0) {
    return NextResponse.json(
      { error: "Slow down — we already received a submission from you in the last minute." },
      { status: 429 },
    );
  }

  // 1. Evidence anchor. source_id is unique per submission so we never collide
  //    with the (source_type, source_id) dedup index. We also stash the session
  //    marker as a second row keyed by session for the 60 s rate-limit check.
  const submissionId = randomUUID();
  const rawPayload = {
    kind: "community_submission",
    brand,
    product_name,
    description,
    old_size,
    old_size_unit,
    new_size,
    new_size_unit,
    old_price,
    new_price,
    evidence_url,
    session_id,
    ip_hash,
  };

  const { data: rawRow, error: rawErr } = await sb
    .from("raw_items")
    .insert({
      source_type: "community_submission",
      source_id: submissionId,
      source_url: evidence_url,
      raw_payload: rawPayload,
    })
    .select("id")
    .single();
  if (rawErr || !rawRow) {
    console.error("submission raw_items insert failed:", rawErr);
    return NextResponse.json(
      { error: "Could not save submission — please try again later." },
      { status: 500 },
    );
  }

  // Rate-limit marker row keyed by session (best-effort; ignore failure).
  await sb
    .from("raw_items")
    .insert({
      source_type: "community_submission",
      source_id: `session:${session_id}`,
      raw_payload: { marker: true, ts: Date.now() },
    });

  // 2. The claim. status='pending', modest confidence so the auto-approve cron
  //    (threshold 90) never publishes it unreviewed. confidence stays numeric —
  //    provenance is carried by raw_items.source_type.
  const { error: claimErr } = await sb.from("claims").insert({
    raw_item_id: rawRow.id,
    extractor_version: "community-v1",
    brand,
    product_name,
    old_size,
    old_size_unit,
    new_size,
    new_size_unit,
    old_price,
    new_price,
    change_description: description,
    confidence: { brand: 0.6, product_name: 0.6, size_change: 0.5, overall: 0.5 },
    status: "pending",
  });
  if (claimErr) {
    console.error("submission claims insert failed:", claimErr);
    return NextResponse.json(
      { error: "Could not save submission — please try again later." },
      { status: 500 },
    );
  }

  return NextResponse.json({ ok: true, session_id });
}
```

**Step 2: Confirm the `raw_items` column names**

Before trusting the insert, verify the real `raw_items` column names (the payload column is `raw_payload`, and the timestamp column — `fetched_at` vs `created_at`). Run:

```bash
grep -n -A20 "CREATE TABLE raw_items" db/migrations/001_foundation.sql
```

Expected: a `raw_payload JSONB` column and a timestamp column. **If the timestamp column is named differently** (e.g. `created_at`), update the two `fetched_at` references in the route. **If there is a UNIQUE `(source_type, source_id)` index**, the per-session marker row will collide on a repeat submit within the same session — that's fine, the marker insert is best-effort and wrapped to ignore failure, but confirm it doesn't throw. If it can throw, wrap it in try/catch or use `.upsert(..., { onConflict: "source_type,source_id", ignoreDuplicates: true })`.

**Step 3: Lint**

Run: `cd web && npm run lint`
Expected: PASS (no errors in the new file).

**Step 4: Smoke test the endpoint**

Start the dev server (`cd web && npm run dev`) in one shell, then:

```bash
# valid submission → 200 {"ok":true,...}
curl -s -X POST http://localhost:3000/api/submit \
  -H 'Content-Type: application/json' \
  -d '{"brand":"Cadbury","product_name":"Dairy Milk","old_size":"200","old_size_unit":"g","new_size":"180","new_size_unit":"g","description":"Bar shrank from 200g to 180g, same price."}'

# missing brand → 400
curl -s -X POST http://localhost:3000/api/submit \
  -H 'Content-Type: application/json' \
  -d '{"product_name":"X","description":"something happened here"}'

# immediate repeat with same session_id → 429
```

Expected: 200 then 400 then (on a fast repeat with a fixed `session_id`) 429. Then confirm in Supabase that a `raw_items` row (`source_type='community_submission'`) and a `claims` row (`status='pending'`, `extractor_version='community-v1'`) were created and linked.

**Step 5: Commit**

```bash
git add web/src/app/api/submit/route.ts
git commit -m "feat(web): community submission endpoint -> raw_items + pending claim"
```

---

### Task 2: SubmissionForm client component

**Files:**
- Create: `web/src/app/submit/_components/SubmissionForm.tsx`
- Create: `web/src/app/submit/styles.module.css`
- Reference (reuse session/localStorage + status-machine pattern): `web/src/app/about/_components/TipForm.tsx` and `web/src/app/about/styles.module.css`

**Step 1: Write the component**

Adapt `TipForm` to the structured-event shape. Key differences from `TipForm`:
- Brand and Product are **required** (not optional).
- Add a size row: `old_size` + `old_size_unit`, `new_size` + `new_size_unit`.
- Add an optional price row: `old_price`, `new_price`.
- Keep the free-text `description` (required, min 10 chars) and optional `evidence_url`.
- POST to `/api/submit` (not `/api/tips`).
- Reuse `getOrCreateSessionId()` verbatim but with key `"fc.submit.session_id"`.

```typescript
"use client";
// Public community-submission form. Lives on /submit. Posts to /api/submit,
// which creates a raw_items evidence anchor + a pending claim. Fields map 1:1
// onto claims columns so submissions arrive structured.
import { useRef, useState } from "react";
import styles from "../styles.module.css";

type Status = "idle" | "submitting" | "success" | "error";
const SESSION_KEY = "fc.submit.session_id";

function getOrCreateSessionId(): string {
  try {
    const existing = window.localStorage.getItem(SESSION_KEY);
    if (existing) return existing;
    const fresh =
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    window.localStorage.setItem(SESSION_KEY, fresh);
    return fresh;
  } catch {
    return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  }
}

export default function SubmissionForm() {
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const formRef = useRef<HTMLFormElement>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (status === "submitting") return;
    const fd = new FormData(e.currentTarget);
    const payload = {
      brand: String(fd.get("brand") || "").trim(),
      product_name: String(fd.get("product_name") || "").trim(),
      old_size: String(fd.get("old_size") || "").trim(),
      old_size_unit: String(fd.get("old_size_unit") || "").trim(),
      new_size: String(fd.get("new_size") || "").trim(),
      new_size_unit: String(fd.get("new_size_unit") || "").trim(),
      old_price: String(fd.get("old_price") || "").trim(),
      new_price: String(fd.get("new_price") || "").trim(),
      description: String(fd.get("description") || "").trim(),
      evidence_url: String(fd.get("evidence_url") || "").trim(),
      session_id: getOrCreateSessionId(),
    };

    if (!payload.brand || !payload.product_name) {
      setError("Brand and product are both required.");
      setStatus("error");
      return;
    }
    if (payload.description.length < 10) {
      setError("Please add at least a sentence describing what changed.");
      setStatus("error");
      return;
    }

    setStatus("submitting");
    setError(null);
    try {
      const res = await fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const j = (await res.json().catch(() => ({}))) as { error?: string };
        setError(j.error || "Submission failed — please try again.");
        setStatus("error");
        return;
      }
      setStatus("success");
      formRef.current?.reset();
    } catch {
      setError("Network error — please try again.");
      setStatus("error");
    }
  }

  if (status === "success") {
    return (
      <div className={`${styles["sub-form"]} ${styles["sub-form-success"]}`} role="status" aria-live="polite">
        <div className={styles["sub-form-status"]}>Submission received</div>
        <p>
          Thanks — this is now in the same review queue our scrapers feed. We&apos;ll
          cross-check it and publish it as an event if it holds up. Most submissions
          are reviewed within a week.
        </p>
        <button type="button" className={styles["sub-form-submit"]} onClick={() => setStatus("idle")}>
          Submit another
        </button>
      </div>
    );
  }

  return (
    <form ref={formRef} className={styles["sub-form"]} onSubmit={handleSubmit}
          aria-label="Submit a shrinkflation event" noValidate>
      <div className={styles["sub-form-row"]}>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-brand">Brand <span className={styles.req}>required</span></label>
          <input id="s-brand" name="brand" type="text" required placeholder="e.g. Cadbury" maxLength={200} autoComplete="off" />
        </div>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-product">Product <span className={styles.req}>required</span></label>
          <input id="s-product" name="product_name" type="text" required placeholder="e.g. Dairy Milk" maxLength={200} autoComplete="off" />
        </div>
      </div>

      <div className={styles["sub-form-row"]}>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-oldsize">Old size</label>
          <div className={styles["sub-form-inline"]}>
            <input id="s-oldsize" name="old_size" type="text" inputMode="decimal" placeholder="200" maxLength={16} autoComplete="off" />
            <input name="old_size_unit" type="text" placeholder="g" maxLength={16} autoComplete="off" aria-label="Old size unit" />
          </div>
        </div>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-newsize">New size</label>
          <div className={styles["sub-form-inline"]}>
            <input id="s-newsize" name="new_size" type="text" inputMode="decimal" placeholder="180" maxLength={16} autoComplete="off" />
            <input name="new_size_unit" type="text" placeholder="g" maxLength={16} autoComplete="off" aria-label="New size unit" />
          </div>
        </div>
      </div>

      <div className={styles["sub-form-row"]}>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-oldprice">Old price (optional)</label>
          <input id="s-oldprice" name="old_price" type="text" inputMode="decimal" placeholder="2.50" maxLength={16} autoComplete="off" />
        </div>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-newprice">New price (optional)</label>
          <input id="s-newprice" name="new_price" type="text" inputMode="decimal" placeholder="2.50" maxLength={16} autoComplete="off" />
        </div>
      </div>

      <div className={styles["sub-form-field"]}>
        <label htmlFor="s-desc">What changed? <span className={styles.req}>required</span></label>
        <textarea id="s-desc" name="description" rows={4} required minLength={10} maxLength={4000}
          placeholder="e.g. The bar dropped from 200g to 180g but the price stayed the same. I kept the old wrapper for comparison." />
      </div>

      <div className={styles["sub-form-field"]}>
        <label htmlFor="s-url">Link to evidence (optional)</label>
        <input id="s-url" name="evidence_url" type="url" inputMode="url" maxLength={800} autoComplete="off"
          placeholder="https://… Reddit post, news article, retailer page, photo" />
      </div>

      {error && status === "error" && (
        <div className={styles["sub-form-error"]} role="alert">{error}</div>
      )}

      <div className={styles["sub-form-actions"]}>
        <button type="submit" className={styles["sub-form-submit"]} disabled={status === "submitting"}>
          {status === "submitting" ? "Sending…" : "Submit event"}
        </button>
        <div className={styles["sub-form-note"]}>
          Submissions enter the same review queue our scrapers feed. We&apos;ll credit
          you on the event unless you ask us not to.
        </div>
      </div>
    </form>
  );
}
```

**Step 2: Write the CSS module**

Copy `web/src/app/about/styles.module.css` tip-form rules into `web/src/app/submit/styles.module.css`, renaming the `tip-form*` class prefix to `sub-form*` and adding `.sub-form-inline` (a flex row, gap ~8px, first input `flex:1`) plus `.req` (small muted label). Match the dark-graphite / Space Grotesk aesthetic from `FULLCARTS_DESIGN_EXPORT.md`. Read the about CSS first:

```bash
grep -n "tip-form\|\.req\|tip-card" web/src/app/about/styles.module.css
```

**Step 3: Lint**

Run: `cd web && npm run lint`
Expected: PASS.

**Step 4: Commit**

```bash
git add web/src/app/submit/_components/SubmissionForm.tsx web/src/app/submit/styles.module.css
git commit -m "feat(web): structured community SubmissionForm component"
```

---

### Task 3: The `/submit` page

**Files:**
- Create: `web/src/app/submit/page.tsx`
- Reference (page shell, SiteNav usage, metadata): `web/src/app/about/page.tsx`

**Step 1: Write the page**

A Static server component that renders `<SiteNav />`, a hero (mission framing: "Spotted a shrink? Put it on the record."), a short "what makes a good submission" list (old vs new size, a photo or archived-listing link, same-price note), the `<SubmissionForm />`, and a "what happens next" line + the `mailto:fullcartsinfo@gmail.com` fallback. Export `metadata` (title `Submit a shrinkflation event · FullCarts`, description) mirroring the `/about` pattern. Match the page-shell classes used by `/about`.

**Step 2: Lint + build**

Run: `cd web && npm run lint && npm run build`
Expected: PASS; the build output lists `/submit` as a route.

**Step 3: Manual check**

`npm run dev`, open `http://localhost:3000/submit`, submit a valid event, confirm the success state renders and a `pending` claim appears in Supabase.

**Step 4: Commit**

```bash
git add web/src/app/submit/page.tsx
git commit -m "feat(web): dedicated /submit page"
```

---

### Task 4: Surface community submissions in the claims queue

**Files:**
- Modify: `web/src/components/admin/ClaimFilters.tsx:20-28` (SOURCES array)
- Modify: `web/src/app/admin/claims/page.tsx:103-118` (SourceBadge map) and add a count banner
- Reference: the `SourceBadge` config object and `loadCategories`/`Promise.all` stats block already in `page.tsx`

**Step 1: Add the Community source filter chip**

In `ClaimFilters.tsx`, add to the `SOURCES` array:

```typescript
  { value: "community_submission", label: "Community" },
```

**Step 2: Add the Community badge**

In `page.tsx` `SourceBadge` `config`, add:

```typescript
    community_submission: { label: "Community", color: "bg-pink-500/10 text-pink-400 border-pink-500/20" },
```

**Step 3: Add a pending-community count banner (the "top of queue" surface)**

In `page.tsx`, add one more query to the existing `Promise.all([...])` stats block (around line 200) that counts pending community claims via an inner join:

```typescript
    supabase
      .from("claims")
      .select("raw_items!inner(source_type)", { count: "exact", head: true })
      .eq("status", "pending")
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .eq("raw_items.source_type" as any, "community_submission"),
```

Destructure its `count` (e.g. `communityPendingRes`) and, when `> 0` and we're not already filtered to community, render a banner above the claim list linking to the filtered+sorted view:

```tsx
{communityPending > 0 && sourceFilter !== "community_submission" && (
  <a href="/admin/claims?status=pending&source=community_submission&sort=newest"
     className="block mb-4 px-4 py-3 rounded border border-pink-500/30 bg-pink-500/10 text-pink-300 text-sm">
    📨 {communityPending} pending community submission{communityPending === 1 ? "" : "s"} awaiting review →
  </a>
)}
```

**Step 4: Default community view to newest-first**

Confirm selecting the Community chip plus `sort=newest` shows freshest submissions on top — the banner link already sets `sort=newest`. No code change needed beyond the banner href; the existing sort machinery handles it.

**Step 5: Lint + build**

Run: `cd web && npm run lint && npm run build`
Expected: PASS.

**Step 6: Manual check**

With at least one pending community claim present, load `/admin/claims` (as admin) → the pink banner shows the count; clicking it filters to community, newest-first, each card showing the pink "Community" badge. Approve one and confirm it promotes normally.

**Step 7: Commit**

```bash
git add web/src/components/admin/ClaimFilters.tsx web/src/app/admin/claims/page.tsx
git commit -m "feat(admin): surface community submissions in claims queue (badge, filter, count banner)"
```

---

### Task 5: Navigation + /about consolidation

**Files:**
- Modify: `web/src/components/SiteNav.tsx:27-32` (LINKS array)
- Modify: `web/src/app/about/page.tsx:2,246-271` (replace TipForm card with a CTA)

**Step 1: Add Submit to the nav**

In `SiteNav.tsx` `LINKS`, add (after Products or at the end before About — pick placement that reads well):

```typescript
  { href: "/submit", label: "Submit" },
```

**Step 2: Replace the /about TipForm card with a CTA**

In `about/page.tsx`, remove the `import TipForm` line and replace the `<div className={styles["tip-card"]}> … </div>` block (containing `<TipForm />`) with a prominent CTA linking to `/submit`, keeping the surrounding `<section id="contact">` lede and the `mailto:` fallback. Example:

```tsx
<a href="/submit" className={styles["tip-cta"] /* or reuse an existing button class */}>
  Submit a shrinkflation event →
</a>
```

Add a `.tip-cta` rule to `about/styles.module.css` if no suitable button class exists. Leave the `TipForm.tsx` file and `/api/tips` route in place (dormant, noted as retired in the design doc) — do not delete.

**Step 3: Lint + build**

Run: `cd web && npm run lint && npm run build`
Expected: PASS; no unused-import error for the removed `TipForm`.

**Step 4: Manual check**

Nav shows **Submit** and routes to `/submit`; `/about` now shows the CTA (no embedded form) and the email fallback still works.

**Step 5: Commit**

```bash
git add web/src/components/SiteNav.tsx web/src/app/about/page.tsx web/src/app/about/styles.module.css
git commit -m "feat(web): add Submit to nav; point /about tip card at /submit"
```

---

### Task 6: Docs + final verification

**Files:**
- Modify: `CLAUDE.md` (Web routes table + a one-line data-flow note)

**Step 1: Document the route and flow**

Add a `/submit` row to the Web routes table in `CLAUDE.md` and a sentence noting community submissions enter as `pending` claims with `raw_items.source_type='community_submission'`. Note that `tips` / `/api/tips` / `TipForm` are retired in favor of this path.

**Step 2: Full verification**

Run:
```bash
cd web && npm run lint && npm run build
```
Expected: both PASS; `/submit` appears in the route list.

**Step 3: End-to-end smoke**

Submit via the `/submit` UI → see it as a pending community claim in `/admin/claims` (pink banner + badge) → approve → confirm it flows to `published_changes` via the normal pipeline.

**Step 4: Commit + push**

```bash
git add CLAUDE.md
git commit -m "docs: document /submit community-submissions route + retired tips path"
git push -u origin claude/relaxed-faraday-l206l1
```

---

## Risks & notes

- **`raw_items` schema drift:** Task 1 Step 2 verifies the timestamp column name and the `(source_type, source_id)` uniqueness assumption before relying on them. Fix the route if they differ.
- **Auto-approve cron:** community claims are stamped `overall: 0.5` so `auto_approve_claims --threshold 90` never publishes them unreviewed. Do **not** raise this.
- **Spam:** anonymous but gated — nothing is public pre-approval; rate-limit + IP hash carry over. If volume becomes a problem, add a hard per-IP daily cap or a hCaptcha later (out of scope now).
- **No web test runner:** verification leans on `npm run lint`, `npm run build`, `curl`, and the manual end-to-end smoke. Introducing a test framework is out of scope.
```
