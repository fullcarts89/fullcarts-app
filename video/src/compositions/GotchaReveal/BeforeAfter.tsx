import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { colors } from "../../theme";
import { fonts } from "../../fonts";
import { GridPattern } from "../../components/GridPattern";
import { ShrinkBar } from "../../components/ShrinkBar";
import type { ShrinkEvent } from "../../data/types";

/**
 * Scene 3 (10-18s): The reveal moment — before/after sizes shown to scale.
 * The visual proof. Both bars use the same pixel-per-unit so the
 * shrink is honest — not exaggerated for emphasis.
 */
export const BeforeAfter: React.FC<{ event: ShrinkEvent }> = ({ event }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fullWidth = 780;
  const beforeRatio = 1;
  const afterRatio = event.sizeAfter / event.sizeBefore;

  const badgeSpring = spring({
    frame: frame - 90,
    fps,
    config: { damping: 9, mass: 0.5, stiffness: 200 },
  });
  const badgeScale = interpolate(badgeSpring, [0, 1], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        background: colors.bg.primary,
        padding: "120px 80px",
      }}
    >
      <GridPattern opacity={0.06} />

      <div
        style={{
          fontFamily: fonts.mono,
          fontSize: 26,
          color: colors.text.secondary,
          letterSpacing: 4,
          textTransform: "uppercase",
          textAlign: "center",
          marginBottom: 80,
        }}
      >
        Same product. Smaller box.
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 90,
          alignItems: "flex-start",
        }}
      >
        <ShrinkBar
          label={`Before · ${formatDate(event.observedDateBefore)}`}
          value={event.sizeBefore}
          unit={event.sizeUnit}
          fullWidthPx={fullWidth}
          fillRatio={beforeRatio}
          color={colors.text.primary}
          startFrame={0}
        />
        <ShrinkBar
          label={`After · ${formatDate(event.observedDateAfter)}`}
          value={event.sizeAfter}
          unit={event.sizeUnit}
          fullWidthPx={fullWidth}
          fillRatio={afterRatio}
          color={colors.red.base}
          startFrame={45}
        />
      </div>

      <div
        style={{
          position: "absolute",
          right: 80,
          top: "50%",
          transform: `translateY(-50%) scale(${badgeScale}) rotate(-6deg)`,
        }}
      >
        <div
          style={{
            background: colors.red.base,
            color: colors.text.primary,
            fontFamily: fonts.mono,
            fontSize: 140,
            fontWeight: 700,
            padding: "32px 56px",
            borderRadius: 28,
            boxShadow: `0 0 80px ${colors.red.base}88`,
            letterSpacing: -3,
          }}
        >
          {event.sizeDeltaPct}%
        </div>
      </div>
    </AbsoluteFill>
  );
};

function formatDate(iso: string): string {
  const d = new Date(iso);
  const month = d.toLocaleString("en-US", { month: "short" });
  return `${month} ${d.getFullYear()}`;
}
