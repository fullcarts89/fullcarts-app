import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {theme} from '../theme';

const GROTESK = '"Space Grotesk", sans-serif';
const MONO = '"JetBrains Mono", monospace';

// The hero-section grid pattern from FULLCARTS_DESIGN_EXPORT.md.
const GRID_BG = `
  repeating-linear-gradient(0deg, rgba(245,244,240,0.05) 0px, transparent 1px, transparent 2px, rgba(245,244,240,0.05) 3px),
  repeating-linear-gradient(90deg, rgba(245,244,240,0.05) 0px, transparent 1px, transparent 2px, rgba(245,244,240,0.05) 3px)
`;

// The site logo: red FC block + Space Grotesk wordmark (Navigation > Logo in
// the design export, scaled up for 1080x1920).
export const LogoBlock: React.FC = () => (
  <div style={{display: 'flex', alignItems: 'center', gap: 16}}>
    <div
      style={{
        width: 56,
        height: 56,
        borderRadius: 10,
        background: theme.red,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: MONO,
        fontWeight: 700,
        fontSize: 26,
        color: theme.text,
      }}
    >
      FC
    </div>
    <span
      style={{
        fontFamily: GROTESK,
        fontWeight: 700,
        fontSize: 40,
        letterSpacing: '-0.025em',
        color: theme.text,
      }}
    >
      FullCarts
    </span>
  </div>
);

// Mono uppercase kicker chip (Category Label / Status Badge pattern).
export const Kicker: React.FC<{text: string}> = ({text}) => (
  <span
    style={{
      fontFamily: MONO,
      fontWeight: 500,
      fontSize: 26,
      textTransform: 'uppercase',
      letterSpacing: '0.08em',
      color: theme.red,
      background: theme.redBg,
      border: `1px solid ${theme.redBorder}`,
      borderRadius: 8,
      padding: '10px 22px',
    }}
  >
    {text}
  </span>
);

// Full-screen branded cutaway: kills the talking-head shot entirely and
// replaces it with the fullcarts.org surface (deep graphite + grid pattern +
// logo + kicker). Children are the beat's evidence/animation layers.
export const CutawayPanel: React.FC<{
  kicker: string;
  durSec: number;
  children: React.ReactNode;
}> = ({kicker, durSec, children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const durF = Math.round(durSec * fps);

  const enter = spring({frame, fps, config: {damping: 200}, durationInFrames: 10});
  const exit = interpolate(frame, [durF - 8, durF - 1], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const opacity = Math.min(enter, exit);

  return (
    <AbsoluteFill style={{opacity}}>
      <AbsoluteFill style={{background: theme.bg}} />
      <AbsoluteFill style={{backgroundImage: GRID_BG, opacity: 0.5}} />
      {/* Vignette so the evidence pops off the grid */}
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(ellipse 80% 60% at 50% 42%, transparent 40%, rgba(10,11,13,0.85) 100%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: 90,
          left: 70,
          right: 70,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          transform: `translateY(${interpolate(enter, [0, 1], [-20, 0])}px)`,
        }}
      >
        <LogoBlock />
        <Kicker text={kicker} />
      </div>
      {children}
    </AbsoluteFill>
  );
};
