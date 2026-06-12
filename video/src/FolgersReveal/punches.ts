// Punch-in / creep-zoom map for the BASE VIDEO layer (face shots only —
// cutaway panels carry their own motion; never stack zooms on them).
// Timestamps follow docs/content/folgers-emphasis-map.md.
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
  {from: 1.6, to: 3.6, kind: 'cut', fromScale: 1.12, toScale: 1.12}, // "got smaller"
  {from: 7.6, to: 11.8, kind: 'cut', fromScale: 1.1, toScale: 1.1}, // "crashed"
  {from: 11.8, to: 13.6, kind: 'cut', fromScale: 1.16, toScale: 1.16}, // "gone. It left."
  {from: 15.5, to: 17.3, kind: 'ramp', fromScale: 1.0, toScale: 1.06}, // "stayed small" creep
  {from: 28.0, to: 29.6, kind: 'cut', fromScale: 1.1, toScale: 1.1}, // "believe me"
  {from: 36.2, to: 38.0, kind: 'cut', fromScale: 1.18, toScale: 1.18}, // "on purpose" — hardest
  {from: 38.6, to: 39.2, kind: 'cut', fromScale: 1.1, toScale: 1.1}, // "look at this"
  {from: 52.2, to: 53.3, kind: 'cut', fromScale: 1.12, toScale: 1.12}, // "actually gets me" breath
  {from: 62.5, to: 64.2, kind: 'ramp', fromScale: 1.04, toScale: 1.12}, // "genius move" push
  {from: 67.5, to: 70.2, kind: 'ramp', fromScale: 1.0, toScale: 1.06}, // "barely moved" creep
  {from: 83.5, to: 84.2, kind: 'cut', fromScale: 1.1, toScale: 1.1}, // "cost left"
  {from: 84.2, to: 88.5, kind: 'cut', fromScale: 1.14, toScale: 1.14}, // "shrink stayed" → slam
  {from: 88.5, to: 89.1, kind: 'ramp', fromScale: 1.14, toScale: 1.0}, // punch OUT — "tell me"
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
