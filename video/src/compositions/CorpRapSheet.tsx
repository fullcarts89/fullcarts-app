import React from "react";
import { z } from "zod";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono, body } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

const cut = z.object({
  brand: z.string(),
  before: z.number(),
  after: z.number(),
  unit: z.string(),
  pct: z.number(),
});

const company = z.object({
  name: z.string(),       // parent company, e.g. "Mondelez"
  tag: z.string(),        // honest breadth line, e.g. "+ 32 more of their brands in our data"
  cuts: z.array(cut),     // one documented cut per named brand (2–3)
});

export const corpRapSheetSchema = z.object({
  coverTitle: z.array(z.string()), // wrap a word in *asterisks* to red-highlight
  coverSub: z.string(),
  companies: z.array(company),
  ctaHeadline: z.string(),
  ctaSub: z.string(),
  ctaPersona: z.string(),
});

type Props = z.infer<typeof corpRapSheetSchema>;
type Company = z.infer<typeof company>;
type Cut = z.infer<typeof cut>;

// Corporate rap sheet carousel. Each FRAME is one slide: render stills 0..(companies+1).
// Slide 0 = cover, 1..N = one parent company each (with a documented cut per named brand),
// N+1 = CTA. Built from real DB data — proves the "they shrank ALL of them" thesis instead of
// naming brands it can't back up.
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
        <span style={{ fontFamily: mono, fontSize: 30, color: theme.color.textTertiary }}>every figure sourced · fullcarts.org</span>
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

// Each row's bar is normalized to its OWN before→after (the red fill = what's LEFT, the gap on
// the right = what they took). Per-row so mixed units (oz / ct / ml) never get cross-compared.
const CutRow: React.FC<{ c: Cut }> = ({ c }) => (
  <div style={{ borderTop: `1px solid ${theme.color.textTertiary}33`, padding: "26px 0 22px" }}>
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 24 }}>
      <span style={{ fontFamily: headline, fontWeight: 700, fontSize: 50, color: theme.color.textPrimary, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.brand}</span>
      <div style={{ display: "flex", alignItems: "center", gap: 22, flexShrink: 0 }}>
        <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 38, color: theme.color.textSecondary, whiteSpace: "nowrap" }}>
          {c.before} → {c.after} {c.unit}
        </span>
        <div style={{ background: theme.color.red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 44, borderRadius: 14, padding: "4px 18px", whiteSpace: "nowrap" }}>−{c.pct}%</div>
      </div>
    </div>
    <div style={{ marginTop: 16, height: 18, background: `${theme.color.textTertiary}22`, borderRadius: 6, overflow: "hidden" }}>
      <div style={{ width: `${(c.after / c.before) * 100}%`, height: "100%", background: theme.color.red, borderRadius: 6 }} />
    </div>
  </div>
);

const CompanySlide: React.FC<{ co: Company }> = ({ co }) => (
  <Frame footer>
    <div style={{ position: "absolute", top: 96, left: 80, right: 80 }}>
      <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 4, textTransform: "uppercase", color: theme.color.red }}>corporate rap sheet</div>
      <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 116, lineHeight: 0.96, letterSpacing: -2, color: theme.color.textPrimary, textTransform: "uppercase", marginTop: 8 }}>{co.name}</div>
      <div style={{ fontFamily: mono, fontSize: 32, color: theme.color.textSecondary, marginTop: 14 }}>{co.tag}</div>
    </div>
    <div style={{ position: "absolute", top: 420, bottom: 150, left: 80, right: 80, display: "flex", flexDirection: "column", justifyContent: "center" }}>
      {co.cuts.map((c, i) => (
        <CutRow key={i} c={c} />
      ))}
    </div>
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

export const CorpRapSheet: React.FC<Props> = ({ coverTitle, coverSub, companies, ctaHeadline, ctaSub, ctaPersona }) => {
  const i = Math.min(Math.floor(useCurrentFrame()), companies.length + 1);
  if (i === 0) return <Cover title={coverTitle} sub={coverSub} />;
  if (i <= companies.length) return <CompanySlide co={companies[i - 1]} />;
  return <CTA headline={ctaHeadline} sub={ctaSub} persona={ctaPersona} />;
};
