import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { INSET, safe } from "../lib/safezone";
import { Brandmark } from "../components/Brandmark";
import { MusicBed } from "../components/MusicBed";

// RECEIPT beat — why the index misses shrinkflation. A package shrinks while the
// shelf price holds; the two readouts contrast "CPI reads +0.0%" (it tracks price)
// against the real "+X% per ounce" the shrink actually costs you. The per-ounce
// figure is exact arithmetic from the shrink %: 1/(1−s) − 1.
// Full-frame, opaque → render h264. Retime via `startDelay`.
export const cpiMechanicSchema = z.object({
  eyebrow: z.string().default("WHY THE NUMBER LIES"),
  price: z.string().default("SAME PRICE"),
  shrinkPct: z.number().default(15),
  punch: z.string().default("the hidden hike the index never sees"),
  source: z.string().default("same price · less product = more per ounce"),
  startDelay: z.number().default(6),
  music: z.object({ src: z.string().default("bg-loop.mp3"), volume: z.number().default(0.33) }).default({}),
});

type Props = z.infer<typeof cpiMechanicSchema>;

export const CpiMechanic: React.FC<Props> = ({ eyebrow, price, shrinkPct, punch, source, startDelay, music }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lf = frame - startDelay;

  const labelIn = enter(lf, fps, { durationInFrames: 14 });
  const shrink = enter(lf, fps, { delay: 16, durationInFrames: 40 }); // 0→1 package shrinks
  const cpiIn = enter(lf, fps, { delay: 54, durationInFrames: 16 });
  const realIn = enter(lf, fps, { delay: 70, durationInFrames: 16 });
  const punchIn = enter(lf, fps, { delay: 90, durationInFrames: 18 });

  const s = shrinkPct / 100;
  const perOz = Math.round((1 / (1 - s) - 1) * 100); // exact per-unit price rise
  const scaleY = interpolate(shrink, [0, 1], [1, 1 - s]);

  const TOP = safe.top;
  const boxFullH = 460;
  const boxW = 300;
  const boxLeft = safe.left + (safe.width - boxW) / 2;
  const boxBaseline = TOP + 180 + boxFullH; // bottoms stay planted as it shrinks

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      <MusicBed src={music.src} volume={music.volume} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 30%, ${theme.color.red}1f 0%, transparent 55%)` }} />
      <div style={{ position: "absolute", top: TOP, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Brandmark scale={1.0} />
      </div>

      <div style={{ position: "absolute", top: TOP + 80, left: safe.left, width: safe.width, opacity: labelIn }}>
        <span style={{ fontFamily: mono, fontSize: 30, letterSpacing: 4, textTransform: "uppercase", color: theme.color.red }}>{eyebrow}</span>
      </div>

      {/* shrinking package (height scales from the bottom) */}
      <div style={{ position: "absolute", left: boxLeft, top: boxBaseline, width: boxW, height: boxFullH, transformOrigin: "bottom center", transform: `scaleY(${scaleY})` }}>
        <div style={{ position: "absolute", bottom: 0, width: "100%", height: "100%", background: theme.color.card, border: `2px solid ${theme.color.border}`, borderRadius: 10, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", gap: 14 }}>
          <div style={{ width: "62%", height: 14, background: theme.color.red, opacity: 0.8, borderRadius: 3 }} />
          <div style={{ width: "46%", height: 10, background: theme.color.border, borderRadius: 3 }} />
          <div style={{ width: "30%", height: 10, background: theme.color.border, borderRadius: 3 }} />
        </div>
      </div>

      {/* price tag — stays put, counter-scaled so it never distorts */}
      <div style={{ position: "absolute", left: boxLeft + boxW - 40, top: TOP + 150, transform: "rotate(-6deg)" }}>
        <div style={{ background: theme.color.amber, color: theme.color.bg, fontFamily: mono, fontWeight: 700, fontSize: 32, padding: "10px 18px", borderRadius: 8, boxShadow: "0 8px 30px rgba(0,0,0,.5)", whiteSpace: "nowrap" }}>{price}</div>
        <div style={{ fontFamily: mono, fontSize: 18, color: theme.color.textTertiary, textTransform: "uppercase", letterSpacing: 2, marginTop: 8, textAlign: "center" }}>on the shelf</div>
      </div>

      {/* two contrasting readouts */}
      <div style={{ position: "absolute", top: TOP + 700, left: safe.left, width: safe.width, display: "flex", gap: 18 }}>
        <div style={{ flex: 1, background: theme.color.card, border: `1px solid ${theme.color.border}`, borderRadius: 12, padding: "20px 22px", opacity: cpiIn }}>
          <div style={{ fontFamily: mono, fontSize: 20, letterSpacing: 2, textTransform: "uppercase", color: theme.color.textTertiary }}>CPI reads</div>
          <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 70, color: theme.color.textSecondary, lineHeight: 1.1 }}>+0.0%</div>
          <div style={{ fontFamily: body, fontSize: 22, color: theme.color.textTertiary }}>it tracks the price tag</div>
        </div>
        <div style={{ flex: 1, background: `${theme.color.red}14`, border: `1px solid ${theme.color.red}55`, borderRadius: 12, padding: "20px 22px", opacity: realIn }}>
          <div style={{ fontFamily: mono, fontSize: 20, letterSpacing: 2, textTransform: "uppercase", color: theme.color.redBright }}>per ounce, you pay</div>
          <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 70, color: theme.color.redBright, lineHeight: 1.1 }}>+{perOz}%</div>
          <div style={{ fontFamily: body, fontSize: 22, color: theme.color.textSecondary }}>−{shrinkPct}% in the box</div>
        </div>
      </div>

      <div style={{ position: "absolute", bottom: INSET.bottom + 34, left: safe.left, width: safe.width, textAlign: "center", fontFamily: headline, fontWeight: 600, fontSize: 40, color: theme.color.textPrimary, opacity: punchIn }}>{punch}</div>
      <div style={{ position: "absolute", bottom: INSET.bottom - 10, left: 0, right: 0, textAlign: "center", fontFamily: mono, fontSize: 22, color: theme.color.textTertiary }}>{source}</div>
    </AbsoluteFill>
  );
};
