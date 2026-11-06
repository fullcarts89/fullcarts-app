# Viral short-form formats, hook/retention evidence, trend life cycles, and legal data access for trend detection (TikTok / Reels / Shorts) — as of Nov 2026

Evidence-quality labels used throughout:
- **[PLATFORM]** = published by TikTok/Meta/YouTube (policy pages, API docs, newsroom, exec statements)
- **[PLATFORM-COMMISSIONED]** = research run or co-authored by a platform with a partner (usually about ads)
- **[PEER-REVIEWED]** / **[PREPRINT]** = academic
- **[VENDOR]** = study or blog from a company selling tools (often a competitor of the SaaS under consideration)
- **[JOURNALISM]** = trade/news reporting
- **[ANECDOTE]** = creator claims, promotional pages, single examples
- **[COURT/LAW-FIRM]** = court rulings or law-firm analyses of them

---

## Q1. Which repeatable short-form formats exist, which can be made faceless/AI-only, and what evidence says they perform?

### Takeaway
The only formats with documented **durability** evidence are utility/how-to ("hack") content and narrative/story formats. Faceless template formats (Reddit-story-over-gameplay, fake-text chats, AI POV history, slideshows) clearly earn huge view totals. But on every platform they now sit inside policy categories that cut monetization or reach unless the creator adds something original. Hard per-format performance data (beyond anecdotes and vendor marketing) mostly doesn't exist. No peer-reviewed or platform source ranks named formats against each other.

### Cited Findings

