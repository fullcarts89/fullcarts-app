import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { Brandmark } from "../components/Brandmark";
import { GridTexture } from "../components/GridTexture";
import { INSET, safe } from "../lib/safezone";

export const outroCardSchema = z.object({
  tagline: z.string().default("Every claim.\n*Source-cited.*"), // \n = manual line break
  followLine: z.string().default("follow — I catch the next one"),
  url: z.string().default("fullcarts.org"),
  statLine: z.string().default("2,200+ documented shrinks · every one source-cited"),
});

// z.input → defaulted fields stay optional; FinalVideo cues pass props without zod parsing
type Props = z.input<typeof outroCardSchema>;

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

// Branded outro / CTA card to close every episode: brandmark, tagline, the follow
// ask, and the URL in a red chip. Full-frame, opaque — the one full-screen beat
// that's allowed to be pure brand. Render at the end, over or after the last line.
export const OutroCard: React.FC<Props> = ({
  tagline = "Every claim.\n*Source-cited.*",
  followLine = "follow — I catch the next one",
  url = "fullcarts.org",
  statLine = "2,200+ documented shrinks · every one source-cited",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const markIn = enter(frame, fps, { durationInFrames: 14 });
  const taglineIn = enter(frame, fps, { delay: 10, durationInFrames: 14 });
  const followIn = enter(frame, fps, { delay: 22, durationInFrames: 12 });
  const urlIn = enter(frame, fps, { delay: 30, durationInFrames: 14 });
  const statIn = enter(frame, fps, { delay: 42, durationInFrames: 12 });

  return (
    <AbsoluteFill style={{ background: theme.color.bg }}>
      <GridTexture opacity={0.06} />
      <AbsoluteFill
        style={{ background: `radial-gradient(circle at 50% 42%, ${theme.color.red}1e 0%, transparent 55%)` }}
      />

      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            opacity: markIn,
            transform: `scale(${interpolate(markIn, [0, 1], [0.85, 1])}) translateY(${interpolate(markIn, [0, 1], [16, 0])}px)`,
          }}
        >
          <Brandmark scale={2.4} />
        </div>

        <div
          style={{
            fontFamily: headline,
            fontWeight: 700,
            fontSize: 72,
            lineHeight: 1.12,
            textAlign: "center",
            whiteSpace: "pre-line",
            color: theme.color.textPrimary,
            maxWidth: safe.width,
            marginTop: 44,
            opacity: taglineIn,
            transform: `translateY(${interpolate(taglineIn, [0, 1], [18, 0])}px)`,
          }}
        >
          {parse(tagline, theme.color.red)}
        </div>

        <div
          style={{
            fontFamily: headline,
            fontWeight: 500,
            fontSize: 40,
            color: theme.color.textSecondary,
            marginTop: 22,
            opacity: followIn,
            transform: `translateY(${interpolate(followIn, [0, 1], [14, 0])}px)`,
          }}
        >
          {followLine}
        </div>

        <div
          style={{
            fontFamily: mono,
            fontWeight: 700,
            fontSize: 46,
            letterSpacing: 1,
            color: theme.color.textPrimary,
            background: theme.color.red,
            borderRadius: theme.radius.md,
            padding: "14px 34px",
            marginTop: 36,
            opacity: urlIn,
            transform: `scale(${interpolate(urlIn, [0, 1], [0.9, 1])})`,
            boxShadow: `0 0 ${Math.round(urlIn * 60)}px ${theme.color.red}66`,
          }}
        >
          {url}
        </div>
      </AbsoluteFill>

      <div
        style={{
          position: "absolute",
          bottom: INSET.bottom,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: mono,
          fontSize: 24,
          color: theme.color.textTertiary,
          opacity: statIn,
        }}
      >
        {statLine}
      </div>
    </AbsoluteFill>
  );
};
