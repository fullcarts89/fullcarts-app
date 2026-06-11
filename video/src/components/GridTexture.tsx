import React from "react";
import { AbsoluteFill } from "remotion";
import { theme } from "../lib/theme";

// The signature "data-grid / graph-paper" texture (from FULLCARTS_DESIGN_EXPORT.md).
// Reinforces the data-brand feel behind title cards and thumbnails.
export const GridTexture: React.FC<{ opacity?: number; cell?: number }> = ({ opacity = 0.08, cell = 48 }) => (
  <AbsoluteFill
    style={{
      opacity,
      backgroundImage: `repeating-linear-gradient(0deg, ${theme.color.textPrimary} 0px, transparent 1px, transparent ${cell}px), repeating-linear-gradient(90deg, ${theme.color.textPrimary} 0px, transparent 1px, transparent ${cell}px)`,
    }}
  />
);
