import React from "react";
import { z } from "zod";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { theme } from "../lib/theme";
import { headline, mono, body } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

// "It's Not You" — the emotional cold-open carousel. Opens on the FEELING, not a
// number (Emotional Lock-In, content-angles.md §4): name the unspoken thought →
// prove it with receipts → resolve with "it's not you." One slide per FRAME:
// opener(0) → feeling(1) → receipts(2..R+1) → resolution(R+2) → CTA(R+3).
// Render stills 0..receipts.length+3.

const receipt = z.object({
  brand: z.string(),
  product: z.string(),
  before: z.number(),
  after: z.number(),
  unit: z.string(),
  pct: z.number(),
});

export const itsNotYouSchema = z.object({
  opener: z.array(z.string()), // big cold-open lines; *asterisks* = red
  feeling: z.string(), // the unspoken thought, said back to them
  receipts: z.array(receipt),
  resolution: z.array(z.string()), // the "it's not you" close; *asterisks* = red
  ctaPersona: z.string(),
});

type Props = z.infer<typeof itsNotYouSchema>;
type Receipt = z.infer<typeof receipt>;

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

const BigText: React.FC<{ lines: string[]; size?: number }> = ({ lines, size = 100 }) => (
  <Frame>
    <div style={{ position: "absolute", top: 90, left: 80 }}><Brandmark scale={1.0} /></div>
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
      {lines.map((line, i) => (
        <div key={i} style={{ fontFamily: headline, fontWeight: 700, fontSize: size, lineHeight: 1.02, letterSpacing: -1, color: theme.color.textPrimary }}>
          {hl(line)}
        </div>
      ))}
    </AbsoluteFill>
  </Frame>
);

const Feeling: React.FC<{ text: string }> = ({ text }) => (
  <Frame footer>
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
      <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 3, textTransform: "uppercase", color: theme.color.textTertiary, marginBottom: 30 }}>you thought…</div>
      <div style={{ fontFamily: headline, fontWeight: 500, fontStyle: "italic", fontSize: 64, lineHeight: 1.18, color: theme.color.textSecondary }}>
        “{text}”
      </div>
    </AbsoluteFill>
  </Frame>
);

const ReceiptSlide: React.FC<{ r: Receipt; idx: number; total: number }> = ({ r, idx, total }) => (
  <Frame footer>
    <div style={{ position: "absolute", top: 110, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
      <div style={{ maxWidth: 760 }}>
        <div style={{ fontFamily: mono, fontSize: 28, letterSpacing: 3, textTransform: "uppercase", color: theme.color.red }}>the receipt</div>
        <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 3, textTransform: "uppercase", color: theme.color.textSecondary, marginTop: 30 }}>{r.brand}</div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 60, lineHeight: 1.02, color: theme.color.textPrimary, marginTop: 4 }}>{r.product}</div>
      </div>
      <span style={{ fontFamily: mono, fontSize: 30, color: theme.color.textTertiary }}>{idx}/{total}</span>
    </div>
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 26, flexWrap: "wrap" }}>
        <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 76, color: theme.color.textTertiary, textDecoration: "line-through" }}>{r.before} {r.unit}</span>
        <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 92, color: theme.color.red }}>{r.after} {r.unit}</span>
      </div>
      <div style={{ marginTop: 34 }}>
        <span style={{ display: "inline-block", background: theme.color.red, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 80, borderRadius: 16, padding: "8px 28px" }}>−{r.pct}%</span>
      </div>
    </AbsoluteFill>
  </Frame>
);

const CTA: React.FC<{ persona: string }> = ({ persona }) => (
  <Frame>
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px" }}>
      <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 92, lineHeight: 1.0, letterSpacing: -1, color: theme.color.textPrimary }}>
        Check {hl("*your*")} cart.
      </div>
      <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 50, color: theme.color.textSecondary, marginTop: 28 }}>
        Search any product — {hl("*free*")} — at fullcarts.org
      </div>
      <div style={{ fontFamily: body, fontSize: 36, color: theme.color.textTertiary, marginTop: 40, lineHeight: 1.3 }}>{persona}</div>
    </AbsoluteFill>
    <div style={{ position: "absolute", bottom: 80, left: 80 }}><Brandmark scale={1.1} /></div>
  </Frame>
);

export const ItsNotYou: React.FC<Props> = ({ opener, feeling, receipts, resolution, ctaPersona }) => {
  const r = receipts.length;
  const last = r + 3;
  const i = Math.min(Math.floor(useCurrentFrame()), last);
  if (i === 0) return <BigText lines={opener} size={112} />;
  if (i === 1) return <Feeling text={feeling} />;
  if (i >= 2 && i <= r + 1) {
    const idx = i - 2;
    return <ReceiptSlide r={receipts[idx]} idx={idx + 1} total={r} />;
  }
  if (i === r + 2) return <BigText lines={resolution} size={92} />;
  return <CTA persona={ctaPersona} />;
};
