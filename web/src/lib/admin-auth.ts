// Server-only helper for verifying an admin session on API routes that
// live outside the `/admin/*` namespace (where middleware doesn't reach).
// Mirrors the cookie check in `middleware.ts`.
import { cookies } from "next/headers";

export async function isAdminRequest(): Promise<boolean> {
  const expected = process.env.ADMIN_PASSWORD_HASH;
  if (!expected) return false;
  const store = await cookies();
  const session = store.get("admin_session")?.value;
  return !!session && session === expected;
}
