# Viral / Trend Intelligence Tools for Short-Form Video, and the "Intelligence + Remix/Create" Intersection

Research date: 2026-11-06. All vendor pricing pages fetched on that date unless marked otherwise. Provenance tags used throughout:
- **[vendor]**: claim on the vendor's own site or blog.
- **[vendor-metrics]**: specific numbers the vendor itself published.
- **[founder]**: founder-reported, e.g. Indie Hackers.
- **[3P-directory]**: aggregator or directory listing.
- **[competitor]**: published by a rival product, so likely biased.
- **[store]**: Chrome Web Store or app store listing.
- **[press]**: trade press.
- **[obs]**: something I saw myself during this session (for example a vendor's MCP tool manifest) that I could not confirm on a public page.

---

## Q1. Who already productises "find what's going viral in my niche, then make my version of it"? How well, at what price, with what traction? (Per-product evidence file)

### Takeaway
The loop is already productised at three levels:
1. **Video-level outlier detection plus AI scripts/hooks.** This is crowded. Sandcastles, Virlo, 1of10, OutlierKit, vidIQ, Viewstats and Mysocial all do it at $15–$499/mo.
2. **Viral library plus one-click remix into finished faceless video plus autopost.** This already exists. Revid.ai does it at $39–$199/mo, with 14k+ creators claimed. vidIQ is converging on the same loop.
3. **Trend-effect or format templates plus AI generation.** Higgsfield Viral Presets, ClipTrend, Zawa Video Remix, TikTok Symphony and Instagram Edits all do this, and the last two are free and platform-native.

Nobody I found combines **live, data-derived format-level intelligence** (clusters of videos sharing a reproducible structure, with lifecycle and saturation signals) with generation. The closest attempts each cover only part of it:
- Format Finder has a static library of 65+ curated formats.
- Virlo clusters by topic and narrative, not by format.
- ClipTrend covers AI-effects templates only, and its traction is low.

### Cited Findings

#### A. Short-form-first outlier/intelligence tools (TikTok / Reels / Shorts)

**Sandcastles (sandcastles.ai)**
- **Detects:** "top 1% outliers in every niche" from a database of "millions of validated outliers." It also analyses "hooks, storytelling, formats and styles" — [Sandcastles home](https://sandcastles.ai/)
- **Platforms:** Instagram, TikTok and YouTube Shorts (Reels is not named as such) — [Sandcastles home](https://sandcastles.ai/)
- **Data sourcing:** Not disclosed. The site says "Millions of videos analyzed daily." Users can optionally connect accounts, and verified channels refresh every 1–12h depending on plan — [Sandcastles home](https://sandcastles.ai/)
- **Creation:** Script writer using "proven storytelling frameworks," hook templates, transcript download and project collections. The intro mentions "remix" but the page does not detail it. MCP connector on all plans, API on Titan — [Sandcastles home](https://sandcastles.ai/)
- **No video creation:** Per a competitor, it has no video editor or generation and "No curated format library," so users infer patterns from top videos — [Format Finder vs Sandcastles, competitor, checked 2026-09-07](https://formatfinder.onepeakcreative.com/resources/compare/format-finder-vs-sandcastles-ai)
- **Pricing [vendor, 2026-11-06]:**
  - Pro: $49/mo, or $39/mo billed yearly. 100 credits, 3 workspaces, 150 competitors per workspace.
  - Visionary: $99/$79. 250 credits.
  - Titan: $499/$399. 1,500 credits, API, 20 workspaces, agency guest access.
  - Unused credits expire monthly.
  - Source: [Sandcastles home](https://sandcastles.ai/). The /pricing URL returned 404. Another directory lists $39/mo or $33/mo annual, which conflicts and may be stale — [3P-directory via search](https://thegtmdirectory.com/tools/sandcastles)
- **Traction [vendor]:** "Trusted by 100k+ users," "4.92 / 5 Rating" — [Sandcastles home](https://sandcastles.ai/). I found no founder, revenue or funding data.
- **Complaints:** No Trustpilot or Reddit complaint corpus found. The only cancellation and refund info came from a low-reliability third party (chargeback service with template copy) — [joinchargeback](https://www.joinchargeback.com/cancels/how-to-cancel-sandcastles)

**Virlo (virlo.ai)**
- **Detects:** "viral short-form content, outliers, and emerging creators." Its year-in-review lists topic-level clustering, Custom Niches and "Orbit" narrative-level social listening that measures acceleration within topics — [Virlo home](https://virlo.ai/); [Virlo year in review, 2026-01-03](https://virlo.ai/blog/virlo-year-in-review)
- **Platforms:** TikTok, YouTube Shorts and Instagram Reels, plus Meta Ads Intelligence on Pro — [Virlo home](https://virlo.ai/). The Jan 2026 year-in-review lists only TikTok and YouTube Shorts as data sources, and its connected accounts were 5,994 YouTube and 3,107 TikTok, with Instagram not listed — [Virlo year in review](https://virlo.ai/blog/virlo-year-in-review)
- **Data sourcing:** "Built its own collection infrastructure instead of relying on third-party data providers," for "tighter control over data quality, costs, and the API" — [Indie Hackers newsletter copy, founder](https://www.sequenzy.com/api/email-examples/ulhbd2932zyfpqf3xtceq8ly/html)
- **Creation:** "Content Studio — AI-powered content creation tools built on trending data." No video generation is stated — [Virlo home](https://virlo.ai/)
- **Pricing [vendor, 2026-11-06]:**
  - Starter: $49/mo, 2,000 credits, daily data refresh.
  - Pro: $199/mo, 12,000 credits, Meta Ads Intelligence, 3 seats, Slack/Discord/webhook alerts, Zapier/n8n.
  - Enterprise: custom, includes API.
  - Source: [Virlo pricing](https://virlo.ai/pricing). A competitor says Enterprise starts at $499 with 30% off yearly — [Shortimize vs Virlo, competitor](https://www.shortimize.com/vs/virlo)
- **Traction [vendor-metrics, as of 2026-01-02, cumulative since launch on 2025-03-01]:** 62,115 registered users; 3,261 paid subscribers (5.25% conversion); 1,431,121 videos indexed; 9,101 connected creator accounts. It launched with a three-person team — [Virlo year in review](https://virlo.ai/blog/virlo-year-in-review)
- **Traction [founder]:** About $1k MRR in March 2025, rising to "$31k MRR" (exact month not given), with a goal of $300k MRR — [Indie Hackers post title/summary](https://www.indiehackers.com/post/KgfHz813vyyWeszqJMIi); [IH newsletter copy](https://www.sequenzy.com/api/email-examples/ulhbd2932zyfpqf3xtceq8ly/html)
- **Segment pivot:** "Agencies seemed to like the early product most." Founder Nic Mauro rebuilt the offer around agency research workflows. The year-in-review says moving away from the "general creator" hurt short-term growth but produced stickier users — [IH newsletter](https://www.sequenzy.com/api/email-examples/ulhbd2932zyfpqf3xtceq8ly/html); [year in review](https://virlo.ai/blog/virlo-year-in-review)
- **Complaints:** Trustpilot reviews are mixed. One 1-star review complained about outlier and niche-update problems and asked to cancel, while several 5-star reviews exist — [Trustpilot ES via search](https://es.trustpilot.com/review/virlo.ai). A SourceForge user said it "needs more data" — [SourceForge](https://sourceforge.net/software/product/Virlo/)

**Mysocial Outliers (mysocial.io/outliers)**
- **Detects:** Outliers as a multiple of a creator's median views over their ~25 most recent posts (example: "175×"), plus a second score against same-topic posts on the same platform — [Mysocial Outliers](https://mysocial.io/outliers/)
- **Platforms:** Topic search on TikTok, Instagram, YouTube, X and Threads. LinkedIn only via tracked creators — [Mysocial Outliers](https://mysocial.io/outliers/)
- **Data sourcing:** Providers are not named — [Mysocial Outliers](https://mysocial.io/outliers/)
- **Creation:** "Save to Ideas" transcribes the video and pulls top comments. MCP for Claude and ChatGPT — [Mysocial Outliers](https://mysocial.io/outliers/)
- **Pricing [vendor]:** $49 / $149 / $349 per month. Outliers is not included on the free plan — [Mysocial Outliers](https://mysocial.io/outliers/)
- **Traction:** No customer counts. The examples come from the founder's own research — [Mysocial Outliers](https://mysocial.io/outliers/)

**Format Finder (OnePeak Creative)**
- **Detects:** It detects nothing live. It is "Not a channel-tracking tool," and works from a curated library of **65+ named viral formats**, each with hook patterns, script beats and shot structures — [Format Finder vs Sandcastles (own site)](https://formatfinder.onepeakcreative.com/resources/compare/format-finder-vs-sandcastles-ai)
- **Platforms:** TikTok, Reels, Shorts and Facebook — [same](https://formatfinder.onepeakcreative.com/resources/compare/format-finder-vs-sandcastles-ai)
- **Creation:** Niche-specific hooks, scripts and shot plans. A "One Click Editor" trims and captions raw footage. Uploaded videos get a craft review, plus retention drop-off analysis if you supply an analytics screenshot — [same](https://formatfinder.onepeakcreative.com/resources/compare/format-finder-vs-sandcastles-ai)
- **Pricing [vendor]:**
  - Starter: $29/mo or $180/yr, 200 credits.
  - Pro: $59/mo or $360/yr.
  - Peak: $97/mo or $588/yr, with courses.
  - Source: [same](https://formatfinder.onepeakcreative.com/resources/compare/format-finder-vs-sandcastles-ai)
- **Traction:** None found.

**Shortimize**
- **What it does:** Tracking and payments for creator and clipping programs, not outlier discovery. Covers 6 platforms (TikTok, IG, YT, FB, Snapchat, X).
- **Pricing [vendor]:** Launch $99/mo, Scale $249/mo — [Shortimize vs Virlo](https://www.shortimize.com/vs/virlo)
- Relevant as proof that brands and apps pay for short-form performance tracking.

**Smaller and long-tail outlier finders**
- Viral Outliers (MCP server; TikTok, IG, YT); Apify "TikTok Outlier Finder," which scores other scrapers' rows; and Chrome extensions "Viral Finder" (YT + TikTok) and "Outviral" (IG/TikTok) — [search results summary](https://apify.com/nerolabs/viral-outlier-finder); [chromeboard Outviral](https://chromeboard.com/extension/outviral-—-ig-tiktok-outl-jfmljlidboiojmadcapooddeenghehln)
- These are a commoditisation signal: an outlier score is an easy feature to copy.

#### B. YouTube-first outlier tools (most of the "outlier" category)

**vidIQ**
- **Detects:** The Outliers feature covers **YouTube long-form and Shorts**. The score uses views, velocity and engagement against the channel baseline. Filters include Outlier Score, VPH, subscriber count, date, length and a Video/Shorts toggle, plus visual search. Free plan returns 6 videos per search — [vidIQ Outliers](https://vidiq.com/features/outliers/)
- **Other platforms:** "vidIQ for Instagram" launched on **2026-05-05**, covering Reels analysis, trend-based ideas and AI covers — [vidIQ product updates](https://vidiq.com/blog/category/product-updates/). A TikTok trending-sounds app ("vidIQ Viral") launched in June 2022, and a free Trending TikTok Sounds tool remains in the site navigation — [vidIQ blog](https://vidiq.com/blog/post/vidiq-for-tiktok-trending-sounds-music/); [vidIQ pricing nav](https://vidiq.com/pricing/)
- **Creation:** MAX includes "Up to 11 hours of short clipping and generations." The navigation lists an AI Video Generator and Clipping — [vidIQ pricing](https://vidiq.com/pricing/)
- **Pricing [vendor, 2026-11-06]:**
  - Free: $0, 150 AI credits.
  - Boost: $16.58/mo, billed $199/yr.
  - MAX: $39/mo, billed $468/yr. The page intro says $49/mo, which conflicts.
  - Enterprise: custom.
  - Source: [vidIQ pricing](https://vidiq.com/pricing/)
- **Traction [vendor]:** "20k+ 5 Star Reviews" — [vidIQ Outliers](https://vidiq.com/features/outliers/)

**1of10**
- **Detects:** Outlier search, thumbnail search, "trending formats" (top 3 on the free plan) and competitor tracking. The pricing page mentions only YouTube — [1of10 pricing](https://1of10.com/pricing)
- **Creation:** AI Thumbnail Generator, AI Video Editor (50 credits per edited video up to 30 min) and an AI Title/Idea generator. Research tools never use credits. MCP/API on Pro and up — [1of10 pricing](https://1of10.com/pricing)
- **Pricing [vendor, 2026-11-06]:**
  - Free: 60 credits.
  - Basic: $15/mo ($180/yr), 150 credits.
  - Pro: $69/mo ($828/yr), 1,000 credits.
  - Ultra: about $417/mo ($4,999/yr) with coaching.
  - Source: [1of10 pricing](https://1of10.com/pricing)
- **Traction:**
  - [vendor] "Trusted by 100,000+ creators" — [1of10 pricing](https://1of10.com/pricing)
  - [store] Chrome extension has about 30,000 users and a 4.0 rating from 32 ratings — [Chrome Web Store via search](https://chromewebstore.google.com/detail/gkfdnmclhbgbidnpmimfdobgjpeblckn)
  - [vendor] Models "trained on 62B views" — [1of10 about via search](https://1of10.com/about)
  - Co-founded in 2023 by Richard Do, with Riad Etmimou as technical co-founder — [1of10 about via search](https://1of10.com/about)
  - No revenue or funding found.

**OutlierKit**
- **Platforms:** YouTube only. Its FAQ confirms it pulls no TikTok or Instagram data — [creatoreconomytools via search](https://creatoreconomytools.com/tool/outlierkit)
- **Pricing [vendor]:**
  - Hobby: $24.92/mo ($299/yr), 100 credits.
  - Pro: $49.92/mo ($599/yr), 500 credits, "AI script & hook analysis."
  - Max: $166.58/mo ($1,999/yr), 50+ channels, aimed at agencies.
  - Lifetime deals are offered. Top-ups cost $19 per 100 credits. MCP/API on all tiers.
  - Source: [OutlierKit pricing](https://outlierkit.com/pricing)
- **Traction:** None stated.
- **Note:** OutlierKit publishes most of the "vs" and pricing content about competitors, so treat its competitor figures as [competitor].

**Viewstats (MrBeast / Jon Youshaei)**
- **Detects:** Outliers, thumbnail search by URL or image, alerts, A/B data. YouTube only — [OutlierKit review, competitor](https://outlierkit.com/blog/viewstats-review-features-alternatives)
- **Pricing:**
  - Pro: $49.99/mo or $479.88/yr per multiple third parties — [search summary](https://outlierkit.com/blog/best-youtube-outlier-finder-tools). The official page showed a "$--.--" placeholder for Pro on 2026-11-06.
  - Business: "Starting at $249/mo" — [Viewstats pricing](https://www.viewstats.com/pricing)
- **History:** Pro launched in May 2024 — [Tubefilter, press](https://www.tubefilter.com/2024/05/29/mrbeast-launches-viewstats-pro-premium-analytics-platform-jimmy-donaldson-jon-youshaei/)
- **Complaints:** "frequent crashes and slow performance" — [creatoreconomytools](https://creatoreconomytools.com/tool/viewstats)

**Spotter Studio**
- **Pricing [competitor, June 2026]:** $49/mo, or $299/yr, with a 60-day trial — [OutlierKit](https://outlierkit.com/resources/spotter-studio-pricing/). Other OutlierKit pages say pricing is not public.
- **Status flag:** On 2026-11-06, spotterstudio.com/pricing returned a 301 redirect to spotter.com/pricing, which returned **404**. The standalone product's current status is unverified and may have been folded into the parent company.

**TubeBuddy**
- **Pricing [competitor, July 2026]:** Pro about $43.20/yr and Legend about $278.28/yr, with 50% off for channels under 1k subscribers — [1of10 blog](https://1of10.com/blog/tubebuddy-pricing-review/)
- YouTube only. No outlier database. Per a competitor it shows only "Content Standouts" — [TubeLab](https://tubelab.net/blog/i-tested-7-youtube-tool-alternatives-to-tubebuddy)

#### C. TikTok analytics and listening (brand/B2B side)

**Exolyt**
- **Platforms:** TikTok only.
- **Tracks:** Accounts, hashtags and sounds (1 / 50 / 300 of each by tier), influencer campaigns and social-listening projects. Refreshes 1×, 2× or 6× per day.
- **Pricing [vendor]:**
  - Basic: $0.
  - Essentials: $400/mo ($330 annual).
  - Advanced: $950/mo ($790 annual).
  - Enterprise: custom.
- **Traction [vendor]:** "#1 TikTok Analytics & Social Intelligence Tool"
- **Creation:** None.
- Source: [Exolyt pricing](https://exolyt.com/pricing)

**Pentos**
- Tracks TikTok songs, topics and trends, with daily snapshots.
- Pricing conflicts: $99/mo starting versus a $999/mo top tier — [Pentos via search; tlinky/quorage](https://www.capterra.com/p/10007697/Pentos/)
- Not verified live.

**Trendpop**
- History: YC company founded in 2020, acquired by Collab in February 2022 with undisclosed terms — [Tubefilter](https://www.tubefilter.com/2022/02/15/collab-acquires-trendpop-viral-tiktok-ads/)
- Launched self-serve for individual creators in October 2022 — [Tubefilter](https://www.tubefilter.com/2022/10/20/trendpop-analytics-platform-all-users-now-available-collab/amp/)
- Used by music marketing and A&R teams — [search summary](https://www.getapp.com/marketing-software/a/trendpop/)
- **Status flag:** A GetApp listing updated in June 2026 still shows it as active, but I found no 2026 product news. It is possibly dormant or absorbed into Collab, and I did not verify live.

**TrendTok:** An AI app that suggests niche-tailored trends and flags rising versus declining trends — [Cyberclick](https://www.cyberclick.es/numerical-blog/tiktok-analytics-que-es-y-como-interpretar-los-informes-de-tiktok?hs_amp=true). Pricing and status not verified.

**Tokchart:** No search results. It is likely defunct or renamed, and I could not verify it.

**Dash Social (formerly Dash Hudson)**
- A "Trending Sounds" feature surfaces current TikTok audio with usage stats and embedded example videos. The team "curates the hottest sounds weekly."
- Plans "starting at $999/month" on dashsocial.com, versus $499/mo on the older dashhudson.com page, which conflicts — [Dash Social Trending Sounds](https://www.dashsocial.com/features/tiktok-trending-sounds); [Dash Hudson page](https://www.dashhudson.com/features/tiktok-trending-sounds)
- Also published a 2026 Social Media Trends Report in February 2026 — [Medianet](https://newshub.medianet.com.au/2026/02/dash-socials-2026-social-media-trends-report-reveals-creative-excellence-now-drives-social-discovery/138244/)

**Sprout / Hootsuite / Later / Metricool**
- Sprout's own guide says it has no specific "trending sounds" discovery feature. Sprout costs about $249/mo per seat.
- A third party claims Metricool tracks hashtag and sound performance.
- Later offers trend-aware hashtag suggestions.
- Hootsuite offers broad social listening.
- None of the four is a format-intelligence product — [search summary incl. Sprout guide](https://sproutsocial.com/insights/tiktok-sounds/); [syncly](https://syncly.app/blog/sprout-social-vs-hootsuite)

**Kalodata (TikTok Shop)**
- Tracks product sales, trending videos and creators, from about $45.90/mo [3P]. A competitor says it has "No organic content or trend analytics."
- FastMoss starts at $39/mo [3P] — [Creatify Kalodata pricing](https://creatify.ai/blog/kalodata-pricing-plans-and-what-you-ll-actually-pay-in-2026); [Virlo compare, competitor](https://virlo.ai/compare/kalodata-vs-fastmoss)

#### D. Platform-native (free) intelligence and creation — the biggest structural threat

**TikTok Creative Center**
- Free trends for hashtags (now browsed by industry, login expected), songs, creators and videos, plus Top Ads and Top Products.
- Its old Video Generator has been removed, and some tools moved to TikTok One — [Creatify guide 2026](https://creatify.ai/blog/tiktok-creative-center); [TikTok help](https://ads.tiktok.com/resources/help/article/creative-center)
- TikTok's US joint venture completed on 2026-01-22 [3P blog] — [search summary](https://creatify.ai/blog/tiktok-creative-center)

**TikTok Symphony Creative Studio and TikTok One**
- Generally available to logged-in TikTok for Business users, running on Seedance 2.0. Outputs are auto-labelled AI-generated.
- Generates "fresh, auto-generated video options daily."
- "Symphony Agent" (Cannes Lions 2026) combines advertiser goals with "insights from top-performing content and emerging trends."
- TikTok One turns campaign goals into creator briefs.
- Sources: [TikTok Symphony blog](https://ads.tiktok.com/business/es/blog/tiktok-symphony-ai-creative-suite); [Vidjet July 2026 update](https://www.vidjet.com/blog/latest-features-on-tiktok-symphony-studio-july-2026-update). The Agent details are partly third-party.

**Instagram Edits**
- Inspiration tab of Reels using trending audio, a "Use audio" button that jumps straight into the editor, and an Insights tab.
- A June 2026 update added an AI assistant, beat markers, and "save formats for future projects" — [Planoly](https://planoly.com/blog/instagrams-edits-app-review); [Hypebeast 2026-06](https://hypebeast.com/2026/6/instagram-edits-app-adds-beat-markers-and-ai-tools)

**Insider channel:** TikTok has sent select publishers a weekly newsletter previewing hashtags it plans to promote. This is not a public product — [Digiday](https://digiday.com/media/tiktok-courts-publishers-weekly-newsletter-previewing-trending-hashtags/)

#### E. "Remix / recreate viral format" creation tools (intelligence + generation intersection)

**Revid.ai** (the closest existing match to the founder's idea)
- **Library:** "3M+ viral videos to remix."
- **Remix and monitoring:** "one-click remix" and "viral watching" of channels (5 channels on Growth, 50 on Ultra).
- **Publishing:** Direct publishing to TikTok, IG, YT and X, with Auto-Mode autopost workers (3 on Growth, 10 on Ultra).
- **Pricing [vendor, 2026-11-06]:**
  - Hobby: $39.
  - Growth: $39 (shown discounted from $99).
  - Elite: $89.
  - Ultra: $199.
  - Higher credit tiers run to $2,799/mo.
- **Traction [vendor]:** "Loved by 14,258+ creators," "Creators publish 30,000+ videos a month."
- Source: [Revid pricing](https://www.revid.ai/pricing)
- **Repurpose feature:** The "Repurpose viral videos" feature watches what is going viral in your niche across TikTok/YT/IG. Its "Repurpose"/"Part 2" modes generate new scripts and visuals, and "Restyle" is limited to footage you have rights to — [Revid repurpose page (PL)](https://www.revid.ai/pl/features/repurpose-viral-videos)

**StoryShort**
- Faceless templates (Reddit story, brainrot, POV, anime, UGC) with autoposting. I found no trend detection.
- Pricing from third parties conflicts: about $19 to $39/mo entry — [Stork](https://www.stork.ai/en/storyshort); [DigitalAgencyNetwork](https://digitalagencynetwork.com/tool/storyshort/)
- Critique: cost per video becomes "uncompetitive" above 10–15 videos/mo — [FluxNote](https://fluxnote.io/guides/storyshort-review-honest-2026)

**Higgsfield Viral Presets**
- 60+ one-tap effect templates (photo in, trend-style clip out), "with new presets added regularly to match current trends" [vendor] — [Higgsfield blog](https://higgsfield.ai/blog/how-to-make-viral-videos-viral-presets)
- 13 new presets added at once [3P] — [Miracamp](https://www.miracamp.com/learn/video-editing/new-higgsfield-viral-presets)

**ClipTrend.ai**
- "Watches what is going viral and turns each repeatable effect into a one-click AI video template." 40–50+ templates, updated weekly.
- Each card shows 3–5 real viral videos with live view counts. It aggregates Seedance 2, Kling 3.0, Veo 3.1 and others.
- Credit packs from $11.99, or a subscription from $14.99 (sources conflict).
- Launched on Product Hunt on 2026-05-09 with weak traction: 0 upvotes, ranked #152 — [Product Hunt / search summary](https://www.producthunt.com/products/cliptrend-ai); [PeerPush](https://peerpush.com/p/cliptrend)

**Zawa Video Remix / "viral video clone"**
- You paste a TikTok/Reels/Shorts link or upload a file. It extracts "hook timing, cut pacing, text overlay placement, product reveal sequence" and regenerates the video around your product.
- A "Trending Now" list of format categories exists, but no sourced feed.
- Free plan available. Paid prices not listed.
- Claims the output is "original content, not a replication" [vendor] — [Zawa](https://zawa.ai/viral-video-clone)

**Other link-to-clone tools:** UGCCopilot, Quinn Clone, the CloneUP iOS app, and an n8n template (Apify + Gemini that clones a viral TikTok and autoposts to 9 platforms via Blotato) — [search summary](https://ugccopilot.ai/use-case/clone-viral-videos/); [n8n workflow 4110](https://n8n.io/workflows/4110); [CloneUP App Store](https://apps.apple.com/us/app/id6769665692). Cloning a user-supplied link is now a commodity.

**Opus Clip / Captions / Submagic**
- Opus has a "virality score" said to factor in "trending content signals" [3P], but there is no official trending-template launch.
- Captions has 100+ templates [3P], but nothing is tied to live trends — [search summary](https://aitoolsatlas.ai/tools/opusclip); [FilmFont](https://filmfont.pages.dev/articles/captions-ai-vs-submagic-vs-opus-clip)
- Not verified on vendor changelogs.

**Viggle:** Not researched in this session (gap).

#### F. Hook libraries, swipe files, and paid trend reports

**Hookest**
- A categorised hook database from $9/mo, with a free plan.
- Rated 6.5/10. The reviewer called the library small and Instagram-heavy, and flagged conflicting messaging about clip reuse rights — [Makerstack review](https://makerstack.co/reviews/hookest-review/)

**Other hook tools:**
- Cut30: video database with swipe collections and CSV export for agencies — [dev.to](https://dev.to/documentorium/the-science-of-virality-how-cut30s-video-database-decodes-winning-content-b3f)
- Inflowave: extracts hooks only from posts that statistically outperformed the account's baseline — [Inflowave](https://inflowave.netlify.app/resources/extract-tiktok-hooks-from-viral-videos)
- Whop "500 viral hooks swipe file" — [Whop](https://whop.com/joined/earnsmartai01/products/500-viral-hooks-swipe-file/)

**Foreplay** (paid ads, not organic)
- Pricing [3P]: Basic $59/mo ($49 annual); Workflow $175 ($149); Agency $459 ($389).
- "Discovery" is a community ad library of 70M–100M+ ads [3P].
- Saves ads from TikTok Creative Center and Top Ads via a Chrome extension. I found no confirmed organic-TikTok library — [toolradar](https://toolradar.com/tools/foreplay); [Creatify Foreplay pricing](https://creatify.ai/es/blog/foreplay-pricing-(2026)-plans-credits-and-what-you-ll-actually-pay)

**Paid trend newsletters** (mostly $5–$20/mo; subscriber counts unverified)
- Trendally: $4.99/mo or $9.99/mo (Pro, with early alerts, hashtags and sounds) — [Gumroad](https://trendally.gumroad.com/l/xwxrh)
- The Fox Creative: TikTok Daily Trend Report at $19.99/mo — [Gumroad](https://thefoxcreative.gumroad.com/l/TiktokTrends)
- BNL Trend Report: $19.99/mo — [BNL](https://gopher-seahorse-5apj.squarespace.com/blog/stay-on-trend-and-on-time-with-the-bnl-trend-report)
- Coco Mocoe: weekly paid Friday report on Substack — [Substack](https://cocomocoe.substack.com/about)
- The Trend Report (Kyle Raymond Fitzpatrick): weekly, paywalled — [Substack](https://1234kyle5678.substack.com/p/trbiz-312024)
- LINK Chains: weekly TikTok trend report for brands — [Substack](https://trendsoftiktok.substack.com)
- New Engen: free monthly brand report — [New Engen](https://newengen.com/insights/monthly-tiktok-trend-report-for-brands/)

**Tribe / Creator.co trend reports:** Not researched (gap).

### Inferences
- **Price bands.** Solo-creator intelligence clusters at $15–$49/mo (1of10 Basic, vidIQ, Sandcastles Pro, Virlo Starter, Mysocial, OutlierKit). Team and agency tiers sit at $149–$499/mo. Brand-grade TikTok listening sits at $400–$999+/mo (Exolyt, Dash Social). Revid's $39/mo for library, remix and autopost undercuts the idea of charging a premium for "intel + creation" to faceless operators.
- **Virlo's numbers don't reconcile.** 3,261 paid subscribers at $49/mo would imply about $160k MRR, which conflicts with the founder-reported $31k MRR. Either the $31k figure predates January 2026, or many subscribers were on cheaper legacy plans or trials. Unresolved.
- **Two named creator tools are converging on the full loop.** Revid.ai (library, remix, autopost) and vidIQ (outliers, Instagram, clipping/generation) are both heading to "find viral, make yours, post it." Sandcastles and Virlo stop at scripts or "Content Studio" text outputs.
- **[obs] vidIQ's MCP manifest** in this session exposes tools named `vidiq_instagram_tiktok_outlier_search`, `vidiq_ig_accounts_from_outliers`, `vidiq_trending_videos`, `vidiq_generate_video`, `vidiq_generate_script` and `vidiq_instagram_publish_reel`. This suggests vidIQ already runs cross-platform (IG/TikTok) outlier search plus generation plus publishing behind its API, even though its public Outliers page still describes YouTube only. Not verified on public pages.
- **[obs] Higgsfield's MCP manifest** in this session exposes `tiktok_music_trending`, `virality_predictor`, a "genjutsu-trending" preset category, `get_presets source:'viral'` and `tiktok_publish`. That is trend-aware templates, generation and direct TikTok publishing in one product from a large AI-video player. Not verified on public pages.
- **The free platform tools are the biggest structural threat.** TikTok Symphony, which daily generates trend-informed videos for advertisers, and Instagram Edits, which offers trending audio and saved formats, cap what anyone can charge for "trending sound + template" features.
- **Format-level intelligence is barely served.** Format Finder sells a static, curated format list at $29–$97. Sandcastles and Virlo work at video or topic level. A competitor explicitly attacks Sandcastles for lacking a format library. That points to perceived demand for format abstraction, but only one small vendor's marketing is evidence of it.

### Gaps
- No revenue, funding or founder data for Sandcastles, Mysocial, Format Finder, Revid.ai or ClipTrend. TrustMRR's Virlo page returned 404.
- I could not see the full Virlo Indie Hackers interview (403), so the date of the $31k MRR figure is unknown.
- Not researched for lack of time: Viggle, Submagic templates, Tribe and Creator.co trend reports, Metricool's trend feature, and the TikTok One "Trends" UI.
- Spotter Studio and Trendpop current status unconfirmed. Tokchart unknown.
- No independent hands-on review comparing output quality of Sandcastles, Virlo, Revid or vidIQ.

---

## Q2. How do these tools obtain data, and what does that imply about legal/ToS risk and data cost for a newcomer?

### Takeaway
- **YouTube-first tools** can lean on the official YouTube Data API, but its default quota is tiny: 10k units/day, with each search costing 100 units, so about 100 searches/day. Scale requires an audit-gated quota increase.
- **TikTok and Instagram data** for commercial trend products comes almost entirely from scraping or third-party scraping APIs. TikTok's Research API excludes commercial use, and Meta's APIs only cover accounts you manage. Virlo built its own scrapers.
- **Legal risk is moderate but real.** US case law (Meta v. Bright Data, 2024) weakens ToS-breach claims against logged-off scraping of public data, but server-impairment theories survived in X v. Bright Data.
- **Data cost is affordable at niche scale.** Hundreds to low thousands of dollars a month covers thousands of tracked creators. It becomes a major cost line at "millions of videos daily" scale.

### Cited Findings
- **YouTube Data API:**
  - Default 10,000 units/day per project, with search.list costing 100 units (about 100 searches/day). Quota resets at midnight PT.
  - Increases require Google's quota-extension compliance audit, which "can take weeks and may be denied."
  - Sources are mostly third parties that sell API alternatives — [ChannelCrawler 2026-03-10](https://channelcrawler.com/insights/youtube-api-daily-limit-quotas-costs-and-how-to-scale-beyond-10000-units-channelcrawler); [Phyllo](https://www.getphyllo.com/post/is-the-youtube-api-free-in-2026-quota-limits-costs-when-to-pay); [Google quota doc](https://developers.google.com/youtube/data/determine_quota_cost?hl=it)
- **TikTok Research API:**
  - Restricted to qualifying academic institutions, takes about 4 weeks to approve, caps at 1,000 requests/day, and "explicitly prohibits commercial use."
  - TikTok's FAQ says "creators, advertisers, and commercial users are not eligible."
  - Sources are vendor blogs selling alternatives — [xpoz](https://www.xpoz.ai/blog/guides/tiktok-research-api-limits-access-and-alternatives/); [keyapi](https://www.keyapi.ai/blog/tiktok-research-api-commercial-trend-scanning/)
- **Instagram:** The Graph API covers only managed or authorized accounts. Not verified with Meta docs this session (see Gaps). Virlo's January 2026 data sources list no Instagram, and vidIQ only launched Instagram in May 2026 — [Virlo year in review](https://virlo.ai/blog/virlo-year-in-review); [vidIQ updates](https://vidiq.com/blog/category/product-updates/)
- **Virlo** "built its own collection infrastructure instead of relying on third-party data providers" for control over "data quality, costs, and the API" — [IH newsletter](https://www.sequenzy.com/api/email-examples/ulhbd2932zyfpqf3xtceq8ly/html)
- **Sandcastles and Mysocial** do not disclose their sources. Sandcastles offers optional account connection for first-party analytics — [Sandcastles](https://sandcastles.ai/); [Mysocial](https://mysocial.io/outliers/)
- **Third-party scraping API pricing** (2026 comparison pages, partly vendor-written):
  - ScrapeCreators: about $47 for 25,000 credits, 1 request per credit, no rate limits.
  - EnsembleData: $100–$1,400/mo in daily-expiring units.
  - Apify: the Clockworks TikTok actor costs $1.70 per 1,000 results; cheaper actors run $0.25–$0.30 per 1,000.
  - Some per-request APIs charge $0.002 per request.
  - Sources: [SocialCrawl 2026](https://www.socialcrawl.dev/blog/best-tiktok-data-apis-2026); [ScrapeCreators blog](https://scrapecreators.com/blog/best-tiktok-scrapers); [Apify EnsembleData](https://apify.com/ensembledata/tiktok-api/pricing)
- **Meta v. Bright Data (N.D. Cal., January 2024):** Judge Chen held that Meta's terms govern logged-in "use," so logged-off scraping of public data did not breach them. Commentators call it "very fact-specific." Meta later abandoned the suit — [JD Supra/FBM](https://www.jdsupra.com/legalnews/major-decision-affects-law-of-scraping-1470808/); [MediaPost](https://www.mediapost.com/publications/article/393996/meta-abandons-lawsuit-against-bright-data-over-scr.html)
- **X Corp. v. Bright Data:** Judge Alsup dismissed the scraping claims and found copyright preemption of the data-sale claims. X was later allowed to revive the case on a server-impairment theory — [MediaPost](https://www.mediapost.com/publications/article/401510/x-corp-can-revive-scraping-battle-with-bright-dat.html)
- **Remix rights:** Revid limits "Restyle" to footage you have rights to — [Revid PL](https://www.revid.ai/pl/features/repurpose-viral-videos). Zawa asserts its output is "original content, not a replication" — [Zawa](https://zawa.ai/viral-video-clone)

### Inferences
- **Cost arithmetic (inference, not quoted).** Assume 10,000 tracked creators, each refreshed daily for about 25 recent posts.
  - With per-result pricing: about 250k results/day, or about 7.5M/month. That costs about $1.9k/mo at $0.25 per 1k, or about $12.8k/mo at $1.70 per 1k.
  - With per-request pricing, if one request returns a creator's 25 posts: about 300k requests/month, or about $560/mo at about $0.0019 per request.
  - A newcomer covering a narrow niche (1–3k creators) can run for low hundreds of dollars a month. Matching Sandcastles' or Virlo's breadth costs real money, or means building scrapers in-house as Virlo did.
- **Legal and ToS risk is asymmetric.** YouTube via the official API is low-risk but quota-capped. TikTok and Instagram via scraping is legally defensible for logged-off public data under current US precedent, but exposes the product to account and IP blocking, sudden breakage and platform cease-and-desists. Relying on a reseller (Apify, ScrapeCreators) pushes some of that risk onto the vendor.
- **Instagram is the hardest platform to cover reliably.** That is both a moat for whoever does it and a reason incumbents cover it thinly.
- **Remixing structure (hook timing, pacing, beats) is lower-risk than re-uploading or restyling the source footage.** A format-level product, which abstracts structure away from any single video, is legally cleaner than "clone this video" tools. This is an inference, not legal advice.

### Gaps
- I did not verify TikTok's or Meta's own developer terms directly. Instagram Graph API limits on other accounts' Reels views are unconfirmed.
- No disclosed data spend from any vendor.
- No TikTok-specific scraping litigation was found.

---

## Q3. Which audiences pay most for trend intelligence (solo creators, faceless operators, agencies, brands, TikTok Shop sellers)?

### Takeaway
- **Brands and agencies pay the most per seat** ($149–$999+/mo).
- **Agencies are the best-documented converting segment** for short-form intelligence: Virlo grew from about $1k to about $31k MRR after pivoting to agency workflows.
- **Solo creators and faceless operators are the largest pool but pay the least** ($9–$49/mo). They are being served by bundles that throw in generation and autopost (Revid at $39).
- **TikTok Shop sellers pay $39–$46/mo** for commerce-centric tools that are weak on organic format intelligence.

### Cited Findings
- **Agencies:** Virlo "rebuilt its offer around [agencies'] research workflow" after agencies "seemed to like the early product most." It moved from about $1k MRR (March 2025) to $31k+ — [IH newsletter](https://www.sequenzy.com/api/email-examples/ulhbd2932zyfpqf3xtceq8ly/html)
- **Agency tiers across vendors:**
  - Virlo Pro: $199/mo, positioned "for growing agencies & teams," with 3 seats and Slack/webhook alerts — [Virlo pricing](https://virlo.ai/pricing)
  - Sandcastles Titan: $499/mo, with agency guest access and 20 workspaces — [Sandcastles](https://sandcastles.ai/)
  - OutlierKit Max: $1,999/yr for "Agencies running client channels" — [OutlierKit pricing](https://outlierkit.com/pricing)
  - Mysocial Authority Intelligence: $349/mo — [Mysocial](https://mysocial.io/outliers/)
- **Researcher segments:** Virlo names market and consumer researchers, editorial teams, strategic planners and competitive-intelligence teams as segments, pivoting away from the "general creator" — [Virlo year in review](https://virlo.ai/blog/virlo-year-in-review)
- **Brands:**
  - Exolyt: Essentials $400/mo, Advanced $950/mo — [Exolyt](https://exolyt.com/pricing)
  - Dash Social: Trending Sounds in plans "starting at $999/month" — [Dash Social](https://www.dashsocial.com/features/tiktok-trending-sounds)
  - Sprout: about $249/mo per seat [3P] — [syncly](https://syncly.app/blog/sprout-social-vs-hootsuite)
  - Shortimize: $99–$249/mo for brands and apps running creator programs — [Shortimize](https://www.shortimize.com/vs/virlo)
- **TikTok Shop sellers:** Kalodata about $45.90/mo; FastMoss from $39/mo [3P] — [Creatify](https://creatify.ai/blog/kalodata-pricing-plans-and-what-you-ll-actually-pay-in-2026); [Virlo compare](https://virlo.ai/compare/kalodata-vs-fastmoss)
- **Solo creators:**
  - 1of10 Basic $15/mo; vidIQ Boost $16.58/mo (annual) — [1of10](https://1of10.com/pricing); [vidIQ](https://vidiq.com/pricing/)
  - Hookest from $9/mo — [Makerstack](https://makerstack.co/reviews/hookest-review/)
  - Paid trend newsletters $4.99–$19.99/mo — [Trendally](https://trendally.gumroad.com/l/xwxrh); [Fox Creative](https://thefoxcreative.gumroad.com/l/TiktokTrends)
- **Faceless operators:**
  - Revid: $39/mo Growth with viral library, remix and autopost; $199 Ultra with 10 autopost workers — [Revid pricing](https://www.revid.ai/pricing)
  - StoryShort: about $19–$39 entry [3P] — [Stork](https://www.stork.ai/en/storyshort)
- **Freemium conversion benchmark:** Virlo converted 5.25% of registered users to paid (3,261 of 62,115) — [Virlo year in review](https://virlo.ai/blog/virlo-year-in-review)

### Inferences
- **A solo founder's revenue-per-customer is 4–10× higher selling to agencies or brand social teams** ($199–$499) than to creators ($19–$49). But the agency segment already has Virlo (proven, with alerts) and Sandcastles (Titan).
- **Faceless operators value output volume over insight.** They will pay for "intel" mostly as a feature inside a generator or autoposter. Revid's bundle shows it, and so does StoryShort's template-driven appeal. That makes intelligence a differentiator for a generator, not a standalone product, in this segment.
- **TikTok Shop sellers are an under-served overlap.** Commerce tools (Kalodata, FastMoss) track products and sales, not organic formats. Zawa and Quinn target "remix this format with my product." The overlap of format intelligence and product-video generation is plausible, but I found no pricing or traction evidence for it.

### Gaps
- No willingness-to-pay surveys or churn data by segment.
- No revenue split between agency and creator customers at any vendor.
- No data on how many faceless operators pay for separate intelligence tools.

---

## Q4. Are there signs of unmet demand (complaints that outlier tools are YouTube-only, trend reports too slow, etc.)?

### Takeaway
The demand signals are real but mostly indirect.
- **"YouTube-only" is a verified limitation of the biggest outlier tools** (vidIQ Outliers, OutlierKit, Viewstats, 1of10, TubeBuddy). It is already being served by short-form tools (Sandcastles, Virlo, Mysocial), so the complaint alone is not an open gap.
- **Weaker coverage:** Instagram coverage is thin, data freshness and niche accuracy draw complaints, and there is no format abstraction. Weekly or monthly human trend reports don't match a 24–48h trend window.
- I found no Reddit corpus of complaints, which is a gap in the evidence.

### Cited Findings
- **OutlierKit** is "Strictly YouTube-only: Does not track TikTok, Instagram Reels…"; its FAQ confirms this — [creatoreconomytools](https://creatoreconomytools.com/tool/outlierkit)
- **vidIQ Outliers** covers YouTube long-form and Shorts only — [vidIQ Outliers](https://vidiq.com/features/outliers/)
- **1of10's** pricing page mentions only YouTube — [1of10 pricing](https://1of10.com/pricing)
- **Virlo:**
  - A Trustpilot 1-star review complained about outlier and niche-update issues — [Trustpilot](https://es.trustpilot.com/review/virlo.ai)
  - A SourceForge reviewer said the platform "needs more data" — [SourceForge](https://sourceforge.net/software/product/Virlo/)
  - 7.54% of indexed videos (107,964) were classified "Unknown" — [Virlo year in review](https://virlo.ai/blog/virlo-year-in-review)
- **Sandcastles' lack of a format library:** A competitor attacks Sandcastles for having "No curated format library," saying users must infer patterns from top videos — [Format Finder](https://formatfinder.onepeakcreative.com/resources/compare/format-finder-vs-sandcastles-ai)
- **Speed:** Zawa says trend windows last "24 to 48 hours at most" [vendor] — [Zawa](https://zawa.ai/viral-video-clone). Paid trend reports are mostly weekly (Coco Mocoe, LINK Chains, The Trend Report) or monthly (New Engen). The Fox Creative sells a daily report at $19.99/mo — [Coco Mocoe](https://cocomocoe.substack.com/about); [Fox Creative](https://thefoxcreative.gumroad.com/l/TiktokTrends); [New Engen](https://newengen.com/insights/monthly-tiktok-trend-report-for-brands/)
- **Exolyt** refreshes TikTok data only 1×/day on Basic and 2×/day on Essentials ($400/mo) — [Exolyt](https://exolyt.com/pricing)
- **StoryShort** critique: cost per video becomes uncompetitive past 10–15 videos/month, and the AI's narrative choices need "tweaking" — [FluxNote](https://fluxnote.io/guides/storyshort-review-honest-2026); [AIIndigo](https://aiindigo.com/blog/storyshort-review-2026-the-reality-of-faceless-channel-automation)
- **Viewstats:** users report "frequent crashes and slow performance" — [creatoreconomytools](https://creatoreconomytools.com/tool/viewstats)
- **ClipTrend's** launch drew 0 upvotes and ranked #152 on its Product Hunt day — [PH/search summary](https://www.producthunt.com/products/cliptrend-ai)

### Inferences
- **Supply has already met the "outlier tools are YouTube-only" complaint.** Sandcastles and Virlo both claim 100k+ users or 60k+ registered users on short-form. A newcomer can't win on platform coverage alone.
- **The least-served needs are:**
  1. **Format abstraction:** "these 40 outliers are all the same 'POV + reveal + text stack' format," rather than a list of videos.
  2. **Lifecycle and saturation timing:** is this format emerging, peaking or over-saturated in my niche?
  3. **Reliable Instagram Reels coverage.**
  4. **Freshness inside the 24–48h window** at a creator price point.
- **ClipTrend shows demand may be weak for trend templates alone.** Higgsfield and TikTok/IG native tools already give these away or bundle them, which is likely why ClipTrend launched to so little interest.

### Gaps
- No Reddit or creator-forum threads surfaced in searches (r/NewTubers, r/TikTokCreators, etc.). Direct complaint evidence is thin and largely competitor-authored.
- No G2 or Trustpilot review counts or ratings for Sandcastles, 1of10 or Revid were verified.
- No search-volume data for terms like "TikTok outlier finder."

---

## Q5. Synthesis: Is "format intelligence + generation" already done well by anyone? Open slots, strongest wedge, verdict

### Takeaway
**Verdict: PARTIALLY REAL.**
- The broad gap ("a viral video creator that finds what's going viral and lets me make my version") is **FALSE**. It is crowded and productised:
  - Revid.ai sells library, one-click remix and autopost at $39/mo with 14k+ creators claimed.
  - vidIQ is assembling outliers, Instagram and generation.
  - Higgsfield, ClipTrend, Zawa, and the free TikTok Symphony and Instagram Edits all offer trend-template or link-clone generation.
- The **real** gap is narrower: **live, data-derived format-level intelligence** (clustering outliers into reproducible formats with lifecycle and saturation signals) that maps directly to a generation template, for a specific audience. Nobody does that well:
  - Format Finder is static and curated.
  - Virlo clusters by topic or narrative.
  - Sandcastles and Revid work at video level.
  - ClipTrend covers AI-effects only, with negligible traction.
- **Narrowest credible wedge:** a "format radar" for faceless short-form operators in 2–4 high-RPM niches. It would:
  - Detect format clusters rising across TikTok and Shorts (Instagram later) from a tracked set of faceless accounts.
  - Label each format's lifecycle stage (emerging, peaking or saturated) with adopter count and velocity.
  - Ship every format as a one-click generation template, using third-party video models, at $29–$79/mo.
  - Optionally add a B2B tier ($199+) that sends agencies daily format alerts for a client's vertical by Slack or email.

### Cited Findings
- **Video-level intelligence plus scripts is crowded:** Sandcastles ($39–$499), Virlo ($49–$199+), 1of10 ($15–$417), OutlierKit ($25–$167), vidIQ ($0–$39+), Mysocial ($49–$349), Viewstats ($49.99 Pro; $249+ Business) — [Sandcastles](https://sandcastles.ai/); [Virlo](https://virlo.ai/pricing); [1of10](https://1of10.com/pricing); [OutlierKit](https://outlierkit.com/pricing); [vidIQ](https://vidiq.com/pricing/); [Mysocial](https://mysocial.io/outliers/); [Viewstats](https://www.viewstats.com/pricing)
- **Intelligence plus generation plus autopost exists:** Revid offers "3M+ viral videos to remix," "one-click remix," channel watching and Auto-Mode publishing, with 14,258+ creators and 30,000+ videos a month [vendor] — [Revid pricing](https://www.revid.ai/pricing)
- **Free platform-native trend-aware creation:**
  - TikTok Symphony Creative Studio auto-generates daily video options, and Symphony Agent uses "insights from top-performing content and emerging trends" — [TikTok blog](https://ads.tiktok.com/business/es/blog/tiktok-symphony-ai-creative-suite); [Vidjet](https://www.vidjet.com/blog/latest-features-on-tiktok-symphony-studio-july-2026-update)
  - Instagram Edits offers trending audio, "Use audio" and saved formats — [Hypebeast](https://hypebeast.com/2026/6/instagram-edits-app-adds-beat-markers-and-ai-tools)
- **Trend-effect templates plus generation:**
  - Higgsfield: 60+ viral presets "added regularly to match current trends" — [Higgsfield](https://higgsfield.ai/blog/how-to-make-viral-videos-viral-presets)
  - ClipTrend: 40–50+ templates, each with live viral proof videos — [PH](https://www.producthunt.com/products/cliptrend-ai)
- **Link-based format cloning:** Zawa extracts hook timing, pacing, overlays and reveal sequence, then regenerates — [Zawa](https://zawa.ai/viral-video-clone)
- **Static format library:** Format Finder has 65+ named formats with hook patterns, beats and shot structures, at $29–$97/mo — [Format Finder](https://formatfinder.onepeakcreative.com/resources/compare/format-finder-vs-sandcastles-ai)
- **Topic clustering exists, but format clustering is undocumented:** Virlo lists "Topic-level clustering" and "Orbit" narrative acceleration — [Virlo year in review](https://virlo.ai/blog/virlo-year-in-review)
- **Proof that intelligence-led short-form SaaS can grow fast:** Virlo went from launch on 2025-03-01 to 62k registered users and 3.2k paid by 2026-01-02 [vendor-metrics], and from $1k to $31k MRR [founder] — [Virlo year in review](https://virlo.ai/blog/virlo-year-in-review); [IH](https://www.indiehackers.com/post/KgfHz813vyyWeszqJMIi)

### Inferences

**Category status by layer**

| Layer | Status | Evidence |
|---|---|---|
| Video-level outliers (YouTube) | Saturated | vidIQ, 1of10, OutlierKit, Viewstats, TubeBuddy, Spotter |
| Video-level outliers (short-form, multi-platform) | Crowded and proven | Sandcastles, Virlo, Mysocial, plus Chrome extensions |
| Trending sounds and hashtags | Commoditised or free | TikTok Creative Center, Edits, Dash Social, Exolyt, vidIQ sounds tool |
| Hook libraries and swipe files | Cheap commodity | Hookest $9, Whop swipe files, Inflowave |
| Link-to-clone ("remix this video") | Commodity | Zawa, UGCCopilot, Quinn, CloneUP, n8n template |
| Viral library plus remix plus autopost (faceless) | Exists, priced low | Revid.ai $39/mo |
| Trend-effect templates plus generation | Exists, often free or bundled | Higgsfield presets, ClipTrend, TikTok Symphony |
| Live format-level clusters plus lifecycle plus template | Open, unproven | Format Finder (static), Virlo (topic), ClipTrend (effects only) |
| Reliable Instagram Reels format intelligence | Thin | Virlo's Jan 2026 sources excluded IG; vidIQ IG only since May 2026 |
| Niche-vertical B2B format alerts | Partly served | Virlo Pro has Slack/webhook alerts at $199, but they are not format-level or vertical-packaged |

**Strongest wedge, adversarially tested**
- **For it:**
  - The wedge combines the one unserved abstraction (format plus lifecycle) with a generator, so it is not "yet another outlier list."
  - Faceless formats are structurally reproducible (stock or B-roll, voiceover, captions, gameplay or Reddit layouts), so a format can be turned into a template mechanically. Face-led trends can't.
  - A narrow niche keeps scraping cost in the low hundreds of dollars a month (see the Q2 arithmetic).
  - Abstracting structure is legally cleaner than cloning footage.
- **Against it:**
  - Revid already has a 3M-video library and could add clustering. vidIQ and Higgsfield have the data and generation pieces and appear to be wiring them together.
  - TikTok and Meta give away trend-aware creation for free.
  - Format detection is technically hard: it needs multimodal clustering (shot structure, text overlays, audio, pacing), not a views-to-median ratio.
  - Creators may not pay a premium for "lifecycle stage" over a $39 bundle.
  - ClipTrend's flat launch shows templates alone don't pull.
- **Alternative wedge with higher ARPU:** B2B "format alerts for brand social teams in one vertical" (for example beauty or CPG), at $199–$499/mo. This follows Virlo's proven pivot to agencies, but competes with Virlo Pro and Dash Social. It suits a founder who can sell to agencies more than one building a StoryShort-style consumer tool.

**Verdict detail:** The gap is PARTIALLY REAL. The generic "viral-format video creator" is FALSE, because it is crowded and sold at about $39/mo. "Live format-level intelligence with lifecycle → one-click generation, for faceless operators in a few niches" is REAL but unproven. Nobody I found sells it, and no demand data confirms anyone will pay a premium for it.

### Gaps
- No vendor documents format-level clustering. I can't rule out that Sandcastles, Virlo or Revid do it internally without marketing it.
- No user research confirms that creators want lifecycle or saturation signals enough to pay for them.
- No data on the conversion uplift a format library adds to a generator (Revid's library usage, for example).
- I didn't verify Higgsfield's or vidIQ's integrated intel-plus-generation loops on public pages; they rest on [obs] MCP manifests only.
