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
import { HookText, hookTextSchema } from "./compositions/HookText";
import { RocketsFeathers, rocketsFeathersSchema } from "./compositions/RocketsFeathers";
import { PriceJump, priceJumpSchema } from "./compositions/PriceJump";
import { FewerCups, fewerCupsSchema } from "./compositions/FewerCups";
import { OutroCard, outroCardSchema } from "./compositions/OutroCard";
import { Carousel, carouselSchema } from "./compositions/Carousel";
import { TierList, tierListSchema } from "./compositions/TierList";
import { CarouselVideo, carouselVideoSchema, calcCarouselVideoMeta } from "./compositions/CarouselVideo";
import folgersCut from "./props/folgers-final.json";
import folgersCutV5 from "./props/folgers-final-v5.json";
import coffee5 from "./props/coffee-5.json";

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

      {/* The current Folgers cut — click to watch the whole thing in Studio */}
      <Composition
        id="FolgersCut"
        component={FinalVideo}
        durationInFrames={1766}
        fps={FPS}
        width={W}
        height={H}
        calculateMetadata={calcFinalMeta}
        defaultProps={folgersCut as unknown as FinalVideoProps}
      />

      {/* v5 — climax hooks replaced with motion graphics (PriceJump + RocketsFeathers)
          and a branded OutroCard close. Face stays on screen for both graphics. */}
      <Composition
        id="FolgersCutV5"
        component={FinalVideo}
        durationInFrames={1766}
        fps={FPS}
        width={W}
        height={H}
        calculateMetadata={calcFinalMeta}
        defaultProps={folgersCutV5 as unknown as FinalVideoProps}
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
        id="HookText"
        component={HookText}
        durationInFrames={60}
        fps={FPS}
        width={W}
        height={H}
        schema={hookTextSchema}
        defaultProps={{ lines: ["they *shrank* your coffee", "and hoped you wouldn't *weigh it*"], zone: "above" as const, accent: "red" as const }}
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

      {/* Motion-graphics panels for the negative space around the talking head.
          Transparent overlays — preview standalone here, use via FinalVideo cues. */}
      <Composition
        id="RocketsFeathers"
        component={RocketsFeathers}
        durationInFrames={150}
        fps={FPS}
        width={W}
        height={H}
        schema={rocketsFeathersSchema}
        defaultProps={{
          title: "ROCKETS & FEATHERS",
          payLabel: "WHAT YOU PAY",
          getLabel: "WHAT YOU GET",
          note: "up *fast* · down *slow* · *or never*",
          zone: "above" as const,
        }}
      />

      <Composition
        id="PriceJump"
        component={PriceJump}
        durationInFrames={150}
        fps={FPS}
        width={W}
        height={H}
        schema={priceJumpSchema}
        defaultProps={{
          // approved per-oz figures (years apart — one listing archived); see approved-claims.md
          label: "PRICE PER OZ — FOLGERS BIG CAN",
          before: 22,
          after: 59.5,
          prefix: "",
          suffix: "¢",
          decimals: 1,
          context: "the shelf price *barely moved.* the can did.",
          zone: "above" as const,
        }}
      />

      <Composition
        id="FewerCups"
        component={FewerCups}
        durationInFrames={150}
        fps={FPS}
        width={W}
        height={H}
        schema={fewerCupsSchema}
        defaultProps={{
          // 51 → 43.5 oz is the verified hard fact; cups-per-can needs a real label first
          before: 51,
          after: 43.5,
          unitLabel: "oz of coffee",
          perIcon: 5,
          decimals: 1,
          subline: "same red can. same shelf.",
          zone: "above" as const,
        }}
      />

      <Composition
        id="OutroCard"
        component={OutroCard}
        durationInFrames={180}
        fps={FPS}
        width={W}
        height={H}
        schema={outroCardSchema}
        defaultProps={{
          tagline: "Every claim.\n*Source-cited.*",
          followLine: "follow — I catch the next one",
          url: "fullcarts.org",
          statLine: "2,200+ documented shrinks · every one source-cited",
        }}
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

      {/* Data-driven IG/TikTok carousel (4:5). One slide per frame: render stills 0..N+1. */}
      <Composition
        id="Carousel"
        component={Carousel}
        durationInFrames={7}
        fps={FPS}
        width={1080}
        height={1350}
        schema={carouselSchema}
        defaultProps={{
          coverTitle: ["5 stealth", "*shrinks*"],
          coverSub: "same price. less product. all documented.",
          items: [
            { rank: "5", brand: "Gatorade", product: "Gatorade Sports Drink", before: 32, after: 28, unit: "fl oz", pct: 12.5 },
            { rank: "4", brand: "Folgers", product: "Folgers Coffee (big can)", before: 51, after: 43.5, unit: "oz", pct: 14.7 },
            { rank: "3", brand: "Chobani", product: "Chobani Flips", before: 5.3, after: 4.5, unit: "oz", pct: 15.1 },
            { rank: "2", brand: "Cadbury", product: "Freddo Faces Egg", before: 122, after: 99, unit: "g", pct: 18.9 },
            { rank: "1", brand: "Aquafresh", product: "Aquafresh Toothpaste", before: 100, after: 75, unit: "ml", pct: 25.0 },
          ],
          ctaHeadline: "spot one you *buy?*",
          ctaSub: "search any product — *free* — at fullcarts.org",
          ctaPersona: "Built by a tired dad who got sick of getting ripped off: the largest free, public shrinkflation database I know of.",
        }}
      />

      {/* Shrinkflation Tier List — reveal carousel: cover → D…S (one per swipe) → full list last. */}
      <Composition
        id="TierList"
        component={TierList}
        durationInFrames={7}
        fps={FPS}
        width={1080}
        height={1350}
        schema={tierListSchema}
        defaultProps={{
          title: ["shrinkflation", "*tier list*"],
          subtitle: "where does your brand rank?",
          coverPrompt: "we start at the bottom. swipe",
          tiers: [
            { tier: "S", color: "red" as const, label: "the worst offenders", brands: [{ name: "Cadbury", pct: 44 }, { name: "Mars", pct: 44 }, { name: "Quality St.", pct: 40 }] },
            { tier: "A", color: "amber" as const, label: "brutal", brands: [{ name: "Nestlé", pct: 38 }, { name: "McVitie's", pct: 34 }, { name: "Sainsbury's", pct: 33 }, { name: "Hershey", pct: 32 }] },
            { tier: "B", color: "blue" as const, label: "getting greedy", brands: [{ name: "Crest", pct: 27 }, { name: "Aquafresh", pct: 25 }, { name: "Kleenex", pct: 25 }] },
            { tier: "C", color: "green" as const, label: "noticeable", brands: [{ name: "Chobani", pct: 24 }, { name: "Walkers", pct: 23 }, { name: "Folgers", pct: 21 }] },
            { tier: "D", color: "gray" as const, label: "barely caught", brands: [{ name: "Gatorade", pct: 16 }] },
          ],
          ctaLine: "agree? comment your worst ↓",
        }}
      />

      {/* Data carousel as a VIDEO (auto-advancing) — posts as a Reel/Short. Same component
          renders both ratios; duration adapts to item count via calcCarouselVideoMeta.
          Default = "5 Stealth Coffee Shrinks" (live DB data). Bars/monograms render offline;
          product photos appear when rendered on a network-open machine (coffee-5-photos.json). */}
      <Composition
        id="CarouselVideo"
        component={CarouselVideo}
        durationInFrames={585}
        fps={FPS}
        width={1080}
        height={1350}
        schema={carouselVideoSchema}
        calculateMetadata={calcCarouselVideoMeta}
        defaultProps={coffee5 as unknown as React.ComponentProps<typeof CarouselVideo>}
      />

      <Composition
        id="CarouselVideoVertical"
        component={CarouselVideo}
        durationInFrames={585}
        fps={FPS}
        width={1080}
        height={1920}
        schema={carouselVideoSchema}
        calculateMetadata={calcCarouselVideoMeta}
        defaultProps={coffee5 as unknown as React.ComponentProps<typeof CarouselVideo>}
      />
    </>
  );
};
