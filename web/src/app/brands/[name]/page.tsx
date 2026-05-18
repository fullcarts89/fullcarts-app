import { notFound } from "next/navigation";
import Link from "next/link";
import { createAdminClient } from "@/lib/supabase/admin";
import SiteNav from "@/components/SiteNav";
import BrandHero from "./_components/BrandHero";
import TimelineExplorer from "./_components/TimelineExplorer";
import WallOfShame from "./_components/WallOfShame";
import ProductGrid from "./_components/ProductGrid";
import { rollupProducts, dominantManufacturer } from "./lib";
import type {
  BrandRanking,
  EventRow,
  ProductEntity,
} from "./types";
import styles from "./styles.module.css";

// ISR: pages regenerate at most once per hour in the background.
export const revalidate = 3600;

// Pre-build the top 20 brands at deploy time; everything else is
// rendered on first visit and then cached.
export async function generateStaticParams() {
  const sb = createAdminClient();
  const { data } = await sb
    .from("brand_rankings")
    .select("brand")
    .order("shrinkflation_events", { ascending: false })
    .limit(20);
  return (data ?? []).map((r) => ({ name: r.brand.toLowerCase() }));
}

interface PageProps {
  params: Promise<{ name: string }>;
}

async function loadBrand(slug: string) {
  // Use admin client (no cookies) so this route stays statically
  // generatable with ISR — createClient() reads cookies and would
  // opt the page into dynamic rendering. All data read here is
  // public (brand_rankings, event_evidence_summary, product_entities
  // are SELECT-able by anon under existing RLS), so service-role
  // access is only for build/revalidate efficiency, not privilege.
  const sb = createAdminClient();
  const lower = decodeURIComponent(slug).toLowerCase();

  // ranking is the canary — if no row, brand doesn't exist and we 404.
  const ranking = await sb
    .from("brand_rankings")
    .select("*")
    .ilike("brand", lower)
    .maybeSingle();

  if (!ranking.data) return null;

  const canonicalBrand = (ranking.data as BrandRanking).brand;

  const [eventsRes, entitiesRes] = await Promise.all([
    sb
      .from("event_evidence_summary")
      .select("*")
      .eq("brand", canonicalBrand)
      .order("evidence_count", { ascending: false }),
    sb
      .from("product_entities")
      .select("id, brand, canonical_name, image_url, manufacturer")
      .eq("brand", canonicalBrand)
      .eq("is_retracted", false),
  ]);

  return {
    ranking: ranking.data as BrandRanking,
    events: (eventsRes.data ?? []) as EventRow[],
    entities: (entitiesRes.data ?? []) as (ProductEntity & { manufacturer: string | null })[],
  };
}

export async function generateMetadata({ params }: PageProps) {
  const { name } = await params;
  const lower = decodeURIComponent(name).toLowerCase();
  const sb = createAdminClient();
  const { data } = await sb
    .from("brand_index")
    .select("brand, shrinkflation_events, product_count, worst_delta_pct, thumbnail")
    .ilike("brand", lower)
    .maybeSingle();
  if (!data) {
    return {
      title: "Brand not found",
      robots: { index: false, follow: true },
    };
  }
  const ev = (data as { shrinkflation_events: number }).shrinkflation_events ?? 0;
  const pc = (data as { product_count: number }).product_count ?? 0;
  const brand = (data as { brand: string }).brand;
  const thumb = (data as { thumbnail: string | null }).thumbnail;
  const slug = encodeURIComponent(brand.toLowerCase());
  const title = `${brand} — ${ev} documented shrink${ev === 1 ? "" : "s"}`;
  const description = `Full scorecard for ${brand}: ${ev} documented shrinkflation event${
    ev === 1 ? "" : "s"
  } across ${pc} product${pc === 1 ? "" : "s"}, with timeline, evidence trail, and per-product history.`;
  return {
    title,
    description,
    alternates: { canonical: `/brands/${slug}` },
    openGraph: {
      title: `${title} · FullCarts`,
      description,
      type: "article",
      url: `/brands/${slug}`,
      siteName: "FullCarts",
      images: thumb ? [{ url: thumb, alt: `${brand} product photo` }] : undefined,
    },
    twitter: {
      card: thumb ? "summary_large_image" : "summary",
      title: `${title} · FullCarts`,
      description,
      images: thumb ? [thumb] : undefined,
    },
  };
}

export default async function BrandPage({ params }: PageProps) {
  const { name } = await params;
  const data = await loadBrand(name);
  if (!data) notFound();

  const { ranking, events, entities } = data;
  const manufacturer = dominantManufacturer(entities);
  const products = rollupProducts(entities, events);

  // BreadcrumbList JSON-LD mirrors the visible breadcrumb so search
  // results can render the brand → product hierarchy. Organization
  // payloads live in the root layout (Phase F).
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://fullcarts.org";
  const brandSlug = encodeURIComponent(ranking.brand.toLowerCase());
  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Brands", item: `${siteUrl}/brands` },
      {
        "@type": "ListItem",
        position: 2,
        name: ranking.brand,
        item: `${siteUrl}/brands/${brandSlug}`,
      },
    ],
  };

  return (
    <>
      <SiteNav />
      <main id="main-content" className={styles.container}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
        />
        <div className={styles.breadcrumb}>
          <Link href="/brands">Brands</Link>
          <span className={styles.sep}>/</span>
          <span className={styles.current}>{ranking.brand}</span>
        </div>

        <BrandHero ranking={ranking} manufacturer={manufacturer} />

        <TimelineExplorer ranking={ranking} events={events} />

        <WallOfShame events={events} entities={entities} />

        <ProductGrid products={products} brand={ranking.brand} />
      </main>
    </>
  );
}
