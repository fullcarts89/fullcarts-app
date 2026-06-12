import React from 'react';
import {
  Audio,
  Sequence,
  interpolate,
  staticFile,
  useVideoConfig,
} from 'remotion';

// SFX track per docs/content/folgers-emphasis-map.md + the style board's
// sound table ("a calm data terminal that slams down a receipt").
//
// Sounds live as named slots in public/sfx/ — drop ElevenLabs/Captions
// exports there. calculateMetadata probes which files exist and passes the
// list in; missing slots are silently skipped so the comp always renders.
//
// Slots: stamp.mp3 whoosh.mp3 whoosh-up.mp3 roll.mp3 ding.mp3 tick.mp3
//        deflate.mp3 pop.mp3 thunk.mp3 slide.mp3 typing.mp3 tap.mp3 drone.mp3

export interface SfxCue {
  at: number; // seconds
  file: string; // slot name under public/sfx/
  volume: number; // 0..1 (board: −12 to −18 dB under the voice)
}

export const sfxCues: SfxCue[] = [
  {at: 0.5, file: 'stamp.mp3', volume: 0.7}, // STAMP #1 — CAUGHT (sonic logo)
  {at: 11.95, file: 'stamp.mp3', volume: 0.5}, // stamp #2 — EXCUSE IS GONE (lighter)
  {at: 18.0, file: 'typing.mp3', volume: 0.18}, // "stare at numbers all day"
  {at: 20.9, file: 'whoosh.mp3', volume: 0.35}, // → db cutaway
  {at: 21.2, file: 'roll.mp3', volume: 0.45}, // 2,228 odometer
  {at: 22.0, file: 'ding.mp3', volume: 0.4}, // counter lands
  {at: 36.2, file: 'thunk.mp3', volume: 0.5}, // "on purpose"
  {at: 39.2, file: 'whoosh.mp3', volume: 0.35}, // → reveal cutaway
  {at: 39.9, file: 'tick.mp3', volume: 0.35}, // ring on (51 oz.)
  {at: 41.8, file: 'tick.mp3', volume: 0.35}, // ring on 43.5-Ounce
  {at: 44.5, file: 'deflate.mp3', volume: 0.5}, // after-bar shrinks
  {at: 46.6, file: 'pop.mp3', volume: 0.55}, // −14.7% badge
  {at: 53.3, file: 'whoosh.mp3', volume: 0.35}, // → chart cutaway
  {at: 54.8, file: 'thunk.mp3', volume: 0.4}, // peak dot lands
  {at: 58.0, file: 'slide.mp3', volume: 0.45}, // arrow draws down
  {at: 59.0, file: 'tick.mp3', volume: 0.4}, // arrow lands
  {at: 74.6, file: 'whoosh.mp3', volume: 0.35}, // → rockets cutaway
  {at: 75.0, file: 'whoosh-up.mp3', volume: 0.4}, // rocket streak (NOT a riser)
  // 77.9 feather: deliberate SILENCE — the quiet is the joke
  {at: 79.4, file: 'tick.mp3', volume: 0.3}, // "rockets & feathers" chip
  {at: 85.6, file: 'stamp.mp3', volume: 0.8}, // STAMP #3 — A PERMANENT RAISE
  {at: 93.6, file: 'tap.mp3', volume: 0.35}, // end card in
  {at: 97.4, file: 'ding.mp3', volume: 0.35}, // "fullcarts.org"
];

const DRONE_OUT_SEC = 93.6; // kill the underbed for the CTA

export const SfxTrack: React.FC<{available: string[]}> = ({available}) => {
  const {fps, durationInFrames} = useVideoConfig();
  const has = (f: string) => available.includes(f);

  return (
    <>
      {sfxCues
        .filter((c) => has(c.file))
        .map((c, i) => (
          <Sequence
            key={`${c.file}-${i}`}
            from={Math.round(c.at * fps)}
            name={`sfx ${c.file} @${c.at}`}
          >
            <Audio src={staticFile(`sfx/${c.file}`)} volume={c.volume} />
          </Sequence>
        ))}
      {has('drone.mp3') ? (
        <Audio
          loop
          src={staticFile('sfx/drone.mp3')}
          name="underbed drone"
          volume={(f) =>
            interpolate(
              f,
              [0, fps * 1.5, fps * (DRONE_OUT_SEC - 0.6), fps * DRONE_OUT_SEC, durationInFrames],
              [0, 0.12, 0.12, 0, 0],
              {extrapolateRight: 'clamp'},
            )
          }
        />
      ) : null}
    </>
  );
};
