# Community Submissions → Claims Queue — Design

**Date:** 2026-06-10
**Status:** Approved, ready for implementation plan

## Problem

FullCarts has no first-class way for the public to report a shrinkflation
event. A `tips` table + `<TipForm />` card exist on `/about`, but tips land in
a table with **no admin review surface** (a write-only black hole) and never
become claims or published events. Discovery is also poor — the form is buried
in `/about`.

## Goal

Let users submit a shrinkflation event from a dedicated page. Each submission
becomes an ordinary **`pending` claim** that rides the existing
approve → promote → published pipeline. Keep the data model consistent: a
community submission is just another claim, identical in shape to a scraped one.

## Decisions (locked)

- **Dedicated `/submit` page** is the headline deliverable.
- **Tip → claim**, with the admin approving via the **existing** `/admin/claims`
  queue. No separate `/admin/tips` triage surface, no new claim status values.
- **Top-of-queue**: community `pending` claims sort first by default.
- **Consolidate**: replace the `/about` `TipForm` card with a CTA to `/submit`.

## Architecture

### Data model consistency (the key constraint)

`claims.raw_item_id` is `NOT NULL` — every claim must anchor to a `raw_items`
row (the immutable evidence locker). So a submission writes **two rows** in one
request, exactly like every scraper does:

1. `raw_items`: `source_type='community_submission'`, `source_id=<uuid>`,
   `raw_payload` = the submission JSON. This is the evidence anchor.
2. `claims`: `status='pending'`, `extractor_version='community-v1'`,
   brand/product/sizes/description copied across, `confidence` JSONB stamped
   `{"source":"community", ...}` for downstream identification.

No schema migration is required — `claims` and `raw_items` already carry every
needed column, and provenance lives in `source_type` + `confidence`. We honor
the project rule of **not adding new values to `claims_status_check`**.

### Components

**1. Public `/submit` page** — `web/src/app/submit/page.tsx` (Static; renders
`<SiteNav />`). Hero + mission framing, a worked example of a good submission,
and a "what happens next" note. Hosts a `SubmissionForm` client component.

**2. `SubmissionForm`** — fields mapping 1:1 onto `claims` columns:
- Brand (required), Product (required)
- Old size + unit, New size + unit (the core event)
- Old price / New price (optional)
- Evidence URL (optional)
- "What changed?" free-text description (required)

Client-side validation mirrors the server. Reuses the localStorage
`session_id` pattern from `TipForm` for dedup.

**3. `POST /api/submit`** route handler — abuse defenses carried over from
`/api/tips` (8 KB body cap, IP hashing, 60 s per-session dedup). Inserts the
`raw_items` row then the `claims` row. Returns `{ ok, session_id }`.

**4. Claims queue surfacing** (`/admin/claims`) — three small touches:
- Extend the `SourceBadge` map with a distinct **"Community"** chip.
- Add **Community** to the existing source-filter chips.
- Default secondary sort so community `pending` claims float to the top.

**5. Nav + `/about`** — add **Submit** to `SiteNav`; replace the `/about`
`TipForm` card with a CTA linking to `/submit`.

## Data flow

```
User → /submit (SubmissionForm)
  → POST /api/submit
    → raw_items (source_type='community_submission')   [evidence anchor]
    → claims (status='pending', extractor_version='community-v1')
  → /admin/claims pending queue (Community badge, sorted to top)
  → admin approves → promote_claims → published_changes
```

## Abuse posture

Submissions are anonymous but **gated** — nothing is public until the founder
approves the claim. Spam lands as `pending` and is discarded in the normal
review flow. Rate-limiting + IP hashing carry over from the tips endpoint.

## Retired surfaces

The legacy `tips` table and `POST /api/tips` go dormant (no destructive
migration). The `TipForm` component is superseded by `SubmissionForm`. Left in
place and noted as retired.

## Out of scope (YAGNI)

- Photo/file upload (the `evidence_files` FK stays unused for now).
- Public "community wall" of accepted submissions.
- AI auto-extraction of submissions (admin structures via the form instead).
- Submitter accounts / auth.
