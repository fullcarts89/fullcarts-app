"use client";
// Admin-only inline action surfaced on public event listings. A logged-in
// admin (long-press logo → /admin/login → password) sees a small "↩ Send
// back to pending" button on each event row. One click → window.confirm →
// POST /api/admin/retract-event → router.refresh.
//
// For non-admins this component renders nothing, so the public site is
// unchanged.
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./RetractEventButton.module.css";

interface Props {
  eventId: string;
}

// Cache the whoami result across button mounts so a product page with 20
// events doesn't fire 20 identical requests on render.
let cachedAdmin: boolean | null = null;
let inflight: Promise<boolean> | null = null;

async function fetchIsAdmin(): Promise<boolean> {
  if (cachedAdmin !== null) return cachedAdmin;
  if (inflight) return inflight;
  inflight = fetch("/api/admin/whoami", { cache: "no-store" })
    .then((r) => r.json())
    .then((j) => {
      cachedAdmin = !!j?.admin;
      return cachedAdmin;
    })
    .catch(() => {
      cachedAdmin = false;
      return false;
    })
    .finally(() => {
      inflight = null;
    });
  return inflight;
}

export default function RetractEventButton({ eventId }: Props) {
  const router = useRouter();
  const [isAdmin, setIsAdmin] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let alive = true;
    fetchIsAdmin().then((ok) => {
      if (alive) setIsAdmin(ok);
    });
    return () => {
      alive = false;
    };
  }, []);

  if (!isAdmin) return null;

  async function onClick(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    if (busy) return;
    const ok = window.confirm(
      "Retract this event and send its backing claims to pending review?",
    );
    if (!ok) return;
    setBusy(true);
    try {
      const res = await fetch("/api/admin/retract-event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event_id: eventId }),
      });
      if (!res.ok) {
        const j = await res.json().catch(() => ({}));
        window.alert(`Retract failed: ${j?.error || res.statusText}`);
        return;
      }
      router.refresh();
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      type="button"
      className={styles.btn}
      onClick={onClick}
      disabled={busy}
      aria-label="Retract event and send backing claims to pending"
    >
      {busy ? "Retracting…" : "↩ Send to pending"}
    </button>
  );
}
