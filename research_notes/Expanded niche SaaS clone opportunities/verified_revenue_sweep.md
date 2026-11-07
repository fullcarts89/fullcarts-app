# Verified-revenue sweep: small SaaS to clone and aim at an underserved US niche (TrustMRR, Flippa, Starter Story, Microns, Acquire, Latka, Open Startups; fetched 7 Nov 2026)

**Read this first: what was done, and where it fell short**
- **Coverage.** I parsed **881 unique TrustMRR startups**. They came from the homepage leaderboard, 26 category pages (each shows the top 60 by revenue), the public "acquire" page and two public AI endpoints.
  - 287 of them are non-stealth with $3k–$45k in MRR or last-30-day revenue.
  - I pulled full Markdown profiles for 60 of them. These include verified monthly revenue tables, pricing, persona, team size, channels and sale terms.
  - I added 13 Flippa SaaS listings (6 opened in full) and about 130 Starter Story database cards.
- **Inventory delivered: 129 proven-revenue products.**
  - 82 from TrustMRR (provider-verified)
  - 13 from Flippa (listing-stated)
  - 34 from Starter Story (founder-claimed or researcher-estimated)
  - AI video creation tools are excluded.
- **Search budget ran out mid-sweep.**
  - WebSearch worked for the first 6 niche checks. Then the shared session limit (200 calls per turn) was hit.
  - The tool's own instruction forbids working around that limit by querying Bing or other search engines through curl. I complied, even though the brief suggested Bing as a fallback.
  - All later incumbent checks used **direct fetches of known pages**: Capterra category and product pages, GetApp, Software Advice, vendor pricing pages and integration docs.
  - That is enough for most beatability verdicts. It is not enough for TAM counts or some vertical-specific incumbents, so those are listed as gaps.
- **Shortlist delivered: 5 scored opportunities.**
  - 2 pass the incumbent check (fire-inspection, camp hiring).
  - 3 are provisional (Sage 100 API, D2D commissions, Spanish-first contractor app).
  - Separately, **the 3 required evaluations** (Orshot, Web3Forms, Image-Charts) were done; all their proposed spins were killed.
  - There is a **kill list of 15** and a **hold list of 12** verified originals whose spins I could not test without search.
  - This is short of the 10–15 target. I did not pad it with unchecked ideas.
