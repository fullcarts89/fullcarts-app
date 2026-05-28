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
 * Scene 5 (25-30s): Receipt + CTA.
 * Every claim ends with a verifiable source. The URL goes on screen
 * long enough to be screenshotted.
 */
export const CTA: React.FC<{ event: ShrinkEvent }> = ({ event }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({ frame, fps, config: { damping: 14, mass: 0.6 } });
  const scale = interpolate(pop, [0, 1], [0.85, 1]);

  const urlFade = interpolate(frame, [25, 40], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: colors.bg.primary,
        alignItems: "center",
        justifyContent: "center",
        padding: 80,
        gap: 56,
      }}
    >
      <GridPattern opacity={0.1} />

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 28,
          transform: `scale(${scale})`,
        }}
      >
        <div
          style={{
            width: 96,
            height: 96,
            borderRadius: 18,
            background: colors.red.base,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: fonts.mono,
            fontWeight: 700,
            fontSize: 42,
            color: colors.text.primary,
            letterSpacing: -2,
            boxShadow: `0 0 80px ${colors.red.base}66`,
          }}
        >
          FC
        </div>
        <div
          style={{
            fontFamily: fonts.headline,
            fontWeight: 700,
            fontSize: 88,
            color: colors.text.primary,
            letterSpacing: -2,
          }}
        >
          FullCarts
        </div>
      </div>

      <div
        style={{
          fontFamily: fonts.headline,
          fontWeight: 700,
          fontSize: 60,
          color: colors.text.primary,
          letterSpacing: -1.5,
          textAlign: "center",
          maxWidth: 900,
          lineHeight: 1.15,
        }}
      >
        Full receipts on every shrink.
      </div>

      <div
        style={{
          opacity: urlFade,
          background: colors.bg.secondary,
          border: `1px solid ${colors.red.border}`,
          borderRadius: 16,
          padding: "28px 48px",
          fontFamily: fonts.mono,
          fontWeight: 500,
          fontSize: 36,
          color: colors.red.hover,
          letterSpacing: -0.5,
        }}
      >
        fullcarts.org/products/{event.productSlug}
      </div>

      <div
        style={{
          fontFamily: fonts.mono,
          fontSize: 22,
          color: colors.text.tertiary,
          letterSpacing: 2,
          textTransform: "uppercase",
          textAlign: "center",
        }}
      >
        Built for shoppers. Not shareholders.
      </div>
    </AbsoluteFill>
  );
};
