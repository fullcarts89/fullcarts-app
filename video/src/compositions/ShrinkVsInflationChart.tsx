import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { INSET, safe } from "../lib/safezone";
import { Brandmark } from "../components/Brandmark";
import { MusicBed } from "../components/MusicBed";

// HOOK beat — the precedent. BLS "All food" package downsizings (bars, left
// axis) vs food-price inflation YoY% (line, right axis), by year. A left→right
// `sweep` grows the bars and draws the inflation line together; the peak year
// (2022) bar burns red and a "166→349 (2×)" chip pops as the sweep reaches it.
// Full-frame, opaque → render h264. Retime via `startDelay` / `sweepFrames`.
const PT = z.object({ year: z.number(), downsizings: z.number(), inflation: z.number() });

export const shrinkVsInflationSchema = z.object({
  eyebrow: z.string().default("SHRINKFLATION TRACKS INFLATION"),
  data: z.array(PT).default([
    { year: 2020, downsizings: 157, inflation: 3.4 },
    { year: 2021, downsizings: 166, inflation: 3.9 },
    { year: 2022, downsizings: 349, inflation: 9.9 },
    { year: 2023, downsizings: 344, inflation: 5.8 },
    { year: 2024, downsizings: 334, inflation: 2.3 },
    { year: 2025, downsizings: 174, inflation: 2.8 },
  ]),
  caption: z.string().default("every food-inflation spike → a jump in downsizings"),
  source: z.string().default("BLS R-CPI-SC · FRED food CPI"),
  startDelay: z.number().default(6),
  sweepFrames: z.number().default(80),
  music: z.object({ src: z.string().default("audio/bg-loop.mp3"), volume: z.number().default(0.33) }).default({}),
});

type Props = z.infer<typeof shrinkVsInflationSchema>;

const niceTop = (vals: number[], ticks = 5) => {
  const max = Math.max(...vals, 1);
  const step = Math.ceil(max / (ticks - 1));
  return step * (ticks - 1);
};

