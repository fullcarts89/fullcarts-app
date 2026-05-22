import Link from "next/link";
import { createAdminClient } from "@/lib/supabase/admin";
import { findDuplicatePairs, findFuzzyDuplicateGroups } from "./lib";
import type { EntityRow } from "./lib";
import DuplicatesClient from "./DuplicatesClient";
import FuzzyDuplicatesClient from "./FuzzyDuplicatesClient";
import styles from "./styles.module.css";
import fuzzyStyles from "./fuzzy.module.css";

type EventSizeRow = {
  entity_id: string | null;
  size_before: number | null;
  size_after: number | null;
  size_unit: string | null;
};

// Pull every non-retracted entity (paginated past PostgREST's 1k cap),
// also count events per entity in the same pass so the duplicate picker
// can rank target = highest-event-count. Now also returns the raw
// size-per-event list so the fuzzy matcher can apply the size-overlap
// requirement.
//
// This is admin-only via the /admin/* middleware. Reads ~21k rows; runs
// in <1s server-side.
async function loadData(): Promise<{
  entities: EntityRow[];
  events: EventSizeRow[];
}> {
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

  // Step 2: pull all live event rows once (with size fields for fuzzy
  // matcher). Used for both the per-entity count and the size-overlap
  // requirement — saves a second round-trip.
  const events: EventSizeRow[] = [];
  for (let from = 0; ; from += PAGE) {
    const { data, error } = await sb
      .from("published_changes")
      .select("entity_id, size_before, size_after, size_unit")
      .eq("is_retracted", false)
      .not("entity_id", "is", null)
      .range(from, from + PAGE - 1);
    if (error) throw new Error(`published_changes: ${error.message}`);
    const batch = (data ?? []) as EventSizeRow[];
    for (const r of batch) events.push(r);
    if (batch.length < PAGE) break;
  }

  // Step 3: derive per-entity event counts from the same event list.
  const counts = new Map<string, number>();
  for (const r of events) {
    if (r.entity_id) counts.set(r.entity_id, (counts.get(r.entity_id) ?? 0) + 1);
  }
  for (const ent of all) ent.event_count = counts.get(ent.id) ?? 0;
  return { entities: all, events };
}

export const dynamic = "force-dynamic";

export default async function DuplicatesPage() {
  const { entities, events } = await loadData();
  const pairs = findDuplicatePairs(entities);
  const fuzzyGroups = findFuzzyDuplicateGroups(entities, events);

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
            <span className={styles.stat_label}>exact-merge candidates</span>
          </span>
          <span className={styles.stat}>
            <span className={styles.stat_value}>
              {new Set(pairs.map((p) => p.group_key)).size.toLocaleString()}
            </span>
            <span className={styles.stat_label}>exact-collision groups</span>
          </span>
          <span className={styles.stat}>
            <span className={styles.stat_value}>{fuzzyGroups.length.toLocaleString()}</span>
            <span className={styles.stat_label}>fuzzy groups</span>
          </span>
          <span className={styles.stat}>
            <span className={styles.stat_value}>{entities.length.toLocaleString()}</span>
            <span className={styles.stat_label}>entities scanned</span>
          </span>
        </div>
      </header>

      {pairs.length === 0 ? (
        <div className={styles.empty}>
          No exact-match duplicate candidates.
        </div>
      ) : (
        <DuplicatesClient pairs={pairs} pageSize={50} />
      )}

      <section>
        <div className={fuzzyStyles.fuzzy_section_header}>
          <h2 className={fuzzyStyles.fuzzy_title}>Size-Signature Duplicates</h2>
          <p className={fuzzyStyles.fuzzy_subtitle}>
            Groups of entities that share the same brand AND identical published_changes size
            change (size_before, size_after, size_unit). Catches Gatorade-class drift where AI
            extraction produced wildly different canonical names (&ldquo;Bottle&rdquo;,
            &ldquo;Gatorade Bottle&rdquo;, &ldquo;Sports Drink&rdquo;) for the same real product.
            <strong> ✓ name match</strong> = members also share a fuzzy name key (high-confidence
            merge). <strong>⚠ names diverge</strong> = could still be the same product OR a real
            product line (e.g. five Herbal Essences scents shrinking uniformly) — verify member
            names before merging. Default target = highest event_count; pick per group via radio.
          </p>
          <div className={fuzzyStyles.fuzzy_stats}>
            <span className={styles.stat}>
              <span className={styles.stat_value}>{fuzzyGroups.length.toLocaleString()}</span>
              <span className={styles.stat_label}>candidate groups</span>
            </span>
            <span className={styles.stat}>
              <span className={styles.stat_value}>
                {fuzzyGroups
                  .filter((g) => g.has_fuzzy_name_match)
                  .length.toLocaleString()}
              </span>
              <span className={styles.stat_label}>✓ name match</span>
            </span>
            <span className={styles.stat}>
              <span className={styles.stat_value}>
                {fuzzyGroups
                  .reduce((acc, g) => acc + g.members.length - 1, 0)
                  .toLocaleString()}
              </span>
              <span className={styles.stat_label}>mergeable sources</span>
            </span>
          </div>
        </div>

        <FuzzyDuplicatesClient groups={fuzzyGroups} />
      </section>
    </div>
  );
}
