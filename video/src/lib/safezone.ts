// Platform-UI safe zones for 1080×1920 short-form. Values are the UNION (worst case)
// across TikTok, Instagram Reels, and YouTube Shorts, so one clip is safe on all three.
// Keep critical content (numbers, badges, brand, burned-in captions) inside `safe`.
//
//  top    — platform tabs / search bar (Reels & Shorts top chrome)
//  bottom — caption + @handle + music ticker + nav (TikTok is the deepest)
//  right  — like / comment / share / save action rail (Reels is the widest)
//  left   — small device/caption margin
export const FRAME = { w: 1080, h: 1920 } as const;

export const INSET = { top: 240, bottom: 450, left: 60, right: 170 } as const;

export const safe = {
  left: INSET.left, // 60
  right: FRAME.w - INSET.right, // 910
  top: INSET.top, // 240
  bottom: FRAME.h - INSET.bottom, // 1470
  width: FRAME.w - INSET.left - INSET.right, // 850
} as const;
