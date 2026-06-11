// Beat map for the Folgers reveal, LOCKED to the real Captions SRT
// (captions_6FE033A0, 1:39.2 total). The SRT is paragraph-level (6 cues), so
// in-cue moments below are word-proportional estimates within each cue —
// expect ±0.5s; nudge in Remotion Studio while scrubbing against the VO.
//
// SRT cue boundaries for reference:
//   1  0.14 – 17.30   hook ("nineteen-month low" ~8.5s, "excuse is gone" ~12s)
//   2 17.62 – 37.54   credibility ("biggest free database" ~21–24s)
//   3 38.36 – 52.40   the reveal ("fifty-one" ~42s, "forty-three and a half"
//                     ~44–45s, "fifteen percent" ~46.5s)
//   4 52.92 – 70.42   chart ("all-time high" ~55.5s, "forty percent" ~59s,
//                     "price per pot crept up" ~65.5–70s)
//   5 70.90 – 87.26   rockets & feathers (~75s), "permanent raise" ~86.6s
//   6 87.94 – 99.22   CTA ("follow me" ~94.3s, "fullcarts.org" ~99s)

export interface CueWindow {
  start: number;
  end: number;
}

export const cues = {
  hookLowCallout: {start: 8.2, end: 12.0}, // "19-MONTH LOW" slam
  excuseGone: {start: 12.0, end: 16.2}, // "THE EXCUSE IS GONE"
  dbOverview: {start: 20.9, end: 24.2}, // fullcarts.org homepage recording
  dbFolgersPage: {start: 24.2, end: 27.4}, // the Folgers product page recording
  listingThen: {start: 39.2, end: 43.6}, // delisted 51 oz Walmart listing
  listingNow: {start: 43.6, end: 48.0}, // current 43.5 oz Walmart listing
  listingSams: {start: 48.0, end: 52.2}, // current 43.5 oz Sam's Club listing
  sizeStrike: {start: 42.0, end: 46.2}, // 51 -> 43.5 strike-through callout
  pctCounter: {start: 46.2, end: 52.0}, // "-14.7%" counter
  priceChart: {start: 53.3, end: 61.5}, // real futures chart screenshot
  peakCallout: {start: 54.8, end: 58.0}, // "ALL-TIME HIGH — 2025"
  dropCallout: {start: 58.0, end: 61.5}, // "DOWN ~40% SINCE"
  rocketsFeathers: {start: 74.6, end: 83.0}, // kinetic typography metaphor
  permanentRaise: {start: 85.6, end: 89.5}, // "A PERMANENT RAISE" slam
  endCard: {start: 93.6, end: 101.5}, // CTA card (runs to the end)
} satisfies Record<string, CueWindow>;

export const inWindow = (tSec: number, w: CueWindow): boolean =>
  tSec >= w.start && tSec < w.end;
