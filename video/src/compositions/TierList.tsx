import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono, body } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

const brand = z.object({ name: z.string(), pct: z.number(), logo: z.string().optional() });
const tier = z.object({
  tier: z.string(),
  color: z.enum(["red", "amber", "blue", "green", "gray"]),
  label: z.string().optional(),
  brands: z.array(brand),
});

// Reveal carousel: cover → tiers bottom-up (D…S, one per swipe, building tension)
// → the full list as the payoff LAST slide. Pass tiers worst-first (S…D).
export const tierListSchema = z.object({
  title: z.array(z.string()), // *asterisks* → red
  subtitle: z.string(),
  coverPrompt: z.string(),
  tiers: z.array(tier),
  ctaLine: z.string(),
});

type Props = z.infer<typeof tierListSchema>;
type Tier = z.infer<typeof tier>;

const colorOf = (c: Tier["color"]) =>
  c === "red" ? theme.color.red : c === "amber" ? theme.color.amber : c === "blue" ? theme.color.blue : c === "green" ? theme.color.green : theme.color.textTertiary;
const dark = (c: Tier["color"]) => c === "amber" || c === "green";
const hl = (text: string) =>
  text.split("*").map((s, i) => (i % 2 === 1 ? <span key={i} style={{ color: theme.color.red }}>{s}</span> : <React.Fragment key={i}>{s}</React.Fragment>));

const Frame: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
    <GridTexture opacity={0.06} />
    {children}
  </AbsoluteFill>
);

