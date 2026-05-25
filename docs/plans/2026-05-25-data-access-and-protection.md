# Data Access, Protection & Monetization — Decision Record

**Date:** May 25, 2026
**Status:** Decided. Execution pending (see "Now" checklist).
**Context:** Founder concern about competitors scraping the FullCarts database and
republishing hard-won insights. This doc records the decisions reached and the
threat-model finding that reordered the priorities.

---

## Guiding principle

**Control bulk access; keep individual access wide open.** At this stage,
obscurity is a bigger threat than theft — the entire growth strategy (social
content engine, SEO-friendly brand/product pages) depends on maximum reach.
Nothing here should reduce reach. We win by being the *canonical, fastest, most
comprehensive source everyone cites*, not the source nobody can copy. The facts
themselves (e.g. "Cadbury 80g → 72g") are public and re-derivable, so they can't
be owned; the moat is the pipeline (private), the brand, velocity, and audience.

---

## The finding that reordered everything

Public pages render server-side and don't ship a browser Supabase client for data
— but that is **not** where the exposure is. RLS policies in
`db/migrations/002_rls_policies.sql` grant public read with `USING (true)` on:

- `product_entities`
- `pack_variants`
- `variant_observations`
- `evidence_files`
- `published_changes` (non-retracted)

The Supabase anon key is public **by design**. So today anyone can bypass the
website entirely:

```
https://ntyhbapphnzlariakgrw.supabase.co/rest/v1/published_changes?select=*
```

…and pull the entire database as clean, paginated JSON. **This is the turnkey
theft vector.** The server-rendered frontend does not protect it, because the hole
is the Supabase REST API + permissive RLS, not the site. Closing this is priority #1.

---

## Decisions

### 1. Anti-scraping: FULL LOCKDOWN

Audit read paths first, then tighten RLS so `anon` cannot bulk-read tables; serve
public pages via the service-role client (`admin.ts`, server-only) or
`SECURITY DEFINER` RPCs; add edge rate-limiting; add a non-fabricated watermark.

- **Vector ranking:** (1) direct Supabase REST dump — CRITICAL; (2) HTML page
  scraping — LOW (it's the content we want indexed); (3) sitemap enumeration —
  LOW–MED (acceptable cost of SEO); (4) `/api/tips` — negligible (insert-only).
- **Prerequisite:** read-path audit — confirm whether public pages read via
  `server.ts` (anon key, would break on RLS tighten) or `admin.ts` (service role,
  safe). **Do not touch RLS until this audit is done.**
- **Defense-in-depth:** cap PostgREST response size (role `statement_timeout` +
  max-rows) so a misconfig can't leak a whole table in one call.
- **Edge:** rate-limit per IP (Vercel WAF / Cloudflare); allow Googlebot/Bingbot,
  throttle datacenter ranges + known scraper UAs.
- **Watermark caveat:** do NOT seed fake shrinkflation facts — it collides with the
  brand promise ("we never invent sizes"). Watermark a non-factual field (invisible
  token) or keep a not-public canary entity that never renders but appears in a
  naive table dump. Proof of copying without lying to the audience.
- **Accepted tradeoff:** cannot block all bots without killing SEO. Goal is "humans
  + search crawlers in, bulk extractors out," not a wall.

### 2. Monetization: GATE NOW, SELL LATER

Anti-scraping and monetization are the *same lever* — a scraper is a customer who
hasn't been shown a bill. Define the free/paid line now so the gate is built with a
future API in mind; **build no billing infra until post-launch demand exists.**

| Free (keep generous — drives reach/SEO/trust) | Paid (bulk/derived value = the theft vector) |
|---|---|
| All public pages, individual brand/product views | Programmatic **API** access, rate-tiered |
| `/insights` macro dashboard | **Bulk export** (full DB, historical time-series) |
| The social content | **Alerts/webhooks** (brand-shrink notifications) |
| Unlimited human browsing | Advanced analytics, custom ranges, redistribution license |

- **Buyers:** newsrooms/consumer-affairs desks, researchers/academics, CPG
  competitive-intelligence teams, investors/analysts, developers.
- **Mission tension:** keep the public-good layer genuinely free for individuals;
  frame paid tiers as "for newsrooms, researchers, and businesses."
- **Deferred:** Stripe, API keys, tier enforcement — built only when demand is proven.

### 3. Licensing: FREE TO CITE, LICENSE TO COPY

Journalists/researchers may cite freely **with attribution** (amplifies reach + the
"canonical source" position); commercial, bulk, or competing reuse requires a
license.

- US reality: facts aren't copyrightable, and *hiQ v. LinkedIn* weakened
  "scraping public data = unauthorized access." Enforcement levers are therefore
  **contract (ToS), copyright (expression), and trademark (brand)** — not access claims.

---

## Sequencing

### Now (cheap, pre-launch, high-leverage)

- [ ] **Read-path audit** — map every public page's data source (`server.ts` vs
      `admin.ts` vs RPC). Report what breaks before any RLS change. *(First task.)*
- [ ] **RLS lockdown** — deny `anon` bulk table reads; route public reads through
      service-role / `SECURITY DEFINER` RPCs.
- [ ] **PostgREST hardening** — statement timeout + max-rows on the public role.
- [ ] **Edge rate-limiting** — Vercel WAF / Cloudflare; allowlist search crawlers.
- [ ] **Watermark** — non-fabricated canary (invisible token or not-public entity).
- [ ] **Terms of Service** — prohibit scraping, bulk extraction, commercial reuse
      without license. (The contract enabling takedowns.)
- [ ] **Copyright notice** — site footer; protects expression.
- [ ] **DMCA agent registration** — ~$6 with the Copyright Office; the practical
      takedown tool.
- [ ] **Trademark filing** — "FullCarts" + logo (~$250–350/class USPTO). Start now
      for the months-long lead time.
- [ ] **Attribution stance** — publish the "free to cite with attribution / license
      to copy" terms.

### Later (post-launch, demand-gated)

- [ ] Paid **API** (rate-tiered, API keys, Stripe billing).
- [ ] **Bulk export** + historical time-series download.
- [ ] **Alerts/webhooks** for tracked-brand shrink events.
- [ ] Advanced analytics tier + redistribution licensing.

---

## On-brand enforcement note

If a competitor lifts the whole database and passes it off as theirs, that is
*content*: "this site copied our entire shrinkflation record without credit" is
exactly the accountability story the brand exists to tell, in the DCC voice. A
thief becomes a reach event.
