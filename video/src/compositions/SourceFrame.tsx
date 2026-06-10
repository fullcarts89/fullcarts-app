import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { Brandmark } from "../components/Brandmark";

export const sourceFrameSchema = z.object({
  sourceName: z.string(), // e.g. "U.S. Bureau of Labor Statistics"
  url: z.string(), // e.g. "bls.gov/cpi"
  asOfDate: z.string(), // e.g. "as of 2026-06-10"
  headline: z.string(), // one-line label for what the screenshot shows
});

type Props = z.infer<typeof sourceFrameSchema>;

// Citation bar designed to sit ON TOP of a REAL screenshot (BLS/FRED chart, a
// FullCarts page, a retailer listing). Transparent → alpha. This is the toolkit's
// evidence-policy guardrail: it labels real evidence, it never fabricates a chart.
export const SourceFrame: React.FC<Props> = ({ sourceName, url, asOfDate, headline: hl }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inAnim = enter(frame, fps, { durationInFrames: 14 });

  return (
    <AbsoluteFill style={{ fontFamily: body }}>
      {/* top headline ribbon */}
      <div
        style={{
          position: "absolute",
          top: 120,
          left: 48,
          right: 48,
          opacity: inAnim,
          transform: `translateY(${interpolate(inAnim, [0, 1], [-30, 0])}px)`,
          background: theme.color.cardScrim,
          borderLeft: `6px solid ${theme.color.red}`,
          borderRadius: theme.radius.lg,
          padding: "22px 28px",
          backdropFilter: "blur(6px)",
        }}
      >
        <div style={{ fontFamily: mono, fontSize: 22, letterSpacing: 2, textTransform: "uppercase", color: theme.color.red }}>
          Real source
        </div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 40, color: theme.color.textPrimary, marginTop: 2 }}>
          {hl}
        </div>
      </div>

      {/* bottom citation bar */}
      <div
        style={{
          position: "absolute",
          bottom: 110,
          left: 48,
          right: 48,
          opacity: inAnim,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: theme.color.cardScrim,
          border: `1px solid ${theme.color.border}`,
          borderRadius: theme.radius.lg,
          padding: "20px 28px",
          backdropFilter: "blur(6px)",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 28, color: theme.color.textPrimary }}>{sourceName}</span>
          <span style={{ fontFamily: mono, fontSize: 22, color: theme.color.textSecondary }}>
            {url} · {asOfDate}
          </span>
        </div>
        <Brandmark scale={0.85} />
      </div>
    </AbsoluteFill>
  );
};
