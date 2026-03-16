"use client";

import { useState } from "react";

export function SourceContent({
  selftext,
  sourceType,
}: {
  selftext: string;
  sourceType: string;
}) {
  const [expanded, setExpanded] = useState(false);

  if (!selftext || selftext.trim().length === 0) return null;

  const label = sourceType === "reddit" ? "Reddit post" : "Article excerpt";
  const isLong = selftext.length > 500;
  const displayText = expanded || !isLong ? selftext : selftext.slice(0, 500) + "…";

  return (
    <div className="mt-1.5">
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-xs text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] transition-colors"
      >
        {expanded ? "▾" : "▸"} {label}
      </button>
      {expanded && (
        <div className="mt-1 px-3 py-2 text-sm text-[var(--text-secondary)] leading-relaxed bg-[var(--bg-primary)] rounded border border-[var(--bg-tertiary)] whitespace-pre-wrap break-words">
          {displayText}
          {isLong && !expanded && (
            <button
              onClick={() => setExpanded(true)}
              className="ml-1 text-[var(--blue-base)] hover:underline text-xs"
            >
              Show more
            </button>
          )}
        </div>
      )}
    </div>
  );
}
