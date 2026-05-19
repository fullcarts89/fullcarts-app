// Global fallback shown during ISR misses / first-render data fetches.
// Deliberately tiny — most public pages cache server-side, so this
// only appears on cold paths (cache miss + brand/product not in the
// generateStaticParams set).
import styles from "./loading.module.css";

export default function Loading() {
  return (
    <div className={styles.wrap} aria-live="polite" aria-busy="true">
      <div className={styles.spinner} aria-hidden="true" />
      <div className={styles.label}>Loading FullCarts…</div>
    </div>
  );
}
