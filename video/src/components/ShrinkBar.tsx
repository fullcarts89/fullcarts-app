import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { colors } from "../theme";
import { fonts } from "../fonts";

interface Props {
  label: string;
  value: number;
  unit: string;
  fullWidthPx: number;
  fillRatio: number;
  color: string;
  startFrame: number;
}

/**
 * Horizontal bar that grows to its target width, with the size label
 * sliding in beside it. Used for the before/after size comparison.
 *
 * fillRatio is the bar's final width relative to fullWidthPx (so the
 * 80g bar can render full-width and the 72g bar renders at 0.9).
 */
export const ShrinkBar: React.FC<Props> = ({
  label,
  value,
  unit,
  fullWidthPx,
  fillRatio,
  color,
  startFrame,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const grow = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 18, mass: 0.8 },
  });
  const barWidth = fullWidthPx * fillRatio * grow;

  const labelOpacity = interpolate(
    frame - startFrame,
    [10, 22],
    [0, 1],
    { extrapolateRight: "clamp", extrapolateLeft: "clamp" },
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <span
        style={{
          fontFamily: fonts.mono,
          fontSize: 24,
          color: colors.text.secondary,
          letterSpacing: 2,
          textTransform: "uppercase",
        }}
      >
        {label}
      </span>
      <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
        <div
          style={{
            height: 110,
            width: barWidth,
            background: color,
            borderRadius: 10,
            boxShadow: `0 0 60px ${color}33`,
          }}
        />
        <span
          style={{
            fontFamily: fonts.mono,
            fontSize: 64,
            fontWeight: 700,
            color,
            opacity: labelOpacity,
            whiteSpace: "nowrap",
          }}
        >
          {value}
          {unit}
        </span>
      </div>
    </div>
  );
};
