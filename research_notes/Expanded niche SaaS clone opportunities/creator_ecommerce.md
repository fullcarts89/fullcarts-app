# Creator & small e-commerce "clone and improve" SaaS (US): photographers, artists, musicians, authors, makers, Shopify brands (excluding video creation)

Research date: 2026-11-07. All pages were fetched on that date unless stated. Raw pages and parsers are saved under `/tmp/claude-0/-home-user-fullcarts-app/26da1d04-da96-596a-8ca0-1065c2a8525f/scratchpad/creator_ecommerce/`.

Provenance labels used throughout:
- **[Stripe-verified]**: TrustMRR, where revenue is "verified with Stripe API key".
- **[Latka est.]** / **[Growjo est. via Latka]**: third-party estimates, not company figures.
- **[CEO/founder-claimed]** or **[vendor-claimed]**: the company's own claim.
- **[Shopify App Store]**: rating and review count from the app's listing.
- **[iOS]**: US App Store rating and rating count from the iTunes Search API, or reviews from the apps.apple.com page.
- **[Capterra]**: rating and review count from Capterra category pages.
- **[ProPublica 990]**: nonprofit filing data.
- **[StoreLeads]**: third-party Shopify store census.
- **[O*NET/BLS]**: 2025 employment from BLS employment projections, shown on O*NET.

Scoring: five criteria, each scored 1–5, for a total out of 25.
- **Rev** (revenue proof): 5 = Stripe-verified or large disclosed revenue; 3 = third-party estimates plus proof from adjacent products; 1 = none.
- **Beat** (beatability): 5 = a poorly rated or neglected incumbent, shown by dated evidence.
- **Copy** (copyability): 5 = MVP in about 1 month on a standard stack.
- **Exp** (expansion): 5 = many adjacent niches, with large counts.
- **Chan** (channel replicability): 5 = an app-store or marketplace listing that a newcomer can reproduce.

---

## Q1. What market-size anchors, data sources and access limits frame this round?

### Takeaway
The anchors below are current (Q3/Q4 2026) and give a usable TAM base:
- Shopify has about 3.2M live stores, 1.25M of them in the US, growing about 15% a year.
- Creator occupations are counted in the low hundreds of thousands: photographers 145k, musicians 170k, writers 140k, bakers 262k.

Several standard sources were blocked: BLS OOH, the Census API, G2, BackerKit and Printavo. Bing results were mostly noise. So the evidence leans on the Shopify App Store, the iOS App Store, Capterra, TrustMRR, Latka and vendor pricing pages.

