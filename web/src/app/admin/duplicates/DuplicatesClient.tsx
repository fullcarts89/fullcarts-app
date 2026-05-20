"use client";

import { useMemo, useState } from "react";
import MergeRow from "./MergeRow";
import BatchToolbar from "./BatchToolbar";
import type { MergePair } from "./lib";
import styles from "./styles.module.css";

interface Props {
  pairs: MergePair[];
  pageSize: number;
}

/**
 * Client-side selection state + "select all visible" / "select top N"
 * shortcuts. Server-fetched pair list is passed in as a prop; this
 * component just adds the interaction layer.
 */
export default function DuplicatesClient({ pairs, pageSize }: Props) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [limit, setLimit] = useState<number>(Math.min(pageSize, pairs.length));

  const visiblePairs = useMemo(() => pairs.slice(0, limit), [pairs, limit]);

  const selectedPairs = useMemo(() => {
    const map = new Map(visiblePairs.map((p) => [p.source.id, p]));
    return Array.from(selectedIds)
      .map((id) => map.get(id))
      .filter((p): p is MergePair => !!p)
      .map((p) => ({ sourceId: p.source.id, targetId: p.target.id }));
  }, [visiblePairs, selectedIds]);

  function toggle(sourceId: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(sourceId)) next.delete(sourceId);
      else next.add(sourceId);
      return next;
    });
  }

  function selectVisible() {
    setSelectedIds(new Set(visiblePairs.map((p) => p.source.id)));
  }

  function selectTop(n: number) {
    setSelectedIds(new Set(visiblePairs.slice(0, n).map((p) => p.source.id)));
  }

  function clearAll() {
    setSelectedIds(new Set());
  }

  return (
    <>
      <div className={styles.controls}>
        <div className={styles.controls_left}>
          <button
            type="button"
            onClick={() => selectTop(10)}
            className={styles.btn_quiet}
          >
            select top 10
          </button>
          <button
            type="button"
            onClick={() => selectTop(25)}
            className={styles.btn_quiet}
          >
            select top 25
          </button>
          <button
            type="button"
            onClick={() => selectTop(50)}
            className={styles.btn_quiet}
          >
            select top 50
          </button>
          <button
            type="button"
            onClick={selectVisible}
            className={styles.btn_quiet}
          >
            select all visible
          </button>
        </div>
        <div className={styles.controls_right}>
          <span className={styles.controls_label}>show:</span>
          {[50, 100, 200].map((n) => (
            <button
              key={n}
              type="button"
              onClick={() => setLimit(Math.min(n, pairs.length))}
              className={
                limit === Math.min(n, pairs.length)
                  ? styles.btn_pill_active
                  : styles.btn_pill
              }
            >
              {n}
            </button>
          ))}
          <button
            type="button"
            onClick={() => setLimit(pairs.length)}
            className={
              limit >= pairs.length ? styles.btn_pill_active : styles.btn_pill
            }
          >
            all ({pairs.length})
          </button>
        </div>
      </div>

      <BatchToolbar
        selectedPairs={selectedPairs}
        onClear={clearAll}
        totalShown={visiblePairs.length}
      />

      <div className={styles.list}>
        {visiblePairs.map((p) => (
          <MergeRow
            key={p.source.id}
            pair={p}
            selected={selectedIds.has(p.source.id)}
            onToggleSelect={() => toggle(p.source.id)}
          />
        ))}
      </div>
    </>
  );
}
