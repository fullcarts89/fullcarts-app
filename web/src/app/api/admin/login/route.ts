import { NextRequest, NextResponse } from "next/server";
import { createHash } from "crypto";

export async function POST(request: NextRequest) {
  const { password } = await request.json();

  if (!password) {
    return NextResponse.json({ error: "Missing password" }, { status: 400 });
  }

  // Hash the provided password and compare with stored hash
  const hash = createHash("sha256").update(password).digest("hex");
  const expectedHash = process.env.ADMIN_PASSWORD_HASH;

  if (!expectedHash) {
    console.error("ADMIN_PASSWORD_HASH not configured");
    return NextResponse.json({ error: "Not configured" }, { status: 500 });
  }

  if (hash !== expectedHash) {
    return NextResponse.json({ error: "Invalid password" }, { status: 401 });
  }

  // Set a secure session cookie (7 days)
  const response = NextResponse.json({ ok: true });
  response.cookies.set("admin_session", hash, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7, // 7 days
  });

  return response;
}
