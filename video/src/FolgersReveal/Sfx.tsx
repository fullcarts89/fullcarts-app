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
  // The three stamps — the sonic logo. Never more than three. (Take 2:
  // CAUGHT cold-open, "catch them in the act" on the series card, and the
  // permanent-raise punchline.)
  {at: 1.75, file: 'stamp.mp3', volume: 0.6}, // "caught" (spoken + title)
  {at: 22.0, file: 'stamp.mp3', volume: 0.45}, // "catch them in the act" (lighter)
  {at: 101.6, file: 'stamp.mp3', volume: 0.7}, // "a permanent raise" (biggest)

  // The zoom motif, distilled: thunks only on the highest-stakes punch-ins.
  {at: 50.6, file: 'thunk.mp3', volume: 0.55}, // "on purpose" — the reference hit
  {at: 99.1, file: 'thunk.mp3', volume: 0.45}, // "the shrink stayed" → sets up stamp #3

  // Structure: transitions + the data reveals
  {at: 28.3, file: 'whoosh.mp3', volume: 0.3}, // → db cutaway
  {at: 28.6, file: 'roll.mp3', volume: 0.15}, // 2,228 odometer
  {at: 29.4, file: 'ding.mp3', volume: 0.3}, // counter lands
  {at: 53.4, file: 'whoosh.mp3', volume: 0.3}, // → reveal cutaway
  {at: 57.3, file: 'deflate.mp3', volume: 0.4}, // after-bar shrinks ("43 and a half")
  {at: 63.6, file: 'pop.mp3', volume: 0.45}, // −14.7% badge ("just gone")
  {at: 65.4, file: 'whoosh.mp3', volume: 0.3}, // → chart cutaway
  {at: 74.9, file: 'whoosh.mp3', volume: 0.3}, // → price-per-pot cutaway
  {at: 86.0, file: 'whoosh.mp3', volume: 0.3}, // → rockets cutaway
  // ~92.3 feather: deliberate SILENCE — the quiet is the joke
  {at: 114.9, file: 'ding.mp3', volume: 0.3}, // "fullcarts.org"
];

const DRONE_OUT_SEC = 111.5; // kill the underbed for the CTA (end card in)
// The feather gag (~92.3–94.8) reads funnier if the whole soundscape holds
// its breath — dip the bed with it.
const FEATHER_DIP = {from: 92.0, to: 94.9};

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
              [
                0,
                fps * 1.5,
                fps * (FEATHER_DIP.from - 0.4),
                fps * FEATHER_DIP.from,
                fps * FEATHER_DIP.to,
                fps * (FEATHER_DIP.to + 0.6),
                fps * (DRONE_OUT_SEC - 0.6),
                fps * DRONE_OUT_SEC,
                durationInFrames,
              ],
              [0, 0.075, 0.075, 0.018, 0.018, 0.075, 0.075, 0, 0],
              {extrapolateRight: 'clamp'},
            )
          }
        />
      ) : null}
    </>
  );
};
