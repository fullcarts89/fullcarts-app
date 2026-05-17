import StubPage from "../_components/StubPage";

export const metadata = {
  title: "Insights — coming soon · FullCarts",
};

export default function InsightsStub() {
  return (
    <StubPage
      title="Insights"
      phase="Coming in Phase C"
      lede={
        <>
          The brand and product pages tell you what individual products did.
          The <strong>Insights</strong> page will tell you what&rsquo;s
          happening across the whole catalog — by year, by category, by
          severity, by parent company.
        </>
      }
      planned={[
        {
          eyebrow: "The bigger picture",
          title: "Three-source validation chart",
          desc: "Our event count over time, overlaid with the BLS shrinkflation index and the FRED CPI: Food at Home line. Three independent data sources, same story.",
        },
        {
          eyebrow: "What we&rsquo;re tracking",
          title: "Categories most affected",
          desc: "Bar chart of average shrink % per category. Candy leads at -19%. Snacks, household, and personal care follow.",
        },
        {
          eyebrow: "What we&rsquo;re tracking",
          title: "Repeat-offender products",
          desc: "Top 10 individual products by cumulative shrink %. Pringles leads with 11 documented shrinks and -243% cumulative loss.",
        },
        {
          eyebrow: "Beyond size",
          title: "Skimpflation leaderboard",
          desc: "254 products where the package didn&rsquo;t change but the ingredients did. Less protein, more sugar, more sodium. Surfaced as its own ranking.",
        },
        {
          eyebrow: "Counter-narrative",
          title: "Restoration corner",
          desc: "Brands that put it back. Currently 75 upsizing events and 1 explicit restoration. We celebrate when this happens — it&rsquo;s the proof tracking works.",
        },
        {
          eyebrow: "Corporate parent tree",
          title: "Who actually owns this brand",
          desc: "Once we backfill manufacturer data from Wikidata, you&rsquo;ll be able to roll up Cadbury, Oreo, Wheat Thins, and many more under Mondelez. Same for P&G, Unilever, Nestlé, and others.",
        },
      ]}
    />
  );
}
