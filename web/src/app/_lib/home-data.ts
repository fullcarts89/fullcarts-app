// Server-side data layer for the homepage. All queries run in parallel
// at build / ISR-revalidate time and never reach the browser.
import { createAdminClient } from "@/lib/supabase/admin";

export interface JustDoc {
  event_id: string;
  entity_id: string | null;
  brand: string;
  product_name: string;
  product_category: string | null;
  size_before: number;
  size_after: number;
  size_unit: string;
  size_delta_pct: number;
  observed_date: string;
  product_image_url: string;
}

export interface BrandOfWeek {
  brand: string;
  thumb: string | null;
  total_events: number;
  product_count: number;
  avg_shrink_per_event: number;
  /** Plain-English reason the brand was selected this week. */
  reason: string;
  top_event_evidence_count: number;
}

export interface ActiveBrand {
  brand: string;
  recent_events: number;
  total_events: number;
  product_count: number;
}

export interface RecentShrink {
  entity_id: string | null;
  brand: string;
  product_name: string;
  product_category: string | null;
  size_before: number;
  size_after: number;
  size_unit: string;
  size_delta_pct: number;
  observed_date: string;
  product_image_url: string;
}

export interface TagCount {
  tag: string;
  count: number;
}

export interface HomeData {
  counters: {
    events: number;
    brands: number;
    products: number;
    bls_downsizings: number;
  };
  just_doc: JustDoc | null;
  brand_of_week: BrandOfWeek | null;
  most_active: ActiveBrand[];
  recent_shrinks: RecentShrink[];
  tags: TagCount[];
}

function n(x: string | number | null | undefined): number {
  if (x == null) return 0;
  const v = typeof x === "string" ? parseFloat(x) : x;
  return Number.isFinite(v) ? v : 0;
}

/** Order in which the seven evidence tags appear on the homepage. */
const TAG_ORDER = [
  "So Smol",
  "Slack Fill",
  "Spot the Difference",
  "Skimpflation",
  "Paper Thin",
  "Not as Advertised",
  "Stretchflation",
];

