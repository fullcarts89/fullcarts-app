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
import { ShrinkCutaway } from "./ShrinkCutaway";
import { Brandmark } from "../components/Brandmark";
import { SourceFrame } from "./SourceFrame";
import { CaughtTitle } from "./CaughtTitle";
import { KineticQuote } from "./KineticQuote";
import { ShrinkReveal } from "./ShrinkReveal";
import { HookText } from "./HookText";
import { RocketsFeathers } from "./RocketsFeathers";
import { PriceJump } from "./PriceJump";
import { FewerCups } from "./FewerCups";
import { OutroCard } from "./OutroCard";
import { HookChart } from "./HookChart";
import { InsetVideo } from "./InsetVideo";
import { LogoReveal } from "./LogoReveal";

// ---- Timeline types (Model B: feed your film + this timeline → one finished MP4) ----
type OverlayCue = { type: "caught" | "shrink" | "shrinkcut" | "stat" | "rundown" | "source" | "kinetic" | "shrinkreveal" | "hook" | "brandmark" | "footnote" | "rockets" | "pricejump" | "fewercups" | "outro" | "hookchart" | "insetvideo" | "logoreveal"; fromSec: number; toSec: number; props: Record<string, unknown> };
// Camera keyframes drive the film's scale/position over time — opening zoom, pattern
// interrupts, and fake "angle change" rehooks from a single take.
type CamKey = { atSec: number; scale: number; x?: number; y?: number };
type CaptionCue = { text: string; fromSec: number; toSec: number }; // wrap a word in *asterisks* to red-highlight it
type CutawayCue = { src: string; kind: "image" | "video"; fromSec: number; toSec: number; fit?: "cover" | "contain"; zoom?: number };
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
  camera?: CamKey[];
};

// interpolate the film transform across camera keyframes
const camAt = (keys: CamKey[] | undefined, t: number): { scale: number; x: number; y: number } => {
  if (!keys || keys.length === 0) return { scale: 1, x: 0, y: 0 };
  const k = [...keys].sort((a, b) => a.atSec - b.atSec);
  if (t <= k[0].atSec) return { scale: k[0].scale, x: k[0].x ?? 0, y: k[0].y ?? 0 };
  const last = k[k.length - 1];
  if (t >= last.atSec) return { scale: last.scale, x: last.x ?? 0, y: last.y ?? 0 };
  let a = k[0];
  let b = k[k.length - 1];
  for (let i = 0; i < k.length - 1; i++) {
    if (t >= k[i].atSec && t <= k[i + 1].atSec) {
      a = k[i];
      b = k[i + 1];
      break;
    }
  }
  const f = (from: number, to: number) => interpolate(t, [a.atSec, b.atSec], [from, to], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return { scale: f(a.scale, b.scale), x: f(a.x ?? 0, b.x ?? 0), y: f(a.y ?? 0, b.y ?? 0) };
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

// Self-aware "*actually 5" correction that pops in when the VO slips and says "six".
// Also used as a small comedic annotation box (e.g. "awkward data pose").
const Footnote: React.FC<{ text: string; top?: number }> = ({ text, top = 580 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = enter(frame, fps, { durationInFrames: 9 });
  const tilt = interpolate(Math.sin(frame / 5), [-1, 1], [-3, 3]);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top, left: 0, right: 0, display: "flex", justifyContent: "center", opacity: p, transform: `translateY(${interpolate(p, [0, 1], [12, 0])}px) scale(${interpolate(p, [0, 1], [0.6, 1])}) rotate(${tilt}deg)` }}>
        <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 46, color: theme.color.textPrimary, background: "rgba(10,11,13,0.85)", border: `1px solid ${theme.color.border}`, borderRadius: 12, padding: "10px 20px", textShadow: "0 2px 0 #000" }}>
          <span style={{ color: theme.color.red }}>*</span>
          {text.replace(/^\*/, "")}
        </span>
      </div>
    </AbsoluteFill>
  );
};

// FullCarts logo in the upper-left, inside the platform safe zone (clear of the status bar).
const CornerLogo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = enter(frame, fps, { durationInFrames: 12 });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top: 250, left: 60, opacity: p, transform: `translateY(${interpolate(p, [0, 1], [-14, 0])}px)` }}>
        <Brandmark scale={1.2} />
      </div>
    </AbsoluteFill>
  );
};