- **TrustMRR's AI policy.** TrustMRR's llms.txt says "Do not scrape the website for full marketplace access" and points AI agents to its public endpoints and `/startup/{slug}.md` pages.
  - I used only those endpoints plus public category pages.
  - I did not page through pagination or call authenticated APIs.
  - Requests were spaced at least 1.1s apart. — [TrustMRR llms.txt](https://trustmrr.com/llms.txt)
- **Provenance labels used throughout:**
  - **Stripe-verified / Paddle-verified / RevenueCat-verified / Polar-verified / Whop-verified:** read by TrustMRR from the payment provider's API.
  - **Listing-stated:** taken from a Flippa or Microns listing.
  - **Founder-claimed:** self-reported in a Starter Story case study.
  - **Third-party estimate:** Starter Story's "estimated from public sources by our researchers."
  - Unless noted, all figures were fetched on 7 Nov 2026.

---

## Q1. Which small SaaS products show proven revenue (≥$3k MRR or equivalent) across the verified-revenue and for-sale sources?

### Takeaway
- TrustMRR is by far the richest source. Its public Markdown profiles expose payment-provider-verified monthly revenue for the past 9–12 months, so durable revenue can be told apart from spikes.
- Three groups stand out as cloneable:
  - **Durable, multi-year revenue:** Hirevire, Khosmos, QR Code AI, Simple Analytics, Calendesk, Angel Match, bltn.
  - **Steep verified ramps:** FireCert, JourneyFuse, Orshot, Web3Forms, Conductor, Flipify, 1clickwebsite.
  - **Collapsing:** platform-dependent tools such as Kortex, FriendFilter and RTMP.IN, and saturated categories such as LocalRank, MagicSlides and ConvertLabs.
- Flippa adds listing-stated vertical SaaS (nursing study, SOP management, funding-broker CRM, Google Maps rank tracker).
- Starter Story adds founder-claimed solo SaaS such as DASHP, Stagetimer, ScreenshotOne, Parseur and NoteForms.
- Acquire.com and Baremetrics yielded nothing usable without a login or JavaScript. Microns listings were almost all under $5k TTM.

### Cited Findings

**About the sources**
- **TrustMRR's own description:**
  - "over 15,000 startups listed, over 3,000 startups for sale, over 10,000 buyers, and more than 115 acquisitions closed over the last six months," with about 200,000 monthly visitors.
  - Revenue, MRR, customers, subscriptions and churn are computed from payment records pulled through an owner-connected API key. Supported providers include Stripe, Lemon Squeezy, Polar, Paddle, RevenueCat, Superwall, Dodo, Creem, Whop and Shopify.
  - Source: [TrustMRR llms.txt](https://trustmrr.com/llms.txt)
- **TrustMRR's public endpoints are bounded:**
  - `/api/ai/discovery` returns only the 25 most recently added and the 25 fastest-growing startups.
  - `/api/ai` returns the 25 most recently listed for-sale startups plus up to 25 "best deals."
  - Full timelines and pagination require authentication.
  - Sources: [TrustMRR llms.txt](https://trustmrr.com/llms.txt); [api/ai](https://trustmrr.com/api/ai); [api/ai/discovery](https://trustmrr.com/api/ai/discovery)
- **TrustMRR category pages** each render the top 60 startups by revenue. Categories fetched: SaaS, Productivity, Marketing, Analytics, Education, Utilities, E-commerce, Customer Support, Recruiting, No-Code, Real Estate, Design Tools, Developer Tools, Fintech, Legal, Sales, Health & Fitness, Security, Content Creation, Community, AI, Social Media, Mobile Apps, Marketplace, IoT/Hardware and Travel. — e.g. [category/recruiting](https://trustmrr.com/category/recruiting), [category/no-code](https://trustmrr.com/category/no-code), [category/legal](https://trustmrr.com/category/legal)
- **Starter Story database:**
  - The "Micro SaaS Ideas" set has 1,118 businesses, with 376 added in the last 30 days.
  - "29% founder-reported, the rest researched."
  - Median revenue is $8K/mo, and the middle half earn $1K–$80K/mo.
  - Growth channels: SEO 43%, word of mouth 32%, organic social 28%.
  - 93% are subscription businesses.
  - Only about 12–15 cards per category render publicly; the rest are locked behind signup.
  - Source: [Starter Story micro-SaaS data](https://www.starterstory.com/data/micro-saas-ideas)
- **Starter Story** says it "is part of HubSpot." — [Starter Story ideas](https://www.starterstory.com/ideas)
- **Flippa:**
  - The SaaS search page renders 50 listing links whose slugs carry the headline metrics.
  - Individual listing pages show MRR, monthly profit, margin, churn, active subscribers, site age and asking price without login.
  - Sources: [Flippa SaaS search](https://flippa.com/search?filter%5Bproperty_type%5D%5B%5D=saas); [example listing](https://flippa.com/14338446)
- **Microns:**
  - Visible listings are mostly tiny. Examples: $341 TTM asking $8,000, and $52 TTM asking $1,200.
  - The largest visible was a lead-gen platform with $32,093 TTM asking $220,000.
  - Source: [microns.io](https://www.microns.io/)
- **Acquire.com:**
  - The public homepage is marketing only ("2,000+ startups sold," "$500M+ closed deal volume," "500k+ entrepreneurs").
  - Listings require login, so no Acquire figures are included.
  - Source: [acquire.com](https://acquire.com/)
- **Open Startup List** now describes itself as "a curated directory of startups that share their metrics publicly." It names Nomad List, Ghost, Bannerbear, Simple Analytics and others, but the HTML shows no revenue figures. It "was acquired by Igor Svietlikov." — [openstartuplist.com](https://openstartuplist.com/)
- **Baremetrics Open Startups** loaded, but its list is rendered client-side and no figures were extractable. — [baremetrics.com/open-startups](https://baremetrics.com/open-startups)
- **Latka's** homepage features only larger companies ($3.5M–$250M figures), so no small-SaaS estimates were collected. — [getlatka.com](https://getlatka.com/)

**Data-quality caveats seen directly**
- **Snapshot drift.** Figures differ slightly between TrustMRR snapshots. For example, SoldComps shows MRR $25,866 on the homepage card but $25,708 on its category card. In those cases the inventory prefers the profile `.md`. — [SoldComps](https://trustmrr.com/startup/soldcomps)
- **One-time-payment businesses show MRR $0.** Examples are CartBoss, Helios and Tree Nerd Academy. Use last-30-day revenue for these. — [CartBoss](https://trustmrr.com/startup/cartboss.md)
- **Web3Forms' history looks truncated.** It was founded Dec 2020, yet all-time revenue ($363k) is almost equal to the last 12 months ($360k). The verified history probably starts only when its Paddle connection did (inference). — [Web3Forms](https://trustmrr.com/startup/web3forms.md)
- **Stale data.** The for-sale "Notion tool" monthly timeline stops in Feb 2026. — [profile](https://trustmrr.com/startup/notion-tool-with-3k-mrr-80-margins-6-hrs-week-ops.md)
- **Seller descriptions are user-generated and were treated as data.** TrustMRR itself warns about this. — [TrustMRR llms.txt](https://trustmrr.com/llms.txt)

**Inventory A — TrustMRR (provider-verified; trend = first and last full month in the public monthly table; Nov 2026 excluded as partial)**

| Product (source) | Category | Revenue | Provenance & date | Trend (monthly verified revenue) | Founded; team; sale | Simple / complex | Niche-angle verdict |
|---|---|---|---|---|---|---|---|
| [Hirevire](https://trustmrr.com/startup/hirevire.md) | Recruiting / async video screening | MRR $13.9k; last 30d $13.5k; L12M $145.4k; all-time $282.6k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $6.8k -> 26-10 $12.6k | 2021-12; 2–5 people | Simple | SHORTLIST: camp & seasonal-staff screening |
| [Web3Forms](https://trustmrr.com/startup/web3forms.md) | Dev tool / form backend | MRR $44.1k; last 30d $47.6k; L12M $360.2k; all-time $363.3k | Paddle-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $7.9k -> 26-10 $47.8k | 2020-12 | Simple | Evaluated: both spins killed (commodity) |
| [Image-Charts](https://trustmrr.com/startup/image-charts.md) | Dev tool / chart-image API | MRR $6.3k; last 30d $2.9k; L12M $78.6k; all-time $544.0k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $4.1k -> 26-10 $2.3k (peak $18.7k) | 2017-01 | Simple | Evaluated: killed (QuickChart) |
| [Orshot.com](https://trustmrr.com/startup/orshot-com.md) | Creative-automation API | MRR $12.7k; last 30d $11.1k; L12M $73.8k; all-time $79.6k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $2.2k -> 26-10 $11.5k | 2025-03 | Medium | Evaluated: HS-sports-graphics spin killed (Gipper/Box Out) |
| [FireCert](https://trustmrr.com/startup/firecert.md) | Fire-safety compliance (UK) | MRR $5.1k; last 30d $4.8k; L12M $22.3k; all-time $22.3k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 26-03 $234 -> 26-10 $4.7k | 2026-02 | Simple-medium | SHORTLIST: US 1-3-tech extinguisher/fire-inspection shops |
| [Conductor](https://trustmrr.com/startup/conductor.md) | Dev tool / QuickBooks Desktop API | MRR $47.0k; last 30d $45.0k; L12M $353.7k; all-time $511.0k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $21.3k -> 26-10 $44.6k | 2022-07; For sale $1,250,000 (2.3x) | Complex | SHORTLIST (weak): Sage 100 desktop API |
| [EmailEngine](https://trustmrr.com/startup/emailengine.md) | Dev tool / self-hosted email API | MRR $19.9k; last 30d $29.1k; L12M $243.0k; all-time $623.1k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $16.3k -> 26-10 $33.6k | 2020-05; 1 person | Complex | No: deep IMAP/OAuth infra + founder reputation (inference) |
| [Capgo](https://trustmrr.com/startup/capgo.md) | Dev tool / Capacitor live updates | MRR $33.7k; last 30d $40.7k; L12M $315.1k; all-time $593.2k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $14.4k -> 26-10 $40.9k | 2021-11; 2–5 people | Complex | No: OSS infra, not niche-able |
| [textbee](https://trustmrr.com/startup/textbee.md) | Dev tool / Android SMS gateway | MRR $4.5k; last 30d $4.4k; L12M $30.4k; all-time $37.5k | Polar-verified (TrustMRR, 7 Nov 2026) | up: 25-11 $1.1k -> 26-10 $5.6k | 2024-11; For sale $200,000 (3.0x) | Simple | No: US carrier/10DLC exposure (inference) |
| [Calendesk](https://trustmrr.com/startup/calendesk.md) | Booking for therapists/services (PL) | MRR $21.4k; last 30d $28.3k; L12M $368.4k; all-time $1163.5k | Stripe-verified (TrustMRR, 7 Nov 2026) | flat: 25-12 $27.8k -> 26-10 $28.4k | 2020-05 | Medium | No: crowded vertical booking |
| [ConvertLabs](https://trustmrr.com/startup/convertlabs.md) | Booking + marketing, home services | MRR $28.1k; last 30d $27.2k; L12M $370.2k; all-time $2251.8k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $35.6k -> 26-10 $27.3k | 2018-04 | Medium | No: Jobber/Housecall Pro dominate |
| [JourneyFuse](https://trustmrr.com/startup/journeyfuse.md) | Travel-advisor CRM | MRR $11.2k; last 30d $21.0k; L12M $70.3k; all-time $70.3k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 26-03 $505 -> 26-10 $20.7k | 2026-03 | Medium | Model to copy: $25 all-in CRM; group-trip spin killed (WeTravel) |
| [Karma](https://trustmrr.com/startup/karma.md) | Slack/Teams recognition | MRR $6.1k; last 30d $21.4k; L12M $298.9k; all-time $749.0k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $27.7k -> 26-10 $20.6k | 2024-01 | Simple | Killed: Bonusly/Kudos/Guusto 4.8-4.9 |
| [Guidejar](https://trustmrr.com/startup/guidejar.md) | Interactive demos / how-to docs | MRR $4.8k; last 30d $8.5k; L12M $86.5k; all-time $153.9k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $6.6k -> 26-10 $8.4k | 2023-07 | Simple | Not checked (Scribe-type crowding likely) |
| [bltn](https://trustmrr.com/startup/bltn.md) | Church bulletins | MRR $38; last 30d $3.5k; L12M $39.5k; all-time $250.5k | Stripe-verified (TrustMRR, 7 Nov 2026) | flat: 25-12 $3.2k -> 26-10 $3.3k | 2014-07 | Simple | Flat legacy revenue; church niche |
| [Formflow](https://trustmrr.com/startup/formflow.md) | Lead-funnel form builder | MRR $5.7k; last 30d $4.0k; L12M $90.3k; all-time $160.0k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $21.2k -> 26-10 $4.2k | 2025-07 | Simple | No: crowded forms market |
| [CartBoss](https://trustmrr.com/startup/cartboss.md) | SMS cart recovery (EU) | MRR $0; last 30d $29.9k; L12M $481.6k; all-time $1776.6k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $43.1k -> 26-10 $28.6k | 2021-03 | Simple | Killed for US: SMS tools well rated |
| [Catering Funnels](https://trustmrr.com/startup/catering-funnels.md) | Restaurant catering lead-gen (DFY) | MRR $4.4k; last 30d $4.3k; L12M $30.3k; all-time $30.3k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 26-01 $747 -> 26-10 $4.9k | 2025-11 | Simple (service-heavy) | Catering-SaaS spin killed (Tripleseat etc.) |
| [VoxNow](https://trustmrr.com/startup/voxnow.md) | Voicemail transcription for law firms (BE) | MRR $3.7k; last 30d $4.0k; L12M $25.2k; all-time $28.4k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $931 -> 26-10 $4.0k | 2025-07; 2–5 people | Simple | Killed: phone systems bundle transcripts |
| [Khosmos](https://trustmrr.com/startup/khosmos.md) | Quote/invoice app for trades (FR) | MRR $22.5k; last 30d $22.9k; L12M $247.2k; all-time $385.3k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $15.5k -> 26-10 $25.9k | 2023-03 | Medium | PROVISIONAL: Spanish-first US contractor app |
| [MON ATELIER](https://trustmrr.com/startup/mon-atelier.md) | Repair-shop ERP (FR) | MRR $2.9k; last 30d $3.9k; L12M $21.2k; all-time $21.2k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 26-03 $67 -> 26-10 $3.6k | 2026-03; 1 person; For sale $120,000 (2.6x) | Medium | Hold: US bike/e-bike or appliance repair (unchecked) |
| [Stealth Company](https://trustmrr.com/startup/anonymous-startup-31.md) | Vacation-rental guest ops | MRR $7.7k; last 30d $9.5k; L12M $141.5k; all-time $229.3k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $16.7k -> 26-10 $10.6k | 2023-06; 2–5 people; For sale $600,000 (5.2x) | Medium | Killed: PMS/guest-app space well rated |
| [Leverage](https://trustmrr.com/startup/leverage.md) | Real-estate deal analysis (DE) | MRR $12.3k; last 30d $3.3k; L12M $117.4k; all-time $194.2k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $10.8k -> 26-10 $4.7k (peak $18.5k) | 2024-04 | Medium | Hold: US investor tools exist (unchecked) |
| [Stealth Company](https://trustmrr.com/startup/flight-award.md) | Award-ticket search | MRR $22.0k; last 30d $21.7k; L12M $150.4k; all-time $150.4k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $1.0k -> 26-10 $28.4k | 2025-12 | Complex (data) | No: scraping/data-heavy |
| [Flipify](https://trustmrr.com/startup/flipify.md) | Reseller deal alerts (iOS/Android) | MRR $19.2k; last 30d $18.0k; L12M $142.5k; all-time $166.6k | RevenueCat-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $4.0k -> 26-10 $19.3k | 2024-10 | Medium | Hold: vertical alerts (farm equipment/boats), ToS risk |
| [DirectRoles](https://trustmrr.com/startup/directroles.md) | Job search (career-page jobs) | MRR $15.6k; last 30d $22.5k; L12M $59.6k; all-time $59.6k | Whop-verified (TrustMRR, 7 Nov 2026) | up: 26-07 $3.9k -> 26-10 $27.8k | 2026-07; 2–5 people; For sale $79,950 (0.3x) | Simple-medium | Hold: for sale at $79,950 |
| [Data Bloo](https://trustmrr.com/startup/data-bloo.md) | Marketing reporting | MRR $6.5k; last 30d $8.1k; L12M $143.7k; all-time $663.3k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $11.9k -> 26-10 $8.0k | 2021-10; 2–5 people | Medium | No: AgencyAnalytics 4.8 etc. |
| [Heron Copier](https://trustmrr.com/startup/heron-copier.md) | Trade copier / journal | MRR $7.5k; last 30d $6.3k; L12M $195.0k; all-time $504.2k | Creem-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $18.8k -> 26-10 $6.7k | 2023-06 | Medium | No: declining |
| [Fidelatoo](https://trustmrr.com/startup/fidelatoo.md) | Digital loyalty cards (FR) | MRR $6.9k; last 30d $6.8k; L12M $95.1k; all-time $174.4k | Stripe-verified (TrustMRR, 7 Nov 2026) | flat: 25-12 $9.7k -> 26-10 $8.3k | 2023-01 | Simple | No: POS-bundled loyalty in US (inference) |
| [LC](https://trustmrr.com/startup/lc.md) | Gov-bid finder AI (Brazil) | MRR $5.6k; last 30d $7.6k; L12M $40.1k; all-time $40.1k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 26-02 $854 -> 26-10 $8.9k | 2025-11; 1 person | Medium | Hold: US municipal-bid alerts for small trades (unchecked) |
| [Magnetic Funnels](https://trustmrr.com/startup/magnetic-funnels.md) | SMB lead automation (Quad Cities) | MRR $8.6k; last 30d $12.3k; L12M $116.6k; all-time $178.9k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $6.0k -> 26-10 $14.0k | 2024-01; 2–5 people | Medium | Agency-like |
| [Chatwith](https://trustmrr.com/startup/chatwith.md) | AI website chatbot | MRR $3.5k; last 30d $5.9k; L12M $59.4k; all-time $116.6k | Paddle-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $13.2k -> 26-10 $6.0k | ? | Simple | No: crowded, declining |
| [anon-2](https://trustmrr.com/startup/anon-2.md) | White-label chatbots for agencies | MRR $5.2k; last 30d $4.9k; L12M $104.4k; all-time $444.8k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $13.8k -> 26-10 $5.7k | ? | Simple | No: declining 13.8k -> 5.7k |
| [Tribe Social](https://trustmrr.com/startup/tribe-social.md) | Custom community apps | MRR $28.3k; last 30d $15.0k; L12M $203.1k; all-time $402.3k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $21.0k -> 26-10 $15.0k | 2024-11 | Medium | No |
| [Welya, Inc.](https://trustmrr.com/startup/welya-inc.md) | Webinar platform (FR) | MRR $30.4k; last 30d $28.9k; L12M $104.5k; all-time $104.5k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $3 -> 26-10 $28.7k | 2025-06; 6–10 people | Medium | No: crowded |
| [uhoh.com](https://trustmrr.com/startup/uhoh-com.md) | MSP / IT help desk (service) | MRR $43.0k; last 30d $41.0k; L12M $383.5k; all-time $466.3k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $30.1k -> 26-10 $49.0k | 2025-06 | Service | Not SaaS |
| [LaDataViz](https://trustmrr.com/startup/ladataviz.md) | Tableau add-ons | MRR $3.3k; last 30d $5.5k; L12M $47.8k; all-time $159.3k | Lemon Squeezy-verified (TrustMRR, 7 Nov 2026) | flat: 25-12 $5.8k -> 26-10 $4.9k | 2023-07 | Simple | Model: paid add-ons for BI tools |
| [Send Letters Online UK](https://trustmrr.com/startup/send-letters-online-uk.md) | Online letter posting (UK) | MRR $0; last 30d $3.9k; L12M $24.5k; all-time $24.5k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 26-05 $647 -> 26-10 $4.0k | 2026-05 | Simple + ops | Hold: US analogs exist (unchecked) |
| [QR Code AI](https://trustmrr.com/startup/qr-code-ai.md) | QR code generator | MRR $14.8k; last 30d $15.9k; L12M $174.3k; all-time $333.8k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $12.6k -> 26-10 $17.1k | 2023-06 | Simple | No: crowded |
| [Stealth Company](https://trustmrr.com/startup/notion-tool-with-3k-mrr-80-margins-6-hrs-week-ops.md) | Notion-as-backend site builder | MRR $4.3k; last 30d $4.2k; L12M $10.4k; all-time $105.8k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-11 $1.6k -> 26-02 $645 (peak $4.6k) | ?; For sale $85,000 (1.7x) | Simple | No: crowded; for sale $85k |
| [FriendFilter + GroupFilter](https://trustmrr.com/startup/friendfilter-groupfilter.md) | Facebook Chrome extensions | MRR $8.2k; last 30d $6.9k; L12M $106.9k; all-time $1796.1k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-11 $8.7k -> 26-09 $3.7k | 2019-03 | Simple | No: platform risk, declining |
| [LocalRank.so](https://trustmrr.com/startup/localrank-so.md) | Local SEO software | MRR $19.0k; last 30d $14.5k; L12M $402.4k; all-time $742.4k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $44.1k -> 26-10 $18.2k | 2025-02; For sale $1,789,000 (10.2x) | Medium | Killed: declining, sellers exiting |
| [MagicSlides.app](https://trustmrr.com/startup/magicslides-app.md) | Google Slides AI add-on | MRR $9.8k; last 30d $9.7k; L12M $171.4k; all-time $731.1k | Stripe-verified (TrustMRR, 7 Nov 2026) | down: 25-12 $19.1k -> 26-10 $9.8k | 2023-01; For sale $700,000 (5.9x) | Simple | No: declining 19k -> 10k |
| [1clickwebsite.ai](https://trustmrr.com/startup/1clickwebsite-ai.md) | AI WordPress sites for agencies | MRR $14.5k; last 30d $14.9k; L12M $94.7k; all-time $103.6k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $2.4k -> 26-10 $15.8k | 2025-06; 1 person | Medium | No: crowded AI site builders |
| [Cosmo](https://trustmrr.com/startup/cosmo.md) | Discord commerce | MRR $17.0k; last 30d $15.1k; L12M $127.6k; all-time $127.7k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $11 -> 26-10 $15.7k (peak $44.5k) | 2025-11; 1 person | Medium | No |
| [Helios](https://trustmrr.com/startup/helios.md) | Engagement for fitness brands | MRR $0; last 30d $30.4k; L12M $334.3k; all-time $724.6k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $23.4k -> 26-10 $31.2k | 2020-12; 2–5 people | Medium | Unclear product |
| [Dashla](https://trustmrr.com/startup/dashla.md) | Tesla dashboard iPhone app | MRR $4.1k; last 30d $7.0k; L12M $88.1k; all-time $88.1k | RevenueCat-verified (TrustMRR, 7 Nov 2026) | up: 26-02 $0 -> 26-10 $7.1k (peak $25.9k) | 2026-03 | Simple | Model: car-brand companion apps |
| [WilderTrips](https://trustmrr.com/startup/wildertrips.md) | Road-trip planner | MRR $4.8k; last 30d $2.5k; L12M $52.4k; all-time $114.0k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $2.1k -> 26-10 $3.0k (peak $6.7k) | 2022-11 | Medium | Consumer |
| [BreadSync](https://trustmrr.com/startup/breadsync.md) | Portfolio P&L dashboard | MRR $6.3k; last 30d $4.8k; L12M $56.6k; all-time $56.6k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 26-04 $3.2k -> 26-10 $16.8k | 2026-03 | Medium | Consumer finance |
| [P7M.io](https://trustmrr.com/startup/confidential-startup-70.md) | Italian .p7m signature viewer | MRR $608; last 30d $3.8k; L12M $24.1k; all-time $24.1k | RevenueCat-verified (TrustMRR, 7 Nov 2026) | up: 26-04 $730 -> 26-10 $4.0k | 2026-03; 1 person; For sale $120,000 (2.6x) | Simple | Model: mandate-created file-format utility |
| [Kortex-Notebooklm](https://trustmrr.com/startup/kortex-notebooklm.md) | NotebookLM Chrome extension | MRR $3.4k; last 30d $2.4k; L12M $232.4k; all-time $232.4k | Dodo Payments-verified (TrustMRR, 7 Nov 2026) | down: 26-01 $20.1k -> 26-10 $2.5k (peak $56.6k) | ?; For sale $50,000 (1.8x) | Simple | No: collapsing 56k -> 2.5k (platform risk) |
| [Zanfia](https://trustmrr.com/startup/zanfia.md) | Creator commerce platform (PL) | MRR $10.1k; last 30d $32.8k; L12M $131.7k; all-time $272.7k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $9.0k -> 26-10 $43.2k | 2021-05; 2–5 people | Medium | No: crowded |
| [Simple Analytics](https://trustmrr.com/startup/simple-analytics.md) | Privacy web analytics | MRR $37.9k; last 30d $39.0k; L12M $475.0k; all-time $1941.3k | Stripe-verified (TrustMRR, 7 Nov 2026) | flat: 25-12 $38.2k -> 26-10 $45.7k | 2018-08 | Medium | No: crowded |
| [Pushouse](https://trustmrr.com/startup/pushouse.md) | WhatsApp e-commerce automation | MRR $27.8k; last 30d $38.5k; L12M $325.1k; all-time $325.1k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 26-01 $7.6k -> 26-10 $37.6k | 2026-01 | Medium | No: low US WhatsApp use |
| [Angel Match](https://trustmrr.com/startup/angel-match.md) | Investor database | MRR $25.8k; last 30d $25.9k; L12M $355.6k; all-time $990.2k | Stripe-verified (TrustMRR, 7 Nov 2026) | flat: 25-12 $32.0k -> 26-10 $26.4k | 2019-01 | Simple (data) | Hold: grant-funder DB for nonprofits (unchecked) |
| [Analytics Mates](https://trustmrr.com/startup/analytics-mates.md) | AI analytics for GA4 | MRR $4.6k; last 30d $23.8k; L12M $267.4k; all-time $716.5k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $18.7k -> 26-10 $28.2k | 2024-01 | Medium | No |
| [Refined Listings](https://trustmrr.com/startup/refined-listings.md) | Virtual staging for agents | MRR $1.5k; last 30d $14.8k; L12M $233.1k; all-time $278.9k | Stripe-verified (TrustMRR, 7 Nov 2026) | up: 25-12 $7.0k -> 26-10 $19.6k (peak $37.7k) | 2024-09; 2–5 people; For sale $495,000 (2.8x) | Medium | Realtor tools assessed in an earlier round |
| [Tree Nerd Academy](https://trustmrr.com/startup/tree-nerd-academy) | Credential exam prep (ISA arborist) | MRR $0; last 30d $41.8k; all-time $259.0k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | n/a |  | Simple | Assessed earlier (do not re-spin to NICET) |
| [Glossa.live](https://trustmrr.com/startup/glossa-live) | Live AI translation for churches | MRR $14.4k; last 30d $31.2k; all-time $196.5k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | n/a |  | Medium | Assessed earlier |
| [SoldComps](https://trustmrr.com/startup/soldcomps) | eBay sold-comps API | MRR $25.7k; last 30d $24.0k; all-time $70.5k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth 18% |  | Simple | ScrapeCreators-type; not re-checked |
| [FreeTCF](https://trustmrr.com/startup/freetcf) | TCF Canada French-test prep app | MRR $23.1k; last 30d $21.1k; all-time $202.8k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth -11% |  | Simple | Model: single-exam prep app |
| [DataFast](https://trustmrr.com/startup/datafast) | Revenue-first analytics | MRR $28.3k; last 30d $30.3k; all-time $332.2k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth -1% |  | Medium | Assessed earlier |
| [Liinks](https://trustmrr.com/startup/liinks) | Link-in-bio | MRR $31.7k; last 30d $31.6k; all-time $1797.1k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth -2% |  | Simple | Assessed earlier |
| [POST BRIDGE](https://trustmrr.com/startup/post-bridge) | Cross-posting to social | MRR $50.1k; last 30d $46.4k; all-time $571.3k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth -11% |  | Simple | Assessed earlier |
| [Bazzly](https://trustmrr.com/startup/bazzly) | Reddit lead-gen | MRR $34.5k; last 30d $39.1k; all-time $96.0k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth 124% |  | Simple | Assessed earlier |
| [Dataford Inc.](https://trustmrr.com/startup/dataford-inc) | Tech-interview prep platform | MRR $37.3k; last 30d $43.0k; all-time $233.2k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth -8% |  | Medium | Model: role-specific interview prep |
| [Sherpa](https://trustmrr.com/startup/sherpa) | Clinical mentorship membership | MRR $25.8k; last 30d $37.5k; all-time $572.3k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | n/a |  | Simple | Model: credentialed-community membership |
| [Marky](https://trustmrr.com/startup/marky) | Social media for self-pub authors | MRR $22.2k; last 30d $16.8k; all-time $1016.6k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | n/a | For sale $495,000 | Medium | Declining; for sale |
| [RTMP.IN](https://trustmrr.com/startup/rtmp-in) | Go live on Instagram from OBS | MRR $6.0k; last 30d $634; all-time $765.5k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | n/a | For sale $420,000 | Simple | Platform risk; for sale |
| [SEO STACK](https://trustmrr.com/startup/seo-stack) | SEO data warehouse | MRR $22.1k; last 30d $18.6k; all-time $515.6k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | n/a | For sale $1,000,000 | Medium | For sale |
| [Lancer.app](https://trustmrr.com/startup/lancer-app) | Upwork proposal automation | MRR $17.7k; last 30d $16.2k; all-time $218.8k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | n/a | For sale $699,999 | Simple | For sale; platform risk |
| [Low Content AI](https://trustmrr.com/startup/low-content-ai) | AI low-content KDP books | MRR $14.7k; last 30d $16.1k; all-time $656.0k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | n/a | For sale $800,000 | Simple | For sale; KDP assessed earlier |
| [ColdSire](https://trustmrr.com/startup/coldsire) | Mailbox reseller for cold email | MRR $13.9k; last 30d $11.9k; all-time $1052.2k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth -17% | For sale $149,000 | Simple (ops) | For sale |
| [TrackAI](https://trustmrr.com/startup/trackai) | AI calorie tracker app | MRR $19.4k; last 30d $19.5k; all-time $286.0k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth -14% |  | Simple | CalAI-type (assessed) |
| [fastwrite.io](https://trustmrr.com/startup/fastwrite-io) | AI writing for students | MRR $12.3k; last 30d $12.2k; all-time $211.7k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | n/a | For sale $150,000 | Simple | For sale |
| [Stud Finder Wall Detector Tool](https://trustmrr.com/startup/stud-finder-wall-detector-tool) | Stud-finder utility app | MRR $5.0k; last 30d $4.6k; all-time $117.5k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | n/a | For sale $130,000 | Simple | For sale; utility-app model |
| [Speedster](https://trustmrr.com/startup/speedster) | Speed-camera detector app | MRR $6.8k; last 30d $7.6k; all-time $300.4k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | n/a |  | Simple | Consumer utility |
| [RankAI](https://trustmrr.com/startup/rankai) | Autonomous SEO content | MRR $56.5k; last 30d $54.9k; all-time $377.0k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth 38% |  | Medium | Crowded AI SEO |
| [Rank Prompt](https://trustmrr.com/startup/rank-prompt) | AI-search visibility tracking | MRR $44.8k; last 30d $55.1k; all-time $332.5k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth 24% |  | Medium | Crowded GEO tools |
| [Audn.AI](https://trustmrr.com/startup/audn-ai) | Automated pentesting for AI apps | MRR $28.3k; last 30d $43.9k; all-time $105.3k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth 20% |  | Complex | Not copyable solo |
| [Apiframe](https://trustmrr.com/startup/apiframe) | Multi-model AI API | MRR $34.9k; last 30d $42.5k; all-time $527.7k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth -10% |  | Medium | Commodity |
| [Chessigma](https://trustmrr.com/startup/chessigma) | Free chess site | MRR $7.9k; last 30d $17.8k; all-time $80.3k | Provider-verified (TrustMRR listing card, 7 Nov 2026) | 30-day revenue growth 0% |  | Medium | Consumer |

**Excluded as AI video creation tools** (per brief; verified on TrustMRR but not inventoried): StoryShort, VidAI, Wava AI, Vidgenie, Produce.so, Faceless.so, Based Labs, CreativeClaw, Kolbo AI. — [TrustMRR homepage](https://trustmrr.com/); [category/social-media](https://trustmrr.com/category/social-media)

**Inventory B — Flippa SaaS listings (listing-stated; fetched 7 Nov 2026)**

| Listing | Category | Revenue (listing-stated) | Other metrics | Simple / complex | Niche-angle note |
|---|---|---|---|---|---|
| [Google Maps rank tracker + AI ranking coach for local SEO agencies](https://flippa.com/13365450) | Local SEO | MRR $22,250; "$273K ARR" | 522 active subs, ~76% on annual plans, 11.5% churn, 79% margin, profit $14,805/mo, 1 yr old, asking $575,000 (2.6x) | Medium | Killed (local SEO saturated; see Q3) |
| [AI study platform for nursing students](https://flippa.com/14338446) | Ed-tech / exam prep | MRR $17,423 on the metrics panel; $18,824 in the overview | 915 subs, ARPU $56.65, 20–23% monthly churn, 34% margin, TikTok/IG creator-led, 1 yr, asking $225,000 | Simple | Hold: credential-prep model (NCLEX incumbents unchecked) |
| [SOP management SaaS + template marketplace](https://flippa.com/11413188) | Ops / SOPs | "$108K annual revenue" | Profit $4,557/mo, 74% margin, 8 yrs, asking $449,000 (3.4x) | Simple | Hold: vertical SOP packs (unchecked) |
| [Fintech SaaS for funding brokers](https://flippa.com/11734387) | Broker CRM | MRR $12,679; "$208K T12" | 35 subs (about $362 ARPA, my calculation), 15% churn, 47% margin, 6 yrs, asking $450,000 | Medium | Hold: MCA/funding-broker CRM (regulatory risk) |
| [B2B facilities SaaS (France)](https://flippa.com/12839625) | Facilities | "~€350k ARR, 93% retention" | 88 subs, 7% churn, 91% margin, 9 yrs, asking $1,325,715 | Medium | Hold |
| [Subscription SaaS for Amazon authors (review community, AU)](https://flippa.com/14387997) | Author tools | Not parsed (AUD); 1.4x multiple on $118,167 ask implies about A$84k/yr (my inference) | "400+ paying members," 18,000+ reviews facilitated, 5–6% churn, 70%+ adj. margin, VA-run 5 hrs/wk | Simple | KDP/author tools assessed earlier |
| [Porn-blocker app (iOS/Windows)](https://flippa.com/12197961) | Accountability | "10.5K MRR," "$240K revenue, $206K net" (slug) | 86% margin (slug) | Simple | No: accountability-software niche crowded (unchecked) |
| [AI ed-tech SaaS for teachers](https://flippa.com/11990705) | Ed-tech | "$6,673 MRR, $80K ARR" (slug) | 428 subscribers (slug) | Simple | Hold |
| [AI-powered HR platform](https://flippa.com/13415587) | HR | "$148K ARR" (slug) | Referral channels (slug) | Medium | — |
| [Trading-bot software company](https://flippa.com/12769422) | Trading | "$733K ARR," "136% CAGR since 2023" (slug) | Low churn (slug) | Complex | No |
| [AI study platform (gamified quizzes + voice tutor)](https://flippa.com/12215721) | Ed-tech | "$434K ARR," "$61K SDE" (slug) | 6,400 paying subscribers (slug) | Medium | — |
| [Content-automation SaaS for creators/publishers](https://flippa.com/13759472) | Content | "$61K TTM revenue" (about $5k/mo) (slug) | 75% margin, $0 ad spend (slug) | Medium | — |
| [Education SaaS](https://flippa.com/12223339) | Ed-tech | "$63K ARR" (about $5.3k/mo) (slug) | 70% margin, DA 24 (slug) | Medium | — |

"(slug)" means the figure appears only in the listing headline/URL that Flippa renders on its search page, and the listing page itself was not opened. — [Flippa SaaS search](https://flippa.com/search?filter%5Bproperty_type%5D%5B%5D=saas)

**Inventory C — Starter Story database cards (founder-claimed unless marked; the card shows no interview date; fetched 7 Nov 2026)**

| Business | What it is | Revenue (provenance) | Founded · team | Growth channels (card) | Simple / complex | Niche-angle note |
|---|---|---|---|---|---|---|
| [DASHP (dashp.io)](https://www.starterstory.com/data/apps-so-simple) | Commission management for pest-control sales teams | $8K/mo (founder-claimed) | 2022 · solo · "$50 to start" | Referral program, direct sales | Simple | **SHORTLIST (S4)**: D2D commission ledger |
| [Stagetimer](https://www.starterstory.com/data/apps-so-simple) | Remote-controlled countdown timer for events | $30K/mo (founder-claimed) | 2021 · 2 co-founders · "built in 3 days" | Word of mouth, PPC | Simple | Hold: worship/AV run-of-show (unchecked) |
| [PDFShift](https://www.starterstory.com/data/apps-so-simple) | HTML-to-PDF API | $9K/mo (founder-claimed) | 2018 · solo | Direct sales, WOM | Simple | Commodity API |
| [Stay in Session](https://www.starterstory.com/data/apps-so-simple) | Distraction blocker | $8K/mo (founder-claimed) | 2020 · solo | WOM, organic social | Simple | Consumer |
| [BetterAnalyst (FormulaBot)](https://www.starterstory.com/data/apps-so-simple) | AI Excel formula generator | $30K/mo (founder-claimed) | 2022 · solo | WOM | Simple | Assessed earlier (FormulaBot) |
| [ScreenshotOne](https://www.starterstory.com/data/1m-apis) | Screenshot API | $20K/mo (founder-claimed) | 2022 · solo · "$2K to start" | Affiliate, PPC | Simple | Commodity API |
| [ScrapingAnt](https://www.starterstory.com/data/1m-apis) | Web-scraping API | $20K/mo (founder-claimed) | — | Affiliate, referral | Medium | ScrapeCreators-type (assessed) |
| [Legislate](https://www.starterstory.com/data/1m-apis) | Contract creation for non-lawyers | $5K/mo (founder-claimed) | — | WOM, SEO | Medium | — |
| [Tinq.ai](https://www.starterstory.com/data/1m-apis) | NLP toolkit API | $4K/mo (founder-claimed) | — | WOM, direct | Medium | — |
| [Spurwing](https://www.starterstory.com/data/1m-apis) | Scheduling API | $50K/mo (founder-claimed) | — | WOM, social ads | Medium | — |
| [Treblle](https://www.starterstory.com/data/1m-apis) | API monitoring | $50K/mo (founder-claimed) | — | WOM, FB community | Complex | — |
| [Bannerbear](https://www.starterstory.com/data/1m-apis) | Image/video generation API | $50K/mo (**third-party estimate**) | 2019 · solo | WOM, social ads | Medium | Orshot-type (Q3) |
| [Parseur](https://www.starterstory.com/data/no-audience-required) | Email/document data extraction | $40K/mo (founder-claimed) | 2017 · 2 co-founders | Affiliate, WOM | Medium | Hold: vertical parsing (e.g., load tenders) |
| [Tech Lockdown](https://www.starterstory.com/data/no-audience-required) | Content-blocking software | $20K/mo (founder-claimed) | 2021 · solo | WOM | Simple | Crowded (unchecked) |
| [NoteForms](https://www.starterstory.com/data/plugins) | Notion form builder | $40K/mo (founder-claimed) | 2021 · solo · "built in 6 days" | WOM, SEO | Simple | Platform add-on model |
| [Data Fetcher](https://www.starterstory.com/data/plugins) | Airtable API importer | $20K/mo (founder-claimed) | 2020 · solo | WOM, email | Simple | Platform add-on model |
| [SuperLemon](https://www.starterstory.com/data/plugins) | WhatsApp chat for Shopify | $30K/mo (founder-claimed) | 2019 · 2 co-founders | WOM, referral | Simple | Low US WhatsApp use |
| [Tailscan](https://www.starterstory.com/data/plugins) | Tailwind live-CSS browser extension | $3K/mo (founder-claimed) | 2022 · solo | WOM, email | Simple | Dev niche |
| [Recall](https://www.starterstory.com/data/plugins) | AI knowledge-base extension | $9K/mo (founder-claimed) | 2023 · 3 people | PPC, referral | Medium | — |
| [Mailman](https://www.starterstory.com/data/plugins) | Email batching | $30K/mo (founder-claimed) | 2020 · 5 people | WOM, PPC | Medium | — |
| [Studio Wombat](https://www.starterstory.com/data/plugins) | WooCommerce plugins | $20K/mo (founder-claimed) | 2017 · solo | WOM, organic social | Simple | Plugin model |
| [Tiiny Host](https://www.starterstory.com/data/one-page-websites) | Drag-and-drop simple hosting | $40K/mo (founder-claimed) | 2019 · solo | WOM, FB community | Simple | — |
| [Excel Exercises](https://www.starterstory.com/data/one-page-websites) | Interactive Excel practice | $30K/mo (founder-claimed) | 2020 · solo · Austin, TX | WOM, SEO | Simple | Hold: interactive practice for other tools |
| [AudioPen](https://www.starterstory.com/data/one-page-websites) | Voice-note-to-text AI | $20K/mo (founder-claimed) | 2023 · solo · "$30 to start" | Affiliate, WOM | Simple | Consumer |
| [AllAuthor](https://www.starterstory.com/data/one-page-websites) | Book marketing for self-published authors | $20K/mo (founder-claimed) | 2016 · 8 people | WOM, social ads | Medium | Author tools assessed earlier |
| [Binderr](https://www.starterstory.com/data/david-vs-goliath) | Client onboarding for accountants/lawyers | $10K/mo (founder-claimed) | 2020 · 19 people · "$2M to start" | Direct sales | Complex | — |
| [Questgen](https://www.starterstory.com/data/bubble-ideas) | AI quiz generator for educators | $4K/mo (founder-claimed) | 2022 · solo · Bubble | SEO, organic social | Simple | — |
| [My AskAI](https://www.starterstory.com/data/bubble-ideas) | AI support chatbot | $20K/mo (founder-claimed) | 2023 · 2 co-founders · Bubble | WOM, SEO | Simple | Crowded |
| [FounderPal](https://www.starterstory.com/data/bubble-ideas) | AI marketing strategy | $10K/mo (founder-claimed) | 2023 · 2 co-founders | Email, SEO | Simple | — |
| [Codemap](https://www.starterstory.com/data/bubble-ideas) | No-code talent marketplace | $7K/mo (founder-claimed) | 2020 · 3 people | WOM, SEO | Medium | — |
| [Achievable](https://www.starterstory.com/data/bubble-ideas) | Test prep for professional exams | $200K/mo (founder-claimed) | 2016 · 12 people | Social ads, press, WOM | Medium | Credential-prep model (hold) |
| [The Agent Nest](https://www.starterstory.com/data/no-code-ideas) | Marketing content library for realtors | $8K/mo (**third-party estimate**) | 2020 · 2 co-founders | WOM, SEO | Simple | Realtor tools assessed earlier |
| [Packager (intunepckgr.com)](https://www.starterstory.com/data/bubble-ideas) | Intune app packaging | $60K/mo (founder-claimed) | 2024 · 3 people · Bubble | SEO, email | Medium | Assessed earlier |
| [Bank Statement Converter](https://www.starterstory.com/data/no-audience-required) | PDF bank statement to CSV | $40K/mo (founder-claimed) | 2021 · solo | WOM, referral | Simple | Assessed earlier |

**Notable TrustMRR for-sale listings ≥$3k/mo** (verified revenue; asking price as shown on the profile):

| Listing | Asking price (multiple) | Listed | Offers |
|---|---|---|---|
| Conductor | $1,250,000 (2.3x) | 6 Mar 2026 | 29 |
| LocalRank.so | $1,789,000 (10.2x) | — | 15 |
| MagicSlides | $700,000 (5.9x) | — | 9 |
| Vacation-rental guest-ops stealth startup | $600,000 (5.2x) | — | 4 |
| Refined Listings | $495,000 (2.8x) | — | 12 |
| textbee | $200,000 (3.0x) | — | 15 |
| MON ATELIER | $120,000 (2.6x) | — | 13 |
| P7M.io | $120,000 (2.6x) | — | 4 |
| Notion tool | $85,000 (1.7x) | — | 5 |
| DirectRoles | $79,950 (0.3x) | 2 Nov 2026 | 13 |
| Kortex | $50,000 (1.8x) | — | 10 |

Sources: [Conductor](https://trustmrr.com/startup/conductor.md); [LocalRank](https://trustmrr.com/startup/localrank-so.md); [MagicSlides](https://trustmrr.com/startup/magicslides-app.md); [anonymous-startup-31](https://trustmrr.com/startup/anonymous-startup-31.md); [Refined Listings](https://trustmrr.com/startup/refined-listings.md); [textbee](https://trustmrr.com/startup/textbee.md); [MON ATELIER](https://trustmrr.com/startup/mon-atelier.md); [P7M.io](https://trustmrr.com/startup/confidential-startup-70.md); [Notion tool](https://trustmrr.com/startup/notion-tool-with-3k-mrr-80-margins-6-hrs-week-ops.md); [DirectRoles](https://trustmrr.com/startup/directroles.md); [Kortex](https://trustmrr.com/startup/kortex-notebooklm.md)

**Selected detail from verified profiles (used later in the shortlist)**
- **Khosmos** (France):
  - A quote/invoice mobile app for building-trade micro-businesses.
  - Pricing: €23.99/mo plus €15.59 per extra user, or €199.99/yr; 14-day trial.
  - Channels: "SEO, App store optimization, Facebook, Instagram, TikTok."
  - Built in Flutter and Laravel; about 12,000 users.
  - Source: [Khosmos profile](https://trustmrr.com/startup/khosmos.md)
- **JourneyFuse:**
  - A $25/mo travel-advisor CRM covering leads, trips, proposals, payments, itineraries and commissions.
  - 563 subs; founded Mar 2026.
  - Its site claims "Trusted by 5,000+ travel advisors and 850+ agencies" (founder-claimed).
  - Sources: [JourneyFuse profile](https://trustmrr.com/startup/journeyfuse.md); [journeyfuse.com](https://journeyfuse.com/)
- **P7M.io:**
  - Opens Italy's mandatory CAdES `.p7m` signed documents in the browser.
  - Pricing: €3.99 per document, €12.99/yr or €24.99 lifetime.
  - Channels: ASO and SEO; solo founder; about 50,000 users.
  - Source: [P7M profile](https://trustmrr.com/startup/confidential-startup-70.md)
- **Conductor:**
  - "Real-time access to every QuickBooks Desktop object via Python, Node.js/TypeScript, and REST."
  - Production pricing is $49 per company file per month.
  - Source: [Conductor profile](https://trustmrr.com/startup/conductor.md)
- **EmailEngine:**
  - $1,450/yr for unlimited instances.
  - Solo, bootstrapped, SEO channel; founder is Andris Reinman.
  - Source: [EmailEngine profile](https://trustmrr.com/startup/emailengine.md)
- **Catering Funnels:**
  - A done-for-you lead-gen and automation service for restaurants with catering.
  - Pricing: $97/mo + $497 setup, $747/mo + $997 setup, or $2,997/mo + $1,997 setup.
  - 8 subs; US.
  - Source: [Catering Funnels profile](https://trustmrr.com/startup/catering-funnels.md)
- **VoxNow** (Belgium):
  - Transcribes and summarizes voicemail and sends instant SMS replies.
  - €90/mo per user; persona "Law Firms"; 32 subs.
  - Source: [VoxNow profile](https://trustmrr.com/startup/voxnow.md)

### Inferences
- **The most cloneable pattern in this sweep is a "boring vertical workflow at a flat low price, sold to an under-tooled trade."**
  - FireCert: £79–£129/mo, 43 subs in 8 months.
  - Khosmos: €24/mo, 865 subs.
  - JourneyFuse: $25/mo, 563 subs in 8 months.
  - MON ATELIER: €19–€39/mo.
  - All four are recent and growing on verified data. Generic horizontal tools in the same set (chatbots, form builders, QR codes, slides, local SEO) are flat or falling.
- **Europe-only originals are an under-mined source of US spins.** Khosmos (France), FireCert (UK), MON ATELIER (France), VoxNow (Belgium), P7M (Italy) and LC (Brazil, government bids) solve problems that have US equivalents. Their US markets were not checked here except FireCert, VoxNow and Khosmos.
- **Platform-dependent extensions can collapse fast.**
  - Kortex: $56.6k/mo in Mar 2026 to $2.5k in Oct.
  - FriendFilter: $12.5k to $3.7k.
  - Treat Chrome or social-platform add-ons as high risk even with verified revenue.

### Gaps
- **Acquire.com** listings (login), Indie Hackers (previous round 403) and Reddit were not available. Baremetrics Open Startups rendered no data.
- **Starter Story** cards carry no interview date, so their figures may be months or years old. Only about 12–15 cards per category are public.
- **Flippa listings** marked "(slug)" were not opened, so their headline figures are unverified even at listing level.
- **TrustMRR categories** show only the top 60 by revenue. Smaller verified startups in large categories (Productivity, Marketing) that sit below that cut are missing, because TrustMRR asks agents not to page through the marketplace.

---

## Q2. Which originals are copyable and can be aimed at an underserved US niche with expansion potential? (shortlist dossiers, scored /25)

### Takeaway
- **Two spins clear the incumbent check:**
  - **FireCert → US 1–3-technician fire-extinguisher and fire-protection inspection shops: 18/25.** The fire-specific incumbents have thin or poor reviews or are mid-market, and the best-known one excludes small shops by policy.
  - **Hirevire → camp and seasonal-staff async screening: 18/25.** Camp-management suites do not do video interviews. The risk is cheap horizontal tools, especially Hireflix at 5.0★ and $75/mo.
- **Three are provisional:**
  - Conductor → Sage 100 desktop API: 16/25.
  - DASHP → D2D summer-sales commission ledger: 16/25.
  - Khosmos → Spanish-first US contractor quoting/invoicing: 15/25. Its incumbent check is incomplete.
- **The three mandated re-checks all failed:**
  - Orshot's high-school-sports spin.
  - Both Web3Forms spins.
  - Image-Charts.
  - Details are in Q3.

**Scoring key:**
- Each item is scored 1–5 on revenue proof (R), beatability (B), copyability (C), expansion (E) and channel replicability (Ch).
- R reflects provenance and durability.
- B is judged against the kill rule: a ≈4.6★+ product with many reviews dominating the exact niche, or core software bundling the feature free.

### Cited Findings

#### S1. FireCert → US small fire-extinguisher / fire-protection inspection shops — **18/25 (R3 B4 C4 E4 Ch3) — PASS**

**Original and revenue proof (Stripe-verified)**
- **Product:** FireCert (UK), founded 24 Feb 2026. It manages "assets, certificates, servicing and compliance across fire alarms, emergency lighting, extinguishers and security systems — without spreadsheets, PDFs or scattered records."
- **Revenue:**
  - MRR $5,123 from 43 active subscriptions; L30 $4,780; all-time $22,263.
  - Monthly revenue: Mar $234 → Apr $1,170 → May $1,483 → Jun $1,693 → Jul $3,107 → Aug $3,710 → Sep $4,832 → Oct $4,696.
  - 95% margin.
- **Pricing:** Professional £79/mo, Business £129/mo.
- **Persona:** "UK Fire Contractors, Security Engineers, Commercial Sites, HMOs & Housing."
- **Traffic and footprint:** 700 visitors and 37,103 Google Search impressions in 30 days (Search Console connected); DR 26.
- Source: [FireCert profile](https://trustmrr.com/startup/firecert.md)

**Spin**
- **Target:** US fire-extinguisher service companies and small fire-protection contractors with 1–3 technicians.
- **Core workflow:** Unit-level asset register with barcode/QR tags; NFPA-10-style due-date engine (monthly, annual, 6-year maintenance, hydrotest); offline mobile inspection with dated photo proof.
- **Commercial layer:** Deficiency → quote; branded PDF certificates; a customer portal for building owners; renewal reminders that generate re-booking.

**Niche incumbents (ratings and prices fetched directly)**
- **Inspect Point:**
  - "Plans start at three technicians, or one or two technicians running 400 or more inspections a year."
  - Every plan is "quoted to your operation"; Enterprise starts at 15 technicians.
  - Software Advice: **3.8★ from 5 reviews**, "pricing available upon request."
  - Sources: [Inspect Point pricing](https://www.inspectpoint.com/pricing); [Software Advice profile](https://www.softwareadvice.com/fleet-management/inspect-point-profile)
- **InspectNTrack:** 4.29★ from 56 ratings on GetApp. — [GetApp](https://www.getapp.com/inspection-software/a/inspectntrack)
- **ServiceTrade:** 4.6★ (345 reviews). Positioned for "commercial HVAC, mechanical, and fire contractors," i.e. mid-market field service. Its pricing page returned 403. — [Capterra inspection category](https://www.capterra.com/inspection-software/)
- **Fire Inspect Hub:** $18/user/mo; 5.0★ from 1 review. — [Capterra](https://www.capterra.com/p/10037388/Fire-Inspect-Hub/)
- **InspectExtinguishers:**
  - Flat CA$29/mo with unlimited users; "Built by a Fire Extinguisher Tech"; 30-day trial.
  - Tracks "every annual, 6-year, and hydrotest date."
  - No Capterra reviews yet.
  - Sources: [inspectextinguishers.com](https://inspectextinguishers.com/); search summary of [Capterra UK listing](https://www.capterra.co.uk/software/1111275/inspectextinguishers)
- **Generic alternatives on the same Software Advice page:**
  - ZenFire 4.7★ (29) from A$29/mo (AU-centric)
  - Mitti by SafetyCulture 4.6★ (356) from $25/mo (generic inspections)
  - SnapInspect 5.0★ (69) from $60/mo (property inspections)
  - Source: [Software Advice](https://www.softwareadvice.com/fleet-management/inspect-point-profile)
- **Life Safety Inspector:** 2.0★ from 1 review ("nothing but a nuisance"); contact for pricing. — search summary of [Capterra](https://www.capterra.com/p/123700/Life-Safety-Inspector/)

**Beatability evidence**
- No fire-specific product with ≈4.6★ and many reviews targets 1–3-tech shops.
- The most-reviewed fire-capable tool (ServiceTrade) is a mid-market field-service platform.
- The best-known fire-inspection tool (Inspect Point) says on its pricing page that it excludes shops under its 3-tech / 400-inspection floor.

**MVP scope (about 2–3 months, solo)**
- Customers, sites and assets with tag IDs.
- Due-date engine, offline PWA or React Native inspection flow with photo capture, and deficiency list → quote.
- PDF report/certificate, and email reminders to building owners.
- Stripe billing; QuickBooks Online export in v1.1.
- **Infra:** Postgres + object storage + a PDF service. Likely under $100/mo at early scale (my estimate).

**Expansion**
- **Adjacent trades:** fire sprinkler (NFPA 25), fire alarm (NFPA 72), kitchen-hood suppression, emergency/exit lighting, and backflow testing.
- **Add-ons:** owner-side compliance portal (FireCert already sells to "Commercial Sites, HMOs & Housing"), AHJ report submission, tag/label printing, invoicing.
- **TAM counts:** not obtained (see Gaps).

**Channel**
- FireCert's channel is not disclosed. Its 37k monthly search impressions on a young domain suggest SEO-led acquisition (inference). — [FireCert profile](https://trustmrr.com/startup/firecert.md)
- **US replication (unverified):** state fire-marshal licensing rosters for portable-extinguisher companies as outbound lists, NAFED, and Facebook groups for extinguisher techs.

#### S2. Hirevire → camp and seasonal-staff async screening — **18/25 (R4 B3 C5 E3 Ch3) — PASS (provisional on pricing wedge)**

**Original and revenue proof (Stripe-verified)**
- **Product:** Hirevire (India), founded Dec 2021; 2–5 people; bootstrapped. It "replaces first-round phone screens with structured async video interviews. Candidates record responses on their own time, no login required."
- **Revenue:**
  - MRR $13,915 from 162 subscriptions; L12M $145,429; all-time $282,585.
  - Monthly revenue: Dec 2025 $6,781 → Mar $13,515 → May $15,429 → Jul $15,335 → Sep $14,935 → Oct $12,584.
  - 80% margin; DR 62.
  - Source: [Hirevire profile](https://trustmrr.com/startup/hirevire.md)
- **Pricing:**
  - $49/mo (300 interviews/yr), $149/mo (1,200/yr) and $249/mo (12,000/yr), billed yearly.
  - Every plan includes AI scorecards and transcripts in 90+ languages.
  - Source: [Hirevire pricing](https://hirevire.com/pricing)

**Spin**
- **Target:** US summer camps first, then other seasonal employers (ski areas, pools, water parks, golf).
- **Workflow:** One link per role (counselor, lifeguard, kitchen, J-1 international staff). Async video answers plus certification uploads (lifeguard/CPR) and availability windows.
- **Camp-specific pieces:**
  - Automatic reference requests.
  - Volunteer or board reviewer panels.
  - **Season-pass pricing** (pay for Jan–Jun, not 12 months).
  - Push of hired staff into CampMinder or UltraCamp staff records.

**Niche incumbents**
- **Campminder:**
  - 4.7★ (256) on Capterra.
  - Its staff module covers "Staff Applications & Forms" and a "Staff Coordinator." The page mentions video only once and lists no async interviews.
  - Pricing is "tiered based on the number of enrolled campers," demo-only.
  - Sources: [Capterra camp category](https://www.capterra.com/camp-management-software/); [campminder.com/staff](https://campminder.com/staff/)
- **iCampPro:** Seasonal hiring with custom applications, "standardizing the interview process," "automatically collecting references" and a staff portal. No async video is mentioned. — [iCampPro staff recruitment](https://www.icamppro.com/summer-camp-staff-recruitment-seasonal-hiring-software)
- **Spark Hire:**
  - 4.7★ (110) on Capterra; Pro $299/mo, Growth $499/mo.
  - Used by Camp Twitch and Shout, a nonprofit camp, to screen "~100 at a time" counselor applicants with remote volunteer reviewers.
  - Sources: [Capterra Spark Hire](https://www.capterra.com/p/125710/Spark-Hire/); [Capterra pricing](https://www.capterra.com/p/125710/Spark-Hire/pricing/); [case study](https://www.casestudies.com/company/spark-hire/case-study/how-camp-twitch-and-shout-uses-spark-hire-for-screening-camp-counselors)
- **Hireflix:** **5.0★ (261)** on Capterra; $75/mo and $150/mo billed yearly, "Unlimited Interview responses," with all features on all plans. — [Hireflix pricing](https://hireflix.com/pricing); [Capterra video-interviewing category](https://www.capterra.com/video-interviewing-software/)
- **Others on Capterra:** VidCruiter 4.6★ (125), HireVue 4.5★ (51), Fountain 4.6★ (39, hourly hiring). — [Capterra video-interviewing category](https://www.capterra.com/video-interviewing-software/)
- **Additional tools named in a search summary:** StoryPrompt (no-login 90-second video intros) and Camp Leaders (a J-1 placement agency). — search results incl. [campleaders.com](https://campleaders.com/us), [StoryPrompt pricing](https://storyprompt.com/pricing)

**Beatability evidence**
- The camp suites (Campminder 4.7★, iCampPro) do not offer async video.
- The horizontal video tools are strong and cheap (Hireflix 5.0★ at $75/mo), but none is camp-specific.
- So the spin survives the kill rule, but **the wedge must be workflow and pricing, not video itself.**

**MVP scope (about 4–6 weeks)**
- Browser MediaRecorder capture to S3/R2, transcription, reviewer scoring and comments, reference-request emails.
- Seasonal billing in Stripe, CSV export, then CampMinder sync.
- **Infra:** Video storage/egress is the main cost. Auto-delete after the season keeps it small (my estimate).

**Expansion**
- **TAM:** The ACA's 2024 National Economic Impact Study "reported 20,175 camps in the United States." — [Wikipedia: Summer camp](https://en.wikipedia.org/wiki/Summer_camp)
- Residential camps hire late-teen and early-twenties counselors seasonally, often alongside international staff vetted by agencies. — [Wikipedia: Summer camp](https://en.wikipedia.org/wiki/Summer_camp)
- **Adjacent markets:** ski areas, aquatics, parks and rec, and summer-sales teams (links to S4). Counts not verified.
- **Add-ons:** reference checks, onboarding documents, background-check reselling.

**Channel**
- Hirevire's channel is not disclosed; DR 62 suggests SEO (inference). — [Hirevire profile](https://trustmrr.com/startup/hirevire.md)
- **Camp channels (unverified):** ACA conferences, camp-director communities, CampMinder/UltraCamp partner listings.

**Risk**
- **Seasonality.** Hiring concentrates in winter and spring, so annual churn is likely unless priced per season (inference).

#### S3. Conductor → "Conductor for Sage 100" (and deeper Sage 50 US) — **16/25 (R5 B3 C2 E3 Ch3) — PROVISIONAL**

**Original and revenue proof (Stripe-verified)**
- **Product:** Conductor (US), founded Jul 2022: "The best QuickBooks Desktop & Enterprise API on the planet."
- **Revenue:**
  - MRR $46,984 from 314 subs; L12M $353,714; all-time $511,001.
  - Monthly revenue rose every month: Dec 2025 $21,316 → Oct 2026 $44,640.
  - 95% margin.
- **Pricing:** $49 per company file per month.
- **For sale:** asking $1.25M (2.3x), 29 offers.
- Source: [Conductor profile](https://trustmrr.com/startup/conductor.md)

**Spin**
- A hosted REST/SDK layer over **Sage 100**, with an on-prem Windows agent using Sage's interfaces.
- Optionally a better-DX layer over Sage 50 US, for vertical SaaS (field service, e-commerce, AP/payroll) that must sync with on-prem accounting.

**Gap evidence**
- **Sage 50 US:**
  - Exposes a 32-bit .NET SDK that must run on the Windows machine where Sage 50 is installed.
  - Sage's own knowledge base says it is a .NET SDK and "A PHP SDK isn't currently available."
  - Source: search summary of [Apideck Sage 50 US guide](https://www.apideck.com/blog/how-to-integrate-with-the-sage-50-us-api)
- **Sage 100:**
  - DCKAP says there is no Sage-published REST API, and the COM-based Business Object Interface is the main route. Apideck's field guide says "Good (REST)," so the sources conflict.
  - Apideck says "Sage 100 is not yet supported."
  - Chift lists a Sage 100 connector (EU-focused).
  - Sources: search summary of [DCKAP](https://www.dckap.com/?p=35549), [Apideck field guide](https://radar.apideck.com/blog/sage-integration-field-guide), [Apideck Sage 100](https://www.apideck.com/accounting-software/sage-100.md), [Chift](https://chift.eu/tools/sage-100)
- **Unified APIs already covering Sage 50:**
  - Rutter's accounting page lists "Sage 50 Accounting" and "QuickBooks Desktop." — [Rutter](https://www.rutter.com/accounting)
  - Codat lists "Sage 50" and "Sage 50 Accounts." — [Codat docs](https://docs.codat.io/integrations/accounting/overview)
  - Merge lists only Sage Business Cloud Accounting and Sage Intacct. — [Merge](https://www.merge.dev/categories/accounting-api)

**Beatability**
- Sage 50 is contested (Rutter, Codat).
- Sage 100 has only a thin field (Chift; Apideck absent).
- No ratings data was obtained.

**Copyability (2)**
- Needs a Windows agent, COM/.NET interop, a reliable sync/queue and Sage developer-program access. Plan on 3+ months even for an experienced developer (my estimate).
- **Infra:** Modest, plus support load.

**Expansion**
- Sage 300, Sage 50 Canada (local SDK only, per Apideck's guide) and other on-prem accounting systems.
- Install-base counts not verified.

**Channel**
- Developer docs and SEO (inference; Conductor's channel is not disclosed).

#### S4. DASHP → D2D summer-sales commission and rep-pay ledger — **16/25 (R2 B3 C4 E4 Ch3) — PROVISIONAL**

**Original and revenue proof (founder-claimed only)**
- **Starter Story card:** DASHP, "Commission management software for pest control sales teams," $8K/mo self-reported; founded 2022; solo founder; "$50 to start"; growth via referral program and direct sales. — [Starter Story apps-so-simple](https://www.starterstory.com/data/apps-so-simple)
- **The original has since broadened.** dashp.io now sells "The Complete Pest Control Management Platform" (technician management, route optimization, field sales) and claims "hundreds of pest control companies." The commission-only revenue is therefore not isolated. — [dashp.io](https://dashp.io/)

**Spin**
- A commission, advance and clawback ledger plus a rep-facing pay app for door-to-door summer-sales organizations (solar, alarm, roofing, fiber, pest) with 5–100 reps.
- **Features:**
  - Install- or activation-triggered payouts and clawbacks on cancellation.
  - Manager override trees.
  - Weekly advances, housing/advance deductions, end-of-season bonuses.
  - Payroll export.

**Niche incumbents**
- **Sequifi:** "Commissions, payroll and HR in one platform… Tiers, splits, overrides and clawbacks, calculated automatically and carried straight into payroll." Verticals listed: Solar, Roofing, Fiber, Pest control. Pricing is demo-only. — [sequifi.com](https://sequifi.com/); [sequifi.com/pricing](https://sequifi.com/pricing)
- **SalesRabbit** (canvassing with a commission calculator), **RepCard** (canvassing and leaderboards; no commission detail found), and **PestPac**, Ecanvasser and Pocomos (canvassing and CRM). — search summary incl. [repcard.com/solutions/pest-control.md](https://repcard.com/solutions/pest-control.md), [pestpac.com](https://www.pestpac.com/features/door-to-door-pest-control-sales-software), [ecanvasser.com](https://ecanvasser.com/solution/pest-control)
- **Horizontal commission software is very well rated, but none is D2D-positioned:** Everstage 4.8★ (1,022), CaptivateIQ 4.8★ (874), Qobra 4.9★ (437), Sales Cookie 4.7★ (196), QuotaPath 4.5★ (123), Commissionly 4.9★ (44). — [Capterra commission software](https://www.capterra.com/commission-software/)
- **DASHP's current pest-control platform category is crowded:** GorillaDesk 4.8★ (278), FieldRoutes 4.3★ (404), PestPac 3.9★ (256). — [Capterra pest control](https://www.capterra.com/pest-control-software/)

**Beatability (3)**
- Sequifi already targets the exact verticals, but it is demo-only and bundled with HR/payroll. Its ratings were not obtained.
- A self-serve, flat-priced ledger for small teams is the opening (inference).

**Copyability (4)**
- A rules engine plus ledger plus mobile view; about 2–3 months.

**Expansion (4)**
- Recruiting/onboarding of summer reps (links to S2), leaderboards, housing management, 1099 documents.

**Channel**
- DASHP's own channels (referral and direct) are replicable in a tight industry network (inference).

#### S5. Khosmos → Spanish-first quoting/invoicing for US Latino-owned trades — **15/25 (R4 B2 C4 E2 Ch3) — PROVISIONAL, incumbent check incomplete**

**Original and revenue proof (Stripe-verified)**
- **Product:** Khosmos (France), founded Mar 2023. "Create complete and professional quotes in less than 1 minute. Sign them on-site or remotely. Invoice and collect payments."
- **Revenue:**
  - MRR $22,505 from 865 subscriptions; L12M $247,239; all-time $385,260.
  - Monthly revenue: Dec 2025 $15,514 → Apr $21,526 → Aug $21,506 → Oct $25,920.
- **Channels:** SEO, ASO, Facebook, Instagram, TikTok.
- Source: [Khosmos profile](https://trustmrr.com/startup/khosmos.md)

**Spin**
- A mobile-first app with Spanish UI, bilingual quote/invoice output and WhatsApp/SMS sharing, aimed at landscaping, painting, cleaning, drywall and roofing owner-operators.

**Incumbent evidence (partial)**
- **Horizontal field-service apps are large and well rated:** Housecall Pro 4.7★ (2,749), Jobber 4.6★ (1,490), Kickserv 4.4★ (387), JobNimbus 4.6★ (482). — [Capterra landscape](https://www.capterra.com/landscape-software/); [Capterra field service](https://www.capterra.com/field-service-management-software/)
- **Spanish marketing pages:**
  - Joist's and Housecall Pro's `/es/` paths return "Page not found."
  - Jobber's and Invoice Simple's `/es` pages were behind bot protection.
  - This is **weak evidence** (it says nothing about in-app language support).
  - Sources: [joist.com/es](https://www.joist.com/es/), [housecallpro.com/es](https://www.housecallpro.com/es/)

**Why it is only provisional**
- If any of Joist, Invoice2go or Jobber ships full Spanish in-app, beatability falls to 1–2.
- Market counts (Hispanic-owned contractor firms) were not obtained.

### Inferences
- **FireCert-US is the strongest new idea in this sweep.** It combines a verified, steep early curve, a regulated recurring workflow (NFPA due dates create built-in renewals), and an incumbent set that is either small-review-count, mid-market, or excludes small shops by policy. It also fits "copyable in 2–3 months."
- **Hirevire-camps is real but thin.** The camp suites lack video, but Hireflix shows the horizontal job is commoditized at $75/mo with 5.0★. Season-pass pricing plus a CampMinder hand-off is the only defensible wedge. Bundling S2 with S4 (seasonal recruiting plus pay for summer-sales teams) may be stronger than either alone.
- **Conductor is the best revenue proof in the set** (verified $47k MRR, rising every month, 95% margin). A Sage spin is technically harder and partly covered by unified APIs. Buying Conductor itself ($1.25M asking) is the cleaner route to this revenue than cloning it.

### Gaps
- **TAM counts:**
  - US fire-extinguisher service companies (the NAFED page returned 404).
  - Ski areas (the NSAA stats page returned 404).
  - D2D sales organizations and Hispanic-owned trade businesses.
  - Sage 100 install base.
  - The Census CBP API now requires a key, and web search was exhausted.
- **Ratings not obtained** for Sequifi, ServiceTrade pricing, Gipper and Box Out, Joist/Invoice2go Spanish support, and TravelJoy.
- **None of the originals disclose acquisition channels**, except Khosmos (SEO/ASO/social), EmailEngine (SEO), P7M (ASO/SEO), Leverage, Cosmo and Chatwith.

---

## Q3. Which spins fail (kill list), and which verified originals still need a spin test (hold list)?

### Takeaway
- **All three mandated re-checks failed:**
  - **Orshot → high-school game-day graphics:** Gipper is the NFHS's exclusive graphics partner at $625–$3,000/yr, Box Out sells at $480–$2,400/yr, and free alternatives exist.
  - **Web3Forms → HIPAA or agency form backends:** Jotform covers HIPAA, and an existing agency-plan clone, Static Forms, earns about $1k MRR after 6 years.
  - **Image-Charts:** QuickChart is $0–$40/mo with 4B+ renders, and Image-Charts' own revenue is falling.
- **Twelve more spins or originals are killed** because a well-rated incumbent dominates the niche, the core software bundles the feature, or the original is collapsing on verified data.
- **Twelve verified originals are held** for a follow-up with web search.

### Cited Findings

**Mandated evaluations (originals Orshot, Web3Forms, Image-Charts; Hirevire is S2 above)**

**K1. Orshot → automated game-day / score graphics for US high-school athletics — KILL.**
- **Original (verified, healthy):**
  - Orshot (UK), "Automate Image, PDF & Video Generation via API."
  - MRR $12,657 from 223 subs; L12M $73,838.
  - Monthly revenue: Dec 2025 $2,160 → Oct 2026 $11,498.
  - Source: [Orshot profile](https://trustmrr.com/startup/orshot-com.md)
- **Original's pricing:** free (100–1,500 credits), Launch $39, Grow $160 (20,000 credits), Scale $349 (75,000 credits). — [Orshot pricing](https://orshot.com/pricing)
- **Gipper:**
  - Annual-only plans at $625, $1,500 and $3,000.
  - Separate "K12 Schools" and "K12 Teams" plans; a "17k+ high school & college logo database"; Content Planner scheduling.
  - Sources: [Gipper pricing](https://www.gipper.com/pricing)
  - Gipper was "named exclusive social media graphics solution partner of NFHS." — [NFHS](https://nfhs.org/stories/gipper-named-exclusive-social-media-graphics-solution-partner-of-nfhs-in-expanded-partnership)
- **Box Out Sports:**
  - Basic $60/mo or $480/yr; Plus $175/mo or $1,500/yr; Premium $275/mo or $2,400/yr.
  - Unlimited users and teams; 13,000+ logos; live-stats score graphics.
  - Serves "high school, college, and amateur athletics" and Minor League Baseball.
  - Source: [Box Out llms.txt](https://boxoutsports.com/llms.txt)
- **Free alternatives** (Canva, Rocket Graphics) are being pushed to schools as Gipper replacements. — search summary of [digitalrecordboard.com](https://digitalrecordboard.com/blog/gipper-free-switch-to-canva/), [halloffame-online.com](https://halloffame-online.com/blog/rocket-graphics-free-alternative-to-gipper-schools-save-money/)
- **Verdict:** A fairly priced incumbent with governing-body distribution, plus a paid #2 and free substitutes. Gipper's "K12 Teams" plan and Box Out's "amateur athletics" positioning cover youth and club sports too.
- **Untested Orshot spins** for the next round: car-dealer inventory graphics, restaurant specials synced from POS, church sermon-series graphics.

**K2. Web3Forms → (a) HIPAA-ready form backend for healthcare practice sites; (b) white-label form inbox for web agencies — KILL (b); DEPRIORITIZE (a).**
- **Original (verified, strong):**
  - Web3Forms (India), "Contact Form API for Modern Websites."
  - MRR $44,130 from 3,209 subs; L30 $47,600.
  - Monthly revenue: Dec 2025 $7,917 → Jun $47,141 → Oct $47,789.
  - DR 86; about 412,000 users; free tier of 250 submissions/month.
  - Source: [Web3Forms profile](https://trustmrr.com/startup/web3forms.md)
- **(b) Agency inbox:**
  - **Static Forms**, a near-identical form backend with a $19/mo Agency plan, shared inbox, spam filtering and AI replies, has **MRR $1,038** after being founded in May 2020. It is listed for sale at $40,000 (2.9x). — [Static Forms profile](https://trustmrr.com/startup/static-forms.md)
  - Formspree sells $15/$30/$90 monthly tiers, or $10/$20/$60 per month billed annually. — [Formspree plans](https://formspree.io/plans)
  - Basin starts at $12.50/mo. — [Basin pricing](https://usebasin.com/pricing)
  - **Verdict:** Weak willingness to pay for the agency angle; the market is commoditized.
- **(a) HIPAA:**
  - Jotform's pricing page offers HIPAA features on paid plans ("excludes HIPAA compliance features" only on the free Starter plan). — [Jotform pricing](https://www.jotform.com/pricing/)
  - Formspree's plans page does not mention HIPAA. — [Formspree plans](https://formspree.io/plans)
  - **Verdict:** HIPAA requires BAAs, audit logging and encrypted storage, which breaks the 1–3-month, low-liability MVP constraint (inference). Not a strict kill under the rule, but deprioritized.
- **Inference:** Web3Forms' moat is distribution (DR 86, a generous free tier), not a niche. Its revenue is best copied by **SEO-led horizontal developer tools**, not vertical spins.

**K3. Image-Charts → chart-image API (any niche spin) — KILL.**
- **Original (verified, declining):**
  - Image-Charts (France, founded 2017).
  - MRR $6,262 from 50 subs; L12M $78,625; all-time $543,969.
  - Revenue is lumpy annual renewals (Jan $18,673, Apr $17,007; most months $2.3–3.1k), with Oct 2026 at $2,316.
  - Source: [Image-Charts profile](https://trustmrr.com/startup/image-charts.md)
- **Original's pricing:** $89/mo paid yearly, and $224/mo Enterprise. — [Image-Charts pricing](https://www.image-charts.com/pricing)
- **QuickChart:** $0/mo, or $40/mo for 10,000 images/month; "4 billion+ images rendered"; renders any Chart.js config. — [QuickChart pricing](https://quickchart.io/pricing/)
- **NiftyImages:** $59/$149/$239 tiers including charts and data stores for personalized email images, which covers the "charts in personalized emails" spin. — [NiftyImages pricing](https://niftyimages.com/pricing)

**Other kills (spins derived from verified originals in Inventory A/B)**

| # | Spin (original) | Original's verified state | Why killed (incumbent evidence) |
|---|---|---|---|
| K4 | Catering inquiry → quote → invoice SaaS for independent restaurants (Catering Funnels) | $4.4k MRR, 8 subs, DFY service-heavy — [profile](https://trustmrr.com/startup/catering-funnels.md) | Capterra catering: Tripleseat 4.7★ (576), HoneyBook 4.7★ (695), Total Party Planner 4.8★ (153), Perfect Venue 4.8★ (82), Event Temple 4.9★ (76), Curate 4.7★ (218), CaterTrax 4.6★ (128) — [Capterra](https://www.capterra.com/catering-software/); Toast sells "Catering & events" inside its POS — [Toast](https://pos.toasttab.com/products/catering-and-events) |
| K5 | AI voicemail transcription + SMS reply for US firms (VoxNow) | $3.7k MRR, 32 subs — [profile](https://trustmrr.com/startup/voxnow.md) | Core phone software bundles it: OpenPhone lists "Voicemail transcripts" and "AI call summaries and transcripts" in its plans ($0/$25/$49/$99/$199 tiers shown) — [OpenPhone pricing](https://www.openphone.com/pricing) |
| K6 | Group-trip organizer payments/rosters (JourneyFuse model) | $11.2k MRR, 563 subs in 8 months — [profile](https://trustmrr.com/startup/journeyfuse.md) | WeTravel 4.8★ (529); Ezus 4.7★ (61); YouLi 4.7★ (30) — [Capterra travel agency](https://www.capterra.com/travel-agency-software/) |
| K7 | Any employee-recognition spin (Karma) | Revenue down $27.7k → $20.6k/mo — [profile](https://trustmrr.com/startup/karma.md) | Awardco 4.9★ (4,860), Guusto 4.9★ (3,857), Workhuman 4.8★ (2,162), Bonusly 4.8★ (1,611), Kudos 4.8★ (1,126) — [Capterra](https://www.capterra.com/employee-recognition-software/) |
| K8 | Vacation-rental guest ops/upsells, US (stealth, for sale $600k) | $16.7k → $10.6k/mo — [profile](https://trustmrr.com/startup/anonymous-startup-31.md) | Hostaway 4.8★ (1,623), Lodgify 4.5★ (1,312), ResNexus 4.8★ (432), GuestWisely 4.7★ (191), Hospitable 4.7★ (145) — [Capterra](https://www.capterra.com/vacation-rental-software/) |
| K9 | SMS cart recovery for US stores (CartBoss) | $43.1k → $28.6k/mo — [profile](https://trustmrr.com/startup/cartboss.md) | Clearstream 4.8★ (708), SlickText 4.8★ (272), EZ Texting 4.5★ (273), TextP2P 5.0★ (130) — [Capterra SMS](https://www.capterra.com/sms-marketing-software/) |
| K10 | Local-SEO rank tracker for agencies (LocalRank; Flippa GBP tracker) | LocalRank $44.1k → $18.2k/mo, asking 10.2x — [profile](https://trustmrr.com/startup/localrank-so.md); Flippa tracker for sale at $575k — [listing](https://flippa.com/13365450) | Two sellers exiting a falling category; the SEO category is saturated (Semrush 4.6★ (2,330), Ahrefs 4.7★ (585), AgencyAnalytics 4.8★ (116), Birdeye 4.7★ (709)) — [Capterra SEO](https://www.capterra.com/seo-software/) |
| K11 | Home-service booking (ConvertLabs, Calendesk) | ConvertLabs $35.6k → $27.3k/mo — [profile](https://trustmrr.com/startup/convertlabs.md) | Housecall Pro 4.7★ (2,749), Jobber 4.6★ (1,490) — [Capterra field service](https://www.capterra.com/field-service-management-software/) |
| K12 | Interactive demos/SOP docs (Guidejar) and AI chatbots (Chatwith, anon-2) | Chatwith $13.2k → $6.0k; anon-2 $13.8k → $5.7k — [Chatwith](https://trustmrr.com/startup/chatwith.md), [anon-2](https://trustmrr.com/startup/anon-2.md) | Verified decline in originals; crowded (incumbents not re-checked this session) |
| K13 | Chrome/social-platform add-ons (Kortex, FriendFilter, RTMP.IN) | Kortex $56.6k (Mar) → $2.5k (Oct); FriendFilter $12.5k → $3.7k; RTMP.IN 3 active subs — [Kortex](https://trustmrr.com/startup/kortex-notebooklm.md), [FriendFilter](https://trustmrr.com/startup/friendfilter-groupfilter.md), [RTMP.IN](https://trustmrr.com/startup/rtmp-in) | Platform dependency, shown by collapsing verified revenue |
| K14 | EmailEngine clone | $19.9k MRR, solo, $1,450/yr — [profile](https://trustmrr.com/startup/emailengine.md) | Not copyable in 1–3 months: multi-protocol (IMAP/SMTP, Gmail API, Microsoft Graph) self-hosted infra (inference) |
| K15 | AI-SEO autopilot clones (RankAI, Rank Prompt, ChatSEO) | Growing on verified data ($35–57k MRR) — [RankAI](https://trustmrr.com/startup/rankai), [Rank Prompt](https://trustmrr.com/startup/rank-prompt) | Not niche-able; horizontal AI-SEO is crowded (inference; no incumbent check run) |

**Hold list: verified originals with a plausible US spin that was not tested this session**

| Original (verified) | Revenue evidence | Candidate US spin to test next |
|---|---|---|
| P7M.io: browser viewer for Italy's mandatory `.p7m` signatures | $3.8k L30; solo; ASO/SEO — [profile](https://trustmrr.com/startup/confidential-startup-70.md) | US "mandate-created file format" utilities (e.g., e-filing formats); none identified yet |
| MON ATELIER: repair-shop ERP, €19–39/mo | $67 → $3.6k/mo in 7 months; for sale $120k — [profile](https://trustmrr.com/startup/mon-atelier.md) | US independent bike/e-bike or appliance repair shops |
| LC (licitacao.pro): AI that finds and summarizes Brazilian public tenders | $854 → $8.9k/mo; 72k visitors; solo — [profile](https://trustmrr.com/startup/lc.md) | Municipal/county bid alerts for small US trades |
| FreeTCF: single-exam (TCF Canada) prep app | $23.1k MRR — [card](https://trustmrr.com/startup/freetcf) | Other single-exam US credentials (not NICET, which was assessed earlier) |
| Flippa nursing study app | $17.4k MRR, TikTok-led — [listing](https://flippa.com/14338446) | NCLEX incumbents unchecked |
| Flipify: marketplace deal alerts | $4.0k → $19.3k/mo — [profile](https://trustmrr.com/startup/flipify.md) | Vertical alerts (farm equipment, boats, RVs); scraping-ToS risk |
| Stagetimer: event countdown timer | $30K/mo founder-claimed — [Starter Story](https://www.starterstory.com/data/apps-so-simple) | Church/worship run-of-show timers (check ProPresenter / Planning Center) |
| LaDataViz: paid Tableau add-ons | $3.3k MRR — [profile](https://trustmrr.com/startup/ladataviz.md) | Power BI / Looker Studio add-ons |
| Dashla: Tesla iPhone dashboard | $4.1k MRR, 1,547 subs — [profile](https://trustmrr.com/startup/dashla.md) | Companion apps for other EV brands |
| Angel Match: investor database | $25.8k MRR, durable since 2019 — [profile](https://trustmrr.com/startup/angel-match.md) | Grant-funder database for small nonprofits |
| Flippa SOP SaaS | "$108K annual revenue," 8 yrs — [listing](https://flippa.com/11413188) | Vertical SOP template packs (dental, HVAC) |
| Send Letters Online UK | $647 → $4.0k/mo — [profile](https://trustmrr.com/startup/send-letters-online-uk.md) | US online certified-mail letters (check existing US services) |

### Inferences
- **The kill pattern is consistent.** Horizontal SMB categories that look easy (recognition, SMS, catering, VR guest apps, local SEO) all have several 4.7–4.9★ products with hundreds or thousands of reviews. Survivors sit where Capterra shows **single-digit or double-digit review counts** for the niche-specific incumbents (fire inspection) or **no niche-specific product at all** (camp video screening).
- **Verified revenue curves are themselves a kill signal.** Six originals in the inventory lost 40–95% of monthly revenue within a year (Kortex, FriendFilter, LocalRank, anon-2, Chatwith, Formflow). Cloning a declining category is riskier than its lifetime revenue suggests.

### Gaps
- **The hold-list spins need incumbent checks.** Web search was exhausted, and the platform forbids search-engine workarounds via curl.
- **Ratings for Gipper and Box Out** were not fetched (no Capterra URLs known), so K1 rests on pricing, distribution and free substitutes rather than review counts.
- **K14 and K15** are judgment calls without a fresh incumbent check.
