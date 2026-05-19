"use client";
// Public tip submission form. Lives inside the "Submit a tip" section
// on /about. Posts to /api/tips → tips table → admin review queue.
//
// session_id is generated once per browser and persisted in
// localStorage so duplicate submits get caught by the rate-limit on
// the server. We deliberately ask for only the minimum to lower
// submission friction; brand + product_name are optional because tips
// without those can still be triaged by the description.
import { useRef, useState } from "react";
import styles from "../styles.module.css";

type Status = "idle" | "submitting" | "success" | "error";

const SESSION_KEY = "fc.tip.session_id";

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

export default function TipForm() {
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
      description: String(fd.get("description") || "").trim(),
      evidence_url: String(fd.get("evidence_url") || "").trim(),
      session_id: getOrCreateSessionId(),
    };

    if (payload.description.length < 10) {
      setError("Please add at least a sentence describing what you saw.");
      setStatus("error");
      return;
    }

    setStatus("submitting");
    setError(null);
    try {
      const res = await fetch("/api/tips", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const body = (await res.json().catch(() => ({}))) as {
          error?: string;
        };
        setError(body.error || "Submission failed — please try again.");
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
      <div className={`${styles["tip-form"]} ${styles["tip-form-success"]}`}>
        <div className={styles["tip-form-status"]}>Tip received</div>
        <p>
          Thanks — your tip is in our review queue. We&apos;ll cross-check it
          against our existing sources and publish it as an event if it
          checks out. Most submissions are reviewed within a week.
        </p>
        <button
          type="button"
          className={styles["tip-form-submit"]}
          onClick={() => setStatus("idle")}
        >
          Submit another tip
        </button>
      </div>
    );
  }

  return (
    <form
      ref={formRef}
      className={styles["tip-form"]}
      onSubmit={handleSubmit}
      aria-label="Submit a shrinkflation tip"
      noValidate
    >
      <div className={styles["tip-form-row"]}>
        <div className={styles["tip-form-field"]}>
          <label htmlFor="tip-brand">Brand</label>
          <input
            id="tip-brand"
            name="brand"
            type="text"
            placeholder="e.g. Cadbury"
            maxLength={200}
            autoComplete="off"
          />
        </div>
        <div className={styles["tip-form-field"]}>
          <label htmlFor="tip-product">Product</label>
          <input
            id="tip-product"
            name="product_name"
            type="text"
            placeholder="e.g. Dairy Milk Mini Eggs"
            maxLength={200}
            autoComplete="off"
          />
        </div>
      </div>
      <div className={styles["tip-form-field"]}>
        <label htmlFor="tip-description">
          What changed? <span className={styles.req}>required</span>
        </label>
        <textarea
          id="tip-description"
          name="description"
          rows={4}
          required
          aria-required="true"
          minLength={10}
          maxLength={4000}
          placeholder="e.g. The bag went from 96g to 80g but the price stayed the same. I have the old bag at home for comparison."
        />
      </div>
      <div className={styles["tip-form-field"]}>
        <label htmlFor="tip-evidence">Link to evidence (optional)</label>
        <input
          id="tip-evidence"
          name="evidence_url"
          type="url"
          placeholder="https://… Reddit post, news article, retailer page, photo"
          maxLength={800}
          autoComplete="off"
          inputMode="url"
        />
      </div>
      {error && status === "error" && (
        <div className={styles["tip-form-error"]} role="alert">
          {error}
        </div>
      )}
      <div className={styles["tip-form-actions"]}>
        <button
          type="submit"
          className={styles["tip-form-submit"]}
          disabled={status === "submitting"}
        >
          {status === "submitting" ? "Sending…" : "Submit tip"}
        </button>
        <div className={styles["tip-form-note"]}>
          Tips go straight into the same review queue our scrapers feed.
          We&apos;ll credit you on the event unless you ask us not to.
        </div>
      </div>
    </form>
  );
}
