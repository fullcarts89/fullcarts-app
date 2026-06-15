import React from "react";
import { Audio, staticFile } from "remotion";

// Ducked background bed for the full-screen data cutaways. `volume` defaults to
// 0.33 (33% under the VO). Renders nothing when `src` is empty, so a comp with
// no bed assigned (or a missing file) never breaks the render. `src` is a path
// under video/public/audio/ (e.g. "bg-loop.mp3"); drop the licensed lane track
// there per docs/content/music-beds.md.
export const MusicBed: React.FC<{ src?: string; volume?: number }> = ({ src, volume = 0.33 }) =>
  src ? <Audio loop src={staticFile(src)} volume={volume} /> : null;
