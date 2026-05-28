import React from "react";
import { Composition } from "remotion";
import { GotchaReveal } from "./compositions/GotchaReveal";
import { shrinkEventSchema } from "./data/types";
import { cadburyMiniEggs } from "./data/cadbury-mini-eggs";

/**
 * Registers every composition. To produce a new short, either:
 *   1. Swap `defaultProps` for a different ShrinkEvent record, or
 *   2. Pass --props=path/to/event.json on the remotion render CLI.
 *
 * 9:16 (1080x1920), 30fps, 30s — TikTok / Reels / YouTube Shorts spec.
 */
export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="GotchaReveal"
        component={GotchaReveal}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        schema={shrinkEventSchema}
        defaultProps={{ event: cadburyMiniEggs }}
      />
    </>
  );
};
