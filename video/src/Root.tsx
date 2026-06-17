import React from "react";
import { Composition } from "remotion";
import { ShrinkOverlay, shrinkOverlaySchema } from "./compositions/ShrinkOverlay";
import { StatCard, statCardSchema } from "./compositions/StatCard";
import { RundownChip, rundownChipSchema, calcRundownChipMeta } from "./compositions/RundownChip";
import { ShrinkCutaway, shrinkCutawaySchema } from "./compositions/ShrinkCutaway";
import { SourceFrame, sourceFrameSchema } from "./compositions/SourceFrame";
import { CaughtTitle, caughtTitleSchema } from "./compositions/CaughtTitle";
import { Thumbnail, thumbnailSchema } from "./compositions/Thumbnail";
import { CoverCard, coverCardSchema } from "./compositions/CoverCard";
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
import { GuessTheCut, guessTheCutSchema } from "./compositions/GuessTheCut";
import { ItsNotYou, itsNotYouSchema } from "./compositions/ItsNotYou";
import { CPIvsReality, cpiVsRealitySchema } from "./compositions/CPIvsReality";
import { CaughtBeforeAfter, caughtBeforeAfterSchema } from "./compositions/CaughtBeforeAfter";
import { ShrinkVsInflationChart, shrinkVsInflationSchema } from "./compositions/ShrinkVsInflationChart";
import { CompoundChart, compoundChartSchema } from "./compositions/CompoundChart";
import { CpiMechanic, cpiMechanicSchema } from "./compositions/CpiMechanic";
import { BudgetShareBars, budgetShareSchema } from "./compositions/BudgetShareBars";
import { PriceCeiling, priceCeilingSchema } from "./compositions/PriceCeiling";
import { SpotTheSkimp, spotTheSkimpSchema, calcSpotMeta } from "./compositions/SpotTheSkimp";
import { SpotThumbnail, spotThumbnailSchema } from "./compositions/SpotThumbnail";
import spotSkimp from "./props/spot-skimp.json";
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
        calculateMetadata={calcRundownChipMeta}
        defaultProps={{
          rank: 1,
          brand: "Cadbury",
          productName: "Freddo Faces Easter Egg",
          sizeBefore: 122,
          sizeAfter: 99,
          unit: "g",
          pctChange: 18.9,
          mode: "shrink" as const,
          showBrand: true,
        }}
      />

      <Composition
        id="ShrinkCutaway"
        component={ShrinkCutaway}
        durationInFrames={150}
        fps={FPS}
        width={W}
        height={H}
        schema={shrinkCutawaySchema}
        defaultProps={{
          brand: "Lay's",
          productName: "Classic",
          sizeBefore: 235,
          sizeAfter: 145,
          unit: "g",
          pctChange: 38.3,
          mode: "shrink" as const,
          shots: [{ src: "cutaways/lays.jpg" }],
          guide: false,
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

      <Composition
        id="CoverCard"
        component={CoverCard}
        durationInFrames={30}
        fps={FPS}
        width={W}
        height={H}
        schema={coverCardSchema}
        defaultProps={{
          faceSrc: "img/cover-face.png",
          eyebrow: "SHRINKFLATION · CAUGHT",
          headline: ["“NEW & IMPROVED”", "IS A *LIE*"],
          sub: "3 cleaning shrinks. one company.",
          url: "fullcarts.org",
          focusY: 22,
          zoom: 1.14,
          cardTop: 1200,
        }}
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

      {/* Guess the Cut — gamified quiz: cover → Q/A pairs → CTA. Render stills 0..items*2+1. */}
      <Composition
        id="GuessTheCut"
        component={GuessTheCut}
        durationInFrames={12}
        fps={FPS}
        width={1080}
        height={1350}
        schema={guessTheCutSchema}
        defaultProps={{
          coverTitle: ["guess", "the *cut*"],
          coverSub: "same price, less inside. most people lowball every one. swipe →",
          items: [
            { rank: "5", brand: "Gatorade", product: "Gatorade Sports Drink", before: 32, after: 28, unit: "fl oz", pct: 12.5, equiv: "half a cup, gone" },
            { rank: "4", brand: "Gaviscon", product: "Gaviscon Double Action", before: 600, after: 500, unit: "ml", pct: 16.7, equiv: "a sixth of the bottle, gone" },
            { rank: "3", brand: "Cadbury", product: "Freddo Faces Egg", before: 122, after: 99, unit: "g", pct: 18.9, equiv: "nearly a fifth of the egg" },
            { rank: "2", brand: "Aquafresh", product: "Aquafresh Toothpaste", before: 100, after: 75, unit: "ml", pct: 25.0, equiv: "1 in every 4 tubes, vanished" },
            { rank: "1", brand: "Sainsbury's", product: "Scottish Oats", before: 1000, after: 500, unit: "g", pct: 50.0, equiv: "half. the. bag." },
          ],
          ctaHeadline: "you lowballed it, *didn't you?*",
          ctaSub: "search any product — *free* — at fullcarts.org",
          ctaPersona: "Tired dad, sick of getting ripped off — so I built the receipts. 2,200+ documented cuts, no ads.",
        }}
      />

      {/* It's Not You — emotional cold open → receipts → resolution. Stills 0..receipts+3. */}
      <Composition
        id="ItsNotYou"
        component={ItsNotYou}
        durationInFrames={7}
        fps={FPS}
        width={1080}
        height={1350}
        schema={itsNotYouSchema}
        defaultProps={{
          opener: ["You're not crazy.", "That box really did", "get *smaller*."],
          feeling: "I swear this used to be bigger… then I felt silly for even noticing.",
          receipts: [
            { brand: "Cadbury", product: "Freddo Faces Egg", before: 122, after: 99, unit: "g", pct: 18.9 },
            { brand: "Aquafresh", product: "Aquafresh Toothpaste", before: 100, after: 75, unit: "ml", pct: 25.0 },
            { brand: "Sainsbury's", product: "Scottish Oats", before: 1000, after: 500, unit: "g", pct: 50.0 },
          ],
          resolution: ["It's not you.", "You're being quietly", "robbed — *by design*."],
          ctaPersona: "Tired dad, sick of getting ripped off — so I built the receipts. 2,200+ documented cuts, no ads.",
        }}
      />

      {/* CPI vs. Reality — macro newsjack (CPI day). STUB. Stills 0..items+1. */}
      <Composition
        id="CPIvsReality"
        component={CPIvsReality}
        durationInFrames={5}
        fps={FPS}
        width={1080}
        height={1350}
        schema={cpiVsRealitySchema}
        defaultProps={{
          cpiHeadline: "Groceries: +2.1% this year",
          cpiSource: "BLS CPI · Food at Home · YoY",
          items: [
            { category: "Candy", cpiPct: 2.1, brand: "Cadbury", product: "Freddo Faces Egg", shelfPct: 18.9 },
            { category: "Personal care", cpiPct: 2.1, brand: "Aquafresh", product: "Toothpaste", shelfPct: 25.0 },
            { category: "Cereal", cpiPct: 2.1, brand: "Sainsbury's", product: "Scottish Oats", shelfPct: 50.0 },
          ],
          ctaHeadline: "Inflation counts the price.",
          ctaSub: "It barely counts the box. We do — fullcarts.org",
        }}
      />

      {/* Caught Before/After — single-product deep dive (video companion). STUB. Stills 0..4. */}
      <Composition
        id="CaughtBeforeAfter"
        component={CaughtBeforeAfter}
        durationInFrames={5}
        fps={FPS}
        width={1080}
        height={1350}
        schema={caughtBeforeAfterSchema}
        defaultProps={{
          brand: "Cadbury",
          product: "Freddo Faces Easter Egg",
          before: 122,
          after: 99,
          unit: "g",
          pct: 18.9,
          sourceLabel: "Reddit + retailer listing, observed 2023 — 72 pieces of evidence",
        }}
      />

      {/* ── CPI Take (The Take, newsjack) — animated data assets ──────────────
          Full-frame opaque → render h264 (.mp4). Each has a `startDelay` (frames)
          to nudge the reveal onto the VO/SRT, and a `sweepFrames` where the data
          climbs so the count-up lands on the spoken number. */}

      {/* ── Spot the Skimp (Easy → Impossible) — full-frame BACKGROUND b-roll.
          Creator embeds their own talking head + captions on top; bottom ~1/3
          is left clean. Panels are SRT-timed; reveals are observational (no
          fabricated measurements). Duration adapts to durationSec via props. */}
      <Composition
        id="SpotTheSkimp"
        component={SpotTheSkimp}
        durationInFrames={2367}
        fps={FPS}
        width={W}
        height={H}
        schema={spotTheSkimpSchema}
        calculateMetadata={calcSpotMeta}
        defaultProps={spotSkimp as unknown as React.ComponentProps<typeof SpotTheSkimp>}
      />

      {/* Spot the Skimp — self-contained cover (render as a still PNG) */}
      <Composition
        id="SpotThumbnail"
        component={SpotThumbnail}
        durationInFrames={30}
        fps={FPS}
        width={W}
        height={H}
        schema={spotThumbnailSchema}
        defaultProps={{
          titleLines: ["Spot", "the Skimp"],
          sub: "Easy → Impossible",
          hook: "Can you spot all *6?*",
          images: [
            "spotskimp/natures.jpg",
            "spotskimp/mars.jpg",
            "spotskimp/charmin.jpg",
            "spotskimp/listerine.jpg",
            "spotskimp/fries.jpg",
            "spotskimp/cheezit.jpg",
          ],
        }}
      />

      {/* ① HOOK — the precedent: BLS downsizings vs food inflation, 2022 flagged */}
      <Composition
        id="ShrinkVsInflationChart"
        component={ShrinkVsInflationChart}
        durationInFrames={180}
        fps={FPS}
        width={W}
        height={H}
        schema={shrinkVsInflationSchema}
        defaultProps={shrinkVsInflationSchema.parse({})}
      />

      {/* ② RECEIPT — why CPI misses it: same price, smaller box, +%/oz */}
      <Composition
        id="CpiMechanic"
        component={CpiMechanic}
        durationInFrames={240}
        fps={FPS}
        width={W}
        height={H}
        schema={cpiMechanicSchema}
        defaultProps={cpiMechanicSchema.parse({})}
      />

      {/* ③ COMPOUND — family-of-4 grocery bill compounded @4.2% + comment bait */}
      <Composition
        id="CompoundChart"
        component={CompoundChart}
        durationInFrames={540}
        fps={FPS}
        width={W}
        height={H}
        schema={compoundChartSchema}
        defaultProps={compoundChartSchema.parse({})}
      />

      {/* ④ WHO IT HITS — food as a share of income, bottom vs top (regressive) */}
      <Composition
        id="BudgetShareBars"
        component={BudgetShareBars}
        durationInFrames={200}
        fps={FPS}
        width={W}
        height={H}
        schema={budgetShareSchema}
        defaultProps={budgetShareSchema.parse({})}
      />

      {/* ⑤ TAKE — price climbs to a ceiling it won't cross, deflects to a shrink */}
      <Composition
        id="PriceCeiling"
        component={PriceCeiling}
        durationInFrames={190}
        fps={FPS}
        width={W}
        height={H}
        schema={priceCeilingSchema}
        defaultProps={priceCeilingSchema.parse({})}
      />
    </>
  );
};
