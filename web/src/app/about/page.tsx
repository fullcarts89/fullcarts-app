import SiteNav from "@/components/SiteNav";
import styles from "./styles.module.css";

export const metadata = {
  title: "About · FullCarts",
  description:
    "FullCarts is a public database of shrinkflation events. Our mission is to name the shrinkers, cite the evidence, and make consumer-product downsizing impossible to hide. Methodology, sources, and how to submit a tip.",
};

// All public data sources we pull from, in source-type order. Each
// gets a card explaining what we use it for and where it sits in the
// flow. Hardcoded because this is a static content page — the sources
// only change with code, not with data.
const SOURCES: Array<{
  name: string;
  tag: string;
  desc: string;
  href: string;
}> = [
  {
    name: "Reddit",
    tag: "Community evidence",
    desc:
      "r/shrinkflation, r/CasualUK, r/UnitedKingdom and similar subs. User-submitted photos of old vs new packaging are some of the strongest evidence we have — every claim we extract from a Reddit post points back to the original post with the image archived to our storage so the proof survives even if the post is later removed.",
    href: "https://www.reddit.com/r/shrinkflation/",
  },
  {
    name: "Google News + GDELT",
    tag: "News coverage",
    desc:
      "We crawl Google News RSS and the GDELT v2 Document API for every article mentioning shrinkflation, package downsizing, or related terms. News outlets often cite specific products and quote brand responses, which lets us cross-check Reddit evidence against journalist reporting.",
    href: "https://api.gdeltproject.org/api/v2/doc/doc",
  },
  {
    name: "Open Food Facts",
    tag: "Product catalog",
    desc:
      "A crowdsourced product database with photos, package weights, and ingredients for over 3 million products. We use it to discover products we don't yet track, to verify package sizes against an independent source, and to surface historical size observations.",
    href: "https://world.openfoodfacts.org/",
  },
  {
    name: "Kroger + Walmart APIs",
    tag: "Retailer-direct",
    desc:
      "Weekly polls of Kroger's product API and Walmart's open store API give us real-time package sizes and per-unit prices for every UPC we have an active variant for. This is how we catch shrinks the moment a new bag hits the shelf.",
    href: "https://developer.kroger.com/",
  },
  {
    name: "USDA FoodData Central",
    tag: "Skimpflation",
    desc:
      "USDA publishes a quarterly database of branded-food nutrition labels. We compare each quarter's release against earlier ones to spot products whose recipe changed — less protein, more added sugar, swapped fats. That's skimpflation: a smaller package is the obvious shrink; a worse recipe is the quiet one.",
    href: "https://fdc.nal.usda.gov/",
  },
  {
    name: "BLS R-CPI-SC",
    tag: "Government-grade",
    desc:
      "The Bureau of Labor Statistics' Research CPI excluding product Size Changes (R-CPI-SC) is the only official US measure of shrinkflation. BLS counts how many CPI-tracked items shrank between quarterly surveys — we plot it alongside our own count so you can see whether our catch list moves with the government's.",
    href: "https://www.bls.gov/cpi/research-series/r-cpi-sc.htm",
  },
  {
    name: "FRED · Food CPI",
    tag: "Macro context",
    desc:
      "The St. Louis Fed's FRED API gives us the official Food-at-Home CPI series. We surface it as the third line on the /insights chart so the shrinkflation count is always read against the inflation backdrop. If food prices are flat but shrinks are accelerating, the story is different than if both are rising in lockstep.",
    href: "https://fred.stlouisfed.org/series/CPIUFDNS",
  },
  {
    name: "Wayback Machine",
    tag: "SKU history",
    desc:
      "When a Reddit post mentions a specific product page, we hit the Internet Archive's CDX API to pull historical snapshots of that page. That gives us a defensible before/after for size and price even when the retailer has since updated the listing.",
    href: "https://web.archive.org/",
  },
];

// Methodology steps: the path a claim takes from raw source to
// public-facing event. Numbered because the order matters.
const STEPS: Array<{ n: string; title: string; body: string }> = [
  {
    n: "01",
    title: "Ingest",
    body:
      "Daily scrapers pull from Reddit, news, retailer APIs, and OFF. Every fetch lands in raw_items as immutable evidence — no edits, no overwrites. If the source ever takes its post or article down, we still have the canonical payload.",
  },
  {
    n: "02",
    title: "Extract",
    body:
      "Claude Haiku reads each new raw_item and extracts structured claims: brand, product name, before size, after size, observed date, change description, confidence sub-scores. Image-only Reddit posts get a vision pass.",
  },
  {
    n: "03",
    title: "Auto-decline",
    body:
      "Junk gets discarded daily — text-only Reddit complaints with no image, news rows with no brand or no measurable size change, off-catalog OFF rows that aren't shrinkflation. Keeps the review queue clean.",
  },
  {
    n: "04",
    title: "Auto-approve",
    body:
      "Claims that pass strict filters (image required, CPG-unit allowlist, overall confidence ≥ 90, sub-score floors) flow through without manual review. Everything else lands in the pending queue for a human.",
  },
  {
    n: "05",
    title: "Promote",
    body:
      "Approved claims are matched to a canonical product_entity (or create one), produce a pack_variant (UPC-keyed), generate before/after variant_observations, and publish a published_changes row with the full evidence trail.",
  },
  {
    n: "06",
    title: "Dedupe",
    body:
      "Syndicated news coverage of the same event collapses into a single published_changes row keyed on (entity, before size, after size). The contributing sources stack into evidence_count + the public source list you see on each event.",
  },
];

