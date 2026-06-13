import React from "react";
import { z } from "zod";
import {
  AbsoluteFill,
  Img,
  Sequence,
  staticFile,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../lib/theme";
import { headline, mono, body } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

// VIDEO version of the data carousel (auto-advancing, animated) — same data + look as
// the still `Carousel`, but it plays as one MP4 so it posts as a Reel / Short.
// Height-responsive (useVideoConfig) so ONE component renders 4:5 (1080×1350) AND
// 9:16 (1080×1920). Per-slide timing + duration computed in calcCarouselVideoMeta.
const item = z.object({
  rank: z.string(),
  brand: z.string(),
  product: z.string(),
  before: z.number(),
  after: z.number(),
  unit: z.string(),
  pct: z.number(),
  image: z.string().optional(), // DB image_url (http…) or local public/ path; falls back to bars
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
const SLIDE_SEC = 2.7;
const CTA_SEC = 3.4;

const secs = (p: Props) => ({
  cover: p.coverSec ?? COVER_SEC,
  slide: p.slideSec ?? SLIDE_SEC,
  cta: p.ctaSec ?? CTA_SEC,
});

// calculateMetadata: total duration adapts to the number of items
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

// entrance fade + rise, exit fade — makes the cut between slides feel smooth
const SlideWrap: React.FC<{ dur: number; children: React.ReactNode }> = ({ dur, children }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const rise = spring({ frame: f, fps, config: { damping: 200 }, durationInFrames: 14 });
  const ty = interpolate(rise, [0, 1], [34, 0]);
  const inOp = interpolate(f, [0, 9], [0, 1], { extrapolateRight: "clamp" });
  const outOp = interpolate(f, [dur - 8, dur], [1, 0], { extrapolateLeft: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: Math.min(inOp, outOp), transform: `translateY(${ty}px)` }}>
      {children}
    </AbsoluteFill>
  );
};

const Bar: React.FC<{ label: string; width: number; color: string; faded?: boolean }> = ({ label, width, color, faded }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
    <div style={{ height: 42, width: `${width}%`, minWidth: 64, background: color, opacity: faded ? 0.4 : 1, borderRadius: 8 }} />
    <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 42, color: theme.color.textPrimary, whiteSpace: "nowrap" }}>{label}</span>
  </div>
);

const ProductSlide: React.FC<{ it: Item }> = ({ it }) => {
  const max = Math.max(it.before, it.after);
  const hasImg = !!it.image;
  const src = it.image ? (it.image.startsWith("http") ? it.image : staticFile(it.image)) : null;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "260px 80px 200px" }}>
      <div style={{ width: "100%", maxWidth: 920, display: "flex", flexDirection: "column", gap: 40 }}>
        {/* rank + brand + product */}
        <div style={{ display: "flex", alignItems: "center", gap: 26 }}>
          <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 132, lineHeight: 0.85, color: theme.color.red }}>#{it.rank}</span>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontFamily: mono, fontSize: 28, letterSpacing: 3, textTransform: "uppercase", color: theme.color.textSecondary }}>{it.brand}</div>
            <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 50, lineHeight: 1.02, color: theme.color.textPrimary, marginTop: 4 }}>{it.product}</div>
          </div>
        </div>

        {/* product photo (when available) — bars-only fallback in network-locked renders */}
        {hasImg && src && (
          <div style={{ alignSelf: "center", width: 460, height: 460, background: "#fff", borderRadius: 22, overflow: "hidden" }}>
            <Img src={src} style={{ width: "100%", height: "100%", objectFit: "contain", objectPosition: it.imagePos ?? "center" }} />
          </div>
        )}

        {/* before / after bars */}
        <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
          <Bar label={`${it.before} ${it.unit}`} width={100} color={theme.color.textTertiary} faded />
          <Bar label={`${it.after} ${it.unit}`} width={(it.after / max) * 100} color={theme.color.red} />
        </div>

        {/* −X% badge */}
        <div>
          <div style={{ display: "inline-block", background: theme.color.red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 80, borderRadius: 18, padding: "8px 28px" }}>−{it.pct}%</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Cover: React.FC<{ title: string[]; sub: string; prompt: string }> = ({ title, sub, prompt }) => {
  const f = useCurrentFrame();
  const blink = Math.sin(f / 5) > -0.3 ? 1 : 0.25; // soft pulse on the prompt
  return (
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
      {title.map((l, i) => (
        <div key={i} style={{ fontFamily: headline, fontWeight: 700, fontSize: 120, lineHeight: 0.98, letterSpacing: -2, color: theme.color.textPrimary, textTransform: "uppercase" }}>{hl(l)}</div>
      ))}
      <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 46, color: theme.color.textSecondary, marginTop: 30 }}>{sub}</div>
      <div style={{ fontFamily: mono, fontSize: 34, color: theme.color.red, letterSpacing: 1, marginTop: 44, opacity: blink }}>{prompt}</div>
    </AbsoluteFill>
  );
};

const CTA: React.FC<{ headline: string; sub: string; persona: string }> = ({ headline: h, sub, persona }) => (
  <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
    <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 92, lineHeight: 1.0, letterSpacing: -1, color: theme.color.textPrimary }}>{hl(h)}</div>
    <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 50, color: theme.color.textSecondary, marginTop: 28 }}>{hl(sub)}</div>
    <div style={{ fontFamily: body, fontSize: 34, color: theme.color.textTertiary, marginTop: 40, lineHeight: 1.35 }}>{persona}</div>
  </AbsoluteFill>
);

// thin top progress bar that fills across the whole video (global frame)
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

      {/* persistent frame: brandmark, progress, footer */}
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
