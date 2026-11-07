# US Home & Field-Service Trades: Clone-and-Improve Vertical SaaS Opportunities (as of 2026-11-07)

Provenance legend used on every figure:
- **[Capterra 2026-11-07]**: live Capterra category or review page fetched 2026-11-07. Format is rating (review count); CS = customer-service sub-score; VfM = value-for-money sub-score. Category rank order includes paid "sponsored" placements, so treat rank as advertising, not quality.
- **[iOS 2026-11-07]**: US App Store rating (rating count) and last-update date from the Apple iTunes Search API, fetched 2026-11-07.
- **[Latka est.]**: GetLatka revenue figure. These are third-party estimates unless Latka marks them as founder-reported. Two look templated or wrong (see Overview).
- **[Press]**: press release or trade press. **[Vendor]**: vendor's own site. **[3rd-party review site]**: affiliate or roundup blogs, lower reliability. **[IBISWorld snippet]**: business count from an IBISWorld public page. These include nonemployer businesses unless stated.

---

## Overview: method, data caveats, and ranked scoreboard

### Takeaway
Under the "beatability, not absence" rule, the strongest clone targets are niches where a PE- or roll-up-owned incumbent has visibly decayed. The clearest cases:
- **Lawn and tree-shrub chemical-program software**, replacing RealGreen and Service Autopilot.
- **Commercial janitorial operations**, against Swept, WinTeam and Janitorial Manager.
- **Short-term-rental turnover-cleaning companies**, against Breezeway and Turno.

These are followed by arborist, snow and ice, small fire-inspection shops, roll-off dumpster, and painting estimating. Pool service, home inspection, mobile pet grooming, mobile detailing, residential maid, roofing measurement and small-shop pest control fail the kill rule: a modern product rated about 4.6+ with many reviews already dominates each one.

