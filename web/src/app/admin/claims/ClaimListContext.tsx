"use client";

import {
  createContext,
  useCallback,
  useContext,
  useState,
  type ReactNode,
} from "react";

// Client-side optimistic-removal store for the /admin/claims card list.
//
// Why this exists: every single-card action (approve / discard / evidence /
// move-to-pending) takes the claim out of the current tab's filter, so the
// card should vanish the instant the route handler succeeds. Previously the
// actions used Server Actions, which auto-revalidate (re-render) the entire
// heavy /admin/claims route on completion — leaving the buttons stuck on
// "..." for the whole double re-render. We now mirror /admin/claims/groups:
// route handler via fetch + optimistic local state, no full-page refresh.
//
// The provider wraps the server-rendered card list; ClaimCard (which hides
// removed cards) and ClaimActions (which calls remove() on success) both read
// this context. A client provider can supply context to client components
// nested inside an otherwise server-rendered subtree.

type ClaimListCtx = {
  removed: Set<string>;
  remove: (claimId: string) => void;
};

const Ctx = createContext<ClaimListCtx | null>(null);

export function ClaimListProvider({ children }: { children: ReactNode }) {
  const [removed, setRemoved] = useState<Set<string>>(new Set());
  const remove = useCallback((claimId: string) => {
    setRemoved((prev) => {
      if (prev.has(claimId)) return prev;
      const next = new Set(prev);
      next.add(claimId);
      return next;
    });
  }, []);
  return <Ctx.Provider value={{ removed, remove }}>{children}</Ctx.Provider>;
}

export function useClaimList(): ClaimListCtx {
  const ctx = useContext(Ctx);
  if (!ctx) {
    throw new Error("useClaimList must be used within a ClaimListProvider");
  }
  return ctx;
}
