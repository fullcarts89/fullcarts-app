import React from 'react';
import {
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {theme} from '../theme';

const MONO = '"JetBrains Mono", monospace';

// Presenter for REAL screenshots (policy: the proof layer must be real
// artifacts -- this component only frames, pans, and annotates them, with a
// visible source citation). When `src` is null it renders a labeled drop slot
// so the comp previews before captures land.
//
// Size `height` to the screenshot's aspect ratio at 934px inner width
// (1080 - 2*70 margin - 2*3 border) so ring percentages map 1:1 onto the
// image instead of onto a crop.
export const EvidenceFrame: React.FC<{
  src: string | null;
  sourceLabel: string;
  placeholder: string;
  top?: number;
  height?: number;
  // Ken Burns drift, in % of frame size.
  panX?: number;
  panY?: number;
  zoomTo?: number;
  // Optional highlight ring over the load-bearing number (% coordinates).
  ring?: {x: number; y: number; r: number};
  rotate?: number;
}> = ({src, sourceLabel, placeholder, top = 240, height = 980, panX = -3, panY = -2, zoomTo = 1.12, ring, rotate = -1.5}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  const enter = spring({frame, fps, config: {damping: 16}});
  const drift = interpolate(frame, [0, durationInFrames], [0, 1]);
  const scale = interpolate(drift, [0, 1], [1, zoomTo]);
  const tx = interpolate(drift, [0, 1], [0, panX]);
  const ty = interpolate(drift, [0, 1], [0, panY]);
  const ringIn = spring({frame: frame - fps * 0.7, fps, config: {damping: 10, mass: 0.5}});

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 70,
        right: 70,
        height,
        opacity: enter,
        transform: `rotate(${rotate}deg) translateY(${interpolate(enter, [0, 1], [80, 0])}px)`,
        background: theme.bgCard,
        border: `3px solid ${theme.bgElevated}`,
        borderRadius: 18,
        overflow: 'hidden',
        boxShadow: '0 30px 80px rgba(0,0,0,0.7)',
      }}
    >
      <div style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
        {src ? (
          <Img
            src={staticFile(src)}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'top',
              transform: `scale(${scale}) translate(${tx}%, ${ty}%)`,
            }}
          />
        ) : (
          <div
            style={{
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: MONO,
              fontSize: 34,
              color: theme.textTertiary,
              textAlign: 'center',
              padding: 60,
              lineHeight: 1.6,
            }}
          >
            {placeholder}
          </div>
        )}
        {ring ? (
          <div
            style={{
              position: 'absolute',
              left: `${ring.x - ring.r}%`,
              top: `${ring.y - ring.r}%`,
              width: `${ring.r * 2}%`,
              aspectRatio: '1',
              border: `8px solid ${theme.red}`,
              borderRadius: '50%',
              opacity: ringIn,
              transform: `scale(${interpolate(ringIn, [0, 1], [2.4, 1])})`,
              boxShadow: '0 0 40px rgba(220,38,38,0.6)',
            }}
          />
        ) : null}
      </div>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          padding: '14px 24px',
          background: 'rgba(10,11,13,0.92)',
          fontFamily: MONO,
          fontSize: 26,
          color: theme.textSecondary,
          display: 'flex',
          alignItems: 'center',
          gap: 14,
        }}
      >
        <span style={{color: theme.green, fontWeight: 700}}>REAL</span>
        <span>{sourceLabel}</span>
      </div>
    </div>
  );
};
