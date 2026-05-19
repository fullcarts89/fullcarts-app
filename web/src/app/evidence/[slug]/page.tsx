// /evidence/[slug] — landing page for one evidence channel (So Smol,
// Slack Fill, Spot the Difference, Skimpflation, Paper Thin, Not as
// Advertised, Stretchflation).
//
// Reads claims with the channel's tag (matched OR evidence-only),
// sorted image-first then most-recent. Each card prefers a link to
// the matched product scorecard (citation-friendly); falls back to
// the external source URL for unmatched evidence.
//
// Slug → tag mapping is the canonical registry at
// `web/src/app/_lib/evidence-tags.ts`. Adding a new channel only
// requires touching that file.

import { notFound } from "next/navigation";
import Link from "next/link";
import { createAdminClient } from "@/lib/supabase/admin";
import SiteNav from "@/components/SiteNav";
import SafeImage from "../../_components/SafeImage";
import {
  EVIDENCE_CHANNELS,
  findChannelBySlug,
} from "../../_lib/evidence-tags";
import styles from "./styles.module.css";

// ISR: regenerate at most once per hour.
export const revalidate = 3600;

const PAGE_SIZE = 120;
const STORAGE_BUCKET_URL =
  (process.env.NEXT_PUBLIC_SUPABASE_URL || "") +
  "/storage/v1/object/public/claim-images/";

function claimImageUrl(path: string | null): string | null {
  if (!path) return null;
  return STORAGE_BUCKET_URL + path;
}

interface EvidenceRow {
  id: string;
  brand: string | null;
  product_name: string | null;
  category: string | null;
  old_size: string | number | null;
  old_size_unit: string | null;
  new_size: string | number | null;
  new_size_unit: string | null;
  change_description: string | null;
  observed_date: string | null;
  image_storage_path: string | null;
  matched_entity_id: string | null;
  raw_items: { source_url: string | null; raw_payload: Record<string, unknown> | null } | null;
}

interface Card {
  id: string;
  brand: string;
  product: string;
  description: string | null;
  date: string;
  image: string | null;
  primaryHref: string;
  sourceHref: string | null;
  sourceLabel: string;
  hasMatchedProduct: boolean;
}

function isoDay(s: string | null | undefined): string {
  return (s ?? "").slice(0, 10);
}

