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
// Evidence is REQUIRED: a submission must carry either an evidence URL or an
// uploaded photo (or both). Photos are uploaded to the public `claim-images`
// storage bucket under a `community/` prefix and the path is stored on
// claims.image_storage_path, so the admin claim queue renders it via the same
// ClaimImage component used for scraped evidence.
//
// The request is multipart/form-data (so a file can ride along). Clients
// downscale/compress the image before upload to stay under Vercel's request
// body limit; we still enforce a hard server-side cap as a backstop.
//
// Abuse defenses mirror /api/tips: IP hashing + 60 s per-session dedup.
// Submissions are anonymous but gated — nothing is public until an admin
// approves the claim.
import { NextRequest, NextResponse } from "next/server";
import { createHash, randomUUID } from "crypto";
import { createAdminClient } from "@/lib/supabase/admin";

export const dynamic = "force-dynamic";

const SOURCE_TYPE = "community_tip";
const STORAGE_BUCKET = "claim-images";
const MAX_DESCRIPTION = 4000;
const MAX_FIELD = 200;
const MAX_UNIT = 16;
const MAX_PHOTO_BYTES = 6 * 1024 * 1024; // 6 MB backstop (clients compress first)
const ALLOWED_IMAGE_TYPES: Record<string, string> = {
  "image/jpeg": "jpg",
  "image/png": "png",
  "image/webp": "webp",
  "image/gif": "gif",
  "image/heic": "heic",
  "image/heif": "heif",
};

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
  let form: FormData;
  try {
    form = await req.formData();
  } catch {
    return NextResponse.json(
      { error: "Expected multipart/form-data" },
      { status: 400 },
    );
  }

  const field = (k: string): string => {
    const v = form.get(k);
    return typeof v === "string" ? v : "";
  };

  const brand = clamp(field("brand"), MAX_FIELD);
  const product_name = clamp(field("product_name"), MAX_FIELD);
  const description = clamp(field("description"), MAX_DESCRIPTION);

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

  const old_size = toNum(field("old_size"));
  const new_size = toNum(field("new_size"));
  const old_size_unit = clamp(field("old_size_unit"), MAX_UNIT) || null;
  const new_size_unit = clamp(field("new_size_unit"), MAX_UNIT) || null;
  const old_price = toNum(field("old_price"));
  const new_price = toNum(field("new_price"));
  const session_id = clamp(field("session_id"), 64) || randomUUID();

  // Optional evidence URL — reject obvious junk, don't be exhaustive.
  const evidence_url_raw = clamp(field("evidence_url"), MAX_FIELD * 4);
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

  // Optional photo. Validate type + size here; upload happens after we know the
  // submission is otherwise valid.
  const photoRaw = form.get("photo");
  const photo =
    photoRaw && typeof photoRaw === "object" && "arrayBuffer" in photoRaw
      ? (photoRaw as File)
      : null;
  const hasPhoto = !!photo && photo.size > 0;

  if (hasPhoto) {
    if (!ALLOWED_IMAGE_TYPES[photo!.type]) {
      return NextResponse.json(
        { error: "Photo must be a JPEG, PNG, WebP, GIF or HEIC image" },
        { status: 400 },
      );
    }
    if (photo!.size > MAX_PHOTO_BYTES) {
      return NextResponse.json(
        { error: "Photo is too large (max 6 MB after compression)" },
        { status: 413 },
      );
    }
  }

  // Evidence is required: a link, a photo, or both.
  if (!evidence_url && !hasPhoto) {
    return NextResponse.json(
      { error: "Evidence is required — add a link or attach a photo." },
      { status: 400 },
    );
  }

  const ip_hash = hashIp(req);
  const sb = createAdminClient();

  // De-dup: same session within 60 s → 429, so a double-click can't double-post.
  const sixtySecondsAgo = new Date(Date.now() - 60_000).toISOString();
  const { data: recent } = await sb
    .from("raw_items")
    .select("id, captured_at")
    .eq("source_type", SOURCE_TYPE)
    .eq("raw_payload->>session_id", session_id)
    .gte("captured_at", sixtySecondsAgo)
    .limit(1);
  if (recent && recent.length > 0) {
    return NextResponse.json(
      { error: "Slow down — we already received a submission from you in the last minute." },
      { status: 429 },
    );
  }

  const submissionId = randomUUID();

  // Upload the photo first (if any) so we can record its path on both rows.
  let image_storage_path: string | null = null;
  if (hasPhoto) {
    const ext = ALLOWED_IMAGE_TYPES[photo!.type];
    const path = `community/${submissionId}.${ext}`;
    const bytes = new Uint8Array(await photo!.arrayBuffer());
    const { error: uploadErr } = await sb.storage
      .from(STORAGE_BUCKET)
      .upload(path, bytes, { contentType: photo!.type, upsert: false });
    if (uploadErr) {
      console.error("submission photo upload failed:", uploadErr);
      return NextResponse.json(
        { error: "Could not save the photo — please try again." },
        { status: 500 },
      );
    }
    image_storage_path = path;
  }

  // 1. Evidence anchor. source_id is unique per submission so we never collide
  //    with the UNIQUE (source_type, source_id) index. content_hash and
  //    scraper_version are NOT NULL columns and must be supplied.
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
    image_storage_path,
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
  //    provenance is carried by raw_items.source_type. image_storage_path lights
  //    up the photo in the admin claim queue via the existing ClaimImage.
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
    image_storage_path,
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
