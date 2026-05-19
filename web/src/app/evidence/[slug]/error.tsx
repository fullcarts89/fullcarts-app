"use client";

// Route-segment error boundary for /evidence/[slug]. Catches Supabase
// hiccups (the soft-error path in page.tsx still exists, but this
// boundary covers any unhandled exception from the route — e.g. a
// transient network drop during the claims query).
//
// Surfaces a retry button (reset()) and a path back into the catalog.

import { useEffect } from "react";
import Link from "next/link";
import SiteNav from "@/components/SiteNav";
import styles from "./styles.module.css";

export default function EvidenceError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    if (process.env.NODE_ENV !== "production") {
      console.error("Evidence channel error:", error);
    }
  }, [error]);

  return (
    <>
      <SiteNav />
      <main id="main-content" className={styles.container}>
        <div className={styles.breadcrumb}>
          <Link href="/">Home</Link>
          <span className={styles.sep}>/</span>
          <span className={styles.current}>Evidence channel</span>
        </div>
        <div className={styles.error}>
          <p style={{ marginBottom: 16 }}>
            We couldn&rsquo;t load evidence for this channel right now.
          </p>
          {error.digest && (
            <p style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-tertiary)", marginBottom: 16 }}>
              Reference · {error.digest}
            </p>
          )}
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <button
              type="button"
              onClick={reset}
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 12,
                textTransform: "uppercase",
                letterSpacing: "0.1em",
                padding: "10px 16px",
                border: "1px solid var(--red-base)",
                background: "var(--red-base)",
                color: "#fff",
                cursor: "pointer",
              }}
            >
              Try again
            </button>
            <Link
              href="/"
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 12,
                textTransform: "uppercase",
                letterSpacing: "0.1em",
                padding: "10px 16px",
                border: "1px solid var(--border-medium)",
                color: "var(--text-primary)",
                textDecoration: "none",
              }}
            >
              Back to homepage
            </Link>
          </div>
        </div>
      </main>
    </>
  );
}
