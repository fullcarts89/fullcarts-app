import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter, fmt } from "../lib/anim";
import { INSET, safe } from "../lib/safezone";
import { Brandmark } from "../components/Brandmark";
import { MusicBed } from "../components/MusicBed";

// COMPOUND beat — the average family-of-4 grocery bill compounded forward.
// Left readout = TODAY (static base); the big readout = IN 10 YEARS, counting up
// ALONG the curve so it lands on the spoken "almost two grand". Bars are one per
// year with a real $ Y-axis + a now→+10yr X-axis. `sweepFrames` stretches the
// climb so it tracks the VO. Full-frame, opaque → render h264.
export const compoundChartSchema = z.object({
  eyebrow: z.string().default("SAME CART, COMPOUNDED"),
  base: z.number().default(1300), // $/mo today
  ratePct: z.number().default(4.2),
  years: z.number().default(10),
  rateLabel: z.string().default("@ 4.2% / yr"),
  unit: z.string().default("/mo"),
  extraNote: z.string().default("+ ~$7,940 / yr — same food"),
  bait: z.string().default("that’s the average — what’s yours? ↓ comment it"),
  source: z.string().default("USDA Moderate-Cost Food Plan · 4.2% = headline rate"),
  accent: z.enum(["red", "green", "blue", "amber"]).default("red"),
  startDelay: z.number().default(15),
  sweepFrames: z.number().default(420),
  music: z.object({ src: z.string().default("audio/bg-loop.mp3"), volume: z.number().default(0.165) }).default({}),
});

type Props = z.infer<typeof compoundChartSchema>;

const money = (n: number) => "$" + fmt(Math.round(n));

