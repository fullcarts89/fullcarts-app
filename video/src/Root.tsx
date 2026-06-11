import React from "react";
import { Composition } from "remotion";
import { ShrinkOverlay, shrinkOverlaySchema } from "./compositions/ShrinkOverlay";
import { StatCard, statCardSchema } from "./compositions/StatCard";
import { RundownChip, rundownChipSchema } from "./compositions/RundownChip";
import { SourceFrame, sourceFrameSchema } from "./compositions/SourceFrame";
import { CaughtTitle, caughtTitleSchema } from "./compositions/CaughtTitle";
import { Thumbnail, thumbnailSchema } from "./compositions/Thumbnail";
import { SafeZonePreview, safeZonePreviewSchema } from "./compositions/SafeZonePreview";
import { FinalVideo, calcFinalMeta, type FinalVideoProps } from "./compositions/FinalVideo";
import { BeforeAfter, beforeAfterSchema } from "./compositions/BeforeAfter";
import { KineticQuote, kineticQuoteSchema } from "./compositions/KineticQuote";
import { ShrinkReveal, shrinkRevealSchema } from "./compositions/ShrinkReveal";

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

      <Composition
        id="CaughtTitle"
        component={CaughtTitle}
        durationInFrames={60}
        fps={FPS}
        width={W}
        height={H}
        schema={caughtTitleSchema}
        defaultProps={{ brand: "Folgers" }}
      />

      <Composition
        id="Thumbnail"
        component={Thumbnail}
        durationInFrames={30}
        fps={FPS}
        width={W}
        height={H}
        schema={thumbnailSchema}
        defaultProps={{ brand: "Folgers", pctChange: 14.7, mode: "shrink" as const }}
      />

      {/* Preview only — overlay + mock platform UI to verify safe zones. Not for export. */}
      <Composition
        id="SafeZonePreview"
        component={SafeZonePreview}
        durationInFrames={60}
        fps={FPS}
        width={W}
        height={H}
        schema={safeZonePreviewSchema}
        defaultProps={{ which: "shrink" as const, guide: true }}
      />

      {/* Model B — full programmatic assembly: your film + a timeline → one finished MP4 */}
      <Composition
        id="FinalVideo"
        component={FinalVideo}
        durationInFrames={1710}
        fps={FPS}
        width={W}
        height={H}
        calculateMetadata={calcFinalMeta}
        defaultProps={
          { fps: 30, durationSec: 57, captions: [], overlays: [] } satisfies FinalVideoProps
        }
      />

      <Composition
        id="BeforeAfter"
        component={BeforeAfter}
        durationInFrames={30}
        fps={FPS}
        width={W}
        height={H}
        schema={beforeAfterSchema}
        defaultProps={{
          beforeSrc: "cutaways/folgers-before.jpg",
          afterSrc: "cutaways/folgers-after.jpg",
          beforeTag: "BEFORE",
          afterTag: "AFTER",
          beforeSize: "51 oz",
          beforePer: "$0.22 / oz",
          afterSize: "43.5 oz",
          afterPer: "59.5¢ / oz",
          deltaLabel: "−14.7% coffee",
        }}
      />

      <Composition
        id="KineticQuote"
        component={KineticQuote}
        durationInFrames={90}
        fps={FPS}
        width={W}
        height={H}
        schema={kineticQuoteSchema}
        defaultProps={{ lines: ["it's *not* you.", "you're being *robbed* —", "by design."], accent: "red" as const, align: "center" as const }}
      />

      <Composition
        id="ShrinkReveal"
        component={ShrinkReveal}
        durationInFrames={90}
        fps={FPS}
        width={W}
        height={H}
        schema={shrinkRevealSchema}
        defaultProps={{
          imageSrc: "cutaways/folgers-before.jpg",
          imagePosition: "left center",
          beforeSize: 51,
          afterSize: 43.5,
          unit: "oz",
          pctChange: 14.7,
        }}
      />
    </>
  );
};
