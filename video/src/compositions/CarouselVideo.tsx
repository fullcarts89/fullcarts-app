import React from "react";
import {
  AbsoluteFill,
  Img,
  Sequence,
  staticFile,
  interpolate,
  spring,
  Easing,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { theme } from "../lib/theme";
import { headline, mono, body } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

// VIDEO version of the data carousel (auto-advancing, animated) — same data + look as
// the still `Carousel`, but it plays as one MP4 so it posts as a Reel / Short.
// Height-responsive (useVideoConfig) so ONE component renders 4:5 (1080×1350) AND
// 9:16 (1080×1920). Per-slide timing + duration computed in calcCarouselVideoMeta.
// Motion mirrors the Folgers cut: staggered reveals, count-up %, badge pop, photo
// scale-in + slow Ken Burns, before/after sliding in from the sides.
const item = z.object({
  rank: z.string(),
  brand: z.string(),
  product: z.string(),
  before: z.number(),
  after: z.number(),
  unit: z.string(),
  pct: z.number(),
  image: z.string().optional(), // single paired photo (before+after) — http or local public/ path
  beforeImage: z.string().optional(), // explicit before/after pair
  afterImage: z.string().optional(),
  imagePos: z.string().optional(),
});

export const carouselVideoSchema = z.object({
  coverTitle: z.array(z.string()), // wrap a word in *asterisks* to red-highlight
  coverSub: z.string(),
  coverPrompt: z.string(),
  items: z.array(item),
  ctaHeadline: z.string(),
  ctaSub: z.string(),
  ctaPersona: z.string(),
  coverSec: z.number().optional(),
  slideSec: z.number().optional(),
  ctaSec: z.number().optional(),
});

type Props = z.infer<typeof carouselVideoSchema>;
type Item = z.infer<typeof item>;

const COVER_SEC = 2.6;
const SLIDE_SEC = 2.9;
const CTA_SEC = 3.4;

const secs = (p: Props) => ({
  cover: p.coverSec ?? COVER_SEC,
  slide: p.slideSec ?? SLIDE_SEC,
  cta: p.ctaSec ?? CTA_SEC,
});

export const calcCarouselVideoMeta = ({ props }: { props: Props }) => {
  const fps = 30;
  const s = secs(props);
  const total = s.cover + props.items.length * s.slide + s.cta;
  return { durationInFrames: Math.round(fps * total), fps };
};

const hl = (text: string) =>
  text.split("*").map((s, i) =>
    i % 2 === 1 ? (
      <span key={i} style={{ color: theme.color.red }}>{s}</span>
    ) : (
      <React.Fragment key={i}>{s}</React.Fragment>
    )
  );

const resolve = (s?: string) => (s ? (s.startsWith("http") ? s : staticFile(s)) : null);

// eased 0..1 ramp between two frames (ease-out cubic) — the house "settle" curve
const ramp = (f: number, start: number, end: number) =>
  interpolate(f, [start, end], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });

// entrance fade + rise, exit fade — smooth cut between slides
const SlideWrap: React.FC<{ dur: number; children: React.ReactNode }> = ({ dur, children }) => {
  const f = useCurrentFrame();
  const inOp = interpolate(f, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const outOp = interpolate(f, [dur - 7, dur], [1, 0], { extrapolateLeft: "clamp" });
  return <AbsoluteFill style={{ opacity: Math.min(inOp, outOp) }}>{children}</AbsoluteFill>;
};

const PhotoCard: React.FC<{ src: string; pos?: string; in0: number }> = ({ src, pos, in0 }) => {
  const f = useCurrentFrame();
  const a = ramp(f, in0, in0 + 14);
  const enter = interpolate(a, [0, 1], [0.94, 1]); // scale-in
  const ken = interpolate(f, [0, 80], [1, 1.05], { extrapolateRight: "clamp" }); // slow Ken Burns
  return (
    <div style={{ width: "100%", height: "100%", borderRadius: 20, overflow: "hidden", background: "#fff", opacity: a, transform: `scale(${enter})` }}>
      <Img src={src} style={{ width: "100%", height: "100%", objectFit: "contain", objectPosition: pos ?? "center", transform: `scale(${ken})` }} />
    </div>
  );
};

const Head: React.FC<{ it: Item }> = ({ it }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const a = ramp(f, 0, 12);
  const slam = spring({ frame: f, fps, config: { damping: 14, mass: 0.7 }, durationInFrames: 18 }); // rank stamps in
  const rankScale = interpolate(slam, [0, 1], [1.35, 1]);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 24, opacity: a, transform: `translateX(${interpolate(a, [0, 1], [-46, 0])}px)` }}>
      <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 120, lineHeight: 0.85, color: theme.color.red, transform: `scale(${rankScale})`, transformOrigin: "left center" }}>#{it.rank}</span>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontFamily: mono, fontSize: 28, letterSpacing: 3, textTransform: "uppercase", color: theme.color.textSecondary }}>{it.brand}</div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 48, lineHeight: 1.02, color: theme.color.textPrimary, marginTop: 4 }}>{it.product}</div>
      </div>
    </div>
  );
};