export const CompoundChart: React.FC<Props> = ({
  eyebrow, base, ratePct, years, rateLabel, unit, extraNote, bait, source, accent, startDelay, sweepFrames, music,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lf = frame - startDelay;
  const accentColor = theme.color[accent];
  const r = ratePct / 100;

  const labelIn = enter(lf, fps, { durationInFrames: 14 });
  const sweep = enter(lf, fps, { delay: 8, durationInFrames: sweepFrames });
  const extraIn = enter(lf, fps, { delay: sweepFrames + 8, durationInFrames: 16 });
  const baitIn = enter(lf, fps, { delay: sweepFrames + 22, durationInFrames: 18 });

  const n = years + 1;
  const vals = Array.from({ length: n }, (_, y) => base * Math.pow(1 + r, y));
  const final = vals[years];
  const current = base * Math.pow(1 + r, sweep * years); // climbs base→final

  // Y axis: round the top up to a clean $500 step above the final value.
  const yTop = Math.ceil(final / 500) * 500;
  const ticks = [];
  for (let v = 0; v <= yTop; v += 500) ticks.push(v);

  const TOP = safe.top;
  const CW = safe.width;
  const CH = 470;
  const padL = 96, padB = 44;
  const plotW = CW - padL;
  const plotH = CH - padB;
  const slot = plotW / n;
  const barW = slot * 0.6;
  const yOf = (v: number) => plotH - (v / yTop) * plotH;
  const chartTop = TOP + 330;
  // how far the sweep has revealed, as a year index (for the moving dot/label)
  const sweptYear = sweep * years;

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      <MusicBed src={music.src} volume={music.volume} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 28%, ${accentColor}22 0%, transparent 55%)` }} />
      <div style={{ position: "absolute", top: TOP, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Brandmark scale={1.0} />
      </div>

      {/* eyebrow + rate */}
      <div style={{ position: "absolute", top: TOP + 80, left: safe.left, width: CW, display: "flex", alignItems: "baseline", justifyContent: "space-between", opacity: labelIn }}>
        <span style={{ fontFamily: mono, fontSize: 28, letterSpacing: 4, textTransform: "uppercase", color: accentColor }}>{eyebrow}</span>
        <span style={{ fontFamily: mono, fontSize: 24, color: theme.color.textTertiary }}>{rateLabel}</span>
      </div>

      {/* TODAY vs IN 10 YEARS readouts */}
      <div style={{ position: "absolute", top: TOP + 130, left: safe.left, width: CW, display: "flex", alignItems: "flex-end", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontFamily: mono, fontSize: 22, letterSpacing: 2, textTransform: "uppercase", color: theme.color.textTertiary }}>today</div>
          <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 72, lineHeight: 1, color: theme.color.textSecondary }}>{money(base)}<span style={{ fontSize: 30 }}>{unit}</span></div>
        </div>
        <div style={{ fontFamily: mono, fontSize: 40, color: theme.color.textTertiary, paddingBottom: 18 }}>→</div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontFamily: mono, fontSize: 22, letterSpacing: 2, textTransform: "uppercase", color: accentColor }}>in {years} years</div>
          <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 96, lineHeight: 1, color: theme.color.textPrimary, textShadow: `0 0 50px ${accentColor}55` }}>{money(current)}<span style={{ fontSize: 38, color: theme.color.textSecondary }}>{unit}</span></div>
        </div>
      </div>

      {/* chart with axes */}
      <div style={{ position: "absolute", top: chartTop, left: safe.left, width: CW, height: CH }}>
        <svg width={CW} height={CH} viewBox={`0 0 ${CW} ${CH}`} style={{ display: "block", overflow: "visible" }}>
          {/* Y grid + tick labels ($) */}
          {ticks.map((t) => (
            <g key={t}>
              <line x1={padL} y1={yOf(t)} x2={CW} y2={yOf(t)} stroke={theme.color.border} strokeWidth={1} strokeDasharray="2 6" />
              <text x={padL - 12} y={yOf(t) + 7} textAnchor="end" fontFamily={mono} fontSize={20} fill={theme.color.textTertiary}>{money(t)}</text>
            </g>
          ))}
          {/* axes lines */}
          <line x1={padL} y1={0} x2={padL} y2={plotH} stroke={theme.color.textTertiary} strokeWidth={2} />
          <line x1={padL} y1={plotH} x2={CW} y2={plotH} stroke={theme.color.textTertiary} strokeWidth={2} />
          {/* bars */}
          {vals.map((v, i) => {
            const reveal = interpolate(sweep, [i / n, (i + 1) / n], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            const full = plotH - yOf(v);
            const h = full * reveal;
            const x = padL + i * slot + (slot - barW) / 2;
            const isLast = i === years;
            const col = i === 0 ? theme.color.textTertiary : isLast ? accentColor : theme.color.blue;
            return <rect key={i} x={x} y={plotH - h} width={barW} height={h} fill={col} opacity={i === 0 ? 0.55 : 0.9} rx={4} />;
          })}
          {/* X tick labels */}
          {vals.map((_, i) => (
            (i === 0 || i === 5 || i === years) ? (
              <text key={i} x={padL + i * slot + slot / 2} y={plotH + 30} textAnchor="middle" fontFamily={mono} fontSize={20} fill={i === years ? theme.color.redBright : theme.color.textTertiary}>{i === 0 ? "now" : `+${i}y`}</text>
            ) : null
          ))}
        </svg>
        {/* axis titles */}
        <div style={{ position: "absolute", left: 0, top: -2, fontFamily: mono, fontSize: 18, color: theme.color.textTertiary }}>$ / month</div>
      </div>

      {/* kicker */}
      <div style={{ position: "absolute", top: chartTop + CH + 18, left: safe.left, width: CW, fontFamily: headline, fontWeight: 600, fontSize: 38, color: accentColor, opacity: extraIn }}>{extraNote}</div>
      {/* comment bait */}
      <div style={{ position: "absolute", bottom: INSET.bottom + 30, left: safe.left, width: CW, textAlign: "center", fontFamily: headline, fontWeight: 500, fontSize: 34, color: theme.color.textPrimary, opacity: baitIn }}>{bait}</div>
      <div style={{ position: "absolute", bottom: INSET.bottom - 10, left: 0, right: 0, textAlign: "center", fontFamily: mono, fontSize: 20, color: theme.color.textTertiary }}>{source}</div>
    </AbsoluteFill>
  );
};
