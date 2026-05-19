import { notFound } from "next/navigation";
import { createAdminClient } from "@/lib/supabase/admin";
import SiteNav from "@/components/SiteNav";
import ProductHero from "./_components/ProductHero";
import SizeTrajectory from "./_components/SizeTrajectory";
import ChangeHistory from "./_components/ChangeHistory";
import RetailersGrid from "./_components/RetailersGrid";
import RelatedProducts from "./_components/RelatedProducts";
import SkimpflationOverlay from "./_components/SkimpflationOverlay";
import PressCoverage from "./_components/PressCoverage";
import {
  buildTrajectory,
  computeSkimpData,
  eventsByDateDesc,
  expandUpcVariants,
  num,
  totalEvidenceCount,
} from "./lib";
import type {
  ConsumerReportRef,
  EventRow,
  PackVariant,
  ProductEntity,
  RelatedProduct,
  SkimpData,
  UsdaNutritionRow,
  VariantObservation,
} from "./types";
import styles from "./styles.module.css";

// ISR: per-product pages regenerate at most once per hour in the
// background. Same cadence as /brands/[name].
export const revalidate = 3600;

// Pre-build the top 30 products at deploy time by event count;
// everything else renders on first visit and gets cached.
export async function generateStaticParams() {
  const sb = createAdminClient();
  const { data } = await sb
    .from("shrinkflation_leaderboard")
    .select("entity_id")
    .order("shrink_count", { ascending: false })
    .limit(30);
  return (data ?? [])
    .filter((r) => r.entity_id)
    .map((r) => ({ id: String(r.entity_id) }));
}

interface PageProps {
  params: Promise<{ id: string }>;
}

async function loadProduct(id: string): Promise<{
  entity: ProductEntity;
  events: EventRow[];
  variants: PackVariant[];
  observations: VariantObservation[];
  related: RelatedProduct[];
  skimp: SkimpData | null;
  press: ConsumerReportRef[];
} | null> {
  const sb = createAdminClient();

  const { data: entity } = await sb
    .from("product_entities")
    .select("id, brand, canonical_name, category, image_url, manufacturer")
    .eq("id", id)
    .maybeSingle();

  if (!entity) return null;

  const [eventsRes, variantsRes, relatedRes] = await Promise.all([
    sb
      .from("event_evidence_summary")
      .select("*")
      .eq("entity_id", entity.id)
      .order("observed_date", { ascending: false }),
    sb
      .from("pack_variants")
      .select("id, variant_name, current_size, size_unit, upc, is_active")
      .eq("entity_id", entity.id),
    sb
      .from("shrinkflation_leaderboard")
      .select("entity_id, name, image_url, shrink_count, cumulative_shrink_pct")
      .eq("brand", entity.brand)
      .neq("entity_id", entity.id)
      .order("shrink_count", { ascending: false })
      .limit(8),
  ]);

  const variants = (variantsRes.data ?? []) as PackVariant[];

  // Pull observations for these variants in a second round-trip — the
  // brand page proved this is cheap enough at per-page scale to skip
  // a denormalised view. Skip the query entirely when no variants
  // exist (no observations possible).
  let observations: VariantObservation[] = [];
  if (variants.length > 0) {
    const { data } = await sb
      .from("variant_observations")
      .select("variant_id, observed_date, source_type, size, size_unit, price, retailer")
      .in("variant_id", variants.map((v) => v.id));
    observations = (data ?? []) as VariantObservation[];
  }

  // Skimpflation overlay — pull USDA nutrition snapshots for any of
  // the entity's UPCs. We hand the raw rows to computeSkimpData()
  // which picks the best UPC + release pair and computes deltas.
  let skimp: SkimpData | null = null;
  const upcCandidates = expandUpcVariants(variants.map((v) => v.upc));
  if (upcCandidates.length > 0) {
    const { data } = await sb
      .from("usda_product_history")
      .select(
        "gtin_upc, release_date, description, brand_name, calories_kcal, protein_g, total_fat_g, saturated_fat_g, carbs_g, fiber_g, sugars_g, calcium_mg, sodium_mg, cholesterol_mg",
      )
      .in("gtin_upc", upcCandidates);
    skimp = computeSkimpData((data ?? []) as UsdaNutritionRow[]);
  }

  // Consumer Reports coverage — silent no-op if the table or the
  // matched_at index isn't there yet (migration 058 may not have been
  // applied locally during development).
  let press: ConsumerReportRef[] = [];
  const pressRes = await sb
    .from("consumer_reports_findings")
    .select("id, source_url, title, published_at, excerpt, brand, product_name")
    .eq("entity_id", entity.id)
    .order("published_at", { ascending: false, nullsFirst: false })
    .limit(8);
  if (!pressRes.error) {
    press = (pressRes.data ?? []) as ConsumerReportRef[];
  }

  const related: RelatedProduct[] = ((relatedRes.data ?? []) as Array<{
    entity_id: string;
    name: string;
    image_url: string | null;
    shrink_count: number;
    cumulative_shrink_pct: string | number | null;
  }>).map((r) => ({
    entity_id: r.entity_id,
    canonical_name: r.name,
    image_url: r.image_url,
    event_count: r.shrink_count,
    worst_delta_pct: num(r.cumulative_shrink_pct),
  }));

  return {
    entity: entity as ProductEntity,
    events: (eventsRes.data ?? []) as EventRow[],
    variants,
    observations,
    related,
    skimp,
    press,
  };
}