export default function AboutPage() {
  return (
    <>
      <SiteNav />
      <div className={styles.container}>
        <header className={styles.hero}>
          <div className={styles["hero-eyebrow"]}>About FullCarts</div>
          <h1>
            Name the shrinkers.{" "}
            <span className={styles.red}>Cite the evidence.</span>
          </h1>
          <p className={styles["hero-lede"]}>
            FullCarts is a public, evidence-based record of consumer-product
            shrinkflation. Every event we publish ties back to a verifiable
            source — a Reddit post, a news article, a retailer API response, a
            USDA record — with the original payload archived so the proof
            survives even when the source disappears.
          </p>
        </header>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>What we count</h2>
          </div>
          <p className={styles["section-lede"]}>
            We publish a <strong>shrinkflation event</strong> when we have
            evidence that a specific product&apos;s package shrank without a
            corresponding price drop. We also track <strong>restorations</strong>
            {" "}
            (when a product&apos;s size is increased back) and{" "}
            <strong>skimpflation</strong> (when the recipe quietly gets cheaper —
            less protein, more filler, swapped fats). Every event has at
            minimum a brand, product name, before/after size with units, an
            observed date, and at least one source URL.
          </p>
          <div className={styles["count-grid"]}>
            <div className={styles["count-card"]}>
              <div className={styles["count-eyebrow"]}>Counted</div>
              <ul>
                <li>Package size reductions (oz, g, ml, count)</li>
                <li>Recipe changes from USDA cross-release diffs</li>
                <li>Stretchflation — bag inflation hiding less product</li>
                <li>Restorations and upsizings</li>
              </ul>
            </div>
            <div className={styles["count-card"]}>
              <div className={styles["count-eyebrow"]}>Not counted</div>
              <ul>
                <li>Anecdotal complaints with no measurable size delta</li>
                <li>Pricing changes alone (no size change documented)</li>
                <li>Promotional sizes (limited-time bigger packs)</li>
                <li>Single-source claims without an image or article</li>
              </ul>
            </div>
          </div>
        </section>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Methodology</h2>
            <div className={styles.meta}>From raw source to public event</div>
          </div>
          <p className={styles["section-lede"]}>
            Six steps, all automated and audited. Every published event can
            be traced back to the exact raw payload it was extracted from.
          </p>
          <div className={styles["steps-list"]}>
            {STEPS.map((s) => (
              <div key={s.n} className={styles["step-row"]}>
                <div className={styles["step-num"]}>{s.n}</div>
                <div>
                  <div className={styles["step-title"]}>{s.title}</div>
                  <div className={styles["step-body"]}>{s.body}</div>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Where the data comes from</h2>
            <div className={styles.meta}>{SOURCES.length} active sources</div>
          </div>
          <p className={styles["section-lede"]}>
            Every claim is grounded in at least one of these. Cross-referencing
            across multiple sources is how we tell a real event from a one-off
            anecdote.
          </p>
          <div className={styles["sources-grid"]}>
            {SOURCES.map((s) => (
              <a
                key={s.name}
                className={styles["source-card"]}
                href={s.href}
                target="_blank"
                rel="noopener noreferrer"
              >
                <div className={styles["source-tag"]}>{s.tag}</div>
                <div className={styles["source-name"]}>{s.name}</div>
                <div className={styles["source-desc"]}>{s.desc}</div>
                <div className={styles["source-link"]}>Visit ↗</div>
              </a>
            ))}
          </div>
        </section>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Submit a tip</h2>
          </div>
          <p className={styles["section-lede"]}>
            Spotted a shrinkflation event in the wild? Send us the details and
            we&apos;ll add it to the review queue. A photo with the old and new
            package side-by-side, or a comparison against an archived listing,
            is the strongest evidence we can review.
          </p>
          <div className={styles["tip-card"]}>
            <div className={styles["tip-eyebrow"]}>How to send</div>
            <p className={styles["tip-body"]}>
              For now, email tips to{" "}
              <a href="mailto:tips@fullcarts.org" className={styles["tip-link"]}>
                tips@fullcarts.org
              </a>{" "}
              with a brief description of what changed and at least one image
              or source URL. We&apos;re building an in-page submission form
              next — it&apos;ll write directly into the same review queue our
              admins use, so your tip is treated identically to the ones our
              scrapers find.
            </p>
            <div className={styles["tip-meta"]}>
              Tips are reviewed within a week. We&apos;ll credit the source on
              the published event unless you ask us not to.
            </div>
          </div>
        </section>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Press &amp; corrections</h2>
          </div>
          <p className={styles["section-lede"]}>
            Journalists, researchers, and brand reps who want to dispute or
            clarify an event are all welcome to reach out. We publish
            corrections in-line on the affected event with the original claim
            preserved for transparency.
          </p>
          <div className={styles["contact-row"]}>
            <a className={styles["contact-card"]} href="mailto:press@fullcarts.org">
              <div className={styles["contact-eyebrow"]}>Press</div>
              <div className={styles["contact-email"]}>press@fullcarts.org</div>
              <div className={styles["contact-body"]}>
                Story ideas, data licensing, embargoed releases, interview
                requests.
              </div>
            </a>
            <a className={styles["contact-card"]} href="mailto:corrections@fullcarts.org">
              <div className={styles["contact-eyebrow"]}>Corrections</div>
              <div className={styles["contact-email"]}>corrections@fullcarts.org</div>
              <div className={styles["contact-body"]}>
                Dispute an event, request a retraction, flag missing context.
                Brand reps welcome.
              </div>
            </a>
          </div>
        </section>
      </div>
    </>
  );
}
