import React from "react";
import {
  AbsoluteFill, Img, Sequence, staticFile, useCurrentFrame, useVideoConfig,
  spring, interpolate, Easing,
} from "remotion";
import { z } from "zod";
import { theme } from "../lib/theme";
import { headline, mono, body } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";
import { corpRapSheetSchema } from "./CorpRapSheet";

// Animated vertical (1080×1920) cut of the Corporate Rap Sheet carousel for
// Shorts / Reels / TikTok. Same props as CorpRapSheet. Cover → 5 companies → CTA,
// each scene animated: tier-stamp slam, staggered rows, real-time shrinking bars,
// popping % chips, slide-in transitions.
export { corpRapSheetSchema as corpRapSheetVideoSchema };
type Props = z.infer<typeof corpRapSheetSchema>;
type Company = Props["companies"][number];
type Cut = Company["cuts"][number];

const COVER = 78;
const CO = 132;
const CTA = 96;

export const calcCorpRapSheetVideoMeta = ({ props }: { props: Props }) => ({
  durationInFrames: COVER + props.companies.length * CO + CTA,
});

const TIER_COLORS: Record<string, string> = {
  S: theme.color.red, A: theme.color.amber, B: theme.color.blue,
  C: theme.color.green, D: theme.color.textTertiary,
};
const hl = (text: string) =>
  text.split("*").map((s, i) =>
    i % 2 === 1 ? <span key={i} style={{ color: theme.color.red }}>{s}</span> : <React.Fragment key={i}>{s}</React.Fragment>
  );
const resolve = (s?: string) => (s ? (s.startsWith("http") ? s : staticFile(s)) : null);

const Shell: React.FC<{ children: React.ReactNode; footer?: boolean }> = ({ children, footer }) => (
  <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
    <GridTexture opacity={0.06} />
    {children}
    {footer && (
      <div style={{ position: "absolute", bottom: 90, left: 90, right: 90, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontFamily: mono, fontSize: 32, color: theme.color.textTertiary }}>every figure sourced · fullcarts.org</span>
        <Brandmark scale={1.0} />
      </div>
    )}
  </AbsoluteFill>
);

// shared "scene enters by pushing up + fading" wrapper
const SceneEnter: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: f, fps, config: { damping: 200, mass: 0.6, stiffness: 110 } });
  const y = interpolate(s, [0, 1], [70, 0]);
  const op = interpolate(f, [0, 10], [0, 1], { extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ transform: `translateY(${y}px)`, opacity: op }}>{children}</AbsoluteFill>;
};

