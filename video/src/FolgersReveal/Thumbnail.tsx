import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {theme} from '../theme';
import {FCMini} from './Overlays';
import type {FolgersRevealProps} from './schema';

const GROTESK = '"Space Grotesk", sans-serif';
const MONO = '"JetBrains Mono", monospace';

const GRID_BG = `
  repeating-linear-gradient(0deg, rgba(245,244,240,0.06) 0px, rgba(245,244,240,0.06) 1px, transparent 1px, transparent 48px),
  repeating-linear-gradient(90deg, rgba(245,244,240,0.06) 0px, rgba(245,244,240,0.06) 1px, transparent 1px, transparent 48px)
`;

// Cover image per the style board's Thumbnail pattern: your face frame +
// bottom scrim + "CAUGHT / Folgers" top-left + the big mono −X% + FC mark.
// Set `coverImage` to a frame extracted from the Captions export
// (public/folgers/cover-face.png, local-only like base.mp4).
export const Thumbnail: React.FC<FolgersRevealProps> = (props) => {
  const pctDrop =
    ((props.sizeAfter - props.sizeBefore) / props.sizeBefore) * 100;
  return (
    <AbsoluteFill style={{background: theme.bg}}>
      {props.coverImage ? (
        <Img
          src={staticFile(props.coverImage)}
          style={{width: '100%', height: '100%', objectFit: 'cover'}}
        />
      ) : (
        <AbsoluteFill
          style={{
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: MONO,
            fontSize: 36,
            color: theme.textTertiary,
            textAlign: 'center',
            lineHeight: 1.8,
          }}
        >
          extract a face frame to
          <br />
          public/folgers/cover-face.png
          <br />
          and set the coverImage prop
        </AbsoluteFill>
      )}
      <AbsoluteFill style={{backgroundImage: GRID_BG, opacity: 0.6}} />
      {/* Bottom scrim so the percent reads over the footage */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(to top, ${theme.bg} 0%, transparent 42%)`,
        }}
      />
      {/* Top scrim for the title block */}
      <AbsoluteFill
        style={{
          background: 'linear-gradient(to bottom, rgba(10,11,13,0.75) 0%, transparent 30%)',
        }}
      />

      <div style={{position: 'absolute', top: 180, left: 78}}>
        <div
          style={{
            fontFamily: MONO,
            fontSize: 57,
            letterSpacing: 26,
            textTransform: 'uppercase',
            color: theme.red,
            textShadow: '0 2px 14px rgba(0,0,0,0.9)',
          }}
        >
          Caught
        </div>
        <div
          style={{
            fontFamily: GROTESK,
            fontWeight: 700,
            fontSize: 192,
            lineHeight: 1,
            color: theme.text,
            marginTop: 14,
            textShadow: '0 4px 0 #000, 0 0 30px rgba(0,0,0,0.9)',
          }}
        >
          {props.brand}
        </div>
      </div>

      <div
        style={{
          position: 'absolute',
          bottom: 400,
          left: 78,
          right: 130,
          fontFamily: MONO,
          fontWeight: 700,
          fontSize: 250,
          lineHeight: 0.9,
          color: theme.red,
          textShadow: '0 0 80px rgba(220,38,38,0.6), 0 4px 0 #000',
        }}
      >
        {pctDrop.toFixed(1)}%
      </div>

      <div style={{position: 'absolute', bottom: 235, left: 78}}>
        <FCMini />
      </div>
    </AbsoluteFill>
  );
};
