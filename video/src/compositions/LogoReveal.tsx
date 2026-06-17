import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline } from "../lib/fonts";
import { enter } from "../lib/anim";
import { GridTexture } from "../components/GridTexture";

export const logoRevealSchema = z.object({
  src: z.string(),
  lines: z.array(z.string()).default([]), // wrap words in *asterisks* to red-highlight
  logoWidth: z.number().default(520),
});

type Props = z.infer<typeof logoRevealSchema>;

const parse = (text: string, color: string) =>
  text.split("*").map((seg, i) =>
    i % 2 === 1 ? (
      <span key={i} style={{ color }}>
        {seg}
      </span>
    ) : (
      <React.Fragment key={i}>{seg}</React.Fragment>
    )
  );

// Full-frame parent-company reveal: a REAL logo (Bucket-1) over graphite with a
// caption stating the ownership fact. For the "illusion of choice" beat.
export const LogoReveal: React.FC<Props> = ({ src, lines, logoWidth }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const logoIn = enter(frame, fps, { durationInFrames: 14 });
  return (
    <AbsoluteFill style={{ background: theme.color.bg }}>
      <GridTexture opacity={0.06} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 40%, ${theme.color.red}1c 0%, transparent 55%)` }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", padding: "0 80px" }}>
        <div
          style={{
            width: logoWidth,
            background: "#ffffff",
            borderRadius: 28,
            padding: "44px 40px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: logoIn,
            transform: `scale(${interpolate(logoIn, [0, 1], [0.85, 1])}) translateY(${interpolate(logoIn, [0, 1], [18, 0])}px)`,
            boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
          }}
        >
          <Img src={staticFile(src)} style={{ width: "100%", objectFit: "contain" }} />
        </div>
        {lines.map((line, i) => {
          const p = enter(frame, fps, { delay: 14 + i * 6, durationInFrames: 12 });
          return (
            <div
              key={i}
              style={{
                fontFamily: headline,
                fontWeight: 700,
                fontSize: 64,
                lineHeight: 1.08,
                textAlign: "center",
                color: theme.color.textPrimary,
                marginTop: i === 0 ? 54 : 6,
                opacity: p,
                transform: `translateY(${interpolate(p, [0, 1], [24, 0])}px)`,
              }}
            >
              {parse(line, theme.color.red)}
            </div>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
