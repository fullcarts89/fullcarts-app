"use client";

import { useState } from "react";

const STORAGE_BASE =
  "https://ntyhbapphnzlariakgrw.supabase.co/storage/v1/object/public/claim-images";

export function ClaimImage({
  src,
  storagePath,
  alt,
}: {
  src: string;
  storagePath?: string | null;
  alt: string;
}) {
  // Try stored image first, then fall back to original URL
  const [useStored, setUseStored] = useState(!!storagePath);
  const [failed, setFailed] = useState(false);

  const activeSrc = useStored && storagePath
    ? `${STORAGE_BASE}/${storagePath}`
    : src;

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
      src={activeSrc}
      alt={alt}
      className="absolute inset-0 w-full h-full object-contain"
      loading="lazy"
      onError={() => {
        if (useStored) {
          // Stored image failed, try original URL
          setUseStored(false);
        } else {
          setFailed(true);
        }
      }}
    />
  );
}
