import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline } from "../lib/fonts";
import { enter } from "../lib/anim";

export const hookTextSchema = z.object({
  lines: z.array(z.string()), // wrap words in *asterisks* to red-highlight
  zone: z.enum(["above", "chin"]).default("above"), // above the head / under the chin
  accent: z.enum(["red", "green"]).default("red"),
  top: z.number().optional(), // explicit y override (e.g. 270 = just under the top danger zone, clears the eyes)
  fontSize: z.number().default(66),
});

type Props = z.infer<typeof hookTextSchema>;

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

// Transparent text overlay that floats in the negative space AROUND the talking head
// (above the head or under the chin) — graphics without cutting away. Scrim + outline
// keep it readable over a busy room. Zones avoid the face band (~y 740–1190).
export const HookText: React.FC<Props> = ({ lines, zone, accent, top: topOverride, fontSize }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const color = theme.color[accent];
  const top = topOverride ?? (zone === "above" ? 360 : 1230);

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top, left: 60, right: 170, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
        {lines.map((line, i) => {
          const p = enter(frame, fps, { delay: i * 5, durationInFrames: 10 });
          return (
            <div
              key={i}
              style={{
                fontFamily: headline,
                fontWeight: 700,
                fontSize,
                lineHeight: 1.08,
                textAlign: "center",
                color: theme.color.textPrimary,
                background: "rgba(10,11,13,0.66)",
                borderRadius: 12,
                padding: "6px 20px",
                backdropFilter: "blur(3px)",
                textShadow: "0 2px 0 #000, 0 0 8px #000",
                opacity: p,
                transform: `translateY(${interpolate(p, [0, 1], [26, 0])}px)`,
              }}
            >
              {parse(line, color)}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
