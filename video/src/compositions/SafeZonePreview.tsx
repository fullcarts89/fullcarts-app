import React from "react";
import { z } from "zod";
import { AbsoluteFill } from "remotion";
import { theme } from "../lib/theme";
import { mono } from "../lib/fonts";
import { SafeZoneGuide } from "../components/SafeZoneGuide";
import { ShrinkOverlay } from "./ShrinkOverlay";
import { StatCard } from "./StatCard";
import { RundownChip } from "./RundownChip";
import { SourceFrame } from "./SourceFrame";
import { CaughtTitle } from "./CaughtTitle";

export const safeZonePreviewSchema = z.object({
  which: z.enum(["shrink", "stat", "rundown", "source", "caught"]),
  guide: z.boolean().default(true),
});

type Props = z.infer<typeof safeZonePreviewSchema>;

// PREVIEW ONLY — composites a mock "footage" background + one overlay + the
// platform-UI safe-zone guide, so we can confirm overlays clear the TikTok/Reels/
// Shorts UI. Not used in production exports.
const MockFootage: React.FC = () => (
  <AbsoluteFill
    style={{
      background: "radial-gradient(70% 50% at 50% 38%, #2c2f36 0%, #121317 60%, #0b0c0f 100%)",
      alignItems: "center",
      justifyContent: "center",
    }}
  >
    <span style={{ fontFamily: mono, fontSize: 26, letterSpacing: 2, color: "#4d4f56" }}>▲ your footage</span>
  </AbsoluteFill>
);

const Overlay: React.FC<{ which: Props["which"] }> = ({ which }) => {
  switch (which) {
    case "shrink":
      return (
        <ShrinkOverlay brand="Gatorade" productName="Gatorade Sports Drink" sizeBefore={32} sizeAfter={28}
          unit="fl oz" pctChange={12.5} source="FullCarts · listing" observedDate="2022-06" mode="shrink" />
      );
    case "stat":
      return (
        <StatCard value={2228} decimals={0} prefix="" suffix="" label="Documented shrinks"
          context="size cuts logged — every one source-cited." source="FullCarts · fullcarts.org" accent="red" />
      );
    case "rundown":
      return (
        <RundownChip rank={1} brand="Cadbury" productName="Freddo Faces" sizeBefore={122} sizeAfter={99}
          unit="g" pctChange={18.9} mode="shrink" />
      );
    case "source":
      return <SourceFrame sourceName="ICE Arabica (KC)" url="tradingeconomics.com" asOfDate="Jun 2026" headline="Coffee: −39% from peak" />;
    case "caught":
      return <CaughtTitle brand="Folgers" />;
  }
};

export const SafeZonePreview: React.FC<Props> = ({ which, guide }) => (
  <AbsoluteFill style={{ background: theme.color.bg }}>
    {which !== "stat" && <MockFootage />}
    <Overlay which={which} />
    {guide && <SafeZoneGuide />}
  </AbsoluteFill>
);
