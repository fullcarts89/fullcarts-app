import type { NextConfig } from "next";

// Image host allowlist. Covers the controlled sources where
// product_entities.image_url and brand_index.thumbnail get backfilled
// from (OFF, Walmart, Kroger product CDNs, Supabase Storage for
// archived claim images), plus the existing Reddit / Imgur hosts used
// by the claim pipeline. Arbitrary GDELT social-card images stay on
// raw <img> tags — they come from any news domain on the planet and
// would require a wildcard remotePattern that defeats the security
// model of next/image.
const nextConfig: NextConfig = {
  images: {
    // Vercel's image optimizer (`/_next/image`) returns HTTP 402
    // OPTIMIZED_IMAGE_REQUEST_PAYMENT_REQUIRED once the plan's
    // optimization quota is exhausted, which blanks every on-site image.
    // Our product/claim photos are already archived as <=1200px WebP, so
    // the optimizer buys almost nothing — serve sources as-is and skip it.
    // This also lifts the remotePatterns host restriction (the long-tail
    // news socialimages now load through next/image too), so SafeImage's
    // allowlist branch is effectively a no-op.
    unoptimized: true,
    remotePatterns: [
      // Reddit (claim photos, gallery images, previews)
      { hostname: "i.redd.it" },
      { hostname: "i.imgur.com" },
      { hostname: "preview.redd.it" },
      { hostname: "external-preview.redd.it" },
      { hostname: "b.thumbs.redditmedia.com" },
      // Open Food Facts crowdsourced product images
      { hostname: "images.openfoodfacts.org" },
      { hostname: "images.openfoodfacts.net" },
      { hostname: "static.openfoodfacts.org" },
      // Walmart product photos (i5/i6 mirrors)
      { hostname: "i5.walmartimages.com" },
      { hostname: "i6.walmartimages.com" },
      // Kroger product photos
      { hostname: "www.kroger.com" },
      { hostname: "pics.kroger.com" },
      // Supabase Storage — archived claim photos served from our
      // public bucket; subdomain is project-scoped so the wildcard
      // restricts to fullcarts's project ref.
      { hostname: "ntyhbapphnzlariakgrw.supabase.co" },
    ],
  },
};

export default nextConfig;
