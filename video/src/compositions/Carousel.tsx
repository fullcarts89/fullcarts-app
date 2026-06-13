import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
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
  image: z.string().optional(), // single paired photo (shows before+after) — http or local public/ path
  beforeImage: z.string().optional(), // explicit before/after pair (e.g. listing screenshot + your bag)
  afterImage: z.string().optional(),
  imagePos: z.string().optional(),
  caught: z.string().optional(), // "first caught" stamp, e.g. "Reddit · Jun 2022"
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
// Photo-forward when a real before/after photo is present; bars fallback otherwise.
const hl = (text: string) =>
  text.split("*").map((s, i) => (i % 2 === 1 ? <span key={i} style={{ color: theme.color.red }}>{s}</span> : <React.Fragment key={i}>{s}</React.Fragment>));

const resolve = (s?: string) => (s ? (s.startsWith("http") ? s : staticFile(s)) : null);

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

const Header: React.FC<{ it: Item }> = ({ it }) => (
  <div style={{ position: "absolute", top: 96, left: 80, right: 80 }}>
    <div style={{ display: "flex", alignItems: "baseline", gap: 22 }}>
      <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 140, lineHeight: 0.9, color: theme.color.red }}>#{it.rank}</span>
      <div>
        <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 3, textTransform: "uppercase", color: theme.color.textSecondary }}>{it.brand}</div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 54, lineHeight: 1.02, color: theme.color.textPrimary, marginTop: 4 }}>{it.product}</div>
      </div>
    </div>
  </div>
);

const PhotoCard: React.FC<{ src: string; pos?: string }> = ({ src, pos }) => (
  <div style={{ width: "100%", height: "100%", background: "#fff", borderRadius: 20, overflow: "hidden" }}>
    <Img src={src} style={{ width: "100%", height: "100%", objectFit: "contain", objectPosition: pos ?? "center" }} />
  </div>
);

const DataRow: React.FC<{ it: Item }> = ({ it }) => (
  <div style={{ position: "absolute", bottom: 140, left: 80, right: 80 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
      <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 48, color: theme.color.textPrimary }}>
        {it.before} → {it.after} {it.unit}
      </span>
      <div style={{ background: theme.color.red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 64, borderRadius: 16, padding: "6px 24px" }}>−{it.pct}%</div>
    </div>
    {it.caught && (
      <div style={{ fontFamily: mono, fontSize: 30, color: theme.color.textTertiary, letterSpacing: 1, marginTop: 18 }}>↳ first caught: {it.caught}</div>
    )}
  </div>
);

const Bar: React.FC<{ label: string; width: number; color: string; faded?: boolean }> = ({ label, width, color, faded }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
    <div style={{ height: 44, width: `${width}%`, minWidth: 70, background: color, opacity: faded ? 0.45 : 1, borderRadius: 8 }} />
    <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 44, color: theme.color.textPrimary, whiteSpace: "nowrap" }}>{label}</span>
  </div>
);

const ProductSlide: React.FC<{ it: Item }> = ({ it }) => {
  const before = resolve(it.beforeImage);
  const after = resolve(it.afterImage);
  const single = resolve(it.image);
  const pair = before && after;
  const hasPhoto = pair || single;

  // photo-forward layout: real before/after photo is the hero, data row beneath
  if (hasPhoto) {
    return (
      <Frame footer>
        <Header it={it} />
        <div style={{ position: "absolute", top: 300, bottom: 320, left: 80, right: 80 }}>
          {pair ? (
            <div style={{ display: "flex", gap: 22, height: "100%" }}>
              {[
                { src: before as string, tag: "before", size: `${it.before} ${it.unit}`, accent: false },
                { src: after as string, tag: "after", size: `${it.after} ${it.unit}`, accent: true },
              ].map((c, i) => (
                <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
                  <div style={{ fontFamily: mono, fontSize: 26, letterSpacing: 3, textTransform: "uppercase", color: c.accent ? theme.color.red : theme.color.textSecondary, marginBottom: 10 }}>{c.tag}</div>
                  <div style={{ flex: 1, minHeight: 0 }}><PhotoCard src={c.src} /></div>
                  <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 38, color: c.accent ? theme.color.red : theme.color.textPrimary, marginTop: 12 }}>{c.size}</div>
                </div>
              ))}
            </div>
          ) : (
            <PhotoCard src={single as string} pos={it.imagePos} />
          )}
        </div>
        <DataRow it={it} />
      </Frame>
    );
  }

  // bars fallback (no photo available)
  const max = Math.max(it.before, it.after);
  return (
    <Frame footer>
      <Header it={it} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "flex-start", padding: "0 80px" }}>
        <div style={{ width: "100%", display: "flex", flexDirection: "column", gap: 26 }}>
          <Bar label={`${it.before} ${it.unit}`} width={100} color={theme.color.textTertiary} faded />
          <Bar label={`${it.after} ${it.unit}`} width={(it.after / max) * 100} color={theme.color.red} />
        </div>
        <div style={{ marginTop: 40 }}>
          <div style={{ display: "inline-block", background: theme.color.red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 88, borderRadius: 18, padding: "10px 30px" }}>−{it.pct}%</div>
        </div>
      </AbsoluteFill>
    </Frame>
  );
};

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
