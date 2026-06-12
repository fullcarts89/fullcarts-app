import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter, countUp, fmt } from "../lib/anim";
import { INSET, safe } from "../lib/safezone";
import { Brandmark } from "../components/Brandmark";

export const statCardSchema = z.object({
  value: z.number(), // the target number, e.g. 2228 or 12.5
  decimals: z.number().default(0), // decimal places for the count-up
  prefix: z.string().default(""), // e.g. "−" or "+"
  suffix: z.string().default(""), // e.g. "%" or ""
  label: z.string(), // small uppercase eyebrow, e.g. "DOCUMENTED SHRINKS"
  context: z.string(), // one supporting line under the number
  source: z.string(), // citation line at the bottom
  accent: z.enum(["red", "green", "blue", "amber"]).default("red"),
});

type Props = z.infer<typeof statCardSchema>;

// Full-frame big-number card (opaque). For "by the numbers" hooks, the database
// counter (count-up to 2,228), and CPI newsjack headlines. Render as standard mp4.
export const StatCard: React.FC<Props> = ({ value, decimals, prefix, suffix, label, context, source, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accentColor = theme.color[accent];

  const labelIn = enter(frame, fps, { durationInFrames: 14 });
  const n = countUp(frame, fps, value, { delay: 6, durationInFrames: 42, decimals });
  const contextIn = enter(frame, fps, { delay: 30, durationInFrames: 16 });

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      {/* subtle accent glow */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% 38%, ${accentColor}22 0%, transparent 55%)`,
        }}
      />
      <div style={{ position: "absolute", top: safe.top, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Brandmark scale={1.1} />
      </div>

      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", padding: 80 }}>
        <div
          style={{
            fontFamily: mono,
            fontSize: 34,
            letterSpacing: 4,
            textTransform: "uppercase",
            color: accentColor,
            opacity: labelIn,
            transform: `translateY(${interpolate(labelIn, [0, 1], [20, 0])}px)`,
          }}
        >
          {label}
        </div>

        <div
          style={{
            fontFamily: mono,
            fontWeight: 700,
            fontSize: 210,
            lineHeight: 1,
            color: theme.color.textPrimary,
            marginTop: 16,
            textShadow: `0 0 60px ${accentColor}55`,
          }}
        >
          {prefix}
          {fmt(n, decimals)}
          {suffix}
        </div>

        <div
          style={{
            fontFamily: headline,
            fontWeight: 500,
            fontSize: 46,
            textAlign: "center",
            color: theme.color.textSecondary,
            maxWidth: 700, // keep centered text inside the right action-rail safe zone
            marginTop: 28,
            opacity: contextIn,
          }}
        >
          {context}
        </div>
      </AbsoluteFill>

      <div
        style={{
          position: "absolute",
          bottom: INSET.bottom,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: mono,
          fontSize: 24,
          color: theme.color.textTertiary,
        }}
      >
        {source}
      </div>
    </AbsoluteFill>
  );
};
