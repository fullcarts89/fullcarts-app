import React from "react";
import { AbsoluteFill } from "remotion";
import { FRAME, INSET, safe, CAPTION } from "../lib/safezone";
import { mono } from "../lib/fonts";

// PREVIEW ONLY — not part of any production render. Shades the platform-UI zones
// (top chrome, bottom caption, right action rail) and mocks the actual TikTok/Reels
// UI so we can confirm overlays sit clear of it. Never composite into a real export.
const band: React.CSSProperties = { position: "absolute", background: "rgba(220,38,38,0.14)" };
const lbl: React.CSSProperties = {
  position: "absolute",
  fontFamily: mono,
  fontSize: 20,
  letterSpacing: 2,
  textTransform: "uppercase",
  color: "rgba(245,244,240,0.7)",
};

export const SafeZoneGuide: React.FC = () => (
  <AbsoluteFill>
    {/* unsafe zones */}
    <div style={{ ...band, top: 0, left: 0, right: 0, height: INSET.top }} />
    <div style={{ ...band, bottom: 0, left: 0, right: 0, height: INSET.bottom }} />
    <div style={{ ...band, top: 0, bottom: 0, right: 0, width: INSET.right }} />

    {/* safe rectangle outline */}
    <div
      style={{
        position: "absolute",
        left: safe.left,
        right: INSET.right,
        top: safe.top,
        bottom: INSET.bottom,
        border: "2px dashed rgba(16,185,129,0.8)",
        borderRadius: 12,
      }}
    />

    {/* caption lane (mute-first) */}
    <div
      style={{
        position: "absolute",
        left: (FRAME.w - CAPTION.maxWidth) / 2,
        width: CAPTION.maxWidth,
        top: CAPTION.top,
        height: CAPTION.bottom - CAPTION.top,
        border: "2px dashed rgba(245,158,11,0.8)",
        borderRadius: 10,
      }}
    />
    <div style={{ ...lbl, top: CAPTION.top - 30, left: (FRAME.w - CAPTION.maxWidth) / 2, color: "rgba(245,158,11,0.95)" }}>
      caption lane
    </div>

    {/* mock action rail (right) */}
    {[1120, 1280, 1440, 1600].map((y) => (
      <div
        key={y}
        style={{
          position: "absolute",
          right: 56,
          top: y,
          width: 84,
          height: 84,
          borderRadius: 42,
          background: "rgba(245,244,240,0.18)",
        }}
      />
    ))}
    {/* mock caption + handle (bottom-left) */}
    <div style={{ position: "absolute", left: 44, bottom: 250, width: 360, height: 22, borderRadius: 6, background: "rgba(245,244,240,0.22)" }} />
    <div style={{ position: "absolute", left: 44, bottom: 210, width: 560, height: 22, borderRadius: 6, background: "rgba(245,244,240,0.16)" }} />

    <div style={{ ...lbl, top: INSET.top / 2 - 12, left: 60 }}>top chrome</div>
    <div style={{ ...lbl, bottom: INSET.bottom / 2 - 12, left: 60 }}>caption / handle / music</div>
    <div style={{ ...lbl, top: 980, right: 18, writingMode: "vertical-rl" }}>action rail</div>
    <div style={{ ...lbl, top: safe.top + 12, left: safe.left + 14, color: "rgba(16,185,129,0.9)" }}>safe</div>
  </AbsoluteFill>
);
