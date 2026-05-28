import React from "react";
import { colors } from "../theme";
import { fonts } from "../fonts";

/**
 * Bottom-corner watermark on every video. Persistent brand surface —
 * every screenshot of a clip becomes an ad for fullcarts.org.
 */
export const Watermark: React.FC = () => {
  return (
    <div
      style={{
        position: "absolute",
        bottom: 48,
        left: 0,
        right: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 12,
      }}
    >
      <div
        style={{
          width: 32,
          height: 32,
          borderRadius: 6,
          background: colors.red.base,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: fonts.mono,
          fontWeight: 700,
          fontSize: 14,
          color: colors.text.primary,
          letterSpacing: -0.5,
        }}
      >
        FC
      </div>
      <span
        style={{
          fontFamily: fonts.mono,
          fontSize: 22,
          fontWeight: 500,
          color: colors.text.secondary,
          letterSpacing: 0.5,
        }}
      >
        fullcarts.org
      </span>
    </div>
  );
};
