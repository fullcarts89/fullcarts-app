# Dev / IT / MSP / agency / no-code micro-SaaS: "clone and improve" opportunities (as of 2026-11-07)

Provenance labels used throughout:
- **[TMRR]**: TrustMRR startup page. Revenue is read from the payment provider (Stripe, Paddle, Polar, Dodo and others) and synced on 2026-11-07. This is the strongest proof available.
- **[Founder]**: the founder or company says so (open dashboard, blog, AMA). Not audited.
- **[3P-est]**: a third-party estimate (Latka, Prospeo, newsletters, aggregators).
- **[Acq]**: an acquisition is evidence of value; terms are usually undisclosed.
- **[Live]**: vendor pricing page fetched with curl on 2026-11-07.
- **[WP.org]**: WordPress.org plugin API or review pages, fetched 2026-11-07. Relative review dates are converted to approximate months.
- **[Capterra]**: Capterra product page JSON-LD, fetched 2026-11-07.

Method notes: G2, Trustpilot and Reddit returned 403 or bot-challenges to curl. The GitHub API was blocked by the session proxy, so open-source star counts could not be verified. TrustMRR's public API needs a key, so I enumerated its startup sitemap (12,398 startup slugs) instead and scraped about 230 relevant startup pages. Raw files are in `/tmp/claude-0/-home-user-fullcarts-app/26da1d04-da96-596a-8ca0-1065c2a8525f/scratchpad/dev_it_msp/`.

---

## Q1. Where is the verified revenue in this space, and what does it say about beatability?

### Takeaway
Verified developer micro-SaaS revenue clusters in a few places: form backends, image and PDF generation APIs, status and uptime pages, WordPress agency tooling and agency reporting. In each, newcomers or small bootstrapped teams have reached $10k–$110k MRR next to larger incumbents. Orshot went from launch in March 2025 to $12.7k MRR, and Web3Forms reached $44k MRR against Formspree. That is direct evidence that "competition exists" does not mean "unbeatable". The MSP layer has fewer public MRR figures, but shows repeated acquisitions by consolidators (ScalePad bought Backup Radar and Quoter), followed by price floors that leave small MSPs out.

