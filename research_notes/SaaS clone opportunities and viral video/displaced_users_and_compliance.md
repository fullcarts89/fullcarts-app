# Displaced users and new compliance obligations (2025–2026): SaaS "clone and improve" opportunities for a solo US founder

Research date: 2026-11-06. Scope: US market, plus EU rules only where they bind US sellers.

**Method and limits:**
- About 22 web searches, then the shared WebSearch budget for this session ran out. Everything after that point comes from direct fetches of URLs already found, plus facts sourced in the earlier round's notes (`research_notes/Niche incumbent check for clones/*.md`, also dated 2026-11-06).
- Some kill-list items and two niche-incumbent checks could not be finished. They are flagged in the Gaps sections.

**Provenance labels used throughout:**
- **[official]**: a regulator, government or vendor primary page.
- **[law firm]**: a law or accounting firm alert.
- **[trade press]**: an industry or news outlet.
- **[vendor]**: the vendor's own claims about itself.
- **[vendor/self-promo]**: a post where the author promotes their own product.
- **[secondary]**: an aggregator, listicle or search-summary snippet that was not opened.

Every dollar figure is a list price as published on the date shown, unless labelled otherwise.

---

## Q0 (objective). Which opportunities survive the niche-incumbent check, and which triggers die?

### Takeaway
Only **three** candidates survive, and only one is clean:
1. **DROP request processing for small California data brokers (strong).** It is a legal obligation with per-request daily fines, and the broker-side tools are either enterprise, pre-launch or "coming soon".
2. **Packaging EPR reporting for $1M–$50M DTC brands (provisional).** The obligation is real and new for California from January 2027. The incumbents sell by demo, but the Shopify App Store check failed to load.
3. **IEEPA tariff-refund reconciliation for small importers (time-boxed, marginal).** It is large, but it is a one-off event and brokers and trade-compliance startups are already working it.

Three more stay on a watchlist because their incumbent checks are incomplete: COPPA kits for small kids' app developers; documents for Title II special districts (deadline April 2028); and a narrower 30-day-cadence DROP add-on for other state registries.

The 6–10 shortlist target was **not** met. Most 2025–2026 displacement events were captured quickly by free or sub-$20 tools, or by the platform itself. Several "new obligations" were vacated, vetoed, narrowed or delayed. This matches the previous round's finding that gaps survive only where a regulator or platform makes the job genuinely hard.

### Cited Findings

#### Shortlist #1: DROP processing for small California data brokers. Verdict: SURVIVES (medium-high confidence)

