import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {theme} from '../theme';

// Annotates the REAL futures chart: a pulsing dot pinned on the all-time-high
// spike, then an arrow drawn from the peak down to the current-price level.
// `peak`/`fallTo` are % coordinates of the underlying screenshot; `aspect` is
// the image's height/width so the viewBox scales uniformly (circles stay
// circles, the arrowhead angle is true). Renders inside the EvidenceFrame
// overlay slot; pure annotation — the data under it is the artifact.
export const PeakFallAnnotation: React.FC<{
  peak: {x: number; y: number};
  fallTo: {x: number; y: number};
  aspect: number; // image height / width
  // Seconds (relative to the parent sequence) when each element lands.
  dotAtSec: number;
  arrowAtSec: number;
}> = ({peak, fallTo, aspect, dotAtSec, arrowAtSec}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const H = 100 * aspect; // viewBox height in units; 1 unit = 1% of width
  const px = peak.x;
  const py = (peak.y / 100) * H;
  const fx = fallTo.x;
  const fy = (fallTo.y / 100) * H;

  const dotIn = spring({
    frame: frame - fps * dotAtSec,
    fps,
    config: {damping: 10, mass: 0.5},
  });
  const pulse = ((frame - fps * dotAtSec) / fps) % 1.4;

  const arrowT = interpolate(
    frame,
    [fps * arrowAtSec, fps * (arrowAtSec + 0.9)],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  // Arrow starts just off the dot so the dot stays readable.
  const sx = px + 3;
  const sy = py + 3;
  const ex = sx + (fx - sx) * arrowT;
  const ey = sy + (fy - sy) * arrowT;
  const angleDeg = (Math.atan2(fy - sy, fx - sx) * 180) / Math.PI;

  return (
    <svg
      viewBox={`0 0 100 ${H}`}
      preserveAspectRatio="none"
      style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}
    >
      {/* Pulse ring radiating from the peak */}
      {dotIn > 0 ? (
        <circle
          cx={px}
          cy={py}
          r={1.4 + pulse * 3.6}
          fill="none"
          stroke={theme.red}
          strokeWidth={0.4}
          opacity={Math.max(0, 0.8 - pulse * 0.65)}
        />
      ) : null}
      {/* The dot on the all-time high */}
      <circle
        cx={px}
        cy={py}
        r={1.4 * dotIn}
        fill={theme.red}
        stroke="#fff"
        strokeWidth={0.35}
        style={{filter: 'drop-shadow(0 0 8px rgba(220,38,38,0.9))'}}
      />
      {/* The fall: arrow drawn from peak toward the current price */}
      {arrowT > 0.01 ? (
        <>
          <line
            x1={sx}
            y1={sy}
            x2={ex}
            y2={ey}
            stroke={theme.red}
            strokeWidth={1}
            strokeLinecap="round"
            style={{filter: 'drop-shadow(0 0 10px rgba(220,38,38,0.7))'}}
          />
          <path
            d="M 0 0 L -3.6 -1.7 L -3.6 1.7 Z"
            fill={theme.red}
            transform={`translate(${ex}, ${ey}) rotate(${angleDeg})`}
            style={{filter: 'drop-shadow(0 0 10px rgba(220,38,38,0.7))'}}
          />
        </>
      ) : null}
    </svg>
  );
};
