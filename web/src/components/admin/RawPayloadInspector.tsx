"use client";
// Admin-only per-source inspector. Renders as a small "Inspect" button
// inline with each source row on /products/[id] and /brands/[name]. Click
// reveals an expanded panel that loads the full `raw_items.raw_payload`
// JSON for that source on demand (one fetch per source, cached after
// first open). Non-admins see nothing — same admin-cookie discovery as
// RetractEventButton, with the cache shared so 30 sources on a page don't
// fire 30 whoami requests.
import { useEffect, useState } from "react";
import styles from "./RawPayloadInspector.module.css";

interface Props {
  claimId: string;
}

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

type Payload = {
  id: string;
  status: string;
  brand: string | null;
  product_name: string | null;
  change_description: string | null;
  observed_date: string | null;
  evidence_tags: string[] | null;
  image_storage_path: string | null;
  raw_items: {
    id: string;
    source_type: string;
    source_url: string | null;
    source_date: string | null;
    raw_payload: Record<string, unknown> | null;
  } | null;
};

export default function RawPayloadInspector({ claimId }: Props) {
  const [isAdmin, setIsAdmin] = useState(false);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [payload, setPayload] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    fetchIsAdmin().then((ok) => {
      if (alive) setIsAdmin(ok);
    });
    return () => {
      alive = false;
    };
  }, []);

  async function load() {
    if (payload || loading) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `/api/admin/source-payload?claim_id=${encodeURIComponent(claimId)}`,
        { cache: "no-store" },
      );
      if (!res.ok) {
        const j = await res.json().catch(() => ({}));
        throw new Error(j?.error || res.statusText);
      }
      setPayload((await res.json()) as Payload);
    } catch (e) {
      setError(e instanceof Error ? e.message : "load failed");
    } finally {
      setLoading(false);
    }
  }

  function toggle(e: React.MouseEvent) {
    // Stop click from bubbling to the parent <a> source row.
    e.preventDefault();
    e.stopPropagation();
    if (!open && !payload) void load();
    setOpen((v) => !v);
  }

  if (!isAdmin) return null;

  return (
    <span className={styles.wrap}>
      <button
        type="button"
        className={styles.btn}
        onClick={toggle}
        aria-expanded={open}
        aria-label="Inspect raw payload for this source"
        title="Admin: show raw_items.raw_payload for this source"
      >
        {open ? "− inspect" : "+ inspect"}
      </button>
      {open && (
        <div
          className={styles.panel}
          // Keep clicks inside the panel from triggering the outer source-row anchor.
          onClick={(e) => e.stopPropagation()}
        >
          {loading && <div className={styles.msg}>Loading…</div>}
          {error && <div className={styles.err}>{error}</div>}
          {payload && (
            <>
              <div className={styles.meta}>
                <div>
                  <strong>claim</strong> {payload.id} · <strong>status</strong>{" "}
                  {payload.status}
                </div>
                {payload.raw_items && (
                  <div>
                    <strong>source</strong> {payload.raw_items.source_type} ·{" "}
                    <strong>fetched</strong>{" "}
                    {payload.raw_items.source_date
                      ? payload.raw_items.source_date.slice(0, 10)
                      : "—"}
                  </div>
                )}
                {payload.raw_items?.source_url && (
                  <div>
                    <a
                      href={payload.raw_items.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={styles.openLink}
                    >
                      ↗ open source URL
                    </a>
                  </div>
                )}
              </div>
              <pre className={styles.json}>
                {JSON.stringify(
                  payload.raw_items?.raw_payload ?? payload,
                  null,
                  2,
                )}
              </pre>
            </>
          )}
        </div>
      )}
    </span>
  );
}
