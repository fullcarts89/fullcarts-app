import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { colors } from "../../theme";
import { Watermark } from "../../components/Watermark";
import { Hook } from "./Hook";
import { Reveal } from "./Reveal";
import { BeforeAfter } from "./BeforeAfter";
import { Receipt } from "./Receipt";
import { CTA } from "./CTA";
import type { ShrinkEvent } from "../../data/types";

/**
 * The "Gotcha Reveal" short — the workhorse pillar from
 * docs/plans/2026-05-13-social-content-engine.md.
 *
 * Five scenes, 30s @ 30fps = 900 frames. Each scene takes the same
 * ShrinkEvent prop, so swapping in another product is one object change.
 *
 * Scene timings (frames @ 30fps):
 *   0-90    (0-3s)    Hook        — the % slams in
 *   90-300  (3-10s)   Reveal      — product + brand
 *   300-540 (10-18s)  BeforeAfter — bars to scale + delta badge
 *   540-750 (18-25s)  Receipt     — ppu math + corporate parent
 *   750-900 (25-30s)  CTA         — URL + tagline
 */
export const GotchaReveal: React.FC<{ event: ShrinkEvent }> = ({ event }) => {
  return (
    <AbsoluteFill style={{ background: colors.bg.primary }}>
      <Sequence from={0} durationInFrames={90}>
        <Hook event={event} />
      </Sequence>
      <Sequence from={90} durationInFrames={210}>
        <Reveal event={event} />
      </Sequence>
      <Sequence from={300} durationInFrames={240}>
        <BeforeAfter event={event} />
      </Sequence>
      <Sequence from={540} durationInFrames={210}>
        <Receipt event={event} />
      </Sequence>
      <Sequence from={750} durationInFrames={150}>
        <CTA event={event} />
      </Sequence>

      <Watermark />

      {event.narrationAudio ? (
        <Audio src={staticFile(event.narrationAudio)} volume={1} />
      ) : null}
    </AbsoluteFill>
  );
};
