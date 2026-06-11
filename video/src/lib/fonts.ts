// Fonts loaded LOCALLY from public/fonts (bundled via @fontsource) so renders work
// offline — no gstatic fetch at render time. Family names below are what the
// compositions reference.
import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

export const headline = "Space Grotesk";
export const body = "Inter";
export const mono = "JetBrains Mono";

const f = (file: string) => staticFile(`fonts/${file}`);

// Space Grotesk — headlines / wordmark
loadFont({ family: headline, url: f("space-grotesk-latin-400-normal.woff2"), weight: "400" });
loadFont({ family: headline, url: f("space-grotesk-latin-500-normal.woff2"), weight: "500" });
loadFont({ family: headline, url: f("space-grotesk-latin-700-normal.woff2"), weight: "700" });

// Inter — body
loadFont({ family: body, url: f("inter-latin-400-normal.woff2"), weight: "400" });
loadFont({ family: body, url: f("inter-latin-500-normal.woff2"), weight: "500" });
loadFont({ family: body, url: f("inter-latin-600-normal.woff2"), weight: "600" });

// JetBrains Mono — all data / numbers
loadFont({ family: mono, url: f("jetbrains-mono-latin-400-normal.woff2"), weight: "400" });
loadFont({ family: mono, url: f("jetbrains-mono-latin-500-normal.woff2"), weight: "500" });
loadFont({ family: mono, url: f("jetbrains-mono-latin-700-normal.woff2"), weight: "700" });
