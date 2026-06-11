import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono } from "../lib/fonts";
import { enter } from "../lib/anim";

export const rocketsFeathersSchema = z.object({
  title: z.string().default("ROCKETS & FEATHERS"),
  payLabel: z.string().default("WHAT YOU PAY"),
  getLabel: z.string().default("WHAT YOU GET"),
  note: z.string().default("up *fast* · down *slow* · *or never*"),
  zone: z.enum(["above", "chin", "full"]).default("above"),
});

// z.input → defaulted fields stay optional; FinalVideo cues pass props without zod parsing
type Props = z.input<typeof rocketsFeathersSchema>;

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

// The "rockets & feathers" economics beat as a real motion graphic instead of text:
// the price line rockets up fast then feathers down slowly; the size line steps down
// at the same moment and stays flat forever. The gap at the right edge IS the story.
// Designed for the negative space around the talking head (above / chin), schematic
// shape only — no fabricated axis numbers, the cited chart cutaway carries the data.
export const RocketsFeathers: React.FC<Props> = ({
  title = "ROCKETS & FEATHERS",
  payLabel = "WHAT YOU PAY",
  getLabel = "WHAT YOU GET",
  note = "up *fast* · down *slow* · *or never*",
  zone = "above",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cardIn = enter(frame, fps, { durationInFrames: 10 });
  // both lines draw left→right together so the divergence reads as one event
  const draw = enter(frame, fps, { delay: 8, durationInFrames: 50 });
  const labelsIn = enter(frame, fps, { delay: 52, durationInFrames: 12 });
  const noteIn = enter(frame, fps, { delay: 62, durationInFrames: 12 });
  // the lost-value gap pulses once after the lines settle
  const gapIn = enter(frame, fps, { delay: 58, durationInFrames: 14 });

  const compact = zone === "chin";
  const top = zone === "above" ? 330 : zone === "chin" ? 1200 : 560;
  const chartH = compact ? 170 : 290;

  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          top,
          left: 60,
          right: 170,
          background: theme.color.cardScrim,
          border: `1px solid ${theme.color.border}`,
          borderRadius: theme.radius.lg,
          padding: compact ? "14px 22px 10px" : "20px 26px 16px",
          opacity: cardIn,
          transform: `translateY(${interpolate(cardIn, [0, 1], [24, 0])}px)`,
        }}
      >
        <div style={{ fontFamily: mono, fontSize: compact ? 22 : 26, letterSpacing: 4, color: theme.color.red }}>
          {title}
        </div>

        <svg width="100%" viewBox={`0 0 760 ${chartH + 30}`} style={{ display: "block", marginTop: 6 }}>
          {/* baseline */}
          <line x1="14" y1={chartH + 14} x2="746" y2={chartH + 14} stroke={theme.color.border} strokeWidth="2" />

          {/* the permanent gap between pay and get, revealed after the lines land */}
          <rect
            x="600"
            y={chartH * 0.38}
            width="146"
            height={chartH * 0.22}
            fill={theme.color.red}
            opacity={gapIn * 0.16}
          />

          {/* WHAT YOU GET — steps down at the shock, never recovers */}
          <path
            d={`M14,${chartH * 0.42} L168,${chartH * 0.42} L196,${chartH * 0.6} L746,${chartH * 0.6}`}
            fill="none"
            stroke={theme.color.textPrimary}
            strokeWidth="5"
            strokeLinecap="round"
            strokeLinejoin="round"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - draw}
          />

          {/* WHAT YOU PAY — rockets up, feathers down, lands well above where it started */}
          <path
            d={`M14,${chartH * 0.92} L120,${chartH * 0.86} L182,${chartH * 0.12} C 300,${chartH * 0.16} 520,${chartH * 0.3} 746,${chartH * 0.38}`}
            fill="none"
            stroke={theme.color.red}
            strokeWidth="7"
            strokeLinecap="round"
            strokeLinejoin="round"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - draw}
          />

          {/* series labels — pay sits above the feathering slope, get below its line */}
          <text
            x="430"
            y={chartH * 0.14}
            textAnchor="middle"
            fontFamily={mono}
            fontSize={compact ? 20 : 24}
            fontWeight="700"
            fill={theme.color.red}
            opacity={labelsIn}
          >
            {payLabel}
          </text>
          <text
            x="742"
            y={chartH * 0.6 + (compact ? 26 : 32)}
            textAnchor="end"
            fontFamily={mono}
            fontSize={compact ? 20 : 24}
            fontWeight="700"
            fill={theme.color.textPrimary}
            opacity={labelsIn}
          >
            {getLabel}
          </text>
        </svg>

        <div
          style={{
            fontFamily: headline,
            fontWeight: 700,
            fontSize: compact ? 30 : 38,
            textAlign: "center",
            color: theme.color.textPrimary,
            marginTop: 2,
            opacity: noteIn,
            transform: `translateY(${interpolate(noteIn, [0, 1], [12, 0])}px)`,
          }}
        >
          {parse(note, theme.color.red)}
        </div>
      </div>
    </AbsoluteFill>
  );
};
