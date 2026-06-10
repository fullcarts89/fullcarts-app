"use client";
// Public community-submission form. Lives on /submit. Posts multipart/form-data
// to /api/submit, which creates a raw_items evidence anchor
// (source_type='community_tip') + a pending claim. Fields map 1:1 onto claims
// columns so submissions arrive structured rather than as free text.
//
// Evidence is REQUIRED: the submitter must provide a link, a photo, or both.
// Photos are downscaled/compressed in the browser (canvas → JPEG) before upload
// so a phone photo stays well under the serverless request-body limit; the
// server uploads them to the claim-images bucket and the admin queue renders
// them via the existing ClaimImage component.
//
// session_id is generated once per browser and persisted in localStorage so
// duplicate submits get caught by the 60 s rate-limit on the server.
import { useRef, useState } from "react";
import styles from "../styles.module.css";

type Status = "idle" | "submitting" | "success" | "error";
const SESSION_KEY = "fc.submit.session_id";
const MAX_DIM = 1920; // longest edge after downscale
const JPEG_QUALITY = 0.82;
const MAX_UPLOAD_BYTES = 6 * 1024 * 1024; // mirror the server backstop

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

// Downscale to MAX_DIM longest edge and re-encode as JPEG. Falls back to the
// original file if the browser can't decode it (e.g. some HEIC images) or the
// canvas pipeline throws.
async function compressImage(file: File): Promise<Blob> {
  try {
    const bitmap = await createImageBitmap(file);
    const scale = Math.min(1, MAX_DIM / Math.max(bitmap.width, bitmap.height));
    const w = Math.max(1, Math.round(bitmap.width * scale));
    const h = Math.max(1, Math.round(bitmap.height * scale));
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) return file;
    ctx.drawImage(bitmap, 0, 0, w, h);
    bitmap.close?.();
    const blob = await new Promise<Blob | null>((resolve) =>
      canvas.toBlob((b) => resolve(b), "image/jpeg", JPEG_QUALITY),
    );
    // If compression somehow made it bigger, keep the smaller original.
    if (blob && blob.size > 0 && blob.size < file.size) return blob;
    return file;
  } catch {
    return file;
  }
}

export default function SubmissionForm() {
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [photoName, setPhotoName] = useState<string | null>(null);
  const formRef = useRef<HTMLFormElement>(null);

  function onPhotoChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    setPhotoName(f ? f.name : null);
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (status === "submitting") return;

    const formEl = e.currentTarget;
    const fd = new FormData(formEl);

    const brand = String(fd.get("brand") || "").trim();
    const product_name = String(fd.get("product_name") || "").trim();
    const description = String(fd.get("description") || "").trim();
    const evidence_url = String(fd.get("evidence_url") || "").trim();
    const photoField = fd.get("photo");
    const photo =
      photoField instanceof File && photoField.size > 0 ? photoField : null;

    if (!brand || !product_name) {
      setError("Brand and product are both required.");
      setStatus("error");
      return;
    }
    if (description.length < 10) {
      setError("Please add at least a sentence describing what changed.");
      setStatus("error");
      return;
    }
    if (!evidence_url && !photo) {
      setError("Evidence is required — add a link or attach a photo.");
      setStatus("error");
      return;
    }

    setStatus("submitting");
    setError(null);

    // Build the multipart payload. Reuse the parsed text fields; replace the
    // raw photo with a compressed JPEG when one was attached.
    const out = new FormData();
    out.set("brand", brand);
    out.set("product_name", product_name);
    out.set("old_size", String(fd.get("old_size") || "").trim());
    out.set("old_size_unit", String(fd.get("old_size_unit") || "").trim());
    out.set("new_size", String(fd.get("new_size") || "").trim());
    out.set("new_size_unit", String(fd.get("new_size_unit") || "").trim());
    out.set("old_price", String(fd.get("old_price") || "").trim());
    out.set("new_price", String(fd.get("new_price") || "").trim());
    out.set("description", description);
    out.set("evidence_url", evidence_url);
    out.set("session_id", getOrCreateSessionId());

    if (photo) {
      const blob = await compressImage(photo);
      if (blob.size > MAX_UPLOAD_BYTES) {
        setError("That photo is too large even after compression — try a smaller image.");
        setStatus("error");
        return;
      }
      // Name it .jpg when we re-encoded; otherwise keep the original name/type.
      const isJpeg = blob.type === "image/jpeg" || blob !== photo;
      out.set("photo", blob, isJpeg ? "evidence.jpg" : photo.name);
    }

    try {
      const res = await fetch("/api/submit", { method: "POST", body: out });
      if (!res.ok) {
        const j = (await res.json().catch(() => ({}))) as { error?: string };
        setError(j.error || "Submission failed — please try again.");
        setStatus("error");
        return;
      }
      setStatus("success");
      formRef.current?.reset();
      setPhotoName(null);
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

      <fieldset className={styles["sub-form-evidence"]}>
        <legend>
          Evidence <span className={styles.req}>required</span>
        </legend>
        <p className={styles["sub-form-hint"]}>
          Add a link or attach a photo — at least one is required. A photo of the
          old and new packaging side by side is the strongest evidence.
        </p>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-url">Link to evidence</label>
          <input
            id="s-url"
            name="evidence_url"
            type="url"
            inputMode="url"
            maxLength={800}
            autoComplete="off"
            placeholder="https://… Reddit post, news article, retailer page"
          />
        </div>
        <div className={styles["sub-form-field"]}>
          <label htmlFor="s-photo">Or attach a photo</label>
          <input
            id="s-photo"
            name="photo"
            type="file"
            accept="image/*"
            onChange={onPhotoChange}
          />
          {photoName && (
            <span className={styles["sub-form-filename"]}>{photoName}</span>
          )}
        </div>
      </fieldset>

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
