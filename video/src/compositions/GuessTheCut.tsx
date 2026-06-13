import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono, body } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

// "Guess the Cut" — the gamified quiz carousel. Each product gets TWO slides: a
// QUESTION (before size shown, after withheld behind a red "?") then the ANSWER
// (the reveal: −%, the after size, and an exactly-true equivalence). The answer
// never shares a slide with the question, so the curiosity forces the swipe.
// One slide per FRAME: cover=0, then Q/A pairs, then CTA. Render stills 0..items*2+1.
//
// GATE WATCH-OUT (see docs/content/carousel-formats.md): every `equiv` line must be
// ARITHMETIC, not embellishment — 32→28 fl oz is "half a cup", NOT "a full glass" —
// and the lineup must stay category-coherent.

const item = z.object({
  rank: z.string(),
  brand: z.string(),
  product: z.string(),
  before: z.number(),
  after: z.number(),
  unit: z.string(),
  pct: z.number(),
  equiv: z.string(), // exactly-true equivalence, e.g. "half a cup, gone"
  image: z.string().optional(), // real product photo: product_entities.image_url (http…) or a public/ path
  imagePos: z.string().optional(),
});

export const guessTheCutSchema = z.object({
  coverTitle: z.array(z.string()), // wrap a word in *asterisks* to red-highlight
  coverSub: z.string(),
  items: z.array(item),
  ctaHeadline: z.string(),
  ctaSub: z.string(),
  ctaPersona: z.string(),
});

type Props = z.infer<typeof guessTheCutSchema>;
type Item = z.infer<typeof item>;

const hl = (text: string) =>
  text.split("*").map((s, i) =>
    i % 2 === 1 ? (
      <span key={i} style={{ color: theme.color.red }}>{s}</span>
    ) : (
      <React.Fragment key={i}>{s}</React.Fragment>
    )
  );

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
      <div style={{ fontFamily: mono, fontSize: 32, letterSpacing: 4, textTransform: "uppercase", color: theme.color.red, marginBottom: 24 }}>the quiz</div>
      {title.map((line, i) => (
        <div key={i} style={{ fontFamily: headline, fontWeight: 700, fontSize: 150, lineHeight: 0.96, letterSpacing: -2, color: theme.color.textPrimary, textTransform: "uppercase" }}>
          {hl(line)}
        </div>
      ))}
      <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 44, color: theme.color.textSecondary, marginTop: 34 }}>{sub}</div>
    </AbsoluteFill>
    <div style={{ position: "absolute", bottom: 80, right: 80, fontFamily: mono, fontSize: 34, color: theme.color.red, letterSpacing: 2 }}>swipe →</div>
  </Frame>
);

// The product-photo panel — reserved on every Q/A slide so the layout always leaves
// room for an image. Renders the real photo when `image` is set; otherwise a labelled
// placeholder so the reserved zone is visible (and obvious that an image belongs there).
const PhotoPanel: React.FC<{ image?: string; imagePos?: string }> = ({ image, imagePos }) => {
  const src = image ? (image.startsWith("http") ? image : staticFile(image)) : null;
  return (
    <div style={{ position: "absolute", right: 72, top: 320, width: 392, height: 600, borderRadius: 22, overflow: "hidden", background: src ? "#fff" : theme.color.card, border: src ? "none" : `2px dashed ${theme.color.border}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
      {src ? (
        <Img src={src} style={{ width: "100%", height: "100%", objectFit: "contain", objectPosition: imagePos ?? "center" }} />
      ) : (
        <span style={{ fontFamily: mono, fontSize: 26, letterSpacing: 2, textTransform: "uppercase", color: theme.color.textTertiary }}>product photo</span>
      )}
    </div>
  );
};

// Left text column clears the photo panel on the right.
const COL_RIGHT = 520;

const QA: React.FC<{ it: Item; reveal: boolean }> = ({ it, reveal }) => (
  <Frame footer>
    <PhotoPanel image={it.image} imagePos={it.imagePos} />

    <div style={{ position: "absolute", top: 110, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
      <div style={{ maxWidth: 560 }}>
        <div style={{ fontFamily: mono, fontSize: 28, letterSpacing: 3, textTransform: "uppercase", color: theme.color.red }}>guess the cut</div>
        <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 3, textTransform: "uppercase", color: theme.color.textSecondary, marginTop: 30 }}>{it.brand}</div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 56, lineHeight: 1.02, color: theme.color.textPrimary, marginTop: 4 }}>{it.product}</div>
      </div>
      <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 88, lineHeight: 0.9, color: theme.color.textTertiary }}>#{it.rank}</span>
    </div>

    <AbsoluteFill style={{ justifyContent: "center", paddingLeft: 80, paddingRight: COL_RIGHT }}>
      <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 2, textTransform: "uppercase", color: theme.color.textTertiary, marginBottom: 14 }}>was</div>
      <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 76, color: theme.color.textPrimary }}>{it.before} {it.unit}</div>

      <div style={{ height: 1, background: theme.color.border, margin: "40px 0" }} />

      {!reveal ? (
        <>
          <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 2, textTransform: "uppercase", color: theme.color.textTertiary, marginBottom: 4 }}>now?</div>
          <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 200, lineHeight: 0.9, color: theme.color.red }}>?</div>
          <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 44, color: theme.color.textSecondary, marginTop: 16 }}>
            how much did they cut? <span style={{ color: theme.color.red, fontFamily: mono }}>swipe →</span>
          </div>
        </>
      ) : (
        <>
          <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 2, textTransform: "uppercase", color: theme.color.textTertiary, marginBottom: 16 }}>now</div>
          <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 76, color: theme.color.red }}>{it.after} {it.unit}</div>
          <div style={{ marginTop: 22 }}>
            <span style={{ display: "inline-block", background: theme.color.red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 64, borderRadius: 16, padding: "6px 26px" }}>−{it.pct}%</span>
          </div>
          <div style={{ fontFamily: headline, fontWeight: 600, fontSize: 46, color: theme.color.textPrimary, marginTop: 30 }}>= {it.equiv}</div>
        </>
      )}
    </AbsoluteFill>
  </Frame>
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

export const GuessTheCut: React.FC<Props> = ({ coverTitle, coverSub, items, ctaHeadline, ctaSub, ctaPersona }) => {
  const n = items.length;
  const i = Math.min(Math.floor(useCurrentFrame()), n * 2 + 1);
  if (i === 0) return <Cover title={coverTitle} sub={coverSub} />;
  if (i === n * 2 + 1) return <CTA headline={ctaHeadline} sub={ctaSub} persona={ctaPersona} />;
  const idx = i - 1;
  return <QA it={items[Math.floor(idx / 2)]} reveal={idx % 2 === 1} />;
};
