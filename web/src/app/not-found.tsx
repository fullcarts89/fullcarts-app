// Global 404. Triggered by notFound() in any route or unmatched URLs.
// Mirrors the design of the global error page; offers clear paths
// back into the site rather than a dead end.

import Link from "next/link";
import SiteNav from "@/components/SiteNav";
import styles from "./error.module.css";

export const metadata = {
  title: "Page not found",
  description:
    "The brand, product, or page you're looking for isn't in the FullCarts catalog yet.",
  robots: { index: false, follow: true },
};

export default function NotFound() {
  return (
    <>
      <SiteNav />
      <main id="main-content" className={styles.wrap}>
        <div className={styles.eyebrow}>404 · Not found</div>
        <h1 className={styles.heading}>
          We don&rsquo;t have a page for that one.
        </h1>
        <p className={styles.body}>
          The brand, product, or evidence channel you tried to open
          isn&rsquo;t in our catalog. Either the URL is mistyped, the
          item was retracted, or we haven&rsquo;t documented it yet.
          Start from the directory and search for what you&rsquo;re
          looking for.
        </p>
        <div className={styles.actions}>
          <Link href="/brands" className={styles.primary}>
            Browse all brands
          </Link>
          <Link href="/products" className={styles.secondary}>
            Browse products
          </Link>
          <Link href="/" className={styles.secondary}>
            Back to homepage
          </Link>
        </div>
      </main>
    </>
  );
}
