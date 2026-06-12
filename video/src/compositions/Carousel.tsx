import React from "react";
import { z } from "zod";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono, body } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

const item = z.object({
  rank: z.string(),
  brand: z.string(),
  product: z.string(),
  before: z.number(),
  after: z.number(),
  unit: z.string(),
  pct: z.number(),
});

export const carouselSchema = z.object({
  coverTitle: z.array(z.string()), // wrap a word in *asterisks* to red-highlight
  coverSub: z.string(),
  items: z.array(item),
  ctaHeadline: z.string(),
  ctaSub: z.string(),
  ctaPersona: z.string(),
});

type Props = z.infer<typeof carouselSchema>;
type Item = z.infer<typeof item>;

// Data-driven IG/TikTok carousel. Each FRAME is one slide: render stills at frame
// 0..(items+1). Slide 0 = cover, 1..N = products, N+1 = CTA. Built from real DB data.
const hl = (text: string) =>
  text.split("*").map((s, i) => (i % 2 === 1 ? <span key={i} style={{ color: theme.color.red }}>{s}</span> : <React.Fragment key={i}>{s}</React.Fragment>));

const Frame: React.FC<{ children: React.ReactNode; footer?: boolean }> = ({ children, footer }) => (
  <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
    <GridTexture opacity={0.06} />
    {children}
    {footer && (
      <div style={{ position: "absolute", bottom: 64, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontFamily: mono, fontSize: 30, color: theme.color.textTertiary }}>documented · fullcarts.org</span>
        <Brandmark scale={0.9} />
      </div>
    )}
  </AbsoluteFill>
);

const Cover: React.FC<{ title: string[]; sub: string }> = ({ title, sub }) => (
  <Frame>
    <div style={{ position: "absolute", top: 90, left: 80 }}><Brandmark scale={1.15} /></div>
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
      {title.map((line, i) => (
        <div key={i} style={{ fontFamily: headline, fontWeight: 700, fontSize: 132, lineHeight: 0.98, letterSpacing: -2, color: theme.color.textPrimary, textTransform: "uppercase" }}>
          {hl(line)}
        </div>
      ))}
      <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 46, color: theme.color.textSecondary, marginTop: 34 }}>{sub}</div>
    </AbsoluteFill>
    <div style={{ position: "absolute", bottom: 80, right: 80, fontFamily: mono, fontSize: 34, color: theme.color.red, letterSpacing: 2 }}>swipe →</div>
  </Frame>
);

const ProductSlide: React.FC<{ it: Item }> = ({ it }) => {
  const max = Math.max(it.before, it.after);
  return (
    <Frame footer>
      <div style={{ position: "absolute", top: 110, left: 80, right: 80 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 24 }}>
          <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 150, lineHeight: 0.9, color: theme.color.red }}>#{it.rank}</span>
          <div>
            <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 3, textTransform: "uppercase", color: theme.color.textSecondary }}>{it.brand}</div>
            <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 60, lineHeight: 1.02, color: theme.color.textPrimary, marginTop: 4 }}>{it.product}</div>
          </div>
        </div>
      </div>

      <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 26 }}>
          <Bar label={`${it.before} ${it.unit}`} width={100} color={theme.color.textTertiary} faded />
          <Bar label={`${it.after} ${it.unit}`} width={(it.after / max) * 100} color={theme.color.red} />
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 40 }}>
          <div style={{ background: theme.color.red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 88, borderRadius: 18, padding: "10px 30px" }}>−{it.pct}%</div>
        </div>
      </AbsoluteFill>
    </Frame>
  );
};

const Bar: React.FC<{ label: string; width: number; color: string; faded?: boolean }> = ({ label, width, color, faded }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
    <div style={{ height: 44, width: `${width}%`, minWidth: 70, background: color, opacity: faded ? 0.45 : 1, borderRadius: 8 }} />
    <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 44, color: theme.color.textPrimary, whiteSpace: "nowrap" }}>{label}</span>
  </div>
);

const CTA: React.FC<{ headline: string; sub: string; persona: string }> = ({ headline: h, sub, persona }) => (
  <Frame>
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
      <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 96, lineHeight: 1.0, letterSpacing: -1, color: theme.color.textPrimary }}>{hl(h)}</div>
      <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 52, color: theme.color.textSecondary, marginTop: 30 }}>{hl(sub)}</div>
      <div style={{ fontFamily: body, fontSize: 36, color: theme.color.textTertiary, marginTop: 40, lineHeight: 1.3 }}>{persona}</div>
    </AbsoluteFill>
    <div style={{ position: "absolute", bottom: 80, left: 80 }}><Brandmark scale={1.1} /></div>
  </Frame>
);

export const Carousel: React.FC<Props> = ({ coverTitle, coverSub, items, ctaHeadline, ctaSub, ctaPersona }) => {
  const i = Math.min(Math.floor(useCurrentFrame()), items.length + 1);
  if (i === 0) return <Cover title={coverTitle} sub={coverSub} />;
  if (i <= items.length) return <ProductSlide it={items[i - 1]} />;
  return <CTA headline={ctaHeadline} sub={ctaSub} persona={ctaPersona} />;
};
