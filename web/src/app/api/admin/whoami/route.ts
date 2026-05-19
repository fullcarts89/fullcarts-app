import { NextResponse } from "next/server";
import { isAdminRequest } from "@/lib/admin-auth";

// Public-facing pages can't read the httpOnly admin_session cookie directly,
// so client components ping this to decide whether to render admin-only UI
// (e.g. the inline retract-event button).
export async function GET() {
  const admin = await isAdminRequest();
  return NextResponse.json({ admin });
}
