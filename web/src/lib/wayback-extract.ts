/**
 * Wayback Machine size extraction — TypeScript port of pipeline/scrapers/wayback.py
 * and pipeline/lib/units.py.
 *
 * Extracts product size/weight from archived HTML using a layered approach:
 *   1. JSON-LD structured data (Schema.org)
 *   2. Retailer-specific patterns
 *   3. Page title parsing (og:title, <title>)
 *   4. Generic spec-label patterns
 *   5. Body text scan (last resort)
 */

// ── Unit normalization ──────────────────────────────────────────────────────

const UNIT_MAP: Record<string, string> = {
  oz: "oz",
  ounce: "oz",
  ounces: "oz",
  "fl oz": "fl oz",
  "fl. oz": "fl oz",
  "fl.oz": "fl oz",
  "fluid ounce": "fl oz",
  "fluid ounces": "fl oz",
  lb: "lb",
  lbs: "lb",
  pound: "lb",
  pounds: "lb",
  g: "g",
  gram: "g",
  grams: "g",
  kg: "kg",
  kilogram: "kg",
  kilograms: "kg",
  ml: "ml",
  milliliter: "ml",
  milliliters: "ml",
  l: "l",
  liter: "l",
  liters: "l",
  ct: "ct",
  count: "ct",
  pack: "ct",
  pcs: "ct",
  pieces: "ct",
  piece: "ct",
  sheets: "sheets",
  sheet: "sheets",
  rolls: "rolls",
  roll: "rolls",
  pt: "pt",
  pint: "pt",
  pints: "pt",
  qt: "qt",
  quart: "qt",
  quarts: "qt",
  gal: "gal",
  gallon: "gal",
  gallons: "gal",
  "sq ft": "sq ft",
  "sq. ft": "sq ft",
  // USDA FoodData Central ISO unit codes
  onz: "oz",
  lbr: "lb",
  grm: "g",
  kgm: "kg",
  mlt: "ml",
  ltr: "l",
  flo: "fl oz",
  gll: "gal",
  ptn: "pt",
  qrt: "qt",
};

function normalizeUnit(u: string): string {
  if (!u) return "oz";
  const key = u.toLowerCase().replace(/\s+/g, " ").trim();
  if (UNIT_MAP[key]) return UNIT_MAP[key];
  const stripped = key.replace(/s$/, "");
  if (UNIT_MAP[stripped]) return UNIT_MAP[stripped];
  return key;
}

// ── Number+unit regex ───────────────────────────────────────────────────────

const NUM_UNIT_RE =
  /(\d+(?:\.\d+)?)\s*(onz|lbr|kgm|grm|mlt|ltr|flo|gll|ptn|qrt|fl\.?\s*oz|fluid\s+ounces?|oz|ounces?|lbs?|pounds?|kg|kilograms?|g|grams?|ml|milliliters?|l|liters?|ct|count|pack|pcs|pieces?|sheets?|rolls?|sq\.?\s*ft|pt|pints?|qt|quarts?|gal|gallons?)/i;

const COMPOUND_LB_OZ_RE =
  /(\d+(?:\.\d+)?)\s*(?:lb|lbs|pound|pounds)\s+(\d+(?:\.\d+)?)\s*(?:oz|ounce|ounces)/i;

function parseSingle(text: string): [number | null, string | null] {
  const m = text.match(NUM_UNIT_RE);
  if (!m) return [null, null];
  return [parseFloat(m[1]), normalizeUnit(m[2])];
}

export function parsePackageWeight(text: string): [number | null, string | null] {
  if (!text || !text.trim()) return [null, null];
  text = text.trim();

  // Compound "1 LB 4 OZ"
  const cm = text.match(COMPOUND_LB_OZ_RE);
  if (cm) {
    const totalOz = parseFloat(cm[1]) * 16 + parseFloat(cm[2]);
    return [totalOz, "oz"];
  }

  // Slash-separated "6 oz/170 g"
  if (text.includes("/")) {
    const parts = text.split("/", 2);
    let [val, unit] = parseSingle(parts[0].trim());
    if (val !== null) return [val, unit];
    [val, unit] = parseSingle(parts[1].trim());
    if (val !== null) return [val, unit];
  }

  // Parenthetical "6 oz (170g)"
  if (text.includes("(")) {
    const before = text.split("(", 2)[0].trim();
    const [val, unit] = parseSingle(before);
    if (val !== null) return [val, unit];
  }

  return parseSingle(text);
}

