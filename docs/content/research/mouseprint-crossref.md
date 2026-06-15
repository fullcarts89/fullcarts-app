# Mouseprint × FullCarts DB — cross-reference

**Companion to:** `mouseprint-downsizing-census.md`
**Run:** 2026-06-15 · **DB as-of:** 2,227 events / 937 brands / 1,880 products
**Method:** For each mouseprint case with numeric old→new sizes, an automated SQL match against
`published_changes` (non-retracted) on **brand-prefix + size-pair within ±3%/±0.25 tolerance**, best
match by `evidence_count`. Results then hand-verified — the tolerance produced a few **false positives**
where a *different* product of the same brand fell inside the numeric window (corrected below).

**Scope note:** Our corpus is **2020→present** (only 13 events predate 2020). Mouseprint's pre-2020
archive (~70 cases, Häagen-Dazs 14oz pint, Tropicana 64→59, Tide 87→70, Breyer's/Edy's 56→48, etc.)
is therefore **out of corpus by construction** — listed in the census as historical/evergreen content
fodder, not cross-referenced here. This file covers the **2020–2026** overlap window.

**Type note:** Skimpflation / dilution / reformulation cases (no clean size pair) can't be size-matched
and are listed separately at the bottom as their own claim-candidate set.

---

## Headline

