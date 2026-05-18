import { createAdminClient } from "@/lib/supabase/admin";
import SiteNav from "@/components/SiteNav";
import InsightsHero from "./_components/InsightsHero";
import BlsHeadline from "./_components/BlsHeadline";
import ThreeLineChart from "./_components/ThreeLineChart";
import CategoryBars from "./_components/CategoryBars";
import SkimpflationLeaderboard from "./_components/SkimpflationLeaderboard";
import RepeatOffenders from "./_components/RepeatOffenders";
import RestorationCorner from "./_components/RestorationCorner";
import NewsFeed from "./_components/NewsFeed";
import EvidenceWall from "./_components/EvidenceWall";
import { buildChart, headlineBls, isoDay } from "./lib";
import type {
  BlsRow,
  CategoryRow,
  DashboardStats,
  EvidenceWallRow,
  FredCpiRow,
  LeaderboardRow,
  NewsFeedRow,
  RestorationRow,
  SkimpRow,
  TimelineRow,
} from "./types";
import styles from "./styles.module.css";

// Refresh once per hour in the background. ISR.
export const revalidate = 3600;

export const metadata = {
  title: "By the numbers · Shrinkflation insights · FullCarts",
  description:
    "Macro shrinkflation data: BLS R-CPI-SC counts, FRED food CPI, USDA skimpflation findings, worst categories, and the products that keep shrinking. Cross-referenced across every source we track.",
};

async function loadInsights() {
  const sb = createAdminClient();

  // Most queries return ≤ 50 rows so the round-trip is dominated by
  // network latency, not payload size — parallelize all of them.
  const [
    statsRes,
    blsRes,
    fredRes,
    timelineRes,
    categoriesRes,
    leaderRes,
    restorationsRes,
    newsRes,
    evidenceRes,
  ] = await Promise.all([
    sb.rpc("dashboard_stats"),
    sb
      .from("bls_shrinkflation")
      .select("series, period, downsizing_count, upsizing_count")
      .order("period", { ascending: false })
      .limit(400),
    sb
      .from("fred_cpi_data")
      .select("observation_date, value")
      .eq("series_id", "CPIUFDNS")
      .order("observation_date", { ascending: false })
      .limit(60),
    sb
      .from("shrinkflation_timeline")
      .select("month, events, shrink_events, restoration_events, avg_shrink_pct")
      .order("month", { ascending: false })
      .limit(48),
    sb
      .from("category_stats")
      .select("category, product_count, total_events, shrink_events, avg_shrink_pct")
      .order("shrink_events", { ascending: false })
      .limit(8),
    sb
      .from("shrinkflation_leaderboard")
      .select("entity_id, name, brand, category, image_url, shrink_count, cumulative_shrink_pct")
      .order("shrink_count", { ascending: false })
      .limit(8),
    sb
      .from("restorations")
      .select("id, brand, product_name, size_before, size_after, size_unit, observed_date, published_at")
      .order("observed_date", { ascending: false })
      .limit(8),
    sb
      .from("news_feed")
      .select("id, url, title, outlet, published_at, summary, linked_products_count")
      .order("published_at", { ascending: false })
      .limit(5),
    sb
      .from("evidence_wall")
      .select("id, brand, product_name, category, signal_type, severity, date_spotted, size_delta_pct, image_url, tag, source_url")
      .eq("status", "approved")
      .order("date_spotted", { ascending: false })
      .limit(8),
  ]);

  // Skimpflation RPC is sequenced separately — the function scans
  // USDA history and can be slow on a cold cache. min_score caps row
  // count to manageable size.
  const skimpRes = await sb.rpc("nutrition_skimpflation", { min_score: 10 });

  // dashboard_stats returns a JSONB blob; defaults protect the page
  // if the function is missing (e.g. fresh DB).
  const statsRaw = (statsRes.data ?? {}) as Partial<DashboardStats>;
  const stats: DashboardStats = {
    total_products: statsRaw.total_products ?? 0,
    total_changes: statsRaw.total_changes ?? 0,
    shrinkflation_events: statsRaw.shrinkflation_events ?? 0,
    categories_tracked: statsRaw.categories_tracked ?? 0,
    avg_shrink_pct: statsRaw.avg_shrink_pct ?? null,
    worst_shrink_pct: statsRaw.worst_shrink_pct ?? null,
    pending_review: statsRaw.pending_review ?? 0,
  };

  const skimpAll = (skimpRes.data ?? []) as SkimpRow[];
  skimpAll.sort((a, b) => {
    const sa = typeof a.skimp_score === "string"
      ? parseFloat(a.skimp_score)
      : (a.skimp_score ?? 0);
    const sb2 = typeof b.skimp_score === "string"
      ? parseFloat(b.skimp_score)
      : (b.skimp_score ?? 0);
    return (sb2 || 0) - (sa || 0);
  });

  return {
    stats,
    bls: (blsRes.data ?? []) as BlsRow[],
    fred: (fredRes.data ?? []) as FredCpiRow[],
    timeline: (timelineRes.data ?? []) as TimelineRow[],
    categories: (categoriesRes.data ?? []) as CategoryRow[],
    leaderboard: (leaderRes.data ?? []) as LeaderboardRow[],
    restorations: (restorationsRes.data ?? []) as RestorationRow[],
    news: (newsRes.data ?? []) as NewsFeedRow[],
    evidence: (evidenceRes.data ?? []) as EvidenceWallRow[],
    skimpTop: skimpAll.slice(0, 8),
    skimpTotal: skimpAll.length,
  };
}

