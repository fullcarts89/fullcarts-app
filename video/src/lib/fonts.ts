// Fonts via @remotion/google-fonts — no .ttf bundling needed. Calling loadFont()
// at module load registers the family for use in any composition.
import { loadFont as loadHeadline } from "@remotion/google-fonts/SpaceGrotesk";
import { loadFont as loadBody } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

export const headline = loadHeadline().fontFamily; // Space Grotesk — headlines
export const body = loadBody().fontFamily; // Inter — body copy
export const mono = loadMono().fontFamily; // JetBrains Mono — metrics, labels, dates
