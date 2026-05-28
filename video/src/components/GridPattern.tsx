import React from "react";
import { AbsoluteFill } from "remotion";
import { colors } from "../theme";

/**
 * Subtle dotted/grid background matching the hero pattern on fullcarts.org.
 * Pure SVG so it scales crisply at any video resolution.
 */
export const GridPattern: React.FC<{ opacity?: number }> = ({
  opacity = 0.08,
}) => {
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity }}>
      <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern
            id="grid"
            width="60"
            height="60"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 60 0 L 0 0 0 60"
              fill="none"
              stroke={colors.text.primary}
              strokeWidth="1"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>
    </AbsoluteFill>
  );
};