function domainOf(url: string | null | undefined): string {
  if (!url) return "";
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

function sourceImageFromPayload(payload: Record<string, unknown> | null | undefined): string | null {
  if (!payload || typeof payload !== "object") return null;
  const candidate =
    (payload as { socialimage?: unknown }).socialimage ??
    (payload as { image?: unknown }).image ??
    (payload as { thumbnail?: unknown }).thumbnail;
  return typeof candidate === "string" && candidate.length > 0 ? candidate : null;
}

function buildCard(row: EvidenceRow): Card {
  const image =
    claimImageUrl(row.image_storage_path) ||
    sourceImageFromPayload(row.raw_items?.raw_payload);
  const sourceUrl = row.raw_items?.source_url || null;
  const primaryHref = row.matched_entity_id
    ? `/products/${row.matched_entity_id}`
    : sourceUrl || (row.brand
        ? `/brands/${encodeURIComponent(row.brand.toLowerCase())}`
        : "/");
  return {
    id: row.id,
    brand: row.brand?.trim() || "Unknown brand",
    product: row.product_name?.trim() || "Documented case",
    description: row.change_description?.trim() || null,
    date: isoDay(row.observed_date),
    image,
    primaryHref,
    sourceHref: sourceUrl,
    sourceLabel: domainOf(sourceUrl) || "View source",
    hasMatchedProduct: !!row.matched_entity_id,
  };
}

export function generateStaticParams() {
  return EVIDENCE_CHANNELS.map((c) => ({ slug: c.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const channel = findChannelBySlug(slug);
  if (!channel) {
    return {
      title: "Evidence channel",
      robots: { index: false, follow: true },
    };
  }
  const title = `${channel.title} — Evidence channel`;
  return {
    title,
    description: channel.intro,
    alternates: { canonical: `/evidence/${channel.slug}` },
    openGraph: {
      title: `${title} · FullCarts`,
      description: channel.intro,
      type: "article",
      url: `/evidence/${channel.slug}`,
      siteName: "FullCarts",
    },
    twitter: {
      card: "summary_large_image",
      title: `${title} · FullCarts`,
      description: channel.intro,
    },
  };
}

export default async function EvidenceChannelPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const channel = findChannelBySlug(slug);
  if (!channel) notFound();

  const sb = createAdminClient();
  // Pull claims tagged with this channel. Join raw_items to lift the
  // source URL + payload (used for the fallback image when no archived
  // claim photo exists). PostgREST `cs.{...}` is JSONB contains, the
  // correct operator for evidence_tags as a tag array.
  const { data, error } = await sb
    .from("claims")
    .select(
      "id, brand, product_name, category, old_size, old_size_unit, new_size, new_size_unit, change_description, observed_date, image_storage_path, matched_entity_id, raw_items ( source_url, raw_payload )",
    )
    .contains("evidence_tags", [channel.tag])
    .in("status", ["matched", "evidence", "approved"])
    .order("observed_date", { ascending: false, nullsFirst: false })
    .limit(PAGE_SIZE);

  if (error) {
    // Don't blow up the route; render a soft error so the channel page
    // is still navigable from the homepage even during a Supabase blip.
    return (
      <>
        <SiteNav />
        <main id="main-content" className={styles.container}>
          <div className={styles.error}>
            We couldn&rsquo;t load evidence for this channel right now. Please
            try again in a moment.
          </div>
        </main>
      </>
    );
  }

  const rows = (data ?? []) as unknown as EvidenceRow[];
  const cards = rows.map(buildCard);

  // Image-first sort: with-image cards lead, by-date within each group.
  cards.sort((a, b) => {
    const ai = a.image ? 0 : 1;
    const bi = b.image ? 0 : 1;
    if (ai !== bi) return ai - bi;
    return b.date.localeCompare(a.date);
  });

  const totalCount = cards.length;
  const withImageCount = cards.filter((c) => c.image).length;
  const matchedCount = cards.filter((c) => c.hasMatchedProduct).length;

  return (
    <>
      <SiteNav />
      <main id="main-content" className={styles.container}>
        <div className={styles.breadcrumb}>
          <Link href="/">Home</Link>
          <span className={styles.sep}>/</span>
          <span className={styles.current}>Evidence · {channel.title}</span>
        </div>

        <header className={styles.hero}>
          <div className={styles.eyebrow}>
            <span className={styles.dot} aria-hidden="true">●</span>
            Evidence channel
          </div>
          <h1>{channel.title}</h1>
          <p className={styles.intro}>{channel.intro}</p>
          <div className={styles.stats}>
            <div className={styles.stat}>
              <span className={styles.statVal}>{totalCount}</span>
              <span className={styles.statLbl}>documented</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statVal}>{withImageCount}</span>
              <span className={styles.statLbl}>with photo evidence</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statVal}>{matchedCount}</span>
              <span className={styles.statLbl}>matched to a product</span>
            </div>
          </div>
        </header>

        {cards.length === 0 ? (
          <div className={styles.empty}>
            No claims tagged for this channel yet. As reviewers tag new
            submissions, they&rsquo;ll surface here.
          </div>
        ) : (
          <div className={styles.grid}>
            {cards.map((c) => {
              const cardInner = (
                <>
                  <div className={styles.thumb}>
                    {c.image ? (
                      <SafeImage
                        src={c.image}
                        alt={`${c.brand} ${c.product}`}
                        fill
                        sizes="(min-width: 1024px) 300px, (min-width: 640px) 33vw, 50vw"
                      />
                    ) : (
                      <div className={styles.thumbPlaceholder} aria-hidden="true">
                        {c.brand.slice(0, 1)}
                      </div>
                    )}
                  </div>
                  <div className={styles.body}>
                    <div className={styles.brand}>{c.brand}</div>
                    <div className={styles.product}>{c.product}</div>
                    {c.description && (
                      <p className={styles.desc}>{c.description}</p>
                    )}
                    <div className={styles.meta}>
                      {c.date && <span>{c.date}</span>}
                      {c.hasMatchedProduct && (
                        <span className={styles.tag}>matched</span>
                      )}
                      {!c.hasMatchedProduct && c.sourceHref && (
                        <span className={styles.tag}>{c.sourceLabel}</span>
                      )}
                    </div>
                  </div>
                </>
              );
              return c.hasMatchedProduct ? (
                <Link
                  key={c.id}
                  href={c.primaryHref}
                  className={styles.card}
                >
                  {cardInner}
                </Link>
              ) : (
                <a
                  key={c.id}
                  href={c.primaryHref}
                  className={styles.card}
                  target={c.primaryHref.startsWith("http") ? "_blank" : undefined}
                  rel={
                    c.primaryHref.startsWith("http")
                      ? "noopener noreferrer"
                      : undefined
                  }
                >
                  {cardInner}
                </a>
              );
            })}
          </div>
        )}

        <nav className={styles.channelsNav} aria-label="Other evidence channels">
          <div className={styles.channelsLabel}>Other channels</div>
          <div className={styles.channelsRow}>
            {EVIDENCE_CHANNELS.filter((c) => c.slug !== slug).map((c) => (
              <Link
                key={c.slug}
                href={`/evidence/${c.slug}`}
                className={styles.channelChip}
              >
                {c.title}
              </Link>
            ))}
          </div>
        </nav>
      </main>
    </>
  );
}
