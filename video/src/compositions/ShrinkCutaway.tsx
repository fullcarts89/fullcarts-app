import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme, accentFor, signFor } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter, countUp } from "../lib/anim";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";
import { safe, INSET } from "../lib/safezone";

export const shrinkCutawaySchema = z.object({
  brand: z.string(),
  productName: z.string(),
  sizeBefore: z.number(),
  sizeAfter: z.number(),
  unit: z.string(),
  pctChange: z.number(), // positive magnitude
  mode: z.enum(["shrink", "restoration"]).default("shrink"),
});

type Props = z.infer<typeof shrinkCutawaySchema>;

const fmt = (n: number) => (Number.isInteger(n) ? `${n}` : n.toFixed(1));

// Full-frame branded before→after "shrink" shot — the cutaway that plays while the
// creator talks about each product. Opaque graphite + grid + alert-red, mirrors the
// ShrinkOverlay visual language (brand · product · bars · big −%) but full-screen.
export const ShrinkCutaway: React.FC<Props> = ({ brand, productName, sizeBefore, sizeAfter, unit, pctChange, mode }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = accentFor(mode);

  const head = enter(frame, fps, { durationInFrames: 14 });
  const barGrow = enter(frame, fps, { delay: 18, durationInFrames: 28 });
  const pop = enter(frame, fps, { delay: 22, durationInFrames: 16 });
  const pctVal = countUp(frame, fps, pctChange, { delay: 20, durationInFrames: 30, decimals: 1 });

  const max = Math.max(sizeBefore, sizeAfter);
  const beforeW = (sizeBefore / max) * 100;
  const afterW = interpolate(barGrow, [0, 1], [beforeW, (sizeAfter / max) * 100]);

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      <GridTexture opacity={0.06} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 30%, ${accent}1f 0%, transparent 55%)` }} />

      {/* brand + product */}
      <div style={{ position: "absolute", top: safe.top, left: safe.left, right: safe.left, opacity: head, transform: `translateY(${interpolate(head, [0, 1], [20, 0])}px)` }}>
        <div style={{ fontFamily: mono, fontSize: 34, letterSpacing: 6, textTransform: "uppercase", color: accent }}>{brand}</div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 78, lineHeight: 1.02, color: theme.color.textPrimary, marginTop: 10 }}>{productName}</div>
      </div>

      {/* hero −% */}
      <div style={{ position: "absolute", top: 560, left: 0, right: 0, textAlign: "center", opacity: pop, transform: `scale(${interpolate(pop, [0, 1], [0.7, 1])})` }}>
        <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 260, lineHeight: 0.9, color: accent, textShadow: `0 0 70px ${accent}55` }}>
          {signFor(mode)}{pctVal}%
        </div>
        <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 8, textTransform: "uppercase", color: theme.color.textSecondary, marginTop: 10 }}>smaller · same price</div>
      </div>

      {/* before → after bars */}
      <div style={{ position: "absolute", top: 1150, left: safe.left, right: safe.left, display: "flex", flexDirection: "column", gap: 36 }}>
        <Bar tag="BEFORE" label={`${fmt(sizeBefore)} ${unit}`} width={beforeW} color={theme.color.textTertiary} faded />
        <Bar tag="NOW" label={`${fmt(sizeAfter)} ${unit}`} width={afterW} color={accent} />
      </div>

      {/* footer */}
      <div style={{ position: "absolute", bottom: INSET.bottom - 60, left: safe.left, right: safe.left, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontFamily: mono, fontSize: 26, color: theme.color.textSecondary }}>documented · sourced</span>
        <Brandmark scale={1.1} />
      </div>
    </AbsoluteFill>
  );
};

const Bar: React.FC<{ tag: string; label: string; width: number; color: string; faded?: boolean }> = ({ tag, label, width, color, faded }) => (
  <div>
    <div style={{ fontFamily: mono, fontSize: 24, letterSpacing: 3, color: theme.color.textTertiary, marginBottom: 8 }}>{tag}</div>
    <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
      <div style={{ height: 46, width: `${width}%`, minWidth: 60, background: color, opacity: faded ? 0.4 : 1, borderRadius: 8 }} />
      <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 48, color: theme.color.textPrimary, whiteSpace: "nowrap" }}>{label}</span>
    </div>
  </div>
);