**Trigger (dated)**
- Consumers could file DROP requests from January 2026. A DROP sandbox opened in March 2026. **From Aug 1, 2026, brokers must process DROP requests at least every 45 days. From Jan 1, 2027 (AB 883), they must do so at least every 30 days.** — [CalPrivacy data broker page, official](https://privacy.ca.gov/data-brokers)
- Processing means four steps: download the consumer deletion lists, standardize and hash the broker's own records, match and process, and report each request's status in DROP within 45 days. — [CalPrivacy, official](https://privacy.ca.gov/data-brokers)

**Penalties and costs**
- $200 per day for failing to register, and **$200 per day for each deletion request not fulfilled as required**, plus CalPrivacy's investigation and administrative costs. — [CalPrivacy, official](https://privacy.ca.gov/data-brokers)
- The annual registration fee is **$6,000** for the current year. — [CalPrivacy, official](https://privacy.ca.gov/data-brokers)
- No statutory cure period applies, and the Delete Act gives consumers no private right of action for DROP violations. — [Clym blog, vendor](https://www.clym.io/blog/california-drop-compliance-data-brokers)
- Independent audits are reported to begin Jan 1, 2028 [secondary]. The CalPrivacy page I fetched did not mention audits. — [UnsubCentral guide, vendor](https://www.unsubcentral.com/california-drop-and-the-delete-act-operational-guide-for-data-brokers/)

**Technical mechanics**
- CalPrivacy publishes six standardized deletion lists, keyed on email, phone, MAID, VIN and connected-TV ID.
- Access is by login or through the **DROP API**. Brokers apply **SHA-256 hashing with Base64 encoding** before matching.
- Each request gets one of four statuses: Deleted, Opted Out, Exempted or Not Found.
- Brokers must keep minimal hashed identifiers on suppression lists. — [UnsubCentral, vendor](https://www.unsubcentral.com/california-drop-and-the-delete-act-operational-guide-for-data-brokers/)

**Size of the obligated segment**
- **More than 600 active registered data brokers** as of July 2026 [vendor]. — [UnsubCentral](https://www.unsubcentral.com/california-drop-and-the-delete-act-operational-guide-for-data-brokers/); [Clym](https://www.clym.io/blog/california-drop-compliance-data-brokers)
- Over **325,000 consumers** had filed by July 2026 [vendor]. — [UnsubCentral](https://www.unsubcentral.com/california-drop-and-the-delete-act-operational-guide-for-data-brokers/)
- About **450,000 deletion requests** had been filed by August 2026, per Clym citing IAPP coverage of a CPPA board meeting [vendor citing trade press]. — [Clym](https://www.clym.io/blog/california-drop-compliance-data-brokers)
- **Only about 30% of registered brokers were processing DROP requests in week one** [vendor; not verified against CPPA]. — [Clym](https://www.clym.io/blog/california-drop-compliance-data-brokers)
- One post says the CPPA ordered people-search site Background Alert to cease operations through 2028 and set up a "Data Broker Enforcement Strike Force" [vendor/self-promo; no date or primary source]. — [DEV post](https://dev.to/t49qnsx7qtkpanks/background-alert-got-shut-down-heres-what-every-data-broker-needs-to-do-before-august-1-2g0b)

**Who is capturing them**
- **TrustArc** publishes DROP guidance. No price was found, and its positioning is enterprise. — [TrustArc](https://trustarc.com/resource/california-delete-act-drop-platform-data-brokers/)
- **UnsubCentral**: suppression-list management is live today. DROP request intake, matching, downstream deletion routing, status tracking and auditable reporting are all marked **"coming soon"**. No pricing is published. The page also says smaller brokers "may start by handling DROP manually". — [UnsubCentral, vendor](https://www.unsubcentral.com/california-drop-and-the-delete-act-operational-guide-for-data-brokers/)
- **Clym**: a general consent and privacy-request platform with no DROP-specific product described. Review sites list a Grow plan at $149/mo, and the figures conflict [secondary]. — [Clym blog](https://www.clym.io/blog/california-drop-compliance-data-brokers); [Clym pricing](https://clym.io/pricing)
- **DropAudit / "DROPShield"** (dropaudit-co.pages.dev): "designed for small and mid-size California data brokers."
  - The live page reads "**pre-launch and is not yet accepting customer data or payment**", with prices set to "Contact us".
  - **Conflict:** a search-engine snippet of the same page showed Starter at $499/mo and Compliance at $1,499/mo. — [DropAudit pricing, fetched 2026-11-06](https://dropaudit-co.pages.dev/pricing)
- **BizSuite**: $497 setup for "DROP integration and deletion automation", then $49/mo for the 45-day cadence and request logging. It "covers 48 brokers", which is ambiguous: it could be a consumer-side removal service rather than broker-side processing [vendor/self-promo, only on the author's own DEV posts]. — [DEV post](https://dev.to/t49qnsx7qtkpanks/background-alert-got-shut-down-heres-what-every-data-broker-needs-to-do-before-august-1-2g0b)

#### Shortlist #2: Packaging EPR reporting for mid-size DTC/CPG brands (Shopify-first). Verdict: PROVISIONAL (medium-low confidence; App Store check failed)

**Trigger (dated)**
- Oregon's 2026 annual supply report covered calendar-2025 data. The reporting portal opened March 31, 2026, and the report was due May 31, 2026 [vendor]. — [rePurpose](https://repurpose.global/blog/oregon-epr-2026-reporting-portal-open-may-31-deadline-approaching)
- Colorado: first invoice payment by Jan 31, 2026, report by May 31, 2026, payment by July 31, 2026 [secondary, from a search summary of vendor and blog pages; not checked against CDPHE]. — [rePurpose deadline blog](https://www.repurpose.global/blog/the-may-31-epr-deadline-is-almost-here-and-heres-what-brands-are-asking); [beancount.io](https://beancount.io/blog/2026/06/04/state-epr-packaging-laws-2026-cpg-brands-online-retailers-california-sb-54-oregon-recycling-modernization-colorado-minnesota-maine-circular-action-alliance-eco-modulation-fees-pcr-content-guide)
- **California (SB 54): first invoices expected January 2027, and preliminary 2027 rates are published. The small-producer exemption covers only brands under $1M in California sales.** The Circular Action Alliance (CAA) is the producer responsibility organization. — [EcoEnclose state table, updated 2026-10-14, vendor](https://www.ecoenclose.com/resources/epr-packaging-requirements/reporting-requirements-by-state)

**Who is exempt**
- Oregon: under $5M global revenue, or under 1 ton of covered materials into the state.
- Colorado: under 1 ton, or under an inflation-adjusted revenue threshold of about $5.6M as of July 2025.
- Minnesota: under $2M global revenue, or under 1 ton. — [EcoEnclose](https://www.ecoenclose.com/resources/epr-packaging-requirements/reporting-requirements-by-state)
- **Conflict:** rePurpose describes Oregon's exempt producers as "<$5M revenue **and** <5 metric tons", against EcoEnclose's "**or** <1 ton". — [rePurpose SMB summary](https://repurpose.global/blog/post/an-executive-summary-epr-compliance-in-oregon-for-smbs)

**Reporting burden and penalties**
- Oregon's low-volume producers can choose detailed weight reporting, flat-fee reporting or the highest flat fee. High-volume producers must file material-specific weights through the CAA Producer Portal. — [rePurpose](https://repurpose.global/blog/post/an-executive-summary-epr-compliance-in-oregon-for-smbs)
- Oregon and Colorado use roughly 60 reporting categories, and "one dataset generates both reports". CAA has released a reporting template [vendor, via search summary]. — [rePurpose deadline blog](https://www.repurpose.global/blog/the-may-31-epr-deadline-is-almost-here-and-heres-what-brands-are-asking)
- Oregon penalties are reported at $25,000/day/violation for qualifying small producers and $50,000 for others [secondary; not checked against Oregon DEQ]. — [rePurpose deadline blog](https://www.repurpose.global/blog/the-may-31-epr-deadline-is-almost-here-and-heres-what-brands-are-asking)

**Who is capturing them**
- **rePurpose Global** claims "500+ CPG brands". It offers EPR reporting, deadline tracking for OR/CO/CA/MN/ME, fee calculations and a packaging simulator. **No public pricing**; the path is demo or free liability assessment. — [rePurpose SMB page, vendor](https://repurpose.global/blog/post/an-executive-summary-epr-compliance-in-oregon-for-smbs); [rePurpose EPR solutions](https://repurpose.global/businesses/epr-solutions)
- **Assent** (enterprise supply-chain compliance) publishes a state EPR law guide. — [Assent](https://www.assent.com/?p=104642)
- Packaging suppliers publish free guides: **EcoEnclose** and **Zenpack**. — [EcoEnclose FAQ](https://ecoenclose.com/blog/epr-faq); [Zenpack guide](https://www.zenpack.us/blog/us-packaging-epr-compliance-guide/)
- **"EPR Manager"** is waitlist-only and claims it will support "every US state implementing packaging EPR". An idea-list site lists "Packaging EPR Compliance SaaS for Mid-Market Brands" as a startup idea, which is a sign that other founders are circling. — [EPR Manager waitlist](https://waitlist-eprmanager-com.pages.dev); [liveinthefuture.org](https://liveinthefuture.org/startups/packaging-epr-compliance-saas.html)
- **Shopify App Store search for "EPR" and "EPR packaging" returned an error page ("We are having trouble loading your results") on both attempts**, so the app-store incumbent check is incomplete. — [apps.shopify.com search](https://apps.shopify.com/search?q=EPR)

#### Shortlist #3: IEEPA tariff-refund reconciliation for small importers. Verdict: TIME-BOXED / MARGINAL (medium-low confidence)

**Trigger (dated)**
- On Feb 20, 2026, the Supreme Court ruled 6–3 in *Learning Resources v. Trump* that IEEPA does not authorize tariffs. — [Clark Hill, law firm](https://www.clarkhill.com/news-events/news/supreme-court-overturns-trumps-ieepa-tariffs); [Mondaq](https://www.mondaq.com/unitedstates/export-controls-trade-investment-sanctions/1750338/supreme-court-strikes-down-ieepa-tariffs-refund-process-and-next-steps-for-importers)
- On Mar 4, 2026, Court of International Trade Judge Eaton held that all importers who paid IEEPA duties are "entitled to the benefit". — [AP via News4Jax, trade press](https://www.news4jax.com/news/politics/2026/03/04/judge-rules-companies-are-entitled-to-refunds-for-trump-tariffs-overturned-by-the-supreme-court/)
- That order was suspended on Mar 6 while CBP built its process. — [GingerControl, vendor, updated 2026-10-12](https://gingercontrol.com/blog/ieepa-supreme-court-ruling-compliance)
- **CBP's CAPE refund module in ACE: Phase 1 opened Apr 20, 2026**, covering about 63% of eligible entries (unliquidated, or liquidated within the prior 80 days). — [Endless Commerce](https://endlesscommerce.com/playbook/supreme-court-ieepa-tariff-ruling-refunds)
- **Phase 2 added entries flagged for reconciliation from Jun 29, 2026.** — [GingerControl](https://gingercontrol.com/blog/ieepa-supreme-court-ruling-compliance)
- Excluded so far: drawback, entries under protest, finally liquidated entries, AD/CVD. — [Endless Commerce](https://endlesscommerce.com/playbook/supreme-court-ieepa-tariff-ruling-refunds)
- Only Phase 1 was listed as eligible in a help article updated July 15, 2026. — [Globalfy help](https://help.globalfy.com/help-center/ieepa-duty-refunds-via-cape-ace)

**Size**
- More than 330,000 importers of record across about 53 million entries [law firm, cited by a vendor].
- About $166B in IEEPA duties collected [press, cited by a vendor]. — [GingerControl](https://gingercontrol.com/blog/ieepa-supreme-court-ruling-compliance)
- About $175B potentially subject to refund claims [estimate]. — [Mondaq](https://webiis08.mondaq.com/unitedstates/international-trade-investment/1754096/the-us-supreme-court-rejects-ieepa-tariffs-refund-opportunities-and-uncertainty-emerge)

**Friction**
- Refunds are not automatic. Importers need ACE Portal access, ACH refund details and a CAPE Declaration. — [Globalfy](https://help.globalfy.com/help-center/ieepa-duty-refunds-via-cape-ace); [KPMG](https://kpmg.com/us/en/taxnewsflash/news/2026/03/us-cbp-ieepa-duty-refund-process-update.html)
- In March, **only about 21,000 of the 330,000+ importers had an ACE account** [secondary search summary of the KPMG/Mondaq/law-firm results; exact source not pinned].
- About **1 in 5 entries has filing errors**, and about **1,880 refunds were stuck as of May 11 for missing ACH details**. — [Endless Commerce](https://endlesscommerce.com/playbook/supreme-court-ieepa-tariff-ruling-refunds)
- Liquidations become final 180 days after liquidation unless protested. — [Endless Commerce](https://endlesscommerce.com/playbook/supreme-court-ieepa-tariff-ruling-refunds)
- Downstream purchasers who did not pay CBP directly may not be eligible. — [Mondaq](https://www.mondaq.com/unitedstates/export-controls-trade-investment-sanctions/1750338/supreme-court-strikes-down-ieepa-tariffs-refund-process-and-next-steps-for-importers)

**Who is capturing them**
- **Customs brokers:** UPS Supply Chain has an "How to Request IEEPA Tariff Refunds" page. Expeditors has a newsflash. — [UPS](https://ups.com/us/en/supplychain/logistics-solutions/customs-brokerage/us-customs-tariff-refunds); [Expeditors](https://info.expeditors.com/newsflash/cbp-preparing-ieepa-tariff-refund-process-in-ace)
- **Globalfy** (cross-border seller services) has a CAPE how-to. — [Globalfy](https://help.globalfy.com/help-center/ieepa-duty-refunds-via-cape-ace)
- **GingerControl** offers a **free IEEPA refund estimator** plus refund and drawback services, with no public pricing. Its site links comparison pages for **Pax, Trava, Caspian and Gaia Dynamics**, AI trade-compliance startups whose refund features I did not verify. — [GingerControl](https://gingercontrol.com/blog/ieepa-supreme-court-ruling-compliance)
- **Accounting and law firms:** KPMG, CLA, Greenberg Traurig and others. — [CLA FAQ](https://www.claconnect.com/en/resources/articles/26/tariff-refunds); [GT](https://www.gtlaw.com/en/insights/2026/3/customs-proposes-process-to-issue-ieepa-tariff-refunds-following-cit-decision)

#### Watchlist (incumbent check incomplete; do not build without finishing it)

- **COPPA amended-rule kit for small kids' app and edtech developers.**
  - The amended rule was published Apr 22, 2025. **Compliance date Apr 22, 2026**, apart from a few listed provisions. — [Federal Register, official](https://www.federalregister.gov/documents/2025/04/22/2025-05904/childrens-online-privacy-protection-rule)
  - New duties: a written information security program, a written data retention policy with a time limit, and biometric identifiers now count as personal information. — [Finnegan via Mondaq, law firm](https://webiis10.mondaq.com/unitedstates/privacy-protection/1790866/coppas-amended-rule-is-now-in-full-effect-what-operators-need-to-know)
  - Maximum penalty reported at $53,088 per violation [secondary]. — [compliancehub.wiki](https://compliancehub.wiki/coppa-april-22-deadline-ftc-updated-rule-compliance/)
  - The Kids Web Services (Epic) site returned HTTP 403, and no search budget was left to check PRIVO, kidSAFE or CARU tooling and pricing. — [BBB National Programs (CARU) reminder](https://bbbprograms.org/media/insights/blog/coppa-amended)
- **Title II documents for special districts and small towns (deadline Apr 26, 2028).**
  - A DOJ interim final rule published Apr 20, 2026 (FR doc 2026-07663) moved entities of 50,000+ population to **Apr 26, 2027**, and entities under 50,000 plus special districts to **Apr 26, 2028**. — [Plante Moran](https://plantemoran.com/explore-our-thinking/insight/2026/04/doj-extends-ada-title-ii-web-accessibility-compliance-deadlines)
  - "The scope of the rule and its technical requirements were not changed." — [Level Access, vendor](https://www.levelaccess.com/blog/the-ada-title-ii-extension-what-it-doesnt-change/)
  - Generic PDF remediation is already crowded (see the kill list). A meeting-packet-specific spin for water, fire and park districts was **not** checked against agenda-management vendors.
- **A multi-state data-broker add-on.** CalPrivacy's 30-day cadence from Jan 1, 2027 is official. — [CalPrivacy](https://privacy.ca.gov/data-brokers). Whether other states (VT, TX, OR registries) are copying DROP-style deletion platforms was not researched.

#### Kill list: triggers considered and why they died

| Trigger (date) | Why it died | Evidence |
|---|---|---|
| ADA Title II + HHS §504 web/document accessibility (DOJ deadlines Apr 2027/Apr 2028; HHS IFR May 7, 2026: 15+ employees May 11, 2027, <15 May 10, 2028) | Deadlines slipped a year, which cuts urgency. Generic PDF remediation is already cheap and crowded: Edlio Accessible Documents (launched Sept 24, 2026; Edlio says 19,000+ schools; also sold standalone); Accessibility on Demand from $0.30/page; DART $0.99/page pay-as-you-go; ThinkCodec first 25 pages free; Continual Engine PREP; AWS published a PDF remediation solution | [Baker Donelson, law firm](https://bakerdonelson.com/hhs-extends-web-and-mobile-accessibility-compliance-deadlines); [Plante Moran](https://plantemoran.com/explore-our-thinking/insight/2026/04/doj-extends-ada-title-ii-web-accessibility-compliance-deadlines); [K-12 Dive press release](https://www.k12dive.com/press-release/20260923-edlio-launches-pdf-accessibility-tool-for-school-websites-1/); [Carahsoft AoD](https://www.carahsoft.com/accessibility-on-demand) [secondary price]; [DART listing](https://saas-hunt.vercel.app/projects/dart) [secondary]; [PREP](https://www.continualengine.com/prep-pdf-remediation-software/); [AWS blog](https://aws.amazon.com/blogs/publicsector/from-inaccessible-to-inclusive-how-the-new-pdf-accessibility-remediation-solution-helps-institutions-compliantly-address-accessibility-requirements) |
| California AB 723 altered listing photos (Jan 1, 2026; B&P §10140.8) | Already captured: Coraly (Chrome extension piloted with the San Diego MLS; flags edits, QR links to originals, compliance record); Pixlmob/PropMedia QR disclosure; StagePro labels + disclosure page + QR; Imagen; Styldod. Also realtor-adjacent, an area the previous round assessed | [NAR, 2026-10-12](https://www.nar.realtor/news/real-estate-news/big-tech-has-a-fix-for-keeping-altered-listing-photos-more-honest); [SDMLS Coraly](https://support.sdmls.com/support/solutions/articles/150000223456-what-is-coraly-and-how-do-i-use-it); [Pixlmob](https://propmedia.pixlmob.com/disclosure/regulations/california-ab-723); [StagePro](https://www.stageproai.com/compliance/ab-723-explained); [Imagen](https://imagen-ai.com/es/solution/ab-723-compliance-ai-real-estate-photo-editing-done-right-imagen/) |
| Gmail ends Gmailify and POP "check mail from other accounts" (starting Jan 2026) | Displaced users weren't paying Google, and the replacements are free or about $1: provider-side forwarding (free); ForwardMyInbox (free; Product Hunt 7 points, 10 followers); ChainMail $1/mo; Mailbird $3.25/mo; eM Client free for 2 accounts; Thunderbird free; the alternative is Google Workspace at $7+/mo | [TidBITS quoting Google help](https://talk.tidbits.com/t/gmail-to-end-pop-fetching-and-gmailify-features/32657); [Slashdot/The Register, 2026-01-05](https://it.slashdot.org/story/26/01/05/1915218/google-to-kill-gmails-pop3-mail-fetching); [Product Hunt ForwardMyInbox](https://www.producthunt.com/products/forwardmyinbox); [ChainMail DEV post, vendor/self-promo](https://dev.to/admin_chainmail_6cfeeb3e6/gmailify-is-shutting-down-in-2026-what-are-your-options-45kd) |
| Exchange Online SMTP AUTH Basic Auth retirement (moved: disabled by default for existing tenants at end of Dec 2026; admins can re-enable; final date to be announced H2 2027) | Soft deadline. Free first-party paths exist (OAuth SMTP, Graph, High Volume Email preview); IP-based relays are unaffected; SMTP2GO is free up to 1,000 emails/mo and $10/mo for 10k. Printer scan-to-email remediation is MSP service work, not SaaS | [CaptainDNS, as of 2026-02-19](https://www.captaindns.com/en/blog/microsoft-exchange-basic-auth-smtp-end); [SMTP2GO pricing, official](https://www.smtp2go.com/pricing/); [Toshiba Tec blog](https://www.toshibatec.co.uk/news/blogs/2025/10/24/the-end-of-smtp-what-microsoft’s-email-security-changes-mean-for-your-business/) |
| Microsoft Publisher retirement (Oct 2026) | Free conversion paths: Word imports .pub; LibreOffice and Scribus import .pub; Microsoft documents a PowerShell bulk export to PDF; Canva/InDesign for redesign | [MUN IT notice](https://www.mun.ca/cio/news-articles/microsoft-publisher-end-of-life-in-october-2026-preparing-your-files-and-choosing-alternatives.php); [Office Watch](https://office-watch.com/2026/microsoft-publisher-is-ending-what-you-need-to-know/); [WFU IT](https://help.wfu.edu/support/solutions/articles/13000853375-microsoft-publisher-will-be-retired-and-lose-support-on-october-1-2026); [Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/5780232/can-i-migrate-my-publisher-files-what-replaces-it) |
| FinCEN residential real estate reporting rule (effective Mar 1, 2026) | Vacated nationwide on Mar 19, 2026 (*Flowers Title Cos. v. Bessent*, E.D. Tex.). FinCEN FAQs of May 18, 2026 say the rule is "without legal effect". An appeal was reported and another court reached a conflicting decision. No obligation means no demand | [Orrick](https://infobytes.orrick.com/2026-03-27/district-court-vacates-fincens-residential-real-estate-reporting-rule/); [Gibson Dunn](https://www.gibsondunn.com/fincen-residential-real-estate-reporting-rule-vacated-nationwide/); [Shumaker](https://www.shumaker.com/insight/client-alert-fincen-real-estate-rule-thrown-into-uncertainty-after-split-federal-court-decisions/) |
| New York LLC Transparency Act (Jan 1, 2026) | Gov. Hochul vetoed the expansion on Dec 19, 2025. The Act covers only non-US LLCs registered in NY | [Simpson Thacher](https://www.stblaw.com/about-us/publications/view/2025/12/23/the-new-york-llc-transparency-act-will-become-effective-on-january-1-2026-with-a-limited-scope); [Seward & Kissel](https://www.sewkis.com/publications/domestic-llcs-escape-new-yorks-transparency-act/) |
| California SB 68 restaurant allergen disclosure (signed Oct 13, 2025; effective Jul 1, 2026) | Applies only to chains with 20+ locations covered by federal menu labeling, not small businesses | [AFS Law](https://www.afslaw.com/perspectives/alerts/california-enacts-first-the-nation-allergen-disclosure-law-restaurant-chains); [California Restaurant Association](https://www.calrest.org/allergen-disclosures-sb-68) |
| GummySearch shutdown (signups closed Nov 30, 2025; offline Dec 1, 2026) + Reddit public API (no new requests after Oct 31, 2026; closure Mar 2027) | GummySearch closed because it couldn't get a Reddit commercial licence, so any replacement carries the same platform risk. Reddit lead-finding is also on the excluded list | [GummySearch notice](https://gummysearch.com/docs/articles/gummysearch-is-now-closed-6533h); [PPC Land, 2026-10-04](https://ppc.land/reddit-to-halt-public-data-api-access-in-march-2027-as-14-000-apps-register/) (both via prior notes) |
| X API pay-per-use (Feb 2026; ~$0.005/read, no free tier) | X tools are excluded, and the API costs make any listening product unattractive | [Open Terms Archive memo](https://opentermsarchive.org/en/memos/x-replaces-its-dollar200-entry-level-api-plan-with-a-pay-per-use-model/) (via prior notes, 3rd-party) |
| HoneyBook price hike (Feb 4, 2025: Starter $19→$36, Essentials $39→$59, Premium $79→$129 monthly) | Captured by cheaper bundles: Moxie about $10–12, Bloom $7–14, Plutio, Bonsai. Also an excluded category | [Fstoppers](https://www.fstoppers.com/business/honeybooks-price-hike-coming-heres-what-need-know-and-how-save-690584) (via prior notes, secondary) |
| Helium 10 removes the $39 Starter plan (Apr 2026, per competitor) | Etsy and TikTok Shop sellers already have cheaper native tools; covered by the previous round | [SentryKit, competitor-written](https://sentrykit.com/blog/helium-10-price-increase-2026-starter-plan-removed/) (via prior notes) |
| beehiiv 2026 / Mailchimp pricing | Captured by MailCheap ($19/mo), EmailOctopus (about $18 at 2.5k) and others; newsletters are excluded | [PPC Land on beehiiv](https://ppc.land/beehiiv-faces-complaints-as-lite-plan-rises-30-at-10-000-subscribers/); [GroupMail](https://blog.groupmail.io/mailchimp-nonprofit-pricing/) (via prior notes) |
| Skype retirement (May 5, 2025) | Microsoft captured users itself: Teams Free migration with chats and contacts carried over, and existing Skype Credit and subscriptions honoured to end of term | [Microsoft 365 blog, official](https://www.microsoft.com/en-us/microsoft-365/blog/2025/02/28/the-next-chapter-moving-from-skype-to-microsoft-teams/) |

### Inferences

#### Shortlist #1: DROP processor (spin, channel, build, risks, verdict)
- **Proposed spin:** a self-serve "DROP autopilot" for brokers with 1–20 staff, at $149–$299/mo, sold against $499+ or "contact us" competitors.
  1. Pull the six DROP lists through the API on a schedule.
  2. Normalize and SHA-256/Base64 hash the broker's identifiers locally. This could be a CLI or Docker job so raw PII never leaves the broker.
  3. Match, generate status files, keep the suppression list, and send 30- and 45-day cadence alerts.
  4. Produce an audit-evidence pack for the 2028 audits.

  The "~1% better" angle: enterprise privacy suites are generalist and the cheap entrants are pre-launch. A $6,000/yr registration fee shows these buyers already pay to operate, so $2–3k/yr is easy to justify against $200/request/day exposure.
- **Acquisition channel:** the obligated population is a finite, named list. CalPrivacy runs the broker registration, and I infer the public registry can be scraped into an outbound list. Add SEO for "DROP API", "Delete Act compliance software" and "45-day DROP" (SERPs are currently dominated by law-firm posts and one indie DEV-post author), and partnerships with privacy law firms who need a tool to point clients at.
- **Build complexity:** about 3–5 weeks for an MVP, on a standard web stack, a worker job and an open-source matcher. The hard parts are the DROP API integration (a sandbox exists, so it is testable) and the trust and security posture, not the code.
- **Risks:**
  - The total market is tiny: about 600 brokers, so roughly $10–40k MRR at best.
  - Customers include people-search sites, so there is reputational and abuse risk.
  - CalPrivacy may improve its own tooling.
  - Enterprise vendors (TrustArc, UnsubCentral) will fill the gap. UnsubCentral's "coming soon" is the clock.
  - Buyers may demand SOC 2.
  - The 30-day ratchet raises the stakes for buyers, which helps sales but also raises liability.
- **Verdict: BUILD CANDIDATE.** Validate quickly, before UnsubCentral ships, by emailing 30 small registrants.

#### Shortlist #2: EPR reporting for DTC brands
- **Proposed spin:** a Shopify app (later WooCommerce and Amazon CSV).
  1. Map each SKU to a packaging bill of materials (component, material, weight; ship-box rules per order size).
  2. Total shipped packaging by destination state from order data.
  3. Output CAA-template CSVs for OR, CO and CA plus estimated fees.
  4. Track the small-producer thresholds automatically.

  Price at $49–$149/mo, or a $499/yr "filing season" plan. The wedge is California SB 54: first invoices come January 2027 and only brands under $1M in California sales are exempt, so many Shopify brands with $1M+ California sales become producers for the first time.
- **Acquisition channel:** the Shopify App Store ("EPR", "SB 54"), "California SB 54 reporting for small brands" SEO, and co-marketing with packaging suppliers that already publish EPR guides to SMBs (EcoEnclose, Zenpack).
- **Build complexity:** about 4–6 weeks. The ongoing cost is keeping each state's category taxonomy current (Oregon added categories for 2026), not infrastructure.
- **Risks:**
  - Annual reporting cadence drives seasonal churn.
  - CAA templates and calculators may be "good enough".
  - rePurpose or Shopify-native apps may already exist; this is unverified.
  - Exemptions remove most tiny stores.
  - Mis-reporting creates liability.
- **Verdict: VALIDATE BEFORE BUILDING.** Re-run the Shopify App Store search manually and interview 10 brands with $1–20M revenue about how they filed in May 2026.

#### Shortlist #3: IEEPA refund reconciliation
- **Proposed spin:** upload ACE entry-summary exports (or broker spreadsheets) and get back:
  - a per-entry refund ledger: IEEPA Chapter 99 lines, expected refund plus interest;
  - a CAPE-phase eligibility tag;
  - a 180-day protest-deadline calendar;
  - ACH receipt reconciliation.

  Aim it at small importers who used several brokers or couriers. Price it one-off at $149–$499, rather than a contingency fee. A solo founder should avoid filing on importers' behalf, because I infer that customs business generally requires a licensed broker (unverified).
- **Acquisition channel:** "IEEPA refund calculator" SEO is contested (GingerControl has a free estimator), plus Amazon seller forums and Facebook groups, and accountants.
- **Build complexity:** about 2–3 weeks: a CSV parser, rules and a calendar.
- **Risks:** a 12–24 month lifespan; brokers bundling refunds for their clients; low data quality; the small importers who most need help may lack ACE accounts at all. A one-off product is not durable MRR, which conflicts with the "clone a money-making SaaS" method.
- **Verdict: OPPORTUNISTIC SIDE PROJECT ONLY.**

#### Pattern across all triggers
- The pattern holds. Displacement events where the platform has a free migration path (Skype, Publisher, Gmail POP, SMTP AUTH) produce **unpaid** displaced users and get captured within weeks. Price-hike events (HoneyBook, beehiiv, Helium 10) are captured by existing cheaper bundles.
- Survivable gaps appear only where **(a)** a regulator imposes a recurring, technical, penalty-backed workflow, and **(b)** the buyer pool is too small or obscure for enterprise vendors to price down to. DROP is the clearest example; EPR is a partial one.

### Gaps
- **Search budget ran out** (shared limit), so these checks did not happen:
  - the Shopify App Store EPR search (it failed twice);
  - COPPA tool pricing (PRIVO, kidSAFE, KWS);
  - agenda-management vendors for the special-district accessibility spin;
  - G2, Trustpilot or Capterra complaint-spike data for any trigger;
  - any Reddit evidence (blocked in the earlier round too).
- **Kill-list items not verified this session.** These were in the brief and are listed only for completeness; my understanding of them comes from training data, is **unverified**, and should be checked before relying on it:
  - Pocket shutdown (Mozilla's support page failed to load);
  - Glitch hosting end;
  - Heroku status;
  - Bending Spoons' Eventbrite, Vimeo and Meetup acquisitions;
  - Instagram Basic Display API end (Dec 2024);
  - BOI/CTA exemption for domestic companies (FinCEN, Mar 2025);
  - 1099-K threshold reversal;
  - the vacated FTC click-to-cancel rule;
  - PCI DSS 4.0 SAQ A changes;
  - the EU Accessibility Act microenterprise exemption;
  - the FSMA 204 delay;
  - Colorado AI Act timing;
  - state privacy-law thresholds;
  - FTC fake-review and junk-fee rules;
  - California SB 478.

  None of these was found to be an opportunity. Treat their status as unconfirmed.
- **DROP:** I couldn't get the exact number of *small* brokers in the CalPrivacy registry, the Background Alert enforcement date and amount from a primary source, or the meaning of BizSuite's "48 brokers".
- **IEEPA:** I couldn't find the CAPE phase status after July 2026, any CAPE filing deadline, or whether courier-entered informal entries (common for small DTC importers after de minimis changes) can be refunded to the buyer.
- **EPR:** Oregon's exemption definition conflicts between sources ("or <1 ton" vs "and <5 metric tons"), and no official count of registered producers was found.

---

## Q1. Which 2025–2026 events displaced the most paying small customers, and who captured them?

### Takeaway
By number of affected payers, the largest 2025–2026 "displacement" is the **IEEPA refund event**: 330,000+ importers of record. It is a one-off claim, not a switching event, and brokers and trade-compliance vendors are already capturing it. Among software events, the price hikes (HoneyBook Feb 2025, beehiiv 2026, Helium 10 Apr 2026) displaced genuinely *paying* customers, but existing cheaper bundles absorbed them. Platform retirements (Skype May 2025, Gmailify/POP Jan 2026, Publisher Oct 2026, Exchange SMTP AUTH Dec 2026) displaced mostly non-paying users, and the platform's own free path or free and $1 tools absorbed them. API closures (Reddit 2026–27, X pay-per-use Feb 2026) killed tools such as GummySearch rather than creating openings.

### Cited Findings
- **IEEPA refunds:** more than 330,000 importers of record across about 53 million entries and about $166B collected. CAPE Phase 1 opened Apr 20, 2026, Phase 2 on Jun 29, 2026. Capture is happening through brokers and vendors: UPS, Expeditors, Globalfy, GingerControl's free estimator, and AI trade-compliance startups (Pax, Trava, Caspian, Gaia Dynamics). — [GingerControl](https://gingercontrol.com/blog/ieepa-supreme-court-ruling-compliance); [UPS](https://ups.com/us/en/supplychain/logistics-solutions/customs-brokerage/us-customs-tariff-refunds); [Expeditors](https://info.expeditors.com/newsflash/cbp-preparing-ieepa-tariff-refund-process-in-ace); [Globalfy](https://help.globalfy.com/help-center/ieepa-duty-refunds-via-cape-ace)
- **Skype (May 5, 2025):** Microsoft moved users to Teams Free, carried chats and contacts over automatically, and honoured paid credit and subscriptions until the end of term. New customers could no longer buy Skype Credit. — [Microsoft 365 blog, official](https://www.microsoft.com/en-us/microsoft-365/blog/2025/02/28/the-next-chapter-moving-from-skype-to-microsoft-teams/)
- **Gmailify and POP fetch end:** "starting January 2026" per Google's help text as quoted by TidBITS. Timing for existing users varies by source: Mailbird says later in 2026, and one site says January 2027 (unverified). — [TidBITS](https://talk.tidbits.com/t/gmail-to-end-pop-fetching-and-gmailify-features/32657); [Mailbird](https://www.getmailbird.com/gmailify-limitations/); [heise](https://heise.de/-10709020)
  - Captured by free forwarding, desktop clients (eM Client, Mailbird, Thunderbird) and micro-tools (ForwardMyInbox free, ChainMail $1/mo). — [Product Hunt](https://www.producthunt.com/products/forwardmyinbox); [DEV post, vendor/self-promo](https://dev.to/admin_chainmail_6cfeeb3e6/gmailify-is-shutting-down-in-2026-what-are-your-options-45kd); [eM Client](https://www.emclient.com/gmailify-is-ending-meet-em-client)
- **Microsoft Publisher (Oct 2026):** Microsoft recommends Word or PowerPoint for church bulletins and newsletters, and documents a bulk PowerShell export to PDF. LibreOffice and Scribus import .pub for free. — [Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/5780232/can-i-migrate-my-publisher-files-what-replaces-it); [MUN](https://www.mun.ca/cio/news-articles/microsoft-publisher-end-of-life-in-october-2026-preparing-your-files-and-choosing-alternatives.php)
- **Exchange SMTP AUTH:** disabled by default at end of Dec 2026, with admins able to re-enable it and final removal to be announced in H2 2027. Affected senders include MFP scan-to-email, ERP/CRM apps, scripts, NAS units and cameras. Free first-party fixes exist, and SMTP2GO is free up to 1,000 emails/mo. — [CaptainDNS](https://www.captaindns.com/en/blog/microsoft-exchange-basic-auth-smtp-end); [SMTP2GO](https://www.smtp2go.com/pricing/)
- **HoneyBook (Feb 4, 2025):** monthly prices rose sharply (Starter $19→$36). Switchers went to Moxie ($10–12), Plutio ($19), Bonsai ($19 annual), Bloom ($7–14) and Dubsado. — [Fstoppers](https://www.fstoppers.com/business/honeybooks-price-hike-coming-heres-what-need-know-and-how-save-690584); [HoneyBook pricing](https://www.honeybook.com/pricing) (both via the earlier round's `coach_practitioner_admin.md`)
- **GummySearch:** closed because it could not reach a commercial licence with Reddit's Data API. New signups closed Nov 30, 2025, and the service goes fully offline Dec 1, 2026. Reddit stops accepting new public API requests on Oct 31, 2026 and closes public API access in March 2027. — [GummySearch notice](https://gummysearch.com/docs/articles/gummysearch-is-now-closed-6533h); [PPC Land](https://ppc.land/reddit-to-halt-public-data-api-access-in-march-2027-as-14-000-apps-register/) (via the earlier round's `local_services_tools.md`)
- **Helium 10:** its pricing page lists only Platinum ($129 monthly / $99 annual) and higher plans. A competitor-written post says the $39 Starter plan was removed in April 2026. — [Helium 10 pricing](https://www.helium10.com/pricing/); [SentryKit, competitor](https://sentrykit.com/blog/helium-10-price-increase-2026-starter-plan-removed/) (via `ecommerce_data_tools.md`)
- **X API** moved to pay-per-use in February 2026 with no free tier, at about $0.005 per post read [3rd-party]. — [Open Terms Archive](https://opentermsarchive.org/en/memos/x-replaces-its-dollar200-entry-level-api-plan-with-a-pay-per-use-model/) (via `realtor_tools.md`)

### Inferences
- The shutdowns that matter for a cloner are those where the displaced users *were paying*, and no free first-party migration exists. None of the 2025–2026 platform retirements checked here meets both conditions.
- Price-hike refugees are real, but they flow to the existing "cheaper clone" tier within weeks. Showing up after the event is too late unless the cloner targets a sub-segment the cheaper bundles ignore.

### Gaps
- No quantitative switching data (churn or migration counts) was found for any event.
- Pocket, Glitch, Heroku, Eventbrite/Vimeo/Meetup (Bending Spoons), Loom/Atlassian, Calendly, Zapier, Notion, Canva, Webflow, Mailchimp, Hootsuite, Typeform, Squarespace/Acuity and Adobe were **not** checked this session because the search budget ran out. Their status is unconfirmed.
- Instagram Basic Display (Dec 2024) and other Meta and Google API changes were not verified this session.

---

## Q2. Which new small-business legal obligations have deadlines with penalties, and is the compliance-tool market for small businesses already served cheaply?

### Takeaway
Of the obligations checked:
- **Served cheaply or bundled:** AB 723 and Title II/HHS 504 document remediation.
- **Dead or not applicable to small businesses:** the FinCEN real estate rule (vacated), the NY LLC Transparency Act (vetoed for domestic LLCs) and SB 68 (chains only).
- **Expensive, demo-only or pre-launch tools:** the **Delete Act DROP** workflow (600+ brokers, $200/request/day) and **packaging EPR** reporting (OR/CO now, CA from January 2027).
- **Not checked:** COPPA's amended rule (in force Apr 22, 2026), because the search budget ran out.

The accessibility rules moved again: the DOJ and HHS interim final rules each added a year, pushing the smallest entities to April and May 2028.

### Cited Findings
- **DOJ Title II:** interim final rule effective Apr 20, 2026 (FR doc 2026-07663). Entities of 50,000+ population: Apr 26, 2027 (was Apr 24, 2026). Entities under 50,000 and special districts: Apr 26, 2028 (was Apr 26, 2027). Comments closed Jun 22, 2026. — [Plante Moran](https://plantemoran.com/explore-our-thinking/insight/2026/04/doj-extends-ada-title-ii-web-accessibility-compliance-deadlines)
  - "The scope of the rule and its technical requirements were not changed." — [Level Access](https://www.levelaccess.com/blog/the-ada-title-ii-extension-what-it-doesnt-change/)
  - A search summary said one source reported the extension being challenged in court. This is unverified (see Gaps). — [Mondaq](https://www.mondaq.com/unitedstates/government-contracts-procurement-ppp/1776328/doj-extends-ada-title-ii-website-accessibility-deadlines-for-governmental-entitiesbut-litigation-and-compliance-risks-remain)
- **HHS §504:** OCR interim final rule announced May 7, 2026 and published May 11, 2026. Recipients with 15+ employees: May 11, 2027. Fewer than 15: May 10, 2028. Coverage includes providers that accept Medicare or Medicaid, per the firm. — [Baker Donelson, law firm](https://bakerdonelson.com/hhs-extends-web-and-mobile-accessibility-compliance-deadlines). Several vendor pages still show the May 2026 date and are out of date. — [Deque](https://www.deque.com/blog/section-504-digital-accessibility-deadlines-what-every-hhs-funded-provider-must-know/)
- **Accessibility tool pricing:**
  - Manual PDF remediation is about $1–$11.50/page, mostly $5–$8 [vendor listicle]. — [Continual Engine](https://www.continualengine.com/?p=8097)
  - AI options: Accessibility on Demand from $0.30/page with no minimum, and DART at $0.99/page [secondary]. — [Carahsoft](https://www.carahsoft.com/accessibility-on-demand); [DART](https://saas-hunt.vercel.app/projects/dart)
  - Edlio Accessible Documents launched Sept 24, 2026: HTML conversion of every PDF, WCAG 2.2 and PDF/UA scans, auto-fixes, and AI-drafted metadata. Available standalone. — [K-12 Dive](https://www.k12dive.com/press-release/20260923-edlio-launches-pdf-accessibility-tool-for-school-websites-1/)
- **AB 723** (effective Jan 1, 2026; B&P §10140.8): disclose digitally altered listing images and give access to the originals. CRMLS Rule 11.5.2 aligns MLS rules. — [SDMLS](https://sdmls.com/?p=4337); [Pixlmob CRMLS page](https://propmedia.pixlmob.com/disclosure/regulations/crmls)
  - Coraly's analysis of about 40,000 US primary photos flagged about 11% as altered, and over 90% of those had no visible disclosure. — [NAR, 2026-10-12](https://www.nar.realtor/news/real-estate-news/big-tech-has-a-fix-for-keeping-altered-listing-photos-more-honest)
- **Delete Act DROP:** Aug 1, 2026 start, 45-day cadence (30 days from Jan 1, 2027), $200/day per unfulfilled request, $6,000 registration fee. — [CalPrivacy, official](https://privacy.ca.gov/data-brokers)
- **Packaging EPR:** California's first invoices are expected January 2027, with a $1M California-sales exemption. Oregon exempts under $5M revenue or under 1 ton; Colorado about $5.6M or 1 ton; Minnesota $2M or 1 ton. — [EcoEnclose](https://www.ecoenclose.com/resources/epr-packaging-requirements/reporting-requirements-by-state)
- **COPPA:** compliance from Apr 22, 2026, requiring a written information security program, a retention policy and biometrics as personal information. — [Federal Register](https://www.federalregister.gov/documents/2025/04/22/2025-05904/childrens-online-privacy-protection-rule); [Finnegan/Mondaq](https://webiis10.mondaq.com/unitedstates/privacy-protection/1790866/coppas-amended-rule-is-now-in-full-effect-what-operators-need-to-know). The Toy Association flagged it to toy-brand members. — [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx)
- **FinCEN RRE rule:** effective Mar 1, 2026 and vacated Mar 19, 2026. FinCEN's May 18, 2026 FAQs call it "without legal effect" while the order stands. — [Orrick](https://infobytes.orrick.com/2026-03-27/district-court-vacates-fincens-residential-real-estate-reporting-rule/); [Gibson Dunn](https://www.gibsondunn.com/fincen-residential-real-estate-reporting-rule-vacated-nationwide/)
- **NY LLC Transparency Act:** the domestic-LLC expansion was vetoed Dec 19, 2025, so the Act covers only non-US LLCs. — [Simpson Thacher](https://www.stblaw.com/about-us/publications/view/2025/12/23/the-new-york-llc-transparency-act-will-become-effective-on-january-1-2026-with-a-limited-scope)
- **SB 68 allergen disclosure:** effective Jul 1, 2026, and limited to chains with 20+ locations. — [AFS Law](https://www.afslaw.com/perspectives/alerts/california-enacts-first-the-nation-allergen-disclosure-law-restaurant-chains)

### Inferences
- Rules aimed at *many tiny* businesses (AB 723 agents, school websites) attract cheap tools and vendor or MLS bundling quickly.
- Rules aimed at *a few hundred to a few thousand* odd-shaped businesses (data brokers, mid-size packaging "producers") stay expensive, because enterprise compliance vendors don't price down and few indie founders notice them. That is where a solo cloner fits.
- Repeated federal delays and vacaturs (DOJ, HHS, FinCEN) make "deadline-driven" products risky unless the obligation is state-level and already enforcing, like DROP or Oregon/Colorado EPR.

### Gaps
- The exact DOJ dates for public colleges and universities differ by a day across sources (Apr 26 vs Apr 27, 2027). The Federal Register text was not fetched.
- Whether Medicare Part B-only providers count as HHS "recipients" was not resolved. Baker Donelson says Medicare or Medicaid; no exclusion was confirmed.
- Not verified this session: PCI DSS 4.0 (SAQ A changes), the EU Accessibility Act microenterprise exemption, BOI/CTA status, 1099-K thresholds, the FTC click-to-cancel vacatur, FTC fake-review and junk-fee rules, California SB 478, the Colorado AI Act, Illinois AI-in-employment notice, new state privacy laws, e-invoicing mandates and California auto-renewal law (AB 2863). None was confirmed as an opportunity, and their status should be checked before anyone relies on it.
- COPPA tooling and pricing for small developers is unchecked.

---

## Q3. Where is switching or compliance demand visible?

### Takeaway
The visible demand signals are mostly **regulator and vendor data, not review-site spikes**. Those signals include:
- 70% of data brokers were not processing DROP in week one;
- 90% of altered listing photos were undisclosed;
- only about 21,000 of 330,000+ IEEPA payers had ACE accounts;
- 1 in 5 entries have filing errors.

There are also community threads (Slashdot and TidBITS on Gmail POP, Microsoft Q&A on Publisher) and a wave of indie "launch posts", which signal founder competition as much as buyer demand. Trustpilot, G2 and Capterra trend data could not be gathered this session.

### Cited Findings
- **DROP:** about 30% of registered brokers were processing requests in week one, and about 450,000 requests had been filed by August 2026 [vendor]. — [Clym](https://www.clym.io/blog/california-drop-compliance-data-brokers)
  - Founder content is clustering around DROP: a series of DEV posts on 45-day deadlines and $200/day penalties. — [DEV post 1](https://dev.to/t49qnsx7qtkpanks/drop-enforcement-is-83-days-out-heres-what-500-data-brokers-are-actually-required-to-do-by-august-3ofi); [DEV post 2](https://dev.to/t49qnsx7qtkpanks/the-200-per-day-problem-hiding-in-californias-new-drop-portal-210)
  - Separate pre-launch products exist: DropAudit. — [DropAudit](https://dropaudit-co.pages.dev/)
  - Law firms are publishing "compliance wave" alerts. — [JD Supra](https://www.jdsupra.com/legalnews/a-compliance-wave-is-coming-data-2897233); [Alston & Bird](https://www.alstonprivacy.com/drop-is-coming-due-what-californias-delete-act-means-for-data-brokers-in-august/)
- **AB 723:** about 11% of 40k US primary photos were altered, and over 90% of those were undisclosed. — [NAR](https://www.nar.realtor/news/real-estate-news/big-tech-has-a-fix-for-keeping-altered-listing-photos-more-honest). HousingWire ran "Most AI-altered listings go undisclosed". — [HousingWire](https://www.housingwire.com/articles/most-ai-altered-listings-go-undisclosed-california-law-bans-it/)
- **IEEPA refunds:** about 1,880 refunds were stuck as of May 11 for missing ACH details, and about 1 in 5 entries had errors. — [Endless Commerce](https://endlesscommerce.com/playbook/supreme-court-ieepa-tariff-ruling-refunds)
- **Gmail POP/Gmailify:** a Slashdot thread on The Register's story ran Jan 5, 2026, and TidBITS has a user thread. Replacement vendors are publishing "Gmailify is ending" landing pages (eM Client, Mailbird). — [Slashdot](https://it.slashdot.org/story/26/01/05/1915218/google-to-kill-gmails-pop3-mail-fetching); [TidBITS](https://talk.tidbits.com/t/gmail-to-end-pop-fetching-and-gmailify-features/32657); [eM Client](https://www.emclient.com/gmailify-is-ending-meet-em-client); [Mailbird](https://www.getmailbird.com/gmailify-replacement-workflow/)
- **Publisher:** Microsoft Q&A threads ask how to keep using Publisher after the cutoff and how to migrate files. — [Microsoft Q&A 1](https://learn.microsoft.com/en-us/answers/questions/5855781/how-can-i-continue-to-use-microsoft-publisher-afte); [Microsoft Q&A 2](https://learn.microsoft.com/en-us/answers/questions/5852051/after-this-date-you-will-no-longer-be-able-to-open)
- **Packaging EPR:** rePurpose runs an "EPR survey" and "what brands are asking" content around the May 31 deadline, a sign of SMB confusion [vendor]. — [rePurpose survey](https://epr-survey.repurpose.global/); [rePurpose blog](https://www.repurpose.global/blog/the-may-31-epr-deadline-is-almost-here-and-heres-what-brands-are-asking)
- **HoneyBook 2025:** Trustpilot backlash after the hike, including a refund request from an annual payer (from the earlier round). — [Trustpilot HoneyBook](https://www.trustpilot.com/review/honeybook.com?page=6) (via `coach_practitioner_admin.md`)

### Inferences
- When several indie launch posts appear (DROP DEV posts, a Gmailify replacement on Product Hunt, EPR waitlists, AI PDF remediators), the window is closing. DROP and EPR still show more regulator-measured non-compliance than shipped products. Gmail POP and AB 723 already show more products than paying demand.
- The best acquisition channel for obligation-driven niches is a **named list of obligated entities**: the CalPrivacy broker registry, CAA-registered producers, the ACE importer population via brokers. That beats "X alternative" SEO, which is saturated for every price-hike event examined.

### Gaps
- No Trustpilot, G2 or Capterra time-series data and no Google Trends "alternative to X" data were gathered, because the search budget ran out. Review-spike evidence is missing for every trigger except HoneyBook (prior round).
- Reddit remains inaccessible to the tools, as in the earlier round.
- Search-volume estimates for "DROP compliance", "SB 54 reporting" and "IEEPA refund" were not obtained.
