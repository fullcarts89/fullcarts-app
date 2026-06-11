import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import type {Caption} from '@remotion/captions';
import {theme} from '../theme';

// TikTok-style captions from a (typically line-level) SRT. Captions-app
// exports time whole lines, not words, so word emphasis is interpolated
// linearly across each cue -- close enough to read as word-synced. If a
// word-level SRT ever lands, this renders it exactly as timed.

const FONT_STACK = '"Space Grotesk", sans-serif';

const normalize = (w: string) =>
  w.toLowerCase().replace(/[^a-z0-9.\-']/g, '');

export const Captions: React.FC<{
  captions: Caption[];
  highlightWords: string[];
}> = ({captions, highlightWords}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const tMs = (frame / fps) * 1000;

  const highlights = useMemo(
    () => new Set(highlightWords.map(normalize)),
    [highlightWords],
  );

  const active = captions.find((c) => tMs >= c.startMs && tMs < c.endMs);
  if (!active) {
    return null;
  }

  const words = active.text.trim().split(/\s+/);
  const progress = (tMs - active.startMs) / (active.endMs - active.startMs);
  const spokenIndex = Math.min(
    words.length - 1,
    Math.floor(progress * words.length),
  );

  return (
    <div
      style={{
        position: 'absolute',
        left: 60,
        right: 60,
        bottom: 480,
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: '6px 14px',
        fontFamily: FONT_STACK,
        fontWeight: 700,
        fontSize: 58,
        lineHeight: 1.15,
        textTransform: 'uppercase',
        textAlign: 'center',
      }}
    >
      {words.map((word, i) => {
        const isKeyword = highlights.has(normalize(word));
        const isSpoken = i === spokenIndex;
        return (
          <span
            key={`${active.startMs}-${i}`}
            style={{
              color: isKeyword ? theme.red : theme.text,
              transform: isSpoken ? 'scale(1.08)' : 'scale(1)',
              textShadow:
                '0 2px 4px rgba(0,0,0,0.9), 0 0 24px rgba(0,0,0,0.6)',
              WebkitTextStroke: '2px rgba(0,0,0,0.55)',
              paintOrder: 'stroke fill',
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
