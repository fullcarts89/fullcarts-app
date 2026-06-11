// Beat map for the Folgers reveal, LOCKED to the real Captions SRT
// (captions_6FE033A0). The SRT is paragraph-level (6 cues), so in-cue moments
// below are word-proportional estimates within each cue -- expect ±0.5s;
// nudge in Remotion Studio while scrubbing against the VO.
//
// SRT cue boundaries for reference:
//   1  0.14 – 17.30   hook ("nineteen-month low" ~8.5s, "excuse is gone" ~12s)
//   2 17.62 – 37.54   credibility ("biggest free database" ~21–24s)
//   3 38.36 – 52.40   the reveal ("fifty-one" ~42s, "forty-three and a half"
//                     ~44–45s, "fifteen percent" ~46.5s)
//   4 52.92 – 70.42   chart ("all-time high" ~55.5s, "forty percent" ~59s,
//                     "price per pot crept up" ~65.5–70s)
//   5 70.90 – 87.26   rockets & feathers (~75s), "permanent raise" ~86.6s
//   6 87.94 – 97.66   CTA ("follow me" ~93.4s, "fullcarts.org" ~97.5s)
//
// 2026-06-11: the final Captions export (Captions_A80B95, 1:37.70) runs 1.5s
// shorter than the original SRT — the "Um," cut + tail trim compressed cue 6.
// Silence-gap analysis showed cues 1-5 still align within ±0.25s; only cue 6's
// end moved (99.22 → 97.66 in voiceover.srt, measured end of speech).
//
// 2026-06-11 v2 (founder feedback): evidence beats are now FULL-SCREEN
// branded cutaways (the `cut*` windows) so ~40% of the runtime is off the
// talking head. The Sam's Club listing was cut. Remotion captions removed —
// the Captions app burns its own.

export interface CueWindow {
  start: number;
  end: number;
}

export const cues = {
  caughtTitle: {start: 0.4, end: 6.0}, // "Caught: Folgers" cold-open (style board)
  hookLowCallout: {start: 8.2, end: 12.0}, // article cutaway (or slam fallback)
  excuseGone: {start: 12.0, end: 16.2}, // "THE EXCUSE IS GONE"

  // Cutaway 1 — the database (credibility beat)
  cutDb: {start: 20.9, end: 27.4},
  dbOverview: {start: 0, end: 3.3}, // homepage recording (rel. to cutDb)
  dbFolgersPage: {start: 3.3, end: 6.5}, // Folgers page recording (rel. to cutDb)
  dbStat: {start: 0.3, end: 6.5}, // "2,228 documented shrinks" StatCard (rel.)

  // Cutaway 2 — the reveal (windows rel. to cutReveal)
  cutReveal: {start: 39.2, end: 52.2},
  listingThen: {start: 0, end: 4.4}, // delisted 51 oz Walmart listing
  listingNow: {start: 4.4, end: 13.0}, // current 43.5 oz Walmart listing
  shrinkOverlay: {start: 2.8, end: 13.0}, // signature data card ("fifty-one" ~42 abs)
  shrinkAfterSec: 2.5, // after-bar shrinks on "forty-three and a half" (~44.5 abs)
  shrinkBadgeSec: 4.6, // −14.7% badge pops on "fifteen percent" (~46.6 abs)

  // Cutaway 3 — the market (windows rel. to cutChart)
  cutChart: {start: 53.3, end: 61.5},
  peakDotSec: 1.5, // dot lands on "all-time high" (~54.8 abs)
  fallArrowSec: 4.7, // arrow draws on "fallen almost forty percent" (~58 abs)
  peakCallout: {start: 1.5, end: 4.7}, // "ALL-TIME HIGH — 2025"
  dropCallout: {start: 4.7, end: 8.2}, // "DOWN ~40% SINCE"

  // Cutaway 4 — the metaphor
  cutRockets: {start: 74.6, end: 83.0},

  permanentRaise: {start: 85.6, end: 89.5}, // "A PERMANENT RAISE" slam
  endCard: {start: 93.6, end: 100.0}, // CTA card (runs to the end; ~2.3s hold past speech)
} as const;

export const inWindow = (tSec: number, w: CueWindow): boolean =>
  tSec >= w.start && tSec < w.end;
