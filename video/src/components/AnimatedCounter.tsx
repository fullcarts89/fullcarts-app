import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

interface Props {
  from: number;
  to: number;
  durationInFrames: number;
  startFrame?: number;
  format?: (n: number) => string;
  style?: React.CSSProperties;
}

/**
 * Mono-font ticking number with ease-out. Same easing as
 * web/src/components/CounterAnimation.tsx so the on-screen number
 * "feels" the same as the site.
 */
export const AnimatedCounter: React.FC<Props> = ({
  from,
  to,
  durationInFrames,
  startFrame = 0,
  format = (n) => n.toFixed(0),
  style,
}) => {
  const frame = useCurrentFrame();
  const localFrame = Math.max(0, frame - startFrame);
  const progress = Math.min(localFrame / durationInFrames, 1);
  const eased = 1 - Math.pow(1 - progress, 4);
  const value = from + (to - from) * eased;

  return <span style={style}>{format(value)}</span>;
};
