import React from "react";
import { z } from "zod";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono, body } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

const brand = z.object({ name: z.string(), pct: z.number() });
const tier = z.object({ tier: z.string(), color: z.enum(["red", "amber", "blue", "green", "gray"]), brands: z.array(brand) });

export const tierListSchema = z.object({
  title: z.array(z.string()), // *asterisks* → red
  subtitle: z.string(),
  tiers: z.array(tier),
  ctaHeadline: z.string(),
  ctaSub: z.string(),
  ctaPersona: z.string(),
});

type Props = z.infer<typeof tierListSchema>;
type Tier = z.infer<typeof tier>;

const colorOf = (c: Tier["color"]) =>
  c === "red" ? theme.color.red : c === "amber" ? theme.color.amber : c === "blue" ? theme.color.blue : c === "green" ? theme.color.green : theme.color.textTertiary;

const hl = (text: string) =>
  text.split("*").map((s, i) => (i % 2 === 1 ? <span key={i} style={{ color: theme.color.red }}>{s}</span> : <React.Fragment key={i}>{s}</React.Fragment>));

const Frame: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
    <GridTexture opacity={0.06} />
    {children}
  </AbsoluteFill>
);

const Row: React.FC<{ t: Tier }> = ({ t }) => {
  const c = colorOf(t.color);
  return (
    <div style={{ display: "flex", alignItems: "stretch", gap: 18 }}>
      <div style={{ width: 132, minHeight: 132, background: c, borderRadius: 16, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        <span style={{ fontFamily: headline, fontWeight: 700, fontSize: 76, color: t.color === "amber" || t.color === "green" ? "#0a0b0d" : "#fff" }}>{t.tier}</span>
      </div>
      <div style={{ flex: 1, display: "flex", flexWrap: "wrap", alignContent: "center", gap: 14 }}>
        {t.brands.map((b, i) => (
          <div key={i} style={{ display: "flex", alignItems: "baseline", gap: 12, background: theme.color.card, border: `1px solid ${theme.color.border}`, borderRadius: 12, padding: "12px 20px" }}>
            <span style={{ fontFamily: headline, fontWeight: 700, fontSize: 38, color: theme.color.textPrimary }}>{b.name}</span>
            <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 32, color: c }}>−{b.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const TierList: React.FC<Props> = ({ title, subtitle, tiers, ctaHeadline, ctaSub, ctaPersona }) => {
  const slide = Math.floor(useCurrentFrame());
  if (slide >= 1) {
    return (
      <Frame>
        <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
          <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 96, lineHeight: 1.0, letterSpacing: -1, color: theme.color.textPrimary }}>{hl(ctaHeadline)}</div>
          <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 50, color: theme.color.textSecondary, marginTop: 28 }}>{hl(ctaSub)}</div>
          <div style={{ fontFamily: body, fontSize: 36, color: theme.color.textTertiary, marginTop: 38, lineHeight: 1.3 }}>{ctaPersona}</div>
        </AbsoluteFill>
        <div style={{ position: "absolute", bottom: 80, left: 80 }}><Brandmark scale={1.1} /></div>
      </Frame>
    );
  }
  return (
    <Frame>
      <div style={{ position: "absolute", top: 84, left: 80, right: 80 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 70, lineHeight: 1.0, letterSpacing: -1, color: theme.color.textPrimary, textTransform: "uppercase" }}>{title.map((l, i) => <div key={i}>{hl(l)}</div>)}</div>
          <Brandmark scale={1.0} />
        </div>
        <div style={{ fontFamily: mono, fontSize: 28, color: theme.color.textSecondary, marginTop: 10 }}>{subtitle}</div>
      </div>

      <div style={{ position: "absolute", top: 330, bottom: 130, left: 80, right: 80, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
        {tiers.map((t, i) => <Row key={i} t={t} />)}
      </div>

      <div style={{ position: "absolute", bottom: 64, left: 80, fontFamily: mono, fontSize: 28, color: theme.color.textTertiary }}>
        ranked by each brand's biggest documented shrink · fullcarts.org
      </div>
    </Frame>
  );
};