// brand icon: real logo if provided (DB/Clearbit URL or local path), else a clean monogram chip
const BrandIcon: React.FC<{ logo?: string; name: string; size: number }> = ({ logo, name, size }) => {
  if (logo) {
    const src = logo.startsWith("http") ? logo : staticFile(logo);
    return (
      <div style={{ width: size, height: size, borderRadius: size / 2, background: "#fff", overflow: "hidden", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Img src={src} style={{ width: "84%", height: "84%", objectFit: "contain" }} />
      </div>
    );
  }
  const initial = (name.match(/[A-Za-z0-9]/)?.[0] ?? "?").toUpperCase();
  return (
    <div style={{ width: size, height: size, borderRadius: size / 2, background: "rgba(245,244,240,0.10)", border: `1px solid ${theme.color.border}`, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <span style={{ fontFamily: headline, fontWeight: 700, fontSize: size * 0.48, color: theme.color.textPrimary }}>{initial}</span>
    </div>
  );
};

const BrandPill: React.FC<{ b: z.infer<typeof brand>; color: string; big?: boolean }> = ({ b, color, big }) => (
  <div style={{ display: "flex", alignItems: "center", gap: big ? 14 : 10, background: theme.color.card, border: `1px solid ${theme.color.border}`, borderRadius: big ? 16 : 10, padding: big ? "12px 26px 12px 14px" : "8px 16px 8px 9px" }}>
    <BrandIcon logo={b.logo} name={b.name} size={big ? 56 : 40} />
    <span style={{ fontFamily: headline, fontWeight: 700, fontSize: big ? 46 : 32, color: theme.color.textPrimary }}>{b.name}</span>
    <span style={{ fontFamily: mono, fontWeight: 700, fontSize: big ? 40 : 28, color }}>−{b.pct}%</span>
  </div>
);

const TierBox: React.FC<{ t: Tier; size: number }> = ({ t, size }) => (
  <div style={{ width: size, height: size, background: colorOf(t.color), borderRadius: size * 0.13, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
    <span style={{ fontFamily: headline, fontWeight: 700, fontSize: size * 0.6, color: dark(t.color) ? "#0a0b0d" : "#fff" }}>{t.tier}</span>
  </div>
);

// progress dots across the bottom-up reveal (D … S)
const Progress: React.FC<{ order: Tier[]; current: number }> = ({ order, current }) => (
  <div style={{ display: "flex", gap: 12 }}>
    {order.map((t, i) => (
      <div key={i} style={{ width: 56, height: 56, borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", background: i === current ? colorOf(t.color) : theme.color.card, border: `1px solid ${i === current ? "transparent" : theme.color.border}`, opacity: i <= current ? 1 : 0.45 }}>
        <span style={{ fontFamily: headline, fontWeight: 700, fontSize: 26, color: i === current ? (dark(t.color) ? "#0a0b0d" : "#fff") : theme.color.textSecondary }}>{t.tier}</span>
      </div>
    ))}
  </div>
);

const Cover: React.FC<{ title: string[]; subtitle: string; prompt: string }> = ({ title, subtitle, prompt }) => (
  <Frame>
    <div style={{ position: "absolute", top: 90, left: 80 }}><Brandmark scale={1.15} /></div>
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
      {title.map((l, i) => (
        <div key={i} style={{ fontFamily: headline, fontWeight: 700, fontSize: 118, lineHeight: 0.98, letterSpacing: -2, color: theme.color.textPrimary, textTransform: "uppercase" }}>{hl(l)}</div>
      ))}
      <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 48, color: theme.color.textSecondary, marginTop: 30 }}>{subtitle}</div>
    </AbsoluteFill>
    <div style={{ position: "absolute", bottom: 84, left: 80, right: 80, fontFamily: mono, fontSize: 34, color: theme.color.red, letterSpacing: 1 }}>{prompt} →</div>
  </Frame>
);

const RevealSlide: React.FC<{ order: Tier[]; idx: number }> = ({ order, idx }) => {
  const t = order[idx];
  const c = colorOf(t.color);
  const worst = idx === order.length - 1;
  return (
    <Frame>
      <div style={{ position: "absolute", top: 84, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Progress order={order} current={idx} />
        <Brandmark scale={0.85} />
      </div>

      <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
          <TierBox t={t} size={210} />
          <div>
            <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 4, textTransform: "uppercase", color: theme.color.textSecondary }}>tier {t.tier}</div>
            <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 64, lineHeight: 1.0, color: c }}>{t.label ?? ""}</div>
          </div>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 16, marginTop: 56 }}>
          {t.brands.map((b, i) => <BrandPill key={i} b={b} color={c} big />)}
        </div>
      </AbsoluteFill>

      <div style={{ position: "absolute", bottom: 84, left: 80, right: 80, fontFamily: mono, fontSize: 34, letterSpacing: 1, color: worst ? theme.color.red : theme.color.textSecondary }}>
        {worst ? "🚩 the worst offenders." : "it gets worse → swipe"}
      </div>
    </Frame>
  );
};

const Row: React.FC<{ t: Tier }> = ({ t }) => {
  const c = colorOf(t.color);
  return (
    <div style={{ display: "flex", alignItems: "stretch", gap: 16 }}>
      <TierBox t={t} size={108} />
      <div style={{ flex: 1, display: "flex", flexWrap: "wrap", alignContent: "center", gap: 12 }}>
        {t.brands.map((b, i) => <BrandPill key={i} b={b} color={c} />)}
      </div>
    </div>
  );
};

const FullList: React.FC<{ tiers: Tier[]; cta: string }> = ({ tiers, cta }) => (
  <Frame>
    <div style={{ position: "absolute", top: 84, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 70, letterSpacing: -1, color: theme.color.textPrimary, textTransform: "uppercase" }}>the full list</div>
      <Brandmark scale={1.0} />
    </div>
    <div style={{ position: "absolute", top: 250, bottom: 150, left: 80, right: 80, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
      {tiers.map((t, i) => <Row key={i} t={t} />)}
    </div>
    <div style={{ position: "absolute", bottom: 64, left: 80, right: 80, fontFamily: mono, fontSize: 28, color: theme.color.textTertiary }}>{cta} · fullcarts.org</div>
  </Frame>
);

export const TierList: React.FC<Props> = ({ title, subtitle, coverPrompt, tiers, ctaLine }) => {
  const slide = Math.floor(useCurrentFrame());
  const order = [...tiers].reverse(); // reveal bottom-up: D … S
  if (slide === 0) return <Cover title={title} subtitle={subtitle} prompt={coverPrompt} />;
  if (slide <= order.length) return <RevealSlide order={order} idx={slide - 1} />;
  return <FullList tiers={tiers} cta={ctaLine} />;
};
