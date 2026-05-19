import { createAdminClient } from "@/lib/supabase/admin";
import SiteNav from "@/components/SiteNav";
import BrandIndex from "./_components/BrandIndex";
import type { BrandIndexRow, RankedBrand } from "./types";
import styles from "./styles.module.css";

// ISR: regenerate at most once per hour.
export const revalidate = 3600;

export const metadata = {
  title: "Brands",
  description:
    "Every brand we're tracking. Severity-tiered, category-filterable, and searchable across 1,000+ brands with documented shrinkflation events.",
  alternates: { canonical: "/brands" },
  openGraph: {
    title: "All brands · FullCarts",
    description:
      "Every brand we're tracking. Severity-tiered, category-filterable, and searchable.",
    type: "website",
    url: "/brands",
    siteName: "FullCarts",
  },
  twitter: {
    card: "summary_large_image",
    title: "All brands · FullCarts",
    description:
      "Every brand we're tracking. Severity-tiered, category-filterable, and searchable.",
  },
};

const PAGE_SIZE = 1000;

async function loadAllBrands(): Promise<RankedBrand[]> {
  // Admin client for build/revalidate; no cookies → page stays SSG-able.
  // All queried data (brand_index view) is public under existing RLS.
  const sb = createAdminClient();

  // brand_index has ~1.2k rows. PostgREST default cap is 1000 rows per
  // request, so paginate via .range() until we get a short page.
  const all: BrandIndexRow[] = [];
  let from = 0;
  while (true) {
    const { data, error } = await sb
      .from("brand_index")
      .select("*")
      .order("shrinkflation_events", { ascending: false })
      .range(from, from + PAGE_SIZE - 1);
    if (error) break;
    const batch = (data ?? []) as BrandIndexRow[];
    if (batch.length === 0) break;
    all.push(...batch);
    if (batch.length < PAGE_SIZE) break;
    from += PAGE_SIZE;
  }

  // Assign canonical rank from the most-events-desc order so the rank
  // badge stays stable when the client re-sorts.
  return all.map((b, i) => ({ ...b, rank: i + 1 }));
}

export default async function BrandsPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const brands = await loadAllBrands();
  const { q } = await searchParams;
  const initialQuery = (q ?? "").trim();

  // Hero counters
  const totalEvents = brands.reduce(
    (s, b) => s + b.shrinkflation_events,
    0,
  );
  const totalProducts = brands.reduce((s, b) => s + b.product_count, 0);

  // CollectionPage JSON-LD — tells search engines this is a directory
  // listing of `brands.length` brand records, each with the canonical
  // /brands/{name} URL. Distinct from the BreadcrumbList we render on
  // /brands/[name].
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://fullcarts.org";
  const collectionJsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: "All brands · FullCarts",
    description: "Every brand we're tracking, with documented shrinkflation events.",
    url: `${siteUrl}/brands`,
    isPartOf: { "@type": "WebSite", name: "FullCarts", url: siteUrl },
    mainEntity: {
      "@type": "ItemList",
      numberOfItems: brands.length,
      itemListElement: brands.slice(0, 100).map((b, i) => ({
        "@type": "ListItem",
        position: i + 1,
        name: b.brand,
        url: `${siteUrl}/brands/${encodeURIComponent(b.brand.toLowerCase())}`,
      })),
    },
  };

  return (
    <>
      <SiteNav />
      <main id="main-content" className={styles.container}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(collectionJsonLd) }}
        />
        <div className={styles.breadcrumb}>
          <span className={styles.current}>All brands</span>
        </div>

        <header className={styles.hero}>
          <h1>Every brand we&rsquo;re tracking.</h1>
          <p className={styles["hero-sub"]}>
            <strong>{brands.length}</strong> brands with{" "}
            <strong>{totalEvents.toLocaleString()}</strong> documented
            shrinkflation events across{" "}
            <strong>{totalProducts.toLocaleString()}</strong> products. Sorted
            by total events by default — click a card for the full brand
            scorecard.
          </p>
        </header>

        <BrandIndex brands={brands} initialQuery={initialQuery} />
      </main>
    </>
  );
}
