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
  articleImage: z.string().nullable(), // press headline screenshot (19-month-low). null => hook slam renders instead
  coverImage: z.string().nullable(), // thumbnail face frame (extracted from base.mp4, local-only)

  brand: z.string(),
  productName: z.string(),
  sizeBefore: z.number(),
  sizeAfter: z.number(),
  sizeUnit: z.string(),

  // Price-per-pot inputs (PotCostCard): today's can price from the cited
  // listing + the "makes up to" cups printed on the BEFORE can.
  potPrice: z.number(),
  potLabelCups: z.number(),

  // Verified macro claims (verified 2026-06-11; see public/folgers/ASSETS.md)
  lowLabel: z.string(), // "19-MONTH LOW"
  peakLabel: z.string(), // "ALL-TIME HIGH — 2025"
  dropLabel: z.string(), // "DOWN ~40% SINCE"
  dbCount: z.number(), // real published_changes count (queried 2026-06-11: 2,228)

  // Source citations shown on the evidence frames (the policy: real artifacts,
  // visibly attributed).
  listingThenSource: z.string(),
  listingNowSource: z.string(),
  priceChartSource: z.string(),
  articleHeadline: z.string(), // SourceHeader claim line over the article
  articleName: z.string(), // CiteCard: publication
  articleUrl: z.string(), // CiteCard: url + date
});

export type FolgersRevealProps = z.infer<typeof folgersRevealSchema>;

export const defaultProps: FolgersRevealProps = {
  baseVideo: null, // drop the Captions export at public/folgers/base.mp4 and set 'folgers/base.mp4'
  srtFile: 'folgers/voiceover-take2.srt',
  dbOverviewRecording: 'folgers/fullcarts-overview.mov',
  dbFolgersRecording: 'folgers/folgers-page.mov',
  listingThenImage: 'folgers/listing-then-sams.png',
  listingNowImage: 'folgers/listing-now-sams.png',
  priceChartImage: 'folgers/price-chart.png',
  articleImage: null, // drop press screenshot at public/folgers/article.png and set 'folgers/article.png'
  coverImage: null, // extract a face frame to public/folgers/cover-face.png and set 'folgers/cover-face.png'

  brand: 'Folgers',
  productName: 'Classic Roast',
  sizeBefore: 51,
  sizeAfter: 43.5,
  sizeUnit: 'oz',

  potPrice: 17.88, // samsclub.com current listing (sale; regular $18.98 — sale understates)
  potLabelCups: 400, // printed on the 51 oz can, visible in the evidence

  lowLabel: '19-MONTH LOW',
  peakLabel: 'ALL-TIME HIGH — 2025',
  dropLabel: 'DOWN ~40% SINCE',
  dbCount: 2228,

  listingThenSource: 'samsclub.com — delisted 51 oz listing',
  listingNowSource: 'samsclub.com — current listing, June 2026',
  priceChartSource: 'ICE coffee futures (KC) — 12-month chart',
  articleHeadline: 'Coffee just hit a 19-month low',
  articleName: 'Barchart',
  articleUrl: 'barchart.com · June 2026',
};
