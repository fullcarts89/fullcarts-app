"use client";
// Shared site nav. Wraps the previously-duplicated inline navs on the
// homepage, /brands, and /brands/[name]. Also bundles the background
// grid so callers only render one component.
//
// Active link is auto-detected from the current path. Products /
// Insights / About are stubs until Phase B/C/D ships — the small amber
// dot after each label flags them as work-in-progress.
//
// Hidden admin affordance: long-press the FullCarts logo for ~800ms to
// land on /admin/login. The single tap behaves normally (goes to "/").
import { usePathname } from "next/navigation";
import { useRef } from "react";
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
  {
    href: "/products",
    label: "Products",
    stub: true,
    tooltip: "Per-product detail pages coming in Phase B",
  },
  { href: "/insights", label: "Insights" },
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
      <div className={styles["bp-grid"]} />
      <nav className={styles.nav}>
        <div className={styles["nav-inner"]}>
          <a
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
