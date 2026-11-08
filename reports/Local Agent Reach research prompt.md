# Run the Reddit / X demand research on your own computer

The cloud session can't reach Reddit, X or YouTube transcripts. Those need a logged-in browser, and the cloud container has none. On your own computer, Agent Reach can use your browser's login, so Claude Code there can collect the first-hand owner complaints that every report so far is missing.

## 1. One-time setup (macOS or Linux, about 10 minutes)

1. Get the reports onto your machine. In your local `fullcarts-app` clone:
   ```bash
   git fetch origin research/niche-incumbent-check
   git checkout research/niche-incumbent-check
   ```
   The reports are in `reports/` and the notes in `research_notes/`.
2. Install Agent Reach. Use only the GitHub release; the PyPI package with the same name is a different project.
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh      # only if `uv --version` fails
   uv tool install https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip
   agent-reach setup
   agent-reach add reddit
   agent-reach add twitter      # optional, and experimental
   ```
3. Logins: Agent Reach first tries to reuse your Chrome login for each site. Its own README recommends a **secondary account**, because platforms can restrict accounts used for automated access. To use a different account, run `agent-reach login reddit` (or `twitter`) and sign in yourself in the window it opens. Never paste passwords or API keys into the chat.
4. Check it works: `agent-reach check reddit` and `agent-reach check youtube`.

Agent Reach is read-only: it never posts, comments, likes or sends messages. Keep the volume modest: the prompt below caps it at about 40 searches per niche.

## 2. Paste this into Claude Code (started inside `fullcarts-app`)

```text
Use the agent-reach skill to collect first-hand demand evidence for the SaaS opportunities in
reports/Expanded niche SaaS clone opportunities.md, and to discover new ones. Read that report's master
table and its "Validate eight candidates" table first. If reports/YouTube founder SaaS mining.md exists,
read it too.

Rules: read-only; space requests a few seconds apart; at most ~40 searches per niche; stop on any rate
limit or bot check instead of retrying; quote posts verbatim with their date and link; never post,
comment or message anyone.

Part A — validate the eight first picks (fire & life-safety inspection for small shops, lawn and tree-shrub
chemical programs, independent kennels and dog daycares, commercial janitorial, septic / grease-trap /
portable sanitation, craft-fair and market vendor applications, chamber-of-commerce software, and
turnover cleaning for short-term rentals). For each niche:
  1. Reddit: search for the incumbents by name (e.g. RealGreen, Service Autopilot, Gingr, PetExec, Swept,
     ServiceCore, Inspect Point, Eventeny, ZAPP, GrowthZone, ChamberMaster, Turno, Breezeway), plus
     "<niche> software", "what do you use for", "switching from", "price increase" and "hate". Use
     relevant subreddits such as r/sweatystartup, r/smallbusiness, r/lawncare, r/doggrooming,
     r/AirBnBHosts, r/vrbo, r/farmersmarket, r/EntrepreneurRideAlong and any trade subreddit you find.
     Collect 10–20 relevant threads per niche.
  2. X: search "<incumbent> price", "<incumbent> support" and "<niche> software" for recent complaints
     or switching intent.
  3. YouTube: read the transcripts of the 3–5 most relevant owner or software videos per niche, and note
     what owners say about software cost, pain and switching.
  4. Summarise: count the threads showing pain, switching intent or willingness to pay; give the 5 best
     quotes; name any competitor the report missed; and give an updated verdict (GO / CONDITIONAL / KILL)
     with reasons.

Part B — discover new opportunities. On r/sweatystartup, r/smallbusiness, r/Entrepreneur, r/SaaS,
r/microsaas and trade subreddits, search phrases such as "is there an app for", "is there software
that", "I'd pay for", "looking for software", "what CRM do you use" and "spreadsheet for". Group the
results into recurring jobs (at least 3 independent posts each), check whether a modern well-rated tool
already does each job (App Store, Capterra), and list the 10 strongest unmet or poorly met jobs with
evidence.

Part C — founder transcripts. For the 15 highest-revenue niche SaaS founders in the YouTube mining
report (Starter Story and other channels), read the transcripts and extract: the acquisition channel,
pricing, time to first customer, churn comments and what they would do differently.

Write everything to reports/Reddit and X demand validation.md, with a summary table at the top. Every
quote needs a date and a link.
```

## 3. What to bring back

Commit and push `reports/Reddit and X demand validation.md` to the `research/niche-incumbent-check` branch, or paste the summary table into the cloud session. I'll fold it into the ranked list and update the go/no-go verdicts.
