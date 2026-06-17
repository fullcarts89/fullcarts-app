import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../lib/theme";
import { mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

// "They hide it in the corner." Full-frame background for the HOOK + TACTIC beats:
// the real net-weight crop, pushed in (Ken Burns toward the number) with an animated
// red ring drawn around the figure. Built as a GREEN-SCREEN BACKGROUND — evidence
// lives in the upper 2/3, the lower third is left clear for the composited talking
// head + the captions the creator adds last. No captions, no SFX baked in.
export const netWeightZoomSchema = z.object({
  src: z.string(),
  mode: z.enum(["hook", "tactic"]).default("hook"),
  eyebrow: z.string().default("THE CORNER THEY HOPE YOU MISS"),
  // ring center + radii as a fraction of the IMAGE box (tuned after a QC frame)
  ringCx: z.number().default(0.52),
  ringCy: z.number().default(0.88),
  ringRx: z.number().default(0.09),
  ringRy: z.number().default(0.22),
});

type Props = z.infer<typeof netWeightZoomSchema>;

// fixed image box (wide net-weight strip, ~6.25:1) seated in the upper frame
const BOX = { left: 40, top: 500, width: 1000, height: 160 };

export const NetWeightZoom: React.FC<Props> = ({ src, mode, eyebrow, ringCx, ringCy, ringRx, ringRy }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ring geometry in image-box coordinates
  const cx = ringCx * BOX.width;
  const cy = ringCy * BOX.height;
  const rx = ringRx * BOX.width;
  const ry = ringRy * BOX.height;

  // push in toward the ring; tactic adds a slow 2x pulse ("taps")
  const base = interpolate(frame, [0, fps * 3.2], [1.04, 1.2], { extrapolateRight: "clamp" });
  const pulse = mode === "tactic" ? 1 + 0.05 * Math.max(0, Math.sin((frame / fps) * Math.PI * 1.5)) : 1;
  const scale = base * pulse;

  // ring draw-in + steady glow pulse
  const ringP = enter(frame, fps, { delay: mode === "hook" ? 5 : 9, durationInFrames: 16 });
  const circ = Math.PI * (3 * (rx + ry) - Math.sqrt((3 * rx + ry) * (rx + 3 * ry)));
  const glow = 0.5 + 0.5 * Math.sin((frame / fps) * Math.PI * 2);
  const eyebrowP = enter(frame, fps, { delay: 2, durationInFrames: 14 });

  return (
    <AbsoluteFill style={{ background: theme.color.bg }}>
      <GridTexture opacity={0.06} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 30%, ${theme.color.red}14 0%, transparent 55%)` }} />

      <div style={{ position: "absolute", top: 300, left: BOX.left, right: 60, opacity: eyebrowP, transform: `translateY(${interpolate(eyebrowP, [0, 1], [-12, 0])}px)` }}>
        <span style={{ fontFamily: mono, fontSize: 30, letterSpacing: 6, textTransform: "uppercase", color: theme.color.red }}>{eyebrow}</span>
      </div>

      {/* image + ring share one transform so the ring stays locked to the number while it zooms */}
      <div
        style={{
          position: "absolute",
          left: BOX.left,
          top: BOX.top,
          width: BOX.width,
          height: BOX.height,
          transform: `scale(${scale})`,
          transformOrigin: `${cx}px ${cy}px`,
        }}
      >
        <Img
          src={staticFile(src)}
          style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: 16, border: `1px solid ${theme.color.border}`, boxShadow: "0 18px 50px rgba(0,0,0,0.55)" }}
        />
        <svg width={BOX.width} height={BOX.height} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
          <ellipse
            cx={cx}
            cy={cy}
            rx={rx}
            ry={ry}
            fill="none"
            stroke={theme.color.red}
            strokeWidth={11}
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={circ * (1 - ringP)}
            style={{ filter: `drop-shadow(0 0 ${6 + glow * 12}px ${theme.color.red})` }}
            transform={`rotate(-4 ${cx} ${cy})`}
          />
        </svg>
      </div>

      <div style={{ position: "absolute", top: 250, left: 60 }}>
        <Brandmark scale={1.1} />
      </div>
    </AbsoluteFill>
  );
};
