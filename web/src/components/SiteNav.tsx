"use client";
// Shared site nav. Wraps the previously-duplicated inline navs on the
// homepage, /brands, and /brands/[name]. Also bundles the background
// grid so callers only render one component.
//
// Active link is auto-detected from the current path. All four
// public sections are live; the `stub` flag is kept for the future
// admin-tool tab.
//
// Hidden admin affordance: long-press the FullCarts logo for ~800ms to
// land on /admin/login. The single tap behaves normally (goes to "/").
import { usePathname } from "next/navigation";
import { useRef } from "react";
import Link from "next/link";
import styles from "./SiteNav.module.css";

const LONG_PRESS_MS = 800;

interface NavLink {
  href: string;
  label: string;
  stub?: boolean;
  /** Tooltip when the link is a stub. */
  tooltip?: string;
}

const LINKS: NavLink[] = [
  { href: "/brands", label: "Brands" },
  { href: "/products", label: "Products" },
  { href: "/insights", label: "Insights" },
  { href: "/about", label: "About" },
];

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(href + "/");
}

export default function SiteNav() {
  const pathname = usePathname() || "/";

  // Long-press the logo to reach /admin/login. Suppress the trailing click
  // so we don't first navigate to "/" and then immediately to /admin/login.
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const fired = useRef(false);

  function startPress() {
    fired.current = false;
    timer.current = setTimeout(() => {
      fired.current = true;
      window.location.href = "/admin/login";
    }, LONG_PRESS_MS);
  }
  function cancelPress() {
    if (timer.current) {
      clearTimeout(timer.current);
      timer.current = null;
    }
  }
  function handleClick(e: React.MouseEvent<HTMLAnchorElement>) {
    if (fired.current) {
      e.preventDefault();
      fired.current = false;
    }
  }
  function handleContextMenu(e: React.MouseEvent<HTMLAnchorElement>) {
    // Suppress the long-press context menu on iOS so the press feels intentional.
    e.preventDefault();
  }

  return (
    <>
      <div className={styles["bp-grid"]} aria-hidden="true" />
      <nav className={styles.nav} aria-label="Main">
        <div className={styles["nav-inner"]}>
          <Link
            href="/"
            className={styles.logo}
            onPointerDown={startPress}
            onPointerUp={cancelPress}
            onPointerLeave={cancelPress}
            onPointerCancel={cancelPress}
            onClick={handleClick}
            onContextMenu={handleContextMenu}
          >
            Full<span>Carts</span>
          </Link>
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
                <Link
                  key={link.href}
                  href={link.href}
                  className={cls}
                  title={link.stub ? link.tooltip : undefined}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>
        </div>
      </nav>
    </>
  );
}
