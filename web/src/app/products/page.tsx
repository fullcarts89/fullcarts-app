import { createAdminClient } from "@/lib/supabase/admin";
import SiteNav from "@/components/SiteNav";
import ProductIndex from "./_components/ProductIndex";
import type { ProductIndexRow, RankedProduct } from "./types";
import styles from "./styles.module.css";

// ISR: regenerate at most once per hour. Same cadence as /brands.
export const revalidate = 3600;

const PAGE_SIZE = 1000;

export const metadata = {
  title: "Products",
  description:
    "Every product we're tracking with at least one documented shrinkflation event. Sortable by event count, worst single shrink, average shrink, or A–Z. Filter by category.",
  alternates: { canonical: "/products" },
  openGraph: {
    title: "All products · FullCarts",
    description:
      "Every product we're tracking with at least one documented shrinkflation event.",
    type: "website",
    url: "/products",
    siteName: "FullCarts",
  },
  twitter: {
    card: "summary_large_image",
    title: "All products · FullCarts",
    description:
      "Every product we're tracking with at least one documented shrinkflation event.",
  },
};

async function loadAllProducts(): Promise<RankedProduct[]> {
  const sb = createAdminClient();

  // product_index has a few thousand rows. PostgREST default cap is
  // 1000 rows per request, so paginate via .range() until we get a
  // short page (same pattern as /brands).
  const all: ProductIndexRow[] = [];
  let from = 0;
  while (true) {
    const { data, error } = await sb
      .from("product_index")
      .select("*")
      .order("shrinkflation_events", { ascending: false })
      .range(from, from + PAGE_SIZE - 1);
    if (error) break;
    const batch = (data ?? []) as ProductIndexRow[];
    if (batch.length === 0) break;
    all.push(...batch);
    if (batch.length < PAGE_SIZE) break;
    from += PAGE_SIZE;
  }

  // Canonical rank from most-events-desc order; stays stable when the
  // client re-sorts by another axis.
  return all.map((p, i) => ({ ...p, rank: i + 1 }));
}

export default async function ProductsPage() {
  const products = await loadAllProducts();

  const totalEvents = products.reduce(
    (s, p) => s + p.shrinkflation_events,
    0,
  );
  const brandCount = new Set(products.map((p) => p.brand)).size;

  // CollectionPage JSON-LD — same pattern as /brands. Top 100 by
  // event count are explicitly enumerated for search engines; the
  // long tail is reachable via the sitemap.
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://fullcarts.org";
  const collectionJsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: "All products · FullCarts",
    description: "Every product we're tracking with at least one documented shrinkflation event.",
    url: `${siteUrl}/products`,
    isPartOf: { "@type": "WebSite", name: "FullCarts", url: siteUrl },
    mainEntity: {
      "@type": "ItemList",
      numberOfItems: products.length,
      itemListElement: products.slice(0, 100).map((p, i) => ({
        "@type": "ListItem",
        position: i + 1,
        name: `${p.brand} ${p.canonical_name}`,
        url: `${siteUrl}/products/${p.entity_id}`,
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
          <span className={styles.current}>All products</span>
        </div>

        <header className={styles.hero}>
          <h1>Every product we&rsquo;re tracking.</h1>
          <p className={styles["hero-sub"]}>
            <strong>{products.length.toLocaleString()}</strong> products with{" "}
            <strong>{totalEvents.toLocaleString()}</strong> documented
            shrinkflation events across{" "}
            <strong>{brandCount.toLocaleString()}</strong> brands. Sorted by
            total events by default — click a card for the full product
            scorecard.
          </p>
        </header>

        <ProductIndex products={products} />
      </main>
    </>
  );
}
