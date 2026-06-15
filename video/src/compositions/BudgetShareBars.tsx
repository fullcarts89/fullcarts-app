import React from "react";
import { z } from "zod";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter, countUp } from "../lib/anim";
import { INSET, safe } from "../lib/safezone";
import { Brandmark } from "../components/Brandmark";
import { MusicBed } from "../components/MusicBed";

// WHO IT HITS beat — the regressive point, as data. Two horizontal bars: the
// share of income each group spends on food. The low-income bar sweeps out long
// and red; the high-income bar stays short and muted — the visual proof that a
// flat food tax lands hardest on the squeezed.
// NB: figures are EXTERNAL (BLS Consumer Expenditure Survey / USDA ERS) — verify
// the exact shares on build day. Full-frame, opaque → render h264.
export const budgetShareSchema = z.object({
  eyebrow: z.string().default("WHO A FOOD TAX HITS"),
  lowLabel: z.string().default("Lowest-income fifth"),
  lowPct: z.number().default(31),
  highLabel: z.string().default("Highest-income fifth"),
  highPct: z.number().default(8),
  punch: z.string().default("a hidden food tax isn’t flat — it’s regressive"),
  source: z.string().default("Share of income spent on food · BLS CES / USDA ERS (verify on build)"),
  startDelay: z.number().default(6),
  music: z.object({ src: z.string().default("audio/bg-loop.mp3"), volume: z.number().default(0.33) }).default({}),
});

type Props = z.infer<typeof budgetShareSchema>;

export const BudgetShareBars: React.FC<Props> = ({ eyebrow, lowLabel, lowPct, highLabel, highPct, punch, source, startDelay, music }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lf = frame - startDelay;

  const labelIn = enter(lf, fps, { durationInFrames: 14 });
  const lowGrow = enter(lf, fps, { delay: 14, durationInFrames: 34 });
  const highGrow = enter(lf, fps, { delay: 40, durationInFrames: 28 });
  const punchIn = enter(lf, fps, { delay: 74, durationInFrames: 18 });

  const lowN = countUp(lf, fps, lowPct, { delay: 14, durationInFrames: 34 });
  const highN = countUp(lf, fps, highPct, { delay: 40, durationInFrames: 28 });

  const maxPct = Math.max(lowPct, highPct, 1);
  const trackW = safe.width;
  const TOP = safe.top;

  const Bar = ({ top, label, pct, grow, n, color, mutedTrack }: { top: number; label: string; pct: number; grow: number; n: number; color: string; mutedTrack?: boolean }) => {
    const w = (pct / maxPct) * trackW * grow;
    return (
      <div style={{ position: "absolute", top, left: safe.left, width: trackW }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 12 }}>
          <span style={{ fontFamily: headline, fontWeight: 600, fontSize: 34, color: theme.color.textPrimary }}>{label}</span>
          <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 44, color }}>{Math.round(n)}%</span>
        </div>
        <div style={{ width: trackW, height: 64, background: theme.color.card, borderRadius: 8, overflow: "hidden" }}>
          <div style={{ width: w, height: "100%", background: color, opacity: mutedTrack ? 0.5 : 0.95, borderRadius: 8, boxShadow: mutedTrack ? undefined : `0 0 24px ${color}55` }} />
        </div>
      </div>
    );
  };

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      <MusicBed src={music.src} volume={music.volume} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 32%, ${theme.color.red}1f 0%, transparent 55%)` }} />
      <div style={{ position: "absolute", top: TOP, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Brandmark scale={1.0} />
      </div>

      <div style={{ position: "absolute", top: TOP + 90, left: safe.left, width: safe.width, opacity: labelIn }}>
        <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 4, textTransform: "uppercase", color: theme.color.red }}>{eyebrow}</div>
        <div style={{ fontFamily: body, fontSize: 28, color: theme.color.textSecondary, marginTop: 10 }}>how much of every paycheck goes to food</div>
      </div>

      <Bar top={TOP + 260} label={lowLabel} pct={lowPct} grow={lowGrow} n={lowN} color={theme.color.red} />
      <Bar top={TOP + 470} label={highLabel} pct={highPct} grow={highGrow} n={highN} color={theme.color.blue} mutedTrack />

      <div style={{ position: "absolute", bottom: INSET.bottom + 34, left: safe.left, width: safe.width, textAlign: "center", fontFamily: headline, fontWeight: 600, fontSize: 40, color: theme.color.textPrimary, opacity: punchIn }}>{punch}</div>
      <div style={{ position: "absolute", bottom: INSET.bottom - 10, left: 0, right: 0, textAlign: "center", fontFamily: mono, fontSize: 20, color: theme.color.textTertiary }}>{source}</div>
    </AbsoluteFill>
  );
};
