"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { reopenFlag, resolveFlag } from "./actions";
import { FLAG_KIND_META, SEVERITY_META } from "./types";
import type { FlagRow as FlagRowType } from "./types";
import styles from "./styles.module.css";

interface Props {
  flag: FlagRowType;
  selected: boolean;
  onToggleSelect(): void;
}

/**
 * Single flag row. Two render modes — open (with selectable checkbox +
 * Resolve button) and resolved (collapsed view with Reopen button).
 *
 * detail JSON is rendered as a key:value list rather than raw JSON for
 * readability. Long string values are truncated.
 */
export default function FlagRow({ flag, selected, onToggleSelect }: Props) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [noteInput, setNoteInput] = useState<string>("");
  const [showNote, setShowNote] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const meta = FLAG_KIND_META[flag.flag_kind] ?? {
    label: flag.flag_kind,
    explainer: "",
    tone: "purple" as const,
  };
  const sev = SEVERITY_META[flag.severity] ?? SEVERITY_META.med;

  function onResolve() {
    setError(null);
    startTransition(async () => {
      try {
        await resolveFlag(flag.id, noteInput || null);
        setShowNote(false);
        setNoteInput("");
        router.refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "resolve failed");
      }
    });
  }

  function onReopen() {
    setError(null);
    startTransition(async () => {
      try {
        await reopenFlag(flag.id);
        router.refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "reopen failed");
      }
    });
  }

  const targetLink = getTargetLink(flag);

  if (flag.resolved_at) {
    return (
      <div className={`${styles.row} ${styles.row_resolved}`}>
        <div className={styles.cell_check} aria-hidden="true" />
        <div className={`${styles.kind_chip} ${styles[`tone_${meta.tone}`]}`}>
          {meta.label}
        </div>
        <div className={styles.cell_target}>
          {targetLink && (
            <a
              href={targetLink.href}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.target_link}
            >
              {targetLink.label} ↗
            </a>
          )}
          <DetailDisplay detail={flag.detail} />
        </div>
        <div className={styles.cell_date}>
          <span className={styles.detected_at}>{shortDate(flag.detected_at)}</span>
          <span className={styles.resolved_at}>
            resolved {shortDate(flag.resolved_at)}
            {flag.resolution_note && (
              <span className={styles.resolution_note}>
                {" "}— “{flag.resolution_note}”
              </span>
            )}
          </span>
        </div>
        <div className={styles.cell_actions}>
          <button
            type="button"
            onClick={onReopen}
            disabled={isPending}
            className={styles.btn_quiet}
          >
            {isPending ? "…" : "Reopen"}
          </button>
          {error && <div className={styles.err}>{error}</div>}
        </div>
      </div>
    );
  }

  return (
    <div className={styles.row}>
      <label className={styles.cell_check}>
        <input
          type="checkbox"
          checked={selected}
          disabled={isPending}
          onChange={onToggleSelect}
          aria-label={`Select flag ${flag.id}`}
        />
      </label>
      <div className={`${styles.kind_chip} ${styles[`tone_${meta.tone}`]}`}>
        {meta.label}
        <span className={`${styles.sev} ${styles[`sev_${sev.tone}`]}`}>{sev.label}</span>
      </div>
      <div className={styles.cell_target}>
        {targetLink && (
          <a
            href={targetLink.href}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.target_link}
          >
            {targetLink.label} ↗
          </a>
        )}
        <DetailDisplay detail={flag.detail} />
        {meta.explainer && (
          <div className={styles.explainer}>{meta.explainer}</div>
        )}
      </div>
      <div className={styles.cell_date}>
        <span className={styles.detected_at}>{shortDate(flag.detected_at)}</span>
        <span className={styles.detected_by}>by {flag.detected_by}</span>
      </div>
      <div className={styles.cell_actions}>
        {showNote ? (
          <div className={styles.note_input_group}>
            <textarea
              value={noteInput}
              onChange={(e) => setNoteInput(e.target.value)}
              placeholder="Resolution note (optional)"
              disabled={isPending}
              className={styles.note_input}
              rows={2}
            />
            <div className={styles.note_actions}>
              <button
                type="button"
                onClick={onResolve}
                disabled={isPending}
                className={styles.btn}
              >
                {isPending ? "…" : "Confirm"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowNote(false);
                  setNoteInput("");
                }}
                disabled={isPending}
                className={styles.btn_quiet}
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <>
            <button
              type="button"
              onClick={onResolve}
              disabled={isPending}
              className={styles.btn}
            >
              {isPending ? "…" : "Resolve"}
            </button>
            <button
              type="button"
              onClick={() => setShowNote(true)}
              disabled={isPending}
              className={styles.btn_quiet}
            >
              + note
            </button>
          </>
        )}
        {error && <div className={styles.err}>{error}</div>}
      </div>
    </div>
  );
}

// ── helpers ───────────────────────────────────────────────────────────

function getTargetLink(
  flag: FlagRowType,
): { href: string; label: string } | null {
  if (flag.entity_id) {
    return {
      href: `/products/${flag.entity_id}`,
      label: "view entity",
    };
  }
  if (flag.event_id) {
    // detail commonly carries entity_id alongside the event; fall back
    // to a generic admin entities search if not present.
    const detailEntity = (flag.detail as Record<string, unknown>).entity_id;
    if (typeof detailEntity === "string") {
      return { href: `/products/${detailEntity}`, label: "view event" };
    }
    return { href: "/admin/entities", label: "view event in admin" };
  }
  if (flag.claim_id) {
    return {
      href: `/admin/claims?status=matched`,
      label: "view in claims",
    };
  }
  return null;
}

function shortDate(iso: string | null): string {
  if (!iso) return "—";
  return iso.slice(0, 19).replace("T", " ");
}

function DetailDisplay({ detail }: { detail: Record<string, unknown> }) {
  if (!detail || Object.keys(detail).length === 0) return null;
  const entries = Object.entries(detail).slice(0, 6);
  return (
    <dl className={styles.detail_dl}>
      {entries.map(([k, v]) => {
        const valueStr = typeof v === "string" ? v : JSON.stringify(v);
        const truncated = valueStr.length > 120 ? valueStr.slice(0, 120) + "…" : valueStr;
        return (
          <span key={k} className={styles.detail_entry}>
            <dt className={styles.detail_key}>{k}</dt>
            <dd className={styles.detail_val}>{truncated}</dd>
          </span>
        );
      })}
    </dl>
  );
}
