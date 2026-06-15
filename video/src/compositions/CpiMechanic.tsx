import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { INSET, safe } from "../lib/safezone";
import { Brandmark } from "../components/Brandmark";
import { MusicBed } from "../components/MusicBed";

// RECEIPT beat — WHY the index misses shrinkflation, told as a step animation:
// a box keeps its $ price tag but loses ounces, so the price PER OUNCE climbs.
// CPI watches the sticker (≈0%); you actually pay +18%/oz. The ounce count and
// per-ounce price tick up live as the box shrinks. Lands the "+X%/oz" on the
// spoken "20% more per ounce". Full-frame, opaque → render h264.
export const cpiMechanicSchema = z.object({
  eyebrow: z.string().default("WHY THE NUMBER LIES"),
  price: z.number().default(5.0), // sticker $, stays flat
  ozBefore: z.number().default(20),
  shrinkPct: z.number().default(15),
  startDelay: z.number().default(6),
  shrinkDelay: z.number().default(70),
  shrinkFrames: z.number().default(60),
  music: z.object({ src: z.string().default("audio/bg-loop.mp3"), volume: z.number().default(0.165) }).default({}),
});

type Props = z.infer<typeof cpiMechanicSchema>;
const usd = (n: number, d = 2) => "$" + n.toFixed(d);

export const CpiMechanic: React.FC<Props> = ({ eyebrow, price, ozBefore, shrinkPct, startDelay, shrinkDelay, shrinkFrames, music }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lf = frame - startDelay;

  const labelIn = enter(lf, fps, { durationInFrames: 14 });
  const stageIn = enter(lf, fps, { delay: 14, durationInFrames: 16 });
  const shrink = enter(lf, fps, { delay: shrinkDelay, durationInFrames: shrinkFrames }); // 0→1
  const verdictIn = enter(lf, fps, { delay: shrinkDelay + shrinkFrames + 6, durationInFrames: 16 });

  const s = shrinkPct / 100;
  const oz = ozBefore * (1 - s * shrink);
  const perOzBefore = price / ozBefore;
  const perOz = price / oz;
  const perOzPct = Math.round((perOz / perOzBefore - 1) * 100);
  const boxScaleY = 1 - s * shrink;

  const TOP = safe.top;
  const CW = safe.width;
  const boxW = 260;
  const boxAreaH = 380;
  const boxLeft = safe.left + 30;
  const baseY = TOP + 250 + boxAreaH; // box bottoms planted here

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      <MusicBed src={music.src} volume={music.volume} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 30%, ${theme.color.red}1f 0%, transparent 55%)` }} />
      <div style={{ position: "absolute", top: TOP, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Brandmark scale={1.0} />
      </div>

      <div style={{ position: "absolute", top: TOP + 80, left: safe.left, width: CW, opacity: labelIn }}>
        <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 4, textTransform: "uppercase", color: theme.color.red }}>{eyebrow}</div>
        <div style={{ fontFamily: body, fontSize: 26, color: theme.color.textSecondary, marginTop: 8 }}>same price, fewer ounces = more per ounce</div>
      </div>

      {/* shrinking box, planted at baseY */}
      <div style={{ position: "absolute", left: boxLeft, top: baseY, width: boxW, height: boxAreaH, transformOrigin: "bottom center", transform: `scaleY(${boxScaleY})` }}>
        <div style={{ position: "absolute", bottom: 0, width: "100%", height: "100%", background: theme.color.card, border: `2px solid ${theme.color.border}`, borderRadius: 10, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", gap: 16 }}>
          <div style={{ width: "60%", height: 16, background: theme.color.red, opacity: 0.85, borderRadius: 3 }} />
          <div style={{ width: "44%", height: 10, background: theme.color.border, borderRadius: 3 }} />
          <div style={{ width: "30%", height: 10, background: theme.color.border, borderRadius: 3 }} />
        </div>
      </div>
      {/* ounces tag, counter-positioned (not scaled) below the box */}
      <div style={{ position: "absolute", left: boxLeft, top: baseY + 22, width: boxW, textAlign: "center", fontFamily: mono, fontWeight: 700, fontSize: 40, color: theme.color.textPrimary, opacity: stageIn }}>
        {oz.toFixed(1)} <span style={{ fontSize: 22, color: theme.color.textTertiary }}>oz</span>
      </div>
      {/* price tag — never moves */}
      <div style={{ position: "absolute", left: boxLeft + 18, top: TOP + 340, transform: "rotate(-6deg)", zIndex: 3, opacity: stageIn }}>
        <div style={{ background: theme.color.amber, color: theme.color.bg, fontFamily: mono, fontWeight: 700, fontSize: 38, padding: "10px 16px", borderRadius: 8 }}>{usd(price)}</div>
        <div style={{ fontFamily: mono, fontSize: 16, color: theme.color.textTertiary, textTransform: "uppercase", letterSpacing: 2, marginTop: 6, textAlign: "center" }}>price unchanged</div>
      </div>

      {/* right column: the two things that move (or don't) */}
      <div style={{ position: "absolute", left: boxLeft + boxW + 70, top: TOP + 250, width: CW - boxW - 100, display: "flex", flexDirection: "column", gap: 26, opacity: stageIn }}>
        <div>
          <div style={{ fontFamily: mono, fontSize: 20, letterSpacing: 1, textTransform: "uppercase", color: theme.color.textTertiary }}>what CPI watches</div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
            <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 54, color: theme.color.textSecondary }}>{usd(price)}</span>
            <span style={{ fontFamily: mono, fontSize: 28, color: theme.color.textSecondary }}>= +0%</span>
          </div>
          <div style={{ height: 8, background: theme.color.card, borderRadius: 4, marginTop: 8 }}>
            <div style={{ width: "4%", height: "100%", background: theme.color.textSecondary, borderRadius: 4 }} />
          </div>
        </div>
        <div>
          <div style={{ fontFamily: mono, fontSize: 20, letterSpacing: 1, textTransform: "uppercase", color: theme.color.redBright }}>what you pay / ounce</div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
            <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 54, color: theme.color.redBright }}>{usd(perOz)}</span>
            <span style={{ fontFamily: mono, fontSize: 28, color: theme.color.redBright }}>+{perOzPct}%</span>
          </div>
          <div style={{ height: 8, background: theme.color.card, borderRadius: 4, marginTop: 8 }}>
            <div style={{ width: `${interpolate(shrink, [0, 1], [4, 100])}%`, height: "100%", background: theme.color.red, borderRadius: 4 }} />
          </div>
        </div>
      </div>

      <div style={{ position: "absolute", bottom: INSET.bottom + 30, left: safe.left, width: CW, textAlign: "center", fontFamily: headline, fontWeight: 600, fontSize: 40, color: theme.color.textPrimary, opacity: verdictIn }}>CPI watches the sticker, not the shrink</div>
      <div style={{ position: "absolute", bottom: INSET.bottom - 10, left: 0, right: 0, textAlign: "center", fontFamily: mono, fontSize: 20, color: theme.color.textTertiary }}>same price · 15% less inside = ~18% more per ounce</div>
    </AbsoluteFill>
  );
};
