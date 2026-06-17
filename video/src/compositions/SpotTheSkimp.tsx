import React from "react";
import { z } from "zod";
import {
  AbsoluteFill,
  Img,
  Sequence,
  staticFile,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { enter } from "../lib/anim";
import { GridTexture } from "../components/GridTexture";
import { Brandmark } from "../components/Brandmark";

// ──────────────────────────────────────────────────────────────────────────
// "Spot the Skimp: Easy → Impossible" — full-frame BACKGROUND b-roll track.
// The creator embeds their own talking head + captions on top in their editor,
// so this composition leaves the bottom ~1/3 of the frame clean (the house
// layout law) and never bakes in audio.
//
// This is NOT a size-delta cutaway (ShrinkCutaway / GuessTheCut are −%-driven).
// These are evidence photos where the difference is SPOTTABLE but not a clean
// measured shrink — so reveals are OBSERVATIONAL ("shorter bar", "thinner
// strips"), never a fabricated number. On-screen figures are limited to ones
// that are spoken in the VO or printed on the pack (2 oz, 24 ct, 12.4 oz,
// "75% MORE"). Three-bucket safe: every panel shows a REAL photo; the only
// synthetic elements are the game UI (stars / labels).
// ──────────────────────────────────────────────────────────────────────────

const difficulty = z.enum(["easy", "medium", "hard", "impossible"]);

const roundSchema = z.object({
  level: z.string(), // "LEVEL 1", "ROUND 2", "FINAL BOSS"
  difficulty,
  stars: z.number().int().min(1).max(5),
  brand: z.string(),
  product: z.string(),
  image: z.string(), // public/ path
  imagePos: z.string().optional(),
  question: z.string(), // shown during the guess window
  reveal: z.string(), // shown after revealAtSec; wrap a word in *asterisks* to highlight
  chip: z.string().optional(), // small mono fact pill (spoken / on-pack only)
  fromSec: z.number(),
  toSec: z.number(),
  revealAtSec: z.number(),
  trick: z.boolean().default(false), // Cheez-It "no skimp" buzzer treatment
  trickTags: z.array(z.string()).default([]),
});

const outroItem = z.object({ image: z.string(), stars: z.number().int(), label: z.string() });

export const spotTheSkimpSchema = z.object({
  durationSec: z.number().default(78.9),
  reservedTop: z.number().default(1320), // everything below this y stays clean for the head
  hook: z.object({
    titleLines: z.array(z.string()),
    sub: z.string(),
    line: z.string(),
    images: z.array(z.string()),
    toSec: z.number(),
  }),
  rounds: z.array(roundSchema),
  outro: z.object({
    headlineLines: z.array(z.string()),
    items: z.array(outroItem),
    followLine: z.string(),
    scoreLine: z.string(),
    fromSec: z.number(),
  }),
});

type Props = z.infer<typeof spotTheSkimpSchema>;
type Round = z.infer<typeof roundSchema>;

// ── helpers ────────────────────────────────────────────────────────────────
const accentForDifficulty = (d: z.infer<typeof difficulty>): string =>
  d === "easy"
    ? theme.color.green
    : d === "medium"
    ? theme.color.amber
    : d === "hard"
    ? theme.color.redBright
    : theme.color.red;

const hl = (text: string, accent: string) =>
  text.split("*").map((s, i) =>
    i % 2 === 1 ? (
      <span key={i} style={{ color: accent }}>{s}</span>
    ) : (
      <React.Fragment key={i}>{s}</React.Fragment>
    )
  );

const span = (fromSec: number, toSec: number, fps: number) => ({
  from: Math.round(fromSec * fps),
  durationInFrames: Math.max(1, Math.round((toSec - fromSec) * fps)),
});

// Star drawn as an SVG polygon — robust regardless of which glyphs the embedded
// fonts ship (★ would tofu under the base64 faces).
const STAR_PTS = "50,4 61,37 97,38 68,59 79,94 50,72 21,94 32,59 3,38 39,37";
const Star: React.FC<{ size: number; on: boolean; accent: string; p?: number }> = ({ size, on, accent, p = 1 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" style={{ transform: `scale(${0.6 + 0.4 * p})`, opacity: p }}>
    <polygon
      points={STAR_PTS}
      fill={on ? accent : "transparent"}
      stroke={on ? accent : theme.color.textTertiary}
      strokeWidth={on ? 0 : 6}
    />
  </svg>
);

const StarMeter: React.FC<{ filled: number; accent: string; size?: number; frame: number; fps: number }> = ({
  filled,
  accent,
  size = 56,
  frame,
  fps,
}) => (
  <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
    {[0, 1, 2, 3, 4].map((i) => (
      <Star key={i} size={size} on={i < filled} accent={accent} p={i < filled ? enter(frame, fps, { delay: 6 + i * 4, durationInFrames: 12 }) : 1} />
    ))}
  </div>
);

const Shell: React.FC<{ accent?: string; children: React.ReactNode }> = ({ accent, children }) => (
  <AbsoluteFill style={{ background: theme.color.bg, fontFamily: body }}>
    <GridTexture opacity={0.06} />
    {accent ? <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 30%, ${accent}1c 0%, transparent 55%)` }} /> : null}
    <div style={{ position: "absolute", top: 250, right: 60 }}><Brandmark scale={0.85} /></div>
    {children}
  </AbsoluteFill>
);

const PhotoCard: React.FC<{ src: string; pos?: string; p: number; ring?: string }> = ({ src, pos, p, ring }) => (
  <div
    style={{
      position: "absolute",
      top: 600,
      left: 110,
      right: 110,
      height: 540,
      borderRadius: 24,
      overflow: "hidden",
      background: "#fff",
      border: ring ? `4px solid ${ring}` : `1px solid ${theme.color.border}`,
      boxShadow: `0 22px 60px rgba(0,0,0,0.55)${ring ? `, 0 0 ${Math.round(p * 60)}px ${ring}66` : ""}`,
      opacity: p,
      transform: `translateY(${interpolate(p, [0, 1], [26, 0])}px) scale(${interpolate(p, [0, 1], [0.96, 1])})`,
    }}
  >
    <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "contain", objectPosition: pos ?? "center" }} />
  </div>
);

// ── per-round panel ──────────────────────────────────────────────────────
const RoundPanel: React.FC<{ r: Round; idx: number; total: number }> = ({ r, idx, total }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = accentForDifficulty(r.difficulty);

  const head = enter(frame, fps, { durationInFrames: 12 });
  const photo = enter(frame, fps, { delay: 6, durationInFrames: 20 });

  const revealFrame = Math.round((r.revealAtSec - r.fromSec) * fps);
  const revealed = frame >= revealFrame;
  const revP = enter(frame, fps, { delay: revealFrame, durationInFrames: 12 });
  // slow Ken-Burns zoom during the guess window to pull the eye to the photo
  const ring = revealed ? accent : undefined;

  // trick buzzer flash
  const flash = r.trick && revealed ? 0.5 + 0.5 * Math.abs(Math.sin((frame - revealFrame) / 4)) : 1;

  return (
    <Shell accent={accent}>
      {/* kicker + progress */}
      <div style={{ position: "absolute", top: 258, left: 60, opacity: head }}>
        <span style={{ fontFamily: mono, fontSize: 26, letterSpacing: 5, textTransform: "uppercase", color: theme.color.textTertiary }}>
          Spot the Skimp · {idx}/{total}
        </span>
      </div>

      {/* difficulty + stars */}
      <div style={{ position: "absolute", top: 312, left: 60, right: 60, opacity: head, transform: `translateY(${interpolate(head, [0, 1], [16, 0])}px)` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
          <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 44, letterSpacing: 2, textTransform: "uppercase", color: accent }}>
            {r.level}
          </span>
          <span style={{ fontFamily: mono, fontSize: 34, letterSpacing: 4, textTransform: "uppercase", color: theme.color.textSecondary }}>
            {r.difficulty}
          </span>
        </div>
        <div style={{ marginTop: 18 }}>
          <StarMeter filled={r.stars} accent={accent} frame={frame} fps={fps} />
        </div>
      </div>

      {/* brand + product */}
      <div style={{ position: "absolute", top: 462, left: 60, right: 60, opacity: head }}>
        <div style={{ fontFamily: mono, fontSize: 28, letterSpacing: 5, textTransform: "uppercase", color: theme.color.textTertiary }}>{r.brand}</div>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 58, lineHeight: 1.0, color: theme.color.textPrimary, marginTop: 4 }}>{r.product}</div>
      </div>

      <PhotoCard src={r.image} pos={r.imagePos} p={photo} ring={ring} />

      {/* question / reveal band */}
      <div style={{ position: "absolute", top: 1168, left: 80, right: 80, textAlign: "center" }}>
        {!revealed ? (
          <div style={{ opacity: head }}>
            <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 60, lineHeight: 1.06, color: theme.color.textPrimary }}>
              {hl(r.question, accent)}
            </div>
          </div>
        ) : r.trick ? (
          <div style={{ opacity: revP, transform: `translateY(${interpolate(revP, [0, 1], [16, 0])}px)` }}>
            <div style={{ display: "inline-block", background: accent, color: theme.color.textPrimary, fontFamily: mono, fontWeight: 700, fontSize: 40, letterSpacing: 4, borderRadius: 12, padding: "8px 22px", opacity: flash }}>
              TRICK — NO SKIMP
            </div>
            <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 56, lineHeight: 1.08, color: theme.color.textPrimary, marginTop: 18 }}>
              {hl(r.reveal, accent)}
            </div>
            <div style={{ display: "flex", gap: 14, justifyContent: "center", marginTop: 20, flexWrap: "wrap" }}>
              {r.trickTags.map((t, i) => (
                <span key={i} style={{ fontFamily: mono, fontWeight: 700, fontSize: 28, letterSpacing: 2, color: accent, border: `2px solid ${accent}`, borderRadius: 10, padding: "6px 16px", textTransform: "uppercase" }}>{t}</span>
              ))}
            </div>
          </div>
        ) : (
          <div style={{ opacity: revP, transform: `translateY(${interpolate(revP, [0, 1], [16, 0])}px)` }}>
            <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 64, lineHeight: 1.05, color: theme.color.textPrimary }}>
              {hl(r.reveal, accent)}
            </div>
            {r.chip ? (
              <div style={{ marginTop: 22 }}>
                <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 28, letterSpacing: 3, color: theme.color.textSecondary, border: `1px solid ${theme.color.border}`, borderRadius: 10, padding: "6px 18px", textTransform: "uppercase" }}>{r.chip}</span>
              </div>
            ) : null}
          </div>
        )}
        {/* the question's chip stays visible during the guess window too */}
        {!revealed && r.chip ? (
          <div style={{ marginTop: 22, opacity: head }}>
            <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 28, letterSpacing: 3, color: theme.color.textSecondary, border: `1px solid ${theme.color.border}`, borderRadius: 10, padding: "6px 18px", textTransform: "uppercase" }}>{r.chip}</span>
          </div>
        ) : null}
      </div>
    </Shell>
  );
};

// ── thumbnail grid (hook montage + outro recap) ──────────────────────────
const ThumbGrid: React.FC<{ items: { image: string; stars?: number; label?: string }[]; top: number; frame: number; fps: number; showStars?: boolean }> = ({ items, top, frame, fps, showStars }) => {
  const COLS = 3;
  const CW = 280;
  const CH = 224;
  const GAP = 20;
  const gridW = COLS * CW + (COLS - 1) * GAP;
  const left = (1080 - gridW) / 2;
  return (
    <>
      {items.map((it, i) => {
        const col = i % COLS;
        const row = Math.floor(i / COLS);
        const p = enter(frame, fps, { delay: 4 + i * 3, durationInFrames: 14 });
        return (
          <div key={i} style={{ position: "absolute", left: left + col * (CW + GAP), top: top + row * (CH + (showStars ? 64 : GAP)), width: CW, opacity: p, transform: `translateY(${interpolate(p, [0, 1], [18, 0])}px)` }}>
            <div style={{ width: CW, height: CH, borderRadius: 14, overflow: "hidden", background: "#fff", border: `1px solid ${theme.color.border}` }}>
              <Img src={staticFile(it.image)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            </div>
            {showStars ? (
              <div style={{ display: "flex", gap: 4, justifyContent: "center", marginTop: 10 }}>
                {[0, 1, 2, 3, 4].map((s) => (
                  <Star key={s} size={26} on={s < (it.stars ?? 0)} accent={theme.color.amber} />
                ))}
              </div>
            ) : null}
          </div>
        );
      })}
    </>
  );
};

const HookPanel: React.FC<{ hook: Props["hook"] }> = ({ hook }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = enter(frame, fps, { durationInFrames: 14 });
  return (
    <Shell accent={theme.color.red}>
      <div style={{ position: "absolute", top: 300, left: 60, right: 60, opacity: t, transform: `translateY(${interpolate(t, [0, 1], [20, 0])}px)` }}>
        <div style={{ fontFamily: mono, fontSize: 30, letterSpacing: 6, textTransform: "uppercase", color: theme.color.red }}>the game</div>
        {hook.titleLines.map((l, i) => (
          <div key={i} style={{ fontFamily: headline, fontWeight: 700, fontSize: 132, lineHeight: 0.94, letterSpacing: -2, color: theme.color.textPrimary, textTransform: "uppercase" }}>{l}</div>
        ))}
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginTop: 26 }}>
          <span style={{ fontFamily: mono, fontWeight: 700, fontSize: 40, letterSpacing: 3, color: theme.color.amber, textTransform: "uppercase" }}>{hook.sub}</span>
        </div>
        <div style={{ marginTop: 18 }}>
          <StarMeter filled={5} accent={theme.color.red} size={48} frame={frame} fps={fps} />
        </div>
        <div style={{ fontFamily: headline, fontWeight: 500, fontSize: 42, color: theme.color.textSecondary, marginTop: 24 }}>{hook.line}</div>
      </div>
      <ThumbGrid items={hook.images.map((image) => ({ image }))} top={846} frame={frame} fps={fps} />
    </Shell>
  );
};

const OutroPanel: React.FC<{ outro: Props["outro"] }> = ({ outro }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = enter(frame, fps, { durationInFrames: 14 });
  return (
    <Shell accent={theme.color.red}>
      <div style={{ position: "absolute", top: 250, left: 60, right: 60, opacity: t, transform: `translateY(${interpolate(t, [0, 1], [18, 0])}px)` }}>
        {outro.headlineLines.map((l, i) => (
          <div key={i} style={{ fontFamily: headline, fontWeight: 700, fontSize: 70, lineHeight: 1.0, letterSpacing: -1, color: theme.color.textPrimary, textTransform: "uppercase" }}>{hl(l, theme.color.red)}</div>
        ))}
      </div>
      <ThumbGrid items={outro.items} top={560} frame={frame} fps={fps} showStars />
      <div style={{ position: "absolute", top: 1180, left: 60, right: 60, textAlign: "center" }}>
        <div style={{ fontFamily: headline, fontWeight: 700, fontSize: 64, color: theme.color.red, opacity: enter(frame, fps, { delay: 18, durationInFrames: 12 }) }}>{outro.followLine}</div>
        <div style={{ fontFamily: mono, fontWeight: 700, fontSize: 34, letterSpacing: 2, color: theme.color.textSecondary, marginTop: 14, opacity: enter(frame, fps, { delay: 24, durationInFrames: 12 }) }}>{outro.scoreLine}</div>
      </div>
    </Shell>
  );
};

export const calcSpotMeta = ({ props }: { props: Props }) => ({
  durationInFrames: Math.max(1, Math.round(props.durationSec * 30)),
  fps: 30,
  width: 1080,
  height: 1920,
});

export const SpotTheSkimp: React.FC<Props> = ({ hook, rounds, outro }) => {
  const { fps } = useVideoConfig();
  const total = rounds.length;
  return (
    <AbsoluteFill style={{ background: theme.color.bg }}>
      <Sequence {...span(0, hook.toSec, fps)}>
        <HookPanel hook={hook} />
      </Sequence>
      {rounds.map((r, i) => (
        <Sequence key={i} {...span(r.fromSec, r.toSec, fps)}>
          <RoundPanel r={r} idx={i + 1} total={total} />
        </Sequence>
      ))}
      <Sequence from={Math.round(outro.fromSec * fps)}>
        <OutroPanel outro={outro} />
      </Sequence>
    </AbsoluteFill>
  );
};
