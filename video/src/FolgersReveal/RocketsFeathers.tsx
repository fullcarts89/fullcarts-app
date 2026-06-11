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

// Pure kinetic-typography metaphor for "rockets and feathers": the word
// ROCKETS launches fast, FEATHERS sways down slowly. Deliberately NO axes, no
// chart, no numbers -- it must read as a metaphor, never as data (bucket 2 of
// the AI/evidence policy; it's rendered, but it testifies to nothing).
export const RocketsFeathers: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const launch = spring({frame, fps, config: {damping: 9, mass: 0.4}});
  const rocketY = interpolate(launch, [0, 1], [520, 0]);

  // Feather starts ~2.4s in, landing on "...and float down like a feather"
  const featherStart = fps * 2.4;
  const featherT = Math.max(0, frame - featherStart);
  const featherY = interpolate(featherT, [0, fps * 6], [-80, 440], {
    extrapolateRight: 'clamp',
  });
  const sway = Math.sin(featherT / (fps * 0.55)) * 90;
  const swayRot = Math.sin(featherT / (fps * 0.55) + 1) * 9;
  const featherIn = interpolate(featherT, [0, fps * 0.4], [0, 1], {
    extrapolateRight: 'clamp',
  });

  const subIn = spring({frame: frame - fps * 2.4, fps, config: {damping: 200}});

  return (
    <div style={{position: 'absolute', inset: 0}}>
      <div
        style={{
          position: 'absolute',
          top: 380,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: GROTESK,
          fontWeight: 700,
          fontSize: 110,
          color: theme.red,
          transform: `translateY(${rocketY}px) rotate(-4deg)`,
          opacity: launch,
          textShadow: '0 0 60px rgba(220,38,38,0.5)',
        }}
      >
        PRICES UP ↑
      </div>
      <div
        style={{
          position: 'absolute',
          top: 620,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: GROTESK,
          fontWeight: 500,
          fontSize: 84,
          color: theme.textSecondary,
          opacity: featherIn,
          transform: `translate(${sway}px, ${featherY}px) rotate(${swayRot}deg)`,
        }}
      >
        prices down… ↓
      </div>
      <div
        style={{
          position: 'absolute',
          top: 1130,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          opacity: subIn,
        }}
      >
        <div
          style={{
            fontFamily: MONO,
            fontSize: 38,
            color: theme.text,
            background: theme.bgCard,
            border: `2px solid ${theme.redBorder}`,
            padding: '16px 30px',
            borderRadius: 12,
          }}
        >
          “rockets and feathers”
        </div>
      </div>
    </div>
  );
};