const renderOverlay = (o: OverlayCue) => {
  switch (o.type) {
    case "caught":
      return <CaughtTitle {...(o.props as React.ComponentProps<typeof CaughtTitle>)} />;
    case "shrink":
      return <ShrinkOverlay {...(o.props as React.ComponentProps<typeof ShrinkOverlay>)} />;
    case "shrinkcut":
      return <ShrinkCutaway {...(o.props as React.ComponentProps<typeof ShrinkCutaway>)} />;
    case "stat":
      return <StatCard {...(o.props as React.ComponentProps<typeof StatCard>)} />;
    case "rundown":
      return <RundownChip {...(o.props as React.ComponentProps<typeof RundownChip>)} />;
    case "source":
      return <SourceFrame {...(o.props as React.ComponentProps<typeof SourceFrame>)} />;
    case "kinetic":
      return <KineticQuote {...(o.props as React.ComponentProps<typeof KineticQuote>)} />;
    case "shrinkreveal":
      return <ShrinkReveal {...(o.props as React.ComponentProps<typeof ShrinkReveal>)} />;
    case "hook":
      return <HookText {...(o.props as React.ComponentProps<typeof HookText>)} />;
    case "brandmark":
      return <CornerLogo />;
    case "footnote":
      return <Footnote text={(o.props as { text: string; top?: number }).text} top={(o.props as { text: string; top?: number }).top} />;
    case "rockets":
      return <RocketsFeathers {...(o.props as React.ComponentProps<typeof RocketsFeathers>)} />;
    case "pricejump":
      return <PriceJump {...(o.props as React.ComponentProps<typeof PriceJump>)} />;
    case "fewercups":
      return <FewerCups {...(o.props as React.ComponentProps<typeof FewerCups>)} />;
    case "outro":
      return <OutroCard {...(o.props as React.ComponentProps<typeof OutroCard>)} />;
    case "hookchart":
      return <HookChart {...(o.props as React.ComponentProps<typeof HookChart>)} />;
    case "insetvideo":
      return <InsetVideo {...(o.props as React.ComponentProps<typeof InsetVideo>)} />;
    case "logoreveal":
      return <LogoReveal {...(o.props as React.ComponentProps<typeof LogoReveal>)} />;
  }
};

const FilmLayer: React.FC<{ film?: string; camera?: CamKey[] }> = ({ film, camera }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const c = camAt(camera, frame / fps);
  return (
    <AbsoluteFill style={{ transform: `scale(${c.scale}) translate(${c.x}px, ${c.y}px)`, transformOrigin: "center center" }}>
      {film ? <OffthreadVideo src={staticFile(film)} style={cover} /> : <PlaceholderBg />}
    </AbsoluteFill>
  );
};

const span = (fromSec: number, toSec: number, fps: number) => ({
  from: Math.round(fromSec * fps),
  durationInFrames: Math.max(1, Math.round((toSec - fromSec) * fps)),
});

// Image cutaway with an optional slow Ken Burns zoom (scale 1 → `zoom`) across
// the cutaway's own duration. Sits on a graphite bg so a contain-fit screenshot
// (e.g. the CNBC article) letterboxes cleanly instead of cropping the headline.
const CutawayImage: React.FC<{ src: string; fit: "cover" | "contain"; zoom?: number; durationInFrames: number }> = ({ src, fit, zoom, durationInFrames }) => {
  const frame = useCurrentFrame();
  const scale = zoom ? interpolate(frame, [0, durationInFrames], [1, zoom], { extrapolateRight: "clamp" }) : 1;
  return (
    <AbsoluteFill style={{ background: theme.color.bg }}>
      <Img src={staticFile(src)} style={{ ...cover, objectFit: fit, transform: `scale(${scale})` }} />
    </AbsoluteFill>
  );
};

export const FinalVideo: React.FC<FinalVideoProps> = ({ film, fps, captions, overlays, cutaways = [], sfx = [], music, camera }) => (
  <AbsoluteFill style={{ background: theme.color.bg }}>
    <FilmLayer film={film} camera={camera} />

    {cutaways.map((c, i) => (
      <Sequence key={`c${i}`} {...span(c.fromSec, c.toSec, fps)}>
        {c.kind === "image" ? (
          <CutawayImage src={c.src} fit={c.fit ?? "cover"} zoom={c.zoom} durationInFrames={span(c.fromSec, c.toSec, fps).durationInFrames} />
        ) : (
          <OffthreadVideo src={staticFile(c.src)} style={{ ...cover, objectFit: c.fit ?? "cover" }} />
        )}
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
