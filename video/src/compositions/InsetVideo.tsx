import React from "react";
import { z } from "zod";
import { AbsoluteFill, OffthreadVideo, staticFile, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { mono } from "../lib/fonts";
import { enter } from "../lib/anim";

export const insetVideoSchema = z.object({
  src: z.string(),
  top: z.number().default(330),
  height: z.number().default(430),
  left: z.number().default(60),
  right: z.number().default(170),
  label: z.string().optional(), // small mono caption under the frame
  fit: z.enum(["cover", "contain"]).default("cover"),
});

type Props = z.infer<typeof insetVideoSchema>;

// A real screen-recording / clip played inside a positioned, rounded frame —
// layers OVER a full-frame card (e.g. the StatCard counter) so the evidence sits
// "above the red text" without covering it. Bucket-1: a real screenshot/recording.
export const InsetVideo: React.FC<Props> = ({ src, top, height, left, right, label, fit }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = enter(frame, fps, { durationInFrames: 12 });
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          top,
          left,
          right,
          opacity: p,
          transform: `translateY(${interpolate(p, [0, 1], [-16, 0])}px)`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 12,
        }}
      >
        <div
          style={{
            width: "100%",
            height,
            borderRadius: 20,
            overflow: "hidden",
            border: `1px solid ${theme.color.border}`,
            boxShadow: "0 18px 50px rgba(0,0,0,0.6)",
            background: "#0d0e11",
          }}
        >
          <OffthreadVideo src={staticFile(src)} muted style={{ width: "100%", height: "100%", objectFit: fit }} />
        </div>
        {label ? (
          <span style={{ fontFamily: mono, fontSize: 24, letterSpacing: 2, color: theme.color.textSecondary }}>{label}</span>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
