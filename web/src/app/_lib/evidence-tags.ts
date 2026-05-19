// Canonical evidence-channel registry. The homepage's tag grid and the
// /evidence/[slug] landing pages both read from here, so a new channel
// only needs to be added in one place.
//
// `tag` is the literal string we set on `claims.evidence_tags` (a JSONB
// array column) during extraction. `slug` is the URL path. Keep them
// 1:1 — anything that mismatches breaks the homepage links.

export interface EvidenceChannel {
  slug: string;
  tag: string;
  title: string;
  intro: string;
  desc: string;
}

export const EVIDENCE_CHANNELS: EvidenceChannel[] = [
  {
    slug: "so-smol",
    tag: "So Smol",
    title: "So smol",
    intro:
      "Comically tiny versions of products you remember being a real size. " +
      "Often paired with side-by-side photos because words alone don't sell it.",
    desc: "Comically small versions of things you remember being big.",
  },
  {
    slug: "slack-fill",
    tag: "Slack Fill",
    title: "Slack fill",
    intro:
      "Same package, visible empty space. The box stayed the same so the " +
      "shelf still looks familiar — there's just less inside.",
    desc: "Same package, visible empty space, less product than the box implies.",
  },
  {
    slug: "spot-the-difference",
    tag: "Spot the Difference",
    title: "Spot the difference",
    intro:
      "Old packaging next to new. The kind of side-by-side photo a shopper " +
      "took because they didn't trust their memory — and were right.",
    desc: "Side-by-side visual proof — old packaging next to new.",
  },
  {
    slug: "skimpflation",
    tag: "Skimpflation",
    title: "Skimpflation",
    intro:
      "Same package, worse recipe. The bag still weighs what it used to — " +
      "but there's less protein, more sugar, more sodium, or cheaper fats. " +
      "USDA's quarterly nutrition releases catch many of these silently.",
    desc: "Same package, worse ingredients — less protein, more sugar, more sodium.",
  },
  {
    slug: "paper-thin",
    tag: "Paper Thin",
    title: "Paper thin",
    intro:
      "Quality drops. Thinner toilet paper, weaker trash bags, cheaper " +
      "materials. Hardest evidence channel to document because it shows up " +
      "in use, not on the label.",
    desc: "Quality drops — thinner toilet paper, weaker bags, cheaper materials.",
  },
  {
    slug: "not-as-advertised",
    tag: "Not as Advertised",
    title: "Not as advertised",
    intro:
      "The label says one thing. The contents say another. Underfills, " +
      "miscounts, and the slow drift between marketing copy and reality.",
    desc: "Weight or count on the label doesn't match what's inside.",
  },
  {
    slug: "stretchflation",
    tag: "Stretchflation",
    title: "Stretchflation",
    intro:
      "Package looks bigger. Product is the same — or smaller. The opposite " +
      "of slack fill: the box grew to mask the fact that nothing else did.",
    desc: "Package looks bigger, but the product stays the same — or shrinks.",
  },
];

export function findChannelBySlug(slug: string): EvidenceChannel | undefined {
  return EVIDENCE_CHANNELS.find((c) => c.slug === slug);
}

export function findChannelByTag(tag: string): EvidenceChannel | undefined {
  return EVIDENCE_CHANNELS.find((c) => c.tag === tag);
}