export const ShrinkVsInflationChart: React.FC<Props> = ({ eyebrow, data, caption, source, startDelay, sweepFrames, music }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lf = frame - startDelay;

  const labelIn = enter(lf, fps, { durationInFrames: 14 });
  const sweep = enter(lf, fps, { delay: 8, durationInFrames: sweepFrames });
  const captionIn = enter(lf, fps, { delay: sweepFrames + 6, durationInFrames: 16 });

  const W = safe.width; // 850
  const H = 460;
  const n = data.length;
  const slot = W / n;
  const barW = slot * 0.52;
  const topDown = niceTop(data.map((d) => d.downsizings));
  const topInf = niceTop(data.map((d) => d.inflation));
  const xc = (i: number) => i * slot + slot / 2;
  const yBar = (v: number) => (v / topDown) * H;
  const yInf = (v: number) => H - (v / topInf) * H;

  let peakIdx = 0;
  data.forEach((d, i) => { if (d.inflation > data[peakIdx].inflation) peakIdx = i; });
  const peak = data[peakIdx];
  const peakPrev = data[peakIdx - 1];

  const linePath = data
    .map((d, i) => `${i ? "L" : "M"}${xc(i).toFixed(1)},${yInf(d.inflation).toFixed(1)}`)
    .join(" ");
  const lineP = sweep;

  // chip springs once the sweep reaches the peak year
  const chipRaw = interpolate(sweep, [peakIdx / n, peakIdx / n + 0.06], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const chipP = chipRaw * chipRaw * (3 - 2 * chipRaw); // smoothstep

  const TOP = safe.top;
  const chartTop = TOP + 200;

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      <MusicBed src={music.src} volume={music.volume} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 28%, ${theme.color.red}1f 0%, transparent 55%)` }} />
      <div style={{ position: "absolute", top: TOP, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Brandmark scale={1.0} />
      </div>

      <div style={{ position: "absolute", top: TOP + 80, left: safe.left, width: safe.width, opacity: labelIn }}>
        <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 4, textTransform: "uppercase", color: theme.color.red }}>{eyebrow}</div>
        <div style={{ display: "flex", gap: 28, marginTop: 14, fontFamily: mono, fontSize: 22, color: theme.color.textSecondary }}>
          <span><span style={{ display: "inline-block", width: 16, height: 16, background: theme.color.blue, marginRight: 8, verticalAlign: "middle" }} /> BLS downsizings / yr</span>
          <span><span style={{ display: "inline-block", width: 22, height: 4, background: theme.color.amber, marginRight: 8, verticalAlign: "middle" }} /> food inflation YoY%</span>
        </div>
      </div>

      {/* chart */}
      <div style={{ position: "absolute", top: chartTop, left: safe.left, width: W, height: H }}>
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ display: "block", overflow: "visible" }}>
          {[0, 0.25, 0.5, 0.75, 1].map((g) => (
            <line key={g} x1={0} y1={H * g} x2={W} y2={H * g} stroke={theme.color.border} strokeWidth={1} strokeDasharray="2 5" />
          ))}
          {data.map((d, i) => {
            const reveal = interpolate(sweep, [i / n, (i + 1) / n], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            const h = yBar(d.downsizings) * reveal;
            const isPeak = i === peakIdx;
            return (
              <rect key={i} x={xc(i) - barW / 2} y={H - h} width={barW} height={h}
                fill={isPeak ? theme.color.red : theme.color.blue}
                opacity={isPeak ? 0.95 : 0.55} rx={4} />
            );
          })}
          <path d={linePath} fill="none" stroke={theme.color.amber} strokeWidth={4}
            pathLength={1} strokeDasharray={1} strokeDashoffset={1 - lineP} strokeLinejoin="round" strokeLinecap="round" />
          {lineP > 0.02 && (
            <circle cx={xc(peakIdx)} cy={yInf(peak.inflation)} r={7 * chipP} fill={theme.color.amber} />
          )}
        </svg>

        {/* 2022 callout chip, anchored to the peak point (1:1 px mapping) */}
        <div style={{
          position: "absolute", left: xc(peakIdx), top: yInf(peak.inflation) - 16,
          transform: `translate(-50%, -100%) translateY(${interpolate(chipP, [0, 1], [12, 0])}px)`,
          opacity: chipP, pointerEvents: "none",
        }}>
          <div style={{ background: theme.color.red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 24, padding: "8px 14px", borderRadius: 8, whiteSpace: "nowrap", boxShadow: `0 0 24px ${theme.color.red}88` }}>
            {peak.year}: {peakPrev?.downsizings ?? "—"}→{peak.downsizings} ({(peak.downsizings / (peakPrev?.downsizings || peak.downsizings)).toFixed(1)}×)
          </div>
        </div>
      </div>

      {/* year labels */}
      <div style={{ position: "absolute", top: chartTop + H + 14, left: safe.left, width: W, display: "flex" }}>
        {data.map((d, i) => (
          <span key={i} style={{ flex: "1 1 0", textAlign: "center", fontFamily: mono, fontSize: 19, color: i === peakIdx ? theme.color.redBright : theme.color.textTertiary }}>
            &rsquo;{String(d.year).slice(2)}
          </span>
        ))}
      </div>

      <div style={{ position: "absolute", bottom: INSET.bottom + 36, left: safe.left, width: safe.width, fontFamily: headline, fontWeight: 500, fontSize: 36, color: theme.color.textPrimary, opacity: captionIn }}>{caption}</div>
      <div style={{ position: "absolute", bottom: INSET.bottom - 10, left: 0, right: 0, textAlign: "center", fontFamily: mono, fontSize: 22, color: theme.color.textTertiary }}>{source}</div>
    </AbsoluteFill>
  );
};
