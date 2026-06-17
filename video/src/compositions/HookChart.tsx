import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono } from "../lib/fonts";
import { enter, countUp } from "../lib/anim";

export const hookChartSchema = z.object({
  title: z.string().default("SAME PRICE · LESS PRODUCT"),
  // anchored panel; defaults sit in the upper-right (above the hand), inside the safe zone
  top: z.number().default(300),
  right: z.number().default(170),
  width: z.number().default(500),
  items: z.array(
    z.object({
      label: z.string(), // e.g. "SWIFFER"
      before: z.number(),
      after: z.number(),
      unit: z.string(),
      pct: z.number(), // positive magnitude
    })
  ),
});

type Props = z.infer<typeof hookChartSchema>;

const Bar: React.FC<{ before: number; after: number; unit: string; pct: number; label: string; delay: number }> = ({ before, after, unit, pct, label, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const rowIn = enter(frame, fps, { delay, durationInFrames: 12 });
  const grow = enter(frame, fps, { delay: delay + 6, durationInFrames: 20 });
  const pctVal = countUp(frame, fps, pct, { delay: delay + 8, durationInFrames: 22, decimals: 1 });
  const max = Math.max(before, after);
  const beforeW = (before / max) * 100;
  const afterW = (after / max) * 100 * grow;
  return (
    <div style={{ opacity: rowIn, transform: `translateY(${interpolate(rowIn, [0, 1], [16, 0])}px)`, display: "flex", flexDirection: "column", gap: 6 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <span style={{ fontFamily: mono, fontSize: 26, letterSpacing: 2, color: theme.color.textPrimary }}>{label}</span>
        <span style={{ fontFamily: mono, fontSize: 24, color: theme.color.textTertiary }}>{before}→{after} {unit}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
        <div style={{ height: 14, width: `${beforeW}%`, background: theme.color.textTertiary, opacity: 0.4, borderRadius: 4, minWidth: 20 }} />
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ height: 14, width: `${afterW}%`, background: theme.color.red, borderRadius: 4, minWidth: 20 }} />
          <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 30, color: theme.color.red, whiteSpace: "nowrap" }}>−{pctVal}%</span>
        </div>
      </div>
    </div>
  );
};

// Compact, transparent before→after bar panel that floats in the negative space
// (upper-right by default — "above the hand") without cutting away from the face.
// Built from real DB numbers; the hook's signature visual.
export const HookChart: React.FC<Props> = ({ title, top, right, width, items }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const panelIn = enter(frame, fps, { durationInFrames: 12 });
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          top,
          right,
          width,
          opacity: panelIn,
          transform: `translateY(${interpolate(panelIn, [0, 1], [-18, 0])}px)`,
          background: theme.color.cardScrim,
          border: `1px solid ${theme.color.border}`,
          borderLeft: `6px solid ${theme.color.red}`,
          borderRadius: theme.radius.xl,
          padding: "26px 30px",
          backdropFilter: "blur(6px)",
          display: "flex",
          flexDirection: "column",
          gap: 22,
        }}
      >
        <div style={{ fontFamily: mono, fontSize: 24, letterSpacing: 3, color: theme.color.red }}>{title}</div>
        {items.map((it, i) => (
          <Bar key={i} {...it} delay={10 + i * 8} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
