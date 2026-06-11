import React from "react";
import { z } from "zod";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono } from "../lib/fonts";
import { enter } from "../lib/anim";

export const caughtTitleSchema = z.object({
  brand: z.string(),
});

type Props = z.infer<typeof caughtTitleSchema>;

// The "Caught:" series cold-open. Transparent → render with alpha and overlay the
// top of the face-hook shot. "CAUGHT:" cream + [BRAND] in alert red, with a red
// accent bar that wipes in. The recognizable open that makes the backlog a series.
export const CaughtTitle: React.FC<Props> = ({ brand }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slam = enter(frame, fps, { durationInFrames: 14 });
  const brandIn = enter(frame, fps, { delay: 6, durationInFrames: 16 });
  const barW = interpolate(enter(frame, fps, { delay: 14, durationInFrames: 18 }), [0, 1], [0, 100], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top: 150, left: 64, right: 64 }}>
        <div
          style={{
            fontFamily: mono,
            fontSize: 30,
            letterSpacing: 8,
            textTransform: "uppercase",
            color: theme.color.red,
            opacity: slam,
            transform: `translateX(${interpolate(slam, [0, 1], [-40, 0])}px)`,
          }}
        >
          Caught
        </div>
        <div
          style={{
            fontFamily: headline,
            fontWeight: 700,
            fontSize: 96,
            lineHeight: 1.0,
            letterSpacing: -1,
            color: theme.color.textPrimary,
            opacity: brandIn,
            transform: `scale(${interpolate(brandIn, [0, 1], [0.85, 1])})`,
            transformOrigin: "left center",
            marginTop: 6,
          }}
        >
          {brand}
        </div>
        <div
          style={{
            height: 10,
            width: `${barW}%`,
            maxWidth: 360,
            background: theme.color.red,
            borderRadius: 5,
            marginTop: 18,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
