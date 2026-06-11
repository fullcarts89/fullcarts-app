import {z} from 'zod';

// Everything factual rides in as props so the composition stays a reusable
// Reveal template: next week's video is new props + new screenshots.
export const folgersRevealSchema = z.object({
  // Filenames under public/folgers/. null => labeled placeholder is rendered
  // so the comp previews before the media lands.
  baseVideo: z.string().nullable(), // Captions talking-head export (mp4)
  srtFile: z.string(), // voiceover SRT (from Captions)
  dbRecording: z.string().nullable(), // fullcarts.org screen recording (mp4)
  listingThenImage: z.string().nullable(), // archived 51 oz listing screenshot
  listingNowImage: z.string().nullable(), // current 43.5 oz listing screenshot
  priceChartImage: z.string().nullable(), // real ICE coffee chart screenshot

  brand: z.string(),
  sizeBefore: z.number(),
  sizeAfter: z.number(),
  sizeUnit: z.string(),

  // Verified macro claims (re-check on capture day; see public/folgers/ASSETS.md)
  lowLabel: z.string(), // "19-MONTH LOW"
  peakLabel: z.string(), // "ALL-TIME HIGH — EARLY 2025"
  dropLabel: z.string(), // "DOWN ~40% SINCE"

  // Source citations shown on the evidence frames (the policy: real artifacts,
  // visibly attributed).
  listingThenSource: z.string(),
  listingNowSource: z.string(),
  priceChartSource: z.string(),

  // Words the caption renderer paints alert-red wherever they occur.
  highlightWords: z.array(z.string()),
});

export type FolgersRevealProps = z.infer<typeof folgersRevealSchema>;

export const defaultProps: FolgersRevealProps = {
  baseVideo: null,
  srtFile: 'folgers/voiceover.srt',
  dbRecording: null,
  listingThenImage: null,
  listingNowImage: null,
  priceChartImage: null,

  brand: 'Folgers',
  sizeBefore: 51,
  sizeAfter: 43.5,
  sizeUnit: 'oz',

  lowLabel: '19-MONTH LOW',
  peakLabel: 'ALL-TIME HIGH — EARLY 2025',
  dropLabel: 'DOWN ~40% SINCE',

  listingThenSource: 'web.archive.org — archived retail listing',
  listingNowSource: 'walmart.com — captured June 2026',
  priceChartSource: 'ICE Coffee C futures — tradingeconomics.com',

  highlightWords: [
    'smaller',
    'crashed',
    'gone',
    'small',
    'fifty-one',
    'fifteen',
    'forty',
    'rockets',
    'feathers',
    'permanent',
    'raise',
    'shrinking',
    'fullcarts.org',
  ],
};
