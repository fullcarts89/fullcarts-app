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
// Bars climb year 0→N as a left→right sweep; the big $ readout counts up ALONG
// the curve (so it lands on the spoken "almost two grand"); the "+$/yr" kicker
// and the comment-bait pop near the end. Full-frame, opaque → render h264.
//
// Retiming: `startDelay` shifts the whole animation (frames) to sit under the VO;
// `sweepFrames` stretches the climb so the count-up lands on the right word.
export const compoundChartSchema = z.object({
  eyebrow: z.string().default("SAME CART, COMPOUNDED"),
  base: z.number().default(1300), // $/mo today
  ratePct: z.number().default(4.2), // annual %
  years: z.number().default(10),
  prefix: z.string().default("$"),
  suffix: z.string().default("/mo"),
  rateLabel: z.string().default("@ 4.2% headline CPI"),
  baseNote: z.string().default("avg US family of 4 · today"),
  extraNote: z.string().default("+ ~$7,940 / yr — same food"),
  bait: z.string().default("that’s the average — what’s yours? ↓ comment it"),
  source: z.string().default("USDA Moderate-Cost Food Plan · 4.2% = headline rate"),
  accent: z.enum(["red", "green", "blue", "amber"]).default("red"),
  startDelay: z.number().default(6),
  sweepFrames: z.number().default(82),
  music: z.object({ src: z.string().default("audio/bg-loop.mp3"), volume: z.number().default(0.33) }).default({}),
});

type Props = z.infer<typeof compoundChartSchema>;

export const CompoundChart: React.FC<Props> = ({
  eyebrow, base, ratePct, years, prefix, suffix, rateLabel, baseNote,
  extraNote, bait, source, accent, startDelay, sweepFrames, music,
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
  const maxV = vals[years];
  const current = base * Math.pow(1 + r, sweep * years); // count-up along the curve

  const TOP = safe.top;
  const barsTop = TOP + 360;
  const barsH = 540;
  const gap = 12;

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      <MusicBed src={music.src} volume={music.volume} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 30%, ${accentColor}22 0%, transparent 55%)` }} />
      <div style={{ position: "absolute", top: TOP, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Brandmark scale={1.0} />
      </div>

      {/* eyebrow + rate tag */}
      <div style={{ position: "absolute", top: TOP + 80, left: safe.left, width: safe.width, display: "flex", alignItems: "baseline", justifyContent: "space-between", opacity: labelIn }}>
        <span style={{ fontFamily: mono, fontSize: 28, letterSpacing: 4, textTransform: "uppercase", color: accentColor }}>{eyebrow}</span>
        <span style={{ fontFamily: mono, fontSize: 24, color: theme.color.textTertiary }}>{rateLabel}</span>
      </div>

      {/* big count-up readout */}
      <div style={{ position: "absolute", top: TOP + 128, left: safe.left, width: safe.width }}>
        <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 156, lineHeight: 1, color: theme.color.textPrimary, textShadow: `0 0 60px ${accentColor}55` }}>
          {prefix}{fmt(Math.round(current))}
          <span style={{ fontSize: 60, color: theme.color.textSecondary }}>{suffix}</span>
        </div>
        <div style={{ fontFamily: body, fontSize: 30, color: theme.color.textSecondary, marginTop: 8 }}>{baseNote}</div>
      </div>

      {/* bars */}
      <div style={{ position: "absolute", top: barsTop, left: safe.left, width: safe.width, height: barsH, display: "flex", alignItems: "flex-end", gap }}>
        {vals.map((v, i) => {
          const reveal = interpolate(sweep, [i / n, (i + 1) / n], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const h = (v / maxV) * barsH * reveal;
          const isLast = i === years;
          const col = i === 0 ? theme.color.textTertiary : isLast ? accentColor : theme.color.blue;
          return (
            <div key={i} style={{ flex: "1 1 0", height: h, background: col, opacity: i === 0 ? 0.5 : 0.92, borderRadius: "5px 5px 0 0", boxShadow: isLast ? `0 0 24px ${accentColor}66` : undefined }} />
          );
        })}
      </div>
      {/* year labels */}
      <div style={{ position: "absolute", top: barsTop + barsH + 12, left: safe.left, width: safe.width, display: "flex", gap }}>
        {vals.map((_, i) => (
          <span key={i} style={{ flex: "1 1 0", textAlign: "center", fontFamily: mono, fontSize: 19, color: i === 0 || i === years ? theme.color.textSecondary : theme.color.textTertiary }}>
            {i === 0 ? "now" : `+${i}`}
          </span>
        ))}
      </div>

      {/* kicker */}
      <div style={{ position: "absolute", top: barsTop + barsH + 56, left: safe.left, width: safe.width, fontFamily: headline, fontWeight: 600, fontSize: 40, color: accentColor, opacity: extraIn }}>{extraNote}</div>

      {/* comment bait */}
      <div style={{ position: "absolute", bottom: INSET.bottom + 36, left: safe.left, width: safe.width, textAlign: "center", fontFamily: headline, fontWeight: 500, fontSize: 38, color: theme.color.textPrimary, opacity: baitIn }}>{bait}</div>

      <div style={{ position: "absolute", bottom: INSET.bottom - 10, left: 0, right: 0, textAlign: "center", fontFamily: mono, fontSize: 22, color: theme.color.textTertiary }}>{source}</div>
    </AbsoluteFill>
  );
};
