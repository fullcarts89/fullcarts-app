import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { INSET, safe } from "../lib/safezone";
import { Brandmark } from "../components/Brandmark";
import { MusicBed } from "../components/MusicBed";

// TAKE beat — the thesis as one motion. A price line climbs (amber) toward a
// dashed ceiling labelled "$15 — you’ll never accept it"; instead of crossing,
// it deflects DOWN (red) into "shrink the box instead." Visualises the
// pressure-release-valve argument. Full-frame, opaque → render h264.
export const priceCeilingSchema = z.object({
  eyebrow: z.string().default("THE CEILING YOU WON’T CROSS"),
  ceilingLabel: z.string().default("$15 box — you’ll never accept it"),
  deflectLabel: z.string().default("so they shrink the box instead"),
  punch: z.string().default("shrinkflation is the pressure-release valve"),
  source: z.string().default("FullCarts · the mechanism"),
  startDelay: z.number().default(6),
  music: z.object({ src: z.string().default("audio/bg-loop.mp3"), volume: z.number().default(0.33) }).default({}),
});

type Props = z.infer<typeof priceCeilingSchema>;

export const PriceCeiling: React.FC<Props> = ({ eyebrow, ceilingLabel, deflectLabel, punch, source, startDelay, music }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lf = frame - startDelay;

  const labelIn = enter(lf, fps, { durationInFrames: 14 });
  const ceilIn = enter(lf, fps, { delay: 10, durationInFrames: 16 });
  const sweep = enter(lf, fps, { delay: 22, durationInFrames: 76 });
  const punchIn = enter(lf, fps, { delay: 96, durationInFrames: 18 });

  const W = safe.width;
  const H = 560;
  const ceilingY = 80;

  // ascent (amber) then deflection (red)
  const apex = { x: 0.58 * W, y: ceilingY + 26 };
  const ascent = `M0,${H} L${0.2 * W},${0.66 * H} L${0.4 * W},${0.34 * H} L${apex.x},${apex.y}`;
  const descent = `M${apex.x},${apex.y} L${0.72 * W},${0.44 * H} L${0.88 * W},${0.6 * H} L${W},${0.64 * H}`;
  const ascP = interpolate(sweep, [0, 0.6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const descP = interpolate(sweep, [0.6, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const apexHit = interpolate(sweep, [0.55, 0.64], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const TOP = safe.top;
  const chartTop = TOP + 220;

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      <MusicBed src={music.src} volume={music.volume} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 28%, ${theme.color.red}1f 0%, transparent 55%)` }} />
      <div style={{ position: "absolute", top: TOP, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Brandmark scale={1.0} />
      </div>

      <div style={{ position: "absolute", top: TOP + 90, left: safe.left, width: safe.width, opacity: labelIn }}>
        <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 4, textTransform: "uppercase", color: theme.color.red }}>{eyebrow}</div>
      </div>

      <div style={{ position: "absolute", top: chartTop, left: safe.left, width: W, height: H }}>
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ display: "block", overflow: "visible" }}>
          {/* ceiling */}
          <line x1={0} y1={ceilingY} x2={W} y2={ceilingY} stroke={theme.color.textTertiary} strokeWidth={2} strokeDasharray="10 8" opacity={ceilIn} />
          {/* ascent */}
          <path d={ascent} fill="none" stroke={theme.color.amber} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - ascP} />
          {/* deflection */}
          <path d={descent} fill="none" stroke={theme.color.red} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - descP} />
          {/* impact mark at the apex */}
          <circle cx={apex.x} cy={apex.y} r={10 * apexHit} fill={theme.color.red} />
        </svg>

        {/* ceiling label (top-right) */}
        <div style={{ position: "absolute", right: 0, top: ceilingY - 44, textAlign: "right", opacity: ceilIn, fontFamily: mono, fontSize: 26, color: theme.color.textSecondary }}>{ceilingLabel}</div>

        {/* deflection label, rides in with the red descent */}
        <div style={{ position: "absolute", left: 0.62 * W, top: 0.5 * H, opacity: descP, transform: `translateY(${interpolate(descP, [0, 1], [14, 0])}px)` }}>
          <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 34, color: theme.color.redBright }}>{deflectLabel} ↓</div>
        </div>
      </div>

      <div style={{ position: "absolute", bottom: INSET.bottom + 34, left: safe.left, width: safe.width, textAlign: "center", fontFamily: headline, fontWeight: 600, fontSize: 40, color: theme.color.textPrimary, opacity: punchIn }}>{punch}</div>
      <div style={{ position: "absolute", bottom: INSET.bottom - 10, left: 0, right: 0, textAlign: "center", fontFamily: mono, fontSize: 22, color: theme.color.textTertiary }}>{source}</div>
    </AbsoluteFill>
  );
};
