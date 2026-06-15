import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme, accentFor, signFor } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter, countUp } from "../lib/anim";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

export const shrinkCutawaySchema = z.object({
  brand: z.string(),
  productName: z.string(),
  sizeBefore: z.number(),
  sizeAfter: z.number(),
  unit: z.string(),
  pctChange: z.number(),
  mode: z.enum(["shrink", "restoration"]).default("shrink"),
  // 1 or 2 real evidence photos. caption sits under each frame.
  shots: z.array(z.object({ src: z.string(), caption: z.string().optional(), tag: z.string().optional() })).default([]),
  // draw faint guides marking the reserved talking-head + caption zone (preview only)
  guide: z.boolean().default(false),
});

type Props = z.infer<typeof shrinkCutawaySchema>;

const fmt = (n: number) => (Number.isInteger(n) ? `${n}` : n.toFixed(1));

// Reserved zone: the bottom ~42% is kept clean so the creator can overlay their
// (minimized) talking head + burned-in captions. All evidence lives above it.
const RESERVE_TOP = 1120;

const FrameBox: React.FC<{ src: string; w: number; h: number; p: number; tag?: string; caption?: string; accent: string }> = ({ src, w, h, p, tag, caption, accent }) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14, opacity: p, transform: `translateY(${interpolate(p, [0, 1], [24, 0])}px)` }}>
    {tag ? (
      <div style={{ fontFamily: mono, fontSize: 26, letterSpacing: 4, textTransform: "uppercase", color: tag.toLowerCase().startsWith("now") ? accent : theme.color.textTertiary }}>{tag}</div>
    ) : null}
    <div style={{ width: w, height: h, borderRadius: 22, overflow: "hidden", background: "#15161a", border: `1px solid ${theme.color.border}`, boxShadow: "0 18px 50px rgba(0,0,0,0.5)" }}>
      <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
    </div>
    {caption ? <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 34, color: theme.color.textPrimary }}>{caption}</div> : null}
  </div>
);

export const ShrinkCutaway: React.FC<Props> = ({ brand, productName, sizeBefore, sizeAfter, unit, pctChange, mode, shots, guide }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = accentFor(mode);

  const head = enter(frame, fps, { durationInFrames: 14 });
  const photoIn = enter(frame, fps, { delay: 8, durationInFrames: 22 });
  const badge = enter(frame, fps, { delay: 18, durationInFrames: 16 });
  const stripIn = enter(frame, fps, { delay: 26, durationInFrames: 16 });
  const pctVal = countUp(frame, fps, pctChange, { delay: 16, durationInFrames: 28, decimals: 1 });

  const two = shots.length >= 2;

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      <GridTexture opacity={0.06} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 22%, ${accent}1c 0%, transparent 50%)` }} />

      {/* header */}
      <div style={{ position: "absolute", top: 96, left: 60, right: 320, opacity: head, transform: `translateY(${interpolate(head, [0, 1], [18, 0])}px)` }}>
        <div style={{ fontFamily: mono, fontSize: 32, letterSpacing: 6, textTransform: "uppercase", color: accent }}>{brand}</div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 62, lineHeight: 1.02, color: theme.color.textPrimary, marginTop: 6 }}>{productName}</div>
      </div>

      {/* −% badge, top-right */}
      <div style={{ position: "absolute", top: 104, right: 60, background: accent, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 72, lineHeight: 1, borderRadius: theme.radius.lg, padding: "12px 24px", opacity: badge, transform: `scale(${interpolate(badge, [0, 1], [0.7, 1])})`, boxShadow: `0 0 ${Math.round(badge * 50)}px ${accent}66`, whiteSpace: "nowrap" }}>
        {signFor(mode)}{pctVal}%
      </div>

      {/* evidence photos */}
      <div style={{ position: "absolute", top: 280, left: 60, right: 60, height: 700, display: "flex", justifyContent: "center", alignItems: "flex-start", gap: 36 }}>
        {two ? (
          <>
            <FrameBox src={shots[0].src} w={460} h={580} p={photoIn} tag={shots[0].tag ?? `before · ${fmt(sizeBefore)} ${unit}`} caption={shots[0].caption} accent={accent} />
            <FrameBox src={shots[1].src} w={460} h={580} p={enter(frame, fps, { delay: 14, durationInFrames: 22 })} tag={shots[1].tag ?? `now · ${fmt(sizeAfter)} ${unit}`} caption={shots[1].caption} accent={accent} />
          </>
        ) : (
          <FrameBox src={shots[0]?.src ?? ""} w={900} h={600} p={photoIn} caption={shots[0]?.caption} accent={accent} />
        )}
      </div>

      {/* before → after data strip */}
      <div style={{ position: "absolute", top: 1010, left: 60, right: 60, textAlign: "center", opacity: stripIn, transform: `translateY(${interpolate(stripIn, [0, 1], [12, 0])}px)` }}>
        <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 50, color: theme.color.textTertiary }}>{fmt(sizeBefore)} {unit}</span>
        <span style={{ fontFamily: mono, fontSize: 50, color: theme.color.textSecondary, margin: "0 22px" }}>→</span>
        <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 50, color: accent }}>{fmt(sizeAfter)} {unit}</span>
        <span style={{ fontFamily: mono, fontSize: 30, letterSpacing: 4, color: theme.color.textTertiary, marginLeft: 26, textTransform: "uppercase" }}>· same price</span>
      </div>

      {/* footer */}
      <div style={{ position: "absolute", top: 1066, left: 60, right: 60, display: "flex", justifyContent: "space-between", alignItems: "center", opacity: stripIn }}>
        <span style={{ fontFamily: mono, fontSize: 24, color: theme.color.textSecondary }}>documented · sourced · fullcarts.org</span>
        <Brandmark scale={1.0} />
      </div>

      {/* reserved zone for the creator's talking head + captions (guides shown in preview only) */}
      {guide ? (
        <>
          <div style={{ position: "absolute", top: RESERVE_TOP, left: 40, right: 40, bottom: 40, border: `2px dashed ${theme.color.border}`, borderRadius: 18 }} />
          <div style={{ position: "absolute", top: RESERVE_TOP + 24, left: 0, right: 0, textAlign: "center", fontFamily: mono, fontSize: 28, letterSpacing: 3, color: theme.color.textTertiary }}>
            ↓ RESERVED: your talking head + captions ↓
          </div>
        </>
      ) : null}
    </AbsoluteFill>
  );
};
