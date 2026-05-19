// next/image wrapper that gracefully degrades on unknown hosts.
//
// Why this exists: entity.image_url can come from OFF, Walmart, Kroger,
// Supabase Storage (controlled hosts we whitelist in next.config.ts),
// or from GDELT socialimage fields (any news domain on earth). The
// next/image component crashes the route if the host isn't in
// `images.remotePatterns`, so we sniff the hostname server-side and
// drop to a plain <img> for the unknown long tail.
//
// Optimized path: CLS prevention from explicit width/height (or fill),
// lazy loading, AVIF/WebP conversion, responsive srcsets.
// Fallback path: raw <img> with native loading="lazy" + decoding=async.
import Image from "next/image";

// Mirror of next.config.ts `images.remotePatterns`. Keep in sync if you
// add a new pattern there. Only hostnames are checked — paths aren't.
const ALLOWED_HOSTS = new Set<string>([
  "i.redd.it",
  "i.imgur.com",
  "preview.redd.it",
  "external-preview.redd.it",
  "b.thumbs.redditmedia.com",
  "images.openfoodfacts.org",
  "images.openfoodfacts.net",
  "static.openfoodfacts.org",
  "i5.walmartimages.com",
  "i6.walmartimages.com",
  "www.kroger.com",
  "pics.kroger.com",
  "ntyhbapphnzlariakgrw.supabase.co",
]);

function canOptimize(src: string): boolean {
  if (!src || src.startsWith("/")) return true;
  try {
    return ALLOWED_HOSTS.has(new URL(src).hostname);
  } catch {
    return false;
  }
}

export interface SafeImageProps {
  src: string;
  alt: string;
  /** Explicit pixel dimensions (preferred). Required for non-fill mode. */
  width?: number;
  height?: number;
  /** Set true when the parent has `position: relative` and you want
   *  the image to fill it (use with object-fit: cover in CSS). */
  fill?: boolean;
  /** Responsive sizes string for Image when fill is true. */
  sizes?: string;
  /** className applied to whichever element actually renders. */
  className?: string;
  /** Eager-load for above-the-fold images; defaults to lazy. */
  priority?: boolean;
}

export default function SafeImage({
  src,
  alt,
  width,
  height,
  fill,
  sizes,
  className,
  priority,
}: SafeImageProps) {
  const optimizable = canOptimize(src);

  if (optimizable) {
    if (fill) {
      return (
        <Image
          src={src}
          alt={alt}
          fill
          sizes={sizes || "(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"}
          className={className}
          priority={priority}
          style={{ objectFit: "cover" }}
        />
      );
    }
    return (
      <Image
        src={src}
        alt={alt}
        width={width || 400}
        height={height || 400}
        className={className}
        priority={priority}
        sizes={sizes}
      />
    );
  }

  // Unknown host — degrade to raw <img>. CLS is still prevented by the
  // parent container's aspect-ratio CSS (every grid card on the site
  // wraps thumbnails in an aspect-ratio constrained box).
  return (
    /* eslint-disable-next-line @next/next/no-img-element */
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      loading={priority ? "eager" : "lazy"}
      decoding="async"
    />
  );
}
