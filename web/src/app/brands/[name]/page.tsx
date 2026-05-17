import { notFound } from "next/navigation";
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
      .eq("brand", canonicalBrand),
  ]);

  return {
    ranking: ranking.data as BrandRanking,
    events: (eventsRes.data ?? []) as EventRow[],
    entities: (entitiesRes.data ?? []) as (ProductEntity & { manufacturer: string | null })[],
  };
}

export default async function BrandPage({ params }: PageProps) {
  const { name } = await params;
  const data = await loadBrand(name);
  if (!data) notFound();

  const { ranking, events, entities } = data;
  const manufacturer = dominantManufacturer(entities);
  const products = rollupProducts(entities, events);

  return (
    <>
      <SiteNav />
      <div className={styles.container}>
        <div className={styles.breadcrumb}>
          <a href="/">Brands</a>
          <span className={styles.sep}>/</span>
          <span className={styles.current}>{ranking.brand}</span>
        </div>

        <BrandHero ranking={ranking} manufacturer={manufacturer} />

        <TimelineExplorer ranking={ranking} events={events} />

        <WallOfShame events={events} entities={entities} />

        <ProductGrid products={products} brand={ranking.brand} />
      </div>
    </>
  );
}
