import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme, accentFor, signFor } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { INSET, safe } from "../lib/safezone";

export const rundownChipSchema = z.object({
  rank: z.number(), // 1..5
  brand: z.string(),
  productName: z.string(),
  sizeBefore: z.number(),
  sizeAfter: z.number(),
  unit: z.string(),
  pctChange: z.number(),
  mode: z.enum(["shrink", "restoration"]).default("shrink"),
  // Off for the green-screen review cut — the product photo behind already shows the brand.
  showBrand: z.boolean().default(true),
});

type Props = z.infer<typeof rundownChipSchema>;

// Compact ranked chip for the "5 things that shrank" rundown. Transparent → render
// with alpha, one per item, drop each over its product b-roll beat in Captions.
export const RundownChip: React.FC<Props> = ({ rank, brand, productName, sizeBefore, sizeAfter, unit, pctChange, mode, showBrand }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = accentFor(mode);

  const chipIn = enter(frame, fps, { durationInFrames: 14 });
  const x = interpolate(chipIn, [0, 1], [-90, 0]);

  return (
    <AbsoluteFill style={{ fontFamily: body }}>
      <div
        style={{
          position: "absolute",
          left: safe.left,
          right: INSET.right, // clear the right action-rail
          bottom: INSET.bottom, // sit above the caption/handle zone
          opacity: chipIn,
          transform: `translateX(${x}px)`,
          display: "flex",
          alignItems: "center",
          gap: 28,
          background: theme.color.cardScrim,
          border: `1px solid ${theme.color.border}`,
          borderRadius: theme.radius.xl,
          padding: "28px 36px",
          backdropFilter: "blur(6px)",
        }}
      >
        <div
          style={{
            fontFamily: mono,
            fontWeight: 700,
            fontSize: 96,
            lineHeight: 1,
            color: accent,
            minWidth: 110,
            textAlign: "center",
          }}
        >
          {rank}
        </div>
        <div style={{ flex: 1 }}>
          {showBrand && (
            <div style={{ fontFamily: mono, fontSize: 24, letterSpacing: 2, textTransform: "uppercase", color: theme.color.textSecondary }}>
              {brand}
            </div>
          )}
          <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 44, color: theme.color.textPrimary }}>
            {productName}
          </div>
          <div style={{ fontFamily: mono, fontSize: 30, color: theme.color.textSecondary, marginTop: 4 }}>
            {sizeBefore} → {sizeAfter} {unit}
          </div>
        </div>
        <div
          style={{
            background: accent,
            color: theme.color.textPrimary,
            fontFamily: mono,
            fontWeight: 700,
            fontSize: 48,
            borderRadius: theme.radius.lg,
            padding: "10px 20px",
            whiteSpace: "nowrap",
          }}
        >
          {signFor(mode)}
          {pctChange}%
        </div>
      </div>
    </AbsoluteFill>
  );
};
