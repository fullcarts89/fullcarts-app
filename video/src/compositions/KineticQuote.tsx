import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline } from "../lib/fonts";
import { enter } from "../lib/anim";
import { GridTexture } from "../components/GridTexture";

export const kineticQuoteSchema = z.object({
  lines: z.array(z.string()), // wrap words in *asterisks* to red-highlight
  accent: z.enum(["red", "green"]).default("red"),
  align: z.enum(["center", "left"]).default("center"),
});

type Props = z.infer<typeof kineticQuoteSchema>;

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

// Full-frame branded kinetic typography — for punch lines ("it's not you",
// "rockets and feathers", "a permanent raise"). Opaque, so it acts as a cutaway.
export const KineticQuote: React.FC<Props> = ({ lines, accent, align }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const color = theme.color[accent];
  return (
    <AbsoluteFill style={{ background: theme.color.bg }}>
      <GridTexture opacity={0.06} />
      <AbsoluteFill
        style={{
          alignItems: align === "center" ? "center" : "flex-start",
          justifyContent: "center",
          padding: "0 90px",
        }}
      >
        {lines.map((line, i) => {
          const p = enter(frame, fps, { delay: i * 6, durationInFrames: 12 });
          return (
            <div
              key={i}
              style={{
                fontFamily: headline,
                fontWeight: 700,
                fontSize: 96,
                lineHeight: 1.06,
                letterSpacing: -1,
                color: theme.color.textPrimary,
                textAlign: align,
                opacity: p,
                transform: `translateY(${interpolate(p, [0, 1], [40, 0])}px)`,
              }}
            >
              {parse(line, color)}
            </div>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
