import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono } from "../lib/fonts";
import { enter } from "../lib/anim";

export const priceJumpSchema = z.object({
  label: z.string(), // mono eyebrow, e.g. "PRICE PER OZ — FOLGERS BIG CAN"
  before: z.number(),
  after: z.number(),
  prefix: z.string().default(""), // e.g. "$"
  suffix: z.string().default(""), // e.g. "¢" or "¢ / oz"
  decimals: z.number().default(0), // max decimals shown (trailing zeros dropped)
  context: z.string().default(""), // one line under the number, *highlights* in red
  zone: z.enum(["above", "chin"]).default("above"),
});

// z.input → defaulted fields stay optional; FinalVideo cues pass props without zod parsing
type Props = z.input<typeof priceJumpSchema>;

const parse = (text: string, color: string) =>
  text.split("*").map((seg, i) =>
    i % 2 === 1 ? (
      <span key={i} style={{ color }}>
        {seg}
      </span>
    ) : (
      <React.Fragment key={i}>{seg}</React.Fragment>
    )
  );

// drop trailing zeros so 22 → "22", 59.5 → "59.5" at decimals=1
const fmtLoose = (n: number, decimals: number) =>
  n.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: decimals });

// The price count-up beat: the old unit price sits struck-through while the live
// number ticks up from old → new and lands with a red glow. Negative-space panel —
// the face stays on screen. Numbers must come from the approved-claims registry.
export const PriceJump: React.FC<Props> = ({ label, before, after, prefix = "", suffix = "", decimals = 0, context = "", zone = "above" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cardIn = enter(frame, fps, { durationInFrames: 10 });
  const tick = enter(frame, fps, { delay: 10, durationInFrames: 38 });
  const contextIn = enter(frame, fps, { delay: 46, durationInFrames: 12 });
  const n = interpolate(tick, [0, 1], [before, after]);
  // glow swells as the number lands
  const glow = interpolate(tick, [0.75, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const top = zone === "above" ? 360 : 1210;

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
        <div style={{ fontFamily: mono, fontSize: 24, letterSpacing: 3, color: theme.color.textSecondary, textTransform: "uppercase" }}>
          {label}
        </div>

        <div style={{ display: "flex", alignItems: "baseline", gap: 26, marginTop: 6 }}>
          <span
            style={{
              fontFamily: mono,
              fontWeight: 700,
              fontSize: 58,
              color: theme.color.textTertiary,
              textDecoration: "line-through",
              textDecorationColor: theme.color.red,
              textDecorationThickness: 5,
            }}
          >
            {prefix}
            {fmtLoose(before, decimals)}
            {suffix}
          </span>
          <span style={{ fontFamily: mono, fontSize: 48, color: theme.color.textTertiary }}>→</span>
          <span
            style={{
              fontFamily: mono,
              fontWeight: 700,
              fontSize: 120,
              lineHeight: 1,
              color: theme.color.red,
              textShadow: `0 0 ${Math.round(glow * 50)}px ${theme.color.red}aa`,
            }}
          >
            {prefix}
            {fmtLoose(n, decimals)}
            {suffix}
          </span>
        </div>

        {context ? (
          <div
            style={{
              fontFamily: headline,
              fontWeight: 700,
              fontSize: 34,
              textAlign: "center",
              color: theme.color.textPrimary,
              marginTop: 10,
              opacity: contextIn,
              transform: `translateY(${interpolate(contextIn, [0, 1], [12, 0])}px)`,
            }}
          >
            {parse(context, theme.color.red)}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
