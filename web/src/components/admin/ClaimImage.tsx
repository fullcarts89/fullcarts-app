"use client";

import { useState } from "react";

export function ClaimImage({ src, alt }: { src: string; alt: string }) {
  const [failed, setFailed] = useState(false);

  if (failed) {
    return (
      <div className="flex items-center justify-center h-full text-[var(--text-tertiary)] text-sm">
        No image
      </div>
    );
  }

  /* eslint-disable @next/next/no-img-element */
  return (
    <img
      src={src}
      alt={alt}
      className="absolute inset-0 w-full h-full object-contain"
      loading="lazy"
      onError={() => setFailed(true)}
    />
  );
}
