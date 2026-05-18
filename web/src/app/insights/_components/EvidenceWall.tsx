// Server component. Renders claims that admins have manually tagged
// "Spot the Difference" via /admin/claims. The image comes from the
// claim's image_storage_path (Reddit-archived front photo, usually a
// side-by-side comparison). before/after sizes come straight off the
// claim row.
import styles from "../styles.module.css";
import { num } from "../lib";
import type { TaggedClaim } from "../types";

interface Props {
  rows: TaggedClaim[];
}

const STORAGE_BUCKET_URL =
  (process.env.NEXT_PUBLIC_SUPABASE_URL || "") +
  "/storage/v1/object/public/claim-images/";

function claimImageUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  return STORAGE_BUCKET_URL + path;
}

export default function EvidenceWall({ rows }: Props) {
  if (rows.length === 0) {
    return (
      <div className={styles.empty}>
        No claims tagged &ldquo;Spot the Difference&rdquo; yet
      </div>
    );
  }
  return (
    <div className={styles["wall-grid"]}>
      {rows.map((r) => {
        const img = claimImageUrl(r.image_storage_path) || r.source_image || null;
        const oldSize = num(r.old_size);
        const newSize = num(r.new_size);
        const unit = r.new_size_unit || r.old_size_unit || "";
        const hasSizes = oldSize > 0 && newSize > 0;
        const deltaPct = hasSizes ? ((newSize - oldSize) / oldSize) * 100 : 0;
        return (
          <a
            key={r.id}
            className={styles["wall-card"]}
            href={r.source_url || "#"}
            target={r.source_url ? "_blank" : undefined}
            rel={r.source_url ? "noopener noreferrer" : undefined}
          >
            <div className={styles["wall-img"]}>
              {img && (
                <img src={img} alt={r.product_name || "Spot the difference"} loading="lazy" />
              )}
              {hasSizes && deltaPct < 0 && (
                <span className={styles["ps-label"]}>{deltaPct.toFixed(0)}%</span>
              )}
              {hasSizes && (
                <>
                  <div className={styles["ps-side"]}>
                    <div className={styles["ps-tag"]}>Before</div>
                    <div className={styles["ps-size"]}>
                      {oldSize}
                      {r.old_size_unit || unit}
                    </div>
                  </div>
                  <div className={`${styles["ps-side"]} ${styles.after}`}>
                    <div className={styles["ps-tag"]}>After</div>
                    <div className={styles["ps-size"]}>
                      {newSize}
                      {r.new_size_unit || unit}
                    </div>
                  </div>
                </>
              )}
            </div>
            <div className={styles["wall-body"]}>
              <div className={styles["wall-product"]}>
                {r.product_name || "Documented case"}
              </div>
              {r.brand && (
                <div className={styles["wall-brand"]}>{r.brand}</div>
              )}
              <div className={styles["wall-signal"]}>Spot the difference</div>
            </div>
          </a>
        );
      })}
    </div>
  );
}
