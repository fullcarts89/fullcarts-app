// Server component. Renders claims that admins have manually tagged
// "Skimpflation" via the Evidence Wall flow in /admin/claims. Cards
// show the archived claim photo (or news article hero) with a deep
// link to the original source.
//
// (Replaces the earlier USDA-driven nutrition_skimpflation RPC view.
// USDA-detected nutrition diffs will get their own pipeline step
// that creates claims with this tag, so this section stays as the
// single source of truth for skimpflation evidence.)
import styles from "../styles.module.css";
import { isoDay } from "../lib";
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

export default function SkimpflationLeaderboard({ rows }: Props) {
  if (rows.length === 0) {
    return (
      <div className={styles["skimp-card-wrap"]}>
        <div className={styles["skimp-eyebrow"]}>Spotted in the wild</div>
        <div className={styles.empty} style={{ marginTop: 16 }}>
          No skimpflation reports yet — we&rsquo;ll surface them here as
          reviewers confirm the photo evidence.
        </div>
      </div>
    );
  }
  return (
    <div className={styles["skimp-card-wrap"]}>
      <div className={styles["skimp-eyebrow"]}>
        Spotted in the wild · {rows.length} confirmed
      </div>
      <div className={styles["skimp-grid"]}>
        {rows.map((r) => {
          const img = claimImageUrl(r.image_storage_path) || r.source_image || null;
          const entityHref = r.matched_entity_id
            ? `/products/${r.matched_entity_id}`
            : null;
          const sourceHref = r.source_url || null;
          // Primary link: product scorecard when matched; otherwise the
          // source URL. Cite-friendly destinations rank above raw sources.
          const primary = entityHref || sourceHref;
          const body = (
            <>
              {img && (
                <div className={styles["skimp-thumb"]}>
                  <img src={img} alt={r.product_name || "Skimpflation"} loading="lazy" />
                </div>
              )}
              <div className={styles["skimp-body"]}>
                <div className={styles["skimp-product"]}>
                  {r.product_name || "(unnamed product)"}
                </div>
                {r.brand && <div className={styles["skimp-brand"]}>{r.brand}</div>}
                {r.change_description && (
                  <div className={styles["skimp-desc"]}>{r.change_description}</div>
                )}
                <div className={styles["skimp-foot"]}>
                  {r.observed_date && (
                    <span>Observed {isoDay(r.observed_date)}</span>
                  )}
                  {entityHref ? (
                    <span className={styles["skimp-source-link"]}>View product →</span>
                  ) : (
                    sourceHref && (
                      <span className={styles["skimp-source-link"]}>View source ↗</span>
                    )
                  )}
                </div>
              </div>
            </>
          );
          if (!primary) {
            return (
              <div key={r.id} className={styles["skimp-row"]}>
                {body}
              </div>
            );
          }
          const isExternal = primary.startsWith("http");
          return (
            <a
              key={r.id}
              className={styles["skimp-row"]}
              href={primary}
              target={isExternal ? "_blank" : undefined}
              rel={isExternal ? "noopener noreferrer" : undefined}
            >
              {body}
            </a>
          );
        })}
      </div>
    </div>
  );
}
