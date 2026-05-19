import Link from "next/link";
import { loadHomeData, brandHref } from "./_lib/home-data";
import { findChannelByTag } from "./_lib/evidence-tags";
import SiteNav from "@/components/SiteNav";
import SafeImage from "./_components/SafeImage";
import styles from "./home.module.css";

// ISR: regenerate at most once per hour.
export const revalidate = 3600;

function fmt(n: number): string {
  return n.toLocaleString();
}

function isoDay(s: string): string {
  return (s || "").slice(0, 10);
}

export default async function Home() {
  const data = await loadHomeData();

  return (
    <>
      <SiteNav />
      <main id="main-content" className={styles.container}>
        {/* HERO */}
        <header className={styles.hero}>
          <div>
            <div className={styles["hero-mark"]}>Live · Updated Daily</div>
            <h1>
              Look it up.
              <br />
              We have receipts.
            </h1>
            <p className={styles["hero-mission"]}>
              <strong>FullCarts</strong> is a public database of every
              shrinkflation event we can verify with a real source.
              We&rsquo;re not guessing — we&rsquo;re citing.
            </p>
            <form action="/brands" method="get" className={styles["search-wrap"]} role="search">
              <label htmlFor="hero-search" className={styles["sr-only"]}>
                Search FullCarts brands
              </label>
              <input
                id="hero-search"
                name="q"
                type="search"
                placeholder={`Did your favorite product shrink? Search ${fmt(data.counters.products)}+ products`}
                autoComplete="off"
                aria-describedby="hero-search-hint"
              />
              <span className={styles["search-icon"]} aria-hidden="true">⌕</span>
            </form>
            <div id="hero-search-hint" className={styles["search-hint"]}>
              Try &ldquo;Cadbury&rdquo;, &ldquo;Pringles&rdquo;, &ldquo;Charmin&rdquo;
              · {fmt(data.counters.brands)} brands tracked
            </div>
            <div className={styles["counter-strip"]}>
              <div className={styles.ctr}>
                <div className={styles["ctr-val"]}>{fmt(data.counters.events)}</div>
                <div className={styles["ctr-lbl"]}>Documented events</div>
              </div>
              <div className={styles.ctr}>
                <div className={styles["ctr-val"]}>{fmt(data.counters.brands)}</div>
                <div className={styles["ctr-lbl"]}>Brands tracked</div>
              </div>
              <div className={styles.ctr}>
                <div className={styles["ctr-val"]}>{fmt(data.counters.products)}</div>
                <div className={styles["ctr-lbl"]}>Products monitored</div>
              </div>
              <div className={styles.ctr}>
                <div className={styles["ctr-val"]}>
                  {fmt(data.counters.bls_downsizings)}
                </div>
                <div className={styles["ctr-lbl"]}>
                  BLS-confirmed downsizings since 2015
                </div>
              </div>
            </div>
          </div>

          {/* JUST DOCUMENTED sidecar */}
          {data.just_doc && (
            <a
              href={
                data.just_doc.entity_id
                  ? `/products/${data.just_doc.entity_id}`
                  : brandHref(data.just_doc.brand)
              }
              className={styles["just-doc"]}
            >
              <div className={styles["just-doc-tag"]}>
                Just documented · {isoDay(data.just_doc.observed_date)}
              </div>
              <div className={styles["just-doc-img"]}>
                <SafeImage
                  src={data.just_doc.product_image_url}
                  alt={`${data.just_doc.brand} ${data.just_doc.product_name} package`}
                  fill
                  priority
                  sizes="(min-width: 960px) 400px, 100vw"
                />
              </div>
              <div className={styles["just-doc-body"]}>
                <div className={styles["just-doc-brand"]}>
                  {data.just_doc.brand}
                  {data.just_doc.product_category &&
                    ` · ${data.just_doc.product_category}`}
                </div>
                <div className={styles["just-doc-name"]}>
                  {data.just_doc.product_name}
                </div>
                <div className={styles["just-doc-stat"]}>
                  <span className={styles["just-doc-delta"]}>
                    {data.just_doc.size_delta_pct.toFixed(1)}%
                  </span>
                  <span className={styles["just-doc-sizes"]}>
                    {data.just_doc.size_before}
                    {data.just_doc.size_unit} → {data.just_doc.size_after}
                    {data.just_doc.size_unit}
                  </span>
                </div>
              </div>
              <div className={styles["just-doc-foot"]}>
                <span>See evidence →</span>
              </div>
            </a>
          )}
        </header>

        {/* METHODOLOGY */}
        <section className={styles.methodology}>
          <div className={styles["meth-head"]}>
            <span className={styles["meth-eyebrow"]}>How we know</span>
            <h2>Every event is backed by at least one verifiable source.</h2>
          </div>
          <div className={styles["meth-body"]}>
            We ingest from public sources — Reddit, news outlets,
            OpenFoodFacts, Kroger, USDA, and BLS — extract claims with AI,
            then a human reviewer approves each one before it goes live.
            Government data and consumer reporting back the macro story.
            <div className={styles["meth-sources"]}>
              <span className={styles["meth-src"]}>Reddit r/shrinkflation</span>
              <span className={styles["meth-src"]}>News (GDELT)</span>
              <span className={styles["meth-src"]}>OpenFoodFacts</span>
              <span className={styles["meth-src"]}>Kroger API</span>
              <span className={styles["meth-src"]}>USDA FDC</span>
              <span className={styles["meth-src"]}>BLS</span>
              <span className={styles["meth-src"]}>FRED CPI</span>
              <span className={styles["meth-src"]}>Consumer Reports</span>
              <span className={styles["meth-src"]}>Wikidata</span>
            </div>
            <Link className={styles["meth-cta"]} href="/about">
              Read the full methodology <span className={styles.arrow}>→</span>
            </Link>
          </div>
        </section>

        {/* BRAND OF THE WEEK */}
        {data.brand_of_week && (
          <section className={`${styles.block}`}>
            <div className={styles["section-head"]}>
              <h2>Brand of the week</h2>
              <div className={styles.meta}>
                Rotated by most-cited event in the last 14 days
              </div>
            </div>
            <a
              className={styles.botw}
              href={brandHref(data.brand_of_week.brand)}
            >
              <div className={styles["botw-img"]}>
                {data.brand_of_week.thumb && (
                  <SafeImage
                    src={data.brand_of_week.thumb}
                    alt={`${data.brand_of_week.brand} product photo`}
                    fill
                    sizes="(min-width: 1024px) 600px, 100vw"
                  />
                )}
              </div>
              <div className={styles["botw-body"]}>
                <span className={styles["botw-eyebrow"]}>
                  Top of mind this week
                </span>
                <h3>{data.brand_of_week.brand}</h3>
                <p className={styles["botw-reason"]}>
                  {data.brand_of_week.reason}
                </p>
                <div className={styles["botw-stats"]}>
                  <div className={styles["botw-stat"]}>
                    <span className={styles.v}>
                      {data.brand_of_week.total_events}
                    </span>
                    <span className={styles.l}>total events</span>
                  </div>
                  <div className={styles["botw-stat"]}>
                    <span className={styles.v}>
                      {data.brand_of_week.product_count}
                    </span>
                    <span className={styles.l}>products tracked</span>
                  </div>
                  <div className={styles["botw-stat"]}>
                    <span className={`${styles.v} ${styles["v-delta"]}`}>
                      {data.brand_of_week.avg_shrink_per_event.toFixed(1)}%
                    </span>
                    <span className={styles.l}>avg shrinkage</span>
                  </div>
                </div>
                <span className={styles["botw-cta"]}>
                  See the full scorecard <span className={styles.arrow}>→</span>
                </span>
              </div>
            </a>
          </section>
        )}

        {/* MOST ACTIVE THIS MONTH */}
        {data.most_active.length > 0 && (
          <section className={styles.block}>
            <div className={styles["section-head"]}>
              <h2>Most active this month</h2>
              <div className={styles.meta}>
                <Link href="/brands">See all {fmt(data.counters.brands)} brands →</Link>
              </div>
            </div>
            <div className={styles["active-grid"]}>
              {data.most_active.map((b, i) => (
                <a
                  key={b.brand}
                  className={styles["active-card"]}
                  href={brandHref(b.brand)}
                >
                  <span className={styles["active-rank"]}>
                    #{i + 1} this month
                  </span>
                  <span className={styles["active-brand"]}>{b.brand}</span>
                  <span className={styles["active-recent"]}>
                    {b.recent_events} new event{b.recent_events === 1 ? "" : "s"}
                  </span>
                  <span className={styles["active-foot"]}>
                    {b.total_events} total · {b.product_count} product
                    {b.product_count === 1 ? "" : "s"}
                  </span>
                </a>
              ))}
            </div>
          </section>
        )}

        {/* RECENT BIGGEST SHRINKS */}
        {data.recent_shrinks.length > 0 && (
          <section className={styles.block}>
            <div className={styles["section-head"]}>
              <h2>Recent biggest shrinks</h2>
              <div className={styles.meta}>
                Top {data.recent_shrinks.length} from the last 180 days · sorted
                by % drop
              </div>
            </div>
            <div className={styles["recent-grid"]}>
              {data.recent_shrinks.map((e, i) => (
                <a
                  key={`${e.brand}-${i}`}
                  className={styles["rb-card"]}
                  href={
                    e.entity_id ? `/products/${e.entity_id}` : brandHref(e.brand)
                  }
                >
                  <div className={styles["rb-img"]}>
                    <SafeImage
                      src={e.product_image_url}
                      alt={`${e.brand} ${e.product_name} package`}
                      fill
                      sizes="(min-width: 1280px) 220px, (min-width: 640px) 33vw, 50vw"
                    />
                  </div>
                  <div className={styles["rb-body"]}>
                    <span className={styles["rb-brand"]}>
                      {e.brand}
                      {e.product_category && ` · ${e.product_category}`}
                    </span>
                    <span className={styles["rb-name"]}>{e.product_name}</span>
                    <div className={styles["rb-stat"]}>
                      <span className={styles["rb-delta"]}>
                        {e.size_delta_pct.toFixed(1)}%
                      </span>
                      <span className={styles["rb-sizes"]}>
                        {e.size_before}
                        {e.size_unit} → {e.size_after}
                        {e.size_unit}
                      </span>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </section>
        )}

        {/* BEYOND SIZE — tag-driven evidence channels */}
        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Beyond size shrinks</h2>
            <div className={styles.meta}>
              Shrinkflation is one signal · here&rsquo;s the rest of what we tag
            </div>
          </div>
          <div className={styles["tag-grid"]}>
            {data.tags.map((t) => {
              const channel = findChannelByTag(t.tag);
              if (!channel) return null;
              return (
                <a
                  key={t.tag}
                  className={styles["tag-card"]}
                  href={`/evidence/${channel.slug}`}
                >
                  <div className={styles["tag-card-head"]}>
                    <span className={styles["tag-card-name"]}>{t.tag}</span>
                    <span className={styles["tag-card-count"]}>{t.count.toLocaleString()}</span>
                  </div>
                  <div className={styles["tag-card-desc"]}>{channel.desc}</div>
                  <span className={styles["tag-card-cta"]}>Browse claims →</span>
                </a>
              );
            })}
          </div>
        </section>
      </main>

      <footer className={styles.footer}>
        <div className={styles["footer-inner"]}>
          <div className={styles["foot-col"]}>
            <Link href="/" className={styles.logo}>
              Full<span>Carts</span>
            </Link>
            <p className={styles["foot-mission"]}>
              A public database of shrinkflation events, sourced and verified.
            </p>
          </div>
          <div className={styles["foot-col"]}>
            <h2 className={styles["foot-h"]}>Browse</h2>
            <ul>
              <li><Link href="/brands">All brands</Link></li>
              <li><Link href="/products">Products</Link></li>
              <li><Link href="/insights">Insights</Link></li>
            </ul>
          </div>
          <div className={styles["foot-col"]}>
            <h2 className={styles["foot-h"]}>About</h2>
            <ul>
              <li><Link href="/about">Methodology</Link></li>
              <li><Link href="/about#sources">Sources</Link></li>
              <li><Link href="/about#contact">Submit a tip</Link></li>
            </ul>
          </div>
          <div className={styles["foot-col"]}>
            <h2 className={styles["foot-h"]}>Follow</h2>
            <ul>
              <li>
                <a href="/rss.xml">
                  RSS feed
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className={styles["foot-credit"]}>
          <Link href="/" className={styles["logo-mini"]}>
            Full<span>Carts</span>
          </Link>
          <span>Updated daily · ISR cache 1h</span>
        </div>
      </footer>
    </>
  );
}
