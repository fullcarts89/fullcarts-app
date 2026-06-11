import React from 'react';
import {CalculateMetadataFunction, Composition, staticFile} from 'remotion';
import {parseSrt} from '@remotion/captions';
import {getVideoMetadata} from '@remotion/media-utils';
import {Main, MainProps} from './FolgersReveal/Main';
import {Thumbnail} from './FolgersReveal/Thumbnail';
import {defaultProps, folgersRevealSchema} from './FolgersReveal/schema';
import {cues} from './FolgersReveal/cues';

const FPS = 30;
const END_CARD_TAIL_SEC = 1; // hold past the last VO

// Duration follows the voiceover: the base video's length when present,
// otherwise the SRT's last cue / end card (+ tail). Captions themselves are
// NOT rendered — the Captions app burns its own into the talking-head edit;
// the SRT is only the timing source of truth.
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
    // The probe decodes via <video>, so it fails on Chromium builds without
    // proprietary codecs (e.g. headless-shell render boxes can't demux
    // H.264). OffthreadVideo extracts frames via ffmpeg, so rendering is
    // unaffected — fall back to the SRT / end-card duration.
    try {
      const meta = await getVideoMetadata(staticFile(props.baseVideo));
      durationSec = Math.max(durationSec, meta.durationInSeconds);
    } catch {
      // keep the caption-derived duration
    }
  }

  return {
    durationInFrames: Math.ceil(durationSec * FPS),
    props,
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="FolgersReveal"
        component={Main}
        width={1080}
        height={1920}
        fps={FPS}
        schema={folgersRevealSchema}
        defaultProps={defaultProps}
        calculateMetadata={calculateMetadata}
      />
      {/* Cover image — render with `npm run thumb` */}
      <Composition
        id="FolgersThumb"
        component={Thumbnail}
        width={1080}
        height={1920}
        fps={FPS}
        durationInFrames={1}
        schema={folgersRevealSchema}
        defaultProps={defaultProps}
      />
    </>
  );
};