### Cited Findings
- **Web3Forms** (form backend): $44,130 MRR, $47,600 last-30-day revenue, 3,209 active subscriptions, founded Dec 2020, bootstrapped, 95% profit margin last 30 days, estimated 412k users, free tier 250 submissions/mo. [TMRR] — [TrustMRR: Web3Forms](https://trustmrr.com/startup/web3forms)
- **Static Forms**: $1,038 MRR, 133 subscriptions, plans $7.50/mo Pro and $16/mo Agency. Listed for sale at $40,000. [TMRR] — [TrustMRR: Static Forms](https://trustmrr.com/startup/static-forms)
- **FormBold**: $656 MRR, 93 subscriptions. [TMRR] — [TrustMRR: FormBold](https://trustmrr.com/startup/formbold)
- **Orshot** (image/PDF/video template API): $12,657 MRR, 223 subscriptions, founded Mar 2025, MRR growth over the last 30 days +41.7%. Plans $39 / $160 / $349 per month. [TMRR] — [TrustMRR: Orshot](https://trustmrr.com/startup/orshot-com)
- **Image-Charts**: $6,262 MRR, 50 subscriptions, $543,969 lifetime revenue, founded 2017, bootstrapped. [TMRR] — [TrustMRR: Image-Charts](https://trustmrr.com/startup/image-charts)
- **PDFBolt** (PDF API): $2,230 MRR, 62 subscriptions, plans $19 / $79 / $249. [TMRR] — [TrustMRR: PDFBolt](https://trustmrr.com/startup/pdfbolt)
- **Cloud Backup for Podio**: $2,375 MRR, 36 subscriptions, $363,607 lifetime revenue, running since 2014. [TMRR] — [TrustMRR: Cloud Backup for Podio](https://trustmrr.com/startup/cloud-backup-for-podio)
- **Changeflow / Trackly** (website change monitoring, billed through Recurly): $3,268 last-30-day revenue, $380,912 lifetime. [TMRR] — [TrustMRR: Changeflow](https://trustmrr.com/startup/trackly-c-o-changeflow-ltd)
- **Embed Notion Pages**: $1,237 MRR, 95 subscriptions. Listed for sale at $29,900. [TMRR] — [TrustMRR: Embed Notion Pages](https://trustmrr.com/startup/embed-notion-pages)
- **An unnamed no-code tool that "turns Notion into a reliable backend"**: $4,294 MRR, 109 subscriptions. Listed for sale at $85,000. [TMRR] — [TrustMRR listing](https://trustmrr.com/startup/notion-tool-with-3k-mrr-80-margins-6-hrs-week-ops)
- **1Lookup** (phone/email/IP validation API): $253,640 MRR, 728 subscriptions. Listed for sale, asking $10M. [TMRR] — [TrustMRR: 1Lookup](https://trustmrr.com/startup/1lookup)
- **Comp AI** (SOC 2 / ISO automation, open source): $17,886 MRR but $921,748 last-30-day revenue (mostly non-recurring or annual). Its pricing page announces a $34M Series A. [TMRR] — [TrustMRR: Comp AI](https://trustmrr.com/startup/comp-ai); [Comp AI pricing](https://trycomp.ai/pricing)
- **Small monitoring entrants are tiny**: UptimeObserver $135 MRR, Hosted Status Page $118 MRR, Pingbuddy $9, Cronwatch $0, SSLMonit $0. [TMRR] — [UptimeObserver](https://trustmrr.com/startup/uptimeobserver); [Hosted Status Page](https://trustmrr.com/startup/hosted-status-page)
- **WP Umbrella** (WordPress agency maintenance dashboard): $110k MRR (+67% year on year), 5,196 premium users, churn 1–2%. [Founder, 2025 yearly review] — [WP Umbrella 2025 review](https://wp-umbrella.com/blog/2025-yearly-review/)
- **Instatus**: $40K MRR with 1,000+ customers. [3P newsletter, undated] — [Superframeworks: Instatus](https://superframeworks.com/blog/instatus)
- **Hyperping**: about $11K MRR and about 232 customers, Sept 2023. [Founder Baremetrics, via newsletter] — [Indie Hustle](https://indiehustle.beehiiv.com/p/a-monitoring-tool-for-websites-making-11k-mrr)
- **Healthchecks.io**: 652 paying customers and $14,043 MRR (2024 post). [Founder] — [Healthchecks blog](https://blog.healthchecks.io/2024/07/running-one-man-saas-9-years-in/)
- **ScreenshotOne**: about $32K MRR, 1,000+ customers, 9% monthly revenue churn, described as a plateau. [3P case study, undated, 2025–26] — [Superframeworks case study](https://superframeworks.com/case-study/screenshotone)
- **Bannerbear**: about $50K–75K MRR through 2024; the public dashboard now shares only selected metrics. [3P analysis] — [woshipm analysis](https://www.woshipm.com/ai/6343398.html); [Bannerbear Open](https://www.bannerbear.com/open)
- **APITemplate.io + CraftMyPDF** (same founder): $50,000 MRR combined at end of 2024, up from $18,500 a year earlier. [Founder, via aggregator] — [gaps.com document-management](https://gaps.com/document-management/)
- **AgencyAnalytics**: "$20+M in revenue and over 6,500 customers" (company, 2024 report) against a Latka estimate of about $15.7M (July 2025). [Founder / 3P-est] — [AgencyAnalytics 2024 report](https://agencyanalytics.com/company/newsroom/2024-benchmarks-report); [Latka](https://getlatka.com/companies/agencyanalytics)
- **Acquisitions**: ScalePad acquired Backup Radar in Nov 2021 and Quoter on Oct 17, 2023 (terms undisclosed). [Acq] — [ScalePad: Backup Radar](https://www.scalepad.com/news/scalepad-acquires-backup-monitoring-solution-backup-radar); [ScalePad: Quoter](https://www.scalepad.com/news/scalepad-acquires-quoter)

### Inferences
- The best-proven micro-SaaS shapes here are infrastructure-light APIs (forms, images, PDFs) and agency multi-site tools. MSP tools show value through acquisitions rather than public MRR.
- Orshot's ramp and Web3Forms' scale show that low-end and mid-market API buyers switch for price, DX and free tiers, even in crowded markets.
- TrustMRR "for sale" listings (Static Forms, Embed Notion Pages, the Notion backend tool) offer a "buy, then niche down" alternative to building.

### Gaps
- No public MRR for Formspree, Basin, DocRaptor, PDFMonkey, Placid, Cronitor, Memberstack or CookieYes. Formspree's only figure is a modeled estimate (see Candidate 1).
- G2, Trustpilot and Reddit were not fetchable, so dated review quotes come only from WordPress.org and Capterra.

---

## Candidate 1 (SHORTLIST): Agency-grade form backend for Webflow, Framer and static sites, with a HIPAA tier

### Takeaway
Form backends are a proven, very profitable micro-SaaS: Web3Forms makes $44k MRR [TMRR] at 95% margin. Horizontal tools compete on price, so the opening is in **agency** features: multi-client workspaces, client handoff, white-label, AI spam triage. A **HIPAA/BAA tier for healthcare-client sites** is a second opening, because Webflow's native forms should not carry patient data (PHI). Score **21/25**.

### Cited Findings
- **Revenue proof**: Web3Forms $44,130 MRR, 3,209 subscriptions [TMRR] — [TrustMRR](https://trustmrr.com/startup/web3forms). Static Forms $1,038 MRR [TMRR] — [TrustMRR](https://trustmrr.com/startup/static-forms). Formspree estimated at about $513,330/yr with 1–10 employees [3P-est, modeled] — [Prospeo](https://prospeo.io/c/formspree-revenue).
- **Incumbent pricing** [Live]:
  - Formspree: $0 / $15 / $30 / $90 per month, billed monthly — [Formspree plans](https://formspree.io/plans)
  - Basin: $12.50 / $24.17 / $40.83 / $108.33 per month (250 / 1K / 5K+ submissions) — [Basin pricing](https://usebasin.com/pricing)
  - Getform, now rebranded "Forminit": $16/mo (5K submissions) and $50/mo (50K), billed yearly — [Forminit pricing](https://getform.io/pricing)
  - Formcarry: $5/mo (500 submissions) and $15/mo (2,000) — [Formcarry pricing](https://formcarry.com/pricing)
  - HIPAAtizer (HIPAA forms, Webflow app): $29–$125/mo — [HIPAAtizer pricing](https://hipaatizer.com/pricing); [Webflow app listing](https://webflow.com/apps/detail/hipaatizer---forms)
- **Platform gaps**:
  - Webflow's free Starter plan has a 50 *lifetime* submission cap — [Webflow help: form submissions](https://help.webflow.com/hc/en-us/articles/33961344521235)
  - Webflow forum guidance is that native form processing should not carry PHI; use a third-party HIPAA processor — [Webflow forum](https://discourse.webflow.com/t/new-lead-captures-via-forms-and-hipaa-compliance-with-webflow/160523)
- **Market**: about 822,550 live Webflow sites (BuiltWith count cited secondhand, April 2026) — [TechnologyChecker](https://technologychecker.io/compare/webflow-vs-framer); [Flow Ninja](https://flowninja.com/blog/framer-vs-webflow). Framer counts conflict: 58,661 to 170,000+ — same sources.
- **Entrants**: dozens of new form backends on TrustMRR (FormsFort "for static sites, Webflow, Framer, WordPress… and agencies", FormHush, Ikiform, nForms) are at $0 MRR. Launching is easy; distribution is the hard part. [TMRR] — [FormsFort](https://trustmrr.com/startup/formsfort); [FormHush](https://trustmrr.com/startup/formhush)

### Inferences
- **Beatability (3/5)**: the low end is cheap and crowded, so a horizontal clone loses. Two gaps are underserved:
  - Agency operations: one dashboard across 40–100 client sites, per-client routing and branding, client-owned billing transfer.
  - Regulated verticals: med-spa, dental, therapy and home-health sites built by agencies on Webflow or Framer, where today's choice is HIPAAtizer or expensive form builders.
- **Spin**: "Form backend for agencies", with a per-client inbox and spam AI, plus a HIPAA add-on: BAA, encrypted-at-rest storage, PHI-safe email notifications that link to the portal instead of carrying data.
- **MVP (4–8 weeks)**: HTML endpoint, honeypot + AI spam filter, multi-workspace agency panel, webhooks / Zapier / Sheets, file uploads, white-label notification emails. The HIPAA tier follows (BAA with AWS; audit logging).
- **Infra cost**: cents per customer for email and storage. The HIPAA tier adds compliance overhead (a BAA-covered email provider, logging).
- **Expansion**: e-sign and intake forms; form → PDF; CRM routing; per-client billing for agencies; Framer and Webflow marketplace apps; lead-quality analytics.
- **Channel**: SEO ("contact form API", "Webflow form backend", "HIPAA Webflow form"), Webflow and Framer app marketplaces, X build-in-public (Web3Forms' founder has about 10k X followers per TrustMRR).
- **Score**: revenue proof 5 / beatability 3 / copyability 5 / expansion 4 / channel 4 = **21/25**.

### Gaps
- Could not verify current Webflow paid-plan submission limits, or whether Formspree, Basin or Forminit sign BAAs.

---

## Candidate 2 (SHORTLIST): CMS-native social/OG image and document generation for agencies and no-code builders (Orshot / Bannerbear model)

### Takeaway
Template-to-image APIs are proven. Bannerbear did about $50–75k MRR through 2024 [3P], Orshot reached $12.7k MRR within about 20 months [TMRR], and Image-Charts makes $6.3k MRR [TMRR]. A newcomer can still win by owning a workflow: Webflow, Framer or Notion CMS items turned automatically into OG images, social posts and PDFs. Score **20/25**.

### Cited Findings
- **Revenue**:
  - Orshot $12,657 MRR, +41.7% MRR in 30 days, founded Mar 2025 [TMRR] — [TrustMRR](https://trustmrr.com/startup/orshot-com)
  - Image-Charts $6,262 MRR [TMRR] — [TrustMRR](https://trustmrr.com/startup/image-charts)
  - Bannerbear at roughly $50–75K MRR through 2024 [3P] — [woshipm](https://www.woshipm.com/ai/6343398.html); its earlier "$53,000 MRR" peak is reported in [Superframeworks](https://superframeworks.com/blog/bannerbear)
- **Pricing** [Live]:
  - Bannerbear $49 / $149 / $299 per month — [Bannerbear pricing](https://www.bannerbear.com/pricing/)
  - Orshot $39 / $160 / $349 per month — [Orshot pricing](https://orshot.com/pricing)
  - Image-Charts $89–99 and $224–249 per month — [Image-Charts pricing](https://www.image-charts.com/pricing)
- **Entrants that failed**: "OG Image API" and "OG Image API LLC" (both founded Dec 2025) show $0 revenue. [TMRR] — [TrustMRR: OG Image API](https://trustmrr.com/startup/og-image-api)

### Inferences
- **Beatability (3/5)**: incumbents are healthy, but horizontal. Bannerbear's entry tier is $49/mo, and Orshot's growth shows buyers will move to a better template editor and integrations. A bare "OG image API" with no workflow wedge gets no revenue (TrustMRR $0 entrants).
- **Spin**: a Webflow and Framer CMS plugin that generates OG and social images (and later PDFs) for every CMS item on publish, with agency multi-site licensing. Possible vertical variants: real-estate listing graphics, event or speaker cards.
- **MVP (6–10 weeks)**: template editor (Satori/resvg or headless Chrome), REST API, Webflow CMS webhook sync, Framer plugin, Zapier/Make app.
- **Infra**: rendering compute is cheap with Satori; video is costly, so defer it.
- **Expansion**: PDF output, short video, auto-posting (Orshot already sells $12/mo per social account), white-label for agencies.
- **Channel**: marketplaces (Webflow, Framer, Zapier), SEO template galleries, X build-in-public.
- **Score**: 5 / 3 / 4 / 4 / 4 = **20/25**.

### Gaps
- Current Bannerbear MRR is not public. Placid's pricing page rendered client-side, so no prices were extracted.

---

## Candidate 3 (SHORTLIST): "Care-plan dashboard" for Webflow, Framer and Shopify agencies (a non-WordPress WP Umbrella)

### Takeaway
WP Umbrella shows that agency site-care tooling can reach **$110k MRR** [Founder] at about €2 per site. In WordPress, though, WP Umbrella is modern, well-rated and cheap, so a horizontal WordPress clone is killed. The beatable gap is agencies on **Webflow (about 822k live sites) and Framer**, which have no plugin-update chore but still sell monthly care plans. They need uptime, SSL and domain expiry, form-delivery tests, broken links, Core Web Vitals, accessibility and visual-diff checks, plus a client report and billing. Score **20/25**.

### Cited Findings
- **Revenue proof (WordPress analog)**: WP Umbrella $110k MRR, 5,196 premium users, 1–2% churn [Founder] — [WP Umbrella 2025 review](https://wp-umbrella.com/blog/2025-yearly-review/). Pricing from €1.99/site/mo [Live] — [WP Umbrella pricing](https://wp-umbrella.com/pricing/).
- **WordPress incumbents** [WP.org]:
  - WP Umbrella plugin: 90k installs, 4.8/5 (81 ratings) — [wp-health plugin](https://wordpress.org/plugins/wp-health/)
  - MainWP Dashboard: 20k installs, 4.9/5 (2,354); MainWP Child: 700k installs — [MainWP](https://wordpress.org/plugins/mainwp/)
  - ManageWP Worker: 1M+ installs, 4.6/5 (680) — [ManageWP Worker](https://wordpress.org/plugins/worker/)
- **ManageWP decline signals**:
  - Recent WP.org review titles: "Customer Support & Site Connection Horrible" (about Nov 2026), "They Were Trusted Partners, and Now They Aren't" (about Oct 2025), "No more updates to a buggy app" (about Feb 2025) — [WP.org ManageWP 1-star reviews](https://wordpress.org/support/plugin/worker/reviews/?filter=1)
  - Capterra 4.7 (23 reviews), including a 1-star titled "ManageWP has Lost the Plot — Clients Looking for Friendlier Services" — [Capterra ManageWP](https://www.capterra.com/p/210350/ManageWP/reviews/)
  - A Capterra reviewer says performance "noticeably dropped" after the GoDaddy acquisition (via search summary) — [Capterra ManageWP](https://www.capterra.com/p/210350/ManageWP/reviews/)
- **Non-WordPress entrants**: WP Admin Online (Apr 2026, $0) and WPBulkify ($54 lifetime) are still WordPress-only. [TMRR] — [WP Admin Online](https://trustmrr.com/startup/wpadmin-online); [WPBulkify](https://trustmrr.com/startup/wpbulkify)
- **Market size**: about 822,550 live Webflow sites, BuiltWith via secondary source, April 2026 — [TechnologyChecker](https://technologychecker.io/compare/webflow-vs-framer)

### Inferences
- **Beatability (4/5)**: I found no Webflow/Framer-native care-plan product in this session's searches (not exhaustively verified). Agencies currently stitch together UptimeRobot, a screenshot tool, Lighthouse and manual reports.
- **MVP (8–12 weeks)**:
  - Add a site by URL plus a Webflow API token.
  - Checks: uptime, SSL, domain WHOIS expiry, a synthetic form-submit test, broken links, Lighthouse/CWV, an axe-core accessibility scan, weekly visual-diff screenshots.
  - Automated monthly white-label PDF report; Stripe care-plan billing to clients.
- **Infra**: headless Chrome for screenshots and Lighthouse costs cents per site per month. Watch the crawl budget.
- **Expansion**:
  - Add WordPress and Shopify (multi-CMS), so the agency moves its whole book.
  - Upsell compliance modules: cookie banner checks, WCAG reports (Candidates 11–12).
  - Webflow CMS backups (Candidate 7). Reseller and white-label tier.
- **Channel**: Webflow and Framer expert/partner communities, the agency SEO term "Webflow maintenance plan", templates for care-plan pricing, partnerships with Webflow template sellers.
- **Score**: 4 / 4 / 4 / 5 / 3 = **20/25**.

### Gaps
- No public count of Webflow or Framer agencies. Webflow Experts directory size not fetched.

---

## Candidate 4 (SHORTLIST): Backup-monitoring and reporting for small MSPs (under 30 clients)

### Takeaway
Backup Radar (now ScalePad) is the category reference, but its **30-client minimum and $495 onboarding** set a floor of about $240/mo before onboarding. That shuts out the long tail of 1–3 technician MSPs. The core is backup-job email and API parsing plus "missing result" detection and PSA ticketing, which a solo founder can copy. Score **18/25**.

### Cited Findings
- **Pricing** [Live]: "$8/client … Pricing is per-client, 30 client minimum. Onboarding is $495." — [Backup Radar pricing](https://www.backupradar.com/pricing). Capterra lists a "$129" starting price (unit unspecified) — [Capterra Backup Radar](https://www.capterra.com/p/184033/ScalePad-Backup-Radar/).
- **Acquisition** [Acq]: ScalePad acquired Backup Radar in Nov 2021 — [ScalePad news](https://www.scalepad.com/news/scalepad-acquires-backup-monitoring-solution-backup-radar)
- **Integration breadth**: monitors 300+ backup applications and integrates with ConnectWise Manage (search summary of ScalePad / TrustRadius listings) — [TrustRadius](https://www.trustradius.com/compare-products/backup-radar)
- **Alternatives exist but are thin**:
  - Alert Centric (Invarosoft), email-parsing-first; ScalePad says it lacks PSA integrations — [ScalePad vs Alert Centric](https://www.scalepad.com/backup-radar/vs-alert-centric)
  - Bocada Cloud, pay-as-you-go with a free starting option — [Bocada](https://insights.bocada.com/backup-radar-alternative)
  - CheckCentral — [ScalePad vs CheckCentral](https://www.scalepad.com/backup-radar/vs-checkcentral)
- **Market size**:
  - "Over 25,000 managed service providers headquartered in the United States" [3P-est, vendor page, undated] — [GTM.ai](https://gtm.ai/content/marketplace/msps-in-the-united-states.md)
  - Provider count shrinking amid consolidation (Sept 2025) — [Business of Tech](https://businessof.tech/2025/09/04/msp-market-expands-to-500b-as-provider-count-shrinks-amid-rapid-consolidation/)

### Inferences
- **Beatability (4/5)**: the minimum and onboarding fee are an explicit gap. ScalePad's bundle strategy pulls Backup Radar toward larger MSPs.
- **Spin**: "Backup Radar for 1–30 clients". Free for 5 clients, $3–5 per client after that, no minimum, self-serve onboarding.
- **MVP (6–10 weeks)**:
  - Inbound email parser for the top 10–15 backup products (Veeam, Datto, Acronis, Cove, MSP360, Synology, M365 backup tools).
  - Missed-job detection; daily dashboard.
  - Ticket creation in HaloPSA, Autotask and ConnectWise; monthly client "backup health" PDF.
- **Infra**: trivial (email ingestion plus a database).
- **Expansion**: patch, AV and EDR status; M365 backup coverage; QBR packs; a client-facing status portal; move upmarket against ScalePad.
- **Channel**: r/msp, MSP Discords and MSPGeek, PSA marketplaces (HaloPSA is popular with small MSPs), comparison SEO ("Backup Radar alternative").
- **Score**: revenue 3 (acquisition plus pricing evidence, no MRR) / beatability 4 / copyability 4 / expansion 4 / channel 3 = **18/25**.

### Gaps
- No public revenue for Backup Radar or its alternatives. Alert Centric and CheckCentral pricing not retrieved. No authoritative count of US MSPs (the 25k figure is a vendor estimate; a Census NAICS 541513 count was not retrieved).

---

## Candidate 5 (SHORTLIST): Per-client status pages plus uptime for MSPs and agencies

### Takeaway
Status pages make money: Instatus about $40k MRR and Hyperping about $11k MRR (2023) [3P/Founder]. Uptime incumbents have broken trust. UptimeRobot restricted its free plan to non-commercial use in late 2024 and retired legacy plans in 2025, and sources conflict on a 2026 reversal. An MSP-specific multi-tenant player exists (IncidentHub Multi-Client, $35–90/mo), but it is small and nothing dominates. Score **18/25**.

### Cited Findings
- **Revenue**:
  - Instatus $40K MRR, 1,000+ customers [3P] — [Superframeworks](https://superframeworks.com/blog/instatus)
  - Hyperping about $11K MRR, Sept 2023 [Founder] — [Indie Hustle](https://indiehustle.beehiiv.com/p/a-monitoring-tool-for-websites-making-11k-mrr)
  - Healthchecks.io $14,043 MRR in 2024 [Founder] — [Healthchecks blog](https://blog.healthchecks.io/2024/07/running-one-man-saas-9-years-in/)
- **Pricing** [Live]:
  - Atlassian Statuspage $29 / $99 / $399 / $1,499 per month (plus $79 / $249 / $599 tiers) — [Statuspage pricing](https://www.atlassian.com/software/statuspage/pricing)
  - Hyperping $24 / $74 / $249 per month — [Hyperping pricing](https://hyperping.com/pricing)
  - Instatus Pro from $20/mo — [Instatus pricing](https://instatus.com/pricing)
  - UptimeRobot $13 / $39 / $83 per month (monthly billing) — [UptimeRobot pricing](https://uptimerobot.com/pricing/)
  - IncidentHub $35 / $60 / $75 / $90 per month, with a "Multi-Client: For MSPs and agencies managing multiple clients" plan — [IncidentHub pricing](https://incidenthub.cloud/pricing)
- **MSP incumbents**:
  - IncidentHub: up to 50 per-client public status pages including tenant-specific M365 and Azure health; "Trusted by 600+ teams" — [IncidentHub MSPs](https://incidenthub.cloud/use-cases/msps)
  - StatusGator markets an MSP white-label use case — [StatusGator MSP](https://statusgator.com/use-cases/managed-service-providers)
- **Beatability evidence**:
  - UptimeRobot limited its free tier to personal, non-commercial use in late 2024 with little notice; false alerts reported in August 2025 — [Notifier](https://notifier.so/guides/uptimerobot-alternative/); [Velprove](https://velprove.com/blog/uptimerobot-commercial-alternative)
  - Sources conflict on whether commercial use was re-allowed in May 2026 (search summary; see Gaps).

### Inferences
- **Beatability (3/5)**: the horizontal market is crowded (Better Stack, Hyperping, Instatus, OnlineOrNot). The **MSP** sub-niche has only small specialists (IncidentHub, StatusGator).
- **Spin**:
  - One account; a branded status page per client showing that client's own monitors, their SaaS vendors, and M365 tenant health.
  - PSA ticket auto-creation; QBR-ready uptime reports.
  - Priced per client ($2–3) instead of per page.
- **MVP (6–8 weeks)**: HTTP, ping and SSL checks; per-client pages on custom domains; vendor-status scraping for the top 50 SaaS; Microsoft 365 Service Health via Graph API; email/SMS/Teams alerts.
- **Infra**: multi-region checkers are low-cost (roughly $50–200/mo total at small scale).
- **Expansion**: domain/SSL expiry, backup monitoring (bundle with Candidate 4), client portal, reseller white-label.
- **Channel**: r/msp, MSP Facebook groups and Discords, PSA marketplaces, "Statuspage alternative for MSPs" SEO.
- **Score**: 4 / 3 / 4 / 4 / 3 = **18/25**.

### Gaps
- IncidentHub's revenue is unknown. I could not resolve whether UptimeRobot's current terms allow commercial use on the free plan.

---

## Candidate 6 (SHORTLIST): Client-reporting dashboard for a vertical agency segment (e.g. home-services / local-SEO agencies)

### Takeaway
Agency reporting is a large, proven category. AgencyAnalytics claims $20M+ revenue and 7,000+ agency customers. But per-client pricing ($20/client/mo since about May 2025, per third parties) and Whatagraph's move upmarket (from €699/mo) leave room for flat-priced, vertical-specific reporting. The leader is well rated (Capterra 4.8, 116 reviews), so the attack has to be vertical, not horizontal. Score **18/25**.

### Cited Findings
- **Revenue**:
  - AgencyAnalytics "$20+M in revenue and over 6,500 customers" [Founder, 2024] — [AgencyAnalytics report](https://agencyanalytics.com/company/newsroom/2024-benchmarks-report)
  - "More than 7,000 agency customers" (2026) — [AgencyAnalytics newsroom](https://agencyanalytics.com/company/newsroom/agencyanalytics-top-growing-companies-2026)
  - Latka estimate about $15.7M [3P-est] — [Latka](https://getlatka.com/companies/agencyanalytics)
- **Pricing** [Live]:
  - AgencyAnalytics "$20 per client, per month" — [AgencyAnalytics pricing](https://agencyanalytics.com/pricing)
  - DashThis $44 / $139 / $279 per month — [DashThis pricing](https://dashthis.com/pricing/)
  - Whatagraph "Max from €699 per month, billed annually" — [Whatagraph pricing](https://whatagraph.com/pricing)
- **Price-change evidence**:
  - The vendor FAQ says it runs smaller periodic increases that apply to the per-client price — [AgencyAnalytics FAQ](https://help.agencyanalytics.com/en/articles/12277276-pricing-update-faq)
  - A competitor claims the May 2025 move to $20/client left a 50-client agency paying over $1,000/mo [3P, competitor] — [Swydo](https://www.swydo.com/blog/agencyanalytics-pricing/)
- **Ratings** [Capterra]: AgencyAnalytics 4.8 (116 reviews) — [Capterra](https://www.capterra.com/p/158746/Agency-Analytics/reviews/)

### Inferences
- **Beatability (3/5)**: the incumbent is loved, so beat it on fit and price shape:
  - A home-services agency dashboard combining Google Business Profile, Local Services Ads, call tracking (e.g. CallRail) and booked-job revenue from field-service software.
  - Flat pricing per agency tier rather than per client.
- **MVP (8–12 weeks)**: connectors for GA4, Google Ads, GBP and LSA, call tracking, one field-service CRM; white-label PDF/email reports. Google Ads developer-token approval is a gating step.
- **Infra**: API sync jobs, low cost. Connector maintenance is the real cost.
- **Expansion**: adjacent verticals (dental/legal marketing agencies), proposal and audit tools, client portal, AI commentary.
- **Channel**: niche agency communities and podcasts, partner integrations, SEO on "[vertical] marketing report template".
- **Score**: 5 / 3 / 3 / 4 / 3 = **18/25**.

### Gaps
- No independent dated user quotes on the AgencyAnalytics price change (G2 and Reddit blocked). Third-party price claims come from competitors.

---

## Candidate 7 (SHORTLIST): SaaS backup for no-code platforms (Airtable / Notion / Webflow CMS / Podio-style)

### Takeaway
Small but durable. Cloud Backup for Podio has run since 2014 at $2.4k MRR and $364k lifetime [TMRR]. NotionBackups reports about $2.2k MRR with 200+ customers [Founder]. Competition is thin and the product is easy to copy. Expansion comes from covering many platforms with one agency or compliance plan. Score **18/25**.

### Cited Findings
- **Revenue**:
  - Cloud Backup for Podio $2,375 MRR, 36 subscriptions, $363,607 lifetime [TMRR] — [TrustMRR](https://trustmrr.com/startup/cloud-backup-for-podio)
  - NotionBackups $2.2K MRR, 200+ customers, about 3 years in (Jan 2025) [Founder] — [Indieniche](https://indieniche.substack.com/p/what-happens-when-notion-fails-this)
- **Pricing**:
  - NotionBackups $6 / $11 / $28 / $89 per month [Live] — [NotionBackups](https://notionbackups.com/)
  - BackupLABS listed from $5/mo for 5 Trello boards (search-result snippet) — [G2 BackupLABS](https://www.g2.com/products/backuplabs/reviews)

### Inferences
- **Beatability (4/5)**: few focused competitors per platform. Native platform features (for example Airtable snapshots) are the main risk; not verified this session.
- **Spin**: "Agency backup for client no-code stacks". Webflow CMS, Airtable and Notion in one dashboard, with restore-to-new-base, retention policies and audit exports.
- **MVP (4–6 weeks per platform)**: API export, encrypted S3, scheduled jobs, diff/restore, email reports.
- **Infra**: storage dominates, at cents per customer.
- **Expansion**: platform count (monday, ClickUp, HubSpot), compliance retention, agency white-label.
- **Channel**: platform marketplaces and communities, SEO on "[platform] backup".
- **Score**: 3 / 4 / 5 / 3 / 3 = **18/25**.

### Gaps
- No revenue data for Airtable-specific backup tools (On2Air, etc.). Webflow CMS backup competitors not researched.

---

## Candidate 8 (SHORTLIST): Quoting / CPQ-lite for micro-MSPs and IT VARs

### Takeaway
Quoter was acquired by ScalePad (Oct 2023) and is well rated (Capterra 4.6, 54 reviews). Its live entry price is **$299/mo for 75 quotes**, rising to $599/mo, which is steep for 1–3 person MSPs. Copying it needs distributor catalog integrations (Pax8, Ingram, TD SYNNEX), which adds integration and partnership work. Score **17/25**.

### Cited Findings
- **Pricing** [Live]: Quoter $299/mo (75 quotes), $449/mo (150), $599/mo (250) — [Quoter pricing](https://www.quoter.com/pricing)
- **Acquisition** [Acq]: ScalePad acquired Quoter, announced Oct 17, 2023; Quoter co-founded 2018 — [ScalePad](https://www.scalepad.com/news/scalepad-acquires-quoter)
- **Ratings** [Capterra]:
  - Quoter 4.6 (54) — [Capterra Quoter](https://www.capterra.com/p/117768/Socket/)
  - QuoteWerks 4.6 (192), Capterra UK — [Capterra UK alternatives](https://www.capterra.co.uk/alternatives/117768/socket)
  - ITQuoter from A$59.9/mo flat, 8 reviews — [Capterra ITQuoter](https://www.capterra.com/p/145129/ITQuoter/)

### Inferences
- **Beatability (3/5)**: the price floor and the consolidator bundle create a gap at the bottom. Alternatives exist (ITQuoter, QuoteWerks, Zomentum), but they are older or less MSP-native.
- **Spin**: "Quoter for solo MSPs". $49–99/mo with unlimited quotes, Pax8 plus Amazon Business catalogs, recurring-service bundles, e-sign plus Stripe deposit, and sync to HaloPSA, Autotask and QuickBooks.
- **MVP (8–12 weeks)**: catalog import, quote builder, e-sign, payments, PSA/accounting push. Distributor API access may require partner agreements.
- **Expansion**: contracts and renewals, procurement, other tech integrators (AV, security, low-voltage).
- **Channel**: r/msp, HaloPSA marketplace, MSP peer groups, "Quoter alternative" SEO.
- **Score**: 4 / 3 / 3 / 4 / 3 = **17/25**.

### Gaps
- No Quoter revenue data. Distributor API terms not checked.

---

## Candidate 9 (SHORTLIST): Vertical website-change monitoring (competitor pricing pages, vendor ToS/regulatory pages)

### Takeaway
Change monitoring is proven but horizontal. Visualping is estimated at $0.68–0.86M revenue on $8M+ funding [3P-est]. Changeflow has earned about $381k lifetime and takes about $3.3k per month [TMRR]. Open-source changedetection.io covers developers. The opportunity is a vertical, compliance- or GTM-specific workflow. Score **17/25**.

### Cited Findings
- **Revenue**:
  - Visualping $678.9K 2023 revenue (another Latka page says $858.8K); 1.5M customers claimed [3P-est] — [Latka Visualping](https://getlatka.com/companies/visualping)
  - Visualping funding $8M over 2 rounds — [Seedtable](https://seedtable.com/startups/Visualping-R99E6JX)
  - Changeflow $3,268 last 30 days, $380,912 lifetime [TMRR] — [TrustMRR](https://trustmrr.com/startup/trackly-c-o-changeflow-ltd)
- **Pricing** [Live]:
  - Visualping $14–$350/mo (Personal 1K up to Business 50K checks) — [Visualping pricing](https://visualping.io/pricing)
  - Changeflow $99/mo and $249/mo, billed annually, plus $180/user/yr extra seats — [Changeflow pricing](https://changeflow.com/pricing)
  - Distill $15 / $35 / $80+ per month — [Distill pricing](https://distill.io/pricing/)

### Inferences
- **Beatability (3/5)**: incumbents sell generic "watch a URL". A product that understands a domain wins on signal-to-noise. Two examples:
  - SaaS competitor pricing and packaging diffs, with structured price extraction.
  - Vendor terms, DPA and subprocessor-list changes for privacy and compliance teams (ties to SOC 2 vendor management).
- **MVP (6–8 weeks)**: headless fetch, semantic diff with an LLM summary, structured extraction, Slack/email digests.
- **Infra**: crawl compute is modest; LLM summaries cost per check.
- **Score**: 4 / 3 / 4 / 3 / 3 = **17/25**.

### Gaps
- Distill.io revenue not found; the results confused it with unrelated companies.

---

## Candidate 10 (SHORTLIST, lower): PDF generation for no-code builders / vertical documents

### Takeaway
Revenue is well proven: APITemplate.io and CraftMyPDF together made $50k MRR at end of 2024 [Founder], and PDFBolt makes $2.2k MRR [TMRR]. But the developer-horizontal segment is crowded, and open-source defaults such as Gotenberg are free (star count unverified). Only a no-code or vertical wedge is viable. Score **16/25**.

### Cited Findings
- **Revenue**: APITemplate.io + CraftMyPDF $50,000 MRR at end of 2024 [Founder via aggregator] — [gaps.com](https://gaps.com/document-management/). PDFBolt $2,230 MRR [TMRR] — [TrustMRR](https://trustmrr.com/startup/pdfbolt).
- **Pricing** [Live]:
  - DocRaptor $15 / $29 / $75 / $149 / $399 / $1,000 per month — [DocRaptor](https://docraptor.com/signup)
  - PDFMonkey €0–€300/mo — [PDFMonkey pricing](https://pdfmonkey.io/pricing)
  - CraftMyPDF $29 / $49 / $99 / $299 / $499 per month — [CraftMyPDF pricing](https://craftmypdf.com/pricing/)
- **Entrants**: "pdfs.build" (Apr 2026) $205 MRR; Peedief $55 MRR. [TMRR] — [pdfs.build](https://trustmrr.com/startup/pdfs-build); [Peedief](https://trustmrr.com/startup/peedief-pdf-generation-for-ai-workflows)

### Inferences
- **Beatability (2/5)**: plenty of cheap, modern options. Spin only if paired with a vertical document workflow, for example MSP QBR reports or inspection reports via Bubble, Glide or Softr plugins.
- **Score**: 4 / 2 / 4 / 3 / 3 = **16/25**.

### Gaps
- Gotenberg / open-source adoption could not be quantified (GitHub API blocked).

---

## Candidate 11 (SHORTLIST, lower): WCAG/ADA monitoring for small public entities and their web vendors

### Takeaway
There is real regulatory demand. The DOJ ADA Title II rule (WCAG 2.1 AA) now applies from April 2027 for entities with populations of 50,000+ and April 2028 for smaller ones. Overlays are discredited: the FTC's final order against accessiBe came in April 2025. Pope Tech is the main well-priced scanner, so the wedge must be gov-specific: PDF agendas and minutes, VPAT and accessibility statements, vendor reports. Procurement makes the sales channel slow. Score **16/25**.

### Cited Findings
- **Deadlines**:
  - DOJ interim final rule (Apr 20, 2026) moved compliance for entities serving 50,000+ people from Apr 24, 2026 to about Apr 26, 2027; smaller entities to 2028. Scope and the WCAG 2.1 AA standard are unchanged — [Duane Morris](https://www.duanemorris.com/alerts/doj_extends_ada_title_ii_digital_accessibility_deadlines_one_year_0426.html); [Plante Moran](https://plantemoran.com/explore-our-thinking/insight/2026/04/doj-extends-ada-title-ii-web-accessibility-compliance-deadlines)
  - One source says the extension is being challenged in court (unverified detail) — same search set
- **Overlay discrediting / market size**:
  - FTC $1M order against accessiBe (proposed Jan 3, 2025; final Apr 22, 2025) — [TechCrunch](https://techcrunch.com/2025/01/03/ftc-orders-ai-accessibility-startup-accessibe-to-pay-1m-for-misleading-advertising); [Data Privacy + Security Insider](https://www.dataprivacyandsecurityinsider.com/2025/04/ftc-settles-with-accessibe-for-misleading-statements-about-wcag-compliance/)
  - A commentator cites reported accessiBe 2024 revenue of $51.3M [3P] — [Adrian Roselli](https://adrianroselli.com/2025/01/ftc-catches-up-to-accessibe.html)
- **Weak WordPress incumbents** [WP.org]:
  - "Web Accessibility (formerly Ally)" by Elementor: 500k+ installs, **2.9/5** (163 ratings) — [plugin page](https://wordpress.org/plugins/pojo-accessibility/)
  - Recent 1-star titles: "Unusable bloatware. Replaced on every site I manage" (about Aug 2026), "Crashed my website" (about Mar 2026) — [WP.org reviews](https://wordpress.org/support/plugin/pojo-accessibility/reviews/?filter=1)
  - accessiBe plugin: 10k installs, 4.1/5 (32) — [plugin page](https://wordpress.org/plugins/accessibe/)
  - UserWay: 80k installs, 4.0/5 (57), last updated Dec 2025 — [plugin page](https://wordpress.org/plugins/userway-accessibility-widget/)
- **Pope Tech pricing** [Live]: Free (25 pages), $25/mo ($30 monthly), $225/mo ($270 monthly), $400/mo, with unlimited users and websites — [Pope Tech pricing](https://pope.tech/pricing/)
- **Small entrants** [TMRR]:
  - ADAWCAG: $1,344 MRR, fixed-price audits from $497 — [TrustMRR](https://trustmrr.com/startup/adawcag)
  - PageAudit ("continuous WCAG compliance monitoring for web agencies"): $0 — [TrustMRR](https://trustmrr.com/startup/pageaudit-by-appforgelabs)

### Inferences
- **Beatability (3/5)**: overlays are on the defensive. Pope Tech is well priced and strong in higher ed, so differentiate on government PDF and document accessibility and on vendor/agency multi-client reporting.
- **MVP (8–12 weeks)**: crawler plus axe-core; PDF tag and structure checks; issue tracker; conformance report and accessibility-statement generator; agency multi-client view.
- **Expansion**: AI-assisted PDF remediation (a services-plus-software margin play), the HHS Section 504 deadline for healthcare, state laws.
- **Channel (2/5)**: government buyers are slow. Sell through the agencies and CMS vendors that build municipal sites.
- **Score**: 3 / 3 / 4 / 4 / 2 = **16/25**.

### Gaps
- Number of US local governments and special districts not retrieved this session. AudioEye and Siteimprove pricing not fetched.

---

## Candidate 12 (SHORTLIST, lowest): Cookie consent plus US-state privacy (GPC) for multi-site agencies on non-WordPress builders

### Takeaway
Demand rises with US state laws (about 20 in effect and 24 enacted as of Oct 2026). CookieYes moving free features behind a paywall in early 2026 caused visible backlash, and Termly's plugin rates poorly. But CookieYes and Complianz remain dominant and well rated, and CookieYes already runs an agency partner program. Viable only bundled into Candidate 3, or aimed at Webflow/Framer agencies. Score **15/25**.

### Cited Findings
- **Laws**:
  - MultiState: 24 states with comprehensive privacy laws (Oct 28, 2026), including ones not yet effective — [MultiState](https://www.multistate.us/insider/2026/10/28/twenty-four-states-now-have-comprehensive-consumer-privacy-laws)
  - About 20 in effect as of Aug 2026 (vendor tracker) — [Enzuzo](https://www.enzuzo.com/blog/us-state-privacy-laws)
- **Incumbents** [WP.org]:
  - CookieYes: 1M+ installs, 4.8/5 (3,236 ratings) — [plugin](https://wordpress.org/plugins/cookie-law-info/)
  - Complianz: 1M+ installs, 4.7/5 (1,668) — [plugin](https://wordpress.org/plugins/complianz-gdpr/)
  - Cookiebot: 100k installs, 4.4/5 (440) — [plugin](https://wordpress.org/plugins/cookiebot/)
  - iubenda: 200k installs, 4.7/5 (398) — [plugin](https://wordpress.org/plugins/iubenda-cookie-law-solution/)
  - Termly: 80k installs, **3.6/5** (205) — [plugin](https://wordpress.org/plugins/uk-cookie-consent/)
- **Backlash** [WP.org]:
  - CookieYes 1-star titles: "DON'T USE IT, free tier is basically useless now" and "Making existing free features paid is the end for me" (about Feb 2026), "Remove feature every update to make it premium" (about Apr 2026) — [CookieYes reviews](https://wordpress.org/support/plugin/cookie-law-info/reviews/?filter=1)
  - Termly titles: "Bad value for money" (about Nov 2026), "Worst support, SEO mess up, for highest price!" (about Mar 2026) — [Termly reviews](https://wordpress.org/support/plugin/uk-cookie-consent/reviews/?filter=1)
- **Pricing** [Live]:
  - CookieYes $10 / $25 / $55 per month *per domain* plus $0.30 per 1,000 extra pageviews; it also has an "Agency Partner Program" — [CookieYes pricing](https://www.cookieyes.com/pricing/)
  - iubenda from €4–€24 (and $5–$24) per site per month — [iubenda pricing](https://www.iubenda.com/en/pricing)
  - Termly $15–$20 per license — [Termly pricing](https://termly.io/pricing/)

### Inferences
- **Beatability (2/5)**: modern, well-rated, fairly priced leaders dominate WordPress, so this is close to the kill rule. Viable as an add-on module (GPC honoring, US-state opt-out page, consent logs) in an agency site-care product.
- **Score**: 4 / 2 / 4 / 3 / 2 = **15/25**.

### Gaps
- Did not verify whether Webflow or Framer now ship native consent banners, which would bundle this away.

---

## Kill list (evaluated, not shortlisted)

### Takeaway
I evaluated 17 more categories and killed each one. In each, either a modern, fairly priced product or an open-source default already dominates the exact sub-niche, the platform bundles it, VC-funded players compress price, or revenue proof is too weak.

### Cited Findings
- **SOC 2-lite for under-10-person startups**: Comp AI is open source, raised a $34M Series A, and shows $921,748 in last-30-day revenue [TMRR]. Vanta, Drata and Delve also compete. Killed: VC price compression. — [TrustMRR Comp AI](https://trustmrr.com/startup/comp-ai); [Comp AI](https://trycomp.ai/pricing)
- **M365 multi-tenant management for MSPs**: CIPP is "completely free and open-source" and self-hostable; Microsoft 365 Lighthouse is free with the partner tier. Killed: free default. — [CyberDrain FAQ](https://cyberdrain.com/faq/); [Nuoptima](https://nuoptima.com/best-microsoft-365-management-tools-for-msps)
- **IT documentation (IT Glue clone)**:
  - Hudu is the modern, well-priced "beat IT Glue" product: from $44/mo and $27/user [Live]; 4.6 rating on only 5 Capterra reviews — [Hudu pricing](https://www.hudu.com/pricing); [Capterra Hudu](https://www.capterra.com/p/10005281/hudu/)
  - IT Glue is $29–$44/user on 36-month terms [Live]; about 4.6 (about 340 reviews) — [IT Glue pricing](https://www.itglue.com/pricing/); [Capterra compare](https://www.capterra.com/compare/170401-10005281/ITGlue-vs-hudu)
  - Kaseya caps auto-renewal increases at 5% plus inflation — [Kaseya Partner First](https://www.kaseya.com/customer-success/partner-first/)
  - Killed: Hudu occupies the gap.
- **DMARC / email-auth for MSPs**: EasyDMARC has a dedicated MSP program, plus PowerDMARC, Palisade, DMARCReport, Suped and others. Killed: crowded specialists. — [EasyDMARC MSP](https://easydmarc.com/pricing/easydmarc/msp); [Palisade buyer's guide](https://www.palisade.email/compare/best-dmarc-monitoring-tools-for-msps)
- **Cron / heartbeat monitoring**: Healthchecks.io is open source at $0 / $5 / $20 / $80 per month [Live] with $14k MRR [Founder]; Cronitor charges $2 per monitor per month. Killed: fairly priced, open-source default. — [Healthchecks pricing](https://healthchecks.io/pricing/); [Cronitor pricing](https://cronitor.io/pricing)
- **Feature flags**: open-source defaults (GrowthBook, Flagsmith, Unleash) and free tiers. Killed. TrustMRR entrants Flagon and Flagup have no listed revenue. Star counts unverified (GitHub API blocked).
- **API mocking**: Mockoon is the open-source default; Mockerito and MockHero are at $0 [TMRR]. Killed. — [Mockerito](https://trustmrr.com/startup/mockerito)
- **Log management for small teams**: Better Stack (from $29–34 [Live]) and other generous free tiers; infrastructure-heavy. Killed. — [Better Stack pricing](https://betterstack.com/pricing)
- **Transactional email**: deliverability infrastructure and incumbents; Emailit makes only $1,495 MRR [TMRR]. Killed. — [TrustMRR Emailit](https://trustmrr.com/startup/emailit)
- **Email validation**: 1Lookup makes $253,640 MRR [TMRR], but it is commodity, data-cost-driven and in a price war; small entrants are shrinking (EmailChecker $349 MRR; Validemail -48.8% MRR in 30 days). Killed or watch. — [1Lookup](https://trustmrr.com/startup/1lookup); [Validemail](https://trustmrr.com/startup/validemail-co)
- **Waitlist / referral launch tools**: Waitlistz has $9 lifetime revenue [TMRR]; usage is inherently temporary. Killed. — [Waitlistz](https://trustmrr.com/startup/waitlistz)
- **Feedback boards / changelogs (Canny clone)**:
  - Canny's pricing shocks: per-tracked-user billing in May 2025, legacy free plans retired by Dec 15, 2025, a further increase in Feb 2026 — [ProductLift](https://www.productlift.dev/blog/canny-pricing/); [CostBench](https://costbench.com/changelog/canny-price-increase-2026-02/)
  - Cheap modern alternatives already harvest those leavers [Live]: Featurebase $29/seat, UserJot $29 / $59, Frill $25+ — [Featurebase](https://www.featurebase.app/pricing); [UserJot](https://userjot.com/pricing); [Frill](https://frill.co/pricing)
  - Canny Capterra 4.6 (77), including "costly for startups with a lot of free/trial users" — [Capterra Canny](https://www.capterra.com/p/161103/Canny/reviews/)
  - Killed.
- **Screenshot API (horizontal)**: ScreenshotOne has plateaued at about $32K MRR with 9% monthly churn [3P]; Urlbox costs $19–$498/mo [Live]; ScreenshotDEV is listed for sale at $0 revenue [TMRR]. Killed. — [Superframeworks](https://superframeworks.com/case-study/screenshotone); [Urlbox](https://urlbox.com/pricing); [ScreenshotDEV](https://trustmrr.com/startup/screenshotdev-for-sale)
- **SEO crawler / rank tracker / backlink monitor**: crowded. Backlink Checker has $72 MRR [TMRR]; CheckMySEO has $34 MRR [TMRR]. Killed. — [Backlink Checker](https://trustmrr.com/startup/backlink-checker); [CheckMySEO](https://trustmrr.com/startup/checkmyseo-seo-audit)
- **Notion-to-website**:
  - Feather sold for about $250k at about $6k MRR (June 2024) [3P] — [Next Founder](https://nextfounder.substack.com/p/this-guy-made-250k-with-a-notion); [Tibo](https://tibo.beehiiv.com/p/might-lost-250k)
  - Super costs $16–$28/mo [Live] — [Super pricing](https://super.so/pricing)
  - Killed: mature and small. Notion's native Sites feature was not verified this session.
- **Webflow / Framer memberships**:
  - Webflow ended User Accounts on Jan 29, 2026 and named Outseta and Memberstack as recommended partners, so those two absorbed the migration — [Webflow help](https://help.webflow.com/hc/en-us/articles/36046006227731)
  - Outseta revenue grew 55% in 2025 [Founder] — [Outseta 9-year update](https://www.outseta.com/posts/our-saas-start-ups-equity-allocation-expenses-and-growth-after-9-years)
  - Framer already has FrameAuth, Outseta, Thenty and Memberhub plugins — [FrameAuth](https://www.framer.com/community/marketplace/plugins/frameauth/)
  - Killed.
- **Horizontal WordPress maintenance dashboard**: WP Umbrella ($110k MRR, 4.8/5, €1.99/site) dominates. Killed; the non-WordPress spin is Candidate 3. — [WP Umbrella](https://wp-umbrella.com/blog/2025-yearly-review/)
- **Internal-tool builders**: VC and open-source saturated (Retool and others). Killed without deep research.

### Inferences
- The kill rule hit most often where open source is the default (cron, flags, mocking, M365 via CIPP) or where a modern indie product already harvests an incumbent's mistakes (Hudu against IT Glue; Featurebase and UserJot against Canny; WP Umbrella against ManageWP).

### Gaps
- GitHub star counts for the open-source defaults (Healthchecks, Mockoon, CIPP, GrowthBook, Gotenberg, changedetection.io) could not be verified: the GitHub API was blocked by the session proxy.

---

## Ranking summary and channels

### Takeaway
Top picks:
1. Agency/HIPAA form backend: **21**
2. CMS-native image/OG API: **20**
3. Non-WordPress agency care-plan dashboard: **20**

Then backup monitoring for small MSPs, MSP status pages, vertical agency reporting and no-code SaaS backup at **18** each. Candidates 3, 5, 4 and 12 stack into one "agency/MSP site-and-service health" suite, which is the clearest expansion path.

### Cited Findings
- Score table, as /5 each for revenue, beatability, copyability, expansion and channel (my judgments; evidence in the sections above):

| # | Candidate | Rev | Beat | Copy | Exp | Chan | Total | Incumbents' main channel |
|---|---|---|---|---|---|---|---|---|
| 1 | Agency + HIPAA form backend | 5 | 3 | 5 | 4 | 4 | **21** | SEO, X build-in-public, marketplaces |
| 2 | CMS-native OG/social image API | 5 | 3 | 4 | 4 | 4 | **20** | Marketplaces (Zapier/Webflow/Framer), SEO |
| 3 | Webflow/Framer agency care-plan dashboard | 4 | 4 | 4 | 5 | 3 | **20** | Agency communities, SEO, WP.org-style plugin distribution |
| 4 | Backup monitoring, small MSPs | 3 | 4 | 4 | 4 | 3 | **18** | MSP communities, PSA marketplaces |
| 5 | Per-client status pages, MSPs | 4 | 3 | 4 | 4 | 3 | **18** | SEO comparisons, MSP communities |
| 6 | Vertical agency reporting | 5 | 3 | 3 | 4 | 3 | **18** | SEO, partner integrations |
| 7 | No-code SaaS backup | 3 | 4 | 5 | 3 | 3 | **18** | Platform communities, SEO |
| 8 | Micro-MSP quoting | 4 | 3 | 3 | 4 | 3 | **17** | MSP communities, PSA marketplaces |
| 9 | Vertical change monitoring | 4 | 3 | 4 | 3 | 3 | **17** | SEO, Chrome extension (Visualping/Distill) |
| 10 | No-code/vertical PDF generation | 4 | 2 | 4 | 3 | 3 | **16** | SEO, Zapier/Make marketplaces |
| 11 | ADA Title II accessibility monitoring | 3 | 3 | 4 | 4 | 2 | **16** | Gov procurement, agencies |
| 12 | Agency cookie/US-privacy module | 4 | 2 | 4 | 3 | 2 | **15** | WP.org plugin directory |

- **TAM anchors**:
  - About 25,000+ US-headquartered MSPs [vendor estimate] — [GTM.ai](https://gtm.ai/content/marketplace/msps-in-the-united-states.md)
  - About 822,550 live Webflow sites [BuiltWith via secondary source] — [TechnologyChecker](https://technologychecker.io/compare/webflow-vs-framer)
  - 5,000+ agencies on WP Umbrella — [WP Umbrella](https://wp-umbrella.com/blog/2025-yearly-review/)
  - 7,000+ agencies on AgencyAnalytics — [AgencyAnalytics](https://agencyanalytics.com/company/newsroom/agencyanalytics-top-growing-companies-2026)
  - 24 states with privacy laws enacted — [MultiState](https://www.multistate.us/insider/2026/10/28/twenty-four-states-now-have-comprehensive-consumer-privacy-laws)
- **Buy-instead-of-build options listed on TrustMRR** [TMRR]:
  - Static Forms: $1,038 MRR, ask $40k — [link](https://trustmrr.com/startup/static-forms)
  - Embed Notion Pages: $1,237 MRR, ask $29.9k — [link](https://trustmrr.com/startup/embed-notion-pages)
  - Notion-backend tool: $4,294 MRR, ask $85k — [link](https://trustmrr.com/startup/notion-tool-with-3k-mrr-80-margins-6-hrs-week-ops)

### Inferences
- **Suggested sequencing for a solo founder**:
  1. Start with Candidate 1 (fastest MVP, strongest revenue proof), or buy Static Forms and pivot it to the agency/HIPAA angle.
  2. Add the Candidate 3 monitoring modules for the same Webflow/Framer agency buyer.
  3. Port the multi-tenant monitoring core to MSPs (Candidates 4 and 5), where per-client pricing is the norm and acquirers (ScalePad, Kaseya, ConnectWise) provide exit paths.
- MSP channels need community credibility. Plan for r/msp, MSP Discords and PSA marketplace listings rather than paid ads.

### Gaps
- Authoritative MSP count (Census NAICS 541513 / CompTIA) not retrieved. No Framer site count consistent across sources. No verified revenue for IncidentHub, Alert Centric, ITQuoter or Pope Tech.
