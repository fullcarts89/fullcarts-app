import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {theme} from '../theme';

const GROTESK = '"Space Grotesk", sans-serif';
const MONO = '"JetBrains Mono", monospace';

// Signature overlays from the FullCarts content style board
// (contentstyleboard.html). The board mocks at 248px phone width = 1080 real,
// so positions/sizes here are board values × 4.355, then nudged for the
// platform safe zones (right ~12% = like rail, bottom ~15% = caption UI).

export const FCMini: React.FC = () => (
  <div style={{display: 'flex', alignItems: 'center', gap: 16}}>
    <div
      style={{
        width: 88,
        height: 88,
        borderRadius: 22,
        background: theme.red,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: MONO,
        fontWeight: 700,
        fontSize: 40,
        color: '#fff',
      }}
    >
      FC
    </div>
    <span style={{fontFamily: GROTESK, fontWeight: 700, fontSize: 50, color: theme.text}}>
      FullCarts
    </span>
  </div>
);

// "Caught:" cold-open — the sonic-logo moment. Label slides in, brand pops,
// red bar wipes.
export const CaughtTitle: React.FC<{brand: string}> = ({brand}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const labelIn = spring({frame, fps, config: {damping: 18}});
  const brandIn = spring({frame: frame - fps * 0.12, fps, config: {damping: 11, mass: 0.6}});
  const barIn = spring({frame: frame - fps * 0.26, fps, config: {damping: 16}});

  return (
    <div style={{position: 'absolute', inset: 0}}>
      <div
        style={{
          position: 'absolute',
          top: 322,
          left: 105,
          fontFamily: MONO,
          fontSize: 57,
          letterSpacing: 30,
          textTransform: 'uppercase',
          color: theme.red,
          opacity: labelIn,
          transform: `translateX(${interpolate(labelIn, [0, 1], [-100, 0])}px)`,
        }}
      >
        Caught
      </div>
      <div
        style={{
          position: 'absolute',
          top: 400,
          left: 96,
          fontFamily: GROTESK,
          fontWeight: 700,
          fontSize: 200,
          lineHeight: 1,
          color: theme.text,
          opacity: brandIn,
          transform: `scale(${interpolate(brandIn, [0, 1], [0.62, 1])})`,
          transformOrigin: 'left center',
          textShadow: '0 4px 0 #000, 0 0 26px rgba(0,0,0,0.9)',
        }}
      >
        {brand}
      </div>
      <div
        style={{
          position: 'absolute',
          top: 660,
          left: 105,
          width: 523,
          height: 35,
          borderRadius: 17,
          background: theme.red,
          transform: `scaleX(${barIn})`,
          transformOrigin: 'left center',
        }}
      />
    </div>
  );
};

// The signature data card: brand/product, −X% badge, before/after bars,
// source line + FC mark. Replaces plain strike/counter callouts.
export const ShrinkOverlay: React.FC<{
  brand: string;
  product: string;
  sizeBefore: number;
  sizeAfter: number;
  unit: string;
  sourceLine: string;
  top: number;
  // Seconds (relative to mount) when the after-bar shrinks and the badge pops.
  afterAtSec: number;
  badgeAtSec: number;
}> = ({brand, product, sizeBefore, sizeAfter, unit, sourceLine, top, afterAtSec, badgeAtSec}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pct = ((sizeAfter - sizeBefore) / sizeBefore) * 100;

  const cardIn = spring({frame, fps, config: {damping: 18}});
  const beforeIn = spring({frame: frame - fps * 0.35, fps, config: {damping: 200}, durationInFrames: Math.round(fps * 0.8)});
  const afterIn = spring({frame: frame - fps * afterAtSec, fps, config: {damping: 200}, durationInFrames: Math.round(fps * 0.8)});
  const badgeIn = spring({frame: frame - fps * badgeAtSec, fps, config: {damping: 11, mass: 0.6}});

  const barRow = (
    label: string,
    widthPct: number,
    color: string,
    opacity: number,
    grow: number,
  ) => (
    <div style={{display: 'flex', alignItems: 'center', gap: 36}}>
      <div style={{flex: 1, height: 56, position: 'relative'}}>
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            bottom: 0,
            width: `${widthPct}%`,
            background: color,
            opacity,
            borderRadius: 14,
            transform: `scaleX(${grow})`,
            transformOrigin: 'left center',
          }}
        />
      </div>
      <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 56, minWidth: 290}}>{label}</div>
    </div>
  );

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 60,
        right: 140,
        background: 'rgba(10,11,13,0.92)',
        border: '1px solid rgba(255,255,255,0.12)',
        borderLeft: `16px solid ${theme.red}`,
        borderRadius: 36,
        padding: '56px 60px',
        color: theme.text,
        opacity: cardIn,
        transform: `translateY(${interpolate(cardIn, [0, 1], [110, 0])}px)`,
      }}
    >
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
        <div>
          <div
            style={{
              fontFamily: MONO,
              fontSize: 44,
              letterSpacing: 8,
              textTransform: 'uppercase',
              color: theme.red,
            }}
          >
            {brand}
          </div>
          <div style={{fontFamily: GROTESK, fontWeight: 700, fontSize: 76, marginTop: 6}}>
            {product}
          </div>
        </div>
        <div
          style={{
            background: theme.red,
            color: '#fff',
            fontFamily: MONO,
            fontWeight: 700,
            fontSize: 78,
            borderRadius: 24,
            padding: '14px 36px',
            whiteSpace: 'nowrap',
            opacity: badgeIn,
            transform: `scale(${interpolate(badgeIn, [0, 1], [0.62, 1])})`,
          }}
        >
          {pct.toFixed(1)}%
        </div>
      </div>
      <div style={{marginTop: 52, display: 'flex', flexDirection: 'column', gap: 36}}>
        {barRow(`${sizeBefore} ${unit}`, 100, '#80808a', 0.45, beforeIn)}
        {barRow(`${sizeAfter} ${unit}`, (sizeAfter / sizeBefore) * 100, theme.red, 1, afterIn)}
      </div>
      <div
        style={{
          marginTop: 52,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div style={{fontFamily: MONO, fontSize: 40, color: theme.textSecondary}}>{sourceLine}</div>
        <FCMini />
      </div>
    </div>
  );
};

