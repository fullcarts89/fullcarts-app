import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { theme } from "../lib/theme";
import { mono } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { INSET } from "../lib/safezone";

export const beforeAfterSchema = z.object({
  beforeSrc: z.string(),
  afterSrc: z.string(),
  beforeTag: z.string().default("BEFORE"),
  afterTag: z.string().default("AFTER"),
  beforeLabel: z.string(),
  afterLabel: z.string(),
  deltaLabel: z.string(),
});

type Props = z.infer<typeof beforeAfterSchema>;

// Stacked before→after evidence card (real listing screenshots). Rendered to a still
// PNG and used as the proof cutaway. Built from REAL images — never fabricated.
const Panel: React.FC<{ src: string; tag: string; label: string; top: number; height: number }> = ({
  src,
  tag,
  label,
  top,
  height,
}) => (
  <div
    style={{
      position: "absolute",
      top,
      left: 48,
      right: 48,
      height,
      background: theme.color.card,
      border: `1px solid ${theme.color.border}`,
      borderRadius: theme.radius.lg,
      overflow: "hidden",
    }}
  >
    <Img src={src} style={{ position: "absolute", width: "100%", height: "100%", objectFit: "contain" }} />
    <div
      style={{
        position: "absolute",
        top: 16,
        left: 16,
        display: "flex",
        alignItems: "center",
        gap: 12,
        background: "rgba(10,11,13,0.82)",
        borderLeft: `5px solid ${theme.color.red}`,
        borderRadius: 8,
        padding: "8px 14px",
      }}
    >
      <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 24, letterSpacing: 3, color: theme.color.red }}>{tag}</span>
      <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 26, color: theme.color.textPrimary }}>{label}</span>
    </div>
  </div>
);

export const BeforeAfter: React.FC<Props> = ({ beforeSrc, afterSrc, beforeTag, afterTag, beforeLabel, afterLabel, deltaLabel }) => {
  const top = INSET.top; // 240
  const bottom = 1920 - INSET.bottom; // 1470
  const usable = bottom - top; // 1230
  const gap = 96;
  const h = (usable - gap) / 2;
  return (
    <AbsoluteFill style={{ background: theme.color.bg }}>
      <GridTexture opacity={0.06} />
      <Panel src={staticFile(beforeSrc)} tag={beforeTag} label={beforeLabel} top={top} height={h} />
      <Panel src={staticFile(afterSrc)} tag={afterTag} label={afterLabel} top={top + h + gap} height={h} />
      {/* delta badge centered in the gap */}
      <div
        style={{
          position: "absolute",
          top: top + h + (gap - 64) / 2,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            background: theme.color.red,
            color: theme.color.textPrimary,
            fontFamily: mono,
            fontWeight: 700,
            fontSize: 40,
            borderRadius: 12,
            padding: "6px 22px",
          }}
        >
          {deltaLabel}
        </div>
      </div>
    </AbsoluteFill>
  );
};