const Thumb: React.FC<{ src?: string; brand: string; appear: number }> = ({ src, brand, appear }) => {
  const r = resolve(src);
  const common: React.CSSProperties = {
    width: 210, height: 210, flexShrink: 0, borderRadius: 24, overflow: "hidden",
    transform: `scale(${appear})`,
  };
  if (r) return <div style={{ ...common, background: "#fff" }}><Img src={r} style={{ width: "100%", height: "100%", objectFit: "contain" }} /></div>;
  return (
    <div style={{ ...common, background: `${theme.color.textTertiary}22`, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <span style={{ fontFamily: headline, fontWeight: 700, fontSize: 96, color: theme.color.textTertiary }}>{brand.slice(0, 1)}</span>
    </div>
  );
};

const Row: React.FC<{ c: Cut; start: number }> = ({ c, start }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  // row slides in
  const enter = spring({ frame: f - start, fps, config: { damping: 200, mass: 0.5, stiffness: 120 } });
  const rowY = interpolate(enter, [0, 1], [50, 0]);
  const rowOp = interpolate(f - start, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // bar shrinks from full -> after/before
  const barStart = start + 8;
  const p = interpolate(f, [barStart, barStart + 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const fill = (1 - p * (1 - c.after / c.before)) * 100;
  // chip pops + counts up after the shrink
  const chipStart = barStart + 22;
  const chipS = spring({ frame: f - chipStart, fps, config: { damping: 9, mass: 0.6, stiffness: 150 } });
  const chipScale = f < chipStart ? 0 : interpolate(chipS, [0, 1], [0.2, 1]);
  const pctVal = interpolate(f, [barStart, chipStart], [0, c.pct], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const thumbScale = interpolate(enter, [0, 1], [0.7, 1]);

  return (
    <div style={{ transform: `translateY(${rowY}px)`, opacity: rowOp, borderTop: `1px solid ${theme.color.textTertiary}33`, padding: "30px 0", display: "flex", alignItems: "center", gap: 34 }}>
      <Thumb src={c.image} brand={c.brand} appear={thumbScale} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 20 }}>
          <span style={{ fontFamily: headline, fontWeight: 700, fontSize: 62, color: theme.color.textPrimary, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.brand}</span>
          <div style={{ background: theme.color.red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 52, borderRadius: 16, padding: "6px 22px", whiteSpace: "nowrap", flexShrink: 0, transform: `scale(${chipScale})` }}>−{pctVal.toFixed(1)}%</div>
        </div>
        <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 44, color: theme.color.textSecondary, marginTop: 10 }}>{c.before} → {c.after} {c.unit}</div>
        <div style={{ marginTop: 16, height: 22, background: `${theme.color.textTertiary}22`, borderRadius: 8, overflow: "hidden" }}>
          <div style={{ width: `${fill}%`, height: "100%", background: theme.color.red, borderRadius: 8 }} />
        </div>
      </div>
    </div>
  );
};

const TierStamp: React.FC<{ tier: string; label: string }> = ({ tier, label }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const start = 6;
  const s = spring({ frame: f - start, fps, config: { damping: 8, mass: 0.8, stiffness: 130 } });
  const scale = f < start ? 0 : interpolate(s, [0, 1], [1.8, 1]);
  const rot = f < start ? -12 : interpolate(s, [0, 1], [-12, 0]);
  const color = TIER_COLORS[tier] ?? theme.color.textTertiary;
  return (
    <div style={{ position: "absolute", top: 150, right: 80, display: "flex", flexDirection: "column", alignItems: "center", width: 230 }}>
      <div style={{ width: 200, height: 200, background: color, borderRadius: 32, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${scale}) rotate(${rot}deg)`, boxShadow: `0 0 0 5px ${color}33` }}>
        <span style={{ fontFamily: headline, fontWeight: 700, fontSize: 150, lineHeight: 1, color: theme.color.textPrimary }}>{tier}</span>
      </div>
      <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 28, letterSpacing: 1.5, textTransform: "uppercase", color, marginTop: 16, textAlign: "center", lineHeight: 1.15, opacity: interpolate(f, [start + 6, start + 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{label}</div>
    </div>
  );
};

const CompanyScene: React.FC<{ co: Company }> = ({ co }) => {
  const f = useCurrentFrame();
  const nameX = interpolate(f, [2, 18], [-60, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const nameOp = interpolate(f, [2, 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const tagOp = interpolate(f, [18, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <Shell footer>
      <div style={{ position: "absolute", top: 70, left: 90 }}><Brandmark scale={1.1} /></div>
      <TierStamp tier={co.tier} label={co.tierLabel} />
      <div style={{ position: "absolute", top: 200, left: 90, right: 340, transform: `translateX(${nameX}px)`, opacity: nameOp }}>
        <div style={{ fontFamily: mono, fontSize: 34, letterSpacing: 5, textTransform: "uppercase", color: theme.color.red }}>corporate rap sheet</div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 128, lineHeight: 0.94, letterSpacing: -2, color: theme.color.textPrimary, textTransform: "uppercase", marginTop: 10 }}>{co.name}</div>
      </div>
      <div style={{ position: "absolute", top: 470, left: 90, right: 90, fontFamily: mono, fontSize: 36, color: theme.color.textSecondary, lineHeight: 1.35, opacity: tagOp }}>
        <span style={{ color: theme.color.textPrimary, fontWeight: 700 }}>{co.brands}</span> of their brands caught shrinking in the FullCarts database — here are {co.cuts.length}:
      </div>
      <div style={{ position: "absolute", top: 640, left: 90, right: 90 }}>
        {co.cuts.map((c, i) => (
          <Row key={i} c={c} start={30 + i * 14} />
        ))}
      </div>
    </Shell>
  );
};

const CoverScene: React.FC<{ title: string[]; sub: string }> = ({ title, sub }) => {
  const f = useCurrentFrame();
  const swipeOp = interpolate(f % 40, [0, 20, 40], [0.35, 1, 0.35]);
  return (
    <Shell>
      <div style={{ position: "absolute", top: 110, left: 90 }}><Brandmark scale={1.3} /></div>
      <AbsoluteFill style={{ justifyContent: "center", padding: "0 90px" }}>
        {title.map((line, i) => {
          const st = 4 + i * 7;
          const op = interpolate(f, [st, st + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const y = interpolate(f, [st, st + 12], [50, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={i} style={{ fontFamily: headline, fontWeight: 700, fontSize: 156, lineHeight: 0.98, letterSpacing: -3, color: theme.color.textPrimary, textTransform: "uppercase", opacity: op, transform: `translateY(${y}px)` }}>{hl(line)}</div>
          );
        })}
        <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 52, color: theme.color.textSecondary, marginTop: 44, opacity: interpolate(f, [28, 42], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{sub}</div>
      </AbsoluteFill>
      <div style={{ position: "absolute", bottom: 130, right: 90, fontFamily: mono, fontSize: 40, color: theme.color.red, letterSpacing: 2, opacity: swipeOp }}>watch →</div>
    </Shell>
  );
};

const CTAScene: React.FC<{ headline: string; sub: string; persona: string }> = ({ headline: h, sub, persona }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame: f, fps, config: { damping: 12, mass: 0.7, stiffness: 120 } });
  return (
    <Shell>
      <AbsoluteFill style={{ justifyContent: "center", padding: "0 90px" }}>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 116, lineHeight: 1.0, letterSpacing: -1, color: theme.color.textPrimary, transform: `scale(${interpolate(pop, [0, 1], [0.9, 1])})`, transformOrigin: "left" }}>{hl(h)}</div>
        <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 60, color: theme.color.textSecondary, marginTop: 36, opacity: interpolate(f, [10, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{hl(sub)}</div>
        <div style={{ fontFamily: body, fontSize: 42, color: theme.color.textTertiary, marginTop: 48, lineHeight: 1.3, opacity: interpolate(f, [20, 34], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{persona}</div>
      </AbsoluteFill>
      <div style={{ position: "absolute", bottom: 120, left: 90 }}><Brandmark scale={1.3} /></div>
    </Shell>
  );
};

export const CorpRapSheetVideo: React.FC<Props> = ({ coverTitle, coverSub, companies, ctaHeadline, ctaSub, ctaPersona }) => (
  <AbsoluteFill style={{ background: theme.color.bg }}>
    <Sequence from={0} durationInFrames={COVER}><SceneEnter><CoverScene title={coverTitle} sub={coverSub} /></SceneEnter></Sequence>
    {companies.map((co, i) => (
      <Sequence key={i} from={COVER + i * CO} durationInFrames={CO}>
        <SceneEnter><CompanyScene co={co} /></SceneEnter>
      </Sequence>
    ))}
    <Sequence from={COVER + companies.length * CO} durationInFrames={CTA}>
      <SceneEnter><CTAScene headline={ctaHeadline} sub={ctaSub} persona={ctaPersona} /></SceneEnter>
    </Sequence>
  </AbsoluteFill>
);
