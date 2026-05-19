import Link from "next/link";
import SiteNav from "@/components/SiteNav";
import { EVIDENCE_CHANNELS } from "../../_lib/evidence-tags";
import styles from "./styles.module.css";

export default function EvidenceNotFound() {
  return (
    <>
      <SiteNav />
      <div className={styles.container}>
        <div className={styles.breadcrumb}>
          <Link href="/">Home</Link>
          <span className={styles.sep}>/</span>
          <span className={styles.current}>Evidence channel</span>
        </div>
        <div className={styles.empty}>
          <p style={{ marginBottom: 24, fontSize: 18, color: "var(--text-primary)" }}>
            That evidence channel doesn&rsquo;t exist.
          </p>
          <p style={{ marginBottom: 24, color: "var(--text-secondary)" }}>
            Try one of the channels we do track:
          </p>
          <div className={styles.channelsRow} style={{ justifyContent: "center" }}>
            {EVIDENCE_CHANNELS.map((c) => (
              <Link
                key={c.slug}
                href={`/evidence/${c.slug}`}
                className={styles.channelChip}
              >
                {c.title}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
