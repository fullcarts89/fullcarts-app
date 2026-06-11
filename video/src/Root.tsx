import React from 'react';
import {CalculateMetadataFunction, Composition, staticFile} from 'remotion';
import {Caption, parseSrt} from '@remotion/captions';
import {getVideoMetadata} from '@remotion/media-utils';
import {Main, MainProps} from './FolgersReveal/Main';
import {defaultProps, folgersRevealSchema} from './FolgersReveal/schema';
import {cues} from './FolgersReveal/cues';

const FPS = 30;
const END_CARD_TAIL_SEC = 1; // hold past the last caption
const MAX_WORDS_PER_PAGE = 6;

// Captions exports paragraph-level SRT cues (12-20s each) -- far too long to
// show as one block. Split each cue into <=6-word pages with timing allocated
// proportionally by word count. Word-level SRTs pass through untouched.
const paginate = (captions: Caption[]): Caption[] => {
  const out: Caption[] = [];
  for (const c of captions) {
    const words = c.text.trim().split(/\s+/);
    const pages = Math.ceil(words.length / MAX_WORDS_PER_PAGE);
    const msPerWord = (c.endMs - c.startMs) / words.length;
    for (let p = 0; p < pages; p++) {
      const slice = words.slice(
        p * MAX_WORDS_PER_PAGE,
        (p + 1) * MAX_WORDS_PER_PAGE,
      );
      const startMs = c.startMs + p * MAX_WORDS_PER_PAGE * msPerWord;
      out.push({
        text: slice.join(' '),
        startMs,
        endMs: startMs + slice.length * msPerWord,
        timestampMs: startMs,
        confidence: c.confidence,
      });
    }
  }
  return out;
};

// Duration follows the voiceover: the base video's length when present,
// otherwise the SRT's last cue / end card (+ tail). The SRT is parsed here
// once and handed to the comp as a prop, so scrubbing in the studio stays
// cheap.
const calculateMetadata: CalculateMetadataFunction<MainProps> = async ({
  props,
}) => {
  const srtText = await fetch(staticFile(props.srtFile)).then((r) => r.text());
  const {captions} = parseSrt({input: srtText});

  let durationSec =
    Math.max(
      captions.length > 0 ? captions[captions.length - 1].endMs / 1000 : 0,
      cues.endCard.end,
    ) + END_CARD_TAIL_SEC;

  if (props.baseVideo) {
    const meta = await getVideoMetadata(staticFile(props.baseVideo));
    durationSec = Math.max(durationSec, meta.durationInSeconds);
  }

  return {
    durationInFrames: Math.ceil(durationSec * FPS),
    props: {...props, captions: paginate(captions)},
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="FolgersReveal"
      component={Main}
      width={1080}
      height={1920}
      fps={FPS}
      schema={folgersRevealSchema}
      defaultProps={{...defaultProps, captions: []}}
      calculateMetadata={calculateMetadata}
    />
  );
};
