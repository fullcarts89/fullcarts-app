// Beat map for the Folgers reveal. All times in SECONDS, against the
// voiceover. These are ESTIMATES against the placeholder SRT (~2.6 words/s);
// once the real Captions SRT lands, lock each cue to the matching caption
// timestamps and they'll never drift again.
//
// Script beats:
//   1. Hook            "coffee can got smaller... 19-month low... can stayed small"
//   2. Credibility     "biggest free shrinkflation database"
//   3. Reveal          can flip + listing: 51 oz -> 43.5 oz, ~15% gone
//   4. Price chart     all-time high early 2025, ~40% fall since
//   5. Rockets/feathers
//   6. Punchline       "permanent raise"
//   7. CTA             comments + follow + fullcarts.org

export interface CueWindow {
  start: number;
  end: number;
}

export const cues = {
  hookLowCallout: {start: 4.5, end: 9.5}, // "19-MONTH LOW" slam
  excuseGone: {start: 10.5, end: 15.0}, // "THE EXCUSE IS GONE"
  dbRecording: {start: 22.0, end: 33.0}, // fullcarts.org screen recording
  listingThen: {start: 42.0, end: 48.5}, // archived 51 oz listing
  sizeStrike: {start: 45.0, end: 56.0}, // 51 -> 43.5 strike-through callout
  listingNow: {start: 48.5, end: 56.0}, // current 43.5 oz listing
  pctCounter: {start: 53.0, end: 60.0}, // "-14.7%" counter
  priceChart: {start: 63.0, end: 76.0}, // real futures chart screenshot
  peakCallout: {start: 64.5, end: 69.5}, // "ALL-TIME HIGH — EARLY 2025"
  dropCallout: {start: 70.0, end: 76.0}, // "DOWN ~40% SINCE"
  rocketsFeathers: {start: 84.0, end: 97.0}, // kinetic typography metaphor
  permanentRaise: {start: 103.0, end: 109.0}, // "A PERMANENT RAISE" slam
  endCard: {start: 112.0, end: 124.0}, // CTA card (runs to the end)
} satisfies Record<string, CueWindow>;

export const inWindow = (tSec: number, w: CueWindow): boolean =>
  tSec >= w.start && tSec < w.end;
