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
import ShrinkingCart from "./_components/ShrinkingCart";
import {
  buildCartBasket,
  buildChart,
  headlineBls,
  imageFromRawPayload,
  isFreeOutlet,
  isoDay,
  stripHtml,
} from "./lib";
import type {
  BlsRow,
  CartItem,
  CategoryRow,
  DashboardStats,
  EventWithSources,
  FredCpiRow,
  LeaderboardRow,
  NewsFeedRow,
  RestorationRow,
  TaggedClaim,
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

  // Date bookends. The chart uses ~4 years of events; the news section
  // uses last 90 days.
  const fourYearsAgo = new Date();
  fourYearsAgo.setMonth(fourYearsAgo.getMonth() - 48);
  const ninetyDaysAgo = new Date();
  ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);

  const [
    statsRes,
    blsRes,
    fredRes,
    eventsRes,
    categoriesRes,
    pcLeaderRes,
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
    // Chart events: pull every shrinkflation event with its source
    // dates so we can key the chart on "when the shrink was first
    // publicly noticed" rather than the AI-extracted observed_date
    // (which has a known fallback-to-today bug). Bounded to 4 years.
    sb
      .from("event_evidence_summary")
      .select("event_id, observed_date, sources")
      .gte("observed_date", isoDay(fourYearsAgo.toISOString()))
      .limit(5000),
    sb
      .from("category_stats")
      .select("category, product_count, total_events, shrink_events, avg_shrink_pct")
      .order("shrink_events", { ascending: false })
      .limit(8),
    // Repeat offenders: pull every shrinkflation row so we can compute
    // per-entity count + worst single drop in JS. The previous query
    // (shrinkflation_leaderboard) summed per-event deltas, which
    // produced nonsensical >100% "cumulative" values. Bounded by
    // event count — ~2.8k rows today, well within payload limits.
    sb
      .from("published_changes")
      .select(
        "entity_id, size_delta_pct, brand, product_name, size_before, size_after, size_unit, observed_date",
      )
      .eq("change_type", "shrinkflation")
      .eq("is_retracted", false)
      .not("entity_id", "is", null)
      .lt("size_delta_pct", 0)
      .limit(5000),
    sb
      .from("restorations")
      .select("id, brand, product_name, size_before, size_after, size_unit, observed_date, published_at")
      .order("observed_date", { ascending: false })
      .limit(8),
    // News: pull raw_items in the last 90 days (news_articles is empty
    // legacy; actual news lives in raw_items). Filter to non-paywalled
    // outlets at the page boundary.
    sb
      .from("raw_items")
      .select("id, source_type, source_url, source_date, raw_payload")
      .in("source_type", ["news", "gdelt"])
      .gte("source_date", ninetyDaysAgo.toISOString())
      .order("source_date", { ascending: false })
      .limit(200),
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

  // For each tagged-claim batch we fetch the underlying raw_items
  // (one extra round-trip) to surface the original source URL + image
  // on the card. Cheap: at most 16 rows total.
  const taggedIds = [
    ...((skimpClaimsRes.data ?? []) as TaggedClaim[]).map((c) => c.raw_item_id),
    ...((spotDiffClaimsRes.data ?? []) as TaggedClaim[]).map((c) => c.raw_item_id),
  ].filter((id): id is string => Boolean(id));
  const taggedRawItemsRes = taggedIds.length
    ? await sb
        .from("raw_items")
        .select("id, source_url, raw_payload")
        .in("id", taggedIds)
    : { data: [] };
  const rawById = new Map<string, { source_url: string | null; image: string | null }>();
  for (const row of (taggedRawItemsRes.data ?? []) as Array<{
    id: string;
    source_url: string | null;
    raw_payload: Record<string, unknown> | null;
  }>) {
    rawById.set(row.id, {
      source_url: row.source_url ?? null,
      // Mirror the pipeline's image extraction so we can fall back to
      // the original Reddit/news image when image_storage_path is null
      // (image backfill misses or hasn't run on that claim yet).
      image: imageFromRawPayload(row.raw_payload),
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

  // Repeat offenders: aggregate published_changes rows by entity_id,
  // count + take MIN(size_delta_pct) per entity, sort by count desc,
  // take top 8. This replaces the previous shrinkflation_leaderboard
  // query whose cumulative_shrink_pct (SUM of per-event %) produced
  // mathematically meaningless >100% values.
  type PcRow = {
    entity_id: string | null;
    size_delta_pct: string | number | null;
    brand: string | null;
    product_name: string | null;
    size_before: string | number | null;
    size_after: string | number | null;
    size_unit: string | null;
    observed_date: string | null;
  };
  type EntityAgg = {
    entity_id: string;
    shrink_count: number;
    worst_drop_pct: number;
    brand: string;
    product_name: string;
  };
  const byEntity = new Map<string, EntityAgg>();
  for (const r of (pcLeaderRes.data ?? []) as PcRow[]) {
    if (!r.entity_id) continue;
    const delta = typeof r.size_delta_pct === "string"
      ? parseFloat(r.size_delta_pct)
      : (r.size_delta_pct ?? 0);
    if (!Number.isFinite(delta) || delta >= 0) continue;
    const cur = byEntity.get(r.entity_id);
    if (!cur) {
      byEntity.set(r.entity_id, {
        entity_id: r.entity_id,
        shrink_count: 1,
        worst_drop_pct: delta,
        brand: r.brand || "",
        product_name: r.product_name || "",
      });
    } else {
      cur.shrink_count += 1;
      if (delta < cur.worst_drop_pct) cur.worst_drop_pct = delta;
    }
  }
  const topEntities = Array.from(byEntity.values())
    .sort((a, b) => b.shrink_count - a.shrink_count || a.worst_drop_pct - b.worst_drop_pct)
    .slice(0, 8);

  // Candidate basket entities: any entity with at least 1 shrink event
  // that appears in pcRows. We rely on image_url filtering to keep the
  // basket visual. Top biggest shrinks first (lowest worst_drop_pct) so
  // if the query hits its row cap we keep the worst-offenders.
  const basketCandidateIds = Array.from(byEntity.values())
    .sort((a, b) => a.worst_drop_pct - b.worst_drop_pct)
    .slice(0, 200)
    .map((e) => e.entity_id);

  // Hydrate canonical name + image_url. Union of leaderboard top-8 and
  // basket-candidate IDs so we do one query instead of two.
  const hydrateIds = Array.from(
    new Set([...topEntities.map((e) => e.entity_id), ...basketCandidateIds]),
  );
  const entitiesRes = hydrateIds.length
    ? await sb
        .from("product_entities")
        .select("id, canonical_name, brand, category, image_url")
        .in("id", hydrateIds)
    : { data: [] };
  const entityById = new Map<string, {
    canonical_name: string;
    brand: string;
    category: string | null;
    image_url: string | null;
  }>();
  for (const row of (entitiesRes.data ?? []) as Array<{
    id: string;
    canonical_name: string;
    brand: string;
    category: string | null;
    image_url: string | null;
  }>) {
    entityById.set(row.id, {
      canonical_name: row.canonical_name,
      brand: row.brand,
      category: row.category,
      image_url: row.image_url,
    });
  }
  // Build the shrinking-cart basket from the same pcRows + entity map.
  // buildCartBasket filters to entities-with-images and 2-60% shrinks,
  // then dedups by brand for visual variety.
  const basket: CartItem[] = buildCartBasket(
    (pcLeaderRes.data ?? []) as PcRow[],
    entityById,
    12,
  );

  const leaderboard: LeaderboardRow[] = topEntities.map((e) => {
    const ent = entityById.get(e.entity_id);
    return {
      entity_id: e.entity_id,
      name: ent?.canonical_name || e.product_name || "Unknown product",
      brand: ent?.brand || e.brand || "—",
      category: ent?.category ?? null,
      image_url: ent?.image_url ?? null,
      shrink_count: e.shrink_count,
      worst_drop_pct: e.worst_drop_pct,
    };
  });

  // News: shape raw_items rows into NewsFeedRow, extracting outlet
  // from the source-type-specific payload field (news → source_name,
  // gdelt → domain), then filter to non-paywalled outlets.
  type RawItem = {
    id: string;
    source_type: string;
    source_url: string | null;
    source_date: string | null;
    raw_payload: Record<string, unknown> | null;
  };
  const rawNews = ((newsRes.data ?? []) as RawItem[]).map((r) => {
    const p = (r.raw_payload || {}) as Record<string, unknown>;
    const outlet = (p["source_name"] as string)
      || (p["domain"] as string)
      || "";
    const title = stripHtml((p["title"] as string) || "");
    // Google News RSS ships <description> as HTML — strip tags so the
    // card doesn't render raw <a href=...> markup. If the cleaned
    // summary is empty or duplicates the title, drop it.
    const rawSummary = stripHtml(
      ((p["description"] as string) || (p["summary"] as string) || "") as string,
    );
    const summary = rawSummary && rawSummary !== title ? rawSummary : null;
    return {
      id: r.id,
      url: r.source_url || "",
      title,
      outlet,
      published_at: r.source_date,
      summary,
      linked_products_count: 0,
    } as NewsFeedRow;
  });
  const news = rawNews
    .filter((n) => n.title && n.url)
    .filter((n) => isFreeOutlet(n.outlet))
    .slice(0, 5);

  return {
    stats,
    bls: (blsRes.data ?? []) as BlsRow[],
    fred: (fredRes.data ?? []) as FredCpiRow[],
    events: (eventsRes.data ?? []) as EventWithSources[],
    categories: (categoriesRes.data ?? []) as CategoryRow[],
    leaderboard,
    restorations: (restorationsRes.data ?? []) as RestorationRow[],
    news,
    basket,
    skimpClaims: enrichTagged((skimpClaimsRes.data ?? []) as TaggedClaim[]),
    spotDiffClaims: enrichTagged((spotDiffClaimsRes.data ?? []) as TaggedClaim[]),
  };
}

export default async function InsightsPage() {
  const data = await loadInsights();
  const chart = buildChart(data.events, data.bls, data.fred);
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
            <h2>The dollars-to-air conversion</h2>
            <div className={styles.meta}>
              Live calculator · real basket data
            </div>
          </div>
          <p className={styles["section-lede"]}>
            Drop in your weekly grocery spend and see how much of every
            dollar is now just air in the bag — the dollar value of the
            food that&apos;s been removed from packages without the price
            changing. Built from actual size deltas, not estimates.
          </p>
          <ShrinkingCart basket={data.basket} />
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
              Last 90 days · non-paywalled outlets
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
