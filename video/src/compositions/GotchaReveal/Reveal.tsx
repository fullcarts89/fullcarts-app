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
import { ProductSilhouette } from "../../components/ProductSilhouette";
import type { ShrinkEvent } from "../../data/types";

/**
 * Scene 2 (3-10s): Product reveal.
 * Show the actual thing under discussion + the offender tag.
 * Pulls a real product image when available, falls back to a styled card.
 */
export const Reveal: React.FC<{ event: ShrinkEvent }> = ({ event }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const lift = spring({
    frame,
    fps,
    config: { damping: 16, mass: 0.7 },
  });
  const translateY = interpolate(lift, [0, 1], [60, 0]);
  const fade = interpolate(frame, [0, 16], [0, 1], {
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
      }}
    >
      <GridPattern opacity={0.08} />

      <div
        style={{
          transform: `translateY(${translateY}px)`,
          opacity: fade,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 40,
        }}
      >
        {event.category ? (
          <div
            style={{
              fontFamily: fonts.mono,
              fontSize: 22,
              color: colors.text.secondary,
              letterSpacing: 4,
              textTransform: "uppercase",
            }}
          >
            {event.category}
          </div>
        ) : null}

        <ProductSilhouette
          imageUrl={event.productImageUrl}
          brand={event.brand}
          productName={event.productName}
          size={640}
        />

        <div style={{ textAlign: "center" }}>
          <div
            style={{
              fontFamily: fonts.mono,
              fontSize: 30,
              fontWeight: 500,
              color: colors.red.hover,
              letterSpacing: 3,
              textTransform: "uppercase",
              marginBottom: 16,
            }}
          >
            {event.brand}
          </div>
          <div
            style={{
              fontFamily: fonts.headline,
              fontSize: 64,
              fontWeight: 700,
              color: colors.text.primary,
              letterSpacing: -1.5,
              lineHeight: 1.1,
              maxWidth: 900,
            }}
          >
            {event.productName}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
