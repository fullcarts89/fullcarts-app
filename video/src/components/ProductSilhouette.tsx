import React from "react";
import { Img } from "remotion";
import { colors } from "../theme";
import { fonts } from "../fonts";

interface Props {
  imageUrl: string | null;
  brand: string;
  productName: string;
  size?: number;
}

/**
 * Renders the product image when available, otherwise falls back to a
 * stylized SVG card so the video always builds without external assets.
 * The fallback uses the same gradient pattern as the /products/[id]
 * hero card in web/public/mockups/products-cadbury-dairy-milk-mini-eggs.html.
 */
export const ProductSilhouette: React.FC<Props> = ({
  imageUrl,
  brand,
  productName,
  size = 520,
}) => {
  if (imageUrl) {
    return (
      <div
        style={{
          width: size,
          height: size,
          borderRadius: 24,
          overflow: "hidden",
          border: `1px solid ${colors.border.subtle}`,
          background: colors.bg.secondary,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Img
          src={imageUrl}
          style={{ width: "100%", height: "100%", objectFit: "contain" }}
        />
      </div>
    );
  }

  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: 24,
        background: `linear-gradient(135deg, ${colors.bg.tertiary} 0%, ${colors.bg.primary} 100%)`,
        border: `1px solid ${colors.border.subtle}`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 20,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <svg
        viewBox="0 0 200 200"
        width={size * 0.55}
        height={size * 0.55}
        style={{ opacity: 0.85 }}
      >
        <ellipse cx="70" cy="105" rx="32" ry="42" fill="#e8d5b7" />
        <ellipse cx="130" cy="100" rx="32" ry="42" fill="#b8d4e8" />
        <ellipse cx="100" cy="135" rx="32" ry="42" fill="#e8b8c8" />
        <ellipse cx="55" cy="60" rx="22" ry="28" fill="#c8e8b8" opacity="0.9" />
        <ellipse cx="148" cy="55" rx="22" ry="28" fill="#e8c8b8" opacity="0.9" />
      </svg>
      <div
        style={{
          fontFamily: fonts.mono,
          fontSize: 18,
          color: colors.text.tertiary,
          letterSpacing: 1.5,
          textTransform: "uppercase",
          textAlign: "center",
          padding: "0 24px",
        }}
      >
        {brand}
        <br />
        {productName}
      </div>
    </div>
  );
};