// count-up % + spring pop on the badge, range slides up — the Folgers "number lands" beat
const Badge: React.FC<{ it: Item; in0: number; withRange?: boolean }> = ({ it, in0, withRange }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const count = ramp(f, in0, in0 + 22);
  const shown = (it.pct * count).toFixed(1);
  const pop = spring({ frame: f - in0, fps, config: { damping: 13, mass: 0.6 }, durationInFrames: 20 });
  const rangeA = ramp(f, in0 - 4, in0 + 12);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 26 }}>
      {withRange && (
        <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 46, color: theme.color.textPrimary, opacity: rangeA, transform: `translateY(${interpolate(rangeA, [0, 1], [16, 0])}px)` }}>
          {it.before} → {it.after} {it.unit}
        </span>
      )}
      <div style={{ background: theme.color.red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: withRange ? 64 : 80, borderRadius: 16, padding: withRange ? "6px 24px" : "8px 28px", transform: `scale(${interpolate(pop, [0, 1], [0.5, 1])})`, opacity: interpolate(f, [in0, in0 + 3], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
        −{shown}%
      </div>
    </div>
  );
};

const Bar: React.FC<{ label: string; target: number; color: string; faded?: boolean; in0: number }> = ({ label, target, color, faded, in0 }) => {
  const f = useCurrentFrame();
  const grow = ramp(f, in0, in0 + 16);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
      <div style={{ height: 42, width: `${target * grow}%`, minWidth: 64, background: color, opacity: faded ? 0.4 : 1, borderRadius: 8 }} />
      <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 42, color: theme.color.textPrimary, whiteSpace: "nowrap", opacity: grow }}>{label}</span>
    </div>
  );
};

const PairColumn: React.FC<{ src: string; tag: string; size: string; accent: boolean; in0: number; fromX: number }> = ({ src, tag, size, accent, in0, fromX }) => {
  const f = useCurrentFrame();
  const a = ramp(f, in0, in0 + 14);
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0, transform: `translateX(${interpolate(a, [0, 1], [fromX, 0])}px)`, opacity: a }}>
      <div style={{ fontFamily: mono, fontSize: 26, letterSpacing: 3, textTransform: "uppercase", color: accent ? theme.color.red : theme.color.textSecondary, marginBottom: 10 }}>{tag}</div>
      <div style={{ flex: 1, minHeight: 0 }}><PhotoCard src={src} in0={in0} /></div>
      <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 38, color: accent ? theme.color.red : theme.color.textPrimary, marginTop: 12 }}>{size}</div>
    </div>
  );
};

const ProductSlide: React.FC<{ it: Item }> = ({ it }) => {
  const before = resolve(it.beforeImage);
  const after = resolve(it.afterImage);
  const single = resolve(it.image);
  const pair = before && after;
  const hasPhoto = pair || single;

  if (hasPhoto) {
    return (
      <AbsoluteFill style={{ padding: "250px 80px 220px", display: "flex", flexDirection: "column" }}>
        <Head it={it} />
        <div style={{ flex: 1, minHeight: 0, marginTop: 34, marginBottom: 30 }}>
          {pair ? (
            <div style={{ display: "flex", gap: 22, height: "100%" }}>
              <PairColumn src={before as string} tag="before" size={`${it.before} ${it.unit}`} accent={false} in0={8} fromX={-40} />
              <PairColumn src={after as string} tag="after" size={`${it.after} ${it.unit}`} accent in0={14} fromX={40} />
            </div>
          ) : (
            <PhotoCard src={single as string} pos={it.imagePos} in0={6} />
          )}
        </div>
        <Badge it={it} in0={22} withRange />
      </AbsoluteFill>
    );
  }

  // bars fallback (no photo) — animated grow + count-up
  const max = Math.max(it.before, it.after);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "260px 80px 200px" }}>
      <div style={{ width: "100%", maxWidth: 920, display: "flex", flexDirection: "column", gap: 40 }}>
        <Head it={it} />
        <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
          <Bar label={`${it.before} ${it.unit}`} target={100} color={theme.color.textTertiary} faded in0={10} />
          <Bar label={`${it.after} ${it.unit}`} target={(it.after / max) * 100} color={theme.color.red} in0={16} />
        </div>
        <Badge it={it} in0={24} />
      </div>
    </AbsoluteFill>
  );
};

