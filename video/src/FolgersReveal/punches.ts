// Punch-in / creep-zoom map for the BASE VIDEO layer (face shots only —
// cutaway panels carry their own motion; never stack zooms on them).
// TAKE 2 — timestamps from the line-level SRT, verified vs audio 2026-06-12.
//
// kind:
//   cut   — instant scale at `from`, instant back at `to` (jump-cut feel)
//   ramp  — linear scale fromScale→toScale across the window (creep / push)
export interface PunchSegment {
  from: number;
  to: number;
  kind: 'cut' | 'ramp';
  fromScale: number;
  toScale: number;
}

export const punches: PunchSegment[] = [
  {from: 5.7, to: 6.9, kind: 'cut', fromScale: 1.12, toScale: 1.12}, // "...can smaller"
  {from: 7.3, to: 9.8, kind: 'cut', fromScale: 1.1, toScale: 1.1}, // the mock quote
  {from: 11.3, to: 13.9, kind: 'cut', fromScale: 1.1, toScale: 1.1}, // "crashed to a 19-month low"
  {from: 24.95, to: 26.5, kind: 'cut', fromScale: 1.1, toScale: 1.1}, // "just a tired dad"
  {from: 39.1, to: 45.4, kind: 'ramp', fromScale: 1.0, toScale: 1.06}, // kitchen-scoops creep
  {from: 46.2, to: 48.0, kind: 'cut', fromScale: 1.12, toScale: 1.12}, // "no. that's not you"
  {from: 50.5, to: 52.3, kind: 'cut', fromScale: 1.18, toScale: 1.18}, // "on purpose" — hardest
  {from: 84.4, to: 86.0, kind: 'cut', fromScale: 1.1, toScale: 1.1}, // "not even making this up"
  {from: 98.0, to: 98.9, kind: 'cut', fromScale: 1.1, toScale: 1.1}, // "the cost left"
  {from: 99.0, to: 103.2, kind: 'cut', fromScale: 1.14, toScale: 1.14}, // "shrink stayed" → raise
  {from: 103.2, to: 103.9, kind: 'ramp', fromScale: 1.14, toScale: 1.0}, // punch OUT — "tell me"
];

export const punchScale = (tSec: number): number => {
  for (const p of punches) {
    if (tSec >= p.from && tSec < p.to) {
      if (p.kind === 'cut') return p.fromScale;
      const t = (tSec - p.from) / (p.to - p.from);
      return p.fromScale + (p.toScale - p.fromScale) * t;
    }
  }
  return 1;
};