**Cross-format evidence**
- Publicis Groupe + TikTok white paper "Globalisation of TikTok Trends": the trend type that lasts longest is the **"utility hack"**, meaning practical, instructional content people save rather than just watch. A second durable pattern is localization, meaning trends rooted in local customs. **[PLATFORM-COMMISSIONED / industry]** — [Campaign Asia](https://www.campaignasia.com/article/publicis-and-tiktok-crack-the-code-on-why-only-27-trends-survive-beyond-two-weeks/4bj3k6n8htrywyqvppeyk43j5r)
- TikTok-commissioned creative research found native-feeling creative lifted watch time. Real people: +9%. Remixing a trend: +14%. A creative story: +16%. (This is ad creative, not organic content.) **[PLATFORM-COMMISSIONED]** — [Social Media Today](https://www.socialmediatoday.com/news/tiktok-shares-new-notes-on-how-to-maximize-ad-effectiveness-in-the-app/694989/)
- TikTok + CreatorIQ report: showing a person early raises "hooking power" by 50% and ad recognition by 32%. A creator saying "you" in the first five seconds was linked to a 128% boost in purchase intent. This counts *against* fully faceless formats, at least for ads. **[PLATFORM-COMMISSIONED]** — [Marketing Brew](https://marketingbrew.com/stories/2023/12/18/pay-attention-to-me-report-shares-brand-tips-for-catching-users-interest-on-tiktok)
- Ling et al. (ACM WebSci 2022) built a labeled dataset of **400 TikTok videos** and trained virality classifiers. They found on-screen text "does not impede video's virality but rather facilitates it." This is a small, older study (2022). **[PEER-REVIEWED]** — [ACM DL](https://dl.acm.org/doi/fullHtml/10.1145/3501247.3531551) / [arXiv](https://arxiv.org/pdf/2111.02452)
- "Shorter Is Different" analyzed **248 million videos** on Kuaishou (a Chinese short-form platform) against Bilibili (long-form). On short-form, top videos attract collective attention more effectively, users interact less per view, and **ordinary creators have a higher probability of producing hit videos**. **[PREPRINT]** — [arXiv 2410.16058](https://arxiv.org/abs/2410.16058)
- I found no large, peer-reviewed 2024–2026 study modelling TikTok virality against duration, hook, and text overlay. A longitudinal finfluencer preprint found "only a negligible overall association between duration and engagement." **[PREPRINT]** — [arXiv 2607.05203](https://arxiv.org/pdf/2607.05203)
- Vendor "virality" datasets exist: Revid claims 176,367 videos analyzed, and Riffkit claims 1,111 "winning TikToks" with a median hook of 4.1 s. Neither is peer-reviewed, and both sell AI video tools. **[VENDOR]** — [Revid](https://www.revid.ai/blog/what-makes-a-tiktok-video-go-viral); [Riffkit](https://riffkit.ai/research/tiktok-hook-study)
- Video vs image: Metricool says video gets 5x more views and 6x more interactions than images on TikTok. No methodology is shown. **[VENDOR]** — [Metricool TikTok study](https://metricool.com/tiktok-study/?pStoreID=.)

**Format-by-format evidence**

*Reddit-story narration over gameplay ("sludge"/brainrot)*
- Wikipedia's "Sludge content" entry describes the broader genre of repetitive background gameplay (Subway Surfers being the best-known example) stacked under other content. **[SECONDARY]** — [Wikipedia: Sludge content](https://en.wikipedia.org/wiki/Sludge_content)
- A critic describes the format: an AI voice reads a Reddit story ("usually stolen but sometimes credited") over random gameplay with large captions. **[COMMENTARY]** — [Inkwell Creative Substack](https://inkwellcreative.substack.com/p/i-watch-too-many-of-those-reddit)
- Earnings claims such as "$50k/month from Reddit horror stories" appear only on promotional TikTok discover pages. **[ANECDOTE, unverified]** — [TikTok discover page](https://www.tiktok.com/discover/do-reddit-stories-make-money)
- Gumroad sellers offer "no copyright" Minecraft-parkour background packs. This suggests a commoditized, widely reused asset supply. **[ANECDOTE]** — [Gumroad listing](https://howtoai.gumroad.com/l/freetiktokassets)
- YouTube's reused-content policy explicitly lists "Content that exclusively features readings of other materials you did not originally create" as not monetizable. Reddit-story read-alouds fall squarely under this. **[PLATFORM]** — [YouTube channel monetization policies](https://support.google.com/youtube/answer/1311392)
- Reddit's terms say user content is owned by the redditors who created it. Commercial use of the Data API needs a separate negotiated agreement. **[SECONDARY summaries of Reddit terms]** — [Activepieces guide](https://www.activepieces.com/blog/reddit-api-access-in-2026-how-to-get-started); [The Register (2023)](https://www.theregister.com/2023/04/18/reddit_charging_ai_api/)
- On **Sep 30, 2026**, Reddit announced:
  - new public API access requests stop Oct 31, 2026
  - access removals for unregistered apps begin Jan 12, 2027
  - remaining public Data API access closes in **March 2027**
  - RSS feeds end Nov 13, 2026

  Reddit cited large-scale scraping and commercial use of its conversations, and is pushing apps to its Developer Platform (Devvit). **[JOURNALISM, citing Reddit]** — [PPC Land](https://ppc.land/reddit-to-halt-public-data-api-access-in-march-2027-as-14-000-apps-register/); [TechRepublic](https://www.techrepublic.com/article/news-reddit-rss-public-api-shutdown/); [Decrypt](https://decrypt.co/379892/reddit-killing-rss-feeds-and-public-api-access-to-fight-ai-scrapers)

*Fake text-message / chat stories*
- I found no verified channel stats. Evidence is mostly vendor generator pages describing "AI-voiced chat stories over gameplay footage": [MakeViral](https://www.makeviral.ai/tools/fake-text-message-video-generator), [Brainrot Shorts](https://www.brainrotshorts.com/texting-story-maker), [Flickify](https://www.flickifyai.com/tools/fake-text-video-generator), [ClipGoat](https://www.clipgoat.com/tools/free-fake-text-message-videos-online-generator). A tutorial cites a "Texty Stories" channel with "millions" of views on its top video, with no hard figures. **[VENDOR/ANECDOTE]** — [Toolify](https://www.toolify.ai/ai-news/viral-tiktok-youtube-shorts-fake-text-video-tutorial-3366925)
- YouTube's policy lists "Image slideshows, templated storylines, or **scrolling text** with minimal or no narrative, commentary, or educational value" as generic/repetitive (not monetizable). **[PLATFORM]** — [YouTube policy](https://support.google.com/youtube/answer/1311392)

*AI history / "what-if" POV*
- The AI "POV: you wake up as…" history trend (gladiator in Rome, Black Plague, etc.) was started by the account **TimeTravellerPOV** in late January 2025 and peaked around **February 2025**. Reports cite "millions of views" (single lower-tier source). The videos are often inaccurate, with six-finger artifacts. **[JOURNALISM, lower tier]** — [ComingSoon](https://comingsoon.net/?p=1924475); [Dexerto mirror](https://jamtest.dexerto.com/tiktok/tiktoks-viral-ai-history-pov-trend-lets-you-go-back-in-time-in-first-person-sort-of-3137127)
- Veo 3–generated racist videos amassed millions of views on TikTok (mid-2025), illustrating the moderation and brand-safety risk of AI-only formats. **[JOURNALISM]** — [Media Matters](https://www.mediamatters.org/tiktok/racist-ai-generated-videos-are-newest-slop-garnering-millions-views-tiktok?page=36); [Ars Technica via mirror](https://hn.jakechampion.name/reader/https://arstechnica.com/ai/2025/07/racist-ai-videos-created-with-google-veo-3-are-proliferating-on-tiktok)
- Kapwing's AI Slop Report (Nov 2025) reviewed about 15,000 top trending channels (top 100 per country). It found **278 AI-slop channels with 63B+ views, 221M subscribers, and an estimated ~$117M/yr revenue**. In a fresh-account test, **21% of the first 500 Shorts were AI-generated** and 33% were "brainrot." This shows AI-only formats *do* reach scale. **[VENDOR study (Kapwing sells video tools), widely reported]** — [The Decoder](https://the-decoder.com/one-in-five-youtube-shorts-shown-to-new-users-is-ai-generated-slop-study-finds/); [TechSpot](https://www.techspot.com/news/110735-over-21-youtube-now-ai-slop-report.html); [The Standard (HK)](https://www.thestandard.com.hk/innovation/article/320275/Over-21-percent-videos-shown-to-new-YouTube-users-are-AI-slop-study-finds)
- A re-check of Kapwing's dataset found **16 of the top 100** most-subscribed AI-slop channels already deleted or stripped of content. **[JOURNALISM]** — [Daily Dot](https://dailydot.com/youtube-ai-slop-study)

*Tutorial / hack / utility*
- "Utility hack" content is the most persistent trend type in the Publicis/TikTok study (see above). — [Campaign Asia](https://www.campaignasia.com/article/publicis-and-tiktok-crack-the-code-on-why-only-27-trends-survive-beyond-two-weeks/4bj3k6n8htrywyqvppeyk43j5r)
- 5-Minute Crafts, a life-hack channel, reports about **28.59B views**. It is the canonical example of an evergreen, templated, largely faceless how-to format at scale. **[SECONDARY]** — [Wikipedia: 5-Minute Crafts](https://en.wikipedia.org/wiki/5-Minute_Crafts)

*Slideshow / carousel-to-video*
- YouTube: image slideshows with minimal narrative are not monetizable (above). **[PLATFORM]**
- Instagram (Apr 2026): the originality policy was extended beyond Reels to **photos and carousels**. Accounts posting mostly "unoriginal content" will no longer be recommended to non-followers. **[JOURNALISM]** — [PetaPixel](https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/); [Digital Camera World](https://www.digitalcameraworld.com/tech/social-media/two-years-later-instagram-is-finally-giving-photographers-the-same-protection-as-videographers-with-this-key-change)

*Split-screen reaction / duet / stitch / compilation*
- YouTube's reused-content policy excludes "Content that gets views from mostly non-verbal reactions to your videos without added voice commentary," "Short videos you compiled from other social media websites," and "Content uploaded many times by other creators." The policy applies "even if you have permission." Reused content is allowed "if viewers can tell that there's a meaningful difference." **[PLATFORM]** — [YouTube policy](https://support.google.com/youtube/answer/1311392)
- TikTok Creator Rewards reportedly excludes Duets, Stitches, repurposed content, and lip-syncs to copyrighted music from "original" content. **[SECONDARY]** — [Nuelink](https://blog.nuelink.com/tiktok-creator-rewards-program/); [Metricool](https://metricool.com/tiktok-creator-fund/)

*Trend-audio lip-sync*: see TikTok Creator Rewards exclusions above. Sound life-cycle data is under Q3.

*Formats with no specific performance evidence found*: "would you rather"/quiz, listicles/top-5, POV skits, storytime, green-screen commentary, before/after, day-in-the-life, "things I wish I knew," tier lists. See Gaps.

### Inferences
- Synthesized productisation table (my inference from the findings above, not a measured ranking):

| Format | Platforms | Faceless/AI-only feasible? | Evidence of performance (quality) | Saturation / penalty risk |
|---|---|---|---|---|
| Tutorial / utility hack / listicle-explainer | All 3 | Yes (voiceover + b-roll/stock/AI) | Most durable trend type (Publicis/TikTok); 5-Minute Crafts scale (secondary) | Low if it carries real info value; YouTube explicitly protects "educational value" |
| Reddit-story over gameplay | All 3 | Yes (TTS + stock gameplay) | Huge historical reach (anecdote/secondary only) | **High**. It is literally YouTube's "readings of other materials" exclusion. Reddit copyright plus Reddit API closure (Mar 2027) add a sourcing risk. Gameplay packs are commoditized |
| Fake text / chat story | All 3 | Yes | Vendor/anecdote only | High. YouTube names "scrolling text…templated storylines" |
| AI history / what-if POV | All 3 | Yes (gen-video) | Kapwing shows AI channels reach tens of billions of views; the POV trend peaked within weeks (Feb 2025) | High and rising: TikTok AIGC slider, labeling, YouTube "AI slop" priority, channel deletions |
| Slideshow / carousel-to-video | TikTok photo mode, IG carousels, Shorts | Yes | No reliable data | YouTube demonetizes low-narrative slideshows; IG originality policy now covers carousels |
| Split-screen reaction / duet / compilation | All 3 | Partly (needs commentary) | None | High on YouTube (non-verbal reactions, compilations) and TikTok CRP |
| Trend-audio lip-sync / meme template | TikTok, Reels | Needs a face or avatar | Remixing a trend +14% watch time (ads) | Short-lived (days to weeks); copyrighted audio excluded from TikTok CRP |
| Storytime / POV skit / day-in-the-life / green-screen commentary | All 3 | Mostly need a face; AI-avatar versions possible | Story +16% watch time (ads); a person early → +50% hook (ads) | Low penalty (original), but hard to template |
| Would-you-rather / quiz / tier list | All 3 | Yes | No data found | Medium. Templated look risks YouTube's "generic or repetitive" category if each video only differs slightly |

- **Evergreen templates** (good library candidates): utility/how-to, explainers/listicles with real facts, story narratives where the story is original or licensed, quiz/would-you-rather (engagement-driven, but unproven).
- **Trend formats** (need live detection): trend audio, meme templates, AI-aesthetic trends like POV history, challenge formats.
- The platform-commissioned evidence that showing a human early raises hook power suggests a structural ceiling for pure-faceless output, at least in ad contexts. An AI-avatar or "face" option may matter for some templates.
- "Proven viral format" is a marketing claim, not something any platform validates. The defensible product claim is "formats with durable evidence" (utility/story) plus "currently rising formats" detected from data.

### Gaps
- No platform-published or peer-reviewed comparison of named formats (Reddit stories vs quizzes vs listicles etc.). All format-specific performance claims are vendor or anecdote.
- No verified channel revenue or view data for Reddit-story, fake-text, or would-you-rather channels. Social Blade or vidIQ lookups of specific channels would be needed, and I didn't find a Tubefilter case study on these.
- Couldn't verify whether TikTok's "photo mode"/carousel content gets distribution comparable to video (only an unverified Metricool claim).
- The full "Shorter Is Different" paper (decay metrics, half-lives) was not read; only the abstract.

---

## Q2. What does platform and third-party evidence say about hooks, first-seconds retention, length, captions, and loops?

### Takeaway
The strongest data on hooks comes from TikTok Marketing Science and is about **ads**: about 50% of impact lands in the first 2 seconds and about 90% of ad recall in the first 6. The organic ranking guidance platforms have published is at signal level: Instagram's top three signals are watch time, likes per reach, and sends per reach. The popular "3-second rule," loop tricks, and fixed optimal lengths have no platform-published or peer-reviewed backing that I could find. YouTube changed what a "Shorts view" means in 2025 and again in 2026, so cross-period view comparisons are unreliable.

### Cited Findings
- TikTok Marketing Science "Value of a View" internal meta-analysis (2021): **90% of ad recall and 80% of awareness impact occur within the first 6 seconds**. **[PLATFORM, ads, 2021: older]** — [MetrixLab whitepaper citing TikTok](https://metrixlab.com/?p=372211)
- TikTok Marketing Science: **50% of a TikTok ad's impact is realized in the first 2 seconds**. The first 6 seconds capture 90% of cumulative ad-recall impact and about 80% of awareness. **[PLATFORM, ads]** — [Social Media Today](https://www.socialmediatoday.com/news/tiktok-shares-new-notes-maximize-ad-effectiveness/694989/)
- Vidmob × TikTok analysis of **1,678 TikTok ads**: featuring a human *and* a product in the first 6 s raised 6-second view-through rate by about 5% over average. Outdoor shooting lowered it by 26%. **[PLATFORM-PARTNER / VENDOR]** — [Vidmob PDF](https://www.vidmob.com/wp-content/uploads/2024/02/Vidmob-x-Tik-Tok-Hook-Analysis-.pdf)
- TikTok + CreatorIQ: a person shown early gives +50% "hooking power." Saying "you" in the first 5 s is linked to +128% purchase intent. **[PLATFORM-COMMISSIONED]** — [Marketing Brew](https://marketingbrew.com/stories/2023/12/18/pay-attention-to-me-report-shares-brand-tips-for-catching-users-interest-on-tiktok)
- Toluna research for TikTok tested 150 ads among 7,163 users in four countries. **[PLATFORM-COMMISSIONED]** — [Toluna](https://tolunacorporate.com/es/wp-json/wp/v2/posts/3749)
- Adam Mosseri (Jan 2025): "The top three signals that matter most for ranking are **watch time, likes and sends**." Creators are told to watch average watch time, likes per reach, and sends per reach. Secondary sources say sends matter slightly more for unconnected (non-follower) reach. The "3–5x weight of sends" figure has unclear attribution. **[PLATFORM exec statement via trade press]** — [Social Media Today](https://www.socialmediatoday.com/news/instagram-shares-algorithm-2025/738034/); [Dataslayer](https://www.dataslayer.ai/blog/instagram-algorithm-2025-complete-guide-for-marketers)
- Instagram reportedly weighs both relative watch time (% viewed) and absolute watch time (seconds). This was not verified in Mosseri's own words. **[SECONDARY]** — [Dataslayer](https://www.dataslayer.ai/blog/instagram-algorithm-2025-complete-guide-for-marketers)
- **Length caps**:
  - YouTube Shorts can be up to **3 minutes** for uploads on/after **Oct 15, 2024**. — [Tubefilter](https://www.tubefilter.com/2024/10/03/youtube-shorts-three-minutes-max-length-redesign-trends-templates/amp/)
  - Instagram Reels up to **3 minutes** from Jan 2025 (Mosseri: "Starting today, you can upload Reels… up to three minutes long"). — [Social Media Today](https://www.socialmediatoday.com/news/instagram-officially-expands-reels-length-to-3-minutes/737766/); [Lindsey Gamble](https://www.lindseygamble.com/blog/instagram-three-minute-reels)
  - Later reports say Reels can run to 20 minutes, but those **over 3 minutes are not recommended to new audiences** (unverified against Instagram help pages). — [Photutorial](https://photutorial.com/instagram-reels-can-be-3-minutes-long-now)
- **TikTok monetization favors longer content**: Creator Rewards (launched Mar 2024) pays only on original videos **over 60 seconds**. Qualified views must come from the For You feed and last at least 5 s, and a video needs 1,000 qualified views before it earns. Creator-reported RPMs are about $0.40–$1.00 per 1,000 qualified views. **[PLATFORM launch + SECONDARY detail]** — [TikTok Newsroom (Mar 18, 2024)](https://newsroom.tiktok.com/introducing-the-new-creator-rewards-program); [Nuelink](https://blog.nuelink.com/tiktok-creator-rewards-program/); [ZDNet](https://www.zdnet.com.au/article/tiktok-rolls-out-new-creator-rewards-program-to-help-you-earn-more-money/)
- **YouTube Shorts view definition changed twice**:
  - From **Mar 31, 2025**, Shorts views count each start or replay with no minimum watch time.
  - From the **Aug 27, 2026** revision, YouTube "will align public view counting for all video formats: long-form videos, Live, and Shorts," counting a view when a video begins to play.

  **[PLATFORM, API docs]** — [YouTube Data API revision history](https://developers.google.com/youtube/v3/revision_history)
- Captions/on-screen text: peer-reviewed evidence (small sample) says text facilitates virality. **[PEER-REVIEWED, 2022]** — [Ling et al., ACM WebSci](https://dl.acm.org/doi/fullHtml/10.1145/3501247.3531551)
- Duration vs engagement: a negligible association in one longitudinal finfluencer dataset. **[PREPRINT]** — [arXiv 2607.05203](https://arxiv.org/pdf/2607.05203)
- Many blog hook statistics (the "3-second rule," "text hooks double retention") have no traceable primary source. **[assessment from search]** — [Virlo blog example](https://virlo.ai/blog/why-the-first-few-seconds-matter); [Creatify example](https://creatify.ai/blog/24-red-hot-scroll-stopping-hooks-to-increase-video-retention-on-tiktok)
- Engagement benchmarks (Socialinsider, **[VENDOR]**; 40.7M organic TikTok videos from 257K brand accounts):
  - Average engagement rate by views was **4.20% in 2025** (vs 3.85% in 2024).
  - Average views per post *fell* for accounts under 50K followers (1K–5K: 860 → 350) and rose 39% for 100K–1M accounts (25,198 → 34,900).
  - Posting frequency rose about 40% (e.g., 10K–50K accounts: 9 → 16 posts/month).

  Methodology notes are internally inconsistent (2025 data labeled 2026). — [Socialinsider TikTok benchmarks](https://www.socialinsider.io/blog/tiktok-stats/)

### Inferences
- Product implication: a hook-first template structure (a strong visual or text claim in seconds 0–2, payoff before about 6 s) is supported by TikTok's own ad research. Treat the organic case as extrapolation.
- Because views now count on play start (with replays counted on Shorts), "loop" engineering inflates Shorts view counts. A trend detector should rank on engagement-per-view, view velocity, or sends/shares rather than raw views, and must not compare Shorts views across the Mar 2025 and Aug 2026 definition changes.
- Socialinsider shows views concentrating in larger accounts and creators posting more often. That suggests rising competition per slot, consistent with a crowded faceless-autoposter market (vendor data, brand accounts only).
- Length strategy diverges by platform. TikTok pays only for 60s+ videos. Instagram reportedly limits >3-min Reels' reach. Shorts cap at 3 min. A template engine should output platform-specific lengths.

### Gaps
- No platform-published *organic* retention curves or "first 3 seconds" benchmarks from TikTok, Instagram, or YouTube. The best data is about ads.
- No platform-published or peer-reviewed evidence on loops, seamless replays, or caption styles (burned-in vs auto-captions).
- Couldn't verify the "Reels >3 min not recommended to non-followers" claim on an Instagram help page.
- YouTube's "viewed vs swiped away" Shorts metric is known to exist, but no aggregate benchmark was found.

---

## Q3. How fast do trend formats and sounds decay, and what is evergreen?

### Takeaway
The best dataset (Publicis × TikTok, six months of top-200 trending hashtags across 7 markets) shows **~48% of TikTok trends fade within 5 days and only ~27% survive past 14 days**. Utility/how-to trends last longest. Sound lifespans are usually cited as peaking within 1–3 weeks, but those figures come from blogs. AI-aesthetic trends like the POV-history wave lasted weeks. Template genres like Reddit-story/gameplay and life-hacks have persisted for years. A trend-detection feature therefore needs **daily** refresh to be useful, while a template library can refresh monthly or quarterly.

### Cited Findings
- Publicis Groupe × TikTok, "Globalisation of TikTok Trends": **26.7% of trends persist beyond 14 days**. The data covered TikTok's top 200 trending hashtags across Thailand, Indonesia, Vietnam, US, UK, Germany, and Japan, over six months, in 16 content categories, analyzed on Publicis's GrowthOS platform. **[PLATFORM-COMMISSIONED / industry; full white paper not located]** — [Campaign Asia](https://www.campaignasia.com/article/publicis-and-tiktok-crack-the-code-on-why-only-27-trends-survive-beyond-two-weeks/4bj3k6n8htrywyqvppeyk43j5r)
- Same study: **48% of TikTok trends fade within five days**. Trends last when creators "adopt, adapt and remix" them. **[industry summary]** — [Pulse.bot summary](https://www.pulse.bot/media/news/only-a-fraction-of-tiktok-trends-last-beyond-two-weeks-publicis-groupe-finds-7f651586-7dc4-4082-9a25-efea55509b06/); [Adobo Magazine](https://www.adobomagazine.com/?p=334821)
- Sound lifespans (blogs): most viral sounds peak within 7–14 days and leave the "priority pool" after about 30 days unless revived. Another blog says sound trends last 1–3 weeks. A claim that TikTok's own taxonomy says format/sound trends saturate within 3–5 days could not be traced to TikTok. **[VENDOR/ANECDOTE]** — [Alibaba product-insights blog](https://www.alibaba.com/product-insights/why-do-some-tiktok-sounds-become-viral-audio-trends-algorithm-breakdown.html); [Lirra](https://lirra.org/blog/how-long-do-tiktok-trends-last/); [SocialTrending](https://socialtrending.link/how-long-do-social-media-trends-last-benchmarks-by-platform-and-trend-type)
- Older academic baseline (YouTube trending videos, about 2014): viewership slows about **two weeks** after a video trends. **[ACADEMIC, older, YouTube not TikTok]** — [arXiv 1409.7733](https://arxiv.org/pdf/1409.7733)
- AI history POV trend: began late Jan 2025 and peaked Feb 2025, a lifespan of weeks. **[JOURNALISM, lower tier]** — [ComingSoon](https://comingsoon.net/?p=1924475)
- Evergreen example: 5-Minute Crafts (life hacks), about 28.59B cumulative views. **[SECONDARY]** — [Wikipedia](https://en.wikipedia.org/wiki/5-Minute_Crafts)
- Interface (formerly Stiftung Neue Verantwortung) published a study on how TikTok hashtags evolve over time. It wasn't read, but it is a lead for hashtag-decay data. — [Interface](https://www.interface-eu.org/publications/tiktok-algorithms-how-platforms-hashtags-evolve-over-time)

### Inferences
- Two-speed product: (1) an **evergreen template library** (utility/explainer, story, quiz, listicle) refreshed slowly; (2) a **trend radar** (sounds, meme templates, AI-aesthetic waves) that must surface signals within 1–3 days of emergence. With about half of trends dead in 5 days, a weekly-refresh radar would mostly show dead trends.
- For an autoposter, the lag between detection, template build, generation, and posting must be well under a week to catch trend formats. That favors parameterized "trend slots" (swap audio or caption pattern) over bespoke templates.
- The genre persistence of Reddit-story/gameplay and life-hacks is inferred from their continued presence and asset markets, not from measured time series.

### Gaps
- The Publicis/TikTok white paper itself (methodology, definition of "trend," decay curves) wasn't located. Only secondary summaries.
- No platform-published or peer-reviewed half-life data for TikTok *sounds* specifically, or for Reels/Shorts trends at all.
- No time-series data on how long faceless *genres* (as opposed to hashtags) stay effective.

---

## Q4. Are faceless/templated formats (e.g., Reddit-story gameplay) being saturated or demoted?

### Takeaway
Yes. In 2025–2026 all three platforms moved formally against unoriginal, templated, and mass-produced output. **YouTube** made "inauthentic"/"generic or repetitive" content (templated storylines, slideshows, scrolling text, mass-produced AI) and readings of others' material ineligible for monetization, and named AI slop a 2026 priority. **TikTok** makes unoriginal or reused material ineligible for the For You feed and added a user slider to see less AI content. **Instagram** replaces reposts with originals, and since April 2026 it has stopped recommending accounts whose output is mostly unoriginal. These rules target the *lack of added originality*, not faceless production as such. Faceless channels with real narration, commentary, or educational value remain explicitly allowed on YouTube.

### Cited Findings
**YouTube**
- On Jul 15, 2025, YouTube renamed "repetitious content" to **"inauthentic content."** The live policy page now uses the heading **"Generic or Repetitive Content"**:
  - definition: "content that looks like it's made with a template"
  - excluded: "Image slideshows, templated storylines, or scrolling text with minimal or no narrative, commentary, or educational value"
  - excluded: "AI-generated content made with generic or unoriginal templates giving the impression of mass production"

  **[PLATFORM]** — [YouTube channel monetization policies](https://support.google.com/youtube/answer/1311392)
- Reused content (a separate policy): excludes "Content that exclusively features readings of other materials you did not originally create," compilations, and "Content uploaded many times by other creators." It allows reuse with a "meaningful difference." **[PLATFORM]** — [same page](https://support.google.com/youtube/answer/1311392)
- YouTube called the July 2025 change a "minor update" and said mass-produced/repetitious content was never eligible to earn. Secondary coverage says it is not a ban on AI or faceless formats. **[PLATFORM via trade press]** — [Social Media Today](https://www.socialmediatoday.com/news/youtube-clarifies-monetization-update-inauthentic-repeated-content/752892/); [PPC Land](https://ppc.land/youtube-clarifies-inauthentic-content-policy-changes/)
- Unverified secondary reports (Jul 2026) say the policy was further split into "generic or repetitive," "unsatisfying or off-putting," and "AI personas on sensitive topics (finance/health/law)." The live page's "Generic or Repetitive Content" heading partially corroborates the rename. **[SECONDARY]** — [faceless.my](https://faceless.my/youtube/youtube-inauthentic-content-policy-faceless-ai-2026/); [ytzolo](https://ytzolo.com/blog/youtube-repetitive-content-policy-ai-slop-2026/)
- Neal Mohan's annual letter (Jan 21, 2026): reducing low-quality AI "slop" is a 2026 priority. YouTube will strengthen systems against spam, clickbait, and repetitive uploads, while expanding AI creation tools (e.g., Shorts using a creator's AI likeness). More than **1 million channels** used YouTube AI creation tools daily in Dec 2025, and Shorts average **200B daily views**. **[PLATFORM exec, via press]** — [Variety AU](https://au.variety.com/2026/digital/global/youtube-channels-using-ai-tools-reduce-slop-neal-mohan-letter-32190/); [eWeek](https://www.eweek.com/news/youtube-ai-slop-crackdown-creators/)
- YouTube reportedly deleted 16 channels mass-producing low-effort content, and enforcement is said to be shifting to channel-level detection. **[SECONDARY, unverified]** — [air.io](https://air.io/en/monetization/youtube-monetization-policy-changes-2026-a-complete-dated-timeline); [OutlierKit](https://alpha.outlierkit.com/resources/youtube-ai-slop-crackdown-2026/). Separately, 16 of Kapwing's top-100 AI-slop channels were found deleted or emptied. **[JOURNALISM]** — [Daily Dot](https://dailydot.com/youtube-ai-slop-study)

**TikTok**
- Community Guidelines: "Content is also ineligible for the FYF if it includes **unoriginal or reused material without anything new**." Creators must "label AI-generated or significantly edited content that shows realistic-looking scenes or people," and unlabeled content "may be removed, restricted, or labeled." **[PLATFORM]** — [TikTok Community Guidelines: Integrity & Authenticity](https://www.tiktok.com/community-guidelines/en/integrity-authenticity)
- Nov 2025: TikTok rolled out an **AI-generated content (AIGC) slider** in Manage Topics so users can see less AI content in For You. It reduces AI content but doesn't eliminate it. **[JOURNALISM]** — [TechCrunch](https://techcrunch.com/2025/11/18/tiktok-now-lets-you-choose-how-much-ai-generated-content-you-want-to-see/); [Engadget](https://www.engadget.com/social-media/tiktok-will-let-users-tone-down-the-amount-of-ai-content-in-their-feed-050100596.html)
- Creator Rewards requires original content over 1 minute and excludes Duets/Stitches/repurposed content. **[SECONDARY]** — [Nuelink](https://blog.nuelink.com/tiktok-creator-rewards-program/)

**Instagram**
- Since 2022, Instagram ranks originals above reposts. It replaces a reposted Reel with the original when it detects identical content and labels reposts with the original creator. Mosseri: "We build classifiers to predict how likely something is to be original, but that's not knowing." **[PLATFORM via press, 2022: older]** — [Engadget](https://www.engadget.com/instagrams-algorithm-overhaul-will-reward-original-content-and-penalize-aggregators-130018977.html); [Tubefilter](https://www.tubefilter.com/2022/04/21/instagram-adam-mosseri-algorithm-change-original-content/)
- Apr 2026: the originality policy was extended to photos and carousels. Accounts posting a majority of "unoriginal content" are no longer recommended to non-followers. Watermarks, minor crops, and borders don't count as original. **[JOURNALISM]** — [PetaPixel](https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/); [Digital Camera World](https://www.digitalcameraworld.com/tech/social-media/two-years-later-instagram-is-finally-giving-photographers-the-same-protection-as-videographers-with-this-key-change); [WebProNews](https://www.webpronews.com/instagrams-aggregator-purge-original-creators-gain-ground-as-repost-empires-crumble/)
- Reported thresholds conflict: "10+ unoriginal posts in 30 days → no recommendations" vs "fix the mix over 30 days and eligibility returns." **[SECONDARY]** — [House of Marketers](https://houseofmarketers.com/instagram-reels-algorithm-update-original-content/); [WebProNews](https://www.webpronews.com/instagrams-aggregator-purge-original-creators-gain-ground-as-repost-empires-crumble/)

**Saturation signals**
- Kapwing (Nov 2025): 21% of the first 500 Shorts served to a new account were AI-generated, and 33% were brainrot. **[VENDOR]** — [The Decoder](https://the-decoder.com/one-in-five-youtube-shorts-shown-to-new-users-is-ai-generated-slop-study-finds/)
- There is a proliferation of fake-text / Reddit-story generators ([MakeViral](https://www.makeviral.ai/tools/fake-text-message-video-generator), [Brainrot Shorts](https://www.brainrotshorts.com/texting-story-maker), [Flickify](https://www.flickifyai.com/tools/fake-text-video-generator), [ClipGoat](https://www.clipgoat.com/tools/free-fake-text-message-videos-online-generator)) and of commoditized gameplay background packs ([Gumroad](https://howtoai.gumroad.com/l/freetiktokassets)). **[VENDOR/ANECDOTE]**

### Inferences
- The specific product the founder describes (an autoposter of templated faceless videos) is the archetype these policies target. To stay viable it should build in "added value" levers: original scripts rather than read-alouds of scraped posts, real narration and commentary, per-video variation, AI-content labeling, and avoidance of identical background assets across users.
- The biggest single risk is **YouTube Partner Program demonetization at the channel level**, since the policy evaluates a channel's overall look of mass production. A second risk is **Instagram non-recommendation** for mostly-unoriginal accounts. A SaaS whose users' channels get demonetized will churn.
- Reddit-story formats carry three compounding risks: a YouTube monetization exclusion, copyright in the underlying posts, and Reddit's March 2027 public-API closure, which eliminates an easy source pipeline.
- Faceless *per se* is not penalized. Explainer, education, and original-story faceless content is explicitly protected by YouTube's "narrative, commentary, or educational value" carve-out.

### Gaps
- No platform has published data quantifying the reach or demonetization impact on specific templated genres (e.g., % of Reddit-story channels demonetized).
- Couldn't confirm the July 2026 YouTube three-category split from a primary YouTube announcement.
- No evidence found on whether TikTok algorithmically down-ranks TTS voice or stock gameplay specifically, as opposed to unoriginality in general.

---

## Q5. What is the minimum legitimate data pipeline for detecting rising formats across TikTok, Reels, and Shorts, and what does it cost per month?

### Takeaway
There is **no official, commercially usable API for discovering trends on TikTok**:
- The Research API is restricted to academics and non-profits and must be non-commercial.
- The Commercial Content API covers EU/EEA ads only.
- Creative Center has no documented data API, and TikTok's terms bar automated collection.

Instagram's Graph API allows limited official discovery: 30 hashtags per account per 7 days, plus Business Discovery on known business/creator accounts. YouTube's Data API is free and official, but since July 2025 its "mostPopular" chart only covers Music, Movies, and Gaming. A realistic pipeline therefore combines **official YouTube + Instagram APIs (free)** with a **third-party TikTok (and probably Reels) data vendor**. My estimate is roughly **$50–$300/month at seed scale on per-request APIs**, or **$500–$2,000+/month on per-record pricing at broader coverage**.

### Cited Findings
**TikTok official**
- Research API eligibility (primary page):
  - academic institutions in "the U.S., EEA, UK, Canada, or Switzerland"
  - EU not-for-profit/independent research bodies
  - Brazilian academic and non-profit groups studying youth safety

  Applicants must "be independent of commercial interests" and research "on a not-for-profit or non-commercial basis." **[PLATFORM]** — [TikTok for Developers: Research API](https://developers.tiktok.com/products/research-api/)
- The Research API is free. Reported limits are 1,000 requests and 100,000 records per day, with about a 4-week review. Using research credentials commercially risks losing access. **[SECONDARY]** — [ApiDojo](https://apidojo.io/blog/tiktok-api/research-api/); [TokConnect](https://tokconnect.com/guides/tiktok-research-api/)
- Commercial Content API: a DSA-driven ad library for ads shown in the EU/EEA (reportedly plus UK, Switzerland, Türkiye). The US is excluded. TikTok describes it as for "the public and researchers," with an approved application required. **[PLATFORM + SECONDARY]** — [TikTok Commercial Content API](https://developers.tiktok.com/products/commercial-content-api); [DEV guide](https://dev.to/odeeb/the-tiktok-ad-library-api-a-developers-honest-guide-to-the-dsa-commercial-content-library-5446)
- TikTok One Creator Commercial Terms prohibit using "automated scripts to collect information" from its commercial products' dashboards/APIs. Whether this covers Creative Center specifically is unconfirmed. TikTok's main ToS contains a prohibition on scraping/data extraction. **[PLATFORM terms; partly via snippet]** — [TikTok One Creator Commercial Terms](https://ads.tiktok.com/help/article/tiktok-one-creative-suite-creator-commercial-terms?lang=en); [ConductAtlas summary of TikTok ToS](https://conductatlas.com/platform/tiktok/tiktok-terms-of-service/prohibition-on-scraping-and-data-extraction/)

**Instagram official (Graph API)**
- Hashtag Search allows a maximum of **30 unique hashtags per Business/Creator account in a rolling 7-day window**. Repeat queries on the same hashtag don't count again. It requires App Review for "Instagram Public Content Access," doesn't support Stories hashtags, and you can't comment on discovered media. **[PLATFORM]** — [Meta Hashtag Search docs](https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-facebook-login/hashtag-search)
- Business Discovery returns other **business/creator** accounts' media with `like_count`, `comments_count`, and (not always) `view_count`. **[PLATFORM]** — [Meta Business Discovery docs](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/business-discovery?locale=zh_CN)
- The Business Discovery rate limit is commonly cited as about 200 calls/user/hour (about 5,000 media items/hour at 25 per page). Other sources say it scales as 200 × the app's daily active users. **[SECONDARY, conflicting]** — [Phyllo](https://www.getphyllo.com/post/instagram-api-rate-limits-explained-and-how-to-scale-beyond-them-2026); [Bundle.social](https://bundle.social/blog/instagram-api-rate-limits); [Mixpeek](https://mixpeek.com/docs/integrations/social-media/instagram)

**YouTube official (Data API v3)**
- From **Jul 21, 2025**, "the `mostPopular` chart will feature videos from the Trending Music, Movies, and Gaming charts," alongside the deprecation of YouTube's Trending page. **[PLATFORM]** — [YouTube Data API revision history](https://developers.google.com/youtube/v3/revision_history)
- YouTube retired the Trending page because visits "decreased significantly, especially over the last five years." It was replaced with category charts. **[PLATFORM via press]** — [9to5Google](https://9to5google.com/2025/07/10/youtube-trending-page-removal/); [Android Central](https://www.androidcentral.com/apps-software/youtube/youtube-replacing-trending-tab-with-new-category-specific-charts)
- Quota changes **[PLATFORM]** — [revision history](https://developers.google.com/youtube/v3/revision_history):
  - **Jun 1, 2026**: `search.list` and `videos.insert` moved to their own quota buckets.
  - **Jun 3, 2026**: a new `videos.batchGetStats` method costs 1 unit, in its own bucket with a 10,000 units/day default.
  - **Dec 4, 2025**: video upload cost dropped from about 1,600 to about 100 units, which matters for autoposting.

**Third-party providers (pricing as listed; verify before budgeting)**
- **Apify (Clockworks actors)** **[VENDOR pricing pages]**:
  - TikTok Video Scraper: **$10 / 1,000 videos** — [Apify](https://apify.com/clockworks/tiktok-video-scraper/pricing)
  - TikTok Data Extractor: $5 / 1,000 results base ($2 at the Gold tier) — [Apify](https://apify.com/clockworks/free-tiktok-scraper/pricing)
  - TikTok Profile Scraper: from $2.50 / 1,000 — [Apify](https://apify.com/clockworks/tiktok-profile-scraper/pricing)
  - Third-party comparisons list the main Clockworks TikTok Scraper at **$1.70 / 1,000** pay-per-event, with comments at +$0.50/1K and transcripts at $27/1K. — [SocialCrawl](https://www.socialcrawl.dev/blog/best-tiktok-data-apis-2026); [use-apify](https://use-apify.com/docs/best-apify-actors/best-tiktok-scrapers)
- **ScrapeCreators** **[VENDOR]**:
  - Prepaid credits that never expire, billed 1 credit per request on most TikTok endpoints. Some endpoints cost more (e.g., audience: 26 credits).
  - **$47 for 25,000 credits** (about $1.88/1K); about **$497 for 500,000** ($0.99/1K); 100 free credits.
  - Cache hits are free.

  — [ScrapeCreators blog](https://scrapecreators.com/blog/pay-as-you-go-social-media-scraping-api); [ScrapeCreators caching](https://scrapecreators.com/blog/api-caching-free-cache-hits); [SocialCrawl comparison](https://www.socialcrawl.dev/blog/best-tiktok-data-apis-2026)
- **EnsembleData** **[VENDOR, via comparison sites]**: monthly unit plans with hard daily caps. Free is 50 units/day. Paid tiers run from "Wood" at **$100/mo** to "Platinum" at **$1,400/mo** (50K units/day). — [SocialCrawl](https://www.socialcrawl.dev/blog/best-tiktok-data-apis-2026); [Apify EnsembleData actor](https://apify.com/ensembledata/tiktok-api/pricing)
- **Bright Data** **[VENDOR, via comparison sites]**:
  - Web Scraper API at **$1.50 / 1,000 records** pay-as-you-go; free tier of 5,000 records/month.
  - "Scale" plan about **$499/mo for ~384K records**, with overage at $1.30/1K.
  - Pre-collected datasets about $2.50/1K.
  - Promotional rates of $0.75–$1.00/1K have been reported.

  — [UsagePricing](https://usagepricing.com/blueprint/bright-data); [Costbench](https://costbench.com/software/web-scraping/bright-data/); [Firecrawl blog](https://www.firecrawl.dev/blog/bright-data-pricing)
- Several comparison articles are written by competing API vendors (SocialCrawl, Xpoz, ScrapeCreators, Phyllo), so figures may be selectively framed. **[assessment]** — [Xpoz](https://www.xpoz.ai/blog/guides/tiktok-api-pricing-2026/); [SocialCrawl](https://www.socialcrawl.dev/blog/best-tiktok-data-apis-2026)

### Inferences
- **Minimum legitimate pipeline** (my design inference):
  1. **YouTube Shorts**: use the official Data API (free; 10K units/day default, separate search bucket since Jun 2026). Track a seed list of channels in the target niches via `videos.batchGetStats`/`videos.list` and compute view and engagement velocity. Don't rely on `mostPopular`, which is now Music/Movies/Gaming only.
  2. **Instagram Reels**: use the official Graph API (free). Run Business Discovery on a curated list of a few hundred creator/business accounts, plus up to 30 hashtags/week per connected IG account. Coverage is thin, with no audio-trend or Explore data, so it may need a vendor supplement.
  3. **TikTok**: there is no commercial official path, so use a third-party vendor that collects **logged-off public** data (see Q6 for the legal reasoning). Pull seed accounts, hashtag feeds, and sound/music pages daily.
  4. **Detection layer**: per-video velocity (views/hour relative to the account's baseline, i.e., "outliers"), clustering by sound ID, caption pattern, and visual template (via embeddings) to find *formats* rather than single videos, plus cross-platform confirmation.
- **Cost model** (illustrative; my own arithmetic on the vendor prices above):
  - Seed scale: 500 TikTok feed requests/day × 30 days = 15K requests/month. On ScrapeCreators per-request pricing that is about **$28–$47/mo**. Pulling the same ~450K video records/month on per-record pricing costs about **$675** (Bright Data $1.50/1K), **$765** (Apify $1.70/1K), up to **$4,500** (Apify Video Scraper $10/1K).
  - EnsembleData's daily-capped plans fall in the **$100–$1,400/mo** band.
  - Adding Reels via a vendor roughly doubles the third-party line. YouTube and the official Instagram API are free beyond engineering and hosting.
  - So the realistic range is **~$50–$300/mo** for an MVP radar, and **$500–$2,000+/mo** for broad multi-platform coverage.
- **Commercial-terms exposure**: the cheapest path (vendor TikTok data) is legally "gray but defensible" for logged-off public metadata. The founder should avoid reselling or rehosting the videos themselves and avoid logged-in scraping.
- Since TikTok's own Creative Center is the obvious free trend source, scraping it is the tempting shortcut. The TikTok One commercial terms language against automated collection makes that riskier than scraping logged-off public pages.

### Gaps
- `search.list` quota cost (believed to be 100 units/call) and the current default for the new search bucket weren't re-verified in this session.
- Couldn't locate Creative Center–specific terms of use, or confirm whether Creative Center content (trending hashtags/sounds/creators) may be reused commercially.
- No official Instagram API exposes trending audio, Reels Explore, or non-business (personal) accounts. I couldn't confirm whether Meta's Content Library (research-only) has any commercial path.
- Vendor prices change frequently, and many figures came from competitor comparison sites rather than the vendors' own pricing pages (except Apify).

---

## Q6. What is the US legal status of scraping public social data, and how do platform ToS interact with it?

### Takeaway
US case law favors scraping **publicly accessible, logged-off** data, but it doesn't immunize it:
- **hiQ v. LinkedIn**: scraping public pages is likely not "unauthorized access" under the CFAA. But the court later held anti-scraping terms enforceable in contract, and hiQ ended under a $500K consent judgment and injunction.
- **Meta v. Bright Data** (2024): logged-off scraping isn't "use" governed by Meta's terms.
- **X v. Bright Data** (2024): X's contract claims were preempted by copyright law, but access/server-impairment claims were allowed to proceed.

Practical rule: **no logged-in scraping, no fake accounts, no server strain, and no republishing copyrighted content.**

### Cited Findings
- **hiQ v. LinkedIn** **[COURT/LAW-FIRM]**:
  - The Ninth Circuit's April 2022 order resolved the CFAA question in hiQ's favor for public data.
  - On **Nov 4, 2022**, the district court held that user-agreement provisions banning scraping and fake profiles are enforceable as a breach-of-contract claim, and found hiQ breached them.
  - In **Dec 2022**, a consent judgment entered **$500,000** against hiQ with a permanent injunction: stop scraping, and destroy the code, data, and algorithms derived from scraped data. hiQ also stipulated liability for trespass to chattels and misappropriation. The stipulation has no precedential value.

  — [Morgan Lewis](https://www.morganlewis.com/blogs/sourcingatmorganlewis/2022/12/linkedin-v-hiq-landmark-data-scraping-suit-provides-guidance-to-data-scrapers-and-web-operators); [ZwillGen](https://www.zwillgen.com/alternative-data/hiq-v-linkedin-wrapped-up-web-scraping-lessons-learned/); [Proskauer](https://newmedialaw.proskauer.com/2022/12/08/hiq-and-linkedin-reach-proposed-settlement-in-landmark-scraping-case/)
- **Meta v. Bright Data** (N.D. Cal., Judge Edward Chen, Jan 2024 summary judgment for Bright Data) **[COURT/LAW-FIRM]**:
  - "Bright Data did not 'use' Facebook and Instagram when it engaged in public logged-off scraping."
  - Meta could not bind Bright Data after its accounts were terminated.
  - The ruling is narrow: Meta's terms only, and it doesn't address scraping behind a login.
  - Meta dropped its remaining claims in Feb 2024.

  — [Quinn Emanuel](https://www.quinnemanuel.com/the-firm/news-events/client-alert-what-does-the-meta-v-bright-data-summary-judgment-ruling-mean-for-web-scraping/); [Farella Braun + Martel](https://www.fbm.com/publications/major-decision-affects-law-of-scraping-and-online-data-collection-meta-platforms-v-bright-data/); [Zyte](https://www.zyte.com/blog/california-court-meta-ruling/)
- **X Corp. v. Bright Data** (N.D. Cal. No. C 23-03698 WHA, Judge Alsup) **[COURT/LAW-FIRM]**:
  - On **May 9, 2024**, X's claims that scraping and selling public X data violated its terms were dismissed as **preempted by the Copyright Act** (conflict preemption). X holds only a non-exclusive license to user content. Trespass-to-chattels, unfair-competition, and tortious-interference claims were also dismissed.
  - In **Nov 2024**, Alsup allowed a second amended complaint limited to claims over Bright Data's **access** (server impairment), and refused to revive claims over misappropriating users' posts.
  - No Ninth Circuit outcome was found.

  — [Courthouse News](https://www.courthousenews.com/judge-tosses-xs-contract-claims-against-data-scraping-company/); [Frankfurt Kurnit](https://technologylaw.fkks.com/post/102j7s5/blockbuster-ruling-federal-court-holds-that-copyright-act-preempts-xs-web-scrap); [MediaPost](https://www.mediapost.com/publications/article/401510/judge-allows-x-corp-to-revive-scraping-battle-wit.html); [Skadden via CLS Blue Sky](https://clsbluesky.law.columbia.edu/?p=60360)
- TikTok's ToS contains a high-severity prohibition on automated scraping of platform data, and a separate provision barring commercial use of other users' content without permission. **[SECONDARY summary of platform terms]** — [ConductAtlas: scraping](https://conductatlas.com/platform/tiktok/tiktok-terms-of-service/provision/CA-P-018595/prohibition-on-automated-scraping-of-platform-data/); [ConductAtlas: commercial use of content](https://conductatlas.com/platform/tiktok/tiktok-terms-of-service/prohibition-on-unauthorized-commercial-use-of-content/)
- Reddit (relevant to Reddit-story sourcing): user content remains owned by users, commercial API use needs a negotiated agreement, and public API access closes March 2027. **[SECONDARY/JOURNALISM]** — [Activepieces](https://www.activepieces.com/blog/reddit-api-access-in-2026-how-to-get-started); [PPC Land](https://ppc.land/reddit-to-halt-public-data-api-access-in-march-2027-as-14-000-apps-register/)

### Inferences
- Lowest-risk posture for the SaaS:
  1. Buy logged-off public **metadata** (counts, captions, sound IDs, timestamps) from vendors rather than running in-house logged-in scrapers.
  2. Don't create accounts on the platforms to scrape, which triggers the hiQ-style contract exposure.
  3. Respect rate limits to avoid trespass/server-impairment theories (the surviving X v. Bright Data claim).
  4. Never redistribute the videos or Reddit posts themselves. Copyright in content is separate from data-access law.
- The case law is all N.D. Cal. or Ninth Circuit, and mostly district-level. TikTok's ToS hasn't been tested like Meta's, so "logged-off isn't use" may not transfer to TikTok's wording.
- Using the vendor's data for *format detection* (analytics) is meaningfully lower risk than *generating videos from scraped third-party stories* (e.g., Reddit posts), which raises copyright issues independent of scraping law.

### Gaps
- No case found specifically involving TikTok scraping in US courts.
- No confirmation of any Ninth Circuit appeal in X v. Bright Data or Meta v. Bright Data.
- Not legal advice. The founder should get counsel on TikTok's current ToS and any vendor's indemnities.

---

## Q7. How do existing trend tools appear to source their data?

### Takeaway
Most trend tools **don't disclose** their data sources. Where sourcing is visible, it falls into three patterns: (a) platform partnership or co-authorship (Publicis's GrowthOS analysis with TikTok; Trendpop's owner Collab is an official TikTok partner); (b) third-party scraping marketplaces (Apify actors, including unofficial scrapers of TikTok's ad library); (c) manual panel or fresh-account sampling (Kapwing's AI-slop study).

### Cited Findings
- **Publicis Groupe** ran its TikTok trend-longevity analysis on its own GrowthOS platform, using TikTok's top-200 trending hashtag data in a white paper co-produced *with TikTok*. This was a partnership, not scraping. **[industry]** — [Campaign Asia](https://www.campaignasia.com/article/publicis-and-tiktok-crack-the-code-on-why-only-27-trends-survive-beyond-two-weeks/4bj3k6n8htrywyqvppeyk43j5r)
- **Trendpop** (YC W21, founded 2020) is a short-form analytics/trend platform for TikTok, Instagram, and YouTube, used heavily by record labels. It was acquired by **Collab** (an official TikTok creative/marketing partner) in **Jan 2022**. Its data-collection method is not disclosed. **[JOURNALISM/aggregator]** — [YC profile](https://www.ycombinator.com/companies/trendpop); [SoCalTech](https://socaltech.com/collab_acquires_trendpop/s-0082197.html); [Mobile Marketing Magazine](https://mobilemarketingmagazine.com/?p=115650)
- **Apify marketplace**: multiple third-party actors claim to pull TikTok's Commercial Content (ad library) data *without* TikTok API approval, alongside general TikTok/Instagram scrapers. This is evidence of a mature unofficial-data supply chain. **[VENDOR]** — [Apify: TikTok Ads Library Scraper](https://apify.com/bovi/tiktok-ads-library-scraper); [Apify: TikTok Ad Library Pro](https://apify.com/constructive_calm/tiktok-ad-library-pro)
- **Kapwing**'s AI-slop study used manual review of top-100 trending channels per country, plus a fresh-account sample of the first 500 Shorts. That is panel/sampling methodology rather than API access. **[VENDOR]** — [The Decoder](https://the-decoder.com/one-in-five-youtube-shorts-shown-to-new-users-is-ai-generated-slop-study-finds/)
- **ViralMoment** (social video trend intelligence) raised a **$2.5M seed** in Jan 2024. Its data source isn't disclosed in the material found. **[aggregator]** — [FounderLodge](https://www.founderlodge.com/round/ViralMoment-raises-2500000-Seed-2024-01-26-Chelsie-Hall-MTc2OTA)
- Data API vendors (Phyllo, ScrapeCreators, EnsembleData, SocialCrawl, Xpoz) market themselves as the backend for creator and trend tools, which implies many tools resell scraped public data under the hood. **[VENDOR]** — [Phyllo](https://www.getphyllo.com/post/tiktok-api-rate-limits-in-2026-quotas-errors-workarounds); [Xpoz](https://www.xpoz.ai/blog/guides/tiktok-research-api-limits-access-and-alternatives/)

### Inferences
- A solo founder can't realistically get a TikTok data partnership early. The practical model is the same one most smaller tools use: a public-data vendor API plus the official YouTube/Instagram APIs. Defensibility then comes from the **format-clustering layer** (identifying reusable *formats* from raw videos), not from exclusive data.
- Trend tools that sit with official partners (Collab/Trendpop, agency platforms like Publicis GrowthOS) have privileged access a SaaS clone can't match. Competing on "freshest TikTok trends" is a weak position, while competing on "format templates that are policy-safe and proven durable" is stronger.

### Gaps
- No public disclosure found of the data sources for consumer-facing trend tools (e.g., Exploding Topics, TrendTok-style apps, vidIQ's Instagram/TikTok "outlier" search, or the AI faceless-video tools StoryShort/AutoShorts). Competitor researchers may surface this from their docs or ToS.
- Couldn't determine whether TikTok's Marketing Partner program grants partners trend-data API access beyond Creative Center.
