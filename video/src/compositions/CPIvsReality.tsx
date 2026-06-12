import React from "react";
import { z } from "zod";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono, body } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

// "Official Inflation vs. Reality" — the macro newsjack carousel (post on CPI day).
// Pairs the REAL category CPI %-change (the institutional number, from BLS/FRED) against
// the documented pack shrink for that category. STUB: layout is functional but minimal —
// polish (icons, the per-category source chip) is TODO.
//
// GATE GUARDRAIL (see docs/content/carousel-formats.md): CPI measures PRICE UP, our number
// measures SIZE DOWN — they are two different hidden hikes. Frame them as "the half inflation
// barely counts," NEVER as "CPI is wrong by Y%."

const item = z.object({
  category: z.string(),
  cpiPct: z.number(), // official YoY CPI change for the category, e.g. 2.1
  brand: z.string(),
  product: z.string(),
  shelfPct: z.number(), // documented pack shrink, e.g. 18.9
});

export const cpiVsRealitySchema = z.object({
  cpiHeadline: z.string(), // e.g. "Groceries: +2.1% this year" — a real BLS/FRED figure
  cpiSource: z.string(), // e.g. "BLS CPI: Food at Home, YoY"
  items: z.array(item),
  ctaHeadline: z.string(),
  ctaSub: z.string(),
});

type Props = z.infer<typeof cpiVsRealitySchema>;
type Item = z.infer<typeof item>;

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

const Cover: React.FC<{ h: string; source: string }> = ({ h, source }) => (
  <Frame>
    <div style={{ position: "absolute", top: 90, left: 80 }}><Brandmark scale={1.15} /></div>
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
      <div style={{ fontFamily: mono, fontSize: 32, letterSpacing: 4, textTransform: "uppercase", color: theme.color.textSecondary, marginBottom: 24 }}>the official number</div>
      <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 116, lineHeight: 1.0, letterSpacing: -2, color: theme.color.textPrimary }}>{h}</div>
      <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 46, color: theme.color.textSecondary, marginTop: 30 }}>…here's what actually happened to the box. <span style={{ color: theme.color.red, fontFamily: mono }}>swipe →</span></div>
      <div style={{ fontFamily: mono, fontSize: 28, color: theme.color.textTertiary, marginTop: 40 }}>{source}</div>
    </AbsoluteFill>
  </Frame>
);

const Pair: React.FC<{ it: Item }> = ({ it }) => (
  <Frame footer>
    <div style={{ position: "absolute", top: 110, left: 80, right: 80 }}>
      <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 3, textTransform: "uppercase", color: theme.color.textSecondary }}>{it.category}</div>
      <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 56, color: theme.color.textPrimary, marginTop: 4 }}>{it.brand} · {it.product}</div>
    </div>
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px", gap: 40 }}>
      <div>
        <div style={{ fontFamily: mono, fontSize: 28, letterSpacing: 2, textTransform: "uppercase", color: theme.color.textTertiary }}>official says price</div>
        <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 96, color: theme.color.textSecondary }}>+{it.cpiPct}%</div>
      </div>
      <div>
        <div style={{ fontFamily: mono, fontSize: 28, letterSpacing: 2, textTransform: "uppercase", color: theme.color.red }}>the box actually</div>
        <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 130, color: theme.color.red }}>−{it.shelfPct}%</div>
      </div>
    </AbsoluteFill>
  </Frame>
);

const CTA: React.FC<{ h: string; sub: string }> = ({ h, sub }) => (
  <Frame>
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
      <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 92, lineHeight: 1.02, letterSpacing: -1, color: theme.color.textPrimary }}>{h}</div>
      <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 50, color: theme.color.textSecondary, marginTop: 28 }}>{sub}</div>
    </AbsoluteFill>
    <div style={{ position: "absolute", bottom: 80, left: 80 }}><Brandmark scale={1.1} /></div>
  </Frame>
);

export const CPIvsReality: React.FC<Props> = ({ cpiHeadline, cpiSource, items, ctaHeadline, ctaSub }) => {
  const i = Math.min(Math.floor(useCurrentFrame()), items.length + 1);
  if (i === 0) return <Cover h={cpiHeadline} source={cpiSource} />;
  if (i <= items.length) return <Pair it={items[i - 1]} />;
  return <CTA h={ctaHeadline} sub={ctaSub} />;
};