### Cited Findings
- **Horizontal reference products are well rated, so a niche spin must beat them on workflow, not on UX alone.**
  - Jobber: 4.6 (1,490) [Capterra 2026-11-07]; iOS 4.81 (21,533) [iOS 2026-11-07].
  - Housecall Pro: 4.7 (2,749) [Capterra]; iOS 4.65 (31,620) [iOS].
  - Workiz: 4.4 (218) [Capterra]; iOS 4.57 (2,201) [iOS].
  - Sources: [Capterra lawn-care category](https://www.capterra.com/lawn-care-software/), [Capterra handyman category](https://www.capterra.com/handyman-software/), [iTunes API: Jobber](https://itunes.apple.com/search?term=Jobber&entity=software&country=us), [iTunes API: Workiz](https://itunes.apple.com/search?term=Workiz&entity=software&country=us).
- **Horizontal FSM revenue proves the overall category.**
  - Jobber: $100M revenue in 2022, up from $50M in 2021; $183.8M raised [Latka]. [Latka Jobber](https://getlatka.com/companies/jobber)
  - Housecall Pro: $37.2M revenue in 2021; $175M raised; 20K customers [Latka]. [Latka Housecall Pro](https://getlatka.com/companies/housecall-pro)
  - Workiz: $29.8M in 2024, up from $13.7M in 2023; $60.3M raised [Latka est.]. [Latka Workiz](https://getlatka.com/companies/workiz)
  - Kickserv: $2.2M revenue in 2022; 1.4K customers [Latka]. [Latka Kickserv](https://getlatka.com/companies/kickserv)
- **Two Latka figures look templated and should not be relied on.**
  - GorillaDesk "2025 estimated revenue: $880K, 8 employees" [Latka est.] is identical to BookingKoala's "$880K, 8 employees" [Latka est.]. [Latka GorillaDesk](https://getlatka.com/companies/gorilladesk); [Latka BookingKoala](https://getlatka.com/companies/bookingkoala)
  - ServiceCore is listed with "$3.4M 2022 revenue" but "$548M raised across 2 rounds" [Latka]. The raise figure is implausible for a $3.4M-revenue company. [Latka ServiceCore](https://getlatka.com/companies/servicecore)
- **Census data was not retrieved.** The Census County Business Patterns API now redirects keyless requests to `missing_key.html` (checked 2026-11-07), so NAICS counts below come from IBISWorld public snippets. [Census API](https://api.census.gov/data/2022/cbp?get=ESTAB&for=us:*&NAICS2017=561710)
- **US business counts, all [IBISWorld snippet]:**
  - Landscaping services: 692,777 (2025). [IBISWorld](https://img3.ibisworld.com/united-states/number-of-businesses/landscaping-services/1497)
  - Janitorial services: 1,232,252 (2025). [IBISWorld](https://img3.ibisworld.com/united-states/number-of-businesses/janitorial-services/1496)
  - Pest control: 33,197 (2025). [IBISWorld](https://img3.ibisworld.com/united-states/number-of-businesses/pest-control/1495)
  - Carpet cleaning: 40,945 (2025, +1.8%). [IBISWorld](https://img3.ibisworld.com/united-states/number-of-businesses/carpet-cleaning/1498)
  - Tree trimming: 175,035 (2025). A separate IBISWorld page shows 19,929 for 2026; these conflict by about 9x, probably a different scope. [IBISWorld](https://script.ibisworld.com/united-states/number-of-businesses/tree-trimming-services/6064)
  - Snowplowing: 111,608 (2025). [IBISWorld](https://script.ibisworld.com/united-states/number-of-businesses/snowplowing-services/5400)
  - House painting & decorating contractors: 223,209 (2025). [IBISWorld](https://script.ibisworld.com/united-states/number-of-businesses/house-painting-decorating-contractors/5738)

### Inferences
**Ranked scoreboard.** Each dimension is scored 1–5 for revenue proof (Rev), beatability (Beat), copyability (Copy), expansion (Exp) and channel replicability (Chan). Detailed evidence follows in each candidate section.

| # | Candidate (sub-niche spin) | Rev | Beat | Copy | Exp | Chan | Total /25 |
|---|---|---|---|---|---|---|---|
| 1 | Lawn and tree-shrub "chemical program" ops (RealGreen / Service Autopilot refugees) | 5 | 5 | 4 | 5 | 4 | **23** |
| 2 | Commercial janitorial ops: bid, QA inspection, geofenced site timekeeping | 4 | 4 | 5 | 5 | 4 | **22** |
| 3 | STR turnover-cleaning *company* ops (cleaner-side, not host-side) | 4 | 4 | 5 | 4 | 4 | **21** |
| 4 | Tree care / arborist estimating, crew and PHC | 4 | 4 | 4 | 4 | 4 | **20** |
| 5 | Commercial snow and ice: weather-triggered dispatch plus slip-and-fall proof | 3 | 4 | 5 | 4 | 4 | **20** |
| 6 | Fire and life-safety inspection for 1–15-tech extinguisher, hood and backflow shops | 5 | 3 | 4 | 4 | 4 | **20** |
| 7 | Roll-off dumpster rental plus junk removal | 4 | 3 | 5 | 4 | 4 | **20** |
| 8 | Painting contractor estimating and sales | 3 | 4 | 5 | 4 | 4 | **20** |
| 9 | Pest control mid-market (5–40 trucks), with a wildlife-control wedge | 5 | 3 | 3 | 4 | 3 | **18** |
| 10 | Septic and grease-trap pumping | 3 | 4 | 4 | 3 | 4 | **18** |
| 11 | Carpet, upholstery and tile cleaning | 2 | 3 | 5 | 4 | 3 | **17** |

**Suite logic.** Candidates 1, 4 and 5 share customers: the same green-industry firms do fertilization, tree PHC and winter snow. A founder could start in one and expand into a green-industry suite. Candidates 2, 3 and 11 form a cleaning suite. Candidates 7 and 10 share hauling and disposal-ticket workflows.

**Recurring monetization add-ons across all candidates:**
- embedded payments, which incumbents already push hard (see the Service Autopilot processor lock-in quote);
- prepay and autopay;
- customer portal;
- review and referral marketing;
- consumer financing for larger jobs (painting, tree removal);
- payroll for hourly crews (janitorial, cleaning).

### Gaps
- No Stripe-verified (TrustMRR) revenue was found for any trade-specific product this round. TrustMRR and StarterStory were not searched, because the tool budget went to Capterra, iOS and press checks.
- NAICS establishment counts from Census CBP or the Nonemployer Statistics were not retrieved because the API requires a key. Septic (562991), solid-waste collection (562111) and fire-extinguisher service lack any count here.
- G2 and Software Advice ratings were not pulled. Capterra plus iOS is the rating basis throughout.

---

## Candidate 1: Lawn and tree-shrub chemical-program software (fertilization, weed control, mosquito), aimed at RealGreen and Service Autopilot refugees

### Takeaway
This is the best-evidenced target. The two legacy specialists for "fert and squirt" lawn programs were both absorbed by roll-ups: RealGreen by WorkWave in 2021, Service Autopilot by Xplor around 2022. Both now show poor ratings, especially for their mobile apps, plus complaints about price, licensing and payment lock-in. Generic mowing tools (Jobber, Crew Control, LawnPro) are well rated but do not model multi-round chemical programs. **Score 23/25.**

### Cited Findings
**Original products and revenue proof**
- **RealGreen.** Real Green Systems, with 35+ years serving lawn care, landscaping, arbor care and pest control, was acquired by WorkWave in a deal announced in June 2021 and completed June 29, 2021 [Press]. Serent-backed holders rolled equity alongside EQT and TA Associates. [BusinessWire](https://www.businesswire.com/news/home/20210622005744/en/Serent-Announces-Acquisition-of-Portfolio-Company-Real-Green-Systems-by-WorkWave-and-Serents-Rollover-Investment-in-the-Combined-Company); [RealGreen newsroom](https://www.realgreen.com/newsroom/workwave-completes-acquisition-of-real-green-systems)
- **FieldRoutes** (pest and lawn). ServiceTitan announced a definitive agreement to acquire it in January 2022 [Press]. [ServiceTitan press](https://www.servicetitan.com/press/fieldroutes-acquisition) Latka estimates FieldRoutes 2025 revenue at $16.4M with 149 employees [Latka est.]. [Latka](https://getlatka.com/companies/fieldroutes)
- **Service Autopilot.** Review sites date Xplor's acquisition to 2022, while an Xplor Pay page describes buying a "controlling interest" [3rd-party / Vendor]. [Review site](https://mowbosshq.pages.dev/guides/service-autopilot-review); [Xplor Pay](https://xplorpay.com/?p=2655)
- **Demand for satellite measuring.** In February 2024, Service Autopilot partnered with Deep Lawn for satellite-imagery lawn measurement and instant quotes [Press]. [Lawn & Landscape](https://lawnandlandscape.com/news/service-autopilot-by-xplor-unites-with-deep-lawn)
- **LMN** (landscape): 2025 revenue estimated at $11.6M, 105 employees [Latka est.]. [Latka LMN](https://getlatka.com/companies/lmn)

**Incumbent ratings and pricing**
- RealGreen: 3.9 (149), CS 3.7, VfM 3.6, ease of use 3.8 [Capterra 2026-11-07; review page "last updated October 19th, 2026"]. [Capterra RealGreen reviews](https://www.capterra.com/p/78106/Service-Assistant/reviews/)
- Service Autopilot: 4.1 (139), VfM 3.8 [Capterra]. [Capterra](https://www.capterra.com/p/122075/Service-Autopilot/reviews/)
- CLIPitc: 3.8 (106), CS 3.7, VfM 3.7 [Capterra]. [Capterra](https://www.capterra.com/p/105509/Clip-Lawn-Maintenance-Software/reviews/)
- Competing generalists are well rated: Crew Control 4.8 (100), 95% recommend; LawnPro 4.6 (188); GorillaDesk 4.8 (278) [Capterra]. [Capterra lawn-care category](https://www.capterra.com/lawn-care-software/)

**Mobile apps (the techs' daily tool)**
- RealGreen Mobile (WorkWave LLC): 1.48 (104), updated 2026-10-15 [iOS]. [iTunes API: RealGreen](https://itunes.apple.com/search?term=RealGreen&entity=software&country=us)
- Mobile Live (Real Green Systems): 1.83 (156) [iOS].
- Service Autopilot: 2.31 (90), updated 2026-07-26; SA Team: 2.86 (28) [iOS]. [iTunes API: Service Autopilot](https://itunes.apple.com/search?term=Service%20Autopilot&entity=software&country=us)
- CLIPitc: 3.46 (28) [iOS].
- Aspire Mobile: 2.21 (68) [iOS]. [iTunes API: Aspire](https://itunes.apple.com/search?term=Aspire%20landscape&entity=software&country=us)

**Beatability: dated review quotes**
- RealGreen, May 9, 2026 (2–10 employees, more than 2 years of use): "Tech support is terrible, cant get ahold of account managers, New SA5 and new mobile live 2.0 app is very clicky and hard to manage." [Capterra](https://www.capterra.com/p/78106/Service-Assistant/reviews/)
- RealGreen, March 5, 2025 (11–50 employees): "prepay letters not matching prepay amount, charging for each measuring license while also not offering a monthly license option." [Capterra]
- RealGreen, Nov 11, 2025: a user says they and a friend had asked for two upgrades for a year, "and still nothing." [Capterra]
- RealGreen, Feb 3, 2026 (51–200 employees): cannot "schedule one job over multiple days." [Capterra]
- Of the 25 RealGreen review titles in Capterra's JSON-LD sample, 7 are rated 1–2 stars. Examples: "Run from Real Green" and "Honest review of realgreen since workwave took over." [Capterra]
- Service Autopilot, Oct 3, 2024 (11–50 employees): "The company was bought by a credit card processor so you no longer have a choice of processor - which means rate increases sneak in." [Capterra](https://www.capterra.com/p/122075/Service-Autopilot/reviews/)
- 7 of 25 Service Autopilot sampled titles are rated 1–2 stars, including "Like using a buggy version of AOL from 1990." [Capterra]
- Third-party review sites report 25%+ single-year price increases after the Xplor deal. These are anecdotal and possibly affiliate content. [3rd-party review site](https://mowbosshq.pages.dev/guides/service-autopilot-review)
- CLIPitc, April 16, 2024: "they don't really test anything, and seems like they are trying to patch an outdated base program." [Capterra](https://www.capterra.com/p/105509/Clip-Lawn-Maintenance-Software/reviews/)
- Crew Control, May 29, 2026: there is no way to automatically tell customers which service is being performed ("routine maintenance, pine straw, weed control, etc."). This suggests that mow-focused tools model programs poorly. [Capterra](https://www.capterra.com/p/183299/Crew-Control/reviews/)

**TAM**
- 692,777 US landscaping-services businesses (2025) [IBISWorld snippet]. [IBISWorld](https://img3.ibisworld.com/united-states/number-of-businesses/landscaping-services/1497)
- 33,197 pest-control businesses (2025), an adjacent market [IBISWorld snippet]. [IBISWorld](https://img3.ibisworld.com/united-states/number-of-businesses/pest-control/1495)

### Inferences
- **Proposed spin.** "Program-first" software for 1–50-truck lawn-care, tree-shrub and mosquito companies. The customer buys a program (for example, a 7-round fertilization plan), and the system auto-generates each round by agronomic window and ZIP, gated by weather.
- **Key differentiators:**
  - prepay discounts and early-bird letters that reconcile correctly (a direct fix for the RealGreen complaint);
  - pesticide application records per stop (product, EPA registration number, rate, area, wind and temperature), with state-report export;
  - production-per-round dashboards;
  - a modern offline mobile app;
  - processor-agnostic payments, with Stripe as default but no lock-in.
- **MVP scope (about 8–12 weeks):**
  - customer and property records with measured square footage (manual entry or a drawn polygon on a map tile);
  - program and round templates;
  - round scheduling and route batching;
  - tech app with application-record capture;
  - auto-invoicing and prepay;
  - CSV import from RealGreen, Service Autopilot and CLIP;
  - customer portal.
- **Imagery note.** Satellite lawn measurement needs licensed imagery, such as Google Maps Platform or Nearmap. Keep it optional or use manual polygons; the Deep Lawn partnership shows this is a paid add-on in the market.
- **Expansion:**
  - tree-shrub PHC (which overlaps candidate 4);
  - mosquito and tick;
  - perimeter pest (overlaps candidate 9);
  - aeration, overseeding and irrigation-startup upsell campaigns;
  - winter snow (candidate 5);
  - direct-mail and lead marketing, which RealGreen itself sells;
  - prepay financing.
- **Channel.** Incumbents use trade media (Lawn & Landscape, Turf), GIE+EXPO, and marketing services. A solo founder can replicate this through owner Facebook groups and YouTube, plus a migration offer (free data import, a contract-buyout credit) aimed at RealGreen and SA users.
- **Scores:** Rev 5, Beat 5, Copy 4 (imagery optional), Exp 5, Chan 4, for **23/25**.

### Gaps
- No count was found for chemical-application lawn firms specifically, as opposed to all landscaping.
- No live RealGreen or Service Autopilot price list was found; both are demo-led.
- State pesticide-reporting formats vary and were not researched.

---

## Candidate 2: Commercial janitorial operations (bidding, site QA inspections, geofenced timekeeping, supply ordering)

### Takeaway
The large commercial-cleaning segment is served by a small modern player (Swept) whose own mobile app rates poorly, and by enterprise or custom-priced tools (WinTeam, Janitorial Manager). The workflow is copyable and has a large hourly workforce, which makes it payroll-adjacent. **Score 22/25.**

### Cited Findings
**Revenue proof**
- Swept: 2024 revenue estimated at $1.8M, up from $1.1M in 2023, with 18 employees [Latka est.]. [Latka Swept](https://getlatka.com/companies/swept)
- WinTeam has 123 Capterra reviews and Janitorial Manager 51 [Capterra 2026-11-07]. These are the review-count proxies for paid niche products. [Capterra janitorial category](https://www.capterra.com/janitorial-software/)

**Ratings**
- Swept: 4.3 (79), VfM 4.1 [Capterra]. [Capterra](https://www.capterra.com/p/148615/Swept/reviews/)
- WinTeam: 4.4 (123), ease 4.0 [Capterra]. [Capterra](https://www.capterra.com/p/184185/WinTeam/reviews/)
- Janitorial Manager: 4.6 (51), CS 4.8 [Capterra]. [Capterra](https://www.capterra.com/p/164100/Janitorial-Manager/reviews/)
- Others in the category: Clean Smarts 4.2 (16), Otuvy 4.2 (38), Lighthouse.io 4.4 (28) [Capterra].
- Swept Mobile: 2.74 (35), updated 2026-10-15 [iOS]. CleanGuru Janitorial: 4.52 (75) [iOS]. [iTunes API: Swept](https://itunes.apple.com/search?term=Swept%20janitorial&entity=software&country=us)

**Pricing**
- Swept: Launch $30/mo; Optimize $150/mo (adds inspections and geofenced clock-in); Scale $225/mo [Capterra pricing page]. [Capterra Swept pricing](https://www.capterra.com/p/148615/Swept/pricing/)
- Method's roundup says Swept starts at $150/mo [3rd-party]. [Method](https://www.method.me/resources/best-janitorial-software)

**Beatability: dated review quotes**
- Swept, March 10, 2025 (11–50 employees): "The app constantly crashed, or was too slow, or wouldn't open at all." [Capterra](https://www.capterra.com/p/148615/Swept/reviews/)
- WinTeam, May 22, 2025 (201–500 employees): "the person they assign to assist you is completely overwhelmed and resolutions are not fully effectuated." [Capterra](https://www.capterra.com/p/184185/WinTeam/reviews/)
- WinTeam, Aug 15, 2024: "Reports were bad and you are not able to pull reports of every field you enter data in." [Capterra]
- Janitorial Manager, Dec 3, 2025: "The main customer page is lacking." Most other JM reviews are positive. [Capterra](https://www.capterra.com/p/164100/Janitorial-Manager/reviews/)

**TAM**
- 1,232,252 US janitorial-services businesses (2025). This includes nonemployers; the commercial-contract subset is unknown [IBISWorld snippet]. [IBISWorld](https://img3.ibisworld.com/united-states/number-of-businesses/janitorial-services/1496)

### Inferences
- **Spin.** "Win and run commercial cleaning accounts" for 5–300-employee contract cleaners:
  - a bid calculator using square footage times production rates per space type, outputting a branded proposal;
  - recurring site schedules;
  - geofenced clock-in/out with a missed-shift alert to the supervisor (a "late notification" is a Swept core feature, so it is table stakes);
  - photo QA inspection scorecards shared with the client in a portal;
  - supply ordering per site;
  - payroll export.
- **MVP (about 8–10 weeks):** bid calculator and proposal; sites and schedules; employee mobile clock-in with geofence; inspection forms; client portal; QuickBooks and Gusto export. No hardware is needed.
- **Expansion:**
  - floor care, carpet and window crews (candidate 11);
  - post-construction cleaning;
  - day-porter and facility services;
  - embedded payroll and earned-wage access (large hourly headcount);
  - client-facing work-order requests;
  - multi-branch franchise accounts.
- **Channel.** ISSA, BSCAI, cleaning-business coaches on YouTube, Facebook commercial-cleaning groups, and SEO on terms like "janitorial bid calculator". A free bid-calculator lead magnet is easy to replicate.
- **Scores:** Rev 4, Beat 4, Copy 5, Exp 5, Chan 4, for **22/25**.

### Gaps
- Janitorial Manager and CleanGuru pricing appeared only in a search summary of comparison pages (custom pricing "from $1,000/mo" for JM; $49/mo for the CleanGuru bidding app) and was not pinned to a primary source.
- No count of commercial-only contract cleaners was found.

---

## Candidate 3: STR turnover-cleaning company operations (software for the cleaning company serving 20–500 Airbnb and Vrbo units)

### Takeaway
The proven products in this space are host- or property-manager-centric: Turno is a host/cleaner marketplace and Breezeway is a property-care platform. Their ratings and quotes show that cleaning companies want an end-to-end operations tool built around turnovers. Residential maid tools (ZenMaid, Automaid) are built around recurring home cleans, not check-out/check-in windows. **Score 21/25.**

### Cited Findings
**Revenue proof**
- TurnoverBnB (now Turno) raised a $4.5M Series A led by RET Ventures in 2021 [Press]. [BusinessWire](https://www.businesswire.com/news/home/20210817005829/en/TurnoverBnB-Raises-4.5-Million-in-Series-A-Round-Led-by-RET-Ventures)
- CB Insights lists $16.09M total over 4 rounds [3rd-party aggregator; later rounds unverified]. [CB Insights](https://www.cbinsights.com/company/turnoverbnb/financials)
- Breezeway has 196 Capterra reviews, 4.6 [Capterra 2026-11-07]. [Capterra Breezeway](https://www.capterra.com/p/186514/Breezeway/reviews/)

**App ratings**
- Turno Cleaners: 3.82 (1,066); Turno Hosts: 4.42 (607) [iOS 2026-11-07]. [iTunes API: Turno](https://itunes.apple.com/search?term=Turno%20cleaning&entity=software&country=us)
- Breezeway: Property Care: 3.17 (84); Breezeway Messaging: 2.50 (12) [iOS].
- ZenMaid Legacy: 3.28 (78); Maidily: 3.75 (8) [iOS]. [iTunes API: ZenMaid](https://itunes.apple.com/search?term=ZenMaid&entity=software&country=us)
- ResortCleaning: 5.0 (10) [Capterra]. Its rating is strong but its review base is tiny. [Capterra maid category](https://www.capterra.com/maid-service-software/)

**Beatability: dated quotes**
- Breezeway, Mar 17, 2026 (2–10 employees): "Being primarily a cleaning company, this does lack some functionality as an end-to-end software for us, causing us to create some work arounds." [Capterra](https://www.capterra.com/p/186514/Breezeway/reviews/)
- Breezeway, Nov 11, 2025 (11–50 employees): "it feels like the only software in the industry that isn't improving or releasing meaningful updates." [Capterra]
- Breezeway, Feb 13, 2025 (51–200 employees, 300+ properties): bulk texts "flood our inbox ... hard to filter." [Capterra]
- Breezeway, Mar 22, 2026: support problems with bugs and the WhatsApp integration. [Capterra]

**Integration surface**
- PMS marketplaces list cleaning integrations; for example, Hostfully lists Turno [Vendor]. [Hostfully](https://www.hostfully.com/integrations/turno/)

**TAM**
- 1.76M available US STR listings in June 2025, up 6.1% year over year (AirDNA "available listings" metric) [3rd-party data vendor]. [AirDNA June 2025 review](https://www.airdna.co/blog/us-review-june-2025)

### Inferences
- **Spin.** The operating system for the turnover-cleaning company:
  - iCal and PMS sync auto-creates turnovers inside the check-out-to-check-in window, with same-day-flip priority;
  - auto-assignment by cleaner zone and availability;
  - per-property checklists with required photos;
  - damage and low-supply reports pushed to the host;
  - linen par and laundry tracking;
  - per-turn cleaner pay;
  - per-turn or monthly host invoicing.
- **MVP (about 6–10 weeks):** iCal ingest (free and universal), turnover board, cleaner mobile app, checklists and photos, host portal, Stripe invoicing, cleaner pay report. Add Hostaway and Guesty APIs later.
- **Expansion:**
  - laundry and linen service;
  - restocking and consumables resale;
  - maintenance and handyman dispatch;
  - hot tub and pool checks;
  - home-watch for second homes;
  - a marketplace of vetted cleaners for hosts (Turno's model) once you have supply.
- **Channel.** Airbnb-cleaner Facebook groups, STR conferences, YouTube STR-cleaning coaches, PMS integration marketplaces, and co-marketing with linen suppliers.
- **Scores:** Rev 4, Beat 4, Copy 5, Exp 4, Chan 4, for **21/25**.

### Gaps
- No count of US STR-cleaning companies was found, and there is no NAICS code; the STR listing count is a proxy.
- Turno's pricing and post-2021 rounds were not verified from primary sources.

---

## Candidate 4: Tree care / arborist operations (estimating with map pins, crew and equipment scheduling, PHC programs)

### Takeaway
Arborist software is proven: ArboStar and SingleOps carry multi-million revenue estimates. The legacy specialist (Arborgold) is visibly decaying and SingleOps' iOS app has not been updated since April 2024. ArboStar is well rated on Capterra but on few reviews, and its mobile apps rate poorly. **Score 20/25.**

### Cited Findings
**Revenue proof**
- ArboStar: 2024 revenue estimated at $10.1M, up from $6.2M in 2023; 47 employees; HQ Canada [Latka est.]. [Latka ArboStar](https://getlatka.com/companies/arbostar)
- SingleOps: 2024 revenue estimated at $6M, up from $3.4M; $8.6M raised; 88 employees [Latka est.]. [Latka SingleOps](https://getlatka.com/companies/singleops)
- Capterra lists SingleOps as "by Granum" [Capterra]. [Capterra SingleOps](https://www.capterra.com/p/176935/SingleOps/)

**Ratings**
- ArboStar: 4.8 (47) [Capterra]. [Capterra arborist category](https://www.capterra.com/arborist-software/)
- ArborNote: 4.8 (10) [Capterra].
- Arborgold: 4.3 (65), VfM 4.0 [Capterra].
- SingleOps: 4.4 (108) [Capterra].
- Tree Plotter INVENTORY: 4.5 (111), which is municipal or inventory-focused [Capterra].
- Arborgold Crew (Tree Management Systems): 1.00 (4); MobileEstimator 7: 3.89 (9) [iOS]. [iTunes API: Arborgold](https://itunes.apple.com/search?term=Arborgold&entity=software&country=us)
- SingleOps: 3.56 (25), **last updated 2024-04-26** [iOS]. [iTunes API: SingleOps](https://itunes.apple.com/search?term=SingleOps&entity=software&country=us)
- ArboStar: 3.57 (35), last updated 2024-12-12; ArboStar Plus: 3.38 (24) [iOS]. [iTunes API: ArboStar](https://itunes.apple.com/search?term=ArboStar&entity=software&country=us)

**Pricing**
- ArboStar: "From US$149/mo billed yearly" per [Capterra NZ](https://www.capterra.co.nz/software/198069/arbostar), versus "$250 per month flat rate" per [GetApp](https://www.getapp.com/landscape-software/a/arbostar). The sources conflict.
- SingleOps: starting price $200/month [Capterra]. [Capterra](https://www.capterra.com/p/176935/SingleOps/)

**Beatability: dated quotes**
- Arborgold, June 21, 2026 (2–10 employees): "For us, Arborgold slowed us down, created extra frustration, and did not deliver on key items we were told would be available." [Capterra](https://www.capterra.com/p/12741/Arborgold/reviews/)
- Arborgold, May 4, 2026 (51–200 employees): "measuring tool imagery is also not the most up to date and does not allow you to toggle to winter months to see under tree coverage." [Capterra]
- 7 of 25 sampled Arborgold titles are rated 1–2 stars, for example "Very poor customer service. Be warned!" [Capterra]
- SingleOps, Apr 30, 2025 (2–10 employees): "The communication/syncing with Quickbooks is terrible, the reoccurring invoices are not automatic." [Capterra](https://www.capterra.com/p/176935/SingleOps/reviews/)
- SingleOps, Jul 29, 2025: "my subscription automatically renewed ... SingleOps won't cancel it until 2026." 4 of 25 sampled titles are rated 1–2 stars, including "Cumbersome and expensive." [Capterra]
- ArboStar, Nov 3, 2025: "While there is a phone app, screen real estate is limited which means that some things can't be shown." No sampled ArboStar titles are rated 1–2 stars. [Capterra](https://www.capterra.com/p/198069/ArboStar/reviews/)

**TAM**
- 175,035 US tree-trimming businesses (2025) per IBISWorld, which conflicts with 19,929 (2026) on another IBISWorld page [IBISWorld snippet]. [IBISWorld](https://script.ibisworld.com/united-states/number-of-businesses/tree-trimming-services/6064)

### Inferences
- **Spin.** Mobile-first arborist estimating and operations:
  - walk the property and drop a pin per tree;
  - attach species, DBH, photo and work type (prune, remove, stump, cable);
  - get a good/better/best proposal with a map;
  - schedule crews plus equipment (bucket truck, crane, chipper) with conflict checks;
  - run PHC treatment programs, reusing candidate 1's program engine;
  - track ISA certification and safety (job briefings).
- **Imagery.** Winter or leaf-off imagery (a gap the Arborgold reviewer flagged) requires licensed historical imagery such as Nearmap. Optional for the MVP.
- **MVP (about 10–12 weeks):** pin-based estimating and proposal, crew and equipment calendar, offline mobile app, invoicing and deposits, QuickBooks two-way sync done well (a pain point at SingleOps and CLIPitc).
- **Expansion:**
  - PHC and lawn (candidate 1);
  - stump grinding and land clearing;
  - municipal and HOA tree inventories (Tree Plotter has 111 reviews, proving demand);
  - utility vegetation-management subcontracting;
  - consumer financing for removals.
- **Channel.** TCIA (Tree Care Industry Association) and TCI EXPO, ISA chapters, arborist Facebook groups, and YouTube climbers and tree-business channels. ArboStar's growth (estimated $6.2M to $10.1M) suggests the channel works.
- **Scores:** Rev 4, Beat 4, Copy 4, Exp 4, Chan 4, for **20/25**.

### Gaps
- Arborgold's current owner and pricing amounts were not found; Capterra shows "3 pricing plans" without figures.
- Granum's relationship to SingleOps (and to LMN) is unverified beyond the Capterra label.

---

## Candidate 5: Commercial snow and ice management (weather-triggered dispatch, time-stamped proof of service against slip-and-fall claims, per-push/per-event billing)

### Takeaway
This is a large, fragmented, liability-driven niche. Capterra has no dedicated category (the slug returns 404). Most tools are either generalists that "lack some snow-specific features" or enterprise suites. Proof of revenue for snow-specific vendors is thin, but adjacent proof is strong (Aspire was acquired by ServiceTitan). The MVP needs no proprietary data, since NWS weather data is free. **Score 20/25.**

### Cited Findings
**Market size**
- SIMA cites an $18B US private snow and ice industry (plus about $4.7B in Canada) [trade association]. [SIMA our-industry](https://sima.org/our-industry?hsLang=en)
- Earlier SIMA research put private-contract snow removal at $16.8B [Press, dated]. [Facilitiesnet](https://www.facilitiesnet.com/site/pressreleases/SIMA-Research-Shows-that-Removing-Snow-Under-Private-Contract-is-a-168-Billion-Industry--38875)
- 111,608 US snowplowing businesses (2025, +3.8%) [IBISWorld snippet]. [IBISWorld](https://script.ibisworld.com/united-states/number-of-businesses/snowplowing-services/5400)
- A secondary blog cites SIMA figures of about 88,200 snow businesses (2022), with the top 4 firms holding about 5% share and "more than 30,000" slip-and-fall claims per year [secondary, lower reliability]. [Blog](https://snowremovalnation.pages.dev/blog/the-hidden-workforce-behind-the-plows-who-actually-clears-the-snow)

**Incumbents and pricing**
- Yeti Snow: about $31.50–$50/mo, with event-based dispatch, GPS tracking, time-stamped logs and snow invoicing [3rd-party roundup]. [Contractorapps roundup](https://contractorapps.pages.dev/comparisons/best-field-service-software-snow-removal)
- Jobber: from about $39/mo, but lacks some snow-specific features [3rd-party roundup].
- SafetyCulture snow and ice template: from $129/mo billed annually [Vendor]. [SafetyCulture](https://safetyculture.com/app/snow-and-ice-management-software)
- Aspire is described as "the enterprise commercial-snow platform — deep, expensive, and worth it past $1M revenue" [3rd-party]. Aspire's own blog publishes a "best snow removal apps" list [Vendor]. [Aspire blog](https://www.youraspire.com/blog/best-snow-removal-business-apps)
- Sitefotos positions itself as an end-to-end platform for "snow removal, landscaping and property maintenance: photo documentation, forms, work orders" [Vendor]. [Sitefotos](https://sitefotos.com/) Its iOS listing shows 0 ratings [iOS 2026-11-07], so no app-store signal is available. [iTunes API: Sitefotos](https://itunes.apple.com/search?term=SiteFotos&entity=software&country=us)
- ServiceTitan agreed to acquire Aspire in July 2021 [Press]. [ACHR News](https://www.achrnews.com/articles/145133-servicetitan-plans-to-acquire-aspire)
- Aspire Mobile: 2.21 (68) [iOS]; Aspire: 4.4 (362) [Capterra].
- Aspire review, July 14, 2026 (51–200 employees): "The CRM lacks many features ... the customer portal isn't as intuitive." [Capterra](https://www.capterra.com/p/161544/Aspire/reviews/)

### Inferences
- **Spin.** "Snow ops plus legal-grade proof" for 3–75-truck commercial snow contractors serving property managers:
  - storm events are created from NWS forecasts and trigger thresholds per site contract (for example, 2-inch trigger);
  - crews dispatch by route;
  - every visit logs GPS, timestamp, photos, salt and ice-melt quantities and surface conditions into a tamper-evident record;
  - a property-manager portal and PDF "service affidavits" are available for slip-and-fall defense;
  - billing supports per-push, per-event, per-inch, seasonal and time-and-materials contracts, plus subcontractor pay.
- **MVP (about 8 weeks):** sites and contracts, storm events, crew app with photo and GPS logs, an event billing engine, a client portal and subcontractor statements.
- **Expansion:**
  - year-round commercial landscape maintenance for the same properties (candidates 1 and 4);
  - parking-lot sweeping and striping;
  - holiday lighting;
  - insurance partnerships (documented-proof discounts);
  - a subcontractor marketplace for overflow storms.
- **Channel.** SIMA Snow & Ice Symposium and membership, plow-contractor forums and Facebook groups, and pre-season (Aug–Oct) SEO and ads. The seasonality means sales concentrate in fall.
- **Scores:** Rev 3 (vendor revenues for snow-only tools unverified), Beat 4, Copy 5, Exp 4, Chan 4, for **20/25**.

### Gaps
- No revenue, review count or pricing was found for Sitefotos or Yeti Snow beyond roundup claims.
- The slip-and-fall claim statistics come from a secondary source, and the SIMA primary report was not fetched.

---

## Candidate 6: Fire and life-safety inspection software for small (1–15-tech) extinguisher, kitchen-hood, sprinkler and backflow route businesses

### Takeaway
Revenue is strongly proven: ServiceTrade carries about a $30M estimate, Inspect Point raised $28M, and Uptick (proven in Australia and New Zealand) took PSG money to expand in North America. The incumbents skew to demo-only or enterprise pricing. The weakness to exploit is affordable, offline-first inspection for owner-operators. Licensed-company lists published by fire marshals make outbound prospecting easy. **Score 20/25.**

### Cited Findings
**Revenue proof**
- ServiceTrade: 2024 revenue estimated at $30.4M, up from $19.6M; $34.1M raised; 211 employees [Latka est.]. [Latka ServiceTrade](https://getlatka.com/companies/servicetrade)
- Inspect Point: $28M equity investment from Mainsail Partners in January 2022 [Press]; "more than 4.5 million inspections" completed; FireCAD acquired in April 2025 [Vendor/Press]. [Inspect Point press](https://www.inspectpoint.com/?p=2297)
- Uptick: strategic growth investment from PSG (June 2025) with a North America focus, and "1.6 million buildings and 26 million pieces of ... equipment" maintained yearly [Press]. [Intl Fire & Safety Journal](https://internationalfireandsafetyjournal.com/psg-backs-uptick-to-expand-global-fire-protection-software/) It also opened a Denver hub [Press]. [WBOC release](https://www.wboc.com/online_features/press_releases/uptick-opens-denver-hub-as-it-expands-north-american-footprint/article_984bdcaf-bd42-515e-ad1d-964318880c48.html) Uptick has a US fire-inspection page [Vendor]. [Uptick US](https://www.uptickhq.com/us)

**Ratings and pricing**
- ServiceTrade: 4.6 (345) [Capterra]; iOS 4.15 (587) [iOS]. [Capterra](https://www.capterra.com/p/132690/ServiceTrade-Commercial/reviews/); [iTunes API: ServiceTrade](https://itunes.apple.com/search?term=ServiceTrade&entity=software&country=us)
- Workforce by Uptick: 3.55 (11) [iOS]. [iTunes API: Uptick](https://itunes.apple.com/search?term=Uptick&entity=software&country=us)
- Inspect Point's pricing page lists no prices ("contact the sales team") [Vendor]. [Inspect Point pricing](https://www.inspectpoint.com/pricing/)

**Beatability: dated quotes**
- ServiceTrade, Apr 27, 2026 (2–10 employees): "The offline functionality for technicians' phones is spotty ... techs' notes will often disappear when they sync back online, and I was told to just take notes in a different app." [Capterra](https://www.capterra.com/p/132690/ServiceTrade-Commercial/reviews/)
- ServiceTrade, May 13, 2026 (501–1,000 employees): "It can also become costly as advanced features or additional support are added." [Capterra]

**Backflow adjacency**
- Syncta offers a tester-side app for "scheduling, routing, submitting, and managing backflow tests" [Vendor]. [Syncta](https://www.syncta.com/)
- SwiftComply sells the municipal-utility side [Vendor]. [SwiftComply](https://www.swiftcomply.com/backflow-prevention-software/)

**TAM (definitions conflict)**
- About 25,491 US fire-protection service businesses (2023) [secondary, unverified]. [WifiTalents](https://wifitalents.com/fire-protection-services-industry-statistics/)
- 19,845 fire-protection and security installation contractors (2025) [IBISWorld snippet]. [IBISWorld](https://www.ibisworld.com/united-states/number-of-businesses/fire-protection-security-system-installation-contractors/6486/)
- 11,752 fire-protection consultants (2025), defined as testing and inspection without sales or installation [IBISWorld snippet]. [IBISWorld](https://www.ibisworld.com/united-states/number-of-businesses/fire-protection-consultants/6485/)
- Cities and states publish licensed extinguisher-company lists, for example Charlotte NC and Arkansas [Gov]. [Charlotte list](https://charlottenc.gov:443/files/sharedassets/city/v/1/public-safety/fire/documents/registered-fire-equipment-companies.pdf); [Arkansas list](https://labor.arkansas.gov/wp-content/uploads/2024-2025-PORTABLE-FIXED-SYSTEMS-COMPANIES1-14-25.pdf)

### Inferences
- **Spin.** "Inspection route in a box" for owner-operated extinguisher, hood-cleaning and backflow shops:
  - asset-level recurring schedules (annual, semi-annual, 6-year and 12-year hydro dates for extinguishers);
  - NFPA 10, 25, 72 and 96 form templates;
  - barcode or QR tag scanning;
  - truly offline mobile (ServiceTrade's weak spot);
  - deficiency-to-quote-to-repair conversion;
  - customer compliance portal;
  - AHJ and municipal report export.
  - Publish transparent self-serve pricing against demo-only incumbents.
- **MVP (about 10–12 weeks):** asset register, recurring inspection generator, offline forms engine with 5–8 NFPA templates, deficiency quotes, invoicing, PDF certificates.
- **Expansion:**
  - backflow testing with water-utility submission formats (Syncta-like);
  - kitchen-hood cleaning photo reports;
  - emergency lighting;
  - sprinkler and alarm;
  - later, monitoring-center integrations.
  - Uptick's progression from niche to 1.6M buildings shows the expansion path.
- **Channel.** NAFED and NFSA, state fire-marshal licensee lists (for cold outbound), and trade shows. Mainsail and PSG funding signals that PE roll-ups are active, which makes an eventual exit plausible.
- **Scores:** Rev 5, Beat 3 (ServiceTrade is decent at 4.6), Copy 4 (many forms and state variations), Exp 4, Chan 4, for **20/25**.

### Gaps
- No NAFED membership count was found.
- Uptick's US pricing and the PSG deal amount are undisclosed.
- AHJ portal requirements (for example, third-party reporting platforms) were not researched.

---

## Candidate 7: Roll-off dumpster rental plus junk removal

### Takeaway
Venture money proves the category (Hauler Hero's $10M seed and $16M Series A; CurbWaste; ServiceCore's Docket). The beatable gap is the 1–20-can owner-operator. That operator needs online booking with ZIP and size pricing, a "where is every can" map, rental-day and overweight auto-charges, and landfill-ticket capture. Funded players skew to bigger haulers and AI and municipal ambitions. **Score 20/25.**

### Cited Findings
**Revenue and funding proof**
- Hauler Hero: $16M Series A led by Frontier Growth, announced Feb 2026 (CB Insights dates it Dec 2, 2025), following a $10M seed [Press]. Its product covers roll-off dispatch, a tablet app and automated invoicing. [Pulse 2](https://pulse2.com/hauler-hero-16-million-series-a/); [Waste Today seed](https://www.wastetodaymagazine.com/news/hauler-hero-announces-10m-in-seed-funding)
- CurbWaste: 2024 revenue estimated at $3M, up from $1.6M; $1.2M raised; 40 employees (Latka page updated Oct 2024) [Latka est.]. [Latka CurbWaste](https://getlatka.com/companies/curbwaste)
- Docket (dumpster rental and junk removal software) is listed as a subsidiary founded in 2023, and ServiceCore is credited on its materials [3rd-party/Vendor]. [Craft.co](https://craft.co/docket-73fd2322ca); [Docket](https://www.yourdocket.com/dumpster-rental-software)

**App ratings**
- Curbwaste Driver: 3.57 (14) [iOS].
- ServiceCore Legacy: 2.92 (48); a new ServiceCore Mobile app released 2026-10-27 has 0 ratings [iOS]. [iTunes API: CurbWaste](https://itunes.apple.com/search?term=CurbWaste&entity=software&country=us); [iTunes API: ServiceCore](https://itunes.apple.com/search?term=ServiceCore&entity=software&country=us)
- "Haul Hero" (seller HAUL HERO LLC): 4.64 (11), last updated 2023-05-25. This may not be the funded Hauler Hero, since the seller name differs [iOS]. [iTunes API: Hauler Hero](https://itunes.apple.com/search?term=Hauler%20Hero&entity=software&country=us)
- Dumpster Controls: 4.69 (13) [iOS].

### Inferences
- **Spin.** "Dumpster rental on autopilot" for small roll-off fleets:
  - an embeddable booking widget (ZIP to price, by size, with debris-type restrictions);
  - deposit capture;
  - an inventory map and status;
  - drop, swap and pull dispatch;
  - automatic extra-day and overweight billing from scale-ticket photos (OCR);
  - landfill cost reconciliation;
  - permit reminders.
- **MVP (about 6–8 weeks):** booking widget and payments, inventory board and map, driver app with photo-of-ticket, auto-billing rules, and QuickBooks sync.
- **Expansion:**
  - junk removal (volume-based quotes from photos);
  - portable toilets and septic (candidate 10);
  - demolition and cleanouts;
  - recycling diversion reports for commercial clients.
  - A lead marketplace linking homeowners to haulers also fits.
- **Channel.** Dumpster-rental business Facebook groups and YouTube "dumpster rental business" creators (a large how-to-start audience), WasteExpo, and SEO for "dumpster rental software".
- **Scores:** Rev 4, Beat 3 (well-funded modern entrants), Copy 5, Exp 4, Chan 4, for **20/25**.

### Gaps
- No US count of roll-off rental businesses was found (NAICS 562111/562119 counts were not retrieved).
- No Capterra ratings or review counts were pulled for Docket, CurbWaste or Hauler Hero.
- Docket pricing was not retrieved.

---

## Candidate 8: Painting contractor estimating and sales

### Takeaway
There are two proven painting-specific products: PaintScout (about a $1.1M estimate) and DripJobs ($97–$147/mo). Both have very thin review bases, so neither dominates. The market of about 223K painting businesses is large. A modern estimating-plus-CRM product with good homeowner-facing proposals is beatable territory. **Score 20/25.**

### Cited Findings
**Revenue proof**
- PaintScout: 2025 revenue estimated at $1.1M, 10 employees, founded 2018 [Latka est.]. [Latka PaintScout](https://getlatka.com/companies/paintscout)

**Pricing and reviews**
- PaintScout: from $79 per user per month [GetApp/Capterra listing]; GetApp shows 4.8/5 from 6 reviews [3rd-party listing]. [GetApp PaintScout](https://www.getapp.com/construction-software/a/paintscout/); [Capterra PaintScout](https://www.capterra.com/p/201082/PaintScout/)
- DripJobs: Pro $97/mo, Advanced $147/mo, Growth custom; month-to-month [Vendor]. Capterra shows about 2 reviews [Capterra]. [DripJobs pricing](https://dripjobs.com/pricing); [Capterra DripJobs](https://www.capterra.com/p/245980/DripJobs/)
- The painter channel is big: the Sherwin-Williams PRO+ app has 4.73 (14,251 ratings) [iOS]. A small painter-specific app, Paintbox, has 4.18 (17) [iOS]. [iTunes API: PaintScout search](https://itunes.apple.com/search?term=PaintScout&entity=software&country=us)

**TAM**
- 223,209 US house painting & decorating contractor businesses (2025) [IBISWorld snippet]; another IBISWorld page shows 217,412 for 2026. [IBISWorld](https://script.ibisworld.com/united-states/number-of-businesses/house-painting-decorating-contractors/5738)

### Inferences
- **Spin.** Production-rate estimating:
  - measure rooms or walls by surface type;
  - apply crew production rates and coats to get labor hours and gallons;
  - produce good/better/best interactive proposals with e-sign, deposit and financing;
  - give homeowners a color-selection portal;
  - pay crews and subs by percentage of job;
  - send job-costing variance reports.
- **MVP (about 6–8 weeks):** estimator, proposal and e-sign, deposit payments, simple scheduling, follow-up automation (DripJobs' core hook), crew pay report.
- **Expansion:**
  - cabinet refinishing, epoxy floors, deck and fence staining, drywall and wallcovering, commercial repaint bids;
  - supplier integrations (paint ordering), consumer financing, and lead marketplaces.
  - The same estimator chassis works for fence and deck builders (not researched in depth).
- **Channel.** PCA (Painting Contractors Association), painting-business Facebook groups and coaches (DripJobs markets as "built by a painter"), and YouTube. Paint-supplier partnerships are a powerful but slower channel.
- **Scores:** Rev 3, Beat 4, Copy 5, Exp 4, Chan 4, for **20/25**.

### Gaps
- PaintScout's own pricing page returned only testimonials in search.
- Capterra review counts for PaintScout and DripJobs were not fully pulled, and no churn or complaint quotes were found.
- Competitors such as Estimate Rocket and Housecall Pro estimating were not rated specifically for painting.

---

## Candidate 9: Pest control mid-market (5–40 trucks), entering through a wildlife-control and exclusion wedge

### Takeaway
Revenue in pest control is proven: FieldRoutes went to ServiceTitan, PestPac sits inside WorkWave, and ServicePro (ServSuite) is listed as another ServiceTitan buy. The mid-market incumbents are poorly rated, especially on mobile. But GorillaDesk (4.8, 278 reviews, 97% recommend) dominates small shops, so the kill rule applies to "small generic pest". The beatable opening is (a) mid-size PestPac refugees and (b) wildlife-control operators, who hack generic tools for trap checks and exclusion bids. **Score 18/25.**

### Cited Findings
**Revenue proof**
- FieldRoutes was acquired by ServiceTitan in January 2022 [Press] and has a 2025 revenue estimate of $16.4M [Latka est.]. [ServiceTitan press](https://www.servicetitan.com/press/fieldroutes-acquisition); [Latka](https://getlatka.com/companies/fieldroutes)
- ServiceTitan's acquisition of ServicePro (ServSuite) is listed on a deal database [3rd-party; details not verified]. [PrivSource](https://www.privsource.com/acquisitions/deal/e4SyNm)

**Ratings**
- PestPac: 3.9 (256), CS 3.9, VfM 3.8, ease 3.6 [Capterra 2026-11-07]. [Capterra](https://www.capterra.com/p/23130/PestPac/reviews/)
- FieldRoutes: 4.3 (404) [Capterra].
- GorillaDesk: 4.8 (278), 97% recommend [Capterra]. [Capterra pest category](https://www.capterra.com/pest-control-software/)
- PestPac Mobile (version 3, WorkWave): 2.40 (149); WorkWave Route Manager: 4.44 (1,220) [iOS]. [iTunes API: PestPac](https://itunes.apple.com/search?term=PestPac&entity=software&country=us)
- FieldRoutes: 3.33 (27); PestRoutes Sales: 2.74 (104) [iOS]. [iTunes API: FieldRoutes](https://itunes.apple.com/search?term=FieldRoutes&entity=software&country=us)
- GorillaDesk: 4.44 (63) [iOS]. [iTunes API: GorillaDesk](https://itunes.apple.com/search?term=GorillaDesk&entity=software&country=us)

**Beatability: dated quotes**
- 8 of 25 sampled PestPac titles are rated 1–2 stars, for example "PestPac is a total ripoff", "I wish I used jobber from day 1" and "Be very careful when you transfer or sell your business." [Capterra](https://www.capterra.com/p/23130/PestPac/reviews/)
- PestPac, Jul 3, 2025 (2–10 employees): "They overpromised and underdelivered then insist on continuing to bill me for the entire contract." [Capterra]
- FieldRoutes, May 14, 2026 (11–50 employees): "these limitations are creating extra administrative work, slowing down reporting." [Capterra](https://www.capterra.com/p/146076/FieldRoutes/reviews/)
- GorillaDesk, Sep 17, 2024: "customer services is terrible. When something happens or is down they dont notify you." This is a minority view against a 4.8 average. [Capterra](https://www.capterra.com/p/130290/GorillaDesk/reviews/)

**Wildlife wedge**
- GorillaDesk markets a wildlife-control page [Vendor]. [GorillaDesk wildlife](https://gorilladesk.com/?p=55152)
- QuoteIQ self-ranks for wildlife, claiming trap inventory, species templates and satellite measuring [Vendor, self-promotional]. [QuoteIQ](https://myquoteiq.com/top-8-softwares-for-wildlife-removal-businesses-in-2026/)
- NWCOPRO is listed on G2 with few details [3rd-party]. [G2 NWCOPRO](https://www.g2.com/products/nwcopro-wildlife-control-software/reviews)
- A Jobber community thread shows wildlife operators improvising trap-job and follow-up structures [Forum]. [Jobber community](https://community.getjobber.com/discussions/cleaning-and-property-maintenance/wildlife-control-pros-%E2%80%94-how-are-you-structuring-trap-jobs--follow-ups/10146)
- States license nuisance-wildlife trappers, for example Florida FWC trapper registration [Gov]. [FWC](https://myfwc.com/license/wildlife/nuisance-wildlife-permits/trapper-registration/)

**TAM**
- 33,197 US pest-control businesses (2025) [IBISWorld snippet]. [IBISWorld](https://img3.ibisworld.com/united-states/number-of-businesses/pest-control/1495)

### Inferences
- **Spin (wedge).** Wildlife-control and exclusion operations:
  - trap-set records with a mandated 24-hour check reminder;
  - species, disposition and relocation logs exportable for state reports;
  - photo-annotated exclusion estimates (sealing points, one-way doors);
  - warranty renewals.
- **Expansion** into full pest: chemical use records with EPA registration numbers, termite bait-station barcode tracking, WDO/NPMA-33 forms, and service agreements. This then targets 5–40-truck PestPac refugees with a migration service.
- **MVP (about 8 weeks)** for the wedge: jobs with trap sets, check scheduling, species log, estimate builder with photo markup, invoicing, renewals.
- **Channel.** NWCOA and state wildlife associations, PCT and PMP trade media, NPMA PestWorld, and pest-owner Facebook groups.
- **Scores:** Rev 5 (pest overall; wildlife-specific revenue unproven), Beat 3 (GorillaDesk is strong), Copy 3 (pest compliance depth), Exp 4, Chan 3, for **18/25**.

### Gaps
- No count of wildlife-control operators was found, and no wildlife-specific software revenue was found.
- PestPac and FieldRoutes pricing were not retrieved.
- Mandatory trap-check intervals vary by state and were not tabulated.

---

## Candidate 10: Septic and grease-trap pumping

### Takeaway
The niche is served by one specialist (ServiceCore, whose legacy app rates poorly), by a legacy incumbent (Summit, now under Ritam Technologies), and by small waste-ERP vendors. Its workflow is specific enough that generic FSM falls short: tank history, disposal manifests and gallons, county inspection forms, and FOG (grease) compliance intervals. Revenue proof is moderate, and Latka's data for ServiceCore is unreliable. **Score 18/25.**

### Cited Findings
**Incumbents**
- ServiceCore is built for "septic, grease, portable restroom rental, and roll-off rental" operators, with two-way QuickBooks sync [Vendor]. [ServiceCore septic](https://try.servicecore.com/septic-business-software/)
- Latka lists ServiceCore 2022 revenue at $3.4M with 126 employees. Its "$548M raised" figure is implausible [Latka]. [Latka](https://getlatka.com/companies/servicecore)
- Summit, "now operated by Ritam Technologies", is described as the legacy incumbent in portable sanitation and septic [Vendor comparison content from ServiceCore; biased]. [ServiceCore blog](https://servicecore.com/blog/summit-vs-housecall-pro/)
- CRO by RapidWorks is a competitor for mixed portable sanitation, septic and roll-off operators [Vendor content, biased]. [RapidWorks](https://www.rapidworks.com/blog/best-servicecore-alternatives-portable-sanitation)
- ServiceCore Legacy: 2.92 (48); the new ServiceCore Mobile app (released 2026-10-27) has 0 ratings [iOS 2026-11-07]. [iTunes API: ServiceCore](https://itunes.apple.com/search?term=ServiceCore&entity=software&country=us)

### Inferences
- **Spin.** "Septic and grease route compliance":
  - a GPS-pinned tank and lid-location history with photos;
  - pump-out records with gallons and a disposal-site manifest;
  - county or state inspection report templates (real-estate transfer inspections);
  - grease-trap interval scheduling (for example, 90-day) with FOG manifest exports for municipal pretreatment programs;
  - truck capacity-aware routing.
- **MVP (about 8–10 weeks):** customer and tank registry, recurring interval scheduling, driver app with manifest capture, disposal log, invoicing, QuickBooks sync.
- **Expansion:**
  - portable toilets and roll-off (candidate 7);
  - drain cleaning and hydro-jetting;
  - septic inspections for realtors (lead channel);
  - municipal FOG program reporting.
- **Channel.** The WWETT Show (pumper industry), *Pumper* magazine, NOWRA and state septic associations, and owner Facebook groups.
- **Scores:** Rev 3, Beat 4, Copy 4, Exp 3, Chan 4, for **18/25**.

### Gaps
- No US count of septic-service businesses was found (NAICS 562991 not retrieved).
- No Capterra ratings were found for ServiceCore or Summit.
- Grease-trap manifest formats by municipality were not researched.

---

## Candidate 11: Carpet, upholstery and tile cleaning

### Takeaway
There is a sizable niche (about 41K businesses) with one specialist (ServiceMonster) whose mobile app rates poorly and whose review base is thin, while generalists cover the basics. It is very copyable, but revenue proof for a specialist is weak. **Score 17/25.**

### Cited Findings
- ServiceMonster: 4.6 (16) on Capterra US; it is designed specifically for the carpet-cleaning industry [Capterra / 3rd-party summary]. [Capterra ServiceMonster](https://www.capterra.com/p/119312/ServiceMonster/)
- ServiceMonster iOS app: 2.78 (55), updated 2026-11-05 [iOS 2026-11-07]. [iTunes API: ServiceMonster](https://itunes.apple.com/search?term=ServiceMonster&entity=software&country=us)
- ServiceMonster pricing conflicts across sources:
  - $49/mo [GetApp](https://www.getapp.com/all-software/a/servicemonster/);
  - $60 per user per month [Capterra];
  - $99 per user per month [ITQlick](https://www.itqlick.com/servicemonster);
  - a competitor (QuoteIQ) cites a $279.99/mo Premier tier [competitor content]. [QuoteIQ](https://myquoteiq.com/best-servicemonster-alternative-for-carpet-cleaning-businesses/)
- 40,945 US carpet-cleaning businesses (2025, +1.8%) [IBISWorld snippet]. [IBISWorld](https://img3.ibisworld.com/united-states/number-of-businesses/carpet-cleaning/1498)

### Inferences
- **Spin.** Room and area menu pricing, with stain treatment, protectant and deodorizer upsells; automatic 6- and 12-month re-clean reminders; and on-site rug pickup and plant-processing tracking. Bundle it with candidate 2 as a cleaning suite.
- **MVP (about 6 weeks):** price-book quoting, scheduling, tech app, invoicing, recurring reminder campaigns.
- **Expansion:** tile and grout, air-duct cleaning, rug-plant operations, and water-damage mitigation (IICRC drying logs; Xactimate-compatible exports would be needed later).
- **Channel.** IICRC courses, Cleanfax, owner Facebook groups and YouTube.
- **Scores:** Rev 2, Beat 3, Copy 5, Exp 4, Chan 3, for **17/25**.

### Gaps
- No revenue estimate for ServiceMonster was found (no Latka page).
- Competitor share in carpet cleaning versus Housecall Pro and Jobber is unknown.

---

## Kill list: candidates that fail the kill rule or lacked evidence (brief)

### Takeaway
Seven niches fail the kill rule outright because a modern, well-rated, fairly priced specialist dominates: residential pool service, home inspection, mobile pet grooming, mobile detailing, residential maid service, small-shop pest control, and roofing measurement (on copyability). Others were dropped for insufficient revenue evidence or because the core software already bundles the feature.

### Cited Findings
- **Pool service (residential maintenance): KILL.**
  - Skimmer: 4.9 (233), CS 4.9, 97% recommend [Capterra 2026-11-07]. [Capterra pool category](https://www.capterra.com/pool-service-software/)
  - Skimmer raised a $74M Series C from Mainsail (Oct 2024), for $84M total; it then had 29,000+ pros servicing 700,000 pools [Press], and now claims 30,000+ pool pros [Vendor]. [Mainsail](https://mainsailpartners.com/skimmer-receives-growth-investment-from-mainsail-partners/); [Skimmer](https://www.getskimmer.com/)
  - Skimmer acquired Pool Builder Geek and Poologics (Aug 2026), expanding into construction and renovation [Press]. [PE Professional](https://peprofessional.com/2026/08/mainsail-backed-skimmer-acquires-pool-builder-geek-and-poologics/)
  - Pool Brain: 4.9 (27) [Capterra]; iOS 3.99 (260) [iOS].
  - Residual irritants: a reported per-pool price rise from $1 to $2 on the Scaling Up tier [3rd-party review site](https://pooldial.com/resources/articles/software-reviews/skimmer-review), and a May 9, 2025 Capterra quote: "Pricing model makes for no way to improve your costs as you pay per customer." [Capterra](https://www.capterra.com/p/177014/Skimmer/reviews/)
- **Home inspection: KILL.**
  - Spectora: 4.9 (937), 95% recommend [Capterra]; iOS 4.76 (2,076) [iOS]; "used by over 12,000 inspectors" [Vendor]. [Capterra home-inspection](https://www.capterra.com/home-inspection-software/); [Spectora](https://www.spectora.com/)
  - Also ISN 4.7 (328) and HomeGauge 4.6 (501) [Capterra].
  - Latka's $5.9M 2025 estimate for Spectora looks low against 12,000 inspectors [Latka est.]. [Latka](https://getlatka.com/companies/spectora)
- **Mobile pet grooming routes: KILL.**
  - MoeGo: 4.7 (232) [Capterra]; iOS 4.59 (298) [iOS].
  - DaySmart Pet iOS: 4.77 (1,103) [iOS]. Time To Pet: 4.9 (301) [Capterra]. [Capterra pet-grooming](https://www.capterra.com/pet-grooming-software/)
  - Gingr's pet-parent app rates 2.14 (307) [iOS], but that is boarding and daycare, not home service.
- **Mobile car detailing: KILL.** Urable rates iOS 4.81 (278) and markets itself as "the most affordable ... all in one CRM" for detailing and PPF [iOS / Vendor]. [Urable](https://urable.com/) Mobile Tech RX rates 4.41 (205) [iOS].
- **Residential maid service: KILL (crowded and well rated).**
  - ZenMaid: 4.7 (205) [Capterra], with an estimated $2.6M 2024 revenue and 1K customers [Latka est.]. [Latka ZenMaid](https://getlatka.com/companies/zenmaid)
  - Automaid: 4.7 (209); Maidily: 4.8 (33), with an estimated $597.9K [Latka est.]. [Capterra maid](https://www.capterra.com/maid-service-software/)
  - The STR-turnover spin survives as candidate 3.
- **Small-shop pest control (1–5 techs): KILL.** GorillaDesk rates 4.8 (278), with CS 4.8, VfM 4.8 and 97% recommend [Capterra]. [Capterra pest](https://www.capterra.com/pest-control-software/) The mid-market and wildlife spin survives as candidate 9.
- **Mow-only lawn care for solos: KILL.** Crew Control rates 4.8 (100), LawnPro 4.6 (188) and Jobber 4.6 (1,490) [Capterra]. The chemical-program spin survives as candidate 1.
- **Roofing measurement and CRM: KILL (copyability and data moat).**
  - Roofr has an estimated $35.2M 2023 revenue [Latka est.]. [Latka Roofr](https://getlatka.com/companies/roofr)
  - AccuLynx: 4.6 (847), with an estimated $14.4M [Capterra / Latka est.]. JobNimbus: 4.6 (482), with an estimated $25M [Capterra / Latka est.]. [Capterra roofing](https://www.capterra.com/roofing-software/)
  - Measurement requires aerial imagery plus ML. Roofr's own reviews complain about imagery and accuracy ("Measurements are regularly incorrect", Jul 10, 2022; "not being able to get clear imagery", Aug 6, 2021). [Capterra Roofr](https://www.capterra.com/p/208102/Roofr/reviews/)
- **Solar installer design: KILL (imagery and irradiance data).** The Capterra solar category is dominated by construction PM tools (Procore 4.5 (2,680), JobNimbus) plus EagleView at 4.3 (44), VfM 3.7 [Capterra]. No niche revenue proof was gathered this round. [Capterra solar](https://www.capterra.com/solar-software/)
- **Garage doors, locksmiths and handyman: KILL (horizontal tools suffice).** The Capterra categories for all three are populated almost entirely by horizontal FSM: Housecall Pro 4.7 (2,749), Jobber 4.6 (1,490), FieldPulse 4.6 (510), Tradify 4.7 (152) [Capterra]. No specialist with revenue proof appears. [Capterra garage-door](https://www.capterra.com/garage-door-software/); [Capterra locksmith](https://www.capterra.com/locksmith-software/); [Capterra handyman](https://www.capterra.com/handyman-software/)
- **Window cleaning, pressure washing and gutter cleaning: DROPPED (insufficient evidence).**
  - Capterra category slugs returned 404 (checked 2026-11-07), and no revenue-proven US specialist was verified.
  - UK window-round app Squeegee rates only 4.14 (22) on US iOS, which is not a strong "proven abroad" signal. [iTunes API: Squeegee](https://itunes.apple.com/search?term=Squeegee&entity=software&country=us)
  - Instant quoting needs licensed imagery.
- **Mold and water restoration: DEFERRED.** Encircle rates iOS 3.75 (130) [iOS] and now turns field data into Xactimate estimates [Vendor]. [Encircle](https://www.getencircle.com/) Competing requires Verisk/Xactimate-compatible output, which lowers copyability. No Capterra category was retrievable (slug 404).
- **Chimney sweeps, irrigation winterization, Christmas-light installers, elevator inspection, appliance repair, flooring, fence and deck: NOT SCORED.**
  - Searches returned no usable evidence: Bing results were off-topic and Capterra category slugs 404.
  - Fence Cloud exists as a fence-estimating ecosystem claiming heritage "since the 80's" [Vendor], but no revenue proof was found. [Fence Cloud](https://fence.cloud/about)
- **HVAC maintenance-agreement management: KILL (bundled).** The Capterra HVAC category is dominated by full FSM suites: Housecall Pro 4.7 (2,749), Jobber 4.6 (1,490), ServiceTitan 4.3 (342), ServiceTrade 4.6 (345) [Capterra]. [Capterra HVAC](https://www.capterra.com/hvac-software/)

### Inferences
- Bundling of maintenance agreements is inferred from the general feature sets of these suites; it was not verified from each pricing page this round.
- Pool service may still hide a commercial-pool compliance niche: health-department daily chemical logs for hotels, HOAs and gyms. This is unresearched and worth a quick check before fully discarding pool.
- Home inspection's adjacent specialties (Florida 4-point and wind-mitigation insurance inspections, sewer scope, radon) may be served by Spectora's templates. This is unverified.

### Gaps
- No evidence was gathered for chimney, irrigation, holiday lighting, elevator, appliance repair, flooring, or fence and deck niches. They are neither confirmed nor killed on the merits.
- Dumpster, septic and fire-extinguisher NAICS counts need Census CBP with an API key.
- TrustMRR, StarterStory, Reddit and Indie Hackers were not consulted this round, so no Stripe-verified or founder-claimed MRR is included.
