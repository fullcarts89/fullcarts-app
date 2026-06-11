import {z} from 'zod';

// Everything factual rides in as props so the composition stays a reusable
// Reveal template: next week's video is new props + new screenshots.
export const folgersRevealSchema = z.object({
  // Filenames under public/. null => labeled placeholder is rendered so the
  // comp previews before the media lands.
  baseVideo: z.string().nullable(), // Captions talking-head export (mp4)
  srtFile: z.string(), // voiceover SRT (from Captions) — drives comp duration
  dbOverviewRecording: z.string().nullable(), // fullcarts.org homepage recording
  dbFolgersRecording: z.string().nullable(), // fullcarts.org Folgers page recording
  listingThenImage: z.string().nullable(), // delisted 51 oz listing screenshot
  listingNowImage: z.string().nullable(), // current 43.5 oz listing screenshot
  priceChartImage: z.string().nullable(), // real coffee futures chart screenshot

  brand: z.string(),
  sizeBefore: z.number(),
  sizeAfter: z.number(),
  sizeUnit: z.string(),

  // Verified macro claims (verified 2026-06-11; see public/folgers/ASSETS.md)
  lowLabel: z.string(), // "19-MONTH LOW"
  peakLabel: z.string(), // "ALL-TIME HIGH — 2025"
  dropLabel: z.string(), // "DOWN ~40% SINCE"

  // Source citations shown on the evidence frames (the policy: real artifacts,
  // visibly attributed).
  listingThenSource: z.string(),
  listingNowSource: z.string(),
  priceChartSource: z.string(),
});

export type FolgersRevealProps = z.infer<typeof folgersRevealSchema>;

export const defaultProps: FolgersRevealProps = {
  baseVideo: null, // drop the Captions export at public/folgers/base.mp4 and set 'folgers/base.mp4'
  srtFile: 'folgers/voiceover.srt',
  dbOverviewRecording: 'folgers/fullcarts-overview.mov',
  dbFolgersRecording: 'folgers/folgers-page.mov',
  listingThenImage: 'folgers/listing-then.png',
  listingNowImage: 'folgers/listing-now.png',
  priceChartImage: 'folgers/price-chart.png',

  brand: 'Folgers',
  sizeBefore: 51,
  sizeAfter: 43.5,
  sizeUnit: 'oz',

  lowLabel: '19-MONTH LOW',
  peakLabel: 'ALL-TIME HIGH — 2025',
  dropLabel: 'DOWN ~40% SINCE',

  listingThenSource: 'walmart.com — delisted 51 oz listing',
  listingNowSource: 'walmart.com — current listing, June 2026',
  priceChartSource: 'ICE coffee futures (KC) — 12-month chart',
};
