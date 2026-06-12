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
  // The three stamps — the sonic logo. Never more than three.
  {at: 0.5, file: 'stamp.mp3', volume: 0.6}, // CAUGHT
  {at: 11.95, file: 'stamp.mp3', volume: 0.45}, // EXCUSE IS GONE (lighter)
  {at: 85.6, file: 'stamp.mp3', volume: 0.7}, // A PERMANENT RAISE (biggest)

  // The zoom motif (founder 2026-06-12): hard punch-ins land with the same
  // low thunk at varying intensity — but not ALL of them (founder trim pass:
  // "believe me" 28.0, "look at this" 38.6, and the peak dot 54.8 dropped).
  // Creep zooms (15.5, 67.5) and the punch-out (88.5) stay silent by design.
  {at: 1.6, file: 'thunk.mp3', volume: 0.4}, // "got smaller"
  {at: 7.6, file: 'thunk.mp3', volume: 0.4}, // "crashed"
  {at: 36.2, file: 'thunk.mp3', volume: 0.55}, // "on purpose" — the reference hit
  {at: 52.2, file: 'thunk.mp3', volume: 0.4}, // "actually gets me" jump-cut
  {at: 83.5, file: 'thunk.mp3', volume: 0.35}, // "cost left"
  {at: 84.2, file: 'thunk.mp3', volume: 0.45}, // "shrink stayed"
  // (11.8 punch has no thunk — the 11.95 stamp owns that moment)

  // Structure: transitions + the data reveals
  {at: 20.9, file: 'whoosh.mp3', volume: 0.3}, // → db cutaway
  {at: 21.2, file: 'roll.mp3', volume: 0.15}, // 2,228 odometer (was way hot)
  {at: 22.0, file: 'ding.mp3', volume: 0.3}, // counter lands
  {at: 39.2, file: 'whoosh.mp3', volume: 0.3}, // → reveal cutaway
  {at: 44.5, file: 'deflate.mp3', volume: 0.4}, // after-bar shrinks
  {at: 46.6, file: 'pop.mp3', volume: 0.45}, // −14.7% badge
  {at: 53.3, file: 'whoosh.mp3', volume: 0.3}, // → chart cutaway
  {at: 74.6, file: 'whoosh.mp3', volume: 0.3}, // → rockets cutaway
  // 77.9 feather: deliberate SILENCE — the quiet is the joke
  {at: 97.4, file: 'ding.mp3', volume: 0.3}, // "fullcarts.org"
];

const DRONE_OUT_SEC = 93.6; // kill the underbed for the CTA
// The feather gag (77.9–79.3) reads funnier if the whole soundscape holds
// its breath — dip the bed with it.
const FEATHER_DIP = {from: 77.6, to: 79.4};

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
