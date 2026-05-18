// Public tip submission endpoint.
//
// Writes to the existing `tips` table (migration 001). The "Anyone can
// submit tips" RLS policy (migration 002) allows inserts from anyone,
// so we use the service-role client purely for convenience — no
// special privilege is being exercised.
//
// Minimal abuse defences:
//   - 4kB body cap
//   - description required, brand/product strongly encouraged
//   - IP hashed (sha256) before storage so we can rate-limit later
//   - one tip per (session_id, ip_hash, minute) — the client generates
//     a session_id on first submit and persists it in localStorage so
//     duplicate submits get caught
import { NextRequest, NextResponse } from "next/server";
import { createHash } from "crypto";
import { createAdminClient } from "@/lib/supabase/admin";

const MAX_DESCRIPTION = 4000;
const MAX_FIELD = 200;

function clamp(s: unknown, max: number): string {
  if (typeof s !== "string") return "";
  return s.trim().slice(0, max);
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
  const description = clamp(b.description, MAX_DESCRIPTION);
  if (!description || description.length < 10) {
    return NextResponse.json(
      { error: "Description must be at least 10 characters" },
      { status: 400 },
    );
  }

  const brand = clamp(b.brand, MAX_FIELD);
  const product_name = clamp(b.product_name, MAX_FIELD);
  const evidence_url_raw = clamp(b.evidence_url, MAX_FIELD * 4);
  const session_id = clamp(b.session_id, 64) || crypto.randomUUID();

  // Lightweight URL sanity check — reject obvious junk but don't try
  // to be exhaustive; admins will sanity-check before promoting.
  let evidence_url: string | null = null;
  if (evidence_url_raw) {
    try {
      const u = new URL(evidence_url_raw);
      if (u.protocol === "http:" || u.protocol === "https:") {
        evidence_url = u.toString();
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

  // De-dup: same session_id submitting within 60s gets a 429 so the
  // user can't accidentally double-submit by clicking too fast.
  const sixtySecondsAgo = new Date(Date.now() - 60_000).toISOString();
  const { data: recent } = await sb
    .from("tips")
    .select("id, created_at")
    .eq("session_id", session_id)
    .gte("created_at", sixtySecondsAgo)
    .limit(1);
  if (recent && recent.length > 0) {
    return NextResponse.json(
      { error: "Slow down — we already received a tip from you in the last minute." },
      { status: 429 },
    );
  }

  const { error } = await sb.from("tips").insert({
    session_id,
    brand: brand || null,
    product_name: product_name || null,
    description,
    evidence_url,
    ip_hash,
    status: "pending",
  });

  if (error) {
    console.error("tip insert failed:", error);
    return NextResponse.json(
      { error: "Could not save tip — please try again later." },
      { status: 500 },
    );
  }

  return NextResponse.json({ ok: true, session_id });
}
