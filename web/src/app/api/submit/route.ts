// Public community-submission endpoint.
//
// A submission becomes an ordinary `pending` claim, identical in shape to a
// scraped one. Because `claims.raw_item_id` is NOT NULL (the immutable
// evidence locker), we write TWO rows per submission — exactly like every
// scraper does:
//   1. raw_items  — source_type='community_tip', the evidence anchor
//   2. claims     — status='pending', extractor_version='community-v1'
//
// Provenance is carried by raw_items.source_type='community_tip' (already an
// allowed value in the raw_items_source_type_check constraint), so /admin/claims
// identifies and filters these with its existing source machinery. No new claim
// status, no migration.
//
// Abuse defenses mirror /api/tips: 8 KB body cap, IP hashing, 60 s per-session
// dedup. Submissions are anonymous but gated — nothing is public until an admin
// approves the claim.
import { NextRequest, NextResponse } from "next/server";
import { createHash, randomUUID } from "crypto";
import { createAdminClient } from "@/lib/supabase/admin";

export const dynamic = "force-dynamic";

const SOURCE_TYPE = "community_tip";
const MAX_DESCRIPTION = 4000;
const MAX_FIELD = 200;
const MAX_UNIT = 16;

function clamp(s: unknown, max: number): string {
  if (typeof s !== "string") return "";
  return s.trim().slice(0, max);
}

function toNum(v: unknown): number | null {
  if (typeof v === "number" && isFinite(v)) return v;
  if (typeof v === "string" && v.trim() !== "") {
    const n = Number(v);
    if (isFinite(n)) return n;
  }
  return null;
}

function hashIp(req: NextRequest): string {
  const fwd = req.headers.get("x-forwarded-for") || "";
  const ip = fwd.split(",")[0].trim() || "0.0.0.0";
  return createHash("sha256").update(ip).digest("hex").slice(0, 24);
}

export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    const text = await req.text();
    if (text.length > 8000) {
      return NextResponse.json({ error: "Payload too large" }, { status: 413 });
    }
    body = JSON.parse(text);
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }
  if (!body || typeof body !== "object") {
    return NextResponse.json({ error: "Invalid body" }, { status: 400 });
  }

  const b = body as Record<string, unknown>;
  const brand = clamp(b.brand, MAX_FIELD);
  const product_name = clamp(b.product_name, MAX_FIELD);
  const description = clamp(b.description, MAX_DESCRIPTION);

  if (!brand) {
    return NextResponse.json({ error: "Brand is required" }, { status: 400 });
  }
  if (!product_name) {
    return NextResponse.json({ error: "Product is required" }, { status: 400 });
  }
  if (!description || description.length < 10) {
    return NextResponse.json(
      { error: "Description must be at least 10 characters" },
      { status: 400 },
    );
  }

  const old_size = toNum(b.old_size);
  const new_size = toNum(b.new_size);
  const old_size_unit = clamp(b.old_size_unit, MAX_UNIT) || null;
  const new_size_unit = clamp(b.new_size_unit, MAX_UNIT) || null;
  const old_price = toNum(b.old_price);
  const new_price = toNum(b.new_price);
  const session_id = clamp(b.session_id, 64) || randomUUID();

  // Optional evidence URL — reject obvious junk, don't be exhaustive.
  const evidence_url_raw = clamp(b.evidence_url, MAX_FIELD * 4);
  let evidence_url: string | null = null;
  if (evidence_url_raw) {
    try {
      const u = new URL(evidence_url_raw);
      if (u.protocol === "http:" || u.protocol === "https:") {
        evidence_url = u.toString();
      } else {
        throw new Error("bad protocol");
      }
    } catch {
      return NextResponse.json(
        { error: "Evidence URL must be a valid http(s) URL" },
        { status: 400 },
      );
    }
  }

  const ip_hash = hashIp(req);
  const sb = createAdminClient();

  // De-dup: same session within 60 s → 429, so a double-click can't double-post.
  // We match the session id stored inside the community_tip payload.
  const sixtySecondsAgo = new Date(Date.now() - 60_000).toISOString();
  const { data: recent } = await sb
    .from("raw_items")
    .select("id, captured_at")
    .eq("source_type", SOURCE_TYPE)
    // PostgREST JSONB text filter: raw_payload->>session_id = session_id
    .eq("raw_payload->>session_id", session_id)
    .gte("captured_at", sixtySecondsAgo)
    .limit(1);
  if (recent && recent.length > 0) {
    return NextResponse.json(
      { error: "Slow down — we already received a submission from you in the last minute." },
      { status: 429 },
    );
  }

  // 1. Evidence anchor. source_id is unique per submission so we never collide
  //    with the UNIQUE (source_type, source_id) index. content_hash and
  //    scraper_version are NOT NULL columns and must be supplied.
  const submissionId = randomUUID();
  const rawPayload = {
    kind: "community_submission",
    brand,
    product_name,
    description,
    old_size,
    old_size_unit,
    new_size,
    new_size_unit,
    old_price,
    new_price,
    evidence_url,
    session_id,
    ip_hash,
  };
  const content_hash = createHash("sha256")
    .update(JSON.stringify(rawPayload))
    .digest("hex");

  const { data: rawRow, error: rawErr } = await sb
    .from("raw_items")
    .insert({
      source_type: SOURCE_TYPE,
      source_id: submissionId,
      source_url: evidence_url,
      raw_payload: rawPayload,
      content_hash,
      scraper_version: "community-v1",
    })
    .select("id")
    .single();
  if (rawErr || !rawRow) {
    console.error("submission raw_items insert failed:", rawErr);
    return NextResponse.json(
      { error: "Could not save submission — please try again later." },
      { status: 500 },
    );
  }

  // 2. The claim. status='pending', modest confidence so the auto-approve cron
  //    (threshold 90) never publishes it unreviewed. confidence stays numeric —
  //    provenance is carried by raw_items.source_type.
  const { error: claimErr } = await sb.from("claims").insert({
    raw_item_id: rawRow.id,
    extractor_version: "community-v1",
    brand,
    product_name,
    old_size,
    old_size_unit,
    new_size,
    new_size_unit,
    old_price,
    new_price,
    change_description: description,
    confidence: { brand: 0.6, product_name: 0.6, size_change: 0.5, overall: 0.5 },
    status: "pending",
  });
  if (claimErr) {
    console.error("submission claims insert failed:", claimErr);
    return NextResponse.json(
      { error: "Could not save submission — please try again later." },
      { status: 500 },
    );
  }

  return NextResponse.json({ ok: true, session_id });
}
