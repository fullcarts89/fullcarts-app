// Shared "coming soon" stub used by /products, /insights, and /about
// until those routes get their real implementations.
import SiteNav from "@/components/SiteNav";
import styles from "./StubPage.module.css";

export interface StubPageProps {
  /** Breadcrumb label and primary heading. */
  title: string;
  /** "Coming in Phase X" or similar. */
  phase: string;
  /** 1–2 sentence overview shown beneath the title. */
  lede: React.ReactNode;
  /** Bullet items showing what's planned. */
  planned: { eyebrow: string; title: string; desc: string }[];
}

export default function StubPage({ title, phase, lede, planned }: StubPageProps) {
  return (
    <>
      <SiteNav />
      <div className={styles.container}>
        <div className={styles.breadcrumb}>
          <span className={styles.current}>{title}</span>
        </div>
        <div className={styles.tag}>{phase}</div>
        <h1 className={styles.h1}>{title}</h1>
        <p className={styles.lede}>{lede}</p>

        <div className={styles.planned}>
          {planned.map((p, i) => (
            <div key={i} className={styles.row}>
              <span className={styles["row-eyebrow"]}>{p.eyebrow}</span>
              <span className={styles["row-title"]}>{p.title}</span>
              <span className={styles["row-desc"]}>{p.desc}</span>
            </div>
          ))}
        </div>

        <div className={styles["cta-row"]}>
          <a className={styles.cta} href="/brands">
            Browse all brands →
          </a>
          <a className={`${styles.cta} ${styles["cta-secondary"]}`} href="/">
            ← Back home
          </a>
        </div>
      </div>
    </>
  );
}