### Cited Findings
- 3,225,094 live Shopify stores. Stores grew 3.7% QoQ and 15% YoY in Q3 2026 [StoreLeads, report dated Oct 30 2026] — [StoreLeads](https://storeleads.app/reports/shopify)
- 38.9% of Shopify stores are in the US, which is 1,253,193 stores [StoreLeads] — [StoreLeads](https://storeleads.app/reports/shopify)
- Shopify stores by category [StoreLeads] — [StoreLeads](https://storeleads.app/reports/shopify):

  | Category | Stores |
  |---|---|
  | Apparel | 875,022 (27.1%) |
  | Home & Garden | 409,956 |
  | Beauty & Fitness | 350,637 |
  | Food & Drink | 219,248 |
  | Arts & Entertainment | 109,431 |
  | Toys & Hobbies | 85,701 |
  | Gifts & Special Events | 60,028 |
  | Games | 33,940 |
  | Books & Literature | 28,629 |

- US employment in 2025 [O*NET/BLS; source line: "Bureau of Labor Statistics 2025 wage data and 2025-2035 employment projections"]:
  - Photographers: 145,000 — [O*NET 27-4021](https://www.onetonline.org/link/summary/27-4021.00)
  - Musicians & singers: 170,400 — [O*NET 27-2042](https://www.onetonline.org/link/summary/27-2042.00)
  - Disc jockeys (except radio): 16,900 — [O*NET 27-2091](https://www.onetonline.org/link/summary/27-2091.00)
  - Writers & authors: 140,300 — [O*NET 27-3043](https://www.onetonline.org/link/summary/27-3043.00)
  - Craft artists: 11,500 — [O*NET 27-1012](https://www.onetonline.org/link/summary/27-1012.00)
  - Fine artists: 28,900 — [O*NET 27-1013](https://www.onetonline.org/link/summary/27-1013.00)
  - Bakers: 262,400 — [O*NET 51-3011](https://www.onetonline.org/link/summary/51-3011.00)
  - Printing press operators: 144,000 — [O*NET 51-5112](https://www.onetonline.org/link/summary/51-5112.00)
- Access limits:
  - bls.gov OOH pages returned HTTP 403, and the BLS API returned 503.
  - The Census nonemployer API returned "Missing Key".
  - g2.com, backerkit.com/pricing and printavo.com returned 403.
  - The iTunes Search API rate-limited (403) after about 30 queries.
  - All of these are noted as gaps below.

### Inferences
- The O*NET figures come from BLS Employment Projections. These normally include self-employed workers; photographers at 145k is well above the wage-and-salary-only OES level. Even so, they undercount hobbyist and side-income creators such as home bakers, Etsy makers and indie authors. Treat them as floors.
- Shopify category counts are a better TAM proxy for "small brand" tools than occupational counts.

### Gaps
- Census nonemployer counts (NAICS 711510 independent artists/writers, 541921 portrait photography, 311811 retail bakeries) need an API key.
- Etsy active-seller counts were not fetched.
- Bowker self-published ISBN counts were not found; the Bing search returned only Bowker homepages.

---

## Q2. Shortlist #1 — "Bakesy for print shops": a made-to-order shop OS for small apparel decorators (DTF, embroidery, screen print, sublimation), expanding to sign shops and engravers. Score 20/25

### Takeaway
The category leader for decorators, Printavo, has a 1.8★ mobile app. It sits inside a PE-style roll-up, Taivo (formerly Inktavo), with 11,000+ customers across five products.

The modern challenger, YoPrint, is small (about $1.2M est.) and priced at $59–69/mo per user. Bakesy separately proves that home-based made-to-order businesses pay $10–18/mo for a mobile-first order/quote/deposit app: it has 4.9★ from 7,292 ratings.

A mobile-first, cheaper shop OS for 1–3 person DTF and embroidery shops is a credible clone-and-improve play.

### Cited Findings
**Original and revenue proof**
- Taivo ("Inktavo is now Taivo") bundles OrderMyGear, Printavo, Clarity Software, GraphicsFlow and OneSource [vendor-claimed] — [Taivo/Inktavo](https://www.inktavo.com/)
  - It claims "11,000+ businesses" across North America, the UK and Europe.
  - Customers include apparel decorators, contract decorators and sign shops.
- YoPrint revenue is about $1.2M (Sep 2025), with 11 employees [Latka est.] — [Latka](https://getlatka.com/companies/yoprint)

**Incumbents: ratings and prices**
- Printavo iOS app: 1.8★ from 52 ratings. First released 2017-03-10; last updated 2026-10-07 [iOS] — [App Store](https://apps.apple.com/us/app/printavo/id1191027240), [iTunes API](https://itunes.apple.com/search?term=printavo&entity=software&country=us)
- YoPrint Basic: $59/mo billed annually or $69 monthly. Includes 1 user; additional users $10/user [vendor pricing] — [YoPrint](https://www.yoprint.com/pricing)
- Capterra print-estimating category [Capterra] — [Capterra](https://www.capterra.com/print-estimating-software/):
  - shopVOX 4.6★ (243)
  - Printlogic 4.5★ (196)
  - PrintSmith Vision 4.0★ (214)
  - ePS Pace 3.7★ (84)
- Printavo's pricing page returned 403, so live Printavo pricing is not verified.

**Proof of the made-to-order model**
- Bakesy (Bakesy, LLC): iOS 4.9★ from 7,292 ratings. Released 2020-07-12; updated 2026-11-04 [iOS] — [App Store](https://apps.apple.com/us/app/bakesy-home-bakery-biz-app/id1515139393)
  - In-app purchases: "Bakesy Membership" $9.99 and "Bakesy Premium Membership" $17.99.
  - A 11/01/2023 review shows the channel: "After struggling with other website builders… I saw an ad for Bakesy… I literally had a website completed & posted on social media in just a few hours."

**Adjacent Shopify activity: DTF gang-sheet apps are young and lightly reviewed (see #5)**
- Build a Gang Sheet: 4.4★ (45), launched Jul 2023 — [Shopify](https://apps.shopify.com/build-a-gang-sheet)
- Kixxl: 4.7★ (35) — [Shopify category](https://apps.shopify.com/categories/selling-products-custom-products-custom-file-upload/all)

**TAM**
- 875,022 Shopify stores sell Apparel [StoreLeads] — [StoreLeads](https://storeleads.app/reports/shopify)
- Printing press operators: 144,000 employed (2025) [O*NET/BLS] — [O*NET](https://www.onetonline.org/link/summary/51-5112.00)

### Inferences
**Beatability.** Three signals point the same way:
- the incumbent mobile app is rated 1.8★;
- the owner is a roll-up spread across five products;
- per-user pricing ($59–69 plus $10/user) is high for garage-scale DTF and embroidery shops.

Bakesy's 7k ratings show that mobile-first, cheap, consumer-grade UX wins with home-based made-to-order operators.

**Proposed spin.** A phone-first shop OS for 1–3 person decorators at $19–39/mo flat.

**MVP (6–10 weeks):**
- Quote builder with garment and print-location pricing matrices.
- Customer art upload, then mockup, then e-sign proof approval.
- Deposit and balance payments through Stripe.
- Kanban production board.
- Shopify and Etsy order import.
- SMS/email status updates.

**Expansion path:**
- Built-in gang-sheet builder (#5).
- Blank-garment ordering via distributor APIs (S&S/SanMar; inference — not verified this session).
- Team-store / fundraiser stores (OrderMyGear's niche).
- Adjacent niches: sign and vinyl shops, laser engravers, Cricut/sublimation home crafters, promo-product resellers.

**Channel.**
- Incumbents: Bakesy uses paid social (review quote). Taivo uses a multi-product ecosystem upsell.
- For a newcomer: Facebook groups and YouTube for DTF/embroidery beginners, a Shopify App Store presence via #5, and the DTF printer and film vendor ecosystem.

**Score:** Rev 3, Beat 4, Copy 4, Exp 5, Chan 4 = **20/25**.

### Gaps
- Printavo's current pricing and its Capterra rating (page blocked).
- YoPrint's ratings.
- Count of US DTF and embroidery micro-shops.
- Whether Taivo has raised prices recently (no dated source found).

---

## Q3. Shortlist #2 — Author direct-sales Shopify app: multi-printer print-on-demand, ebook/audiobook delivery, signed and special editions, pre-orders and Kickstarter backer import. Score 19/25

### Takeaway
On Shopify, the two book-printing connectors are poorly rated:
- Lulu Direct: 3.9★ (47), with 21% one-star reviews.
- Bookvault: 1.8★ (9), with July 2026 "nightmare" reviews.

BookFunnel dominates ebook delivery and now sells direct as merchant of record, but it does not print. Authors demonstrably pay for niche tools: Marky has a Stripe-verified $22.2k MRR from 478 subscriptions.

An app that routes print orders across printers and unifies print and digital fulfilment for author-run Shopify stores is beatable and copyable.

### Cited Findings
**Lulu Direct** [Shopify App Store] — [Shopify](https://apps.shopify.com/lulu-direct), [1-star reviews](https://apps.shopify.com/lulu-direct/reviews?ratings%5B%5D=1)
- 3.9★ from 47 reviews, launched Apr 26 2018.
- Rating split: 49% 5★; 13% 2★ (6 reviews); 21% 1★ (10 reviews).
- Dated quotes:
  - Jan 6 2021: "Absolutely the WORST app experience I've had so far."
  - Jun 1 2024: "When i am trying to connect Lulu direct to my shopify store and open the app, it fails to load…"
  - May 4 2026: "i wish i could speak to a live person quicker an more direct"
- Balance: there are positive reviews from Sep 8 2026 and Jul 2026, praising fulfilment speed and support.

**Bookvault** [Shopify App Store] — [Shopify](https://apps.shopify.com/bookvault)
- 1.8★ from 9 reviews, launched May 23 2022.
- Jul 13 2026: "Cannot get this to work… it navigates me out of Shopify and into BookVault with no way to connect the two."
- Jul 19 2026: "So glitchy… it won't let me unlink the store… it's a nightmare"
- On Oct 23 2026 the developer replied that a "rebuilt Bookvault app… now runs inside your Shopify admin".

**BookFunnel**
- Pricing [vendor pricing] — [BookFunnel pricing](https://bookfunnel.com/pricing/):
  - First-Time Author: $30/yr, 500 downloads/mo.
  - Mid-List: $200/yr, 5,000 downloads/mo, up to 4 pen names.
  - Bestseller: $300/yr, unlimited.
  - Includes crowdsourcing delivery, watermarking and ARC delivery.
- BookFunnel now sells direct as merchant of record: "We take the payment, work out and file the sales tax and VAT, and deliver the books" [vendor] — [BookFunnel Sell](https://bookfunnel.com/sell/)

**Other comparisons**
- Gumroad charges 10% + $0.50 per direct sale and 30% via its Discover marketplace [vendor pricing] — [Gumroad pricing](https://gumroad.com/pricing)
- Kickstarter now runs its own built-in Pledge Manager (relevant to backer import) — [Kickstarter](https://start.kickstarter.com/pledge-manager)

**Willingness to pay**
- Marky, "a tool for self-publishing authors to manage their social media" [Stripe-verified] — [TrustMRR Marky](https://trustmrr.com/startup/marky):
  - MRR $22,204 from 478 active subscriptions.
  - All-time revenue $1,016,675.
  - Founded July 2023, US.
- Plottr: about $550K revenue (Dec 2025), 5 employees [Latka est.] — [Latka](https://getlatka.com/companies/plottr)

**ARC module comparables**
- Booksprout iOS: 2.5★ from 19 ratings, updated 2026-10-02 [iOS] — [App Store](https://apps.apple.com/us/app/booksprout/id1590873280)
- BookSirens: $10 per ARC + $2 per reader, or $100/yr unlimited [vendor pricing] — [BookSirens](https://booksirens.com/pricing)

**TAM**
- 28,629 Shopify stores in Books & Literature [StoreLeads] — [StoreLeads](https://storeleads.app/reports/shopify)
- Writers & authors: 140,300 (2025) [O*NET/BLS] — [O*NET](https://www.onetonline.org/link/summary/27-3043.00)

### Inferences
**Beatability.** Both print connectors fail at the basic job of connecting the store and syncing stock or listings. BookFunnel owns digital delivery but not print. Authors with Shopify stores therefore stitch together 2–3 tools.

**Kill-rule check.** No modern 4.6★+ app with many reviews dominates "print + digital for author stores", so this passes.

**Proposed spin.** "Author Store Fulfilment" for Shopify:
- route each print SKU to Lulu, Bookvault or another printer API, with cost and shipping-time comparison and fallback;
- deliver ebooks and audiobooks natively, or via BookFunnel;
- signed and personalised-edition workflows (an inscription field, routed to the author's packing list);
- pre-orders with release-date capture;
- bundles of print + ebook + audiobook;
- CSV import of Kickstarter or BackerKit backers into Shopify orders.

**MVP (6–8 weeks):**
- One printer integration plus digital delivery and stock sync.
- Signed-edition flag.
- Then a second printer.

**Expansion path:**
- ARC/street-team module, which competes with Booksprout (2.5★ iOS).
- Comics and zines, tabletop RPG creators (PDF + POD), poets, cookbook authors, photographers' photobooks.
- Merch (bookmarks, art prints) through POD partners.

**Channel.**
- Incumbents: Shopify App Store, plus BookFunnel's group promos and author swaps (built-in network).
- For a newcomer: author Facebook groups and conferences, podcasts, the App Store listing, and partnerships with printers.

**Score:** Rev 3, Beat 4, Copy 4, Exp 4, Chan 4 = **19/25**.

### Gaps
- Whether the Lulu Print API and Bookvault API are open to third-party apps. This is believed but not verified this session.
- BookFunnel's direct-sales fee percentage (not shown on the fetched page).
- Number of indie authors selling direct on Shopify specifically.

---

## Q4. Shortlist #3 — Juried art-fair and makers-market application, jury and booth platform (organizer-paid), expanding to juried exhibitions, photo contests and holiday markets. Score 19/25

### Takeaway
The US art-fair application market runs on ZAPP (live since 2004) and CaFÉ, both owned by the nonprofit Creative West, which reported $23.2M in 2024–25. Pricing is per call and per application.

The modern for-profit entrant, Eventeny (about $5.9M est.), charges $240/mo plus 3%, and its iOS app is rated 2.8★. Submittable proves the broader submissions market at $49M revenue.

A modern, cheaper, application-to-booth-to-payment platform for small and mid-size fairs and makers markets is beatable. ZAPP's artist-profile network effect is the main moat.

### Cited Findings
**Original: ZAPP and CaFÉ**
- ZAPP is "Where artists & art festivals connect", footer "2004-2026© ZAPP™ Software, LLC | Creative West". The live listing includes 2026–27 fine-art festivals such as Winter Park Sidewalk Art Festival 2027 and St. Armands Fall Fine Art Festival Oct 2026 [vendor] — [ZAPP](https://www.zapplication.org/)
- The ZAPP events list filters by application fee and booth fee — [ZAPP events](https://www.zapplication.org/participating-events.php)
- CaFÉ (Creative West, "formerly WESTAF") pricing for organizers [vendor pricing] — [CaFÉ pricing](https://www.callforentry.org/how-it-works/pricing/):
  - $225 onboarding.
  - $250 per call (Pro) or $475 per call (Plus).
  - $2.49 per application on Pro; on Plus, $0 up to 250 applications, then $2.49.
  - $120 annual renewal.
  - Plus electronic processing fees.

**Revenue proof**
- Creative West (Denver) revenue: $23,215,745 in the 2024–2025 filing. This is the whole organisation and includes grant pass-through, not just ZAPP/CaFÉ [ProPublica 990] — [ProPublica](https://projects.propublica.org/nonprofits/search?q=%22Creative+West%22)
- Submittable: $49M annual revenue (Nov 2023), "according to a submission to GetLatka"; $64.3M raised [company-submitted via Latka; dated 2023] — [Latka](https://getlatka.com/companies/submittable)
- Eventeny: about $5.9M revenue (Sep 2025); 54 employees (Jan 2025) [Latka est.] — [Latka](https://getlatka.com/companies/eventeny)

**Incumbent pricing and quality**
- Eventeny Pro: "$240/mo… billed annually ($2,880/yr)" + "3% transaction fees". Includes vendor, sponsor and talent booth mapping [vendor pricing] — [Eventeny pricing](https://www.eventeny.com/pricing/)
- Eventeny iOS app: 2.8★ from 63 ratings, updated 2026-07-31 [iOS] — [App Store](https://apps.apple.com/us/app/eventeny/id1550972026)
  - 04/24/2025: "The user interface is abysmal. You cannot bookmark, favorite, or otherwise flag an event you're attending…"
  - 04/17/2025: "I can't click on half the buttons, including the feedback and help buttons…"
  - These reviews are from the attendee-facing side.

**TAM floors**
- Craft artists 11,500 and fine artists 28,900 (2025) [O*NET/BLS] — [O*NET craft](https://www.onetonline.org/link/summary/27-1012.00), [O*NET fine](https://www.onetonline.org/link/summary/27-1013.00)
- 109,431 Shopify stores in Arts & Entertainment [StoreLeads] — [StoreLeads](https://storeleads.app/reports/shopify)

### Inferences
**Beatability.**
- The incumbents are a 2004-era nonprofit product and a for-profit entrant with a poorly rated app and a high entry price.
- Small fairs, makers markets and holiday markets with fewer than 250 vendors are poorly served at $240/mo or $250–475 per call.

**Kill-rule check.** No well-rated modern tool clearly dominates this exact sub-niche (juried applications plus booth assignment plus vendor payments for small and mid-size fairs), so this passes.

**Moat to overcome.** Artists keep one reusable portfolio in ZAPP and CaFÉ. Ways in:
- free portfolio import;
- free for artists;
- organizer pricing per event under $150, or a per-application fee passed to applicants.

**MVP (8–12 weeks):**
- Organizer call builder with custom fields and image requirements.
- Artist profiles with reusable portfolio.
- Blind jury scoring.
- Accept/waitlist/decline emails.
- Booth fee checkout via Stripe Connect.
- Drag-drop booth map.
- Vendor communications.

**Expansion path:**
- Juried exhibitions and photo contests (CaFÉ's other use).
- Makers markets and holiday markets.
- Farmers-market vendor management.
- Open-studio tours.
- Comic cons' artist alleys.
- Add-ons: public artist directory/marketplace, sponsor management, insurance and permit document collection, day-of check-in.

**Channel.**
- Incumbents: two-sided network effects (artists find shows on ZAPP).
- For a newcomer: direct outreach to organizers (lists are public on ZAPP and CaFÉ), then an SEO'd show calendar for artists.

**Score:** Rev 4, Beat 4, Copy 4, Exp 4, Chan 3 = **19/25**.

### Gaps
- ZAPP's organizer price list (the "ZAPP for Events" page returned 404).
- Number of US art fairs and makers markets.
- Dated artist complaints about ZAPP. The Bing search returned irrelevant results.

---

## Q5. Shortlist #4 — The "Marky model" for an adjacent creator niche: a niche-specific social-media manager (not video generation) for indie musicians around release cycles, or for Etsy/Shopify makers. Score 18/25

### Takeaway
Marky shows that a narrowly targeted social-media tool for one creator niche (self-published authors) can reach a Stripe-verified $22.2k MRR from 478 subscriptions within about 3 years. Social schedulers in general also earn well: Postiz has $379k MRR.

Cloning the model for a niche with its own content rhythm is a proven-revenue, copyable play. Candidates are music release campaigns, or maker product drops and craft-fair announcements. It must stay out of the excluded AI-video category.

### Cited Findings
- Marky: "A tool for self-publishing authors to manage their social media" [Stripe-verified] — [TrustMRR Marky](https://trustmrr.com/startup/marky)
  - MRR $22,204; 478 active subscriptions; all-time revenue $1,016,675.
  - $16,470 revenue in the last 30 days.
  - Founded July 2023, US. Founder has 1,899 followers on X.
- Postiz, "agentic social media scheduler": $413k 30-day revenue, $379k MRR [Stripe-verified] — [TrustMRR content-creation](https://trustmrr.com/category/content-creation)
- Podawaa (LinkedIn publishing): $62k MRR [Stripe-verified] — [TrustMRR content-creation](https://trustmrr.com/category/content-creation)
- Liinks (link-in-bio): $31,694 MRR from 5,537 active subscriptions; founded May 2020; founder has 12.5k X followers [Stripe-verified] — [TrustMRR Liinks](https://trustmrr.com/startup/liinks)
- TAM:
  - Musicians & singers: 170,400 [O*NET/BLS] — [O*NET](https://www.onetonline.org/link/summary/27-2042.00)
  - Shopify Arts & Entertainment 109,431 stores; Gifts & Special Events 60,028 [StoreLeads] — [StoreLeads](https://storeleads.app/reports/shopify)

### Inferences
**Beatability.** Horizontal schedulers (Postiz, Buffer and similar) ignore niche workflows such as:
- pre-save and release-date countdowns;
- tour-date and setlist posts;
- product-drop and market-day announcements.

Marky's success with authors suggests niche templates and asset generation win over general scheduling.

**Kill-rule check.** No evidence was found of a dominant niche tool for musicians' social posting. Smart-link tools (Feature.fm, Linkfire) are adjacent but different. This is unverified, so it is listed as a gap.

**MVP (4–6 weeks):**
- Connect Instagram, Facebook, TikTok and Threads accounts.
- Release or drop calendar, which auto-generates a 4–6 week post plan.
- Template library: static images and carousels, captions, hashtags.
- Scheduling.

**Expansion path:**
- Ad boosting.
- Fan email capture.
- Smart links.
- Analytics.
- Other niches using the same engine: podcasters, artists, Etsy makers.

**Channel.**
- Incumbents: the founder's personal brand on X (from TrustMRR profile data).
- For a newcomer: niche Facebook groups and subreddits, YouTube tutorials, affiliate partnerships with distributors and course creators.

**Score:** Rev 4, Beat 3, Copy 4, Exp 4, Chan 3 = **18/25**.

### Gaps
- Marky's exact feature set and pricing (the TrustMRR page summary was truncated).
- Ratings and revenue of musician-specific social tools.
- Need to confirm the spin avoids the excluded "AI video creation/viral-format" category: keep it to static posts and scheduling.

---

## Q6. Shortlist #5 — Shopify DTF gang-sheet builder plus transfer storefront app, for DTF and UV-DTF print shops selling transfers online. Score 18/25

### Takeaway
DTF gang-sheet builders are a young Shopify category (launched 2023+). No leader has many reviews: the top listings have only 15–45 reviews, at 4.4–5.0★.

This is a classic "be the best-rated app in a forming category" Shopify play. Revenue proof is weak (review counts only), but the channel is highly replicable, and the app is a natural wedge into Shortlist #1.

### Cited Findings
- Drip Apps' "Build a Gang Sheet": 4.4★ (45), launched Jul 17 2023, free to install with additional charges [Shopify App Store] — [Shopify](https://apps.shopify.com/build-a-gang-sheet)
- Other builders in the custom-file-upload category [Shopify App Store] — [Shopify category](https://apps.shopify.com/categories/selling-products-custom-products-custom-file-upload/all):
  - Kixxl "AI DTF Gang Sheet Builder": 4.7★ (35)
  - Antigro Gang Sheet Builder: 5.0★ (38)
  - Gangio DTF Gang Sheet Builder: 4.9★ (15)
- Generic upload apps with more reviews [Shopify App Store] — [Shopify category](https://apps.shopify.com/categories/selling-products-custom-products-custom-file-upload/all):
  - Upload-Lift: 4.9★ (178)
  - Uploadery: 4.6★ (182)
  - OPTIS Product Options: 4.9★ (2,383)
- NinjaPOD "DTF Print on Demand": 4.4★ (75) [Shopify App Store] — [POD category](https://apps.shopify.com/categories/finding-products-sourcing-options-print-on-demand-pod/all)
- 875,022 Shopify stores sell Apparel [StoreLeads] — [StoreLeads](https://storeleads.app/reports/shopify)

### Inferences
**Beatability.** No incumbent has the "many reviews at 4.6★+" profile that would trigger the kill rule.

**Copyability.** The core is a browser canvas: auto-nesting, DPI and transparency checks, sheet-size pricing. It is buildable in 4–8 weeks.

**Differentiators:**
- automatic artwork fixes (background removal, upscaling, a halftone warning);
- price-per-square-inch calculators;
- reorder of saved sheets;
- a production-ready file export (PNG/PDF at 300 DPI) delivered to the shop's RIP folder or email.

**Expansion path:**
- UV-DTF, stickers, sublimation and screen-print transfer sheets.
- Wholesale price tiers for repeat B2B buyers.
- Then upsell the shop OS (#1).

**Channel.** The Shopify App Store, plus DTF Facebook groups and YouTube.

**Score:** Rev 2, Beat 3, Copy 4, Exp 4, Chan 5 = **18/25**.

### Gaps
- Install counts and revenue for any gang-sheet app (not public).
- Pricing of the incumbents (individual listings not parsed beyond "free to install").

---

## Q7. Shortlist #6 — Wedding and event DJ planning portal plus booking CRM, expanding to live entertainers (wedding bands, MCs, string quartets, mobile bartenders). Score 17/25

### Takeaway
DJ business software splits three ways:
- a dated but cheap legacy CRM: DJEP, at $20–50/mo;
- an expensive modern music-planning portal: Vibo, at $149–179/mo;
- a modern multi-industry event CRM: Check Cherry, from $29/mo, with modest mobile ratings and feature requests.

A combined "Vibo-grade client music planning plus Check Cherry-grade booking" product at $39–59/mo is a plausible wedge. Check Cherry's breadth is the main risk.

### Cited Findings
**Vibo**
- $149/mo billed yearly, or $179 monthly; "Built for pro Wedding and Event DJs" [vendor pricing] — [Vibo](https://vibodj.com/pricing)

**DJ Event Planner (DJEP)**
- StandAlone $20/mo, Premium $35/mo, Premium Plus $50/mo [vendor pricing] — [DJEP pricing](https://www.djeventplanner.com/pricing.php)
- Site navigation still centres on Mobile DJ Forums, DJ Chat and "Most Requested Songs" charts going back to 2013 [vendor] — [DJEP](https://www.djeventplanner.com/)
- Companion iOS app "Most Requested Song Charts": 2.8★ (5), last updated 2019-01-15 [iOS] — [App Store](https://apps.apple.com/us/app/most-requested-song-charts/id1448422800)

**Check Cherry**
- From $29/mo billed annually (30 upcoming bookings); "160+ five-star reviews" [vendor pricing] — [Check Cherry pricing](https://www.checkcherry.com/pricing)
- Industries served include Photo Booth Owners, Wedding DJs, Mobile Bartenders and Photographers — [Check Cherry](https://www.checkcherry.com/)
- iOS: 4.8★ from 12 ratings [iOS] — [App Store](https://apps.apple.com/us/app/check-cherry/id1669623301)
  - 03/17/2023: "Please add push notifications."
  - 07/13/2024: "Would love for an update that allows notifications to alert when a new lead pops up"

**Others**
- DJ Planning Center iOS: 5.0★ (10) [iOS] — [iTunes API](https://itunes.apple.com/search?term=dj+event+planner&entity=software&country=us)
- GigSalad (entertainer marketplace) iOS: 2.5★ (43), last updated 2018-07-06 [iOS] — [App Store](https://apps.apple.com/us/app/gigsalad-hire-entertainers/id1227480456)
- Horizontal competitor HoneyBook [Latka est.; Capterra; iOS] — [Latka](https://getlatka.com/companies/honeybook), [Capterra](https://www.capterra.com/photography-studio-software/), [App Store](https://apps.apple.com/us/app/honeybook-small-business-crm/id1104772757):
  - Revenue about $74.2M (Oct 2024).
  - Capterra 4.7★ (695); iOS 4.8★ (16,360).

**TAM**
- DJs (except radio): 16,900; musicians & singers: 170,400 (2025) [O*NET/BLS] — [O*NET DJ](https://www.onetonline.org/link/summary/27-2091.00), [O*NET musicians](https://www.onetonline.org/link/summary/27-2042.00)

### Inferences
**Beatability.**
- There is a price gap between DJEP ($20–50, dated) and Vibo ($149–179).
- Check Cherry is modern and fairly priced but horizontal across event pros. Its music-planning depth is unverified.

**Kill-rule check.** Check Cherry comes closest to dominance. Its 160+ five-star reviews are vendor-stated, and its 12 iOS ratings are thin, so this passes with risk.

**MVP (6–8 weeks):**
- Inquiry form, quote and package builder, e-contract and deposit.
- Client portal with Spotify/Apple Music search for must-play and do-not-play lists, a timeline builder (grand entrance, first dance), and a guest request QR.
- Automated reminders.

**Expansion path:**
- Multi-op DJ companies (staff scheduling).
- Wedding bands (sub-musician payouts, setlists).
- MCs, uplighting and photo-booth add-ons, mobile bartenders.

**Channel.**
- Incumbents: DJEP uses community forums and SEO song charts; Check Cherry uses video content.
- For a newcomer: DJ Facebook groups, DJ Expo, YouTube, and a free "most requested wedding songs" SEO tool.

**Score:** Rev 3, Beat 3, Copy 4, Exp 3, Chan 4 = **17/25**.

### Gaps
- Check Cherry and Vibo revenue (no Latka profiles; 404).
- Check Cherry's Capterra rating.
- Share of DJs on DJEP versus Check Cherry versus HoneyBook.

---

## Q8. Shortlist #7 — Maker batch-production, COGS and inventory app (Craftybase alternative) for candle, soap, cosmetics and jewelry makers selling on Etsy, Shopify and at markets. Score 17/25

### Takeaway
Craftybase, the proven maker-inventory SaaS (about $660K est., 6 staff), now starts at $83–99/mo. It positions itself "for product businesses managing a team". Forecasting apps such as Prediko (4.9★) serve larger brands.

That leaves solo and hobby-to-pro makers underserved at the $15–35/mo price point. Beatability evidence is mostly price and positioning, not bad reviews.

### Cited Findings
- Craftybase revenue about $660K (Sep 2025), 6 employees [Latka est.] — [Latka](https://getlatka.com/companies/craftybase)
- Craftybase pricing [vendor pricing] — [Craftybase pricing](https://craftybase.com/pricing):
  - Indie: $83/mo billed annually ($990/yr) or $99 monthly; 1,000 order lines/mo, unlimited users.
  - Business: $166/mo billed annually, or $199 monthly.
  - Indie is described as "For product businesses managing a team and growing order volume".
- The `apps.shopify.com/craftybase` handle returned 404, so no Shopify listing was found under that handle.
- iOS search surfaced only small calculators, such as "Craft Price Calculator" at 4.3★ (146) [iOS] — [App Store](https://apps.apple.com/us/app/craft-price-calculator/id6446635931)
- Prediko inventory planning [Shopify App Store; Latka est.] — [Shopify](https://apps.shopify.com/prediko), [Latka](https://getlatka.com/companies/prediko):
  - 4.9★ (267), launched Aug 2023.
  - Revenue about $1.4M (Oct 2024); $5.5M raised.
  - Reviews come from brands such as Victoria Beckham (Nov 2026), which signals an upmarket focus.
- Shopify retired Stocky, its free inventory app, after Aug 31 2026 and points merchants to native inventory management — [Shopify Help](https://help.shopify.com/en/manual/sell-in-person/shopify-pos/inventory-management/stocky)
- TAM, Shopify stores by category [StoreLeads] — [StoreLeads](https://storeleads.app/reports/shopify):
  - Beauty & Fitness 350,637
  - Home & Garden 409,956
  - Gifts & Special Events 60,028

### Inferences
**Proposed spin.** A $15–35/mo maker app with:
- recipes and bill of materials (BOM), with ingredient and material costs;
- batch production that converts raw stock into finished units;
- COGS per unit and margin per channel;
- Etsy, Shopify and Square stock sync;
- low-stock reorder lists;
- printable labels and ingredient lists.

**Expansion path:**
- Lot and batch traceability and cosmetic-safety record-keeping for soap and cosmetics makers (regulatory angle, unverified this session).
- Wholesale line sheets.
- Craft-fair inventory packing lists (pairs with #3).
- Adjacent niches: coffee roasters, hot sauce and cottage food, small apparel makers.

**Channel.**
- Craftybase: content SEO (not verified this session).
- For a newcomer: Etsy seller forums, maker YouTube, Shopify App Store listing.

**Score:** Rev 3, Beat 3, Copy 4, Exp 4, Chan 3 = **17/25**.

### Gaps
- Craftybase ratings (Capterra/G2 not fetched or blocked).
- Whether a cheaper Craftybase tier exists outside the parsed text.
- Etsy active-seller counts.
- MoCRA small-business obligations for soap and cosmetics makers (not fetched).

---

## Q9. Shortlist #8 — Product-seeding and UGC usage-rights manager for small Shopify brands (under ~$1M GMV). Score 17/25

### Takeaway
Shopify's free Collabs app covers the basics but is rated only 4.2★, and reviews in October 2026 complain about missing automations and no API. Dedicated tools are either priced for larger brands (Social Snowball from $249/mo) or built for affiliate tracking rather than gifting and rights management.

Stack Influence shows brands pay heavily for micro-creator seeding ($872k Stripe-verified 30-day revenue, mostly non-recurring). A self-serve, cheap "gift → content → usage-rights expiry → whitelisting" tool is beatable, but the space is crowded.

### Cited Findings
- Shopify Collabs: 4.2★ (449), free [Shopify App Store] — [Shopify](https://apps.shopify.com/collabs)
  - Oct 22 2026: "I wish there were more automations and the ability to manually add collabs"
  - Oct 5 2026: "they have no such API access for Collabs. It's the main drawback."
- Affiliate-category apps [Shopify App Store] — [Shopify affiliate category](https://apps.shopify.com/categories/marketing-and-conversion-advertising-affiliate-programs/all):
  - Social Snowball: "From $249/month", 4.6★ (211)
  - Modash: 5.0★ (18)
  - impact.com: 4.4★ (203)
  - UpPromote: 4.9★ (3,931)
  - Awin: 1.9★ (33)
- Stack Influence, "Micro Creator marketing platform for eComm brands": $872k revenue in the last 30 days, $28k MRR [Stripe-verified] — [TrustMRR ecommerce](https://trustmrr.com/category/ecommerce)
- TAM: 1,253,193 US Shopify stores [StoreLeads] — [StoreLeads](https://storeleads.app/reports/shopify)

### Inferences
**Beatability.**
- The free platform tool is mediocre (4.2★, no API).
- The premium tools start at $249/mo.
- None of the fetched listings advertises usage-rights expiry tracking. This is an inference from the listings, not verified.

**Kill-rule check.** Collabs is free, but it is not good enough to trigger the kill rule.

**MVP (6–8 weeks):**
- Creator application page.
- Product gifting via draft orders.
- Content-due reminders.
- Content capture (Instagram/TikTok tags plus upload).
- Usage-rights terms with expiry alerts.
- A simple creator payout ledger.

**Expansion path:**
- Paid whitelisting/Spark-ads code collection.
- A creator-side portfolio and rate card (micro-influencers).
- A marketplace of vetted micro-creators.

**Channel.** Shopify App Store, plus DTC operator newsletters and podcasts.

**Score:** Rev 4, Beat 3, Copy 3, Exp 3, Chan 4 = **17/25**.

### Gaps
- Ratings and prices of other seeding/UGC tools (Archive, Superfiliate, GRIN, Aspire) were not fetched.
- Creator-side tools (Beacons, Passionfroot) returned 403 or 404.

---

## Q10. Shortlist #9 (borderline) — Small-volume "picture day" photography for solo photographers: dance studios, youth leagues, daycares, pet and Santa minis. Score 14/25

### Takeaway
The volume-photography platforms are modern and cheap to start:
- GotPhoto: free plus 12% service fee, or $9.90/mo plus 9%. Built for 2,500–100,000+ subjects a year.
- PhotoDay: free signup, takes a cut of each order.

There is a positioning gap for very small operators, but no strong evidence of a poorly rated incumbent. Keep this on a watchlist rather than prioritising it.

### Cited Findings
- GotPhoto: "Designed for studios photographing 2,500–100,000+ subjects per year". Free plan $0/mo + 12% service fee; Growth $9.90/mo + 9% [vendor pricing] — [GotPhoto](https://www.gotphoto.com/en-us/pricing)
- GotPhoto's US iOS app was released 2026-04-30 and has no ratings yet [iOS] — [iTunes API](https://itunes.apple.com/search?term=gotphoto&entity=software&country=us)
- PhotoDay: "100% Free to Sign Up"; lab costs come out of each order. Custom pricing for studios "processing $500K+ in annual PhotoDay sales" [vendor pricing] — [PhotoDay](https://www.photoday.com/pricing)
- PhotoDay Capture iOS: 4.5★ (8) [iOS] — [App Store](https://apps.apple.com/us/app/photoday-capture/id1370434730)
- Pixieset: free plan with 15% store commission; Basic $8/mo billed annually or $10 monthly [vendor pricing] — [Pixieset](https://pixieset.com/pricing/)
- Pixieset revenue about $19M (Jul 2025), 173 employees [Latka est.] — [Latka](https://getlatka.com/companies/pixieset)
- Photographers: 145,000 (2025) [O*NET/BLS] — [O*NET](https://www.onetonline.org/link/summary/27-4021.00)

### Inferences
**Possible spin.**
- QR or face-match tagging on a phone.
- Prepaid packages.
- Parent self-serve galleries with lab dropship.
- Flat $15/mo with no commission.

**Weaknesses.** Beatability is weak and incumbents' fees are low.

**Score:** Rev 3, Beat 2, Copy 3, Exp 3, Chan 3 = **14/25**.

### Gaps
- GotPhoto and PhotoDay revenue.
- Ratings of their main web products.
- Count of solo volume photographers.

---

## Q11. Kill list and holds: which candidates were evaluated and rejected, and why?

### Takeaway
At least 20 further candidates were evaluated and killed or held. Most fail the kill rule in one of two ways:
- a modern 4.6★+ product with many reviews dominates: Bakesy, Pixieset, Stan, UpPromote, Printful, Artwork Archive and others;
- or the platform now bundles the feature: Shopify B2B on Basic, Stocky replaced by native inventory, Kickstarter's own Pledge Manager.

Two are held for lack of evidence rather than killed.

### Cited Findings
**K1. Custom cake and cookie home-baker order intake: killed (dominated)**
- Bakesy: iOS 4.9★ from 7,292 ratings; $9.99/$17.99 in-app purchases [iOS] — [App Store](https://apps.apple.com/us/app/bakesy-home-bakery-biz-app/id1515139393)
- Hotplate, for food drops [vendor; Latka est.; iOS] — [Hotplate](https://www.hotplate.com/), [Latka](https://getlatka.com/companies/hotplate), [App Store](https://apps.apple.com/us/app/hotplate-portal-sell-food/id6762679640):
  - Claims "Join 5k+ chefs earning $100M"; charges a transaction fee per order.
  - Revenue about $2.7M (Dec 2024).
  - Portal app: 4.9★ (39).
- Castiron, the former maker/baker commerce platform: castiron.me now serves an "Online Casinos Canada 2026" page, which suggests the domain lapsed or the service is defunct (inference) — [castiron.me](https://www.castiron.me/)
- Capterra's bakery category is dominated by POS (Toast 4.1★ (555); Square 4.6★ (3,045)), not custom-order tools — [Capterra](https://www.capterra.com/bakery-software/)
- Bakesy's model is reused in #1 and #7.

**K2. Generic photographer galleries/CRM (Pixieset, ShootProof, Pic-Time, Sprout, 17hats, Táve clones): killed (dominated)**
- iOS ratings [iOS] — [Pixieset](https://apps.apple.com/us/app/pixieset-studio-manager/id6469647424), [Pic-Time](https://apps.apple.com/us/app/pic-time/id1434304532), [HoneyBook](https://apps.apple.com/us/app/honeybook-small-business-crm/id1104772757), [Dubsado](https://apps.apple.com/us/app/dubsado/id6447585549), [17hats](https://apps.apple.com/us/app/17hats/id1069498016):
  - Pixieset Studio Manager: 4.9★ (2,429)
  - Pic-Time: 4.7★ (2,172)
  - HoneyBook: 4.8★ (16,360)
  - Dubsado: 4.8★ (583)
  - 17hats: 3.1★ (35)
- Capterra photography-studio category: HoneyBook 4.7★ (695), Iris Works 4.6★ (218), 17hats 4.4★ (136), Studio Ninja 4.4★ (68) [Capterra] — [Capterra](https://www.capterra.com/photography-studio-software/)
- Pricing: Pixieset free/$8 per month [vendor] — [Pixieset](https://pixieset.com/pricing/)
- Revenue [Latka] — [Latka 17hats](https://getlatka.com/companies/17hats), [Latka Dubsado](https://getlatka.com/companies/dubsado):
  - 17hats: about $6.5M est. (Dec 2023, stale)
  - Dubsado: about $2.5M est. (Jul 2025)

**K3. Real-estate photography media delivery (Aryeo clone): killed (platform-tied)**
- Aryeo says it "is the only platform that delivers media for Zillow Showcase listings" (Bing snippet of aryeo.com) — [Aryeo](https://www.aryeo.com/)

**K4. Photo-booth operator CRM: killed**
- Check Cherry is built for this industry: from $29/mo, "160+ five-star reviews" — [Check Cherry](https://www.checkcherry.com/pricing)

**K5. Podcast hosting/analytics: killed**
- Capterra podcast hosting [Capterra] — [Capterra](https://www.capterra.com/podcast-hosting-software/):
  - Buzzsprout: 4.8★ (746)
  - Transistor: 4.9★ (15)
  - Ausha: 4.8★ (78)
- Revenue [Latka est.] — [Latka Buzzsprout](https://getlatka.com/companies/buzzsprout), [Latka Transistor](https://getlatka.com/companies/transistor):
  - Buzzsprout: about $5.6M (Oct 2024)
  - Transistor: about $3M (Oct 2022, stale)

**K6. Digital-product, link-in-bio and creator storefronts (Gumroad/Payhip/Podia clones): killed (dominated)**
- Stan: $3.6M MRR [Stripe-verified]; iOS 4.9★ (13,479) — [TrustMRR content-creation](https://trustmrr.com/category/content-creation), [App Store](https://apps.apple.com/us/app/stan-link-in-bio-for-creators/id6478343472)
- Gumroad: $7.1M 30-day revenue [Stripe-verified], despite 10% + $0.50 fees — [TrustMRR ecommerce](https://trustmrr.com/category/ecommerce), [Gumroad](https://gumroad.com/pricing)
- Shopify digital-products apps [Shopify App Store] — [Shopify category](https://apps.shopify.com/categories/selling-products-digital-goods-and-services-digital-products/all):
  - Shopify Digital Products: free, 4.8★ (1,440)
  - Filemonk: 4.9★ (508)
  - Sky Pilot: 4.9★ (441)
- Podia: about $811K est. (Oct 2024) — [Latka](https://getlatka.com/companies/podia)

**K7. Membership/community (Circle/Skool/Mighty clones): killed**
- Revenue [Latka est.] — [Latka Skool](https://getlatka.com/companies/skool), [Latka Mighty](https://getlatka.com/companies/mighty-networks), [Latka Kajabi](https://getlatka.com/companies/kajabi):
  - Skool: about $26.6M (Sep 2025)
  - Mighty Networks: about $8.6M (Oct 2024), $66M raised
  - Kajabi: about $75M (Jun 2024)
- On Shopify, Tevello Courses & Communities has 5.0★ (760) — [Shopify category](https://apps.shopify.com/categories/selling-products-digital-goods-and-services-digital-products/all)

**K8. Affiliate/referral programs (Rewardful/Tolt/FirstPromoter clones): killed**
- Shopify affiliate apps [Shopify App Store] — [Shopify category](https://apps.shopify.com/categories/marketing-and-conversion-advertising-affiliate-programs/all):
  - UpPromote: 4.9★ (3,931)
  - ReferralCandy: 4.9★ (1,480)
  - ReferrLy: 5.0★ (1,133)
  - GoAffPro: 4.6★ (951)
  - Shopify Collabs: free
- Rewardful: $2.8M (Aug 2024) "according to the CEO", 8 employees [CEO-claimed] — [Latka](https://getlatka.com/companies/rewardful)

**K9. Pre-orders and subscriptions: killed**
- PreProduct: 4.9★ (108) [Shopify App Store] — [Shopify](https://apps.shopify.com/preproduct)
  - Oct 31 2026: "The best pre-order software on the market."
- Recharge: $100M (Nov 2025) "according to X" [reported] — [Latka](https://getlatka.com/companies/recharge)

**K10. Product personalizers and print-on-demand: killed**
- Personalizers and options apps [Shopify App Store] — [POD category](https://apps.shopify.com/categories/finding-products-sourcing-options-print-on-demand-pod/all), [variants category](https://apps.shopify.com/categories/selling-products-custom-products-product-variants/all):
  - Customily: 4.9★ (282)
  - Teeinblue: 4.9★ (393)
  - Globo Product Options: 4.9★ (5,267)
- Print-on-demand apps [Shopify App Store] — same POD category link:
  - Printful: 4.8★ (4,018)
  - Printify: 4.7★ (4,358)
  - Gelato: 4.8★ (1,053)
- Customily revenue about $3.5M est. — [Latka](https://getlatka.com/companies/customily)

**K11. Wholesale/B2B portals and Faire alternatives: killed (platform bundles, saturated)**
- "Shopify B2B is available on the Basic, Grow, Advanced, and Shopify Plus plans" — [Shopify Help](https://help.shopify.com/en/manual/b2b)
- Wholesale apps [Shopify App Store] — [Shopify wholesale category](https://apps.shopify.com/categories/finding-products-sourcing-options-wholesale/all):
  - BSS B2B: 4.9★ (1,204)
  - Sami B2B: 4.9★ (995)
  - SparkLayer: 4.9★ (388)
- Faire Sell Wholesale: 4.6★ (473), with 7% one-star. Oct 11 2026: "Creo que un 25% es mucho para primeras compras" ("I think 25% is a lot for first purchases") — [Shopify](https://apps.shopify.com/faire-sell-wholesale/reviews?sort_by=newest)
- Brandboom: $50/$100 per user per month; Business tier has a $500/mo minimum [vendor] — [Brandboom](https://www.brandboom.com/pricing)
- Brandboom revenue about $4.4M est. — [Latka](https://getlatka.com/companies/brandboom)
- Faire itself is a marketplace with about $117.1M revenue est. (Oct 2024). A marketplace is not copyable by a solo founder — [Latka](https://getlatka.com/companies/faire)

**K12. Inventory forecasting and post-Stocky POS inventory: killed (platform plus a strong incumbent)**
- Stocky "will no longer be available after August 31st, 2026"; Shopify directs merchants to native inventory management — [Shopify Help](https://help.shopify.com/en/manual/sell-in-person/shopify-pos/inventory-management/stocky)
- Stocky's final rating: 3.0★ (210), with 28% one-star [Shopify App Store] — [Shopify](https://apps.shopify.com/stocky/reviews?sort_by=newest)
  - Dec 16 2025: "…pushing you to upgrade to Shopify POS Pro at $89 per month"
- Alternatives [Shopify App Store; Latka est.] — [Shopify Prediko](https://apps.shopify.com/prediko), [Shopify IP](https://apps.shopify.com/inventory-planner), [Latka](https://getlatka.com/companies/inventory-planner):
  - Prediko: 4.9★ (267)
  - Inventory Planner by Sage: 4.3★ (154), about $2.9M est.

**K13. Crowdfunding pledge managers and pre-order stores: killed (platform bundles)**
- Kickstarter now offers "The Kickstarter Pledge Manager… Built directly into Kickstarter" — [Kickstarter](https://start.kickstarter.com/pledge-manager)
- Gamefound iOS: 4.8★ (314) — [App Store](https://apps.apple.com/us/app/gamefound/id6504344271)
- BackerKit: about $6.5M est. (Oct 2024) — [Latka](https://getlatka.com/companies/backerkit)
- PledgeManager charges a flat per-backer fee plus "5% of in-tool sales" — [PledgeManager](https://www.pledgemanager.com/pricing)

**K14. Reseller crosslisting (Vendoo/List Perfectly clones): killed (crowded, well-rated)**
- Vendoo: iOS 4.5★ (2,897); $14.99/mo Starter, $29.99/mo Growth — [App Store](https://apps.apple.com/us/app/vendoo-a-sellers-best-friend/id1612168777), [Vendoo](https://www.vendoo.co/pricing)
- List Perfectly: $29/$49/$69/$99+ per month — [List Perfectly](https://listperfectly.com/pricing/)
- AI-listing newcomers, e.g. SellOut: 4.7★ (156) — [iTunes API](https://itunes.apple.com/search?term=list+perfectly&entity=software&country=us)

**K15. Artist and gallery inventory (Artwork Archive/Artlogic clones): killed (dominated)**
- Capterra art-gallery category [Capterra] — [Capterra](https://www.capterra.com/art-gallery-software/):
  - Artwork Archive: 4.9★ (110)
  - ArtCloud: 4.8★ (72)
  - Artlogic: 4.7★ (45)

**K16. Band setlist/management (BandHelper clone): killed (low price ceiling)**
- BandHelper: iOS 4.3★ (113), solo developer since 2013 — [App Store](https://apps.apple.com/us/app/bandhelper/id552012927)
- In-app purchase prices run from $3/mo (Basic, solo) to $14/mo (Pro, 6–20 users)

**K17. Booking-agency software (Gigwell clone): killed (enterprise sales; free-tool moat)**
- Gigwell launched free booking tools for artists, agents and venues — [Gigwell free tools](https://freetools.gigwell.com/)
- A Gigwell post cites "ten years and nearly $3 billion in global…" (snippet truncated) — [Gigwell Advance](https://advance.gigwell.com/posts/gigwell-launches-artist-essentials)
- Latka data is stale (2022 profile) — [Latka](https://getlatka.com/companies/gigwell)

**K18. Standalone ARC/review-team manager for authors: killed as standalone, folded into #2**
- Booksprout: iOS 2.5★ (19) — beatable — [App Store](https://apps.apple.com/us/app/booksprout/id1590873280)
- But cheap incumbents and bundled delivery cap revenue:
  - BookSirens: $100/yr — [BookSirens](https://booksirens.com/pricing)
  - BookFunnel ARC delivery is included in its plans — [BookFunnel](https://bookfunnel.com/pricing/)

**H1. Indie touring-merch POS and settlement: held (evidence gap)**
- atVenu is enterprise-focused: "125K" events a year, "$2B+" processed annually, "28K" artists, teams and venues [vendor-claimed] — [atVenu](https://www.atvenu.com/)
- atVenu revenue: about $12.2M (Sep 2025) [Growjo est. via Latka] — [Latka](https://getlatka.com/companies/atvenu)
- Indie-band alternative ratings (e.g. Merch Cat) could not be retrieved (iTunes rate limit). Square's free POS partly bundles the feature.

**H2. Creator-side brand-deal CRM and media kits for micro-influencers: held (evidence gap, crowded)**
- Stan: 4.9★ (13,479) — [App Store](https://apps.apple.com/us/app/stan-link-in-bio-for-creators/id6478343472)
- Beacons and Passionfroot data could not be retrieved (403/404).

### Inferences
- The kill rule bites hardest in mature Shopify App Store categories. Wholesale pricing, options/personalizers, affiliate, digital downloads, POD and pre-orders all have multiple 4.9★ apps with hundreds to thousands of reviews.
- Remaining Shopify opportunities are in young or neglected sub-categories: book-printing connectors, DTF gang sheets, and seeding/rights tools.
- Off-Shopify, the clearest beatable incumbents are roll-ups or legacy products in operator-heavy niches:
  - Printavo under Taivo;
  - ZAPP and CaFÉ from 2004;
  - DJEP;
  - Eventeny's app at 2.8★.

### Gaps
- Several holds need follow-up: Merch Cat and other indie merch apps, Beacons, Passionfroot, Collabstr, plus tattoo-artist booking and florist proposal tools (Curate), which were not reached because of iTunes rate limits.
- Kickstarter's pledge-manager fee level was not fetched (Kickstarter returned 429).

---

## Q12. How do the shortlisted ideas rank, and what links them?

### Takeaway
1. Made-to-order decorator shop OS — 20/25
2. Author direct-sales Shopify app — 19/25
3. Art-fair and makers-market applications — 19/25
4. Marky-model niche social manager — 18/25
5. DTF gang-sheet Shopify app — 18/25
6. DJ/entertainer planning CRM — 17/25
7. Maker COGS/batch inventory — 17/25
8. Product-seeding/UGC-rights app — 17/25
9. Small-volume photography — 14/25 (borderline)

Two clusters share code and channels:
- the "made-to-order maker" stack: #1, #5 and #7, with #3 as a distribution channel to makers;
- the "author" stack: #2 plus the folded-in ARC module.

### Cited Findings
- Bakesy's 4.9★ from 7,292 ratings at $9.99–$17.99/mo shows mobile-first made-to-order tooling sells to home-based operators — [App Store](https://apps.apple.com/us/app/bakesy-home-bakery-biz-app/id1515139393)
- Shortlist #1 anchor: Printavo's 1.8★ iOS app, and Taivo's 11,000+ customers across five products — [App Store](https://apps.apple.com/us/app/printavo/id1191027240), [Taivo](https://www.inktavo.com/)
- Shortlist #2 anchor: Lulu Direct 3.9★ (21% one-star) and Bookvault 1.8★ on Shopify — [Lulu](https://apps.shopify.com/lulu-direct), [Bookvault](https://apps.shopify.com/bookvault)
- Shortlist #3 anchor: CaFÉ per-call and per-application pricing, Creative West $23.2M revenue, Eventeny 2.8★ iOS and $240/mo + 3% — [CaFÉ](https://www.callforentry.org/how-it-works/pricing/), [ProPublica](https://projects.propublica.org/nonprofits/search?q=%22Creative+West%22), [Eventeny](https://www.eventeny.com/pricing/)
- Shortlist #4 anchor: Marky's Stripe-verified $22,204 MRR — [TrustMRR](https://trustmrr.com/startup/marky)

### Inferences

| # | Idea | Rev | Beat | Copy | Exp | Chan | Total | Incumbent channel |
|---|---|---|---|---|---|---|---|---|
| 1 | Decorator shop OS | 3 | 4 | 4 | 5 | 4 | 20 | Roll-up cross-sell (Taivo); paid social (Bakesy model) |
| 2 | Author direct-sales Shopify app | 3 | 4 | 4 | 4 | 4 | 19 | Shopify App Store; BookFunnel promos/swaps network |
| 3 | Art-fair/makers-market apps | 4 | 4 | 4 | 4 | 3 | 19 | Two-sided artist network (ZAPP/CaFÉ); organizer sales |
| 4 | Marky-model niche social manager | 4 | 3 | 4 | 4 | 3 | 18 | Founder brand on X; niche communities |
| 5 | DTF gang-sheet Shopify app | 2 | 3 | 4 | 4 | 5 | 18 | Shopify App Store |
| 6 | DJ planning + booking CRM | 3 | 3 | 4 | 3 | 4 | 17 | DJ forums/SEO charts (DJEP); video content (Check Cherry) |
| 7 | Maker COGS/batch inventory | 3 | 3 | 4 | 4 | 3 | 17 | Content/SEO (assumed); Etsy communities |
| 8 | Product seeding/UGC rights | 4 | 3 | 3 | 3 | 4 | 17 | Shopify App Store; DTC newsletters |
| 9 | Small-volume photography | 3 | 2 | 3 | 3 | 3 | 14 | Photographer groups; lab partnerships |

- Suggested sequencing for a solo founder:
  - Start with #5, which is the fastest to ship and rides the Shopify App Store, then expand into #1 (land and expand).
  - Alternatively start with #2, a clear bad-review wedge in a niche with a strong willingness-to-pay signal.
  - #3 has the highest ceiling but needs organizer sales and has to overcome a network-effect moat.

### Gaps
- Install counts or MRR for the Shopify apps scored on review counts alone (#5, #8).
- Current prices for Printavo and ZAPP-for-Events, which would firm up the beatability scores for #1 and #3.
