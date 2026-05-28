import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { colors } from "../../theme";
import { fonts } from "../../fonts";
import { GridPattern } from "../../components/GridPattern";
import { AnimatedCounter } from "../../components/AnimatedCounter";
import type { ShrinkEvent } from "../../data/types";

/**
 * Scene 4 (18-25s): The math + the corporate parent.
 * Price stays the same, price-per-unit ticks up.
 * Always name the parent company. Populist outrage licensed by the data.
 */
export const Receipt: React.FC<{ event: ShrinkEvent }> = ({ event }) => {
  const frame = useCurrentFrame();

  const headerFade = interpolate(frame, [0, 12], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const ppuFade = interpolate(frame, [10, 24], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const parentFade = interpolate(frame, [80, 100], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const sourcesFade = interpolate(frame, [130, 150], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  const ppuBefore = event.pricePerUnitBefore ?? 0;
  const ppuAfter = event.pricePerUnitAfter ?? 0;
  const ppuRise = ppuBefore > 0 ? ((ppuAfter - ppuBefore) / ppuBefore) * 100 : 0;

  return (
    <AbsoluteFill
      style={{
        background: colors.bg.primary,
        padding: 80,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        gap: 60,
      }}
    >
      <GridPattern opacity={0.05} />

      <div
        style={{
          fontFamily: fonts.mono,
          fontSize: 26,
          color: colors.text.secondary,
          letterSpacing: 4,
          textTransform: "uppercase",
          opacity: headerFade,
        }}
      >
        And here's what you pay
      </div>

      <div
        style={{
          background: colors.bg.secondary,
          border: `1px solid ${colors.border.subtle}`,
          borderRadius: 24,
          padding: 48,
          display: "flex",
          flexDirection: "column",
          gap: 28,
          opacity: ppuFade,
        }}
      >
        <Row
          label="Shelf price"
          before={fmtMoney(event.priceBefore)}
          after={fmtMoney(event.priceAfter)}
          afterColor={colors.text.primary}
        />
        <Divider />
        <Row
          label={`Price per ${event.sizeUnit}`}
          before={fmtMoney(ppuBefore, 4)}
          after={
            <AnimatedCounter
              from={ppuBefore}
              to={ppuAfter}
              durationInFrames={45}
              startFrame={10}
              format={(n) => fmtMoney(n, 4)}
              style={{
                fontFamily: fonts.mono,
                fontSize: 64,
                fontWeight: 700,
                color: colors.red.base,
              }}
            />
          }
          afterColor={colors.red.base}
        />
        <Divider />
        <div
          style={{
            fontFamily: fonts.headline,
            fontSize: 44,
            fontWeight: 700,
            color: colors.red.hover,
            textAlign: "center",
            marginTop: 8,
            letterSpacing: -1,
          }}
        >
          You pay {ppuRise > 0 ? "+" : ""}
          {ppuRise.toFixed(1)}% more per {event.sizeUnit}.
        </div>
      </div>

      {event.manufacturer ? (
        <div
          style={{
            textAlign: "center",
            opacity: parentFade,
          }}
        >
          <div
            style={{
              fontFamily: fonts.mono,
              fontSize: 22,
              color: colors.text.secondary,
              letterSpacing: 3,
              textTransform: "uppercase",
              marginBottom: 14,
            }}
          >
            Made by
          </div>
          <div
            style={{
              fontFamily: fonts.headline,
              fontSize: 56,
              fontWeight: 700,
              color: colors.text.primary,
              letterSpacing: -1,
            }}
          >
            {event.manufacturer}
          </div>
        </div>
      ) : null}

      <div
        style={{
          fontFamily: fonts.mono,
          fontSize: 22,
          color: colors.text.tertiary,
          textAlign: "center",
          opacity: sourcesFade,
        }}
      >
        Backed by {event.evidenceCount} independent sources →
      </div>
    </AbsoluteFill>
  );
};

const Row: React.FC<{
  label: string;
  before: React.ReactNode;
  after: React.ReactNode;
  afterColor: string;
}> = ({ label, before, after, afterColor }) => (
  <div
    style={{
      display: "grid",
      gridTemplateColumns: "1fr auto auto auto",
      alignItems: "center",
      gap: 32,
    }}
  >
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
    <span
      style={{
        fontFamily: fonts.mono,
        fontSize: 48,
        fontWeight: 500,
        color: colors.text.secondary,
      }}
    >
      {before}
    </span>
    <span
      style={{
        fontFamily: fonts.mono,
        fontSize: 36,
        color: colors.text.tertiary,
      }}
    >
      →
    </span>
    <span
      style={{
        fontFamily: fonts.mono,
        fontSize: 64,
        fontWeight: 700,
        color: afterColor,
        minWidth: 220,
        textAlign: "right",
      }}
    >
      {after}
    </span>
  </div>
);

const Divider: React.FC = () => (
  <div style={{ height: 1, background: colors.border.subtle }} />
);

function fmtMoney(n: number | null, digits: number = 2): string {
  if (n == null) return "—";
  return `$${n.toFixed(digits)}`;
}
