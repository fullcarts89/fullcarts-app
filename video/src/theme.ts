/**
 * FullCarts design tokens, mirrored from the web app
 * (FULLCARTS_DESIGN_EXPORT.md + web/src/app/globals.css).
 *
 * Keep these in sync with the web theme so videos and the site
 * look like one product.
 */
export const colors = {
  bg: {
    primary: "#0a0b0d",
    secondary: "#161719",
    tertiary: "#2a2b2d",
    hover: "#1a1b1d",
  },
  text: {
    primary: "#f5f4f0",
    secondary: "#a0a0a5",
    tertiary: "#80808a",
  },
  red: {
    base: "#dc2626",
    hover: "#ef4444",
    bg: "rgba(220, 38, 38, 0.1)",
    border: "rgba(220, 38, 38, 0.2)",
  },
  green: {
    base: "#10b981",
  },
  blue: {
    base: "#3b82f6",
  },
  amber: {
    base: "#f59e0b",
  },
  border: {
    subtle: "rgba(255, 255, 255, 0.1)",
    medium: "rgba(255, 255, 255, 0.2)",
  },
} as const;

export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  pill: 9999,
} as const;
