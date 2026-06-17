import React from "react";
import { z } from "zod";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { theme } from "../lib/theme";
import { headline, body, mono } from "../lib/fonts";
import { GridTexture } from "../components/GridTexture";

export const coverCardSchema = z.object({
  faceSrc: z.string(), // a cover frame from the film (staticFile path)
  eyebrow: z.string().default("SHRINKFLATION · CAUGHT"),
  headline: z.array(z.string()), // wrap a word in *asterisks* for the red highlight
  sub: z.string(),
  url: z.string().default("fullcarts.org"),
  focusY: z.number().default(24), // objectPosition Y % (lower = show more of the top of frame)
  zoom: z.number().default(1.12),
  cardTop: z.number().default(1200), // where the graphite card starts
});

type Props = z.infer<typeof coverCardSchema>;

const parse = (text: string, color: string) =>
  text.split("*").map((seg, i) =>
    i % 2 === 1 ? (
      <span key={i} style={{ color }}>
        {seg}
      </span>
    ) : (
      <React.Fragment key={i}>{seg}</React.Fragment>
    )
  );

// Series cover / thumbnail (still PNG): face cover frame up top, a graphite card
// below with the eyebrow + "X IS A LIE" headline + sub + url. Matches the profile
// grid so the series reads as one body of work.
export const CoverCard: React.FC<Props> = ({ faceSrc, eyebrow, headline: lines, sub, url, focusY, zoom, cardTop }) => (
  <AbsoluteFill style={{ background: theme.color.bg }}>
    {/* face */}
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: cardTop + 80, overflow: "hidden" }}>
      <Img
        src={staticFile(faceSrc)}
        style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: `center ${focusY}%`, transform: `scale(${zoom})`, transformOrigin: "center top" }}
      />
      {/* fade the bottom of the photo into the card */}
      <AbsoluteFill style={{ background: `linear-gradient(to top, ${theme.color.bg} 0%, transparent 22%)` }} />
    </div>

    {/* graphite card */}
    <div style={{ position: "absolute", top: cardTop, left: 0, right: 0, bottom: 0, background: theme.color.bg }}>
      <GridTexture opacity={0.05} />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "flex-start", paddingTop: 56, paddingLeft: 70, paddingRight: 70 }}>
        <div style={{ fontFamily: mono, fontSize: 34, letterSpacing: 12, textTransform: "uppercase", color: theme.color.red }}>{eyebrow}</div>

        <div style={{ marginTop: 30, textAlign: "center" }}>
          {lines.map((line, i) => (
            <div key={i} style={{ fontFamily: headline, fontWeight: 700, fontSize: 124, lineHeight: 1.0, letterSpacing: -1, color: theme.color.textPrimary }}>
              {parse(line, theme.color.red)}
            </div>
          ))}
        </div>

        <div style={{ marginTop: 34, fontFamily: body, fontWeight: 500, fontSize: 50, color: theme.color.textSecondary, textAlign: "center" }}>{sub}</div>

        <div style={{ marginTop: 40, fontFamily: mono, fontWeight: 700, fontSize: 54, letterSpacing: 1, color: theme.color.red }}>{url}</div>
      </AbsoluteFill>
    </div>
  </AbsoluteFill>
);
