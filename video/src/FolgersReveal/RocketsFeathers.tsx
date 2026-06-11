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

// "Rockets and feathers", rebuilt as a full-screen branded animation: a red
// streak rips up the panel (the rocket), then a gray path drifts down in slow
// sways (the feather). Pure metaphor — deliberately NO axes, no numbers, no
// tick labels, so it can never be mistaken for data (bucket 2 of the
// AI/evidence policy).
//
// Geometry lives in a 1080x1100 viewBox positioned under the kicker.
const ROCKET_PATH = 'M 120 1020 C 300 980, 420 760, 520 480 C 580 310, 640 190, 760 90';
const ROCKET_LEN = 1300; // ~path length, for dash draw-on
const FEATHER_PATH =
  'M 760 140 C 660 260, 520 300, 420 330 C 560 360, 680 420, 620 510 C 480 590, 400 610, 340 650 C 520 690, 660 760, 600 850 C 500 930, 420 950, 360 990';
const FEATHER_LEN = 2200;

export const RocketsFeathers: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Phase 1 — the rocket: fast, violent, overshooting spring.
  const launch = spring({frame, fps, config: {damping: 14, mass: 0.5}, durationInFrames: Math.round(fps * 0.9)});
  const rocketDraw = interpolate(launch, [0, 1], [ROCKET_LEN, 0]);
  const rocketsWordIn = spring({frame: frame - fps * 0.45, fps, config: {damping: 11, mass: 0.6}});

  // Phase 2 — the feather: starts on "...float down like a feather" (~2.4s),
  // takes its time. Linear-ish draw so the descent reads slow and reluctant.
  const featherT = interpolate(frame, [fps * 2.4, fps * 7.6], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const featherDraw = FEATHER_LEN * (1 - featherT);
  const feathersWordIn = spring({frame: frame - fps * 3.0, fps, config: {damping: 200}});

  const chipIn = spring({frame: frame - fps * 4.6, fps, config: {damping: 16}});

  return (
    <div style={{position: 'absolute', inset: 0}}>
      <svg
        viewBox="0 0 1080 1100"
        style={{position: 'absolute', top: 220, left: 0, width: 1080, height: 1100}}
      >
        <defs>
          <linearGradient id="rocketGrad" x1="0" y1="1" x2="1" y2="0">
            <stop offset="0%" stopColor={theme.red} stopOpacity="0" />
            <stop offset="35%" stopColor={theme.red} stopOpacity="0.9" />
            <stop offset="100%" stopColor={theme.redHover} stopOpacity="1" />
          </linearGradient>
        </defs>
        {/* Rocket streak */}
        <path
          d={ROCKET_PATH}
          fill="none"
          stroke="url(#rocketGrad)"
          strokeWidth={20}
          strokeLinecap="round"
          strokeDasharray={ROCKET_LEN}
          strokeDashoffset={rocketDraw}
          style={{filter: 'drop-shadow(0 0 26px rgba(220,38,38,0.65))'}}
        />
        {/* Hot tip of the streak */}
        {launch > 0.95 ? (
          <circle
            cx={760}
            cy={90}
            r={16 + Math.sin(frame / 2.2) * 3}
            fill={theme.redHover}
            style={{filter: 'drop-shadow(0 0 30px rgba(239,68,68,0.9))'}}
          />
        ) : null}
        {/* Feather path: dashed, slow, swaying down */}
        <path
          d={FEATHER_PATH}
          fill="none"
          stroke={theme.textSecondary}
          strokeWidth={7}
          strokeLinecap="round"
          strokeDasharray={`26 18`}
          strokeDashoffset={featherDraw}
          opacity={featherT > 0 ? 0.85 : 0}
          pathLength={FEATHER_LEN}
        />
      </svg>

      {/* PRICES UP — rides the launch */}
      <div
        style={{
          position: 'absolute',
          top: 330,
          left: 90,
          fontFamily: GROTESK,
          fontWeight: 700,
          fontSize: 96,
          letterSpacing: '-0.025em',
          color: theme.redHover,
          opacity: rocketsWordIn,
          transform: `translateY(${interpolate(rocketsWordIn, [0, 1], [60, 0])}px)`,
          textShadow: '0 0 50px rgba(220,38,38,0.5)',
        }}
      >
        UP LIKE A<br />ROCKET
      </div>

      {/* DOWN LIKE A FEATHER — drifts in with the descent */}
      <div
        style={{
          position: 'absolute',
          top: 880,
          right: 90,
          textAlign: 'right',
          fontFamily: GROTESK,
          fontWeight: 500,
          fontSize: 76,
          letterSpacing: '-0.02em',
          color: theme.textSecondary,
          opacity: feathersWordIn,
          transform: `translateY(${interpolate(feathersWordIn, [0, 1], [-40, 0])}px)`,
        }}
      >
        down like
        <br />a feather…
      </div>

      {/* The economists' actual term, in the site's badge language */}
      <div
        style={{
          position: 'absolute',
          top: 1490,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          opacity: chipIn,
          transform: `translateY(${interpolate(chipIn, [0, 1], [40, 0])}px)`,
        }}
      >
        <div
          style={{
            fontFamily: MONO,
            fontSize: 34,
            color: theme.text,
            background: theme.bgCard,
            border: `2px solid ${theme.redBorder}`,
            padding: '18px 34px',
            borderRadius: 12,
          }}
        >
          economists call it{' '}
          <span style={{color: theme.redHover, fontWeight: 700}}>
            “rockets &amp; feathers”
          </span>
        </div>
      </div>
    </div>
  );
};
