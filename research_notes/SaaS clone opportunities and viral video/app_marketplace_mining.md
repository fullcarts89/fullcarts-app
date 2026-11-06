# App-marketplace mining: proven paid categories with weak, overpriced or neglected incumbents (as of 2026-11-06)

**Method and provenance.** All marketplace figures were pulled directly from first-party marketplace pages or APIs on **2026-11-06**, unless marked otherwise:
- Shopify: 74 keyword searches on apps.shopify.com, then 989 app listing pages parsed (JSON-LD `aggregateRating`, "Launched" date, "Built for Shopify" badge, pricing block). 777 apps returned a rating. A few listings failed to fetch (curl errors), including Smile.io, Refersion, Weglot and Synder.
- Atlassian: Marketplace REST API v2 (`/rest/2/addons`, `/distribution`, `/reviews?sort=recent`, `/pricing/cloud/live`, `/versions/latest`). That covered 678 Jira and Confluence Cloud apps across the popular, top-grossing and highest-rated lists, plus about 25 keyword searches. "Installs" means Atlassian's `totalInstalls`. Prices are Atlassian list prices: `monthsValid=12` means annual and `1` means monthly. A $0 price at the 10-user tier means the app is free for up to 10 users.
- WordPress: api.wordpress.org `query_plugins` (browse=popular, the top 1,500 plugins) plus `plugin_information` with reviews.
- Chrome Web Store: detail pages for about 90 extensions, which give users, average rating, rating count and last-updated date. CWS reviews load dynamically and were **not** retrievable. Chrome-Stats (third-party) returned HTTP 403 (Cloudflare), so **historical rating trends could not be verified**. Only current ratings are reported.
- Google Workspace Marketplace: about 25 search-result pages, which give rating and install bucket, plus 6 app pages, which give review count, pricing type, listing-updated date and recent reviews.
- **Web-search budget was exhausted mid-task.** Revenue-share terms for Atlassian, Chrome and Workspace, developer revenue case studies (Indie Hackers, Starter Story), third-party trackers, and HubSpot, Slack, Figma, Wix, Squarespace and Zapier data were **not** collected. See the Gaps sections.

Label key: **[ML]** = marketplace listing or API, platform-reported (installs, ratings, review counts, list prices). **[Review]** = verbatim user review on the marketplace, with its date. **[Dev-site]** = the vendor's own claim. **[Platform-doc]** = official platform documentation.

---

## Q1. Which Shopify App Store categories have the worst rating-to-review-count ratio among apps with paid plans?

### Takeaway
Shopify is close to fully saturated. In almost every category, the top 7 apps by review count rate 4.7–5.0 and offer a free plan. Only **5 third-party apps with 120+ reviews rate 4.3 or lower** in the 777-app scan. The worst ratings with high review counts belong to **Shopify's own free apps and big-platform channel apps**, and each of those already has a 4.9–5.0, free-plan third-party alternative with thousands of reviews. The only third-party paid category with a clear "incumbent is degrading" signal is **store backup and restore (Rewind)**.