// Full-frame stat moment: small red label, huge mono number, gray caption.
export const StatCard: React.FC<{
  label: string;
  value: number;
  caption: string;
  top: number;
}> = ({label, value, caption, top}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const labelIn = spring({frame, fps, config: {damping: 200}});
  const numIn = spring({frame: frame - fps * 0.14, fps, config: {damping: 12, mass: 0.6}});
  const capIn = spring({frame: frame - fps * 0.34, fps, config: {damping: 200}});
  // Counter roll-up, easing out into the real number.
  const shown = Math.round(value * interpolate(numIn, [0, 1], [0, 1]));

  return (
    <div style={{position: 'absolute', top, left: 0, right: 0, textAlign: 'center'}}>
      <div
        style={{
          fontFamily: MONO,
          fontSize: 52,
          letterSpacing: 16,
          textTransform: 'uppercase',
          color: theme.red,
          opacity: labelIn,
          transform: `translateY(${interpolate(labelIn, [0, 1], [26, 0])}px)`,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontFamily: MONO,
          fontWeight: 700,
          fontSize: 290,
          lineHeight: 1,
          marginTop: 18,
          color: theme.text,
          textShadow: '0 0 120px rgba(220,38,38,0.4)',
          opacity: numIn,
        }}
      >
        {shown.toLocaleString()}
      </div>
      <div
        style={{
          fontFamily: GROTESK,
          fontWeight: 500,
          fontSize: 56,
          color: theme.textSecondary,
          marginTop: 30,
          opacity: capIn,
          transform: `translateY(${interpolate(capIn, [0, 1], [26, 0])}px)`,
        }}
      >
        {caption}
      </div>
    </div>
  );
};

// Source citation card (SourceFrame .cite): name + url left, FC mark right.
export const CiteCard: React.FC<{
  name: string;
  url: string;
  top: number;
}> = ({name, url, top}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame: frame - fps * 0.2, fps, config: {damping: 18}});

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 60,
        right: 140,
        background: 'rgba(10,11,13,0.92)',
        border: '1px solid rgba(255,255,255,0.12)',
        borderRadius: 26,
        padding: '40px 50px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        opacity: enter,
        transform: `translateY(${interpolate(enter, [0, 1], [60, 0])}px)`,
      }}
    >
      <div>
        <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 48, color: theme.text}}>
          {name}
        </div>
        <div style={{fontFamily: MONO, fontSize: 38, color: theme.textSecondary, marginTop: 8}}>
          {url}
        </div>
      </div>
      <FCMini />
    </div>
  );
};

