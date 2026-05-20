import Link from "next/link";
import { createAdminClient } from "@/lib/supabase/admin";
import { findDuplicatePairs } from "./lib";
import type { EntityRow } from "./lib";
import DuplicatesClient from "./DuplicatesClient";
import styles from "./styles.module.css";

// Pull every non-retracted entity (paginated past PostgREST's 1k cap),
// also count events per entity in the same pass so the duplicate picker
// can rank target = highest-event-count.
//
// This is admin-only via the /admin/* middleware. Reads ~21k rows; runs
// in <1s server-side.
async function loadEntities(): Promise<EntityRow[]> {
  const sb = createAdminClient();
  const PAGE = 1000;
  const all: EntityRow[] = [];
  // Step 1: paginate entities.
  for (let from = 0; ; from += PAGE) {
    const { data, error } = await sb
      .from("product_entities")
      .select("id, brand, canonical_name, image_url, category, created_at")
      .eq("is_retracted", false)
      .order("id")
      .range(from, from + PAGE - 1);
    if (error) throw new Error(`product_entities: ${error.message}`);
    const batch = (data ?? []) as Array<Omit<EntityRow, "event_count">>;
    for (const row of batch) all.push({ ...row, event_count: 0 });
    if (batch.length < PAGE) break;
  }

  // Step 2: tally events per entity. Single batched fetch (~3k rows post-retract).
  const counts = new Map<string, number>();
  for (let from = 0; ; from += PAGE) {
    const { data, error } = await sb
      .from("published_changes")
      .select("entity_id")
      .eq("is_retracted", false)
      .not("entity_id", "is", null)
      .range(from, from + PAGE - 1);
    if (error) throw new Error(`published_changes: ${error.message}`);
    const batch = (data ?? []) as Array<{ entity_id: string | null }>;
    for (const r of batch) {
      if (r.entity_id) counts.set(r.entity_id, (counts.get(r.entity_id) ?? 0) + 1);
    }
    if (batch.length < PAGE) break;
  }
  for (const ent of all) ent.event_count = counts.get(ent.id) ?? 0;
  return all;
}

export const dynamic = "force-dynamic";

export default async function DuplicatesPage() {
  const entities = await loadEntities();
  const pairs = findDuplicatePairs(entities);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.header_top}>
          <h1 className={styles.title}>Entity Duplicates</h1>
          <Link href="/admin/entities" className={styles.linkback}>
            ← Entity Browser
          </Link>
        </div>
        <p className={styles.subtitle}>
          Entities that share the same brand AND a normalised (lowercase, alpha-num only)
          canonical_name. Target column = the entity in the group with the most events; merging
          collapses the source INTO the target, then retracts the source. Reversible per-row via
          /admin/entities.
        </p>
        <div className={styles.stats}>
          <span className={styles.stat}>
            <span className={styles.stat_value}>{pairs.length.toLocaleString()}</span>
            <span className={styles.stat_label}>merge candidates</span>
          </span>
          <span className={styles.stat}>
            <span className={styles.stat_value}>
              {new Set(pairs.map((p) => p.group_key)).size.toLocaleString()}
            </span>
            <span className={styles.stat_label}>collision groups</span>
          </span>
          <span className={styles.stat}>
            <span className={styles.stat_value}>{entities.length.toLocaleString()}</span>
            <span className={styles.stat_label}>entities scanned</span>
          </span>
        </div>
      </header>

      {pairs.length === 0 ? (
        <div className={styles.empty}>
          No duplicate candidates. Nothing to merge.
        </div>
      ) : (
        <DuplicatesClient pairs={pairs} pageSize={50} />
      )}
    </div>
  );
}