### Cited Findings
**Low-rated apps with high review counts, third-party, 120+ reviews, rating ≤4.3 [ML]:**
- Gorgias AI Helpdesk: 4.3★ / 708 reviews, from $10/mo, Built for Shopify — [listing](https://apps.shopify.com/helpdesk)
- **Rewind Backups: 4.3★ / 632 reviews, plans $19/mo and $99/mo, launched Jan 5 2016, no Built for Shopify badge** — [listing](https://apps.shopify.com/backup)
- CS Amazon Integration & Sync (Feed.Biz): 4.1★ / 245 — [listing](https://apps.shopify.com/amazon-3)
- Yoast SEO: 4.3★ / 174, from $19/mo — [listing](https://apps.shopify.com/yoast-seo)
- Bold QuickBooks Sync Pro: 3.2★ / 167, from $19.99/mo, launched 2015 — [listing](https://apps.shopify.com/quickbooks-online)
- Only 18 third-party apps with 120+ reviews rated ≤4.5 out of 777 rated apps. Examples in the 4.4–4.5 band: Transcy 4.5/2,561, LangShop 4.5/470, Chargeflow 4.5/437, Helium Customer Fields 4.5/355 (from $15/mo), BeProfit 4.5/203 (from $49/mo), Re:amaze 4.5/181 (from $29/mo) — [Shopify App Store search](https://apps.shopify.com/search)

**Shopify-owned and big-platform apps are the worst-rated, but each has an entrenched third-party winner [ML]:**
- Shopify Search & Discovery 2.6★/514 vs Searchanise 4.7/1,267 (free plan) — [S&D](https://apps.shopify.com/search-and-discovery), [Searchanise](https://apps.shopify.com/search?q=search+filter)
- Shopify Bundles 2.9★/571 vs Kaching Bundles 5.0/6,636, Fast Bundles 5.0/3,641, Pumper 4.9/3,635 — [Bundles](https://apps.shopify.com/shopify-bundles)
- Shopify Order Printer 3.6★/387 vs Order Printer Pro 4.9/3,053, Avada PDF Invoice 4.9/713 (free plan) — [Order Printer](https://apps.shopify.com/shopify-order-printer)
- Shopify Subscriptions 3.8★/895 vs Appstle 5.0/9,219, Seal 4.9/3,163 (free plans) — [Subscriptions](https://apps.shopify.com/shopify-subscriptions)
- Shopify Marketplace Connect 4.1★/2,133; Meta Facebook & Instagram 3.9★/5,837; Amazon MCF 3.8★/108. These are channel or partnership apps and cannot be cloned — [Marketplace Connect](https://apps.shopify.com/marketplace-connect), [Facebook](https://apps.shopify.com/facebook)

**Categories where the top 7 apps all rate ≥4.6 with free plans (saturated) [ML]:** product options (Globo 4.9/5,266), reviews (Loox 4.9/10,045), loyalty (BON 5.0/1,984), affiliate (UpPromote 4.9/3,930), pre-order/back-in-stock (Artos 5.0/3,915), popups (Pop Convert 4.9/8,688), SEO (Booster 4.8/5,487), page builders (GemPages 4.9/4,263), bulk edit (Matrixify 4.9/1,872), order tracking (17TRACK 4.9/4,584), cookie consent (Pandectes 5.0/3,117), delivery date (Logbase 4.9/1,344), B2B/wholesale (BSS 4.9/1,203), order limits, labels, countdowns, cart drawers and quote requests — [Shopify App Store search](https://apps.shopify.com/search)

**Rewind complaint evidence [Review], from the 1–2★ newest-first pages** — [1★](https://apps.shopify.com/backup/reviews?ratings%5B%5D=1&sort_by=newest), [2★](https://apps.shopify.com/backup/reviews?ratings%5B%5D=2&sort_by=newest):
- Aug 23 2026: "I cancelled this and I've still been charged… they've doubled the cost I originally agreed to and now I can't unsubscribe and stop paying."
- Jun 13 2026: "We thought this app will cost 9 USD a month... now we paid for long time around 40 to 50 USD"
- Apr 24 2026: "Restore was blocked for 4 days… Nobody available for help over the weekend. I also don't like you cannot restore specific items. You either restore ALL blog posts or none, ALL products or none, ALL collections or none… Switching to other app."
- Apr 4 2026: "was free, they charged me 160 euros. not recommended". Rewind replied Apr 6 2026: "This was our first price increase in many years".
- Mar 29 2026: account "deactivated because we have not logged in for over 90 days… However, the app did not stop collecting the charges for all these months."
- Dec 29 2025: "They raised the pricing by double without announcing it."
- Dec 27 2025: manual sort orders lost "for over 1500 products". Rewind replied (Jan 29 2026) that it "cannot currently see, back up, or reliably restore the manual sort order".
- Sep 22 2025: "notified us of a soon-to-be price increase from an affordable $9/mo to $19/mo."
- Sep 27–30 2025: Rewind replied "You're right that inventory is not backed up. This is a Shopify API limitation."
- Rewind's listing now positions the app as "The safety net for AI Toolkit, Sidekick, and Magic" [ML] — [listing](https://apps.shopify.com/backup)

**Platform economics [Platform-doc]:** Shopify charges 0% revenue share on a developer's first $1,000,000 of *lifetime* gross app revenue (counting only revenue from Jan 1 2025 onward), and 15% above that. A 2.9% processing fee applies to all billing, and registration is a one-time $19 per Partner account — [shopify.dev](https://shopify.dev/docs/apps/launch/distribution/revenue-share)

### Inferences
- Review counts on Shopify are heavily solicited: free plans plus in-app review prompts push top apps to 4.9–5.0. A rating of 4.3 is therefore an outlier, and it signals real dissatisfaction.
- The classic "low-rated incumbent" gap on Shopify mostly sits in apps Shopify itself ships. Third-party dev shops (Kaching, Essential, CWILL, Avada, BSS, Hulk) already close those gaps with free plans, so cloning them fails the niche check.
- Backup and restore stands out: demand is rising because AI bulk edits (Sidekick, AI Toolkit, Magic) create new ways to wreck a catalog, the leader roughly doubled its entry price in 2025, and its restore is coarse.

### Gaps
- Rewind's ownership history and any revenue figures were not verified (search budget exhausted).
- No historical rating series was available for Shopify apps (third-party trackers not reached), so "decline" is shown only through dated review text.
- It is unknown whether Shopify plans native product or version history.

---

## Q2. Which Chrome extensions with 100k+ users and paid tiers have rating declines or neglect?

### Takeaway
Many large paid or freemium extensions currently rate 2–3.8★. The biggest cluster is **screen capture** (GoFullPage, FireShot, Awesome Screenshot, Loom, Screencastify), but every capture sub-category already has **4.5–4.8★ alternatives with 1M users and thousands of reviews**, so the clone ideas die at the niche check. No Chrome idea survived to the shortlist.

### Cited Findings
**Current CWS figures [ML]** (format: rating / rating count / users / last updated):
- GoFullPage – Full Page Screen Capture: **3.4 / 84.8K / 11,000,000**, updated Oct 23 2026 — [CWS](https://chromewebstore.google.com/detail/fdpohaocaechififmbbbbbknoalclacl)
- FireShot: **2.1 / 53K / 3,000,000**, updated May 24 2026 — [CWS](https://chromewebstore.google.com/detail/mcbpblocgmgfnpjjppndjkmgjaogfceg). Pro pricing: $39.95/yr, $7.95/mo or $99.95 lifetime. FireShot claims "6,000,000+ users" across browsers [Dev-site] — [getfireshot.com](https://getfireshot.com/buy.php)
- Awesome Screen Recorder & Screenshot: 3.2 / 29.6K / 4,000,000 — [CWS](https://chromewebstore.google.com/detail/nlipoenfbbikpbjkfpfillcgkoblgpmj)
- Loom: 2.8 / 10.2K / 8,000,000 — [CWS](https://chromewebstore.google.com/detail/liecbddmkiiihnedobmlmillhodjkdmb). Screencastify: 3.7 / 11.7K / 9,000,000 — [CWS](https://chromewebstore.google.com/detail/mmeijimgabbpbgpdklnllpncmdofkcpn). Vidyard: 3.4 / 1.3K / 300,000 — [CWS](https://chromewebstore.google.com/detail/jiihcciniecimeajcniapbngjjbonjan)
- Grammarly: 3.6 / 43.2K / 40,000,000 — [CWS](https://chromewebstore.google.com/detail/kbfnbcaeplbcioakkpcpgfkobkghlhen). LanguageTool: 3.1 / 12.6K / 2,000,000 — [CWS](https://chromewebstore.google.com/detail/oldceeleldhonbafppcapldpdifcinji). DeepL: 3.6 / 12.7K / 4,000,000 — [CWS](https://chromewebstore.google.com/detail/cofdbpoegempjloogbagkncekinflcnj)
- Teleparty: 3.8 / 17.5K / 10,000,000 — [CWS](https://chromewebstore.google.com/detail/oocalimimngaihdkbihfgmpkcpnmlaoa). Language Reactor (in-app purchases): 3.8 / 4.5K / 2,000,000 — [CWS](https://chromewebstore.google.com/detail/hoombieeljmmljlkjmnheibnpciblicm)
- Education: Kami 2.5 / 8.4K / 18,000,000 — [CWS](https://chromewebstore.google.com/detail/ecnphlgnajanjnkcmbpancdjoidceilk). Read&Write 2.8 / 1.6K / 19,000,000 — [CWS](https://chromewebstore.google.com/detail/inoeonmfapjbbkmdafoankkfajkcphgd). Mote (in-app purchases) 3.5 / 171 / 2,000,000 — [CWS](https://chromewebstore.google.com/detail/ajphlblkfpppdpkgokiejbjfohfohhmk)
- Others: HubSpot Sales 2.8 / 8.2K / 1M — [CWS](https://chromewebstore.google.com/detail/oiiaigjnkhngdbnoookogelabohpglmd). Momentum (in-app purchases) 4.0 / 13.7K / 2M — [CWS](https://chromewebstore.google.com/detail/laookkfknpbbblfpciffpaejjkokdgca). Raindrop.io (in-app purchases) 3.6 / 787 / 400K — [CWS](https://chromewebstore.google.com/detail/ldgfbffkinooeloadekpmfoklnobpien). Bitly 3.9 / 1.6K / 500K — [CWS](https://chromewebstore.google.com/detail/iabeihobmhlgpkcgjiloemdbofjbdcic). Data Scraper 3.9 / 705 / 300K — [CWS](https://chromewebstore.google.com/detail/nndknepjnldbdbepjfgmncbggmopgden). "Vendasta Yesware" 3.4 / 1.1K / 80K — [CWS](https://chromewebstore.google.com/detail/gkjnkapjmjfpipfcccnjbjcbgdnahpjp). Magical text expander 3.8 / 3.5K / 200K, last updated Apr 4 2026 — [CWS](https://chromewebstore.google.com/detail/iibninhmiggehlcdolcilmhacighjamp)
- Neglect signals by last update date: Instapaper 4.2 / 563 / 200K, Nov 6 2024 — [CWS](https://chromewebstore.google.com/detail/ldjkgaaoikpmhmkelcgkgacicjfbofhh). Lightshot 3.4 / 7K / 2M, Jul 23 2024 — [CWS](https://chromewebstore.google.com/detail/mbniclmhobmnbdlbpiphghaielnnpgdp). ColorZilla 4.0 / 3.9K / 4M, May 22 2024 — [CWS](https://chromewebstore.google.com/detail/bhlhnicpbhignbdhedgjhgdocnmhomnp)

**Niche-incumbent check for screen capture [ML]:**
- Scrnli (recorder plus screenshot): 4.8 / 11K / 1,000,000, updated Nov 4 2026 — [CWS](https://chromewebstore.google.com/detail/ijejnggjjphlenbhmjhhgcdpehhacaal)
- Screenshot Tool – Screen Capture & Editor: 4.5 / 5.4K / 1,000,000 — [CWS](https://chromewebstore.google.com/detail/edlifbnjlicfpckhgjhflgkeeibhhcii)
- Scrolling screenshot tool: 4.8 / 2.4K / 500,000 (stale, last updated Jul 20 2023) — [CWS](https://chromewebstore.google.com/detail/mfpiaehgjbbfednooihadalhehabhcjo)
- FullPage Capture: 4.8 / 1.1K / 100,000 — [CWS](https://chromewebstore.google.com/detail/ggacghlcchiiejclfdajbpkbjfgjhfol). Full Page Screenshot – Screen Capture & Editor: 5.0 / 763 / 100,000 — [CWS](https://chromewebstore.google.com/detail/ijidfpoenjmfdabnmchmdoopghmjnjij)

**Well-rated controls in the same scan [ML]:** Mailtrack 4.8 / 11.9K / 3M; Boomerang 4.8 / 2.1K / 900K; Streak 4.8 / 6.5K / 700K; Wappalyzer 4.9 / 2K / 3M; Text Blaze 4.6 / 1.9K / 800K; GMass 4.8 / 9.2K / 400K — [CWS](https://chromewebstore.google.com/)

### Inferences
- The weak ratings concentrate in capture and recording, writing and grammar, and edu tools. All three are either crowded with free, well-rated alternatives (capture), commoditised by LLMs (grammar), or sold to school districts so that demand is bought rather than found in search (edu). They fail criterion 2 or the niche check.
- Chrome's lack of public review text in static HTML, plus the Chrome-Stats block, means "rating declined" cannot be shown from data in this session. Only "currently low" can.

### Gaps
- Historical rating trends (Chrome-Stats returned 403) and reasons for the low GoFullPage and FireShot ratings were not obtained.
- Teleparty and Language Reactor were not niche-checked, so their status is unknown.
- Chrome Web Store monetisation and fee rules were not verified (search budget).
- No Chrome extension revenue case studies were collected.

---

## Q3. Which Atlassian, Google Workspace and WordPress categories show solo-developer revenue and weak incumbents?

### Takeaway
These three marketplaces have more real gaps than Shopify, because incumbents are often a single developer, an abandoned vendor integration, or a roll-up (Appfire on Atlassian):
- **Atlassian:** an abandoned Google-built Jira↔Google Chat app, mediocre Appfire and Ricksoft Gantt apps (but too complex to build solo), and many Appfire apps at 2.3–3.8★.
- **Google Workspace:** a cluster of 2.6–3.7★ paid utilities with 400K–8M installs, several from one solo developer (Digital Inspiration), plus Drive folder-copy and Sheets↔Calendar apps rated 3.0–3.3★ and still unchallenged.
- **WordPress:** the two dominant broken-link checkers (700K installs combined) both sit at 3.8★, with complaints about false positives and forced accounts or credit cards.

No verified solo-developer revenue figure was obtained in this session (search budget exhausted).

### Cited Findings
**Atlassian, weak paid incumbents [ML]** (format: stars / reviews / installs; price at 100 users per year):
- Gantt: BigGantt (Appfire) 3.46 / 273 / 5,512; $2,090/yr — [listing](https://marketplace.atlassian.com/apps/1213016/biggantt-gantt-chart-for-jira). WBS Gantt-Chart (Ricksoft) 3.49 / 161 / 5,314; $1,320/yr — [listing](https://marketplace.atlassian.com/apps/1211768/wbs-gantt-chart-for-jira-enterprise-project-management). Gantt-Chart for Jira (Werkstack) 3.45 / 129 / 445; $1,200/yr — [listing](https://marketplace.atlassian.com/apps/28997/gantt-chart-for-jira)
  - [Review] BigGantt, Jun 11 2026: "When you remove a project from the Gantt view, it actually deletes the corresponding Jira issues from your workspace… there's no trash bin or recovery option". Feb 3 2026: "After reporting a blocking defect to support… nothing was done for 24 hours." WBS Gantt, Sep 11 2025: "It's EASY to waste a lot of time if you don't hit the SAVE button ALL THE TIME… Autosave as a feature.... naah". May 14 2025: "it only worked for 3 months out of the 6 that we used it" — [BigGantt reviews](https://marketplace.atlassian.com/apps/1213016/biggantt-gantt-chart-for-jira?tab=reviews), [WBS reviews](https://marketplace.atlassian.com/apps/1211768/wbs-gantt-chart-for-jira-enterprise-project-management?tab=reviews)
- Other Appfire apps below 3.9★ [ML]: Page Approval for Confluence 3.39 / 73 / 1,619, $770/yr; Advanced Tables 3.77 / 57 / 3,640, $1,210/yr; Markdown for Confluence 3.52 / 16 / 2,223, $1,340/yr; BigTemplate 3.84 / 66 / 3,546; Comala Document Approval 2.29 / 6 / 212; Surveys for Jira 3.81 / 22 / 365 — [Atlassian Marketplace](https://marketplace.atlassian.com/)
  - [Review] Page Approval, Oct 18 2024: "there is a 'Planned transition to a paid model for the first half of October 2024', so it's no longer free to use". Nov 15 2024: "'You do not have a valid license'". Dec 12 2025: "No version for Confluence 10" — [reviews](https://marketplace.atlassian.com/apps/144/page-approval-for-confluence?tab=reviews)
- Abandoned or low-rated vendor integrations [ML]: **Google Chat for Jira Cloud (Google LLC): 2.3 / 109 / 10,994, latest cloud release 2021-11-11, free** — [listing](https://marketplace.atlassian.com/apps/1218638/google-chat-for-jira-cloud). Also GitHub for Atlassian 3.32 / 511 / 138,591; GitLab for Jira 2.76 / 342 / 32,198; Sentry 2.47 / 100 / 16,264; Zendesk Support for Jira 3.36 / 143 / 12,841. These are vendor-owned and cannot be cloned.
- Proven-paid chat-connector category [ML], prices at 100 users per year: WISOFT Slack Connector for Jira (appears in the top-grossing list) 3.38 / 57 / 1,120, $4/mo for ≤10 users, $900/yr — [listing](https://marketplace.atlassian.com/apps/1214122/slack-connector-for-jira). Move Work Forward Advanced Microsoft Teams Connector 4.07 / 43 / 1,186, $990/yr. yasoon Microsoft 365 for Jira 4.63 / 198 / 5,857, $3,800/yr. yasoon Teams for Jira 4.54 / 30 / 827, $2,100/yr — [Atlassian Marketplace](https://marketplace.atlassian.com/)
- Solo-named vendors with paid apps exist but are small [ML]: Glossary for Jira (Oleksii Smargunov), 14 installs, $3.50/mo for 10 users; Snapshot visual feedback (James Loughran), 21 installs, $10/mo for 10 users; Tooltip Express (Djordje Stojanovic), 47 installs — [Atlassian Marketplace](https://marketplace.atlassian.com/)

**Google Workspace, weak paid utilities [ML]** (rating / review count / installs):
- Digital Inspiration (Amit Agarwal; the listing calls him a "Google Developer Expert"):
  - Email Studio for Gmail 2.6★ / 326 / 566K+, updated Jun 12 2026 — [listing](https://workspace.google.com/marketplace/app/email_studio_for_gmail/60106804857)
  - Email Address Extractor 3.4★ / 359 / 404K+, updated Apr 6 2026 — [listing](https://workspace.google.com/marketplace/app/email_address_extractor/1045030766919)
  - Save Emails and Attachments 3.7★ / 724 / 2M+, updated Nov 2 2026 — [listing](https://workspace.google.com/marketplace/app/save_emails_and_attachments/513239564707)
  - Email Spreadsheets 3.7★ / 628K+. Mail Merge with Attachments 4.3★ / 9M+. Email Notifications for Forms 4.0★ / 21M+. Document Studio 4.2★ / 6M+.
  - All are "Free of charge with paid features". The Email Studio listing says its developer is "the developer behind… several other popular Google add-ons that have 1,000,000+ users" [Dev-site claim on listing].
- Copy folder in Google Drive (Lincoln Apps "Awesome Files"): 3.3★ / 131 / 661K+, paid features, updated Nov 17 2025 — [listing](https://workspace.google.com/marketplace/app/copy_folder_in_google_drive/891769470715). Folder Copy (ez34.net): 3.0★ / 229K+.
- Sheets2GCal (GCalTools): 3.2★ / 133 / 8M+, paid features (individual or domain subscriptions), updated Nov 6 2026 — [listing](https://workspace.google.com/marketplace/app/sheets2gcal/137564231775). Event-o-Matic 3.5★ / 674K+. Sync Sheets to Calendar (EventTrakr) 1.9★ / 56K+.
- Other low-rated apps with high installs [ML]: Gmail to Notion 2.9★ / 77 / 1M+ (free) — [listing](https://workspace.google.com/marketplace/app/gmail_to_notion_save_emails_to_notion_da/798174831908). Mail merge for Google Docs 3.5★ / 4M+. Doc Tools (Ablebits) 3.4★ / 5M+. Remove Duplicates (Ablebits) 3.3★ / 3M+. pdfFiller 2.0★ / 2M+. Lumin PDF 3.7★ / 22M+ — [Workspace Marketplace](https://workspace.google.com/marketplace)

**WordPress [ML]:**
- Broken Link Checker (WPMU DEV): 500K+ active installs, rating 76/100 (3.8★), 605 ratings (365×5★, 134×1★), updated Oct 13 2026 — [wp.org](https://wordpress.org/plugins/broken-link-checker/)
- Broken Link Checker by AIOSEO: 200K+, 76/100, 87 ratings (57×5★, 22×1★), updated Sep 30 2026 — [wp.org](https://wordpress.org/plugins/broken-link-checker-seo/)
- Other WordPress plugins with weak ratings and high installs (not pursued): ExactMetrics 50/100 / 1,546 ratings / 200K; Elementor Image Optimizer 34/100 / 1M; Ally accessibility 58/100 / 500K; Jetpack 74/100 / 3M — [api.wordpress.org](https://api.wordpress.org/plugins/info/1.2/?action=query_plugins&request[browse]=popular)

**Platform rules found [Platform-doc]:** Google apps that use restricted scopes (such as full Gmail or Drive access) must pass restricted-scope verification. Apps that access restricted data "from or through a third-party server must undergo an annual security assessment" (CASA), and must reverify "at least every 12 months" — [Google](https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification)

### Inferences
- Atlassian pricing scales per user, so a 100-user customer pays $900–$3,800 a year even for simple connector apps. A few hundred installs can therefore produce meaningful revenue. Treat this as an inference: Atlassian's revenue-share rate was not verified.
- Digital Inspiration's portfolio (one solo developer, multiple paid add-ons with 400K–21M installs) is the closest thing to "proven solo-developer marketplace revenue" found here. But no revenue figure was verified, and several of his apps show neglect: Rhino-runtime breakage and complaints about unanswered support tickets.
- Apps that run purely in Apps Script ("runs entirely within your Google account", as Email Address Extractor's listing says) appear to avoid the server-side CASA assessment, which is a structural advantage for a solo clone. This reading of Google's doc should be confirmed before relying on it.

### Gaps
- No verified solo-developer revenue figures (Indie Hackers, Starter Story, Atlassian partner reports) — search budget exhausted.
- Atlassian revenue share for Forge vs Connect apps, the Connect deprecation timeline, and the Data Center end-of-life schedule were all unverified (the primary-doc fetch attempts failed).
- Workspace search cards don't show review counts, so many apps have only a rating plus an install bucket.

---

## Q4. Shortlist: which opportunities survive the mandatory niche-incumbent check?

### Takeaway
Six candidates survive the letter of the check. None is a slam dunk. The best combinations of proof, build simplicity and weak incumbents are **(1) WordPress broken-link checker**, **(2) Drive folder copy** and **(3) Shopify backup/undo**; the third has a fast-closing window. The other three are conditional or small.

### Cited Findings

#### 1. WordPress — broken-link checker with no account or card, local-first, and low false positives
- **Incumbents [ML]:** WPMU DEV BLC 500K+ installs, 3.8★/605, with 22% of ratings at 1★. AIOSEO BLC 200K+, 3.8★/87, with 25% at 1★ — [WPMU](https://wordpress.org/plugins/broken-link-checker/), [AIOSEO](https://wordpress.org/plugins/broken-link-checker-seo/)
- **Paid traction:** monetised through a WPMU DEV membership upsell (review: "I don't want to upgrade my membership") and AIOSEO's paid scanning ("the question should actually be 'if you do this, we will charge your credit card'"). No revenue figures.
- **Complaints [Review]** — [WPMU reviews](https://wordpress.org/support/plugin/broken-link-checker/reviews/), [AIOSEO reviews](https://wordpress.org/support/plugin/broken-link-checker-seo/reviews/):
  - Oct 29 2026 (WPMU): "Hundreds of false positives… When there are 20 items on the screen and you click 'Select All' it selects All items… it unlinked EVERY link (300+)"
  - Sep 2 2026: "The database tables were corrupted during the last update"
  - Aug 10 2026: "Editors used to have access to the local link checker, but… only Admin accounts"
  - AIOSEO, Sep 29 2026: "Does not function without account/credit card"
  - Sep 17 2026: "Even for a 'free' account creditcard details are required"
  - Jun 10 2026: "Every broken link reported is not broken"
  - Apr 20 2026: "I didn't like providing credit card details to download a free plugin"
- **Spin:** a self-contained local scanner (no SaaS account), automatic re-verification to cut false positives (HEAD→GET fallback, 403/429 and bot-wall detection, retry windows), paginated bulk actions that only touch visible selections, an editor role capability, and weekly email digests. Free core plus Pro (scheduling, external-link monitoring, multisite).
- **Niche-incumbent check [ML]:** a wp.org search for "broken links" returns only tiny dedicated alternatives: check-for-broken-links (2K installs, 4.0/6 ratings) and broken-link-notifier (1K, 4.8/14). The rest are SEO suites (Rank Math 4M; Internal Links 100K) — [wp.org API](https://api.wordpress.org/plugins/info/1.2/?action=query_plugins&request[search]=broken%20links). **Passes.**
- **Platform risk:** wp.org review and guideline moderation; buyers are price-sensitive. External SaaS audit tools are substitutes (not measured here).
- **Build:** 2–4 weeks (PHP crawler on Action Scheduler, link-status cache, admin UI).
- **Verdict: GO-candidate, with a moderate revenue ceiling.**

#### 2. Google Workspace — "Copy/clone Drive folder" done right
- **Incumbents [ML]:** Copy folder in Google Drive (Lincoln Apps) 3.3★/131/661K+, paid features. Folder Copy 3.0★/229K+ — [listing](https://workspace.google.com/marketplace/app/copy_folder_in_google_drive/891769470715)
- **Complaints [Review]:**
  - Jun 16 2026: "A ripoff plugin with ripoff prices. None of the plans offer unlimited data transfers and the prices are steep… anyone can do but literally for free just by asking AI to write them their own script."
  - Oct 18 2026: "It was very hard for me to cancel my subscription."
  - Oct 26 2026: "It says its installed but I cant find it in the apps or anywhere."
  - The developer reply on Aug 24 2026 concedes "there are free alternatives, including custom scripts".
- **Spin:** unlimited folder copies for a flat low price, resumable jobs that survive the Apps Script execution limit, shared-drive support, optional preservation of sharing permissions, a progress UI, and one-click cancel.
- **Niche-incumbent check [ML]:** searches for "copy folder" and "duplicate folder" surface no well-rated dedicated alternative. Results are Power Tools 3.6★, Doctopus (edu) and duplicate finders — [search](https://workspace.google.com/marketplace/search/copy%20folder). **Passes.**
- **Platform risk:** the Drive restricted scope requires verification, and an annual CASA assessment applies if data goes through a server [Platform-doc]. Google could ship native folder copy (not verified).
- **Build:** 2–4 weeks.
- **Verdict: GO-candidate.** Validate pricing tolerance first.

#### 3. Shopify — backup plus granular "undo" for AI and bulk edits (Rewind challenger)
- **Incumbent:** Rewind 4.3★/632, $19–$99/mo, with a 2025 price rise from $9 to $19, coarse restores, weekend support gaps and billing-after-cancel complaints (quotes in Q1) — [listing](https://apps.shopify.com/backup)
- **Spin:** a change timeline with per-item and per-field diff and undo ("undo Sidekick's last bulk edit"), granular restore (single blog post or product), snapshots of manual collection sort orders where the API allows, export to the merchant's own storage, transparent flat pricing and easy cancel.
- **Niche-incumbent check [ML]:**
  - BackupMaster 4.8/124 (free, $19/mo or $205.20/yr; launched 2017) — [listing](https://apps.shopify.com/backup-master)
  - TinyBackup 5.0/59 (free, $11, $17, $33; Jan 2024) — [listing](https://apps.shopify.com/tinybackup)
  - Syncora 4.7/19 (free, $9.99, $19.99; Jan 2025) — [listing](https://apps.shopify.com/syncora-backup-restore)
  - New in 2026, all with 0–2 reviews: Avada Backups (Apr 9 2026, free), Savepoint (Jul 15 2026; free/$9/$19), StoreVault (Aug 14 2026; $4.50–$9.50), StoreArk (Aug 25 2026) — [search](https://apps.shopify.com/search?q=backup+restore)
  - **Passes on the letter (no cheap app with many reviews), but the window is closing fast.**
- **Platform risk:** Shopify revenue share is favourable (0% on the first $1M) [Platform-doc]. Some objects can't be fully restored through the API (Rewind's own replies cite inventory and manual sort order). Shopify-native versioning is a risk (unknown).
- **Build:** 3–6 weeks. Correct restores are the hard part.
- **Verdict: Conditional GO.** Speed and the "AI-edit undo" positioning are the wedge.

#### 4. Google Workspace — Sheets ↔ Google Calendar sync plus timesheets
- **Incumbents [ML]:** Sheets2GCal 3.2★/133/8M+ (paid features). Event-o-Matic 3.5★/674K+. EventTrakr 1.9★/56K+ — [Sheets2GCal](https://workspace.google.com/marketplace/app/sheets2gcal/137564231775)
- **Complaints [Review]:**
  - Oct 4 2026: "Does not work, it was easier to script it myself in AppsScript"
  - Mar 14 2026: "Doesn't work with the Sheets app, and right now I'm in a doom loop trying to login to Workspace."
  - Developer post, Jul 16 2025: "a glitch with Google's OAuth verification system… preventing all our users from opening the add-on today."
  - Positive use case, Mar 24 2026: calendar-to-Sheets "automated timesheet system… imports the Calendar event colors… as project codes".
- **Spin:** two-way sync built for timesheets and billable hours (colour or tag mapped to project, weekly invoice-ready rollups).
- **Niche-incumbent check [ML]:** Sheet.Cal 2-way sync 4.5★/25K+. Calendar to Sheets (Nicework) 4.8★/4K+. Calendar Sync for Sheets 5.0★/359. Calrows 5.0★/70 — [search](https://workspace.google.com/marketplace/search/sheets%20to%20calendar). A credible but small incumbent exists. **Passes narrowly.**
- **Platform risk:** OAuth verification dependence (as the 2025 outage shows).
- **Build:** 2–4 weeks.
- **Verdict: Conditional.** Differentiate on timesheets, not on sync.

#### 5. Google Workspace — Gmail contact or email-address extractor to Sheets
- **Incumbent [ML]:** Email Address Extractor (Digital Inspiration) 3.4★/359/404K+, paid features — [listing](https://workspace.google.com/marketplace/app/email_address_extractor/1045030766919)
- **Complaints [Review]:**
  - Oct 27 2025: "Very poor app. Doesn't do what it says, very misleading."
  - Aug 20 2024: "The extraction process was incomplete and over complicated"
  - Dec 18 2024: install fails on a second Gmail account, "Bad gateway"
  - Feb 26 2026: "not free at all!"
- **Spin:** reliable, resumable extraction (label or date filters, dedupe, name parsing, enrichment-free), runnable across multiple accounts, with transparent one-time or yearly pricing.
- **Niche-incumbent check [ML]:** the top "email extractor" results are a different job (Tomba is an email-finder data service, 4.6★/102K+; Sheet SMS extracts from websites, 214 installs) — [search](https://workspace.google.com/marketplace/search/email%20extractor). **Passes.**
- **Platform risk:** the Gmail restricted scope requires verification, and CASA applies if processing goes through a server [Platform-doc]. The incumbent avoids a server by running in Apps Script.
- **Build:** 1–3 weeks.
- **Verdict: Conditional.** Small but fast. It could be bundled with #2 and #4 as a "Workspace utilities" portfolio.

#### 6. Atlassian (Jira Cloud) — Google Chat notifications and actions for Jira
- **Incumbent:** Google's free app 2.3★/109/10,994 installs, last release Nov 2021 — [listing](https://marketplace.atlassian.com/apps/1218638/google-chat-for-jira-cloud)
- **Complaints [Review]:**
  - Aug 14 2026: "Doesn't work. Impossible to set up. Requires me to turn off security settings"
  - Feb 25 2026: "The app is very old, the project search and the notifications when selecting All projetos does not work"
  - Aug 18 2025: wants notifications only "whereever I'm tagged, watching, assigned"
  - Jun 17 2025: "Integration fails with no indication on why or how to fix it."
  - Apr 15 2025: "Error in last step"
- **Paid proof is adjacent:** the Slack, Teams and M365 connectors cost $900–$3,800/yr at 100 users (Q3).
- **Spin:** a Forge-native app with per-user and per-team filters (assigned, mentioned, watching, or a JQL filter), threaded updates, and Spanish and other localised issue types.
- **Niche-incumbent check [ML]:**
  - Canary Apps' Google Chat for Jira: 4.06★/4 reviews/121 installs, $5/mo for ≤10 users, $1,200/yr at 100 users — [listing](https://marketplace.atlassian.com/apps/1233261/google-chat-for-jira)
  - Move Work Forward's Advanced Google Chat for Jira: 5.0★/3/407 — [listing](https://marketplace.atlassian.com/apps/1233491/advanced-google-chat-for-jira)
  - On the Workspace side: Canary's "Jira Watcher" 5.0★/27K+, Redwerk's MyJiraBot 4.3★/17K+, and Google's "Jira for Google Chat" 3.9★/1M+ — [search](https://workspace.google.com/marketplace/search/jira)
  - **Passes on review counts, but incumbents exist, and their tiny install bases (121–407) suggest weak willingness to pay.**
- **Platform risk:** Google could refresh its free app. Atlassian could ship a first-party integration.
- **Build:** 2–4 weeks.
- **Verdict: Conditional, low priority.**

### Inferences
- Bundling 2, 4 and 5 under one Google Workspace publisher brand would share OAuth verification cost and cross-sell, mirroring how Digital Inspiration operates.
- On Shopify, the only defensible wedge found is positioning around the new AI-edit risk, and four 2026 entrants already target backup. Move within weeks or skip it.

### Gaps
- Live price points for Lincoln Apps, Digital Inspiration, GCalTools and AIOSEO BLC Pro were not captured.
- Install-to-paid conversion for any candidate is unknown.
- Whether Google Drive or Shopify plans native features (folder copy, product version history) was not verified.

---

## Q5. Kill list: which ideas fail the niche-incumbent or simplicity check?

### Takeaway
Most "bad incumbent" signals are already answered by cheap, well-rated apps with many reviews, or the idea needs a build too heavy for a solo founder.

### Cited Findings
- **Chrome full-page screenshot** (GoFullPage 3.4/84.8K/11M; FireShot 2.1/53K/3M; Awesome Screenshot 3.2/29.6K/4M). Killed by Scrnli 4.8/11K/1M, Screenshot Tool 4.5/5.4K/1M and FullPage Capture 4.8/1.1K [ML] — [CWS search](https://chromewebstore.google.com/search/full%20page%20screenshot)
- **Chrome screen recorders** (Loom 2.8, Screencastify 3.7, Vidyard 3.4). Killed by Scrnli 4.8/11K/1M; it also overlaps the AI-video researcher's scope [ML] — [Scrnli](https://chromewebstore.google.com/detail/ijejnggjjphlenbhmjhhgcdpehhacaal)
- **Chrome edu tools** (Kami 2.5/18M users; Read&Write 2.8/19M). Demand is bought through district sales (inference) [ML] — [Kami](https://chromewebstore.google.com/detail/ecnphlgnajanjnkcmbpancdjoidceilk)
- **Shopify bundles, search, order printer, subscriptions** (Shopify's own apps at 2.6–3.8★). Killed by Kaching 5.0/6,636, Searchanise 4.7/1,267, Order Printer Pro 4.9/3,053 and Appstle 5.0/9,219, all with free plans [ML] — [Shopify search](https://apps.shopify.com/search?q=bundle)
- **Shopify helpdesk** (Gorgias 4.3/708). Killed by Chatty 4.9/1,898 and Commslayer 4.9/243, both with free plans [ML]. **QuickBooks sync** (Bold 3.2/167): killed by A2X 4.9/362 and Intuit 4.6/3,364 (free) [ML]. **SEO** (Yoast 4.3/174): killed by Booster 4.8/5,487 (free plan) [ML] — [Shopify search](https://apps.shopify.com/search?q=helpdesk)
- **Atlassian Gantt.** Strong demand, with weak BigGantt and WBS ratings and prices of $1,320–$2,090/yr at 100 users. It fails simplicity: robust dependency scheduling and drag-drop at scale is not a 2–6 week build. Incumbents also exist: DevSamurai Project Management 4.34/175/2,951; GanttTable 4.69/16/1,301; Tempo Gantt 4.2/61/6,269 [ML] — [listing](https://marketplace.atlassian.com/apps/1223423/project-management-resource-planning-gantt-chart-for-jira)
- **Confluence page approval** (Appfire 3.39, switched from free to paid in Oct 2024). Crowded: AppFox Approvals 4.4/21/933, AppFox Workflows 4.65/25/924, AURA Workflow 5.0/11/286, Breeze 4.75/15/181, Approval Path 5.0/5/50, Comala Document Management 4.68/177/5,870 [ML] — [search](https://marketplace.atlassian.com/search?query=approval)
- **Confluence Markdown and Mermaid rendering** (Render Markdown 3.46, last release Oct 2021; Atlassian Labs Mermaid 2.99; Mermaid Chart 2.84). Covered by Just Add+ (Markdown, diagrams and code) 4.29/50/7,932, weweave Mermaid 4.58/15/2,156 and Stratus Mermaid 4.02/23/6,167 [ML] — [Just Add+](https://marketplace.atlassian.com/apps/1211438/just-add-embed-markdown-diagrams-code-in-confluence-git)
- **Email Studio-style Gmail automation** (2.6★; broken in June 2026 by the Apps Script Rhino deprecation). [Review] Jun 12 2026: "Execution failed. The Rhino runtime is deprecated and no longer supported". Sep 12 2026: "Just does what Gmail can already do natively". Recurring sends are covered by "Recurring emails for Gmail" 4.9★/41K+ [ML] — [Email Studio](https://workspace.google.com/marketplace/app/email_studio_for_gmail/60106804857), [search](https://workspace.google.com/marketplace/search/recurring%20email)
- **Forms quiz timers, response limiters, form notifications and mail merge.** All crowded with 4.6–4.9★ apps with 1M–16M installs: Everest Web Deals 4.8/1M+; Monkey Cube Timer 4.8/5M+; LIMIT IT 4.7/6M+; Form Notify 4.6/855K+; YAMM 4.7/16M+; Mailmeteor 4.9/7M+ [ML] — [Workspace search](https://workspace.google.com/marketplace/search/quiz%20timer)
- **Save Gmail attachments to Drive** (Digital Inspiration 3.7/724/2M+). Not shortlisted: no complaint quotes were captured (fails criterion 4), and small new 4.8–5.0★ apps exist (Attachment Hippo 993 installs; Dioveo; HomeDrop) [ML] — [search](https://workspace.google.com/marketplace/search/gmail%20attachments)

### Inferences
- The biggest structural lesson: high-visibility marketplaces with solicited reviews (Shopify, Chrome capture) are largely competed away. Gaps survive in duller, per-seat or utility niches (Workspace add-ons, WordPress utilities, Atlassian connectors) where incumbents are solo developers, neglected vendor apps or roll-ups.

### Gaps
- HubSpot, Slack, Figma Community, Wix, Squarespace and Zapier marketplaces were not mined. Their listing pages are JS-rendered, and the search budget was exhausted.
