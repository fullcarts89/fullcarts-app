// Server component. Renders claims that admins have manually tagged
// "Spot the Difference" via /admin/claims. Card shows the archived
// claim photo (or, for news-sourced claims, the article's social
// image as fallback). Metrics are intentionally absent here — the
// section's job is the visual side-by-side, not the numeric delta.
import styles from "../styles.module.css";
import SafeImage from "../../_components/SafeImage";
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
  // Drop cards that have no image — the section is the visual wall,
  // empty placeholders defeat the purpose. Sources are usually
  // Reddit posts with archived front-photo evidence so most rows
  // have image_storage_path populated; gdelt socialimage covers the
  // rest. A row with neither still earns a card-less mention by
  // virtue of being tagged, but we don't render it.
  const cards = rows
    .map((r) => ({
      row: r,
      img: claimImageUrl(r.image_storage_path) || r.source_image || null,
    }))
    .filter((c) => c.img);

  if (cards.length === 0) {
    return (
      <div className={styles.empty}>
        No side-by-side photos confirmed yet. As reviewers tag visual
        evidence, the wall fills here.
      </div>
    );
  }
  return (
    <div className={styles["wall-grid"]}>
      {cards.map(({ row: r, img }) => {
        // Prefer the product scorecard when matched — gives readers a
        // FullCarts-internal citation page instead of punting them to
        // the original source.
        const entityHref = r.matched_entity_id
          ? `/products/${r.matched_entity_id}`
          : null;
        const primary = entityHref || r.source_url || "#";
        const isExternal = primary.startsWith("http");
        return (
          <a
            key={r.id}
            className={styles["wall-card"]}
            href={primary}
            target={isExternal ? "_blank" : undefined}
            rel={isExternal ? "noopener noreferrer" : undefined}
          >
            <div className={styles["wall-img"]}>
              <SafeImage
                src={img!}
                alt={
                  r.brand && r.product_name
                    ? `${r.brand} ${r.product_name} — side-by-side comparison`
                    : r.product_name || "Spot the difference"
                }
                fill
                sizes="(min-width: 1024px) 280px, (min-width: 640px) 33vw, 50vw"
              />
            </div>
            <div className={styles["wall-body"]}>
              <div className={styles["wall-product"]}>
                {r.product_name || "Documented case"}
              </div>
              {r.brand && <div className={styles["wall-brand"]}>{r.brand}</div>}
            </div>
          </a>
        );
      })}
    </div>
  );
}
