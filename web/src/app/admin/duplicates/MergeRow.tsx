"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { mergePair } from "./actions";
import type { EntityRow, MergePair } from "./lib";
import styles from "./styles.module.css";

interface Props {
  pair: MergePair;
  selected: boolean;
  onToggleSelect(): void;
}

/**
 * One merge candidate row. Two columns side-by-side: source (will be
 * absorbed + retracted) and target (will keep everything). Per-row
 * "merge" button for one-at-a-time application; the checkbox feeds the
 * batch button at the top of the page.
 */
export default function MergeRow({ pair, selected, onToggleSelect }: Props) {
  const [isPending, startTransition] = useTransition();
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [merged, setMerged] = useState(false);
  const router = useRouter();

  function onMerge() {
    if (
      !window.confirm(
        `Merge "${pair.source.canonical_name}" INTO "${pair.target.canonical_name}"?\n\n` +
          "All claims, events, and pack variants on the source will move to the target. " +
          "The source will be retracted (reversible).",
      )
    ) {
      return;
    }
    setError(null);
    setResult(null);
    startTransition(async () => {
      try {
        const out = await mergePair(pair.source.id, pair.target.id);
        setResult(
          `Merged. ${out.claimsMoved} claims, ${out.eventsMoved} events, ${out.variantsMoved} variants moved.`,
        );
        setMerged(true);
        router.refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "merge failed");
      }
    });
  }

  if (merged) {
    return (
      <div className={`${styles.row} ${styles.done}`}>
        <div className={styles.done_label}>✓ merged</div>
        <div className={styles.done_detail}>
          {pair.source.canonical_name} → {pair.target.canonical_name}
          {result && <span className={styles.done_counts}> · {result}</span>}
        </div>
      </div>
    );
  }

  return (
    <div className={styles.row}>
      <label className={styles.check}>
        <input
          type="checkbox"
          checked={selected}
          disabled={isPending}
          onChange={onToggleSelect}
          aria-label={`Select merge of ${pair.source.canonical_name} into ${pair.target.canonical_name}`}
        />
      </label>

      <EntityCell ent={pair.source} role="source" />
      <div className={styles.arrow} aria-hidden="true">
        →
      </div>
      <EntityCell ent={pair.target} role="target" />

      <div className={styles.actions}>
        <button
          type="button"
          onClick={onMerge}
          disabled={isPending}
          className={styles.btn}
        >
          {isPending ? "merging…" : "Merge →"}
        </button>
        {error && <div className={styles.err}>{error}</div>}
        {result && <div className={styles.ok}>{result}</div>}
      </div>

      {pair.group_size > 2 && (
        <div className={styles.group_badge}>
          group of {pair.group_size}
        </div>
      )}
    </div>
  );
}

function EntityCell({ ent, role }: { ent: EntityRow; role: "source" | "target" }) {
  return (
    <div
      className={`${styles.cell} ${role === "source" ? styles.source : styles.target}`}
    >
      <div className={styles.cell_top}>
        {ent.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={ent.image_url}
            alt=""
            className={styles.thumb}
            loading="lazy"
          />
        ) : (
          <div className={`${styles.thumb} ${styles.thumb_empty}`} />
        )}
        <div className={styles.cell_meta}>
          <div className={styles.cell_name}>{ent.canonical_name}</div>
          <div className={styles.cell_sub}>
            {ent.brand} · {ent.event_count} events
          </div>
        </div>
      </div>
      <div className={styles.cell_links}>
        <a
          href={`/products/${ent.id}`}
          target="_blank"
          rel="noreferrer"
          className={styles.linklet}
        >
          /products ↗
        </a>
        <span className={styles.id_chip}>{ent.id.slice(0, 8)}</span>
      </div>
    </div>
  );
}
