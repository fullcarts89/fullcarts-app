"use client";

// Global error boundary. Catches unhandled exceptions in server or
// client components and shows a recovery UI instead of a blank page.
// Keeps the user on-site with clear paths back to the indexes.

import { useEffect } from "react";
import Link from "next/link";
import styles from "./error.module.css";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Surface the digest in console so we can correlate Vercel logs to
    // user-reported issues; no third-party error tracker wired up yet.
    if (process.env.NODE_ENV !== "production") {
      console.error("FullCarts route error:", error);
    }
  }, [error]);

  return (
    <div className={styles.wrap}>
      <div className={styles.eyebrow}>Something broke</div>
      <h1 className={styles.heading}>
        We couldn&rsquo;t finish loading this page.
      </h1>
      <p className={styles.body}>
        FullCarts hit an unexpected error. The team is notified
        automatically and most pages recover on a retry. You can try
        again, head back to the brand directory, or browse the macro
        insights while we sort it out.
      </p>
      {error.digest && (
        <div className={styles.digest}>Reference · {error.digest}</div>
      )}
      <div className={styles.actions}>
        <button onClick={reset} className={styles.primary} type="button">
          Try again
        </button>
        <Link href="/brands" className={styles.secondary}>
          Browse brands
        </Link>
        <Link href="/insights" className={styles.secondary}>
          See insights
        </Link>
      </div>
    </div>
  );
}
