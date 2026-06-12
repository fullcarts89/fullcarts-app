import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { INSET } from "../lib/safezone";

export const beforeAfterSchema = z.object({
  beforeSrc: z.string(),
  afterSrc: z.string(),
  beforeTag: z.string().default("BEFORE"),
  afterTag: z.string().default("AFTER"),
  beforeSize: z.string(),
  beforePer: z.string(),
  afterSize: z.string(),
  afterPer: z.string(),
  deltaLabel: z.string(),
});

type Props = z.infer<typeof beforeAfterSchema>;

// Clean before→after card: the real can (cropped from the listing screenshot, so the
// Walmart clutter is out of frame) + clean brand labels for size + price-per-oz.
// Real product image, real numbers — never fabricated.
const Row: React.FC<{ src: string; tag: string; size: string; per: string; top: number; height: number }> = ({
  src,
  tag,
  size,
  per,
  top,
  height,
}) => (
  <div
    style={{
      position: "absolute",
      top,
      left: 56,
      right: INSET.right,
      height,
      display: "flex",
      background: theme.color.card,
      border: `1px solid ${theme.color.border}`,
      borderRadius: theme.radius.lg,
      overflow: "hidden",
    }}
  >
    <div style={{ width: height * 0.74, height: "100%", position: "relative", background: "#fff", flexShrink: 0 }}>
      <Img src={src} style={{ position: "absolute", width: "100%", height: "100%", objectFit: "cover", objectPosition: "left center" }} />
    </div>
    <div style={{ flex: 1, padding: "0 36px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
      <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 26, letterSpacing: 4, color: theme.color.red }}>{tag}</span>
      <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 76, lineHeight: 1, color: theme.color.textPrimary, marginTop: 6 }}>{size}</div>
      <div style={{ fontFamily: mono, fontSize: 34, color: theme.color.textSecondary, marginTop: 10 }}>{per}</div>
    </div>
  </div>
);

export const BeforeAfter: React.FC<Props> = ({ beforeSrc, afterSrc, beforeTag, afterTag, beforeSize, beforePer, afterSize, afterPer, deltaLabel }) => {
  const top = INSET.top + 40;
  const bottom = 1920 - INSET.bottom - 40;
  const usable = bottom - top;
  const gap = 120;
  const h = (usable - gap) / 2;
  return (
    <AbsoluteFill style={{ background: theme.color.bg }}>
      <GridTexture opacity={0.06} />
      <Row src={staticFile(beforeSrc)} tag={beforeTag} size={beforeSize} per={beforePer} top={top} height={h} />
      <Row src={staticFile(afterSrc)} tag={afterTag} size={afterSize} per={afterPer} top={top + h + gap} height={h} />
      <div style={{ position: "absolute", top: top + h + (gap - 72) / 2, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <div style={{ background: theme.color.red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 44, borderRadius: 14, padding: "8px 26px" }}>
          {deltaLabel}
        </div>
      </div>
    </AbsoluteFill>
  );
};

