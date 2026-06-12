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

export const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const bgIn = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const line = (delaySec: number) =>
    spring({frame: frame - fps * delaySec, fps, config: {damping: 14}});

  // Card enters at cue 111.5s; the url pops at +3.3s ≈ 114.8s, landing with
  // the VO's "fullcarts.org" (~1:55).
  const q = line(0.3);
  const follow = line(0.8);
  const url = line(3.3);

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        background: theme.bg,
        opacity: bgIn,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 70,
        padding: 80,
      }}
    >
      <div
        style={{
          fontFamily: GROTESK,
          fontWeight: 700,
          fontSize: 92,
          color: theme.text,
          textAlign: 'center',
          lineHeight: 1.15,
          opacity: q,
          transform: `translateY(${interpolate(q, [0, 1], [60, 0])}px)`,
        }}
      >
        Is <span style={{color: theme.red}}>your</span> coffee
        <br />
        shrinking too?
      </div>
      <div
        style={{
          fontFamily: GROTESK,
          fontSize: 44,
          color: theme.textSecondary,
          textAlign: 'center',
          opacity: follow,
          transform: `translateY(${interpolate(follow, [0, 1], [40, 0])}px)`,
        }}
      >
        Tell me in the comments ↓<br />
        Follow for the next one.
      </div>
      <div
        style={{
          fontFamily: MONO,
          fontWeight: 700,
          fontSize: 60,
          color: theme.text,
          background: theme.red,
          padding: '18px 44px',
          borderRadius: 14,
          opacity: url,
          transform: `scale(${interpolate(url, [0, 1], [1.6, 1])})`,
          boxShadow: '0 16px 60px rgba(220,38,38,0.45)',
        }}
      >
        fullcarts.org
      </div>
    </div>
  );
};
