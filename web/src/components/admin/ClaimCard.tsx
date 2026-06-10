"use client";

import type { ReactNode } from "react";
import { useClaimList } from "@/app/admin/claims/ClaimListContext";

// Thin client wrapper around each server-rendered claim <article>. When the
// card's action succeeds (ClaimActions calls remove(claimId)), this returns
// null so the card disappears instantly — no router.refresh / page re-render.
export function ClaimCard({
  claimId,
  children,
}: {
  claimId: string;
  children: ReactNode;
}) {
  const { removed } = useClaimList();
  if (removed.has(claimId)) return null;
  return <>{children}</>;
}
