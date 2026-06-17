import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

// Static cover / thumbnail (render a single still PNG). Built on the REAL shelf
// photo so the size gap is visible, with the Caught: framing + the −% badge.
// Works as a 9:16 Reels/Shorts cover. No face needed.
export const gmThumbSchema = z.object({
  src: z.string().default("ctc_evidence.jpg"),
  brand: z.string().default("GENERAL MILLS"),
  product: z.string().default("Cinnamon Toast Crunch"),
  pct: z.string().default("−16.7%"),
  before: z.string().default("12 OZ"),
  after: z.string().default("10 OZ"),
  kicker: z.string().default("SAME PRICE."),
});

type Props = z.infer<typeof gmThumbSchema>;

export const GMThumb: React.FC<Props> = ({ src, brand, product, pct, before, after, kicker }) => {
  const red = theme.color.red;
  return (
    <AbsoluteFill style={{ background: theme.color.bg }}>
      <GridTexture opacity={0.07} />
      <AbsoluteFill style={{ background: `radial-gradient(60% 40% at 50% 40%, ${red}1c 0%, transparent 60%)` }} />

      {/* the real boxes — contain so both stay fully visible */}
      <div style={{ position: "absolute", top: 470, left: 40, right: 40, height: 760 }}>
        <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "contain", borderRadius: 20, filter: "saturate(1.05)" }} />
      </div>

      {/* eyebrow + brand */}
      <div style={{ position: "absolute", top: 250, left: 60, right: 60 }}>
        <div style={{ fontFamily: mono, fontSize: 38, letterSpacing: 10, textTransform: "uppercase", color: red }}>Caught</div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 96, lineHeight: 0.96, color: theme.color.textPrimary, marginTop: 4 }}>{brand}</div>
        <div style={{ fontFamily: mono, fontSize: 34, letterSpacing: 2, color: theme.color.textSecondary, marginTop: 10 }}>{product}</div>
      </div>

      {/* huge −% badge, top-right over the photo */}
      <div style={{ position: "absolute", top: 540, right: 70, background: red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 132, lineHeight: 0.9, borderRadius: 26, padding: "18px 30px", boxShadow: `0 0 70px ${red}88`, transform: "rotate(-4deg)" }}>
        {pct}
      </div>

      {/* before → after + kicker */}
      <div style={{ position: "absolute", top: 1270, left: 0, right: 0, textAlign: "center" }}>
        <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 84, color: theme.color.textPrimary }}>
          {before} <span style={{ color: theme.color.textSecondary }}>→</span> <span style={{ color: red }}>{after}</span>
        </div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 110, color: theme.color.textPrimary, marginTop: 10, letterSpacing: -1 }}>{kicker}</div>
      </div>

      {/* brandmark + url */}
      <div style={{ position: "absolute", bottom: 150, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
        <Brandmark scale={1.5} />
        <div style={{ fontFamily: mono, fontSize: 32, letterSpacing: 3, color: theme.color.textTertiary }}>fullcarts.org</div>
      </div>
    </AbsoluteFill>
  );
};