// ── Retailer detection ──────────────────────────────────────────────────────

export function detectRetailer(url: string): string {
  const u = url.toLowerCase();
  if (u.includes("walmart.com")) return "walmart";
  if (u.includes("amazon.com")) return "amazon";
  if (u.includes("kroger.com")) return "kroger";
  if (u.includes("target.com")) return "target";
  if (u.includes("openfoodfacts.org")) return "openfoodfacts";
  if (u.includes("fdc.nal.usda.gov")) return "usda_fdc";
  return "generic";
}

// ── Extraction result type ──────────────────────────────────────────────────

type ExtractionResult = {
  size: number | null;
  unit: string | null;
  method: string | null;
};

const NONE: ExtractionResult = { size: null, unit: null, method: null };

function result(size: number, unit: string, method: string): ExtractionResult {
  return { size, unit, method };
}

// ── Layer 1: JSON-LD ────────────────────────────────────────────────────────

const JSON_LD_RE =
  /<script[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;

const JSON_WEIGHT_RE =
  /"(?:weight|size|netContent)"\s*:\s*\{[^}]*"value"\s*:\s*"?(\d+(?:\.\d+)?)"?[^}]*"unitText"\s*:\s*"([^"]+)"/;

function extractJsonLd(html: string): ExtractionResult {
  let m: RegExpExecArray | null;
  // Reset lastIndex for global regex
  JSON_LD_RE.lastIndex = 0;
  while ((m = JSON_LD_RE.exec(html)) !== null) {
    const wm = m[1].match(JSON_WEIGHT_RE);
    if (wm) {
      const size = parseFloat(wm[1]);
      if (!isNaN(size)) return result(size, normalizeUnit(wm[2].trim()), "json_ld");
    }
  }
  return NONE;
}

// ── Layer 2: Retailer-specific extractors ───────────────────────────────────

function extractWalmart(html: string): ExtractionResult {
  let m = html.match(/data-product-size=["']([^"']+)["']/i);
  if (m) {
    const [size, unit] = parsePackageWeight(m[1]);
    if (size !== null) return result(size, unit!, "walmart_data_attr");
  }

  m = html.match(
    /(?:Net\s*Weight|Package\s*Size|Size)[^<]*<\/(?:td|th|dt|span)>\s*<(?:td|dd|span)[^>]*>\s*([^<]+)/i,
  );
  if (m) {
    const [size, unit] = parsePackageWeight(m[1].trim());
    if (size !== null) return result(size, unit!, "walmart_spec_row");
  }

  return NONE;
}

function extractAmazon(html: string): ExtractionResult {
  const labels = [
    "Size",
    "Package Information",
    "Item Weight",
    "Net Content",
    "Net Quantity",
    "Unit Count",
    "Item Package Quantity",
  ];
  for (const label of labels) {
    const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const re = new RegExp(
      `(?:<th[^>]*>|<span[^>]*class="[^"]*label[^"]*"[^>]*>)\\s*${escaped}\\s*</(?:th|span)>\\s*<(?:td|span)[^>]*>\\s*([^<]+)`,
      "i",
    );
    const m = html.match(re);
    if (m) {
      const [size, unit] = parsePackageWeight(m[1].trim());
      if (size !== null) return result(size, unit!, "amazon_detail_table");
    }
  }

  let m = html.match(
    /(?:Size|Weight|Volume|Count)[:\s]*<\/span>\s*<span[^>]*>\s*(\d+(?:\.\d+)?\s*(?:fl\.?\s*oz|oz|lb|g|kg|ml|l|ct|count|pack))/i,
  );
  if (m) {
    const [size, unit] = parsePackageWeight(m[1]);
    if (size !== null) return result(size, unit!, "amazon_span");
  }

  m = html.match(/(\d+(?:\.\d+)?)\s*(Ounce|Fl\s*Oz|Count|Pack)\s*\(Pack of \d+\)/i);
  if (m) {
    const size = parseFloat(m[1]);
    return result(size, normalizeUnit(m[2]), "amazon_variation");
  }

  return NONE;
}

