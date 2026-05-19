// Public RSS 2.0 feed of recent shrinkflation events. One <item> per
// published_changes row (most recent 50, dedup-friendly because the view
// is already collapsed by entity+size). Cached server-side (revalidate
// every hour) so the route stays cheap even under feed-reader polling.
//
// Each item links to the public product scorecard so journalists landing
// from a feed reader get the citation page, not a raw event.
import { createAdminClient } from "@/lib/supabase/admin";

export const revalidate = 3600;

const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://fullcarts.org";
const FEED_LIMIT = 50;

interface FeedRow {
  id: string;
  entity_id: string | null;
  brand: string | null;
  product_name: string | null;
  size_before: string | number | null;
  size_after: string | number | null;
  size_unit: string | null;
  size_delta_pct: number | null;
  observed_date: string | null;
  published_at: string | null;
  evidence_count: number | null;
}

function xmlEscape(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function rfc822(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toUTCString();
}

function titleFor(r: FeedRow): string {
  const brand = r.brand?.trim() || "Unknown brand";
  const rawName = r.product_name?.trim() || "product";
  // De-dup brand when product_name already leads with it (extractor
  // often produces "Cadbury Favourites" for brand "Cadbury").
  const name = rawName.toLowerCase().startsWith(brand.toLowerCase())
    ? rawName.slice(brand.length).trim() || rawName
    : `${brand} ${rawName}`;
  const headline = name.toLowerCase().startsWith(brand.toLowerCase())
    ? name
    : `${brand} ${name}`;
  const unit = (r.size_unit ?? "").trim();
  const before = r.size_before != null ? `${r.size_before}${unit}` : "";
  const after = r.size_after != null ? `${r.size_after}${unit}` : "";
  if (before && after) {
    return `${headline} shrank ${before} → ${after}`;
  }
  return `${headline} documented`;
}

function descFor(r: FeedRow): string {
  const parts: string[] = [];
  if (r.size_delta_pct != null) {
    const pct = Math.abs(r.size_delta_pct).toFixed(1);
    parts.push(`${pct}% smaller`);
  }
  if (r.evidence_count && r.evidence_count > 1) {
    parts.push(`${r.evidence_count} sources`);
  }
  if (r.observed_date) parts.push(`observed ${r.observed_date}`);
  return parts.join(" · ") || "Shrinkflation event documented by FullCarts.";
}

function linkFor(r: FeedRow): string {
  if (r.entity_id) return `${SITE_URL}/products/${r.entity_id}`;
  if (r.brand) {
    return `${SITE_URL}/brands/${encodeURIComponent(r.brand.toLowerCase())}`;
  }
  return SITE_URL;
}

export async function GET(): Promise<Response> {
  const sb = createAdminClient();
  const { data, error } = await sb
    .from("published_changes")
    .select(
      "id, entity_id, brand, product_name, size_before, size_after, size_unit, size_delta_pct, observed_date, published_at, evidence_count",
    )
    .eq("is_retracted", false)
    .eq("change_type", "shrinkflation")
    .not("brand", "is", null)
    .order("published_at", { ascending: false, nullsFirst: false })
    .limit(FEED_LIMIT);

  if (error) {
    return new Response(`Feed unavailable: ${error.message}`, { status: 500 });
  }

  const rows = (data ?? []) as FeedRow[];
  const lastBuild = rfc822(rows[0]?.published_at ?? new Date().toISOString());

  const items = rows
    .map((r) => {
      const title = xmlEscape(titleFor(r));
      const link = xmlEscape(linkFor(r));
      const desc = xmlEscape(descFor(r));
      const pubDate = rfc822(r.published_at || r.observed_date);
      const guid = xmlEscape(`${SITE_URL}/events/${r.id}`);
      return `    <item>
      <title>${title}</title>
      <link>${link}</link>
      <guid isPermaLink="false">${guid}</guid>
      ${pubDate ? `<pubDate>${pubDate}</pubDate>` : ""}
      <description>${desc}</description>
    </item>`;
    })
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>FullCarts — Documented Shrinkflation</title>
    <link>${SITE_URL}</link>
    <atom:link href="${SITE_URL}/rss.xml" rel="self" type="application/rss+xml" />
    <description>Recent shrinkflation events documented and cited by FullCarts.</description>
    <language>en-us</language>
    <lastBuildDate>${lastBuild}</lastBuildDate>
${items}
  </channel>
</rss>
`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
      "Cache-Control": "public, max-age=3600, s-maxage=3600",
    },
  });
}
