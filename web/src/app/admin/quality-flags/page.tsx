import Link from "next/link";
import { createAdminClient } from "@/lib/supabase/admin";
import FlagsClient from "./FlagsClient";
import type { FlagRow } from "./types";
import styles from "./styles.module.css";

export const dynamic = "force-dynamic";

const PAGE_SIZE = 100;

export default async function QualityFlagsPage({
  searchParams,
}: {
  searchParams: Promise<{
    status?: string;
    kind?: string;
    severity?: string;
  }>;
}) {
  const params = await searchParams;
  const status: "open" | "resolved" | "all" =
    params.status === "resolved" || params.status === "all" ? params.status : "open";
  const kind = params.kind && params.kind.length > 0 ? params.kind : null;
  const severity =
    params.severity === "high" || params.severity === "med" || params.severity === "low"
      ? params.severity
      : null;

  const sb = createAdminClient();

  // Status counts (always shown so admin can see the queue size irrespective of current filter).
  const [openRes, resolvedRes, allRes] = await Promise.all([
    sb.from("data_quality_flags").select("*", { count: "exact", head: true }).is("resolved_at", null),
    sb.from("data_quality_flags").select("*", { count: "exact", head: true }).not("resolved_at", "is", null),
    sb.from("data_quality_flags").select("*", { count: "exact", head: true }),
  ]);
  const statusCounts = {
    open: openRes.count ?? 0,
    resolved: resolvedRes.count ?? 0,
    all: allRes.count ?? 0,
  };

  // Open count per flag_kind so the filter pills can show counts. We do
  // this with a small in-app aggregation: PostgREST doesn't expose
  // GROUP BY, so pull a `flag_kind`-only projection and bucket in JS.
  // The open queue should stay under ~10k rows even after backfill, so a
  // single pull is fine.
  const openKindsRes = await sb
    .from("data_quality_flags")
    .select("flag_kind")
    .is("resolved_at", null)
    .limit(20000);
  const kindCounts: Record<string, number> = {};
  for (const row of (openKindsRes.data ?? []) as Array<{ flag_kind: string }>) {
    kindCounts[row.flag_kind] = (kindCounts[row.flag_kind] ?? 0) + 1;
  }
  const kindBreakdown = Object.entries(kindCounts)
    .map(([kind, open]) => ({ kind, open }))
    .sort((a, b) => b.open - a.open);

  // Main list query.
  let query = sb
    .from("data_quality_flags")
    .select("*")
    .order("detected_at", { ascending: false })
    .limit(PAGE_SIZE);
  if (status === "open") query = query.is("resolved_at", null);
  else if (status === "resolved") query = query.not("resolved_at", "is", null);
  if (kind) query = query.eq("flag_kind", kind);
  if (severity) query = query.eq("severity", severity);

  const { data: flagsData, error } = await query;
  if (error) throw new Error(`data_quality_flags: ${error.message}`);
  const flags = (flagsData ?? []) as FlagRow[];

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.header_top}>
          <h1 className={styles.title}>Quality Flags</h1>
          <Link href="/admin/entities" className={styles.linkback}>
            ← Entities
          </Link>
          <Link href="/admin/claims" className={styles.linkback}>
            ← Claims
          </Link>
        </div>
        <p className={styles.subtitle}>
          Open queue of data-quality issues raised by the pipeline detectors. Each row points at one
          claim, entity, or event — admin reviews, fixes via the appropriate tool ({" "}
          <Link href="/admin/entities" className={styles.inlinelink}>
            /admin/entities
          </Link>{" "}
          /{" "}
          <Link href="/admin/duplicates" className={styles.inlinelink}>
            /admin/duplicates
          </Link>{" "}
          /{" "}
          <Link href="/admin/claims" className={styles.inlinelink}>
            /admin/claims
          </Link>
          ), then resolves the flag. Reopen any row if the fix didn&rsquo;t stick.
        </p>
        <div className={styles.stats}>
          <span className={styles.stat}>
            <span className={styles.stat_value}>
              {statusCounts.open.toLocaleString()}
            </span>
            <span className={styles.stat_label}>open</span>
          </span>
          <span className={styles.stat}>
            <span className={styles.stat_value}>
              {statusCounts.resolved.toLocaleString()}
            </span>
            <span className={styles.stat_label}>resolved</span>
          </span>
          <span className={styles.stat}>
            <span className={styles.stat_value}>
              {kindBreakdown.length.toLocaleString()}
            </span>
            <span className={styles.stat_label}>kinds</span>
          </span>
        </div>
      </header>

      <FlagsClient
        flags={flags}
        statusCounts={statusCounts}
        currentStatus={status}
        currentKind={kind}
        currentSeverity={severity}
        kindBreakdown={kindBreakdown}
      />
    </div>
  );
}
