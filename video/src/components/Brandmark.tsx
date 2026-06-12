import React from "react";
import { theme } from "../lib/theme";
import { headline, mono } from "../lib/fonts";

// The FullCarts wordmark — rendered (FC red box + Space Grotesk wordmark) since the
// repo has no logo asset. Matches FULLCARTS_DESIGN_EXPORT.md §10.
export const Brandmark: React.FC<{ scale?: number }> = ({ scale = 1 }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 10 * scale }}>
    <div
      style={{
        width: 44 * scale,
        height: 44 * scale,
        borderRadius: 10 * scale,
        background: theme.color.red,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 20 * scale, color: theme.color.textPrimary }}>
        FC
      </span>
    </div>
    <span
      style={{
        fontFamily: headline,
        fontWeight: 700,
        fontSize: 26 * scale,
        letterSpacing: -0.5,
        color: theme.color.textPrimary,
      }}
    >
      FullCarts
    </span>
  </div>
);
