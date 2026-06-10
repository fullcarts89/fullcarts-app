"use client";
// Public community-submission form. Lives on /submit. Posts to /api/submit,
// which creates a raw_items evidence anchor (source_type='community_tip') + a
// pending claim. Fields map 1:1 onto claims columns so submissions arrive
// structured rather than as free text.
//
// session_id is generated once per browser and persisted in localStorage so
// duplicate submits get caught by the 60 s rate-limit on the server.
import { useRef, useState } from "react";
import styles from "../styles.module.css";

type Status = "idle" | "submitting" | "success" | "error";
const SESSION_KEY = "fc.submit.session_id";

function getOrCreateSessionId(): string {
  try {
    const existing = window.localStorage.getItem(SESSION_KEY);
    if (existing) return existing;
    const fresh =
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    window.localStorage.setItem(SESSION_KEY, fresh);
    return fresh;
  } catch {
    return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  }
}

export default function SubmissionForm() {
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const formRef = useRef<HTMLFormElement>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (status === "submitting") return;

    const fd = new FormData(e.currentTarget);
    const payload = {
      brand: String(fd.get("brand") || "").trim(),
      product_name: String(fd.get("product_name") || "").trim(),
      old_size: String(fd.get("old_size") || "").trim(),
      old_size_unit: String(fd.get("old_size_unit") || "").trim(),
      new_size: String(fd.get("new_size") || "").trim(),
      new_size_unit: String(fd.get("new_size_unit") || "").trim(),
      old_price: String(fd.get("old_price") || "").trim(),
      new_price: String(fd.get("new_price") || "").trim(),
      description: String(fd.get("description") || "").trim(),
      evidence_url: String(fd.get("evidence_url") || "").trim(),
      session_id: getOrCreateSessionId(),
    };

    if (!payload.brand || !payload.product_name) {
      setError("Brand and product are both required.");
      setStatus("error");
      return;
    }
    if (payload.description.length < 10) {
      setError("Please add at least a sentence describing what changed.");
      setStatus("error");
      return;
    }

    setStatus("submitting");
    setError(null);
    try {
      const res = await fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const j = (await res.json().catch(() => ({}))) as { error?: string };
        setError(j.error || "Submission failed — please try again.");
        setStatus("error");
        return;
      }
      setStatus("success");
      formRef.current?.reset();
    } catch {
      setError("Network error — please try again.");
      setStatus("error");
    }
  }

  if (status === "success") {
    return (
      <div
        className={`${styles["sub-form"]} ${styles["sub-form-success"]}`}
        role="status"
        aria-live="polite"
      >
        <div className={styles["sub-form-status"]}>Submission received</div>
        <p>
          Thanks — this is now in the same review queue our scrapers feed.
          We&apos;ll cross-check it and publish it as an event if it holds up.
          Most submissions are reviewed within a week.
        </p>
        <button
          type="button"
          className={styles["sub-form-submit"]}
          onClick={() => setStatus("idle")}
        >
          Submit another
        </button>
      </div>
    );
  }

  return (
    <form
      ref={formRef}
      className={styles["sub-form"]}
      onSubmit={handleSubmit}
      aria-label="Submit a shrinkflation event"
      noValidate
    >
      <div className={styles["sub-form-row"]}>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-brand">
            Brand <span className={styles.req}>required</span>
          </label>
          <input
            id="s-brand"
            name="brand"
            type="text"
            required
            aria-required="true"
            placeholder="e.g. Cadbury"
            maxLength={200}
            autoComplete="off"
          />
        </div>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-product">
            Product <span className={styles.req}>required</span>
          </label>
          <input
            id="s-product"
            name="product_name"
            type="text"
            required
            aria-required="true"
            placeholder="e.g. Dairy Milk"
            maxLength={200}
            autoComplete="off"
          />
        </div>
      </div>

      <div className={styles["sub-form-row"]}>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-oldsize">Old size</label>
          <div className={styles["sub-form-inline"]}>
            <input
              id="s-oldsize"
              name="old_size"
              type="text"
              inputMode="decimal"
              placeholder="200"
              maxLength={16}
              autoComplete="off"
            />
            <input
              name="old_size_unit"
              type="text"
              placeholder="g"
              maxLength={16}
              autoComplete="off"
              aria-label="Old size unit"
            />
          </div>
        </div>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-newsize">New size</label>
          <div className={styles["sub-form-inline"]}>
            <input
              id="s-newsize"
              name="new_size"
              type="text"
              inputMode="decimal"
              placeholder="180"
              maxLength={16}
              autoComplete="off"
            />
            <input
              name="new_size_unit"
              type="text"
              placeholder="g"
              maxLength={16}
              autoComplete="off"
              aria-label="New size unit"
            />
          </div>
        </div>
      </div>

      <div className={styles["sub-form-row"]}>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-oldprice">Old price (optional)</label>
          <input
            id="s-oldprice"
            name="old_price"
            type="text"
            inputMode="decimal"
            placeholder="2.50"
            maxLength={16}
            autoComplete="off"
          />
        </div>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-newprice">New price (optional)</label>
          <input
            id="s-newprice"
            name="new_price"
            type="text"
            inputMode="decimal"
            placeholder="2.50"
            maxLength={16}
            autoComplete="off"
          />
        </div>
      </div>

      <div className={styles["sub-form-field"]}>
        <label htmlFor="s-desc">
          What changed? <span className={styles.req}>required</span>
        </label>
        <textarea
          id="s-desc"
          name="description"
          rows={4}
          required
          aria-required="true"
          minLength={10}
          maxLength={4000}
          placeholder="e.g. The bar dropped from 200g to 180g but the price stayed the same. I kept the old wrapper for comparison."
        />
      </div>

      <div className={styles["sub-form-field"]}>
        <label htmlFor="s-url">Link to evidence (optional)</label>
        <input
          id="s-url"
          name="evidence_url"
          type="url"
          inputMode="url"
          maxLength={800}
          autoComplete="off"
          placeholder="https://… Reddit post, news article, retailer page, photo"
        />
      </div>

      {error && status === "error" && (
        <div className={styles["sub-form-error"]} role="alert">
          {error}
        </div>
      )}

      <div className={styles["sub-form-actions"]}>
        <button
          type="submit"
          className={styles["sub-form-submit"]}
          disabled={status === "submitting"}
        >
          {status === "submitting" ? "Sending…" : "Submit event"}
        </button>
        <div className={styles["sub-form-note"]}>
          Submissions enter the same review queue our scrapers feed. We&apos;ll
          credit you on the event unless you ask us not to.
        </div>
      </div>
    </form>
  );
}
