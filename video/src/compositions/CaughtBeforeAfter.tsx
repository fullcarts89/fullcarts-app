import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono, body } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

// "Caught Before/After" — single-product deep-dive carousel; the static companion to
// the Wednesday `Caught:` video (cross-format reinforcement). One slide per FRAME:
// cover(0, just the product — "notice anything?") → the size cut(1) → the per-unit price
// math(2) → the source/receipt(3) → CTA(4). STUB: the price-math slide is wired but the
// unit-price figure is thin in the DB — pass it explicitly or it's omitted.
//
// Bucket-1 note: `image` should be a real product photo (product_entities.image_url);
// falls back to a typographic panel if absent (sandbox can't fetch image hosts — renders
// on a network-open machine).

export const caughtBeforeAfterSchema = z.object({
  brand: z.string(),
  product: z.string(),
  before: z.number(),
  after: z.number(),
  unit: z.string(),
  pct: z.number(),
  pricePerUnitBefore: z.string().optional(), // e.g. "$0.21/oz"
  pricePerUnitAfter: z.string().optional(), // e.g. "$0.25/oz"
  sourceLabel: z.string(), // e.g. "Reddit + retailer listing, observed 2025-10"
  image: z.string().optional(),
  imagePos: z.string().optional(),
});

type Props = z.infer<typeof caughtBeforeAfterSchema>;

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

const ProductPanel: React.FC<{ image?: string; imagePos?: string }> = ({ image, imagePos }) => {
  if (!image) return null;
  const src = image.startsWith("http") ? image : staticFile(image);
  return (
    <div style={{ position: "absolute", right: 80, top: 360, width: 420, height: 560, background: "#fff", borderRadius: 22, overflow: "hidden" }}>
      <Img src={src} style={{ width: "100%", height: "100%", objectFit: "contain", objectPosition: imagePos ?? "center" }} />
    </div>
  );
};

export const CaughtBeforeAfter: React.FC<Props> = (p) => {
  const i = Math.min(Math.floor(useCurrentFrame()), 4);
  const eyebrow = (t: string, color: string = theme.color.red) => (
    <div style={{ fontFamily: mono, fontSize: 28, letterSpacing: 3, textTransform: "uppercase", color }}>{t}</div>
  );
  const head = (
    <div style={{ position: "absolute", top: 110, left: 80, right: 80 }}>
      <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 3, textTransform: "uppercase", color: theme.color.textSecondary }}>caught: {p.brand}</div>
      <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 60, color: theme.color.textPrimary, marginTop: 4, maxWidth: 760 }}>{p.product}</div>
    </div>
  );

  // 0 — cover: just the product
  if (i === 0) {
    return (
      <Frame>
        <div style={{ position: "absolute", top: 90, left: 80 }}><Brandmark scale={1.15} /></div>
        <ProductPanel image={p.image} imagePos={p.imagePos} />
        <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px", paddingRight: p.image ? 540 : 80 }}>
          <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 104, lineHeight: 1.0, letterSpacing: -1, color: theme.color.textPrimary }}>
            Same price.<br />Same shelf.<br /><span style={{ color: theme.color.red }}>Smaller box.</span>
          </div>
          <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 46, color: theme.color.textSecondary, marginTop: 30 }}>Here's {p.brand}. <span style={{ color: theme.color.red, fontFamily: mono }}>swipe →</span></div>
        </AbsoluteFill>
      </Frame>
    );
  }
  // 1 — the cut
  if (i === 1) {
    return (
      <Frame footer>
        {head}
        <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
          {eyebrow("the cut")}
          <div style={{ display: "flex", alignItems: "baseline", gap: 26, marginTop: 18, flexWrap: "wrap" }}>
            <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 80, color: theme.color.textTertiary, textDecoration: "line-through" }}>{p.before} {p.unit}</span>
            <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 96, color: theme.color.red }}>{p.after} {p.unit}</span>
          </div>
          <div style={{ marginTop: 34 }}>
            <span style={{ display: "inline-block", background: theme.color.red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 88, borderRadius: 18, padding: "10px 30px" }}>−{p.pct}%</span>
          </div>
        </AbsoluteFill>
      </Frame>
    );
  }
  // 2 — the price math (per-unit)
  if (i === 2) {
    return (
      <Frame footer>
        {head}
        <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
          {eyebrow("the math they hide")}
          {p.pricePerUnitBefore && p.pricePerUnitAfter ? (
            <div style={{ display: "flex", alignItems: "baseline", gap: 26, marginTop: 20, flexWrap: "wrap" }}>
              <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 72, color: theme.color.textTertiary }}>{p.pricePerUnitBefore}</span>
              <span style={{ fontFamily: mono, fontSize: 60, color: theme.color.textTertiary }}>→</span>
              <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 96, color: theme.color.red }}>{p.pricePerUnitAfter}</span>
            </div>
          ) : (
            <div style={{ fontFamily: headline, fontWeight: 600, fontSize: 56, color: theme.color.textPrimary, marginTop: 20, lineHeight: 1.15 }}>
              Same shelf price. Fewer {p.unit}. The price-per-{p.unit} quietly went up.
            </div>
          )}
          <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 44, color: theme.color.textSecondary, marginTop: 34 }}>A smaller pack at the same price <span style={{ color: theme.color.red }}>is</span> a price hike — hidden.</div>
        </AbsoluteFill>
      </Frame>
    );
  }
  // 3 — the receipt / source
  if (i === 3) {
    return (
      <Frame footer>
        {head}
        <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
          {eyebrow("the receipt", theme.color.textSecondary)}
          <div style={{ fontFamily: headline, fontWeight: 600, fontSize: 58, color: theme.color.textPrimary, marginTop: 20, lineHeight: 1.15 }}>{p.sourceLabel}</div>
          <div style={{ fontFamily: mono, fontSize: 34, color: theme.color.textSecondary, marginTop: 34 }}>Look it up yourself → fullcarts.org</div>
        </AbsoluteFill>
      </Frame>
    );
  }
  // 4 — CTA
  return (
    <Frame>
      <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 92, lineHeight: 1.02, letterSpacing: -1, color: theme.color.textPrimary }}>I catch the <span style={{ color: theme.color.red }}>next</span> one.</div>
        <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 50, color: theme.color.textSecondary, marginTop: 28 }}>Follow + search any product, free, at fullcarts.org</div>
      </AbsoluteFill>
      <div style={{ position: "absolute", bottom: 80, left: 80 }}><Brandmark scale={1.1} /></div>
    </Frame>
  );
};
