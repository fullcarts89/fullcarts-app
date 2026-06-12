import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { GridTexture } from "../components/GridTexture";

export const shrinkRevealSchema = z.object({
  imageSrc: z.string(), // real product image (cropped to the product)
  imagePosition: z.string().default("left center"),
  beforeSize: z.number(),
  afterSize: z.number(),
  unit: z.string(),
  pctChange: z.number(),
});

type Props = z.infer<typeof shrinkRevealSchema>;

// The signature "watch it shrink" cutaway: the real product scales down from its old
// size to its new size, a ghost outline marks what was lost, the size ticks down, and
// the −X% badge pops. Real product image, real numbers.
export const ShrinkReveal: React.FC<Props> = ({ imageSrc, imagePosition, beforeSize, afterSize, unit, pctChange }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const ratio = afterSize / beforeSize; // e.g. 43.5/51 = 0.853
  // hold full → shrink → hold
  const shrink = interpolate(frame, [18, 54], [1, ratio], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const size = interpolate(frame, [18, 54], [beforeSize, afterSize], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const badge = enter(frame, fps, { delay: 56, durationInFrames: 14 });

  const BOX = 560; // full footprint (square-ish stage)
  const cx = 540;
  const cy = 760;

  return (
    <AbsoluteFill style={{ background: theme.color.bg }}>
      <GridTexture opacity={0.06} />

      {/* ghost outline of original size */}
      <div
        style={{
          position: "absolute",
          left: cx - BOX / 2,
          top: cy - BOX / 2,
          width: BOX,
          height: BOX,
          border: `3px dashed ${theme.color.textTertiary}`,
          borderRadius: 24,
          opacity: 0.6,
        }}
      />

      {/* the product, scaling down */}
      <div
        style={{
          position: "absolute",
          left: cx - (BOX * shrink) / 2,
          top: cy - (BOX * shrink) / 2,
          width: BOX * shrink,
          height: BOX * shrink,
          borderRadius: 20,
          overflow: "hidden",
          background: "#fff",
        }}
      >
        <Img src={staticFile(imageSrc)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: imagePosition }} />
      </div>

      {/* ticking size label */}
      <div style={{ position: "absolute", top: 300, left: 0, right: 0, textAlign: "center" }}>
        <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 84, color: theme.color.textPrimary }}>
          {Number.isInteger(size) ? size : size.toFixed(1)} {unit}
        </span>
      </div>

      {/* −X% badge */}
      <div
        style={{
          position: "absolute",
          top: 1180,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          opacity: badge,
          transform: `scale(${interpolate(badge, [0, 1], [0.7, 1])})`,
        }}
      >
        <div
          style={{
            background: theme.color.red,
            color: theme.color.textPrimary,
            fontFamily: mono,
            fontWeight: 700,
            fontSize: 72,
            borderRadius: 16,
            padding: "10px 30px",
          }}
        >
          −{pctChange}%
        </div>
      </div>
      <div style={{ position: "absolute", top: 1300, left: 0, right: 0, textAlign: "center", fontFamily: headline, fontWeight: 500, fontSize: 38, color: theme.color.textSecondary }}>
        same can · less coffee
      </div>
    </AbsoluteFill>
  );
};