export async function loadHomeData(): Promise<HomeData> {
  const sb = createAdminClient();

  // Counters — four parallel COUNT/aggregate queries.
  // The BLS sum can't be done via PostgREST so we fetch the 959 rows
  // and reduce in JS (small, cached by ISR).
  const [eventsRes, brandsRes, productsRes, blsRes] = await Promise.all([
    sb
      .from("published_changes")
      .select("*", { count: "exact", head: true })
      .eq("is_retracted", false)
      .eq("change_type", "shrinkflation"),
    sb
      .from("brand_rankings")
      .select("*", { count: "exact", head: true }),
    sb
      .from("product_entities")
      .select("*", { count: "exact", head: true }),
    sb
      .from("bls_shrinkflation")
      .select("downsizing_count")
      .gte("period", "2015-01-01"),
  ]);
  const blsRows = (blsRes.data ?? []) as { downsizing_count: number | null }[];
  const blsSum = blsRows.reduce(
    (s, r) => s + (r.downsizing_count ?? 0),
    0,
  );

  // Just documented — most recent shrinkflation event with an image,
  // filtered to a plausible delta so unit-parsing errors don't surface.
  const justDocRes = await sb
    .from("recent_changes")
    .select(
      "id, entity_id, brand, product_name, product_category, size_before, size_after, size_unit, size_delta_pct, observed_date, product_image_url",
    )
    .eq("is_retracted", false)
    .eq("change_type", "shrinkflation")
    .not("product_image_url", "is", null)
    .gte("size_delta_pct", -50)
    .lte("size_delta_pct", -3)
    .order("published_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  // Brand of the week — brand of the most-cited event in the last 14
  // days. Falls back to the most-active brand in the last 30 days if
  // the 14-day window has no qualifying event.
  const bowResp = await sb
    .from("published_changes")
    .select("brand, evidence_count, observed_date")
    .eq("is_retracted", false)
    .gte(
      "published_at",
      new Date(Date.now() - 14 * 86400 * 1000).toISOString(),
    )
    .order("evidence_count", { ascending: false })
    .limit(1)
    .maybeSingle();
  let bowBrand: string | null = bowResp.data?.brand ?? null;
  const bowTopEvidence = n(bowResp.data?.evidence_count);
  if (!bowBrand) {
    const fallback = await sb
      .from("published_changes")
      .select("brand")
      .eq("is_retracted", false)
      .gte(
        "published_at",
        new Date(Date.now() - 30 * 86400 * 1000).toISOString(),
      )
      .order("published_at", { ascending: false })
      .limit(1)
      .maybeSingle();
    bowBrand = fallback.data?.brand ?? null;
  }

  let brandOfWeek: BrandOfWeek | null = null;
  if (bowBrand) {
    const [rankRes, thumbRes] = await Promise.all([
      sb
        .from("brand_rankings")
        .select("brand, shrinkflation_events, product_count, avg_shrink_per_event")
        .eq("brand", bowBrand)
        .maybeSingle(),
      sb
        .from("product_entities")
        .select("image_url")
        .eq("brand", bowBrand)
        .not("image_url", "is", null)
        .order("created_at", { ascending: false })
        .limit(1)
        .maybeSingle(),
    ]);
    if (rankRes.data) {
      brandOfWeek = {
        brand: rankRes.data.brand,
        thumb: thumbRes.data?.image_url ?? null,
        total_events: rankRes.data.shrinkflation_events ?? 0,
        product_count: rankRes.data.product_count ?? 0,
        avg_shrink_per_event: n(rankRes.data.avg_shrink_per_event),
        top_event_evidence_count: bowTopEvidence,
        reason:
          bowTopEvidence >= 3
            ? `Top of mind this week — ${bowTopEvidence} sources documented the same event in the last 14 days.`
            : "Most recently spotted in our pipeline.",
      };
    }
  }

  // Most active this month — top 6 brands by published-event count in
  // the last 30 days, joined to brand_rankings for the static totals.
  const recentBrandsRes = await sb
    .from("published_changes")
    .select("brand")
    .eq("is_retracted", false)
    .eq("change_type", "shrinkflation")
    .gte(
      "published_at",
      new Date(Date.now() - 30 * 86400 * 1000).toISOString(),
    );
  const recentCounts = new Map<string, number>();
  for (const r of (recentBrandsRes.data ?? []) as { brand: string }[]) {
    recentCounts.set(r.brand, (recentCounts.get(r.brand) ?? 0) + 1);
  }
  const topBrandNames = [...recentCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([brand]) => brand);
  let mostActive: ActiveBrand[] = [];
  if (topBrandNames.length > 0) {
    const ranksRes = await sb
      .from("brand_rankings")
      .select("brand, shrinkflation_events, product_count")
      .in("brand", topBrandNames);
    const byBrand = new Map<
      string,
      { events: number; products: number }
    >();
    for (const r of (ranksRes.data ?? []) as {
      brand: string;
      shrinkflation_events: number;
      product_count: number;
    }[]) {
      byBrand.set(r.brand, {
        events: r.shrinkflation_events,
        products: r.product_count,
      });
    }
    mostActive = topBrandNames.map((brand) => ({
      brand,
      recent_events: recentCounts.get(brand) ?? 0,
      total_events: byBrand.get(brand)?.events ?? 0,
      product_count: byBrand.get(brand)?.products ?? 0,
    }));
  }

  // Recent biggest shrinks — last 6 events in the last 180 days with
  // images and plausible delta, sorted by % drop.
  const recentShrinksRes = await sb
    .from("recent_changes")
    .select(
      "entity_id, brand, product_name, product_category, size_before, size_after, size_unit, size_delta_pct, observed_date, product_image_url",
    )
    .eq("is_retracted", false)
    .eq("change_type", "shrinkflation")
    .not("product_image_url", "is", null)
    .gte("size_delta_pct", -50)
    .lte("size_delta_pct", -5)
    .gte(
      "observed_date",
      new Date(Date.now() - 180 * 86400 * 1000)
        .toISOString()
        .slice(0, 10),
    )
    .order("size_delta_pct", { ascending: true })
    .limit(6);

  // Tag counts — read all claims with non-empty evidence_tags and count
  // in JS. Cheap because there are only ~700 such rows total.
  const tagRows = await sb
    .from("claims")
    .select("evidence_tags")
    .not("evidence_tags", "is", null);
  const tagCounts = new Map<string, number>();
  for (const r of (tagRows.data ?? []) as {
    evidence_tags: string[] | null;
  }[]) {
    for (const t of r.evidence_tags ?? []) {
      tagCounts.set(t, (tagCounts.get(t) ?? 0) + 1);
    }
  }
  const tags: TagCount[] = TAG_ORDER.map((tag) => ({
    tag,
    count: tagCounts.get(tag) ?? 0,
  }));

  return {
    counters: {
      events: eventsRes.count ?? 0,
      brands: brandsRes.count ?? 0,
      products: productsRes.count ?? 0,
      bls_downsizings: blsSum,
    },
    just_doc: justDocRes.data
      ? {
          event_id: justDocRes.data.id,
          entity_id: justDocRes.data.entity_id ?? null,
          brand: justDocRes.data.brand,
          product_name: justDocRes.data.product_name,
          product_category: justDocRes.data.product_category,
          size_before: n(justDocRes.data.size_before),
          size_after: n(justDocRes.data.size_after),
          size_unit: justDocRes.data.size_unit ?? "",
          size_delta_pct: n(justDocRes.data.size_delta_pct),
          observed_date: justDocRes.data.observed_date ?? "",
          product_image_url: justDocRes.data.product_image_url!,
        }
      : null,
    brand_of_week: brandOfWeek,
    most_active: mostActive,
    recent_shrinks: (recentShrinksRes.data ?? []).map(
      (r: {
        entity_id: string | null;
        brand: string;
        product_name: string;
        product_category: string | null;
        size_before: string | number;
        size_after: string | number;
        size_unit: string | null;
        size_delta_pct: string | number;
        observed_date: string;
        product_image_url: string;
      }) => ({
        entity_id: r.entity_id ?? null,
        brand: r.brand,
        product_name: r.product_name,
        product_category: r.product_category,
        size_before: n(r.size_before),
        size_after: n(r.size_after),
        size_unit: r.size_unit ?? "",
        size_delta_pct: n(r.size_delta_pct),
        observed_date: r.observed_date,
        product_image_url: r.product_image_url,
      }),
    ),
    tags,
  };
}

export function brandHref(brand: string): string {
  return `/brands/${encodeURIComponent(brand.toLowerCase())}`;
}
