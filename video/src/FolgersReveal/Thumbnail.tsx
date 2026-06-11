import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {theme} from '../theme';
import {LogoBlock, Kicker} from './Cutaway';
import type {FolgersRevealProps} from './schema';

const GROTESK = '"Space Grotesk", sans-serif';
const MONO = '"JetBrains Mono", monospace';

const GRID_BG = `
  repeating-linear-gradient(0deg, rgba(245,244,240,0.05) 0px, transparent 1px, transparent 2px, rgba(245,244,240,0.05) 3px),
  repeating-linear-gradient(90deg, rgba(245,244,240,0.05) 0px, transparent 1px, transparent 2px, rgba(245,244,240,0.05) 3px)
`;

// Static evidence card for the thumbnail (no springs — this comp renders as
// a single still via `npm run thumb`).
const ThumbCard: React.FC<{
  src: string | null;
  label: string;
  top: number;
  left: number;
  width: number;
  height: number;
  rotate: number;
}> = ({src, label, top, left, width, height, rotate}) => (
  <div
    style={{
      position: 'absolute',
      top,
      left,
      width,
      height,
      transform: `rotate(${rotate}deg)`,
      background: theme.bgCard,
      border: `3px solid ${theme.bgElevated}`,
      borderRadius: 18,
      overflow: 'hidden',
      boxShadow: '0 30px 80px rgba(0,0,0,0.8)',
    }}
  >
    {src ? (
      <Img
        src={staticFile(src)}
        style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'left top'}}
      />
    ) : null}
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        bottom: 0,
        padding: '10px 20px',
        background: 'rgba(10,11,13,0.92)',
        fontFamily: MONO,
        fontSize: 24,
        color: theme.textSecondary,
        display: 'flex',
        gap: 12,
      }}
    >
      <span style={{color: theme.green, fontWeight: 700}}>REAL</span>
      <span>{label}</span>
    </div>
  </div>
);

// Cover image for TikTok/Reels: brand surface + the verdict + the receipts.
// Everything visual is a real artifact (the Walmart listings) per the
// AI-vs-evidence policy.
export const Thumbnail: React.FC<FolgersRevealProps> = (props) => {
  const pctDrop =
    ((props.sizeAfter - props.sizeBefore) / props.sizeBefore) * 100;
  return (
    <AbsoluteFill style={{background: theme.bg}}>
      <AbsoluteFill style={{backgroundImage: GRID_BG, opacity: 0.6}} />
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(ellipse 90% 50% at 50% 30%, rgba(220,38,38,0.14) 0%, transparent 65%)',
        }}
      />

      <div
        style={{
          position: 'absolute',
          top: 100,
          left: 70,
          right: 70,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <LogoBlock />
        <Kicker text="DOCUMENTED" />
      </div>

      {/* The verdict */}
      <div style={{position: 'absolute', top: 290, left: 70, right: 70}}>
        <div
          style={{
            fontFamily: GROTESK,
            fontWeight: 700,
            fontSize: 120,
            lineHeight: 1.02,
            letterSpacing: '-0.025em',
            color: theme.text,
          }}
        >
          {props.brand.toUpperCase()}
          <br />
          SHRANK<span style={{color: theme.redHover}}>.</span>
        </div>
        <div
          style={{
            marginTop: 36,
            fontFamily: MONO,
            fontWeight: 700,
            fontSize: 64,
            display: 'flex',
            alignItems: 'baseline',
            gap: 28,
          }}
        >
          <span
            style={{
              color: theme.textSecondary,
              textDecoration: 'line-through',
              textDecorationColor: theme.red,
              textDecorationThickness: 6,
            }}
          >
            {props.sizeBefore} {props.sizeUnit}
          </span>
          <span style={{color: theme.redHover}}>
            → {props.sizeAfter} {props.sizeUnit}
          </span>
        </div>
        <div
          style={{
            marginTop: 30,
            fontFamily: MONO,
            fontWeight: 700,
            fontSize: 150,
            color: theme.redHover,
            textShadow: '0 0 80px rgba(220,38,38,0.55)',
          }}
        >
          {pctDrop.toFixed(1)}%
        </div>
      </div>

      {/* The receipts */}
      <ThumbCard
        src={props.listingThenImage}
        label="walmart.com — the old can"
        top={1180}
        left={50}
        width={640}
        height={358}
        rotate={-3}
      />
      <ThumbCard
        src={props.listingNowImage}
        label="walmart.com — today"
        top={1330}
        left={350}
        width={680}
        height={294}
        rotate={2.5}
      />

      {/* CTA bar */}
      <div
        style={{
          position: 'absolute',
          bottom: 110,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            fontFamily: GROTESK,
            fontWeight: 700,
            fontSize: 44,
            color: theme.text,
            background: theme.red,
            padding: '20px 44px',
            borderRadius: 14,
            boxShadow: '0 0 70px rgba(220,38,38,0.45)',
          }}
        >
          the receipts are public
        </div>
      </div>
    </AbsoluteFill>
  );
};
