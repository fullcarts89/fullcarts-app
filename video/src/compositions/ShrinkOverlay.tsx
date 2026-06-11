import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme, accentFor, signFor } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { INSET, safe } from "../lib/safezone";
import { Brandmark } from "../components/Brandmark";

export const shrinkOverlaySchema = z.object({
  brand: z.string(),
  productName: z.string(),
  sizeBefore: z.number(),
  sizeAfter: z.number(),
  unit: z.string(),
  pctChange: z.number(), // positive magnitude, e.g. 12.5
  source: z.string(), // e.g. "FullCarts • retailer listing"
  observedDate: z.string(), // e.g. "Observed 2022-06"
  mode: z.enum(["shrink", "restoration"]).default("shrink"),
});

type Props = z.infer<typeof shrinkOverlaySchema>;

// Lower-third before→after card. Transparent background → render with alpha and
// composite over your talking-head footage in Captions App.
export const ShrinkOverlay: React.FC<Props> = ({
  brand,
  productName,
  sizeBefore,
  sizeAfter,
  unit,
  pctChange,
  source,
  observedDate,
  mode,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = accentFor(mode);

  const cardIn = enter(frame, fps, { durationInFrames: 16 });
  const y = interpolate(cardIn, [0, 1], [80, 0]);
  const barGrow = enter(frame, fps, { delay: 10, durationInFrames: 22 });
  const badge = enter(frame, fps, { delay: 16, durationInFrames: 14 });

  // Before/after bar widths (relative to the larger value).
  const max = Math.max(sizeBefore, sizeAfter);
  const beforeW = (sizeBefore / max) * 100;
  const afterW = (sizeAfter / max) * 100 * barGrow;

  return (
    <AbsoluteFill style={{ fontFamily: body }}>
      <div
        style={{
          position: "absolute",
          left: safe.left,
          right: INSET.right, // clear the right action-rail
          bottom: INSET.bottom, // sit above the caption/handle zone
          opacity: cardIn,
          transform: `translateY(${y}px)`,
          background: theme.color.cardScrim,
          border: `1px solid ${theme.color.border}`,
          borderLeft: `6px solid ${accent}`,
          borderRadius: theme.radius.xl,
          padding: "40px 44px",
          backdropFilter: "blur(6px)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ fontFamily: mono, fontSize: 26, letterSpacing: 2, textTransform: "uppercase", color: accent }}>
              {brand}
            </div>
            <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 46, color: theme.color.textPrimary, marginTop: 4 }}>
              {productName}
            </div>
          </div>
          <div
            style={{
              opacity: badge,
              transform: `scale(${interpolate(badge, [0, 1], [0.7, 1])})`,
              background: accent,
              color: theme.color.textPrimary,
              fontFamily: mono,
              fontWeight: 700,
              fontSize: 52,
              borderRadius: theme.radius.lg,
              padding: "10px 22px",
              whiteSpace: "nowrap",
            }}
          >
            {signFor(mode)}
            {pctChange}%
          </div>
        </div>

        {/* Before → after bars */}
        <div style={{ marginTop: 30, display: "flex", flexDirection: "column", gap: 16 }}>
          <Row label={`${sizeBefore} ${unit}`} width={beforeW} color={theme.color.textTertiary} faded />
          <Row label={`${sizeAfter} ${unit}`} width={afterW} color={accent} />
        </div>

        <div style={{ marginTop: 30, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontFamily: mono, fontSize: 22, color: theme.color.textSecondary }}>
            {source} · {observedDate}
          </span>
          <Brandmark scale={0.9} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Row: React.FC<{ label: string; width: number; color: string; faded?: boolean }> = ({
  label,
  width,
  color,
  faded,
}) => (
  <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
    <div
      style={{
        height: 30,
        width: `${width}%`,
        background: color,
        opacity: faded ? 0.45 : 1,
        borderRadius: 6,
        minWidth: 40,
      }}
    />
    <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 32, color: theme.color.textPrimary }}>{label}</span>
  </div>
);