// SourceFrame header card: "REAL SOURCE" eyebrow + claim headline.
export const SourceHeader: React.FC<{headline: string; top: number}> = ({headline, top}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 16}});

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 60,
        right: 140,
        background: 'rgba(10,11,13,0.92)',
        borderLeft: `16px solid ${theme.red}`,
        borderRadius: 26,
        padding: '36px 50px',
        opacity: enter,
        transform: `translateY(${interpolate(enter, [0, 1], [-50, 0])}px)`,
      }}
    >
      <div
        style={{
          fontFamily: MONO,
          fontSize: 40,
          letterSpacing: 8,
          textTransform: 'uppercase',
          color: theme.red,
        }}
      >
        Real source
      </div>
      <div style={{fontFamily: GROTESK, fontWeight: 700, fontSize: 64, marginTop: 8, color: theme.text}}>
        {headline}
      </div>
    </div>
  );
};

// Comic thought bubble (cream cloud + trailing dots) for gag moments.
export const ThoughtBubble: React.FC<{
  text: string;
  durSec: number;
}> = ({text, durSec}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const enter = spring({frame, fps, config: {damping: 10, mass: 0.5}});
  const exit = interpolate(
    frame,
    [Math.round(durSec * fps) - 12, Math.round(durSec * fps) - 1],
    [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );
  const bob = Math.sin(frame / 9) * 6;
  const cream = '#f5f4f0';
  const dotIn = (delay: number) =>
    spring({frame: frame - delay, fps, config: {damping: 12, mass: 0.4}});

  return (
    <div style={{position: 'absolute', inset: 0, opacity: exit}}>
      <div
        style={{
          position: 'absolute',
          top: 430 + bob,
          left: 70,
          width: 560,
          padding: '46px 50px',
          background: cream,
          borderRadius: '48% 52% 50% 50% / 58% 55% 45% 42%',
          boxShadow: '0 16px 50px rgba(0,0,0,0.55)',
          opacity: enter,
          transform: `scale(${interpolate(enter, [0, 1], [0.5, 1])})`,
          transformOrigin: '70% 110%',
          textAlign: 'center',
          fontFamily: GROTESK,
          fontStyle: 'italic',
          fontWeight: 700,
          fontSize: 50,
          lineHeight: 1.15,
          color: theme.bg,
        }}
      >
        {text}
      </div>
      {/* Trailing dots toward the mouth */}
      <div
        style={{
          position: 'absolute',
          top: 700 + bob * 0.6,
          left: 580,
          width: 44,
          height: 36,
          background: cream,
          borderRadius: '50%',
          opacity: Math.min(dotIn(4), exit),
          transform: `scale(${dotIn(4)})`,
          boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: 770 + bob * 0.3,
          left: 645,
          width: 26,
          height: 21,
          background: cream,
          borderRadius: '50%',
          opacity: Math.min(dotIn(8), exit),
          transform: `scale(${dotIn(8)})`,
          boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
        }}
      />
    </div>
  );
};

// "Price per pot" visualization — the stealth-increase math made visible.
// Deliberately price-history-free: it applies TODAY's can price to both can
// sizes ("even if the price never moved a cent"), so every input is either
// on-screen evidence (price, label cups) or arithmetic. 12-cup pot standard.
export const PotCostCard: React.FC<{
  price: number; // today's can price (from the cited listing)
  labelCups: number; // "makes up to" cups printed on the BEFORE can
  sizeBefore: number;
  sizeAfter: number;
  potCups?: number;
  sourceLine: string;
  top: number;
}> = ({price, labelCups, sizeBefore, sizeAfter, potCups = 12, sourceLine, top}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const potsBefore = labelCups / potCups;
  const potsAfter = (labelCups * (sizeAfter / sizeBefore)) / potCups;
  const centsBefore = Math.round((price / potsBefore) * 100);
  const centsAfter = Math.round((price / potsAfter) * 100);
  const pctUp = Math.round((centsAfter / centsBefore - 1) * 100);

  const cardIn = spring({frame, fps, config: {damping: 18}});
  const beforeIn = spring({frame: frame - fps * 0.35, fps, config: {damping: 200}, durationInFrames: Math.round(fps * 0.7)});
  const afterIn = spring({frame: frame - fps * 1.0, fps, config: {damping: 200}, durationInFrames: Math.round(fps * 0.7)});
  const badgeIn = spring({frame: frame - fps * 1.7, fps, config: {damping: 11, mass: 0.6}});

  const row = (label: string, cents: number, maxCents: number, color: string, opacity: number, grow: number, sub: string) => (
    <div style={{display: 'flex', alignItems: 'center', gap: 36}}>
      <div style={{width: 260, fontFamily: MONO, fontSize: 36, color: theme.textSecondary}}>{sub}</div>
      <div style={{flex: 1, height: 56, position: 'relative'}}>
        <div
          style={{
            position: 'absolute', left: 0, top: 0, bottom: 0,
            width: `${(cents / maxCents) * 100}%`,
            background: color, opacity, borderRadius: 14,
            transform: `scaleX(${grow})`, transformOrigin: 'left center',
          }}
        />
      </div>
      <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 56, minWidth: 170}}>{label}</div>
    </div>
  );

  return (
    <div
      style={{
        position: 'absolute', top, left: 60, right: 140,
        background: 'rgba(10,11,13,0.92)',
        border: '1px solid rgba(255,255,255,0.12)',
        borderLeft: `16px solid ${theme.red}`,
        borderRadius: 36, padding: '56px 60px',
        color: theme.text, opacity: cardIn,
        transform: `translateY(${interpolate(cardIn, [0, 1], [110, 0])}px)`,
      }}
    >
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div style={{fontFamily: MONO, fontSize: 44, letterSpacing: 8, textTransform: 'uppercase', color: theme.red}}>
          Cost per pot
        </div>
        <div
          style={{
            background: theme.red, color: '#fff', fontFamily: MONO, fontWeight: 700,
            fontSize: 78, borderRadius: 24, padding: '14px 36px', whiteSpace: 'nowrap',
            opacity: badgeIn, transform: `scale(${interpolate(badgeIn, [0, 1], [0.62, 1])})`,
          }}
        >
          +{pctUp}%
        </div>
      </div>
      <div style={{fontFamily: GROTESK, fontWeight: 700, fontSize: 64, marginTop: 14}}>
        same can price. fewer pots.
      </div>
      <div style={{marginTop: 52, display: 'flex', flexDirection: 'column', gap: 36}}>
        {row(`${centsBefore}¢`, centsBefore, centsAfter, '#80808a', 0.45, beforeIn, `${sizeBefore} oz can`)}
        {row(`${centsAfter}¢`, centsAfter, centsAfter, theme.red, 1, afterIn, `${sizeAfter} oz can`)}
      </div>
      <div style={{marginTop: 52, display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div style={{fontFamily: MONO, fontSize: 30, color: theme.textSecondary, lineHeight: 1.5, maxWidth: 560}}>
          {sourceLine}
        </div>
        <FCMini />
      </div>
    </div>
  );
};

// Series announcement card ("new series. It's called Caught.") — the
// CaughtTitle language with an episode line, for the format launch beat.
export const SeriesCard: React.FC<{episode: string}> = ({episode}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const labelIn = spring({frame, fps, config: {damping: 18}});
  const brandIn = spring({frame: frame - fps * 0.15, fps, config: {damping: 11, mass: 0.6}});
  const barIn = spring({frame: frame - fps * 0.3, fps, config: {damping: 16}});
  const epIn = spring({frame: frame - fps * 0.5, fps, config: {damping: 200}});

  return (
    <div style={{position: 'absolute', inset: 0}}>
      <div
        style={{
          position: 'absolute',
          top: 300,
          left: 105,
          fontFamily: MONO,
          fontSize: 44,
          letterSpacing: 22,
          textTransform: 'uppercase',
          color: theme.red,
          opacity: labelIn,
          transform: `translateX(${interpolate(labelIn, [0, 1], [-100, 0])}px)`,
          textShadow: '0 2px 12px rgba(0,0,0,0.9)',
        }}
      >
        New series
      </div>
      <div
        style={{
          position: 'absolute',
          top: 366,
          left: 100,
          fontFamily: GROTESK,
          fontWeight: 700,
          fontSize: 210,
          lineHeight: 1,
          color: theme.text,
          opacity: brandIn,
          transform: `scale(${interpolate(brandIn, [0, 1], [0.62, 1])})`,
          transformOrigin: 'left center',
          textShadow: '0 4px 0 #000, 0 0 26px rgba(0,0,0,0.9)',
        }}
      >
        CAUGHT
      </div>
      <div
        style={{
          position: 'absolute',
          top: 640,
          left: 105,
          width: 560,
          height: 35,
          borderRadius: 17,
          background: theme.red,
          transform: `scaleX(${barIn})`,
          transformOrigin: 'left center',
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: 712,
          left: 105,
          fontFamily: MONO,
          fontSize: 46,
          color: theme.text,
          opacity: epIn,
          transform: `translateY(${interpolate(epIn, [0, 1], [20, 0])}px)`,
          textShadow: '0 2px 12px rgba(0,0,0,0.9)',
        }}
      >
        {episode}
      </div>
    </div>
  );
};
