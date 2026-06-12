import { interpolate, spring, type SpringConfig } from "remotion";

// Smooth, no-overshoot spring for every entrance — gentle ease-out that settles
// cleanly, never a harsh snap, jitter, or bounce.
const SMOOTH: Partial<SpringConfig> = { damping: 200, mass: 0.9 };

// Eased 0→1 entrance progress for a beat, with an optional delay (in frames).
export const enter = (
  frame: number,
  fps: number,
  { delay = 0, durationInFrames = 18 }: { delay?: number; durationInFrames?: number } = {}
) =>
  spring({
    frame: frame - delay,
    fps,
    config: SMOOTH,
    durationInFrames,
  });

// Animated count-up to a target integer (for the database counter / CPI %).
export const countUp = (
  frame: number,
  fps: number,
  to: number,
  { delay = 0, durationInFrames = 40, decimals = 0 }: { delay?: number; durationInFrames?: number; decimals?: number } = {}
) => {
  const p = enter(frame, fps, { delay, durationInFrames });
  const v = interpolate(p, [0, 1], [0, to], { extrapolateRight: "clamp" });
  const factor = Math.pow(10, decimals);
  return Math.round(v * factor) / factor;
};

// Thousands separators for big numbers, e.g. 2228 -> "2,228".
export const fmt = (n: number, decimals = 0) =>
  n.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
