# Niche incumbent check: professional AI/productivity clones (Claude organiser extension, bookkeeper formula tool, compliance-aware advisor LinkedIn writer)

Research date: 2026-11-06. Live pages fetched today are marked "(fetched 2026-11-06)". Chrome Web Store (CWS) counts marked "CWS-displayed" were read from the live store listing today. Those are the store's own numbers, which is the closest thing to verified here. Labels used: **vendor-claimed** (the company's own page), **third-party estimate / secondary** (listicles, competitor blogs, affiliate pages), **CWS-displayed** (store listing). Competitor-authored comparison pages are flagged as biased.

Reddit coverage note: every search aimed at Reddit communities (r/ClaudeAI, r/excel, r/Bookkeeping, r/CFP and others) returned zero Reddit threads. This looks like a limit of the search tool, not proof that nobody is talking about it. Demand evidence below comes from public feature-request trackers, vendor traction and review sites.

---

## 1A. Claude extension: what does claude.ai already do natively (Nov 2026)?

### Takeaway
As of Anthropic's release notes dated 5 Nov 2026, claude.ai still has **no user-created folders, no per-chat Markdown/PDF export and no general prompt library**. The report's kill condition ("Claude ships native folders/search") has therefore **not** fired for folders. It has partly fired for search: Claude can now search past chats conversationally, the sidebar searches titles and message content, and there are Projects, starring, memory and an account-wide data export. All of this cuts into the "search" and "organisation" value of the extension.

