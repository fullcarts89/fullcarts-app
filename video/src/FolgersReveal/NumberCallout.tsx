import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {theme} from '../theme';

const MONO = '"JetBrains Mono", monospace';
const GROTESK = '"Space Grotesk", sans-serif';

// Slam-in label, e.g. "19-MONTH LOW" / "A PERMANENT RAISE".
export const SlamCallout: React.FC<{
  text: string;
  sub?: string;
  top?: number;
}> = ({text, sub, top = 360}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 12, mass: 0.7}});
  const scale = interpolate(enter, [0, 1], [2.2, 1]);

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 0,
        right: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 18,
        opacity: enter,
        transform: `scale(${scale})`,
      }}
    >
      <div
        style={{
          fontFamily: GROTESK,
          fontWeight: 700,
          fontSize: 96,
          letterSpacing: '-0.02em',
          color: theme.text,
          background: theme.red,
          padding: '10px 36px',
          transform: 'rotate(-2deg)',
          boxShadow: '0 12px 40px rgba(220,38,38,0.45)',
        }}
      >
        {text}
      </div>
      {sub ? (
        <div
          style={{
            fontFamily: MONO,
            fontSize: 34,
            color: theme.textSecondary,
            background: 'rgba(10,11,13,0.85)',
            padding: '6px 18px',
          }}
        >
          {sub}
        </div>
      ) : null}
    </div>
  );
};

// "51 oz" struck through, replaced by "43.5 oz".
export const SizeStrike: React.FC<{
  before: number;
  after: number;
  unit: string;
  top?: number;
}> = ({before, after, unit, top = 300}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const strike = spring({frame: frame - fps * 0.8, fps, config: {damping: 14}});
  const afterIn = spring({frame: frame - fps * 1.4, fps, config: {damping: 11, mass: 0.6}});

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 0,
        right: 0,
        display: 'flex',
        alignItems: 'baseline',
        justifyContent: 'center',
        gap: 44,
        fontFamily: MONO,
        fontWeight: 700,
      }}
    >
      <div style={{position: 'relative', fontSize: 110, color: theme.textSecondary}}>
        {before}
        <span style={{fontSize: 56}}> {unit}</span>
        <div
          style={{
            position: 'absolute',
            left: '-4%',
            top: '52%',
            height: 10,
            width: `${strike * 108}%`,
            background: theme.red,
            transform: 'rotate(-6deg)',
          }}
        />
      </div>
      <div
        style={{
          fontSize: 130,
          color: theme.red,
          opacity: afterIn,
          transform: `scale(${interpolate(afterIn, [0, 1], [1.8, 1])})`,
          textShadow: '0 8px 32px rgba(220,38,38,0.5)',
        }}
      >
        {after}
        <span style={{fontSize: 64}}> {unit}</span>
      </div>
    </div>
  );
};

// Ticking percentage counter, e.g. 0 -> -14.7%.
export const PercentCounter: React.FC<{
  toPct: number; // e.g. -14.7
  label: string;
  top?: number;
}> = ({toPct, label, top = 1180}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = spring({frame, fps, config: {damping: 200}, durationInFrames: Math.round(fps * 1.2)});
  const value = interpolate(t, [0, 1], [0, toPct]);

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 0,
        right: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 8,
      }}
    >
      <div
        style={{
          fontFamily: MONO,
          fontWeight: 700,
          fontSize: 150,
          color: theme.red,
          textShadow: '0 8px 40px rgba(220,38,38,0.45)',
        }}
      >
        {value.toFixed(1)}%
      </div>
      <div
        style={{
          fontFamily: GROTESK,
          fontSize: 36,
          fontWeight: 500,
          color: theme.textSecondary,
          textTransform: 'uppercase',
          letterSpacing: '0.12em',
        }}
      >
        {label}
      </div>
    </div>
  );
};
