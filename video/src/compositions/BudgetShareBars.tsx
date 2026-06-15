import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter, countUp } from "../lib/anim";
import { INSET, safe } from "../lib/safezone";
import { Brandmark } from "../components/Brandmark";
import { MusicBed } from "../components/MusicBed";

// WHO IT HITS beat — share of income spent on food, bottom vs top, as a proper
// labelled bar chart: a 0–40% X-axis with gridlines + tick labels, two value
// counters, then a staggered "≈ 4×" ratio callout so the panel keeps moving.
// EXTERNAL figures (BLS CES / USDA ERS) — verify on build. h264.
export const budgetShareSchema = z.object({
  eyebrow: z.string().default("WHO A FOOD TAX HITS"),
  lowLabel: z.string().default("Lowest-income fifth"),
  lowPct: z.number().default(31),
  highLabel: z.string().default("Highest-income fifth"),
  highPct: z.number().default(8),
  axisMax: z.number().default(40),
  punch: z.string().default("a hidden food tax isn’t flat — it’s regressive"),
  source: z.string().default("Share of income spent on food · BLS CES / USDA ERS (verify on build)"),
  startDelay: z.number().default(6),
  music: z.object({ src: z.string().default("audio/bg-loop.mp3"), volume: z.number().default(0.165) }).default({}),
});

type Props = z.infer<typeof budgetShareSchema>;

export const BudgetShareBars: React.FC<Props> = ({ eyebrow, lowLabel, lowPct, highLabel, highPct, axisMax, punch, source, startDelay, music }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lf = frame - startDelay;

  const labelIn = enter(lf, fps, { durationInFrames: 14 });
  const axisIn = enter(lf, fps, { delay: 8, durationInFrames: 14 });
  const lowGrow = enter(lf, fps, { delay: 16, durationInFrames: 32 });
  const highGrow = enter(lf, fps, { delay: 44, durationInFrames: 26 });
  const ratioIn = enter(lf, fps, { delay: 78, durationInFrames: 18 });
  const punchIn = enter(lf, fps, { delay: 104, durationInFrames: 18 });

  const lowN = countUp(lf, fps, lowPct, { delay: 16, durationInFrames: 32 });
  const highN = countUp(lf, fps, highPct, { delay: 44, durationInFrames: 26 });
  const ratio = (lowPct / Math.max(highPct, 1));

  const TOP = safe.top;
  const CW = safe.width;
  const H = 360;
  const xticks: number[] = [];
  for (let v = 0; v <= axisMax; v += 10) xticks.push(v);
  const xOf = (p: number) => (p / axisMax) * CW;

  const Row = ({ y, label, pct, grow, n, color, muted }: { y: number; label: string; pct: number; grow: number; n: number; color: string; muted?: boolean }) => (
    <>
      <div style={{ position: "absolute", left: 0, top: y - 34, width: CW, display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <span style={{ fontFamily: headline, fontWeight: 600, fontSize: 30, color: theme.color.textPrimary }}>{label}</span>
        <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 40, color }}>{Math.round(n)}%</span>
      </div>
      <div style={{ position: "absolute", left: 0, top: y, width: CW, height: 56, background: theme.color.card, borderRadius: 8, overflow: "hidden" }}>
        <div style={{ width: xOf(pct) * grow, height: "100%", background: color, opacity: muted ? 0.5 : 0.95, borderRadius: 8, boxShadow: muted ? undefined : `0 0 24px ${color}55` }} />
      </div>
    </>
  );

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      <MusicBed src={music.src} volume={music.volume} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 30%, ${theme.color.red}1f 0%, transparent 55%)` }} />
      <div style={{ position: "absolute", top: TOP, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Brandmark scale={1.0} />
      </div>

      <div style={{ position: "absolute", top: TOP + 80, left: safe.left, width: CW, opacity: labelIn }}>
        <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 4, textTransform: "uppercase", color: theme.color.red }}>{eyebrow}</div>
        <div style={{ fontFamily: body, fontSize: 26, color: theme.color.textSecondary, marginTop: 8 }}>how much of every paycheck goes to food</div>
      </div>

      {/* chart */}
      <div style={{ position: "absolute", top: TOP + 230, left: safe.left, width: CW, height: H }}>
        {/* vertical gridlines + % ticks */}
        <svg width={CW} height={H} viewBox={`0 0 ${CW} ${H}`} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
          {xticks.map((t) => (
            <g key={t} opacity={axisIn}>
              <line x1={xOf(t)} y1={0} x2={xOf(t)} y2={H - 36} stroke={theme.color.border} strokeWidth={1} strokeDasharray="2 6" />
              <text x={xOf(t)} y={H - 10} textAnchor="middle" fontFamily={mono} fontSize={20} fill={theme.color.textTertiary}>{t}%</text>
            </g>
          ))}
        </svg>
        <Row y={56} label={lowLabel} pct={lowPct} grow={lowGrow} n={lowN} color={theme.color.red} />
        <Row y={200} label={highLabel} pct={highPct} grow={highGrow} n={highN} color={theme.color.blue} muted />
      </div>

      {/* ratio callout */}
      <div style={{ position: "absolute", top: TOP + 230 + H + 24, left: safe.left, width: CW, display: "flex", alignItems: "center", gap: 16, opacity: ratioIn, transform: `translateY(${interpolate(ratioIn, [0, 1], [14, 0])}px)` }}>
        <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 64, color: theme.color.redBright }}>≈{ratio.toFixed(1)}×</span>
        <span style={{ fontFamily: headline, fontWeight: 600, fontSize: 32, color: theme.color.textPrimary }}>more of every paycheck, for the same tax</span>
      </div>

      <div style={{ position: "absolute", bottom: INSET.bottom + 30, left: safe.left, width: CW, textAlign: "center", fontFamily: headline, fontWeight: 600, fontSize: 40, color: theme.color.textPrimary, opacity: punchIn }}>{punch}</div>
      <div style={{ position: "absolute", bottom: INSET.bottom - 10, left: 0, right: 0, textAlign: "center", fontFamily: mono, fontSize: 18, color: theme.color.textTertiary }}>{source}</div>
    </AbsoluteFill>
  );
};
