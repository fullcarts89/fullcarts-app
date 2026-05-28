import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { colors } from "../../theme";
import { fonts } from "../../fonts";
import { GridPattern } from "../../components/GridPattern";
import type { ShrinkEvent } from "../../data/types";

/**
 * Scene 1 (0-3s): The hook.
 * The number throws the punch. Per the social-content-engine doc's
 * "Product/Outcome Showcase" winner: shocking result first, explain later.
 */
export const Hook: React.FC<{ event: ShrinkEvent }> = ({ event }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.6, stiffness: 180 },
  });
  const scale = interpolate(pop, [0, 1], [0.6, 1]);

  const captionOpacity = interpolate(frame, [18, 30], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  const pctText = `${event.sizeDeltaPct}%`;

  return (
    <AbsoluteFill
      style={{
        background: colors.bg.primary,
        alignItems: "center",
        justifyContent: "center",
        padding: 80,
      }}
    >
      <GridPattern opacity={0.12} />

      <div
        style={{
          fontFamily: fonts.mono,
          fontSize: 28,
          color: colors.red.hover,
          letterSpacing: 4,
          textTransform: "uppercase",
          marginBottom: 36,
          opacity: interpolate(frame, [0, 12], [0, 1], {
            extrapolateRight: "clamp",
            extrapolateLeft: "clamp",
          }),
        }}
      >
        Caught
      </div>

      <div
        style={{
          fontFamily: fonts.mono,
          fontSize: 360,
          fontWeight: 700,
          color: colors.red.base,
          lineHeight: 1,
          transform: `scale(${scale})`,
          textShadow: `0 0 120px ${colors.red.base}55`,
          letterSpacing: -8,
        }}
      >
        {pctText}
      </div>

      <div
        style={{
          marginTop: 48,
          maxWidth: 900,
          textAlign: "center",
          fontFamily: fonts.headline,
          fontSize: 56,
          fontWeight: 700,
          color: colors.text.primary,
          letterSpacing: -1.5,
          lineHeight: 1.15,
          opacity: captionOpacity,
        }}
      >
        {event.brand} just shrunk
        <br />
        {event.productName}.
      </div>
    </AbsoluteFill>
  );
};
