import React from "react";
import { z } from "zod";
import { AbsoluteFill } from "remotion";
import { theme, accentFor, signFor } from "../lib/theme";
import { headline, mono } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { INSET, safe } from "../lib/safezone";
import { Brandmark } from "../components/Brandmark";

export const thumbnailSchema = z.object({
  brand: z.string(),
  pctChange: z.number(),
  mode: z.enum(["shrink", "restoration"]).default("shrink"),
});

type Props = z.infer<typeof thumbnailSchema>;

// Cover/thumbnail overlay (render as a still PNG with alpha). Drop over a face
// cover frame so the profile grid reads as one series: CAUGHT: [brand] top,
// big mono −X% badge, grid texture, brandmark. Bottom scrim aids legibility.
export const Thumbnail: React.FC<Props> = ({ brand, pctChange, mode }) => {
  const accent = accentFor(mode);
  return (
    <AbsoluteFill>
      <GridTexture opacity={0.06} />
      {/* bottom scrim for legibility over a photo */}
      <AbsoluteFill
        style={{ background: `linear-gradient(to top, ${theme.color.bg} 0%, transparent 45%)` }}
      />

      <div style={{ position: "absolute", top: safe.top, left: safe.left, right: INSET.right }}>
        <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 8, textTransform: "uppercase", color: accent }}>
          Caught
        </div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 92, lineHeight: 1, color: theme.color.textPrimary }}>
          {brand}
        </div>
        <div style={{ marginTop: 18 }}>
          <Brandmark scale={1.1} />
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          bottom: INSET.bottom,
          left: safe.left,
          fontFamily: mono,
          fontWeight: 700,
          fontSize: 200,
          lineHeight: 0.9,
          color: accent,
          textShadow: `0 0 50px ${accent}66`,
        }}
      >
        {signFor(mode)}
        {pctChange}%
      </div>
    </AbsoluteFill>
  );
};
