import StubPage from "../_components/StubPage";

export const metadata = {
  title: "Products — coming soon · FullCarts",
};

export default function ProductsStub() {
  return (
    <StubPage
      title="Products"
      phase="Coming in Phase B"
      lede={
        <>
          Each shrinkflation event in the database belongs to a{" "}
          <strong>specific product</strong> — Cadbury Dairy Milk Mini Eggs,
          Pringles Original, etc. Right now you can see the per-brand summary
          on the <a href="/brands">brands page</a>. Per-product detail pages
          are next.
        </>
      }
      planned={[
        {
          eyebrow: "What's coming",
          title: "Per-product scorecards",
          desc: "Full size-over-time timeline, every documented event, every source link, and the retailers where the product is sold.",
        },
        {
          eyebrow: "What's coming",
          title: "Related products",
          desc: "Quick links to other products from the same brand that have been documented.",
        },
        {
          eyebrow: "What's coming",
          title: "Skimpflation overlay",
          desc: "If we have USDA nutrition data showing the product's ingredients also changed, we surface it on the same page.",
        },
      ]}
    />
  );
}
