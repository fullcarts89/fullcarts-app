// Beat map for the Folgers reveal — TAKE 2, locked to the line-level SRT
// (Folgers_SRT_6.12.26, 51 cues, film 1:56.82) and verified against the
// actual audio via silence-gap analysis 2026-06-12 (gaps match SRT
// boundaries within ±0.3–0.5s at −37dB; the soft-spoken asides sit below
// −25dB, so use the gentler threshold when re-verifying).
//
// Structure: cold open CAUGHT → mock quote → 19-month low → series card →
// tired dad → DB cutaway (wink lands back on face at ~34) → kitchen creep →
// ON PURPOSE → reveal cutaway → chart cutaway → price-per-pot cutaway →
// rockets & feathers cutaway → permanent raise → CTA/end card.
// Five full-screen cutaways ≈ 44s of 118s ≈ 37% off the talking head.

export interface CueWindow {
  start: number;
  end: number;
}

export const cues = {
  caughtTitle: {start: 1.6, end: 7.0}, // pops as he says "caught" (~1.75)
  hookLowCallout: {start: 11.2, end: 15.6}, // 19-month-low (article slot / slam)
  seriesCard: {start: 16.8, end: 23.2}, // "new series... called Caught"

  // Cutaway 1 — the database ("biggest free shrinkflation database").
  // ENDS at 33.8 so the wink (~34, after "and uh") lands on his face.
  cutDb: {start: 28.3, end: 33.8},
  dbOverview: {start: 0, end: 2.8}, // homepage recording (rel.)
  dbFolgersPage: {start: 2.8, end: 5.5}, // Folgers page recording (rel.)
  dbStat: {start: 0.3, end: 5.5}, // 2,228 StatCard (rel.)

  // Cutaway 2 — the reveal (rel. to cutReveal)
  cutReveal: {start: 53.4, end: 64.7},
  listingThen: {start: 0, end: 3.6}, // 51 oz Sam's listing ("51 ounces" ~53.8)
  listingNow: {start: 3.6, end: 11.3}, // 43.5 oz Sam's listing ("43 and a half" ~57)
  shrinkOverlay: {start: 1.0, end: 11.3}, // signature data card
  shrinkAfterSec: 3.1, // after-bar shrinks on "43 and a half" (~57.5 abs)
  shrinkBadgeSec: 9.1, // −14.7% badge pops on "gone" (~63.5 abs)

  // Cutaway 3 — the market (rel. to cutChart)
  cutChart: {start: 65.4, end: 74.5},
  peakDotSec: 2.1, // dot on "all time high" (~67.5 abs)
  fallArrowSec: 5.8, // arrow on "dropped almost 40%" (~71.2 abs)
  peakCallout: {start: 2.1, end: 5.8}, // "ALL-TIME HIGH — 2025"
  dropCallout: {start: 5.8, end: 9.1}, // "DOWN ~40% SINCE"

  // Cutaway 4 — the stealth math ("so watch what they did")
  cutPotCost: {start: 74.9, end: 82.9},
  potCostCard: {start: 0.3, end: 8.0}, // rel.

  // Cutaway 5 — the metaphor. Card on face for "there's a name for this";
  // cutaway enters on "economists call it rockets" (86.2).
  cutRockets: {start: 86.0, end: 96.6},
  rocketsChipSec: 0.4, // "rockets & feathers" named immediately (~86.4 abs)
  rocketsLaunchSec: 4.2, // streak rips on "go up like a rocket" (~90.3 abs)
  rocketsFeatherSec: 6.3, // feather on "come down like a feather" (~92.3 abs)

  permanentRaise: {start: 101.3, end: 104.5}, // "...a permanent raise" slam
  endCard: {start: 111.5, end: 117.8}, // CTA card from "follow..." to the end
} as const;

export const inWindow = (tSec: number, w: CueWindow): boolean =>
  tSec >= w.start && tSec < w.end;
