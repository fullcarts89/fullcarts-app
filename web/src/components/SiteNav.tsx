"use client";
// Shared site nav. Wraps the previously-duplicated inline navs on the
// homepage, /brands, and /brands/[name]. Also bundles the background
// grid so callers only render one component.
//
// Active link is auto-detected from the current path. Products /
// Insights / About are stubs until Phase B/C/D ships — the small amber
// dot after each label flags them as work-in-progress.
import { usePathname } from "next/navigation";
import styles from "./SiteNav.module.css";

interface NavLink {
  href: string;
  label: string;
  stub?: boolean;
  /** Tooltip when the link is a stub. */
  tooltip?: string;
}

const LINKS: NavLink[] = [
  { href: "/brands", label: "Brands" },
  {
    href: "/products",
    label: "Products",
    stub: true,
    tooltip: "Per-product detail pages coming in Phase B",
  },
  {
    href: "/insights",
    label: "Insights",
    stub: true,
    tooltip: "Platform-wide trends coming in Phase C",
  },
  {
    href: "/about",
    label: "About",
    stub: true,
    tooltip: "Methodology + contact coming in Phase C",
  },
];

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(href + "/");
}

export default function SiteNav() {
  const pathname = usePathname() || "/";
  return (
    <>
      <div className={styles["bp-grid"]} />
      <nav className={styles.nav}>
        <div className={styles["nav-inner"]}>
          <a href="/" className={styles.logo}>
            Full<span>Carts</span>
          </a>
          <div className={styles["nav-links"]}>
            {LINKS.map((link) => {
              const active = isActive(pathname, link.href);
              const cls = [
                styles["nav-link"],
                active ? styles.active : "",
                link.stub ? styles.stub : "",
              ]
                .filter(Boolean)
                .join(" ");
              return (
                <a
                  key={link.href}
                  href={link.href}
                  className={cls}
                  title={link.stub ? link.tooltip : undefined}
                >
                  {link.label}
                </a>
              );
            })}
          </div>
        </div>
      </nav>
    </>
  );
}