export async function generateMetadata({ params }: PageProps) {
  const { id } = await params;
  const data = await loadProduct(id);
  if (!data) {
    return { title: "Product not found", robots: { index: false, follow: true } };
  }
  const { entity, events } = data;
  const ev = events.length;
  const title = `${entity.brand} ${entity.canonical_name} — ${ev} documented shrink${
    ev === 1 ? "" : "s"
  }`;
  const description = `Size-over-time history, every documented event, and full evidence trail for ${entity.brand} ${entity.canonical_name}.`;
  const image = entity.image_url ?? undefined;
  return {
    title,
    description,
    alternates: { canonical: `/products/${entity.id}` },
    openGraph: {
      title: `${title} · FullCarts`,
      description,
      type: "article",
      url: `/products/${entity.id}`,
      siteName: "FullCarts",
      images: image
        ? [{ url: image, alt: `${entity.brand} ${entity.canonical_name} package` }]
        : undefined,
    },
    twitter: {
      card: image ? "summary_large_image" : "summary",
      title: `${title} · FullCarts`,
      description,
      images: image ? [image] : undefined,
    },
  };
}

export default async function ProductPage({ params }: PageProps) {
  const { id } = await params;
  const data = await loadProduct(id);
  if (!data) notFound();

  const { entity, events, variants, observations, related, skimp, press } = data;
  const eventsDesc = eventsByDateDesc(events);
  const trajectory = buildTrajectory(events);
  const evidenceTotal = totalEvidenceCount(events);
  const unit = events[0]?.size_unit || "";

  // Structured data — Product + BreadcrumbList. Crawlers use the Product
  // schema for rich result eligibility; BreadcrumbList renders the
  // brand → product hierarchy in SERPs. UPCs (when present) hand search
  // engines a hard identifier so they can dedupe across our pages.
  const siteUrl =
    process.env.NEXT_PUBLIC_SITE_URL ?? "https://fullcarts.org";
  const brandSlug = encodeURIComponent(entity.brand.toLowerCase());
  const productJsonLd = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: `${entity.brand} ${entity.canonical_name}`,
    brand: { "@type": "Brand", name: entity.brand },
    category: entity.category ?? undefined,
    image: entity.image_url ?? undefined,
    description: `${entity.brand} ${entity.canonical_name} — ${events.length} documented shrinkflation event${
      events.length === 1 ? "" : "s"
    } tracked by FullCarts.`,
    url: `${siteUrl}/products/${entity.id}`,
    manufacturer: entity.manufacturer ?? undefined,
    gtin: variants.find((v) => v.upc)?.upc ?? undefined,
  };
  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Brands", item: `${siteUrl}/brands` },
      {
        "@type": "ListItem",
        position: 2,
        name: entity.brand,
        item: `${siteUrl}/brands/${brandSlug}`,
      },
      {
        "@type": "ListItem",
        position: 3,
        name: entity.canonical_name,
        item: `${siteUrl}/products/${entity.id}`,
      },
    ],
  };

  return (
    <>
      <SiteNav />
      <main id="main-content" className={styles.container}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify([productJsonLd, breadcrumbJsonLd]),
          }}
        />
        <div className={styles.breadcrumb}>
          <a href="/brands">Brands</a>
          <span className={styles.sep}>/</span>
          <a href={`/brands/${encodeURIComponent(entity.brand.toLowerCase())}`}>
            {entity.brand}
          </a>
          <span className={styles.sep}>/</span>
          <span className={styles.current}>{entity.canonical_name}</span>
        </div>

        <ProductHero entity={entity} events={events} variants={variants} />

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Size trajectory</h2>
            {trajectory.length >= 2 && (
              <div className={styles.meta}>
                {trajectory[0].size}
                {unit} → {trajectory[trajectory.length - 1].size}
                {unit} across {events.length} event
                {events.length === 1 ? "" : "s"}
              </div>
            )}
          </div>
          <SizeTrajectory steps={trajectory} unit={unit} />
        </section>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Change history</h2>
            <div className={styles.meta}>
              {events.length} event{events.length === 1 ? "" : "s"} ·{" "}
              {evidenceTotal} total source
              {evidenceTotal === 1 ? "" : "s"} · click a row for sources
            </div>
          </div>
          <ChangeHistory events={eventsDesc} />
        </section>

        {skimp && (
          <section className={styles.block}>
            <div className={styles["section-head"]}>
              <h2>What changed inside?</h2>
              <div className={styles.meta}>
                USDA FoodData Central · barcode {skimp.upc} ·{" "}
                {skimp.releases_compared} releases compared
              </div>
            </div>
            <SkimpflationOverlay data={skimp} />
          </section>
        )}

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Where it&apos;s sold</h2>
            <div className={styles.meta}>
              {variants.length} variant{variants.length === 1 ? "" : "s"} ·
              monitored via retailer APIs
            </div>
          </div>
          <RetailersGrid variants={variants} observations={observations} />
        </section>

        {press.length > 0 && (
          <section className={styles.block}>
            <div className={styles["section-head"]}>
              <h2>Press coverage</h2>
              <div className={styles.meta}>
                {press.length} Consumer Reports finding
                {press.length === 1 ? "" : "s"}
              </div>
            </div>
            <PressCoverage refs={press} />
          </section>
        )}

        {related.length > 0 && (
          <section className={styles.block}>
            <div className={styles["section-head"]}>
              <h2>Other {entity.brand} products we track</h2>
              <div className={styles.meta}>
                Top {Math.min(related.length, 8)} by event count
              </div>
            </div>
            <RelatedProducts brand={entity.brand} products={related} />
          </section>
        )}
      </main>
    </>
  );
}