export default async function InsightsPage() {
  const data = await loadInsights();
  const chart = buildChart(data.timeline, data.bls, data.fred);
  const headline = headlineBls(data.bls);

  const today = new Date().toISOString();
  const lastUpdated = isoDay(today);

  return (
    <>
      <SiteNav />
      <div className={styles.container}>
        <InsightsHero stats={data.stats} lastUpdated={lastUpdated} />
        <BlsHeadline
          count={headline.count}
          quarter={headline.quarter}
          prevQuarterDeltaPct={headline.prevQuarterDeltaPct}
          yearAgoDeltaPct={headline.yearAgoDeltaPct}
        />

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Inflation, shrinkflation, and how they trade off</h2>
            <div className={styles.meta}>Monthly · trailing window</div>
          </div>
          <p className={styles["section-lede"]}>
            When the food-at-home CPI rises, brands face a choice — raise the
            price, shrink the package, or change the recipe. Plotting{" "}
            <strong>our documented shrink events</strong> (red) against the{" "}
            <strong>BLS downsizing count</strong> (blue dashed) and{" "}
            <strong>FRED&apos;s food-at-home CPI</strong> (amber) shows how
            the three move together.
          </p>
          <ThreeLineChart points={chart} />
          <div className={styles.caveat}>
            FRED CPI is YoY%, BLS counts are quarterly spread evenly across
            months, our events are monthly raw counts
          </div>
        </section>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Which categories are getting hit hardest?</h2>
            <div className={styles.meta}>
              Top {data.categories.length} · by event count
            </div>
          </div>
          <p className={styles["section-lede"]}>
            Snacks and confectionery typically dominate the list — small,
            repeatedly-purchased items where shaving a few grams off the bag
            is least noticeable to shoppers.
          </p>
          <CategoryBars rows={data.categories} />
        </section>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Skimpflation: when the recipe quietly changes</h2>
            <div className={styles.meta}>USDA FoodData Central</div>
          </div>
          <p className={styles["section-lede"]}>
            It&apos;s not just the bag getting smaller.{" "}
            <strong>Skimpflation</strong> is when brands swap ingredients to
            lower cost — less meat, more filler, less butter, more palm oil.
            We cross-reference USDA&apos;s quarterly FoodData Central releases
            to flag nutrition changes that look like ingredient substitution
            rather than reformulation for taste.
          </p>
          <SkimpflationLeaderboard rows={data.skimpTop} totalCount={data.skimpTotal} />
        </section>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Repeat-offender products</h2>
            <div className={styles.meta}>
              Top {data.leaderboard.length} by event count
            </div>
          </div>
          <p className={styles["section-lede"]}>
            Products with the most distinct documented shrinkflation events.
            These aren&apos;t one-off cuts — they&apos;re a pattern.
          </p>
          <RepeatOffenders rows={data.leaderboard} />
        </section>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Restoration corner</h2>
            <div className={styles.meta}>Good news</div>
          </div>
          <p className={styles["section-lede"]}>
            Not every shrink stays shrunk. These products got their size{" "}
            <em>restored</em> — either as a deliberate brand response to
            negative coverage, or as part of a packaging redesign that
            reverted earlier downsizing.
          </p>
          <RestorationCorner rows={data.restorations} />
        </section>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>In the news</h2>
            <div className={styles.meta}>
              {data.news.length} articles linked to tracked products
            </div>
          </div>
          <NewsFeed rows={data.news} />
        </section>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Spot the difference</h2>
            <div className={styles.meta}>Curated evidence wall</div>
          </div>
          <p className={styles["section-lede"]}>
            Hand-selected side-by-side comparisons where the size change is
            visually verifiable from a single photo or shelf observation.
            The full evidence trail lives on each product&apos;s page.
          </p>
          <EvidenceWall rows={data.evidence} />
        </section>
      </div>
    </>
  );
}