function extractKroger(html: string): ExtractionResult {
  let m = html.match(
    /class="[^"]*(?:ProductDetails|product-title|kds-Heading)[^"]*"[^>]*>\s*([^<]+)/i,
  );
  if (m) {
    const [size, unit] = parsePackageWeight(m[1].trim());
    if (size !== null) return result(size, unit!, "kroger_heading");
  }

  m = html.match(
    /(?:Size|Weight|Net\s*Wt)[:\s]*<\/(?:span|dt|th)>\s*<(?:span|dd|td)[^>]*>\s*([^<]+)/i,
  );
  if (m) {
    const [size, unit] = parsePackageWeight(m[1].trim());
    if (size !== null) return result(size, unit!, "kroger_spec");
  }

  m = html.match(/"(?:productSize|size|sellBy)"\s*:\s*"([^"]+)"/);
  if (m) {
    const [size, unit] = parsePackageWeight(m[1]);
    if (size !== null) return result(size, unit!, "kroger_json");
  }

  return NONE;
}

function extractTarget(html: string): ExtractionResult {
  let m = html.match(/data-test=["']product-title["'][^>]*>([^<]+)/i);
  if (m) {
    const [size, unit] = parsePackageWeight(m[1].trim());
    if (size !== null) return result(size, unit!, "target_title_attr");
  }

  m = html.match(
    /(?:Net [Ww]eight|Package Quantity|Size)[:\s]*<\/(?:span|b|div)>\s*<(?:span|div)[^>]*>\s*([^<]+)/i,
  );
  if (m) {
    const [size, unit] = parsePackageWeight(m[1].trim());
    if (size !== null) return result(size, unit!, "target_spec");
  }

  m = html.match(/"package_quantity"\s*:\s*"([^"]+)"/);
  if (m) {
    const [size, unit] = parsePackageWeight(m[1]);
    if (size !== null) return result(size, unit!, "target_json");
  }

  m = html.match(/"net_weight"\s*:\s*"([^"]+)"/);
  if (m) {
    const [size, unit] = parsePackageWeight(m[1]);
    if (size !== null) return result(size, unit!, "target_json");
  }

  return NONE;
}

function extractOpenFoodFacts(html: string): ExtractionResult {
  let m = html.match(/id=["']field_quantity_value["'][^>]*>\s*([^<]+)/i);
  if (m) {
    const [size, unit] = parsePackageWeight(m[1].trim());
    if (size !== null) return result(size, unit!, "off_quantity_field");
  }

  m = html.match(
    /Quantity[:\s]*(\d+(?:\.\d+)?\s*(?:fl\.?\s*oz|oz|lb|g|kg|ml|l|ct))/i,
  );
  if (m) {
    const [size, unit] = parsePackageWeight(m[1]);
    if (size !== null) return result(size, unit!, "off_quantity_text");
  }

  m = html.match(/"product_quantity"\s*:\s*"?(\d+(?:\.\d+)?)"?/);
  if (m) {
    const size = parseFloat(m[1]);
    if (!isNaN(size)) return result(size, "g", "off_json");
  }

  return NONE;
}

function extractUsdaFdc(html: string): ExtractionResult {
  let m = html.match(/Package\s*Weight[:\s]*([^<]+)/i);
  if (m) {
    const [size, unit] = parsePackageWeight(m[1].trim());
    if (size !== null) return result(size, unit!, "usda_package_weight");
  }

  m = html.match(
    /(?:Serving\s*Size|Household\s*Serving)[^<]*<\/(?:td|th|span)>\s*<(?:td|span)[^>]*>\s*([^<]+)/i,
  );
  if (m) {
    const [size, unit] = parsePackageWeight(m[1].trim());
    if (size !== null) return result(size, unit!, "usda_serving");
  }

  m = html.match(
    /"(?:packageWeight|householdServingFullText|servingSize)"\s*:\s*"([^"]+)"/,
  );
  if (m) {
    const [size, unit] = parsePackageWeight(m[1]);
    if (size !== null) return result(size, unit!, "usda_json");
  }

  return NONE;
}

