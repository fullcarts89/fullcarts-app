import StubPage from "../_components/StubPage";

export const metadata = {
  title: "About — coming soon · FullCarts",
};

export default function AboutStub() {
  return (
    <StubPage
      title="About"
      phase="Coming in Phase C"
      lede={
        <>
          FullCarts is a public database of shrinkflation events. Our mission
          is simple: <strong>name the shrinkers, cite the evidence</strong>.
          A full methodology and submit-a-tip form is on the way — this page
          will go live once the rest of the site does.
        </>
      }
      planned={[
        {
          eyebrow: "Methodology",
          title: "How a claim becomes an event",
          desc: "Public sources → AI extraction → human review → published event. Every event has at least one verifiable source.",
        },
        {
          eyebrow: "Sources",
          title: "Where the data comes from",
          desc: "Reddit r/shrinkflation, news outlets (via GDELT), OpenFoodFacts, Kroger API, USDA FDC, BLS, FRED CPI, Consumer Reports, Wikidata.",
        },
        {
          eyebrow: "Get involved",
          title: "Submit a tip",
          desc: "Spotted shrinkflation in the wild? A form on this page will let you submit it directly into our pipeline for review.",
        },
        {
          eyebrow: "Contact",
          title: "Press / corrections / partnerships",
          desc: "Contact details and a press kit go here.",
        },
      ]}
    />
  );
}
