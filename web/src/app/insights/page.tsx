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
  FredCpiRow,
  LeaderboardRow,
  NewsFeedRow,
  RestorationRow,
  TaggedClaim,
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
  // Tagged-claim queries (skimpflation, spot-the-difference) pull from
  // the same claims table — PostgREST array-contains uses `cs.{val}`.
  const [
    statsRes,
    blsRes,
    fredRes,
    timelineRes,
    categoriesRes,
    leaderRes,
    restorationsRes,
    newsRes,
    skimpClaimsRes,
    spotDiffClaimsRes,
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
      .from("claims")
      .select(
        "id, brand, product_name, category, old_size, old_size_unit, new_size, new_size_unit, change_description, observed_date, image_storage_path, evidence_tags, raw_item_id",
      )
      .contains("evidence_tags", ["Skimpflation"])
      .order("observed_date", { ascending: false, nullsFirst: false })
      .limit(8),
    sb
      .from("claims")
      .select(
        "id, brand, product_name, category, old_size, old_size_unit, new_size, new_size_unit, change_description, observed_date, image_storage_path, evidence_tags, raw_item_id",
      )
      .contains("evidence_tags", ["Spot the Difference"])
      .order("observed_date", { ascending: false, nullsFirst: false })
      .limit(8),
  ]);

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

  // For each tagged-claim batch we fetch the underlying raw_items in
  // one extra round-trip to surface the original source URL on the
  // card. Cheap: at most 16 rows total.
  const taggedIds = [
    ...((skimpClaimsRes.data ?? []) as TaggedClaim[]).map((c) => c.raw_item_id),
    ...((spotDiffClaimsRes.data ?? []) as TaggedClaim[]).map((c) => c.raw_item_id),
  ].filter((id): id is string => Boolean(id));
  const rawItemsRes = taggedIds.length
    ? await sb
        .from("raw_items")
        .select("id, source_url, raw_payload")
        .in("id", taggedIds)
    : { data: [] };
  const rawById = new Map<string, { source_url: string | null; image: string | null }>();
  for (const row of (rawItemsRes.data ?? []) as Array<{
    id: string;
    source_url: string | null;
    raw_payload: Record<string, unknown> | null;
  }>) {
    rawById.set(row.id, {
      source_url: row.source_url ?? null,
      image: (row.raw_payload?.["socialimage"] as string) || null,
    });
  }

  const enrichTagged = (rows: TaggedClaim[]): TaggedClaim[] =>
    rows.map((c) => {
      const r = c.raw_item_id ? rawById.get(c.raw_item_id) : undefined;
      return {
        ...c,
        source_url: r?.source_url ?? null,
        source_image: r?.image ?? null,
      };
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
    skimpClaims: enrichTagged((skimpClaimsRes.data ?? []) as TaggedClaim[]),
    spotDiffClaims: enrichTagged((spotDiffClaimsRes.data ?? []) as TaggedClaim[]),
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
          <SkimpflationLeaderboard rows={data.skimpClaims} />
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
          <EvidenceWall rows={data.spotDiffClaims} />
        </section>
      </div>
    </>
  );
}
