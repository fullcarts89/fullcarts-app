import SiteNav from "@/components/SiteNav";
import styles from "./styles.module.css";

export default function BrandNotFound() {
  return (
    <>
      <SiteNav />
      <div className={styles.container}>
        <div style={{ padding: "120px 0 80px", textAlign: "center" }}>
          <h1
            style={{
              fontFamily: "var(--font-headline)",
              fontWeight: 700,
              fontSize: "clamp(40px, 7vw, 72px)",
              letterSpacing: "-0.02em",
              marginBottom: 16,
            }}
          >
            Brand not found
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 18 }}>
            We don&apos;t have a record for that brand yet.{" "}
            <a href="/" style={{ color: "var(--red-base)" }}>
              Back home →
            </a>
          </p>
        </div>
      </div>
    </>
  );
}