- **~95** mouseprint numeric cases checked in the 2020–2026 window.
- **~48 already TRACKED** in our DB (often with deep evidence — Folgers 31, Gatorade 28, Kleenex 20,
  Cottonelle 15, Tropicana 12, Charmin 11, Gain 9, Aleve 8, Angel Soft 5). Our Reddit/news/GDELT
  scrapers independently catch the high-virality shrinks — including the same recent ones mouseprint
  just published (Febreze 8.8→8.1, Smucker's, Thomas', Quilted Northern, Tide 84→80, Ziploc, Cascade,
  Dole, Kroger, SeaPak, Little Debbie, Tyson, Q-Tips, Jif, Lorna Doone, Mission, Tom's of Maine…).
- **~47 GAPs** — documented by mouseprint, not in our DB. These are the **claim-creation candidates**
  (pending the go/no-go discussion). Listed below, newest first.

> **The standout convergence (already tracked):** **Febreze Air Mist 8.8→8.1 fl oz** — mouseprint
> published it 2026-06-08; our DB logged the identical change **2026-04-07** (3 evidence), ~2 months
> earlier. Strongest "two independent watchdogs, we had it first" content beat in the set.

---

## GAPS — mouseprint documents it, we don't (claim candidates)

Newest first. `~%` = computed cut. These need their own evidence before any DB write (see "Claim
creation" note at bottom). A ⚠ marks a near-miss where we track a *different* size/product of the
same brand (so it's a genuinely new event, not a dupe).

### 2026
| Brand | Product | Change | ~% | Note |
|---|---|---|---|---|
| Dawn | Platinum dish soap | 32→30 oz | 6.3% | ⚠ we track other Dawn cuts (7→6.5, 19.4→18), not this |
| Hershey's | Dark Chocolate Assortment | 29→23.9 oz | 17.6% | high-magnitude |
| Kirkland | Ultra Fabric Softener | 187→150 oz | 19.8% | high-magnitude |
| Iams | Dog Food (XL) | 44→38.5 lb | 12.5% | |
| Swiffer | Dusters | 28→24 ct | 14.3% | ⚠ we track Swiffer Wet Cloths 32→24, not Dusters |
| Oscar Mayer | Beef Franks | 16→15 oz | 6.3% | |
| Kellogg's | Corn Pops | 18.1→16.4 oz | 9.4% | ⚠ we track Corn Pops 10→7.8, not this size |
| Hungry Jack | Syrup | 27.6→24 oz | 13% | |
| Post | Premier Protein Cereal | 11→9 oz | 18.2% | high-magnitude |
| Hershey's | Snack Size Chocolate | 19.8→18 oz | 9.1% | |
| Viva | Paper Towels (double) | 94→86 sh | 8.5% | |
| Charmin | Mega Rolls Ultra Soft | 224→208 sh | 7.1% | ⚠ we track other Charmin counts |
| Finish | Ultimate Dishwashing Pods | 76→62 | 18.4% | high-magnitude |
| Scotts | Turf Builder | 5,000→4,000 sq ft | 20% | non-grocery, high-magnitude |

### 2025
| Brand | Product | Change | ~% | Note |
|---|---|---|---|---|
| Simply Orange* | *(tracked 64→46)* | — | — | *TRACKED — listed for contrast* |
| Tide | Liquid Detergent (alt size) | 250→225 oz | 10% | ⚠ we track Tide 84→80 & 92→84, not this |
| All | Free & Clear Detergent | 88→73 oz | 17% | high-magnitude |
| Bounty | Mega Rolls | 180→164 sh | 8.9% | ⚠ we track Bounty 135→123 & 98→90, not Mega |
| Viva | Paper Towels (triple) | 141→129 sh | 8.5% | |
| Kellogg's | Raisin Bran | 16.6→14.5 oz | 12.7% | ⚠ we track other Raisin Bran sizes |
| Honey Nut Cheerios | Cereal | 29→27 oz | 6.9% | verify vs any General Mills entry |
| Ghirardelli | Dark Choc Mint Squares | 12→10 | 16.7% | |
| Reynolds | Parchment Paper | 50→45 sq ft | 10% | |
| Turkey Hill | Ice Cream | 48→46 oz | 4.2% | + skimpflation angle (→"frozen dairy dessert") |
| Crystal Light | Drink Mix | 6→4 pack | 33% | high-magnitude |
| Ruffles | Potato Chips | 9→8.5 oz | 5.6% | |

### 2024
| Brand | Product | Change | ~% | Note |
|---|---|---|---|---|
| Oreo | Regular | 14.3→13.29 oz | 7.1% | ⚠ we track Oreo Thins, NOT Regular |
| Kellogg's | Froot Loops | 10.1→7.9 oz | 21.8% | ⚠ high-mag; we track Corn Pops not Froot Loops |
| Dove | Dark Chocolate | 10→7.61 oz | ~24% | high-magnitude |
| Trader Joe's | Sparkling Water | 42→33.5 oz | 20.2% | high-magnitude |
| Great Value | Whole Almonds | 30→25 oz | 16.7% | |
| Gillette | Custom Plus 3 Razors | 36→30 | 17% | |
| Brawny | Paper Towels | 120→100 sh | 16.7% | |
| Betty Crocker | Au Gratin Potatoes | 4.7→4 oz | 14.9% | |
| Maxwell House | Colombian Coffee (sm) | 10→9 oz | 10% | |
| Kellogg's | Raisin Bran Crunch | 22→20 oz | 9.1% | |
| Downy | Fabric Softener | 170→150 oz | 11.8% | |
| Ritz | Bits | 8.8→7.5 oz | 14.8% | |
| Puffs | Tissues | 56→48 | 14.3% | |
| Chex Mix | Family-size bags | 15→13.5 oz | 10% | |
| Stacy's | Pita Chips | 18→16 oz | 11.1% | |
| Campbell's | Home Style Soup | 18→15.5 oz | 13.9% | |
| Dove | Bar soap | 3.17→2.6 oz | 18% | high-magnitude |
| Lever 2000 | Bar soap | 4→3.75 oz | 6.3% | |
| Secret | Deodorant | 2.6→2.37 oz | 8.8% | |
| Tyson | Chicken patties | 10→8 ct | 20% | ⚠ we track Tyson nuggets 32→29, not patties |
| Lesser Evil | Popcorn | 5→4.6 oz | 8% | |
| Equate | Shampoo/Conditioner | 13→12 oz | 7.7% | |
| Goodman's | Macaroons | 10→9 oz | 10% | |

### 2020–2023 (selected; lower content-priority)
| Brand | Product | Change | ~% |
|---|---|---|---|
| Arm & Hammer | Sensitive Skin Detergent | 189→140 oz | 26% |
| Quilted Northern | Ultra Plush | 284→255 sh | 10.2% |
| Walgreens | Ultra Soft TP | 284→244 sh | 14.1% |
| Crisco | Vegetable Oil | 48→40 oz | 16.7% |
| Werther's | Original Hard Caramels | 34→30 oz | 11.8% |
| Duke's | Mayonnaise | 32→30 oz | 6.25% |
| Farm Rich | Mozzarella Bites | 20→15 oz | 25% |
| Umpqua | Frozen Yogurt | 56→48 oz | 14.3% |
| Sabra | Guacamole | 8→7 oz | 12.5% |
| Stella Artois | Beer Cans | 12→11.2 oz | 6.7% |
| Ortega | Taco Shells | 5.8→4.9 oz | 15.5% |
| Kettle | Potato Chips | 8.5→7.5 oz | 11.8% |
| Nutri Source | Large Breed Dog Food | 30→26 lb | 13.3% |
| Pennysticks | Pretzels | 12→10 oz | 16.7% |
| Suave | Shampoo | 30→22.5 oz | 25% (we track 30→22.7 — likely same; verify) |
| Cap'n Crunch | Cereal | 12.5→11.4 oz | ~9% |
| Quaker | Life Cereal | 24.8→22.3 oz | 10.1% |
| Pedigree | Dog Food | 50→44 lb | 12% |
| Seventh Generation | Detergent | 100→90 oz | 10% |
| Post | Honey Bunches of Oats | 14.5→12 oz | 17.2% (we track Family 23→18, not this) |
| Pantene | Conditioner | 12→10 oz | 16.7% |
| Milky Way | Fun Size | 11.24→10.65 oz | 5.3% |
| Aveeno | Lotion | 20→18 oz | 10% |
| Breton | Crackers | 8.8→7.3 oz | 17% |
| Gain | Liquid Detergent | 92→88 oz | 4.3% (we track 165→154, not this) |
| Arm & Hammer | Detergent | 75→67.5 oz | 10% |
| Hershey's | Kisses (Classic→Share) | 12→10 oz | 16.7% (⚠ matcher hit Reese's; genuine gap) |
| Dawn | Dishwashing Liquid | 8→7 oz | 12% (we track 7→6.5, not 8→7) |
| Lay's | Potato Chips (Party) | 15.25→13 oz | 15% |
| Doritos | Doritos | 9.75→9.25 oz | 5.1% |
| Tostitos | Hint of Lime | 13→11 oz | 15.4% |
| Tostitos | Hint of Guacamole | 12→11 oz | 8.3% |
| Keebler | Club Crackers | 13.7→12.5 oz | 9% |

---

## TRACKED — already in our DB (do NOT re-create; these are convergence content picks)

High-evidence DB entries that mouseprint also documents (great "independent confirmation" material):

| Brand | Change | Our evidence | Mouseprint |
|---|---|---|---|
| Folgers | 51→43.5 oz | **31** | 2022-05 |
| Gatorade | 32→28 fl oz | **28** | 2022-03 |
| Crest | 4.1→3.8 oz | **21** | 2021-12 |
| Kleenex | 65→60 ct | **20** | 2022-06 |
| Cottonelle | 340→312 ct | **15** | 2022-03 |
| Tropicana | 52→46 fl oz | **12** | 2024-08 |
| Charmin | 264→244 ct | **11** | 2022-09 |
| Gain | 165→154 oz | **9** | 2021-12 |
| Aleve | 100→90 ct | **8** | 2021-12 |
| Angel Soft | 425→320 ct | **5** | 2022-06 |
| Tide | 92→84 fl oz | 5 | 2024-04 |
| Febreze | 8.8→8.1 fl oz | 3 (logged 2 mo before MP) | 2026-06 |

…plus exact matches at evidence 1–2: Smucker's 32→30, Thomas' 20→18, Quilted Northern 295→255 &
328→295, Tide 84→80, Ziploc 280→270, Cascade 52→47, Dole 59→52, Kroger 45→40, SeaPak 16→14,
Little Debbie 8→6, Great Value coffee 11.3→9.6 & paper towels 168→120, Pure Leaf 64→59,
Simply Orange 64→46, Bounty 135→123 & 98→90, Q-Tips 1875→1750, Jif 1.5→1.1, Lorna Doone 1.5→1,
Mission 8→6, Tom's of Maine 4.7→4, DiGiorno 27.5→23.9, Green Mountain 12→10, Kashi 13→9.7,
Special K Red Berries 16.9→15.6, Charmin 363→330, Tyson nuggets 32→29, Manischewitz/Yehuda 5→4,
Oreo Thins 13.1→11.78, Pepperidge Goldfish 30→27.3 & Milano 6.25→6, M&M's 10.7→10, Folgers
Breakfast 25.4→22.6, Betty Crocker 15.25→13.25, Colgate 5.1→4.8, Darigold 64→59, Green Giant 10→8,
Hill's Science Diet 15→12.5, Corn Pops 10→7.8 & 14.6→13.1, Corn Flakes 24→18, Peet's 12→10.5,
Utz 28→26, Safeguard 4→3.2, Huggies 96→84, Keebler 11.3→9.75, Kirkland TP 425→380, Gold Peak 64→59,
Dial 21→16, Powerade 32→28, Hershey Kisses 18→16.1, Great Value PT 168→120, Dove body wash 24→20,
Dawn 7→6.5 & 19.4→18.

---

## Skimpflation / non-size candidates (separate claim track)

These are recipe/dilution/quality cuts (no clean size pair) — candidates for the **evidence-wall /
Skimpflation channel**, not size events. Verify independently before any write.

- **Reese's** — milk chocolate → composite, peanut butter → "creme" (2026-02) — *flagship; high interest*
- **Turkey Hill** ice cream → "frozen dairy dessert" (2025-07)
- **Blue Bunny** ice cream → "frozen dairy dessert" (2024-02)
- **Annie's** Shells & Cheddar reformulation (2025-04)
- **Imperial** margarine — oil 53%→48%, 70→60 cal (2025-03)
- **Smart Balance** spread — fat 64%→39% (2022–2023)
- **Wish-Bone** Italian — oil −22%, +water, +salt (2023-08)
- **Aldi** margarine — oil 51%→40% (2018, evergreen)
- **CVS / Kroger / Walgreens / Robitussin** cough syrup — concentration cut ~50% (2022-12)
- **Act** mouthwash — fluoride 0.05%→0.02% (2022-12)
- **Hungry Man** Double Chicken Bowls — protein 39→33 g (2022-10)
- **Lysol** Disinfecting Wipes — thinner substrate, 19.7→17.7 oz (2018, evergreen)

---

## Claim creation — how (pending go-ahead)

If we green-light creating claims for the gaps, the clean path (no schema change) is the same one the
public `/submit` form uses: write a `raw_items` anchor (`source_type='community_tip'` or a new
`source_type='mouseprint_ref'`) + a `pending` `claims` row per case, then they ride the normal
approve → promote pipeline. **But** every claim still needs *our own* evidence to survive review —
mouseprint is a lead, not a source we can cite. Realistic options to discuss:
1. **Seed pending claims** from the gaps (brand/size/%) and let the existing scrapers/vision backfill
   evidence — lowest effort, but claims sit unverified until real evidence lands.
2. **Targeted re-scrape** — point the Kroger/Walmart/OFF/Open-Prices scrapers + Wayback at the specific
   gap SKUs to capture real before/after listings as first-class evidence, then create claims that are
   already substantiated. Higher effort, but produces publishable events.
3. **Cherry-pick** the ~12 highest-magnitude / most on-trend gaps (Froot Loops 21.8%, Dove Dark 24%,
   Trader Joe's 20%, Crystal Light 33%, Post Premier 18%, All 17%, Hershey Dark 17.6%, Kirkland
   Softener 19.8%, Finish 18.4%, Scotts 20%) for manual evidence-backed entry + content.

**Recommendation:** option 2 or 3, not 1 — seeding bare unverified claims pollutes the review queue
and risks the data-quality flags. Decide scope before any DB write.