const Cover: React.FC<{ title: string[]; sub: string; prompt: string }> = ({ title, sub, prompt }) => {
  const f = useCurrentFrame();
  const blink = Math.sin(f / 5) > -0.3 ? 1 : 0.25;
  const subA = ramp(f, title.length * 5 + 2, title.length * 5 + 16);
  return (
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
      {title.map((l, i) => {
        const a = ramp(f, i * 5, i * 5 + 14);
        return (
          <div key={i} style={{ fontFamily: headline, fontWeight: 700, fontSize: 120, lineHeight: 0.98, letterSpacing: -2, color: theme.color.textPrimary, textTransform: "uppercase", opacity: a, transform: `translateY(${interpolate(a, [0, 1], [40, 0])}px)` }}>{hl(l)}</div>
        );
      })}
      <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 46, color: theme.color.textSecondary, marginTop: 30, opacity: subA, transform: `translateY(${interpolate(subA, [0, 1], [24, 0])}px)` }}>{sub}</div>
      <div style={{ fontFamily: mono, fontSize: 34, color: theme.color.red, letterSpacing: 1, marginTop: 44, opacity: blink * ramp(f, 24, 36) }}>{prompt}</div>
    </AbsoluteFill>
  );
};

const CTA: React.FC<{ headline: string; sub: string; persona: string }> = ({ headline: h, sub, persona }) => {
  const f = useCurrentFrame();
  const a1 = ramp(f, 0, 14);
  const a2 = ramp(f, 8, 22);
  const a3 = ramp(f, 18, 34);
  return (
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
      <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 92, lineHeight: 1.0, letterSpacing: -1, color: theme.color.textPrimary, opacity: a1, transform: `translateY(${interpolate(a1, [0, 1], [30, 0])}px)` }}>{hl(h)}</div>
      <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 50, color: theme.color.textSecondary, marginTop: 28, opacity: a2 }}>{hl(sub)}</div>
      <div style={{ fontFamily: body, fontSize: 34, color: theme.color.textTertiary, marginTop: 40, lineHeight: 1.35, opacity: a3 }}>{persona}</div>
    </AbsoluteFill>
  );
};

const ProgressBar: React.FC = () => {
  const f = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const w = interpolate(f, [0, durationInFrames - 1], [0, 100], { extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", top: 120, left: 80, right: 80, height: 8, background: theme.color.card, borderRadius: 4, overflow: "hidden" }}>
      <div style={{ height: "100%", width: `${w}%`, background: theme.color.red, borderRadius: 4 }} />
    </div>
  );
};

export const CarouselVideo: React.FC<Props> = (props) => {
  const { coverTitle, coverSub, coverPrompt, items, ctaHeadline, ctaSub, ctaPersona } = props;
  const { fps } = useVideoConfig();
  const s = secs(props);
  const coverF = Math.round(fps * s.cover);
  const slideF = Math.round(fps * s.slide);
  const ctaF = Math.round(fps * s.cta);

  return (
    <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
      <GridTexture opacity={0.06} />

      <div style={{ position: "absolute", top: 70, left: 80 }}><Brandmark scale={1.0} /></div>
      <ProgressBar />
      <div style={{ position: "absolute", bottom: 60, left: 0, right: 0, textAlign: "center", fontFamily: mono, fontSize: 28, color: theme.color.textTertiary, letterSpacing: 1 }}>
        documented · fullcarts.org
      </div>

      <Sequence from={0} durationInFrames={coverF}>
        <SlideWrap dur={coverF}><Cover title={coverTitle} sub={coverSub} prompt={coverPrompt} /></SlideWrap>
      </Sequence>

      {items.map((it, i) => (
        <Sequence key={i} from={coverF + i * slideF} durationInFrames={slideF}>
          <SlideWrap dur={slideF}><ProductSlide it={it} /></SlideWrap>
        </Sequence>
      ))}

      <Sequence from={coverF + items.length * slideF} durationInFrames={ctaF}>
        <SlideWrap dur={ctaF}><CTA headline={ctaHeadline} sub={ctaSub} persona={ctaPersona} /></SlideWrap>
      </Sequence>
    </AbsoluteFill>
  );
};
