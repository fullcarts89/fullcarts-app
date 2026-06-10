import SiteNav from "@/components/SiteNav";
import SubmissionForm from "./_components/SubmissionForm";
import styles from "./styles.module.css";

export const metadata = {
  title: "Submit a shrinkflation event",
  description:
    "Spotted a product that shrank? Put it on the record. Submit the brand, the old and new size, and your evidence — it enters the same review queue our scrapers feed.",
  alternates: { canonical: "/submit" },
  openGraph: {
    title: "Submit a shrinkflation event · FullCarts",
    description:
      "Report a product downsizing to FullCarts. Submissions are reviewed and, if they hold up, published to the public record.",
    type: "website",
    url: "/submit",
    siteName: "FullCarts",
  },
  twitter: {
    card: "summary",
    title: "Submit a shrinkflation event · FullCarts",
    description:
      "Report a product downsizing to FullCarts' public, evidence-based record.",
  },
};

export default function SubmitPage() {
  return (
    <>
      <SiteNav />
      <main id="main-content" className={styles.page}>
        <header className={styles.hero}>
          <div className={styles.eyebrow}>Community submission</div>
          <h1>Spotted a shrink? Put it on the record.</h1>
          <p>
            FullCarts is a public, evidence-based record of consumer-product
            shrinkflation. If you&apos;ve caught a product that quietly got
            smaller, tell us what changed — your submission enters the same
            review queue our scrapers feed, and we publish it as an event if it
            holds up.
          </p>
        </header>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>What makes a strong submission</h2>
          </div>
          <ul className={styles.checklist}>
            <li>
              The old size and the new size, with units — e.g. 200g → 180g.
            </li>
            <li>
              A note on the price: a same-price shrink is the clearest case.
            </li>
            <li>
              A link to evidence — a Reddit post, a news article, a retailer
              page, or a photo of the old and new packaging side by side.
            </li>
            <li>
              The brand and product name as they appear on the package.
            </li>
          </ul>
        </section>

        <section className={styles.block}>
          <div className={styles["section-head"]}>
            <h2>Submit an event</h2>
          </div>
          <p className={styles["section-lede"]}>
            Brand and product are required; everything else helps us verify
            faster. Nothing is published until a human reviews it.
          </p>
          <div className={styles.card}>
            <div className={styles["card-eyebrow"]}>Event submission</div>
            <SubmissionForm />
            <div className={styles["card-meta"]}>
              Prefer email? Send details to{" "}
              <a
                href="mailto:fullcartsinfo@gmail.com"
                className={styles["card-link"]}
              >
                fullcartsinfo@gmail.com
              </a>{" "}
              instead — both paths land in the same queue.
            </div>
          </div>
        </section>
      </main>
    </>
  );
}
