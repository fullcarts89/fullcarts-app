import { createAdminClient } from "@/lib/supabase/admin";
import BrandIndex from "./_components/BrandIndex";
import type { BrandIndexRow, RankedBrand } from "./types";
import styles from "./styles.module.css";

// ISR: regenerate at most once per hour.
export const revalidate = 3600;

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

export default async function BrandsPage() {
  const brands = await loadAllBrands();

  // Hero counters
  const totalEvents = brands.reduce(
    (s, b) => s + b.shrinkflation_events,
    0,
  );
  const totalProducts = brands.reduce((s, b) => s + b.product_count, 0);

  return (
    <>
      <div className={styles["bp-grid"]} />
      <nav className={styles.nav}>
        <div className={styles["nav-inner"]}>
          <a href="/" className={styles.logo}>
            Full<span>Carts</span>
          </a>
          <div className={styles["nav-links"]}>
            <a href="/brands" className="active">
              Brands
            </a>
            <a href="/products" className="stub" title="Coming in Phase B">
              Products
            </a>
            <a href="/insights" className="stub" title="Coming in Phase C">
              Insights
            </a>
            <a href="/about" className="stub" title="Coming in Phase C">
              About
            </a>
          </div>
        </div>
      </nav>

      <div className={styles.container}>
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

        <BrandIndex brands={brands} />
      </div>
    </>
  );
}