const RETAILER_EXTRACTORS: Record<string, (html: string) => ExtractionResult> = {
  walmart: extractWalmart,
  amazon: extractAmazon,
  kroger: extractKroger,
  target: extractTarget,
  openfoodfacts: extractOpenFoodFacts,
  usda_fdc: extractUsdaFdc,
};

// ── Layer 3: Title parsing ──────────────────────────────────────────────────

const OG_TITLE_RE =
  /<meta[^>]*property=["']og:title["'][^>]*content=["']([^"']*)["']/i;
const TITLE_RE = /<title[^>]*>([\s\S]*?)<\/title>/i;

function extractFromTitle(html: string): ExtractionResult {
  const ogm = html.match(OG_TITLE_RE);
  if (ogm) {
    const text = ogm[1].replace(/&amp;/g, "&").replace(/&#39;/g, "'");
    const [size, unit] = parsePackageWeight(text);
    if (size !== null) return result(size, unit!, "og_title");
  }

  const tm = html.match(TITLE_RE);
  if (tm) {
    const text = tm[1].trim().replace(/&amp;/g, "&").replace(/&#39;/g, "'");
    const [size, unit] = parsePackageWeight(text);
    if (size !== null) return result(size, unit!, "title");
  }

  return NONE;
}

// ── Layer 4: Generic spec-label patterns ────────────────────────────────────

const GENERIC_SPEC_RES = [
  /(?:net\s*weight|net\s*wt|size|volume|quantity|total\s*weight|package\s*size)[:\s]*(\d+(?:\.\d+)?\s*(?:fl\.?\s*oz|oz|lb|lbs|g|kg|ml|l|ct|count|sheets|rolls|gal|qt|pt))/i,
  /<meta[^>]*(?:name|property)=["']product:weight["'][^>]*content=["']([^"']*)["']/i,
];

function extractGenericSpec(html: string): ExtractionResult {
  for (const re of GENERIC_SPEC_RES) {
    const m = html.match(re);
    if (m) {
      const [size, unit] = parsePackageWeight(m[1].trim());
      if (size !== null) return result(size, unit!, "spec_label");
    }
  }
  return NONE;
}

// ── Layer 5: Body text scan ─────────────────────────────────────────────────

function extractBodyText(html: string): ExtractionResult {
  const bodyMatch = html.slice(0, 50000).match(/<body[^>]*>([\s\S]*?)<\/body>/i);
  if (!bodyMatch) return NONE;

  const bodyText = bodyMatch[1].replace(/<[^>]+>/g, " ");
  const m = bodyText.match(
    /(?:net\s*(?:wt|weight)|size|volume|contents?)[:\s]+(\d+(?:\.\d+)?\s*\w+)/i,
  );
  if (m) {
    const [size, unit] = parsePackageWeight(m[1]);
    if (size !== null) return result(size, unit!, "body_text");
  }

  return NONE;
}

// ── Main extraction function ────────────────────────────────────────────────

export function extractSizeFromHtml(
  html: string,
  url: string = "",
): ExtractionResult {
  if (!html) return NONE;

  const retailer = detectRetailer(url);

  // Layer 1: JSON-LD
  const jsonLd = extractJsonLd(html);
  if (jsonLd.size !== null) return jsonLd;

  // Layer 2: Retailer-specific
  const extractor = RETAILER_EXTRACTORS[retailer];
  if (extractor) {
    const specific = extractor(html);
    if (specific.size !== null) return specific;
  }

  // Layer 3: Title parsing
  const title = extractFromTitle(html);
  if (title.size !== null) return title;

  // Layer 4: Generic spec-label
  const spec = extractGenericSpec(html);
  if (spec.size !== null) return spec;

  // Layer 5: Body text scan
  return extractBodyText(html);
}
