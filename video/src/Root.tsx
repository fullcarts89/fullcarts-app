import React from "react";
import { Composition } from "remotion";
import { ShrinkOverlay, shrinkOverlaySchema } from "./compositions/ShrinkOverlay";
import { StatCard, statCardSchema } from "./compositions/StatCard";
import { RundownChip, rundownChipSchema } from "./compositions/RundownChip";
import { SourceFrame, sourceFrameSchema } from "./compositions/SourceFrame";

// 9:16 vertical, 30fps. Overlay comps have no background → render with alpha
// (--codec=prores --prores-profile=4444). StatCard is full-frame → --codec=h264.
const W = 1080;
const H = 1920;
const FPS = 30;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ShrinkOverlay"
        component={ShrinkOverlay}
        durationInFrames={150}
        fps={FPS}
        width={W}
        height={H}
        schema={shrinkOverlaySchema}
        defaultProps={{
          brand: "Gatorade",
          productName: "Gatorade Sports Drink",
          sizeBefore: 32,
          sizeAfter: 28,
          unit: "fl oz",
          pctChange: 12.5,
          source: "FullCarts · retailer listing",
          observedDate: "Observed 2022-06",
          mode: "shrink" as const,
        }}
      />

      <Composition
        id="StatCard"
        component={StatCard}
        durationInFrames={180}
        fps={FPS}
        width={W}
        height={H}
        schema={statCardSchema}
        defaultProps={{
          value: 2228,
          decimals: 0,
          prefix: "",
          suffix: "",
          label: "Documented shrinks",
          context: "size cuts logged in the FullCarts database — every one source-cited.",
          source: "FullCarts · fullcarts.org · as of 2026-06-10",
          accent: "red" as const,
        }}
      />

      <Composition
        id="RundownChip"
        component={RundownChip}
        durationInFrames={120}
        fps={FPS}
        width={W}
        height={H}
        schema={rundownChipSchema}
        defaultProps={{
          rank: 1,
          brand: "Cadbury",
          productName: "Freddo Faces Easter Egg",
          sizeBefore: 122,
          sizeAfter: 99,
          unit: "g",
          pctChange: 18.9,
          mode: "shrink" as const,
        }}
      />

      <Composition
        id="SourceFrame"
        component={SourceFrame}
        durationInFrames={150}
        fps={FPS}
        width={W}
        height={H}
        schema={sourceFrameSchema}
        defaultProps={{
          sourceName: "U.S. Bureau of Labor Statistics",
          url: "bls.gov/cpi",
          asOfDate: "as of 2026-06-10",
          headline: "Grocery CPI — official print",
        }}
      />
    </>
  );
};
