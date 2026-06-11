import React from 'react';
import {CalculateMetadataFunction, Composition, staticFile} from 'remotion';
import {parseSrt} from '@remotion/captions';
import {getVideoMetadata} from '@remotion/media-utils';
import {Main, MainProps} from './FolgersReveal/Main';
import {defaultProps, folgersRevealSchema} from './FolgersReveal/schema';
import {cues} from './FolgersReveal/cues';

const FPS = 30;
const END_CARD_TAIL_SEC = 1; // hold past the last caption

// Duration follows the voiceover: the base video's length when present,
// otherwise the SRT's last cue (+ tail). The SRT is also parsed here once and
// handed to the comp as a prop, so scrubbing in the studio stays cheap.
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
    props: {...props, captions},
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
