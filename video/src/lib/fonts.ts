// Fonts are base64-embedded (see fontsCss.ts) and injected as @font-face — NO network
// fetch and NO blocking delayRender, so renders are deterministic and can never hang on
// a stalled font request or an unresolved font promise across Remotion's recycled tabs.
// Data-URI fonts decode synchronously enough that frames capture with the correct face.
import { FONTS_CSS } from "./fontsCss";

export const headline = "Space Grotesk";
export const body = "Inter";
export const mono = "JetBrains Mono";

if (typeof document !== "undefined" && !document.querySelector("style[data-fullcarts-fonts]")) {
  const style = document.createElement("style");
  style.setAttribute("data-fullcarts-fonts", "");
  style.innerHTML = FONTS_CSS;
  document.head.appendChild(style);
  // Nudge the browser to decode immediately (best-effort; not awaited).
  try {
    document.fonts.load("700 1em 'Space Grotesk'");
    document.fonts.load("700 1em 'JetBrains Mono'");
    document.fonts.load("400 1em 'Inter'");
  } catch {
    /* no-op */
  }
}
