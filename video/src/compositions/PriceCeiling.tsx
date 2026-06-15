import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { INSET, safe } from "../lib/safezone";
import { Brandmark } from "../components/Brandmark";
import { MusicBed } from "../components/MusicBed";

// TAKE beat — the price climbs toward a ceiling it can't cross ($20 box). When
// it reaches the ceiling it CAN'T go higher, so it flattens (price capped) — and
// the takeaway is they shrink the box instead. Labelled $ Y-axis + time X-axis.
// No downward deflection, no mystery icons. h264.
export const priceCeilingSchema = z.object({
  eyebrow: z.string().default("THE CEILING YOU WON’T CROSS"),
  ceiling: z.number().default(20),
  ceilingLabel: z.string().default("$20 box — you’ll never pay this"),
  cappedLabel: z.string().default("price hits the wall"),
  deflectLabel: z.string().default("so they shrink the box instead"),
  punch: z.string().default("shrinkflation is the pressure-release valve"),
  source: z.string().default("FullCarts · the mechanism"),
  startDelay: z.number().default(6),
  music: z.object({ src: z.string().default("audio/bg-loop.mp3"), volume: z.number().default(0.165) }).default({}),
});

type Props = z.infer<typeof priceCeilingSchema>;

export const PriceCeiling: React.FC<Props> = ({ eyebrow, ceiling, ceilingLabel, cappedLabel, deflectLabel, punch, source, startDelay, music }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lf = frame - startDelay;

  const labelIn = enter(lf, fps, { durationInFrames: 14 });
  const axisIn = enter(lf, fps, { delay: 8, durationInFrames: 14 });
  const sweep = enter(lf, fps, { delay: 20, durationInFrames: 80 });
  const deflectIn = enter(lf, fps, { delay: 92, durationInFrames: 18 });
  const punchIn = enter(lf, fps, { delay: 110, durationInFrames: 18 });

  const TOP = safe.top;
  const CW = safe.width;
  const H = 470;
  const padL = 78, padB = 44;
  const plotW = CW - padL, plotH = H - padB;
  const yTop = ceiling + 4;
  const xOf = (f: number) => padL + f * plotW;
  const yOf = (v: number) => plotH - (v / yTop) * plotH;
  const cy = yOf(ceiling);
  const cap = ceiling - 1; // the price gets pinned just under the ceiling

  // rise toward the ceiling, then flatten (capped)
  const bend = { x: xOf(0.52), y: yOf(cap) };
  const rise = `M${xOf(0)},${yOf(6)} C${xOf(0.18)},${yOf(8)} ${xOf(0.36)},${yOf(15)} ${bend.x},${bend.y}`;
  const flat = `M${bend.x},${bend.y} L${xOf(1)},${bend.y}`;
  const riseP = interpolate(sweep, [0, 0.6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const flatP = interpolate(sweep, [0.6, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const hit = interpolate(sweep, [0.56, 0.66], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ring = interpolate(sweep, [0.58, 0.8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ticks: number[] = [];
  for (let v = 0; v <= yTop; v += 5) ticks.push(v);

  const chartTop = TOP + 230;

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      <MusicBed src={music.src} volume={music.volume} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 28%, ${theme.color.red}1f 0%, transparent 55%)` }} />
      <div style={{ position: "absolute", top: TOP, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Brandmark scale={1.0} />
      </div>

      <div style={{ position: "absolute", top: TOP + 90, left: safe.left, width: CW, opacity: labelIn }}>
        <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 4, textTransform: "uppercase", color: theme.color.red }}>{eyebrow}</div>
      </div>

      <div style={{ position: "absolute", top: chartTop, left: safe.left, width: CW, height: H }}>
        <svg width={CW} height={H} viewBox={`0 0 ${CW} ${H}`} style={{ display: "block", overflow: "visible" }}>
          {ticks.map((t) => (
            <g key={t} opacity={axisIn}>
              <line x1={padL} y1={yOf(t)} x2={CW} y2={yOf(t)} stroke={theme.color.border} strokeWidth={1} strokeDasharray="2 6" />
              <text x={padL - 12} y={yOf(t) + 7} textAnchor="end" fontFamily={mono} fontSize={20} fill={theme.color.textTertiary}>${t}</text>
            </g>
          ))}
          <line x1={padL} y1={0} x2={padL} y2={plotH} stroke={theme.color.textTertiary} strokeWidth={2} opacity={axisIn} />
          <line x1={padL} y1={plotH} x2={CW} y2={plotH} stroke={theme.color.textTertiary} strokeWidth={2} opacity={axisIn} />
          <text x={padL} y={plotH + 34} fontFamily={mono} fontSize={18} fill={theme.color.textTertiary}>price over time →</text>

          {/* ceiling */}
          <line x1={padL} y1={cy} x2={CW} y2={cy} stroke={theme.color.redBright} strokeWidth={2.5} strokeDasharray="12 8" opacity={axisIn} />

          {/* rising price → capped flat */}
          <path d={rise} fill="none" stroke={theme.color.amber} strokeWidth={6} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - riseP} />
          <path d={flat} fill="none" stroke={theme.color.amber} strokeWidth={6} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - flatP} />

          {/* blocked burst where it hits the wall */}
          <circle cx={bend.x} cy={bend.y} r={42 * ring} fill="none" stroke={theme.color.redBright} strokeWidth={3} opacity={1 - ring} />
          <circle cx={bend.x} cy={bend.y} r={9 * hit} fill={theme.color.redBright} />
        </svg>

        {/* ceiling label top-right */}
        <div style={{ position: "absolute", right: 0, top: cy - 44, textAlign: "right", opacity: axisIn, fontFamily: mono, fontSize: 24, color: theme.color.redBright }}>{ceilingLabel}</div>
        {/* "price hits the wall" near the bend, just under the flat line */}
        <div style={{ position: "absolute", left: bend.x - padL + 8, top: bend.y + 10, opacity: hit, fontFamily: mono, fontSize: 20, color: theme.color.textSecondary }}>{cappedLabel}</div>

        {/* takeaway — lower clear zone, well below the line */}
        <div style={{ position: "absolute", left: padL + 8, top: yOf(7.5), width: plotW - 16, textAlign: "center", opacity: deflectIn, transform: `translateY(${interpolate(deflectIn, [0, 1], [14, 0])}px)` }}>
          <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 44, color: theme.color.redBright }}>↓ {deflectLabel}</div>
        </div>
      </div>

      <div style={{ position: "absolute", bottom: INSET.bottom + 30, left: safe.left, width: CW, textAlign: "center", fontFamily: headline, fontWeight: 600, fontSize: 40, color: theme.color.textPrimary, opacity: punchIn }}>{punch}</div>
      <div style={{ position: "absolute", bottom: INSET.bottom - 10, left: 0, right: 0, textAlign: "center", fontFamily: mono, fontSize: 22, color: theme.color.textTertiary }}>{source}</div>
    </AbsoluteFill>
  );
};
