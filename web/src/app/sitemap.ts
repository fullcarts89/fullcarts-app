// Dynamic XML sitemap. Lists static routes + every brand/product/evidence
// channel we publish so search engines can crawl the long tail. Cached
// the same hour as the rest of the site (ISR-friendly).
//
// Brand index has ~1.2k rows, product index a few thousand. PostgREST
// caps responses at 1000 rows so we paginate via range() — same pattern
// as /brands and /products.

import type { MetadataRoute } from "next";
import { createAdminClient } from "@/lib/supabase/admin";
import { EVIDENCE_CHANNELS } from "./_lib/evidence-tags";

export const revalidate = 3600;

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://fullcarts.org";
const PAGE_SIZE = 1000;
const HARD_CAP = 50_000; // sitemap protocol limit per file

async function fetchAll<T>(
  sb: ReturnType<typeof createAdminClient>,
  table: string,
  columns: string,
  orderColumn: string,
): Promise<T[]> {
  const out: T[] = [];
  let from = 0;
  while (out.length < HARD_CAP) {
    const { data, error } = await sb
      .from(table)
      .select(columns)
      .order(orderColumn, { ascending: false })
      .range(from, from + PAGE_SIZE - 1);
    if (error || !data || data.length === 0) break;
    out.push(...(data as T[]));
    if (data.length < PAGE_SIZE) break;
    from += PAGE_SIZE;
  }
  return out;
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const now = new Date();
  const sb = createAdminClient();

  const [brands, products] = await Promise.all([
    fetchAll<{ brand: string; last_detected: string | null }>(
      sb,
      "brand_index",
      "brand, last_detected",
      "shrinkflation_events",
    ),
    fetchAll<{ entity_id: string; last_detected: string | null }>(
      sb,
      "product_index",
      "entity_id, last_detected",
      "shrinkflation_events",
    ),
  ]);

  const staticRoutes: MetadataRoute.Sitemap = [
    { url: `${SITE_URL}/`, lastModified: now, changeFrequency: "daily", priority: 1.0 },
    { url: `${SITE_URL}/brands`, lastModified: now, changeFrequency: "daily", priority: 0.9 },
    { url: `${SITE_URL}/products`, lastModified: now, changeFrequency: "daily", priority: 0.9 },
    { url: `${SITE_URL}/insights`, lastModified: now, changeFrequency: "daily", priority: 0.9 },
    { url: `${SITE_URL}/about`, lastModified: now, changeFrequency: "monthly", priority: 0.6 },
  ];

  const evidenceRoutes: MetadataRoute.Sitemap = EVIDENCE_CHANNELS.map((c) => ({
    url: `${SITE_URL}/evidence/${c.slug}`,
    lastModified: now,
    changeFrequency: "weekly",
    priority: 0.7,
  }));

  const brandRoutes: MetadataRoute.Sitemap = brands.map((b) => ({
    url: `${SITE_URL}/brands/${encodeURIComponent(b.brand.toLowerCase())}`,
    lastModified: b.last_detected ? new Date(b.last_detected) : now,
    changeFrequency: "weekly",
    priority: 0.6,
  }));

  const productRoutes: MetadataRoute.Sitemap = products.map((p) => ({
    url: `${SITE_URL}/products/${p.entity_id}`,
    lastModified: p.last_detected ? new Date(p.last_detected) : now,
    changeFrequency: "weekly",
    priority: 0.5,
  }));

  return [
    ...staticRoutes,
    ...evidenceRoutes,
    ...brandRoutes,
    ...productRoutes,
  ].slice(0, HARD_CAP);
}
