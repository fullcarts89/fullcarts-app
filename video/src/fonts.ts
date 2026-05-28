import { loadFont as loadSpaceGrotesk } from "@remotion/google-fonts/SpaceGrotesk";
import { loadFont as loadJetBrainsMono } from "@remotion/google-fonts/JetBrainsMono";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

const sg = loadSpaceGrotesk("normal", { weights: ["500", "700"] });
const jb = loadJetBrainsMono("normal", { weights: ["500", "700"] });
const inter = loadInter("normal", { weights: ["400", "500", "600"] });

export const fonts = {
  headline: sg.fontFamily,
  mono: jb.fontFamily,
  body: inter.fontFamily,
} as const;
