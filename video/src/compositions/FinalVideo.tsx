import React from "react";
import {
  AbsoluteFill,
  Sequence,
  OffthreadVideo,
  Img,
  Audio,
  staticFile,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../lib/theme";
import { headline, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { CAPTION } from "../lib/safezone";
import { ShrinkOverlay } from "./ShrinkOverlay";
import { StatCard } from "./StatCard";
import { RundownChip } from "./RundownChip";
import { SourceFrame } from "./SourceFrame";
import { CaughtTitle } from "./CaughtTitle";

// ---- Timeline types (Model B: feed your film + this timeline → one finished MP4) ----
type OverlayCue = { type: "caught" | "shrink" | "stat" | "rundown" | "source"; fromSec: number; toSec: number; props: Record<string, unknown> };
type CaptionCue = { text: string; fromSec: number; toSec: number }; // wrap a word in *asterisks* to red-highlight it
type CutawayCue = { src: string; kind: "image" | "video"; fromSec: number; toSec: number };
type SfxCue = { src: string; atSec: number; volume?: number };

export type FinalVideoProps = {
  film?: string; // staticFile path, e.g. "film/folgers.mp4" — omit to preview on a placeholder bg
  fps: number;
  durationSec: number; // set to your film's length
  captions: CaptionCue[];
  overlays: OverlayCue[];
  cutaways?: CutawayCue[];
  sfx?: SfxCue[];
  music?: { src: string; volume?: number };
};

export const calcFinalMeta = ({ props }: { props: FinalVideoProps }) => ({
  durationInFrames: Math.max(1, Math.round(props.durationSec * props.fps)),
  fps: props.fps,
  width: 1080,
  height: 1920,
});

const cover: React.CSSProperties = { position: "absolute", width: "100%", height: "100%", objectFit: "cover" };

const PlaceholderBg: React.FC = () => (
  <AbsoluteFill
    style={{
      background: "radial-gradient(70% 50% at 50% 36%, #2c2f36 0%, #121317 60%, #0b0c0f 100%)",
      alignItems: "center",
      justifyContent: "center",
    }}
  >
    <span style={{ fontFamily: mono, fontSize: 26, letterSpacing: 2, color: "#4d4f56" }}>▲ your film goes here</span>
  </AbsoluteFill>
);

// red-highlight parser: "they took *14.7%*" → "14.7%" in alert red
const renderHighlighted = (text: string) =>
  text.split("*").map((seg, i) =>
    i % 2 === 1 ? (
      <span key={i} style={{ color: theme.color.red }}>
        {seg}
      </span>
    ) : (
      <React.Fragment key={i}>{seg}</React.Fragment>
    )
  );

const CaptionLine: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = enter(frame, fps, { durationInFrames: 6 });
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: CAPTION.top,
        height: CAPTION.bottom - CAPTION.top,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity: p,
        transform: `translateY(${interpolate(p, [0, 1], [14, 0])}px)`,
      }}
    >
      <div
        style={{
          maxWidth: CAPTION.maxWidth,
          textAlign: "center",
          fontFamily: headline,
          fontWeight: 700,
          fontSize: 56,
          lineHeight: 1.15,
          color: theme.color.textPrimary,
          textShadow: "0 3px 0 #000, 0 0 10px #000, 3px 0 0 #000, -3px 0 0 #000",
        }}
      >
        {renderHighlighted(text)}
      </div>
    </div>
  );
};

const renderOverlay = (o: OverlayCue) => {
  switch (o.type) {
    case "caught":
      return <CaughtTitle {...(o.props as React.ComponentProps<typeof CaughtTitle>)} />;
    case "shrink":
      return <ShrinkOverlay {...(o.props as React.ComponentProps<typeof ShrinkOverlay>)} />;
    case "stat":
      return <StatCard {...(o.props as React.ComponentProps<typeof StatCard>)} />;
    case "rundown":
      return <RundownChip {...(o.props as React.ComponentProps<typeof RundownChip>)} />;
    case "source":
      return <SourceFrame {...(o.props as React.ComponentProps<typeof SourceFrame>)} />;
  }
};

const span = (fromSec: number, toSec: number, fps: number) => ({
  from: Math.round(fromSec * fps),
  durationInFrames: Math.max(1, Math.round((toSec - fromSec) * fps)),
});

export const FinalVideo: React.FC<FinalVideoProps> = ({ film, fps, captions, overlays, cutaways = [], sfx = [], music }) => (
  <AbsoluteFill style={{ background: theme.color.bg }}>
    {film ? <OffthreadVideo src={staticFile(film)} style={cover} /> : <PlaceholderBg />}

    {cutaways.map((c, i) => (
      <Sequence key={`c${i}`} {...span(c.fromSec, c.toSec, fps)}>
        {c.kind === "image" ? <Img src={staticFile(c.src)} style={cover} /> : <OffthreadVideo src={staticFile(c.src)} style={cover} />}
      </Sequence>
    ))}

    {overlays.map((o, i) => (
      <Sequence key={`o${i}`} {...span(o.fromSec, o.toSec, fps)}>
        {renderOverlay(o)}
      </Sequence>
    ))}

    {captions.map((c, i) => (
      <Sequence key={`cap${i}`} {...span(c.fromSec, c.toSec, fps)}>
        <CaptionLine text={c.text} />
      </Sequence>
    ))}

    {sfx.map((s, i) => (
      <Sequence key={`s${i}`} from={Math.round(s.atSec * fps)}>
        <Audio src={staticFile(s.src)} volume={s.volume ?? 1} />
      </Sequence>
    ))}

    {music ? <Audio src={staticFile(music.src)} volume={music.volume ?? 0.15} loop /> : null}
  </AbsoluteFill>
);
