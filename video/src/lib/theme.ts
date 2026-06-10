// FullCarts design tokens — mirrored from FULLCARTS_DESIGN_EXPORT.md / web globals.css.
// Single source of truth for the video toolkit so every overlay is on-brand.
export const theme = {
  color: {
    bg: "#0a0b0d", // deep graphite
    card: "#161719",
    cardScrim: "rgba(10,11,13,0.92)", // overlay card bg, readable over footage
    border: "rgba(255,255,255,0.12)",
    textPrimary: "#f5f4f0", // cream
    textSecondary: "#a0a0a5",
    textTertiary: "#80808a",
    red: "#dc2626", // alert red — shrinkflation
    redBright: "#ef4444",
    green: "#10b981", // signal green — restoration / positive
    blue: "#3b82f6",
    amber: "#f59e0b",
  },
  radius: { sm: 8, md: 12, lg: 16, xl: 24 },
} as const;

export type ChangeMode = "shrink" | "restoration";

// Accent + sign helpers so shrink (red, −) and restoration (green, +) share one code path.
export const accentFor = (mode: ChangeMode) =>
  mode === "restoration" ? theme.color.green : theme.color.red;
export const signFor = (mode: ChangeMode) => (mode === "restoration" ? "+" : "−");
