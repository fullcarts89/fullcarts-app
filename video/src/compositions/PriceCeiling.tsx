import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { INSET, safe } from "../lib/safezone";
import { Brandmark } from "../components/Brandmark";
import { MusicBed } from "../components/MusicBed";

// TAKE beat — the price climbs toward a ceiling it can't cross ($20 box), hits
// it (impact pulse), and instead of breaking through it deflects DOWN as a red
// "shrink the box" — and a little box icon physically shrinks. Real $ Y-axis +
// time X-axis. Full-frame, opaque → render h264.
export const priceCeilingSchema = z.object({
  eyebrow: z.string().default("THE CEILING YOU WON’T CROSS"),
  ceiling: z.number().default(20), // $ you'll never pay
  ceilingLabel: z.string().default("$20 box — you’ll never accept it"),
  deflectLabel: z.string().default("so they shrink the box instead"),
  punch: z.string().default("shrinkflation is the pressure-release valve"),
  source: z.string().default("FullCarts · the mechanism"),
  startDelay: z.number().default(6),
  music: z.object({ src: z.string().default("audio/bg-loop.mp3"), volume: z.number().default(0.165) }).default({}),
});

type Props = z.infer<typeof priceCeilingSchema>;

export const PriceCeiling: React.FC<Props> = ({ eyebrow, ceiling, ceilingLabel, deflectLabel, punch, source, startDelay, music }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lf = frame - startDelay;

  const labelIn = enter(lf, fps, { durationInFrames: 14 });
  const axisIn = enter(lf, fps, { delay: 8, durationInFrames: 14 });
  const sweep = enter(lf, fps, { delay: 20, durationInFrames: 80 });
  const punchIn = enter(lf, fps, { delay: 100, durationInFrames: 18 });

  const TOP = safe.top;
  const CW = safe.width;
  const H = 470;
  const padL = 78, padB = 44;
  const plotW = CW - padL, plotH = H - padB;
  const yTop = ceiling + 4; // headroom above the ceiling
  const xOf = (f: number) => padL + f * plotW; // f in 0..1
  const yOf = (v: number) => plotH - (v / yTop) * plotH;
  const cy = yOf(ceiling);

  // ascent toward the ceiling, then deflection down
  const apex = { x: xOf(0.55), y: cy + 8 };
  const ascent = `M${xOf(0)},${yOf(5)} C${xOf(0.2)},${yOf(7)} ${xOf(0.4)},${yOf(15)} ${apex.x},${apex.y}`;
  const descent = `M${apex.x},${apex.y} C${xOf(0.68)},${yOf(15)} ${xOf(0.82)},${yOf(11)} ${xOf(1)},${yOf(10)}`;
  const ascP = interpolate(sweep, [0, 0.62], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const descP = interpolate(sweep, [0.62, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const hit = interpolate(sweep, [0.58, 0.66], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ring = interpolate(sweep, [0.6, 0.78], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const boxShrink = descP; // box shrinks as the deflection plays
  const ticks: number[] = [];
  for (let v = 0; v <= yTop; v += 5) ticks.push(v);

  const chartTop = TOP + 230;
  // little box icon near the end of the descent
  const boxCx = xOf(0.9), boxBottom = yOf(0) , bw = 70, bh = 150 * (1 - 0.4 * boxShrink);

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
          {/* Y grid + $ labels */}
          {ticks.map((t) => (
            <g key={t} opacity={axisIn}>
              <line x1={padL} y1={yOf(t)} x2={CW} y2={yOf(t)} stroke={theme.color.border} strokeWidth={1} strokeDasharray="2 6" />
              <text x={padL - 12} y={yOf(t) + 7} textAnchor="end" fontFamily={mono} fontSize={20} fill={theme.color.textTertiary}>${t}</text>
            </g>
          ))}
          {/* axes */}
          <line x1={padL} y1={0} x2={padL} y2={plotH} stroke={theme.color.textTertiary} strokeWidth={2} opacity={axisIn} />
          <line x1={padL} y1={plotH} x2={CW} y2={plotH} stroke={theme.color.textTertiary} strokeWidth={2} opacity={axisIn} />
          <text x={padL} y={plotH + 34} fontFamily={mono} fontSize={18} fill={theme.color.textTertiary}>price over time →</text>

          {/* the ceiling */}
          <line x1={padL} y1={cy} x2={CW} y2={cy} stroke={theme.color.redBright} strokeWidth={2.5} strokeDasharray="12 8" opacity={axisIn} />

          {/* ascent (amber) then deflection (red) */}
          <path d={ascent} fill="none" stroke={theme.color.amber} strokeWidth={6} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - ascP} />
          <path d={descent} fill="none" stroke={theme.color.red} strokeWidth={6} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - descP} />

          {/* impact at the ceiling */}
          <circle cx={apex.x} cy={apex.y} r={40 * ring} fill="none" stroke={theme.color.redBright} strokeWidth={3} opacity={1 - ring} />
          <circle cx={apex.x} cy={apex.y} r={9 * hit} fill={theme.color.redBright} />

          {/* shrinking box icon on the deflection */}
          {descP > 0.05 && (
            <g opacity={descP}>
              <rect x={boxCx - bw / 2} y={boxBottom - bh} width={bw} height={bh} fill={theme.color.red} opacity={0.85} rx={5} />
            </g>
          )}
        </svg>

        {/* ceiling label (top-right) */}
        <div style={{ position: "absolute", right: 0, top: cy - 44, textAlign: "right", opacity: axisIn, fontFamily: mono, fontSize: 24, color: theme.color.redBright }}>{ceilingLabel}</div>

        {/* deflection label — LEFT side, clear of the right-side descent */}
        <div style={{ position: "absolute", left: padL + 14, top: yOf(7), maxWidth: 360, opacity: descP, transform: `translateY(${interpolate(descP, [0, 1], [14, 0])}px)` }}>
          <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 36, color: theme.color.redBright, lineHeight: 1.15 }}>{deflectLabel} ↓</div>
        </div>
      </div>

      <div style={{ position: "absolute", bottom: INSET.bottom + 30, left: safe.left, width: CW, textAlign: "center", fontFamily: headline, fontWeight: 600, fontSize: 40, color: theme.color.textPrimary, opacity: punchIn }}>{punch}</div>
      <div style={{ position: "absolute", bottom: INSET.bottom - 10, left: 0, right: 0, textAlign: "center", fontFamily: mono, fontSize: 22, color: theme.color.textTertiary }}>{source}</div>
    </AbsoluteFill>
  );
};
