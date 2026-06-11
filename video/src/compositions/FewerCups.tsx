import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono } from "../lib/fonts";
import { enter } from "../lib/anim";

export const fewerCupsSchema = z.object({
  before: z.number(), // e.g. 51 (oz) or cups-per-can off the real label
  after: z.number(),
  unitLabel: z.string(), // e.g. "oz of coffee" / "cups per can"
  perIcon: z.number().default(5), // how much one icon represents
  decimals: z.number().default(1), // decimals for the lost-amount count-up
  subline: z.string().default("same shelf price."),
  zone: z.enum(["above", "chin"]).default("above"),
});

// z.input → defaulted fields stay optional; FinalVideo cues pass props without zod parsing
type Props = z.input<typeof fewerCupsSchema>;

const fmtLoose = (n: number, decimals: number) =>
  n.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: decimals });

const Cup: React.FC<{ size: number; color: string; opacity: number; drop: number }> = ({ size, color, opacity, drop }) => (
  <svg width={size} height={size} viewBox="0 0 48 48" style={{ opacity, transform: `translateY(${drop}px)` }}>
    {/* simple mug: body + handle + steam-free, reads at 40px */}
    <path d="M8 14 h26 v18 a8 8 0 0 1 -8 8 h-10 a8 8 0 0 1 -8 -8 z" fill={color} />
    <path d="M34 18 h4 a6 6 0 0 1 0 12 h-4 v-5 h3.4 a1.4 1.4 0 0 0 0 -2.8 H34 z" fill={color} />
  </svg>
);

// The "what you actually lost" visual: a grid of cups pops in, then the lost ones
// turn red and drop out while the deficit counts up. Quantities must be real —
// off the can label or the approved-claims registry, never estimated.
export const FewerCups: React.FC<Props> = ({ before, after, unitLabel, perIcon = 5, decimals = 1, subline = "same shelf price.", zone = "above" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const lost = before - after;
  const iconsTotal = Math.max(1, Math.round(before / perIcon));
  const iconsLost = Math.min(iconsTotal, Math.max(1, Math.round(lost / perIcon)));

  const cardIn = enter(frame, fps, { durationInFrames: 10 });
  const countIn = enter(frame, fps, { delay: 34, durationInFrames: 30 });
  const lostAmt = interpolate(countIn, [0, 1], [0, lost]);
  const sublineIn = enter(frame, fps, { delay: 58, durationInFrames: 12 });

  const top = zone === "above" ? 340 : 1200;
  const iconSize = iconsTotal > 14 ? 40 : 52;

  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          top,
          left: 60,
          right: 170,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          background: theme.color.cardScrim,
          border: `1px solid ${theme.color.border}`,
          borderRadius: theme.radius.lg,
          padding: "18px 26px 14px",
          opacity: cardIn,
          transform: `translateY(${interpolate(cardIn, [0, 1], [24, 0])}px)`,
        }}
      >
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 6, maxWidth: 720 }}>
          {Array.from({ length: iconsTotal }, (_, i) => {
            const isLost = i >= iconsTotal - iconsLost;
            const popIn = enter(frame, fps, { delay: 6 + i * 1.5, durationInFrames: 8 });
            // the lost cups turn red and sink after the grid settles
            const out = isLost ? enter(frame, fps, { delay: 36 + (i - (iconsTotal - iconsLost)) * 3, durationInFrames: 12 }) : 0;
            return (
              <Cup
                key={i}
                size={iconSize}
                color={isLost && out > 0.2 ? theme.color.red : theme.color.textPrimary}
                opacity={popIn * (1 - out * 0.72)}
                drop={interpolate(popIn, [0, 1], [10, 0]) + out * 8}
              />
            );
          })}
        </div>

        <div style={{ display: "flex", alignItems: "baseline", gap: 16, marginTop: 8 }}>
          <span
            style={{
              fontFamily: mono,
              fontWeight: 700,
              fontSize: 96,
              lineHeight: 1,
              color: theme.color.red,
              textShadow: `0 0 ${Math.round(countIn * 40)}px ${theme.color.red}88`,
            }}
          >
            −{fmtLoose(lostAmt, decimals)}
          </span>
          <span style={{ fontFamily: headline, fontWeight: 700, fontSize: 40, color: theme.color.textPrimary }}>
            {unitLabel}
          </span>
        </div>

        <div
          style={{
            fontFamily: headline,
            fontWeight: 700,
            fontSize: 32,
            color: theme.color.textSecondary,
            marginTop: 4,
            opacity: sublineIn,
            transform: `translateY(${interpolate(sublineIn, [0, 1], [10, 0])}px)`,
          }}
        >
          {subline}
        </div>
      </div>
    </AbsoluteFill>
  );
};