### Cited Findings
- **Release notes, checked up to 5 Nov 2026, contain no entries for folders, starring/favourites, sidebar organisation or Markdown/PDF chat export.** The only saved-prompt feature listed is "/slash command" prompt shortcuts in Claude in Chrome (Max, 16 Sep 2025) — [Claude release notes (fetched 2026-11-06)](https://support.claude.com/en/articles/12138966-release-notes)
- **Past-chat search inside Claude:** launched 11 Aug 2025 for Max/Team/Enterprise ("Claude can search past chats to continue earlier context"). On 2 Mar 2026, memory built from chat history reached all users including Free — [Claude release notes](https://support.claude.com/en/articles/12138966-release-notes)
- **Memory timeline:** memory summary from 11 Sep 2025 (Team first). Max on 23 Oct 2025, then Pro. On 10 Jul 2026 it became individual categorised entries. On 25 Aug 2026 it began working across chat and Cowork, with editable "Topics" in Settings > Memory — [Claude release notes](https://support.claude.com/en/articles/12138966-release-notes). Each project gets its own separate memory, and Team/Enterprise users get incognito chats — [Anthropic: Bringing memory to teams](https://www.anthropic.com/news/memory)
- **Projects:** project permissions and sharing for Team/Enterprise arrived 1 Aug 2025. On 7 Jul 2026 chat and Cowork began sharing "one home, with one place for projects and artifacts" (Max first). On 16 Sep 2026 Projects started carrying over into the unified Claude experience, rolling out gradually to Pro/Max — [Claude release notes](https://support.claude.com/en/articles/12138966-release-notes)
- **Starring:** the official help centre says starring a project pins it to the left panel — [Claude help: projects](https://support.claude.com/en/articles/9519177). A third-party tutorial shows chats being starred from the sidebar three-dot menu — [Guideflow tutorial](https://www.guideflow.com/tutorial/how-to-star-a-chat-from-the-sidebar-in-claudeai) (secondary, not confirmed against an official page)
- **Sidebar search:** a changelog entry surfaced in search says a bug that made chat search return no results was fixed, "so search finds chats by title and message content again." The source page was not isolated; the likely source is [Claude changelog](https://claude.com/docs/cowork/changelog). A vendor page (AI Toolbox, a competitor) says native search has "no date, role, or exact-match filters" — [AI Toolbox (vendor, biased) (fetched)](https://www.ai-toolbox.co/claude-chrome-extension)
- **Native export is account-wide only:** Settings > Privacy > Export data sends an emailed link covering all conversations. A third-party guide says Projects data and memory are not included and the link expires in 24 hours — [TakeoutDay guide (secondary)](https://takeoutday.org/guides/how-to-export-claude-data). Third-party export guides also report that no Anthropic API lists or reads consumer Projects (as of May 2026). This came from the search result set and the exact page was not isolated: [aimemory.pro](https://aimemory.pro/blog/claude-projects-export-guide-2026) / [amitkoth.com](https://amitkoth.com/export-claude-projects-data/) (secondary)
- **Free-plan Projects cap is disputed:** several 2026 guides say Free accounts get 5 projects and paid plans get unlimited. An older guide says Projects are paid-only — [Northlab (secondary)](https://northlabapps.com/blog/claude-projects-explained/)
- **Users keep asking for folders:** several 2026 public feature requests ask for chat folders, sidebar categories or subfolders inside Projects. These include a 13 Jun 2026 request noting "a Claude.ai Project has no organization below the Project itself" — [claudeissues mirror #68262](https://claudeissues.com/issue/68262-feature-subfolders-nested-organization-within-a-claude-ai-project-web-desktop-mo), [#68491](https://claudeissues.com/issue/68491-feature-request-folder-category-organization-for-conversation-sidebar), [GitHub anthropics/claude-code #35431](https://github.com/anthropics/claude-code/issues/35431). Some of these were filed on the Claude Code repo and reportedly closed as off-topic.

### Inferences
- Folders are still a real native gap. But the "unified Claude experience" rolling out from Sep 2026 is reshaping the sidebar around Projects, artifacts and Cowork. That is the moment Anthropic would add organisation features, so platform risk is high in the next 6–12 months.
- Native conversational search plus memory weakens "full-text search" as a reason to pay. Exact-match and filtered search is still a sliver, but a thin one.
- Prompt library: native Skills and slash-command prompts in Chrome partly cover reusable prompts for power users.

### Gaps
- Could not confirm from an official page whether conversational chat search ("search and reference chats") is now available on Pro and Free, or only on Max/Team/Enterprise.
- No official Anthropic roadmap statement on folders found.
- No r/ClaudeAI threads surfaced (tool limitation).

---

## 1B. Claude extension: existing third-party extensions (folders / search / export / prompts)

### Takeaway
The niche is **already crowded**. At least 12 Claude-specific or multi-AI extensions offer folders, full-text search, Markdown/PDF export and prompt libraries. The leaders are AI Chat Exporter (**100,000 users, 4.9★, about 1K ratings, CWS-displayed**) for export, and AI Toolbox (**40,000+ users, vendor-claimed**) for a full Superpower-style feature set at $9.99/mo. One small listing is almost exactly the proposed product (local-first, folders, full-text search, Markdown export, $29 one-time, Pro free until 31 Dec 2026).

### Cited Findings
**Leaders (by traction)**
- **AI Chat Exporter: Save Claude as PDF, MD and more** (ai-chat-exporter.net): **100,000 users, 4.9/5, about 1K ratings, updated 19 Oct 2026, v3.10.1** (CWS-displayed). It exports PDF, Markdown, Text, CSV and JSON. It also exports Projects as ZIP or merged MD, Cowork sessions and temporary chats, with toggles for artifacts, thinking and tool use. Free tier: unlimited non-PDF exports, 3 PDFs per day. Paid PRO raises the PDF cap to 30 or 100 per day. Everything except PDF is generated locally; PDFs go to the developer's server — [CWS listing (fetched 2026-11-06)](https://chromewebstore.google.com/detail/ai-chat-exporter-save-cla/elhmfakncmnghlnabnolalcjkdpfjnin)
- **AI Toolbox (formerly ChatGPT Toolbox / Claude Toolbox)** by Infi Developments has a Claude module with:
  - full-text search with exact-match
  - folders with unlimited subfolders
  - message bookmarks and an Artifact Vault
  - Smart Tags and an `@@` context-mention feature
  - a prompt library and prompt chains
  - TXT/MD/JSON/PDF export, per chat or in bulk

  Pricing: Free (2 root folders, 25 search results, TXT-only export), **Premium $9.99/mo**, Lifetime $49.50 for one module, All-Access Lifetime $99.50 (ChatGPT, Gemini, Claude, Grok), Teams $15/seat/mo. Claims **40,000+ users, 4.7/5** (vendor-claimed, apparently across modules). Chromium only, no Firefox — [AI Toolbox Claude page (vendor) (fetched)](https://www.ai-toolbox.co/claude-chrome-extension); [AI Toolbox press page (vendor)](https://www.ai-toolbox.co/press). A comparison blog gives 40,000 users and 4.8 from 996 reviews (secondary, 14 Oct 2026) — [Backrun (fetched)](https://backrun.co/blog/claude-toolbox-chrome-extension). Described as a two-person company founded Sep 2024 (vendor-sourced profile) — [EveryDev](https://www.everydev.ai/tools/ai-toolbox)

**Mid/small Claude-specific listings**
- **Claude Toolbox: Chat History Search, Bookmarks & Export**: about 6,000 users, 4.0 (68 reviews), updated 22 May 2026 (secondary) — [Backrun](https://backrun.co/blog/claude-toolbox-chrome-extension)
- **Claude Chat Exporter**: 2,000 users, 4.2 (CWS snippet via search) — [CWS](https://chromewebstore.google.com/detail/claude-chat-exporter/fagmaagfcmfdncfgngnbfboohodcofcd)
- **Toolbox for Claude: Export, Folders & Prompts** (browserlab.io): **1,000 users, 4.7 (25 ratings), updated 2 Mar 2026** (CWS-displayed). Features: nested folders up to 5 levels, export to PDF/MD/HTML/JSON/TXT, a prompt library and enhancer, pinned messages. Free plan: 2 folders and 5 exports a day. Premium price not shown — [CWS listing (fetched)](https://chromewebstore.google.com/detail/toolbox-for-claude-export/hhbcdmmjedmlhkhlkohphknmbinblhjh)
- **Claude Exporter** (rxliuli): **766 users, 5.0 (1 rating), updated 5 Nov 2026** (CWS-displayed). Exports Markdown, HTML and ZIP with media. Free up to 1,000 messages per task (MD only); Pro unlocks the rest — [CWS listing (fetched)](https://chromewebstore.google.com/detail/claude-exporter/ifigplgihgdedekfaelihglkhdfogbme)
- **Chat Folders, Search & Export for Claude™** (organizerlabs.com): **6 users, no ratings, updated 31 Oct 2026** (CWS-displayed). Features: full-text search with exact-phrase and exclusion operators, folders and pins, local stats, Markdown export, and "data stays in the browser, no analytics." Free: 3 folders. **Pro: $29 one-time**, adding smart folders, scheduled ZIP backups, PDF/bulk export and Obsidian frontmatter. Pro is free for installs before 31 Dec 2026. *This is close to a feature-for-feature version of the proposed product, already shipped* — [CWS listing (fetched)](https://chromewebstore.google.com/detail/chat-folders-search-expor/dnopfmakdomfdemhceekofglenkigadl)
- **Superpower for Claude** (Sulfurbyte): usage counter, PDF/MD export, saved prompts with variables, prompt chains, message queue, wide chat. Rated 4.9 in a search snippet; no user count found. Freemium — [AlternativeTo](https://alternativeto.net/software/superpower-for-claude/about/) (403 on fetch; details from search snippet)
- **Chat Manager for Claude**: folders, tags, prompt library, export. Free: 5 folders, 20 tags, unlimited prompts, Markdown export. Pro: unlimited folders, sync, history import — [CCM site](https://uy-scuti100.github.io/ccm/)
- **Chat Folders for Claude** (v0.2.2, local-only storage, title-only search) — [developer post on DEV](https://dev.to/hssolution/chat-folders-for-claude-sidebar-folders-and-exporting-a-virtualised-chat-to-markdown-4khc)
- Other listings found in a CWS search: Claude Organizer (about 52 users), Folders for Claude (about 25 users), Claude Folders, Nest for Claude, Claude Project Downloader, and "Folders, Search & Export for ChatGPT & Claude" — [CWS search results](https://chromewebstore.google.com/detail/claude-organizer-folders/pnbhfiebkknicpbljchmgibnpmlgebif); user counts from search snippets via [Backrun / search](https://backrun.co/blog/claude-toolbox-chrome-extension)
- **Firefox**: a "Folders for Claude" Firefox add-on exists (by Daan25) — [Firefox add-on mirror](https://firefox.marketplace.browsertotal.com/ja/firefox/addon/folders-for-claude/)

**Multi-AI organisers covering Claude**
- **Foldif**: free; the same folders work across Claude, ChatGPT and Gemini — [Foldif guide (vendor)](https://foldif.com/guides/organize-claude-conversations)
- **Easy Folders**: freemium with 5 free folders (secondary review; platform coverage per listicle) — [G2 seller page](https://www.g2.com/sellers/easy-folders)
- **LLMnesia**: a full-text index across ChatGPT, Claude, Gemini and 10+ platforms; **AI Hub**: unified ChatGPT/Claude/Gemini workspace — [LLMnesia comparison (vendor)](https://www.llmnesia.com/compare/llmnesia-vs-superpower-chatgpt)
- **Superpower ChatGPT (the clone source) is still ChatGPT-only** per competitor comparison pages — [LLMnesia (vendor, biased)](https://www.llmnesia.com/compare/llmnesia-vs-superpower-chatgpt)

### Inferences
- The claim "Claude has no equivalent mature folders/search/export extension" is **false**. AI Toolbox is a direct Superpower-for-Claude equivalent at about the proposed price ($9.99 vs $8). Export is commoditised by a free 100k-user tool.
- The price anchor is weak: $29 one-time, $49.50 lifetime, and free exporters already exist. A $64/yr subscription would have to beat lifetime deals.
- "Local-first, no newsletter" is not a moat. Several listings already claim local storage and no tracking (organizerlabs, Chat Folders for Claude, AI Toolbox's IndexedDB).

### Gaps
- Could not read AI Toolbox's Claude-module CWS listing directly, so its 40k figure stays vendor-claimed and may combine all modules.
- No revenue data for any Claude extension.
- Superpower for Claude user count not found.

---

## 1C. Claude extension: platform blockers, demand and VERDICT

### Takeaway
The main blockers are (1) Anthropic shipping folders during the ongoing sidebar unification, (2) DOM/internal-API breakage, since there is no official consumer chat-history API, and (3) a saturated CWS category with lifetime-deal price anchors. **Verdict: gap FALSE (high confidence)** as the report stated it. The native folder gap is real, but it is already filled by a dozen extensions.

### Cited Findings
- Projects and artifacts are being moved into a unified chat+Cowork home (Jul–Sep 2026 rollout). Any DOM-injected sidebar folders sit on a surface that is changing right now — [Claude release notes](https://support.claude.com/en/articles/12138966-release-notes)
- No Anthropic API lists or reads consumer Projects (as of May 2026, third-party report). Extensions therefore have to scrape claude.ai's internal endpoints or DOM — [aimemory.pro (secondary)](https://aimemory.pro/blog/claude-projects-export-guide-2026)
- A developer of a competing extension describes exporting "a virtualised chat" to Markdown as technically fiddly, because claude.ai virtualises long chats — [DEV post](https://dev.to/hssolution/chat-folders-for-claude-sidebar-folders-and-exporting-a-virtualised-chat-to-markdown-4khc)
- Demand signal: repeated 2026 feature requests for folders and subfolders (see 1A), plus 100k installs of a Claude export tool and 40k (vendor-claimed) for AI Toolbox, show real demand. The open question is how much demand is left over.

### Inferences
- **VERDICT: gap FALSE. Confidence: high.**
- What remains is narrow:
  - (a) **Firefox/Safari users.** AI Toolbox is Chromium-only, though at least one small Firefox add-on exists.
  - (b) An **open-source, auditable, zero-network** organiser for privacy-sensitive professionals (lawyers, clinicians), where "verifiably local" is the product. Organizerlabs already claims this, so the edge would be open source plus security review.
  - (c) **Projects/Cowork-aware organisation**: nested folders *inside* Projects, which users are explicitly requesting.

  Each sliver is small, and Anthropic can remove (c) natively. Revenue ceiling looks like hobby or lifestyle level.
- The kill condition is mis-specified. The binding constraint is not Anthropic but AI Toolbox plus free exporters, which are already in place.

### Gaps
- No Reddit threads retrieved, so it is unknown what r/ClaudeAI users currently recommend.
- No data on churn or paid-conversion rates for Claude extensions.

---

## 2A. Bookkeeper formula tool: native AI in Excel / Google Sheets and free assistants

### Takeaway
Native AI now covers most of what the clone would do for anyone on Microsoft 365 or paid Google Workspace:
- **Copilot in Excel** comes with consumer M365 (credit-limited) and business plans (Copilot Chat "standard access"; full Copilot $18–21/user/mo). It now has agentic editing and finance/accounting skills, including reconciliations and journal entries (Frontier, Oct 2026).
- **Claude for Excel** has been GA on Claude Pro ($20) since May 2026.
- **Gemini in Sheets** generates and fixes formulas on paid Workspace.

The only users native AI does not reach are those on perpetual Excel 2016/2019, which went out of support in Oct 2025.

### Cited Findings
- **Copilot in Excel for business plans:** Copilot Chat-eligible plans (Business Basic/Standard/Premium) include "standard access". Paid Microsoft 365 Copilot Business is listed at $21/user/mo, with $18 for eligible existing customers until 31 Dec 2026. Bundles: Business Basic+Copilot $21 (promo), Business Standard+Copilot $23.50 (search-result summaries; secondary; prices vary by source) — [universal.cloud](https://universal.cloud/en/support-articles/microsoft-365-copilot-business/), [ifeeltech](https://ifeeltech.com/blog/microsoft-365-business-plan-comparison-copilot-2026), [Microsoft: Business Standard with Copilot](https://www.microsoft.com/en-us/microsoft-365/business/microsoft-365-business-standard-with-copilot)
- **Agentic Excel:** one 2026 source says Microsoft made agentic Word/Excel/PowerPoint capabilities GA and the default experience for Microsoft 365 Copilot and Microsoft 365 Premium customers on 22 Apr 2026. In Excel, Copilot plans a task, executes it in the workbook and checks the result. (Source page not isolated in the search results; see the [universal.cloud](https://universal.cloud/en/support-articles/microsoft-365-copilot-business/) / [Dynamics Smartz](https://www.dynamicssmartz.com/blog/microsoft-365-copilot-guide/) guides.)
- **The COPILOT() worksheet function was retired on 14 Sep 2026.** Microsoft points users to the Copilot pane instead — [Microsoft Support: COPILOT function](https://support.microsoft.com/en-us/excel/functions/copilot-function)
- **Consumer plans:** Copilot has been included in Microsoft 365 Personal and Family since 16 Jan 2025 (with a price increase) — [Microsoft 365 blog](https://microsoft.com/microsoft-365/blog/2025-01-16/copilot-is-now-included-in-microsoft-365-personal-and-family). Usage draws on monthly AI credits that apply in Excel — [Microsoft Support: AI credits](https://support.microsoft.com/office/68530f1a-4459-4d02-9818-8233c1f673b8). Third-party sources put the allowance at about 60 credits/month for the Personal/Family owner — [Office Watch (secondary)](https://office-watch.com/2026/copilot-access-levels-for-microsoft-365-consumer-plans-what-you-actually-get/)
- **Finance/accounting skills in Copilot for Excel:**
  - 25 Jun 2026: finance skills (DCF, closing the books, variance analysis), GA for M365 Copilot customers.
  - 29 Oct 2026: accounting capabilities for reconciliations, journal entries (accruals, reclasses, allocations, reversals, recurring), an opt-in audit trail of Copilot changes, and workbook history with selective undo. These are **Frontier (early access) only** and need a M365 Copilot licence. Depreciation is not mentioned.
  - Source: [DataStudios summary of Microsoft Copilot blog (secondary) (fetched)](https://www.datastudios.org/post/microsoft-copilot-for-finance-excel-cowork-accounting-capital-markets-plugins)
- Microsoft's **Financial Reconciliation agent** in Excel compares two datasets, suggests matching rules that the user accepts, regenerates or removes, and produces a report — [Microsoft Learn](https://learn.microsoft.com/en-us/copilot/finance/reconcile/reconcile-data)
- **Claude for Excel:** available to all Claude Pro subscribers since 24 Jan 2026 (after the Oct 2025 Max/Enterprise beta) — [The Decoder](https://the-decoder.com/anthropic-activates-claudes-excel-integration-for-all-pro-subscribers). GA reported on 7 May 2026 (secondary) — [Deckary](https://deckary.com/blog/claude-for-excel), [Vantaige](https://vantaige.io/blog/claude-microsoft-office-excel-word-outlook-setup-2026). Claude add-ins support Skills (11 Mar 2026) — [Claude release notes](https://support.claude.com/en/articles/12138966-release-notes)
- **Excel University's 2026 accountant guide** (28 Jul 2026) recommends Copilot in Excel, the Claude Excel add-in, Power Query AI, ChatGPT/Claude, Perplexity and GitHub Copilot. **It recommends no niche formula-generator SaaS.** It warns that Copilot "doesn't understand your chart of accounts", that AI formulas need review "as you would a junior staff member's file", and that "blind trust in AI-generated formulas... is a real risk" — [Excel University (fetched)](https://www.excel-university.com/best-ai-tools-for-accountants-in-excel-2026-guide/)
- An accountant-focused guide recommends Copilot for in-sheet work plus ChatGPT Plus for building and debugging formulas (single-blog opinion) — [LearnSignal](https://www.learnsignal.com/blog/best-excel-ai-tools-accountants-2026/)
- **Gemini in Sheets:** generates and inserts formulas and builds tables. It needs a qualifying Workspace or Google AI plan; free personal accounts generally lack the side panel — [Jotform guide (secondary)](https://www.jotform.com/ai/how-to-use-gemini-in-google-sheets/). Apr 2026: "build and edit complex spreadsheets with Gemini" — [Workspace Updates](https://workspaceupdates.googleblog.com/2026/04/build-and-edit-complex-spreadsheets-with-Gemini-in-Google-Sheets.html). Jun 2026: one-click formula-error troubleshooting (Business Standard/Plus, Enterprise, Google AI Pro/Ultra) — [Workspace Updates](https://workspaceupdates.googleblog.com/2026/06/troubleshoot-formula-errors-in-sheets.html)

### Inferences
- For bookkeepers on M365 (the large majority of active firms) or paid Workspace, a $9 standalone formula generator competes with tools they already pay for and that work *inside* the workbook with context. That is better than copy-pasting from a web app.
- Native tools still do not *test* formulas against edge cases or guarantee version compatibility. That is the only feature gap left (see 2B).

### Gaps
- Microsoft's 29 Oct 2026 Copilot blog post was not fetched directly. Frontier-only status comes from a secondary summary.
- No official confirmation of whether Copilot Chat "standard access" in Business Basic/Standard includes in-grid formula writing or only chat suggestions.

---

## 2B. Bookkeeper formula tool: existing formula generators and accountant-specific tools

### Takeaway
**Older-Excel compatibility is already a standard feature**: GPTExcel has a version selector for Excel 2010–365, Musely adjusts to the selected version, and AIExcel warns when a formula needs 365. **Accountant-specific AI formula tools with reconciliation, depreciation and payroll templates already exist** (ExcelCPA claims 2,000+ professionals; FixMyFormula). FormulaBot has pivoted to "Better Analyst" analytics at $20/mo, which supports the report's "bloat" claim. **No tool found runs generated formulas against edge-case test suites.** That is the one real gap.

### Cited Findings
- **FormulaBot is now Better Analyst** (formulabot.com redirects there). Free: 10 chat messages and 100 AI credits/mo. **Pro $20/mo** ($240/yr). Team $119/mo for 5 seats. Enterprise is custom. Positioned around dashboards, data sources, scheduled tasks and a Slack agent. No mention of formula validation or Excel-version selection — [Better Analyst pricing (fetched 2026-11-06)](https://betteranalyst.com/pricing)
- FormulaBot's price history: about $6.99/mo in an early review, versus a $18–20/mo Starter in 2026 reviews (secondary) — [Medium (older)](https://medium.com/@Jason_Feller/is-excel-formula-bot-better-than-chatgpt-407fbd984bf8), [ToolsForHumans](https://www.toolsforhumans.ai/ai-tools/excel-formula-bot)
- **GPTExcel:** users "set the version, from Excel 2010 to Excel 365" (365, 2021, 2019, 2016, 2013, 2010). It supports Google Sheets, LibreOffice and Airtable, and has Explain and Optimize modes. It does not validate formulas and tells users to check against their own data. Free: 4 runs per 12 hours — [GPTExcel formula generator (fetched)](https://gptexcel.uk/products/formula-generator)
- **Musely Excel Formula Bot** adjusts suggestions to the selected Excel version (vendor) — [Musely](https://musely.ai/tools/excel-formula-bot)
- **AIExcel** targets Excel 2016+ and flags when a formula needs M365/2021 functions (XLOOKUP, LET, dynamic arrays) (vendor) — [aiexcel.pro](https://aiexcel.pro/)
- Copilot itself reportedly sometimes uses XLOOKUP/FILTER/LET, which break in Excel 2019 and earlier (secondary listicle) — [BrightSEOTools](https://brightseotools.com/post/11-free-ai-excel-formula-generators)
- **ExcelCPA (excelcpatools.com)** is an "AI-powered Excel formula generator and VBA macro generator designed for accounting, audit, and finance professionals". It covers:
  - bank reconciliation and transaction matching
  - journal-entry/ledger validation formulas
  - audit sampling
  - tax provision
  - fixed-asset depreciation
  - payroll, reconciliation and depreciation templates

  It claims compatibility with M365, Excel 2021, 2019 and **2016**. It says it uses "secure local processing". It is labelled "Beta Access" with no public pricing. It claims "2,000+ Professionals" (**vendor-claimed**) and 90% time savings (vendor-claimed, unverified). It does not describe automated formula testing — [ExcelCPA (fetched)](https://www.excelcpatools.com/)
- **FixMyFormula:** an AI formula assistant plus month-end close and reconciliation formulas, P&L/budget templates and variance analysis for accountants. From a search snippet; the page fetch returned empty — [FixMyFormula](https://fixmyformula.com/excel-for-accountants/)
- **FormulasHQ:** 8 AI tools (formula generator, VBA/Apps Script, CSV Data Wizard). Claims "trusted by 99,000+ accountants, analysts, Salesforce admins..." (**vendor-claimed**) — [FormulasHQ](https://formulashq.com/)
- **Autosheet:** a free generator using gpt-4o-mini. Its FAQ says the formula "is not guaranteed to work" — [Autosheet](https://autosheet.com/tools/generate-excel-formulas)
- Other generators surfaced: excelform.xyz, excelformula.co, multiple.chat, Ajelix. A 2026 listicle "tested" 11 free generators (secondary) — [BrightSEOTools](https://brightseotools.com/post/11-free-ai-excel-formula-generators)
- **Willingness-to-pay signals:**
  - A G2 reviewer says FormulaBot's paid tool "can be replicated in Gemini, ChatGPT" — [G2 Excel Formula Bot reviews](https://www.g2.com/products/excel-formula-bot/reviews?qs=pros-and-cons)
  - A 2026 comparison lists ChatGPT as the most common alternative "because most people already have access" — [FindAnomaly (secondary)](https://www.findanomaly.ai/formula-bot-alternatives-2026)
- Free bookkeeping templates (bank reconciliation, ledgers, payroll timesheets) are plentiful from Vertex42, Beginner Bookkeeping and similar sources. Many results were low-quality aggregators and some were UK-centric — [Funding Circle guide](https://www.fundingcircle.com/us/resources/?p=8359), [Business Accounting Basics (UK)](https://www.businessaccountingbasics.co.uk/excel-bookkeeping-templates/)

### Inferences
- The report's three claimed gaps:
  - "FormulaBot emits 365-only functions": **already solved by competitors** (GPTExcel, Musely, AIExcel) and by adding "Excel 2016" to the prompt.
  - "Bloated into analytics": **true**, but that is FormulaBot leaving the category, not an open category. Better Analyst's pivot suggests standalone formula generation was not a durable business at $20/mo.
  - "Doesn't validate formulas": **true across the whole category, Copilot included.** Building a real validator (parse the formula, run it in a spreadsheet engine against generated edge cases such as blanks, text-in-number columns, negative values, period boundaries and leap years) is technically feasible. Marketing it as a "guarantee" to bookkeepers creates liability, and every accountant educator says to review AI output anyway.
- The bookkeeper template library is not unique: ExcelCPA, FixMyFormula and free templates cover reconciliation, depreciation and payroll.

### Gaps
- No pricing found for ExcelCPA or FixMyFormula. Their traction is unverified.
- No G2/Capterra review counts gathered for GPTExcel, Ajelix or ExcelCPA.
- No tool was found that markets "tested/validated formulas". Absence in search results is not proof that none exists.

---

## 2C. Bookkeeper formula tool: old-Excel population, demand and VERDICT

### Takeaway
There is **no US or accounting-specific data** on how many bookkeepers still use Excel 2016/2019. The only survey found is a German SMB panel, cited secondhand, showing Office 2016 on 34% of *on-premises* Office PCs in Sep 2026. Office 2016/2019 have been out of support since 14 Oct 2025, so the target segment is shrinking and has already chosen not to pay for subscriptions. **Verdict: gap PARTIALLY REAL, mostly FALSE (medium-high confidence).** Only the "tested formula" feature is unclaimed.

### Cited Findings
- Office 2016 and Office 2019 support ended 14 Oct 2025. The apps still run but carry security risk — [Microsoft Support](https://support.microsoft.com/en-us/office/system-requirements/end-of-support-for-office-2016-and-office-2019); [BleepingComputer](https://www.bleepingcomputer.com/news/microsoft/microsoft-office-2016-and-office-2019-reach-end-of-support-in-october/)
- An Intra2net survey of small German businesses *without* M365 found Office 2016 on 34% of on-prem Office PCs in Sep 2026 (still the most common version). Only 10% updated their on-prem suite in the prior 12 months. Zinstall also says no count of Office 2016/2019 users has been published since end of support (secondhand, non-US, non-accounting) — [Zinstall research](https://www.zinstall.com/research/microsoft-office-statistics)
- No Reddit threads from r/Bookkeeping, r/Accounting or r/excel surfaced in three differently phrased searches.

### Inferences
- **VERDICT: PARTIALLY REAL (narrow), confidence medium-high.**
  - Old-Excel compatibility: gap FALSE.
  - Bookkeeper templates: FALSE (ExcelCPA, FixMyFormula, free templates).
  - Native AI substitution: strong for M365/Workspace users.
  - Validation with edge-case tests: REAL as a missing feature, but demand and willingness to pay are unproven.
- The remaining sliver is a **"formula test harness / linter"** for accountants: paste or select a formula, auto-generate edge-case rows, show pass/fail and version-compatibility flags. It works best as an Excel add-in (AppSource) or a Copilot/Claude Skill, not as a standalone generator. Even then, Microsoft's Oct 2026 audit-trail and workbook-history features are moving toward the "trust" problem.
- At $9/$19, buyers would be the price-sensitive tail of solo bookkeepers on unsupported Excel versions. That is a poor ICP.

### Gaps
- No share-of-version data for US bookkeepers or accounting firms (CPA.com, Karbon or Intuit surveys not found).
- No direct willingness-to-pay data (surveys or conversion rates) for formula tools.

---

## 3A. Advisor LinkedIn tool: regulatory requirements (FINRA, SEC, mortgage, insurance) and whether a checklist suffices

### Takeaway
For **broker-dealer-affiliated reps**, a "FINRA-friendly checklist" is **not sufficient**:
- Static LinkedIn posts promoting the firm's business currently need **registered-principal approval before use**.
- The site itself must be principal-approved.
- Business communications must be **retained for at least 3 years**, which in practice means firm-approved, archive-integrated tools.

FINRA's Jul 2026 proposal (RN 26-14) would loosen pre-use approval to a risk-based model, but it is **not adopted**, and it explicitly keeps firms responsible for AI content, which must be "vetted, tested and monitored". RIAs face the SEC Marketing Rule and 5-year books-and-records retention. Mortgage LOs and insurance agents face employer or carrier pre-approval plus state rules (NMLS ID display, the NAIC UTPA/Model 570 framework).

### Cited Findings
- **FINRA current guidance:**
  - Static social content generally needs registered-principal approval before use, and some must be filed.
  - Interactive content can be supervised like correspondence.
  - A registered principal must approve any social site an associated person intends to use for business *before use*.
  - Business-related communications must be retained for at least 3 years.
  - Using personal sites for business can defeat recordkeeping.

  Source: [FINRA Social Media key topic (fetched 2026-11-06)](https://www.finra.org/rules-guidance/key-topics/social-media); [Regulatory Notice 11-39](https://www.finra.org/rules-guidance/notices/11-39)
- **RN 26-14 (published 9 Jul 2026; comments closed 11 Sep 2026):**
  - Would replace mandatory pre-use approval with written risk-based procedures deciding which retail communications need approval.
  - Would remove the static/interactive distinction.
  - Firms stay responsible whether a human or AI created a communication.
  - Generative AI tools may be part of supervision "provided they are vetted, tested and monitored".
  - Firms must keep evidence that supervisory procedures were carried out.
  - **Current rules remain in effect until adopted.** No adoption or effective date found as of 6 Nov 2026.

  Sources: [FINRA RN 26-14 (fetched)](https://www.finra.org/rules-guidance/notices/26-14); [Mintz analysis](https://www.mintz.com/insights-center/viewpoints/2401/2026-07-14-pivotal-moment-broker-dealer-communications-finra); [CCG comment letter](https://www.finra.org/sites/default/files/NoticeComment/CCG%20Comments%20-%20FINRA%20Notice%2026-14%20Comment%20Letter%20FINAL%20VERSION%20FOR%20SUBMISSION.pdf)
- FINRA guidance says AI-generated investor communications fall under the same rules as other communications — [InvestmentNews](https://www.investmentnews.com/regulation-and-legislation/finra-clarifies-guidelines-around-ai-chatbot-communications/253319). One vendor says FINRA has not mandated AI-disclosure labels as of 2026 (vendor, unverified) — [Defiance Analytics](https://www.defianceanalytics.com/blog/ai-content-creation-under-finra-compliance-rules)
- Advisors' business profiles, LinkedIn included, "need to be approved by your broker-dealer or another registered principal". A personal profile can become a business account depending on what is posted (vendor blog, FMG/Twenty Over Ten) — [Twenty Over Ten blog](https://blog.twentyoverten.com/social-media-compliance-for-financial-advisors/). Retail communications on LinkedIn need principal pre-approval (secondary) — [Wolf Financial](https://wolf.financial/blog/linkedin-advertising-compliance-broker-dealers-finra-2210)
- **SEC (RIAs):** social posts can be advertisements under Rule 206(4)-1. Testimonial analysis applies to social commentary. Advisers must keep social communications covered by Rule 204-2 (advice or advertisements), generally for 5 years with the first 2 easily accessible (law-firm commentary) — [Morgan Lewis on OCIE social media alert](https://morganlewis.com/pubs/2012/01/ocies-social-media-alert-proceed-with-caution-maintain-required-records-and-adopt-and-implement-robust-policies-and); [K&L Gates materials](https://files.klgates.com/files/upload/2016im_supplemental_materials_sessioniii1.pdf). The SEC's Apr 2024 risk alert flagged gaps in Marketing Rule policies, procedures and recordkeeping — [Stradley Ronon](https://www.stradley.com/insights/publications/2024/04/im-client-alert-april-23-2024)
- **Mortgage:** Reg Z's "advertisement" definition catches nearly any social post promoting mortgage credit. TILA, RESPA, UDAAP, ECOA, the Fair Housing Act and state laws apply — [PerformLine (vendor)](https://performline.com/blog-post/social-media-compliance-monitoring-loan-officers/); [Bankers Hub](https://www.bankershub.com/blogs/blog/social-media-marketing-reg-z-respa-udap-compliance). NMLS ID display is expected on mortgage-related social content, varies by state, and Virginia also requires the NMLS Consumer Access URL on the profile (vendor) — [ActiveComply SAFE Act guide](https://www.activecomply.com/compliance-resources/the-safe-act-101-a-guide-for-mortgage-advertising-marketing-compliance). LOs typically need marketing or compliance approval for accounts and posts (vendor) — [Strategic Compliance Partners (Mar 2026)](https://strategiccompliancepartners.com/2026/03/16/advertising-approvals-for-new-loan-officers-the-compliance-gap-most-brokers-miss/)
- **Insurance:** the NAIC Unfair Trade Practices Act has been adopted in about 45 states, and Model 570 covers life and annuity advertising. Regulators hold insurers responsible for agent advertising made on their behalf — [Saifr blog](https://saifr.ai/blog/general-compliance-requirements-for-insurance-advertising); [Stackmatix](https://stackmatix.com/blog/insurance-ad-compliance-state-regulations). Carrier guidelines require pre-approval and say not to post until approved — [Americo advertising guidelines](https://www.americo.com/Content/AdvertisingGuidelines.pdf); [National Life independent-agent guidelines](https://agentblog.nationallife.com/wp-content/uploads/2020/01/Independent-Agent-Advertising-Guidelines.pdf)

### Inferences
- A checklist tool **cannot** be the system of record for BD reps. Their firm's principal must approve the content and the firm must archive it, so reps can generally only post through firm-sanctioned tools. A self-serve $29 tool that publishes directly to LinkedIn would likely breach many BDs' written supervisory procedures. That rules out most BD-affiliated reps as self-serve buyers.
- The legally viable self-serve buyer is a **small SEC- or state-registered RIA** whose own CCO (often the founder) approves content, plus independent insurance agents and mortgage brokers posting non-product thought leadership. Even these need archiving.
- If RN 26-14 is adopted, it makes AI tools *more* acceptable for BDs ("vetted, tested, monitored"). That favours vendors who sell to firm compliance departments, not to individual reps.

### Gaps
- Did not fetch the SEC Marketing Rule text. The requirement for written policies and pre-use review of advertisements under 206(4)-7 and the Marketing Rule was not verified here.
- LinkedIn's compliance-archiving partner programme (Smarsh, Global Relay capture of LinkedIn) was not confirmed in this pass.
- No data on the BD-affiliated vs independent-RIA split of LinkedIn-active advisors.

---

## 3B. Advisor LinkedIn tool: existing compliance-aware content tools (pricing, traction, overlap)

### Takeaway
The space has **enterprise incumbents** (Hearsay, which claims 200k+ advisors and starts around $10k/yr; Smarsh; Broadridge; Saifr), **advisor marketing suites** (Snappy Kraken from $199/mo, FMG/Twenty Over Ten from about $99/mo), and **several ≤$59/mo AI tools for advisors** with approval workflows or FINRA pre-review: Apaya ($39–55/mo, 3-day trial), FINRAGuard AI ($50/mo solo, with archive), FinKode ($49/mo) and LinkedGrow ($59/mo). Mortgage and insurance have their own AI social tools (Lender Homepage, Lately, Agency Revolution). The report's "Kleo has no trial" gap is closed by generic LinkedIn writers such as Taplio and Supergrow, which offer 7-day trials.

### Cited Findings
**Enterprise / firm-sold**
- **Hearsay Systems:** claims to serve **200,000+ advisors** (vendor-claimed, about 2023), with clients including BlackRock, Schwab, Morgan Stanley and New York Life. It offers Content+ (compliant third-party content libraries), AI recommendations, and a **Jasper partnership** for AI-created content that fits firm compliance — [InvestmentNews](https://investmentnews.com/fintech/news/hearsay-uses-ai-to-recommend-content-advisors-can-post-on-social-media-236644). Starting price about **$10,000/yr**, no free trial (aggregator listing, secondary) — [Capterra](https://www.capterra.com/p/124035/Hearsay-Social/)
- **Saifr (Fidelity Labs, launched Jan 2022):** AI first-pass compliance review (SaifrReview, SaifrScan) against FINRA 2210, SEC 482 and the Marketing Rule. It serves BDs and RIAs and has expanded into life-insurance compliance. Pricing not public — [BusinessWire launch](https://www.businesswire.com/news/home/20220124005136/en/Fidelity-Investments%C2%AE-Launches-Innovative-New-Regulatory-Technology-RegTech-Business-to-Help-Financial-Institutions-Create-Compliant-Public-Communications); [Saifr for RIAs](https://saifr.ai/compliance-for-rias); [FinTech Global](https://fintech.global/insurtech100/saifr-expands-ai-suite-for-life-insurance-compliance/)
- **Broadridge** offers social media publishing for advisors (listing) — [The Wealth Mosaic](https://www.thewealthmosaic.com/vendors/broadridge-financial-solutions/social-media-publishing/)

**Advisor marketing suites**
- **Snappy Kraken:** Campaigns Foundations **$199/mo + $199 setup** (annual), Grow $299/mo + $499 setup, Freedom360 $899/mo. Includes "built-in compliance", profile and campaign review, and broker-dealer configuration in every tier. Social posting is limited to blog posts (Grow website tier) — [Snappy Kraken pricing (fetched 2026-11-06)](https://snappykraken.com/pricing). A 20% LPL discount is reported (secondary) — [Adapter](https://adapter.to/blog/snappy-kraken-review)
- **FMG Suite** (acquired Twenty Over Ten in Dec 2020): entry about $99/mo + $199 setup, managed about $895/mo (**competitor-sourced, biased**) — [Asset Engine comparison](https://getassetengine.com/compare/fmg-suite-vs-snappy-kraken/); [CB Insights](https://www.cbinsights.com/compare/leadcenterai-vs-site-twenty-ten)
- SageContent tiers from $250/mo; WealthReach Attract from $500/mo (secondary listicle by SageContent) — [SageContent blog](https://sagecontent.ai/blog/best-ai-marketing-tools-financial-advisors)

**≤$59/mo AI tools overlapping the proposed product**
- **Apaya:** "AI Social Media Manager for Financial Advisors". The search title says $39/mo; the page says self-serve "starts at $55/month billed annually". **3-day free trial.** Per-campaign review-or-auto-publish approval workflow. Targets RIAs, independent and fee-only advisors. No archiving or disclosure features mentioned; LinkedIn listed as an integration. Customer claim "35% more inbound consultation requests" has no sample size (vendor-claimed) — [Apaya advisors page (fetched)](https://apaya.com/solutions/professional-services/financial-advisors)
- **FINRAGuard AI:** AI pre-review scoring against FINRA 2210 and SEC rules, risky-language highlighting, compliant rewrites, disclaimer suggestions (Team+), a **content archive with 3-year audit retrieval**, LinkedIn/X/email review. **Solo $50/mo ($594/yr)**, Team $150/mo, Firm $350/mo. The checkout shows conflicting prices ($99/$299/$699). No customers named, no trial, crypto checkout (NOWPayments). Legitimacy unverified — [FINRAGuard AI (fetched)](https://my-finraguardai.pages.dev/)
- **FinKode:** Starter **$49/mo** (20 pieces), $99, $199. Covers SEC Marketing Rule and FINRA 2210 for blog, social and email (search snippet; unverified) — [FinKode](https://finkode.io/)
- **LinkedGrow:** financial-services LinkedIn content page, Pro **$59/mo** (generic tool with an industry landing page) — [LinkedGrow financial services](https://linkedgrow.ai/industries/financial-services)

**Kleo and generic LinkedIn writers (the clone source)**
- **Kleo:** $99/mo (about $948–999/yr), **no free trial**, 30-day money-back guarantee (sources differ on whether that is annual-only). Its Chrome extension was taken down after a LinkedIn cease-and-desist; sources disagree on whether that was early 2025 or early 2026. Reportedly about 70,000 users lost access, and Kleo relaunched as a web app. All of this is from competitor blogs (secondary, biased) — [Scripe](https://scripe.io/blog/kleo-alternatives), [AuthoredUp](https://authoredup.com/blog/kleo-review), [Ligo Social](https://ligosocial.com/kleo-alternative), [ContentIn (25 Aug 2026)](https://contentin.io/blog/kleo-alternatives/)
- Alternatives with trials: Taplio (7-day trial, $39–49 entry), LinkedGrow (7-day trial), Supergrow and Postiv (7-day trials), Reepl (free plan) (secondary) — [LinkedGrow Kleo comparison](https://linkedgrow.ai/compare/kleo-alternative)

**Mortgage and insurance**
- **Lender Homepage:** an AI content engine writing mortgage-specific posts for LOs, with review before one-click publishing (pricing not public) — [Lender Homepage](https://www.lenderhomepage.com/products/social-media)
- **Lately:** compliance-reviewed social for financial services. AmeriFirst (250 licensed LOs) is a case study (vendor) — [Lately case study](https://lately.ai/customer-stories/amerifirst-compliant-social-media-program)
- **ActiveComply / PerformLine:** monitor LO social posts for compliance (vendors) — [ActiveComply](https://www.activecomply.com/compliance-resources/the-safe-act-101-a-guide-for-mortgage-advertising-marketing-compliance), [PerformLine](https://performline.com/blog-post/social-media-compliance-monitoring-loan-officers/)
- **Agency Revolution:** an AI social media app for insurance agents and carriers. **Sendible:** an insurance AI assistant with approval workflows. **Agent Marketing Lab:** AI posts for agents (pricing not public) — [Agency Revolution](https://agencyrevolution.com/insurance-marketing-tools/social-media/), [Sendible](https://www.sendible.com/resources/insurance-social-media-ai-assistant)

### Inferences
- "No compliance workflow at $29–59" is **false**. Apaya, FINRAGuard and FinKode sit at $39–59 with approval and pre-review. Their traction is unverified and probably small.
- "Kleo has no trial" is true but irrelevant, because many generic writers offer trials.
- What incumbents do well: enterprise vendors (Hearsay, Smarsh, Saifr) own BD distribution through home-office contracts, approved-content libraries and archiving. Advisor suites (Snappy Kraken, FMG) bundle compliance review with BD configuration. A solo-rep tool cannot get onto BD approved-vendor lists without a firm-level sale.
- Gap that looks real: **voice-learning, hook-driven personal LinkedIn writing** (Kleo-style) built into the compliance workflow of a small RIA. Most advisor tools are content libraries or campaign automation, not personal-voice writers. Apaya and FinKode are the closest; their depth on voice learning is unknown.

### Gaps
- No G2/Capterra review counts or funding data for Apaya, FinKode or FINRAGuard. FINRAGuard looks like an early-stage or possibly low-legitimacy operation.
- Twenty Over Ten / FMG and Lumio, Levitate, AdvisorStream and Vestorly were not checked individually in this pass (search on Twenty Over Ten's "Lead Pilot" returned nothing usable).
- Smarsh and Global Relay pricing and their LinkedIn capture not checked.

---

## 3C. Advisor LinkedIn tool: LinkedIn platform terms and VERDICT

### Takeaway
Posting to a member's own profile through LinkedIn's official API (`w_member_social`) is available. Third-party guides say it is self-serve via "Share on LinkedIn"; Microsoft's docs list it under the Community Management API. LinkedIn is hostile to browser extensions that overlay or scrape its UI (the Kleo takedown, extension scanning), so API-only posting is the right architecture. **Verdict: gap PARTIALLY REAL, narrow (medium confidence).** It is FALSE for BD-affiliated reps, crowded for independent RIAs at ≤$59, and closed by employer or carrier approval systems for LOs and agents.

### Cited Findings
- `w_member_social` lets an app "post, comment and like posts on behalf of an authenticated member" — [Microsoft Learn: Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/posts-api). Community Management API catalogue — [LinkedIn Developer](https://developer.linkedin.com/product-catalog/marketing/community-management-api). Third-party 2026 guides say "Share on LinkedIn" grants `w_member_social` for personal-profile posting without review, with about 150 calls per member per day. Reading back one's own posts (`r_member_social`) is closed (secondary, conflicting with the official framing) — [Blotato](https://www.blotato.com/blog/linkedin-posting-api)
- LinkedIn's help centre reportedly classes extensions that automate activity as prohibited software. An Apr 2026 report says LinkedIn scans for about 6,000+ Chrome extensions via a hidden script — [The Next Web (5 Apr 2026)](https://thenextweb.com/news/linkedin-browsergate-extension-scanning-privacy-fingerprint)
- Kleo's extension was removed after a LinkedIn cease-and-desist citing scraping and UI overlays (secondary, dates conflict) — [Ligo Social](https://ligosocial.com/kleo-alternative); [AuthoredUp](https://authoredup.com/blog/kleo-review)

### Inferences
- **VERDICT: PARTIALLY REAL. Confidence: medium.**
  - **BD-affiliated reps:** FALSE. A checklist cannot replace principal pre-approval and archiving, and firms mandate approved tools (Hearsay, Smarsh-captured channels).
  - **Small RIAs / IARs not tied to a BD:** PARTIALLY REAL but crowded (Apaya, FinKode, FINRAGuard, LinkedGrow at $39–59). The defensible angle is *Kleo-grade personal-voice writing plus a CCO approval queue plus export or integration to an archive* (Smarsh, Global Relay or similar), not a checklist.
  - **Mortgage brokers:** mostly closed by employer approval and monitoring vendors (ActiveComply, PerformLine) and LO-specific AI tools (Lender Homepage, Lately). The NMLS-ID auto-insertion and state-rule sliver is small.
  - **Insurance agents:** carrier pre-approval is the bottleneck, and carriers are liable. A self-serve tool cannot pre-clear carrier approval, so the sliver is generic thought-leadership posts that do not name carriers or products.
- What would make it viable: selling to the **firm** (CCO/compliance) rather than the rep. If RN 26-14 is adopted, it may open a "vetted, tested, monitored" AI-content lane for BDs, but that favours enterprise vendors.
- Proposed $29 solo pricing is under the crowd's $39–59 band. Adding archiving to reach compliance adequacy raises costs.

### Gaps
- Did not confirm LinkedIn's current official approval requirements for `w_member_social` from the developer portal.
- No r/CFP, r/FinancialPlanning or r/LoanOfficers threads retrieved, so it is unknown what practitioners currently recommend or complain about.
- Did not determine what share of US advisors are BD-affiliated vs independent RIA-only (the key sizing number for the viable sliver).
