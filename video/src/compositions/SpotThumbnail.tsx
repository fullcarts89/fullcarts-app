import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

// Self-contained cover/thumbnail for the "Spot the Skimp" video. Opaque full-frame
// — render as a still PNG (no face frame needed). Big title + difficulty ladder +
// the 6-photo evidence grid + the comment-bait hook. On-brand graphite/red.
export const spotThumbnailSchema = z.object({
  titleLines: z.array(z.string()).default(["Spot", "the Skimp"]),
  sub: z.string().default("Easy → Impossible"),
  hook: z.string().default("Can you spot all *6?*"),
  images: z.array(z.string()).default([]),
});

type Props = z.infer<typeof spotThumbnailSchema>;

const STAR_PTS = "50,4 61,37 97,38 68,59 79,94 50,72 21,94 32,59 3,38 39,37";
const Star: React.FC<{ size: number; color: string }> = ({ size, color }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <polygon points={STAR_PTS} fill={color} />
  </svg>
);

const hl = (text: string) =>
  text.split("*").map((s, i) =>
    i % 2 === 1 ? <span key={i} style={{ color: theme.color.red }}>{s}</span> : <React.Fragment key={i}>{s}</React.Fragment>
  );

export const SpotThumbnail: React.FC<Props> = ({ titleLines, sub, hook, images }) => {
  const COLS = 3;
  const CW = 300;
  const CH = 230;
  const GAP = 18;
  const gridW = COLS * CW + (COLS - 1) * GAP;
  const left = (1080 - gridW) / 2;
  const ladder = [theme.color.green, theme.color.green, theme.color.amber, theme.color.amber, theme.color.red];
  return (
    <AbsoluteFill style={{ background: theme.color.bg }}>
      <GridTexture opacity={0.07} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 28%, ${theme.color.red}26 0%, transparent 58%)` }} />

      <div style={{ position: "absolute", top: 250, left: 60 }}><Brandmark scale={1.2} /></div>

      <div style={{ position: "absolute", top: 360, left: 60, right: 60 }}>
        <div style={{ fontFamily: mono, fontSize: 34, letterSpacing: 8, textTransform: "uppercase", color: theme.color.red }}>The Game</div>
        {titleLines.map((l, i) => (
          <div key={i} style={{ fontFamily: headline, fontWeight: 700, fontSize: 168, lineHeight: 0.9, letterSpacing: -3, color: theme.color.textPrimary, textTransform: "uppercase" }}>{l}</div>
        ))}
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 26 }}>
          <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 40, letterSpacing: 2, color: theme.color.amber, textTransform: "uppercase" }}>{sub}</span>
          <div style={{ display: "flex", gap: 8 }}>
            {ladder.map((c, i) => <Star key={i} size={44} color={c} />)}
          </div>
        </div>
      </div>

      {/* evidence grid */}
      {images.slice(0, 6).map((img, i) => {
        const col = i % COLS;
        const row = Math.floor(i / COLS);
        return (
          <div key={i} style={{ position: "absolute", left: left + col * (CW + GAP), top: 740 + row * (CH + GAP), width: CW, height: CH, borderRadius: 14, overflow: "hidden", background: "#fff", border: `1px solid ${theme.color.border}` }}>
            <Img src={staticFile(img)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          </div>
        );
      })}

      {/* comment-bait hook */}
      <div style={{ position: "absolute", top: 1500, left: 60, right: 60, textAlign: "center" }}>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 96, lineHeight: 1.0, color: theme.color.textPrimary }}>{hl(hook)}</div>
        <div style={{ fontFamily: mono, fontSize: 34, letterSpacing: 2, color: theme.color.textSecondary, marginTop: 22 }}>1 of them is a <span style={{ color: theme.color.red, fontWeight: 700 }}>TRICK</span></div>
      </div>
    </AbsoluteFill>
  );
};
