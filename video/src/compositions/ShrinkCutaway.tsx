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
  guide: z.boolean().default(false),
});

type Props = z.infer<typeof shrinkCutawaySchema>;

const fmt = (n: number) => (Number.isInteger(n) ? `${n}` : n.toFixed(1));

// Platform-safe layout (dropped ~15% off the top + pulled in off the right action rail):
// all content lives between LEFT/RIGHT and above RESERVE_TOP. Top danger = phone status bar
// + app icons; right danger = like/comment/share rail; bottom = creator's head + captions.
const LEFT = 60;
const RIGHT = 170; // right edge of content = 1080 - 170 = 910 (clears the action rail)
const TOP = 300; // clears the status bar / top icons
const RESERVE_TOP = 1180; // bottom ~38% kept clean for the creator's head + captions

const FrameBox: React.FC<{ src: string; w: number; h: number; p: number; tag?: string; caption?: string; accent: string }> = ({ src, w, h, p, tag, caption, accent }) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, opacity: p, transform: `translateY(${interpolate(p, [0, 1], [24, 0])}px)` }}>
    {tag ? (
      <div style={{ fontFamily: mono, fontSize: 26, letterSpacing: 4, textTransform: "uppercase", color: tag.toLowerCase().startsWith("now") ? accent : theme.color.textTertiary }}>{tag}</div>
    ) : null}
    <div style={{ width: w, height: h, borderRadius: 22, overflow: "hidden", background: "#15161a", border: `1px solid ${theme.color.border}`, boxShadow: "0 18px 50px rgba(0,0,0,0.55)" }}>
      <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
    </div>
    {caption ? <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 32, color: theme.color.textPrimary }}>{caption}</div> : null}
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
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 34%, ${accent}1c 0%, transparent 52%)` }} />

      {/* header (left of the badge) */}
      <div style={{ position: "absolute", top: TOP, left: LEFT, right: 380, opacity: head, transform: `translateY(${interpolate(head, [0, 1], [18, 0])}px)` }}>
        <div style={{ fontFamily: mono, fontSize: 32, letterSpacing: 6, textTransform: "uppercase", color: accent }}>{brand}</div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 62, lineHeight: 1.02, color: theme.color.textPrimary, marginTop: 6 }}>{productName}</div>
      </div>

      {/* −% badge — top-right, INSIDE the right safe edge */}
      <div style={{ position: "absolute", top: TOP - 4, right: RIGHT, background: accent, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 72, lineHeight: 1, borderRadius: theme.radius.lg, padding: "12px 24px", opacity: badge, transform: `scale(${interpolate(badge, [0, 1], [0.7, 1])})`, boxShadow: `0 0 ${Math.round(badge * 50)}px ${accent}66`, whiteSpace: "nowrap" }}>
        {signFor(mode)}{pctVal}%
      </div>

      {/* evidence photos */}
      <div style={{ position: "absolute", top: 460, left: LEFT, right: RIGHT, height: 560, display: "flex", justifyContent: "center", alignItems: "flex-start", gap: 28 }}>
        {two ? (
          <>
            <FrameBox src={shots[0].src} w={400} h={470} p={photoIn} tag={shots[0].tag ?? `before · ${fmt(sizeBefore)} ${unit}`} caption={shots[0].caption} accent={accent} />
            <FrameBox src={shots[1].src} w={400} h={470} p={enter(frame, fps, { delay: 14, durationInFrames: 22 })} tag={shots[1].tag ?? `now · ${fmt(sizeAfter)} ${unit}`} caption={shots[1].caption} accent={accent} />
          </>
        ) : (
          <FrameBox src={shots[0]?.src ?? ""} w={820} h={540} p={photoIn} caption={shots[0]?.caption} accent={accent} />
        )}
      </div>

      {/* before → after data strip */}
      <div style={{ position: "absolute", top: 1050, left: LEFT, right: RIGHT, textAlign: "center", opacity: stripIn, transform: `translateY(${interpolate(stripIn, [0, 1], [12, 0])}px)` }}>
        <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 50, color: theme.color.textTertiary }}>{fmt(sizeBefore)} {unit}</span>
        <span style={{ fontFamily: mono, fontSize: 50, color: theme.color.textSecondary, margin: "0 22px" }}>→</span>
        <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 50, color: accent }}>{fmt(sizeAfter)} {unit}</span>
        <span style={{ fontFamily: mono, fontSize: 30, letterSpacing: 4, color: theme.color.textTertiary, marginLeft: 24, textTransform: "uppercase" }}>· same price</span>
      </div>

      {/* footer */}
      <div style={{ position: "absolute", top: 1120, left: LEFT, right: RIGHT, display: "flex", justifyContent: "space-between", alignItems: "center", opacity: stripIn }}>
        <span style={{ fontFamily: mono, fontSize: 24, color: theme.color.textSecondary }}>documented · sourced · fullcarts.org</span>
        <Brandmark scale={1.0} />
      </div>

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
