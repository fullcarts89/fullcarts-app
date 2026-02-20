-- ============================================================
-- FullCarts Database Schema + Seed Data
-- Run this in Supabase SQL Editor (supabase.com → your project → SQL Editor)
-- ============================================================

-- ── PRODUCTS ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
  upc              text PRIMARY KEY,
  name             text NOT NULL,
  brand            text,
  category         text,
  current_size     numeric,
  unit             text,
  type             text,
  repeat_offender  boolean DEFAULT false,
  company_response jsonb,
  fighting_back    boolean DEFAULT false,
  created_at       timestamptz DEFAULT now()
);

-- ── EVENTS ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS events (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  upc           text REFERENCES products(upc) ON DELETE CASCADE,
  date          date,
  old_size      numeric,
  new_size      numeric,
  unit          text,
  pct           numeric,
  price_before  numeric,
  price_after   numeric,
  type          text,
  notes         text,
  created_at    timestamptz DEFAULT now()
);

-- ── SUBMISSIONS ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS submissions (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name          text,
  brand         text,
  old_size      text,
  new_size      text,
  price_before  text,
  price_after   text,
  type          text,
  status        text DEFAULT 'pending',
  created_at    timestamptz DEFAULT now()
);

-- ── REDDIT STAGING ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reddit_staging (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_url       text UNIQUE,
  subreddit        text,
  posted_utc       timestamptz,
  scraped_utc      timestamptz,
  tier             text,
  title            text,
  brand            text,
  product_hint     text,
  old_size         numeric,
  old_unit         text,
  new_size         numeric,
  new_unit         text,
  old_price        numeric,
  new_price        numeric,
  explicit_from_to boolean,
  fields_found     integer,
  score            integer,
  num_comments     integer,
  status           text DEFAULT 'pending',
  created_at       timestamptz DEFAULT now()
);

-- ── CONTRIBUTORS ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS contributors (
  id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  username  text UNIQUE,
  reports   integer DEFAULT 0,
  verified  integer DEFAULT 0,
  streak    integer DEFAULT 0,
  level     text DEFAULT 'Scout'
);

-- ── CONFIRMATIONS ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS confirmations (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  upc        text REFERENCES products(upc) ON DELETE CASCADE,
  session_id text,
  created_at timestamptz DEFAULT now()
);

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE reddit_staging ENABLE ROW LEVEL SECURITY;
ALTER TABLE contributors ENABLE ROW LEVEL SECURITY;
ALTER TABLE confirmations ENABLE ROW LEVEL SECURITY;

-- Products & Events: anyone can read
CREATE POLICY "Public read products" ON products FOR SELECT USING (true);
CREATE POLICY "Public read events" ON events FOR SELECT USING (true);

-- Submissions: anyone can insert, only admin can read/update
CREATE POLICY "Anyone can submit" ON submissions FOR INSERT WITH CHECK (true);
CREATE POLICY "Admin reads submissions" ON submissions FOR SELECT USING (auth.role() = 'authenticated');

-- Reddit staging: service role only (scraper + dashboard)
CREATE POLICY "Service role manages staging" ON reddit_staging FOR ALL USING (auth.role() = 'service_role');
-- Also allow public read so dashboard can view
CREATE POLICY "Public read staging" ON reddit_staging FOR SELECT USING (true);

-- Contributors: anyone can read
CREATE POLICY "Public read contributors" ON contributors FOR SELECT USING (true);

-- Confirmations: anyone can insert and read
CREATE POLICY "Anyone can confirm" ON confirmations FOR INSERT WITH CHECK (true);
CREATE POLICY "Public read confirmations" ON confirmations FOR SELECT USING (true);

-- ============================================================
-- SEED: PRODUCTS
-- ============================================================

INSERT INTO products (upc, name, brand, category, current_size, unit, type, repeat_offender, company_response, fighting_back) VALUES
('048500205020', 'Tropicana Pure Premium OJ', 'Tropicana', 'Beverages', 52, 'fl oz', 'shrinkflation', true, '{"status":"deflected","quote":"We''ve adjusted some of our product sizes as part of ongoing portfolio management to deliver the best value to consumers.","source":"Tropicana Communications, Q1 2022","url":null}', false),
('028400090506', 'Doritos Nacho Cheese', 'Frito-Lay', 'Snacks', 9.25, 'oz', 'downsizing', true, '{"status":"deflected","quote":"Frito-Lay periodically evaluates our product portfolio and packaging to meet evolving consumer preferences and market conditions.","source":"Frito-Lay PR Statement, 2022","url":null}', false),
('052000337842', 'Gatorade Thirst Quencher', 'Gatorade', 'Beverages', 28, 'fl oz', 'shrinkflation', false, null, false),
('037000753599', 'Bounty Select-A-Size', 'Bounty', 'Paper Goods', 83, 'sheets', 'count-cut', true, '{"status":"deflected","quote":"We are always looking for ways to balance product quality with rising raw material and production costs while keeping products accessible.","source":"P&G Investor Relations, FY2023","url":null}', false),
('048001214823', 'Hellmann''s Real Mayonnaise', 'Unilever', 'Condiments', 32, 'oz', 'shrinkflation', true, '{"status":"restored","quote":"Following consumer feedback, we have returned Hellmann''s Real Mayonnaise to its original 32oz size across all US retail channels.","source":"Unilever Consumer Affairs, Jan 2024","url":null}', true),
('037600107556', 'Skippy Creamy Peanut Butter', 'Hormel', 'Pantry', 16.3, 'oz', 'downsizing', true, null, false),
('025500012237', 'Folgers Classic Roast', 'Folgers', 'Beverages', 43.5, 'oz', 'downsizing', true, null, false),
('030772031674', 'Charmin Ultra Soft', 'P&G', 'Paper Goods', 244, 'sheets', 'downsizing', true, '{"status":"deflected","quote":"We continuously look for opportunities to improve efficiency and deliver value, which sometimes results in changes to product configurations.","source":"P&G Spokesperson, 2022","url":null}', false),
('044000001803', 'Wheat Thins Original', 'Nabisco', 'Snacks', 9.1, 'oz', 'shrinkflation', false, null, false),
('037000805403', 'Tide Pods Laundry', 'P&G', 'Household', 57, 'count', 'count-cut', false, null, false),
('051500280027', 'Jif Creamy Peanut Butter', 'J.M. Smucker', 'Pantry', 16, 'oz', 'shrinkflation', false, null, false),
('077567221827', 'Breyers Natural Vanilla Ice Cream', 'Breyers', 'Dairy', 1.5, 'qt', 'shrinkflation', true, '{"status":"deflected","quote":"Unilever has made adjustments to certain ice cream sizes to reflect the realities of ingredient and logistics costs in today''s environment.","source":"Unilever Annual Report, 2022","url":null}', false),
('074570940219', 'Häagen-Dazs Vanilla', 'Nestlé', 'Dairy', 14, 'fl oz', 'shrinkflation', true, '{"status":"deflected","quote":"The 14 fl oz size aligns our US product with global sizing standards for the brand and allows us to maintain our quality standards.","source":"Nestlé USA Media Statement, 2021","url":null}', false),
('036000044569', 'Cottonelle Ultra Clean', 'Kimberly-Clark', 'Paper Goods', 141, 'sheets', 'count-cut', true, null, false),
('021000009480', 'Kraft Mac & Cheese Original', 'Kraft Heinz', 'Pantry', 7.25, 'oz', 'shrinkflation', false, '{"status":"deflected","quote":"We are committed to providing families with quality, affordable meals and regularly evaluate ways to do so in a challenging cost environment.","source":"Kraft Heinz Communications, 2023","url":null}', false),
('028400090414', 'Lay''s Classic Potato Chips', 'Frito-Lay', 'Snacks', 7.75, 'oz', 'downsizing', false, null, false),
('016000275287', 'Cheerios Original', 'General Mills', 'Cereal', 18, 'oz', 'downsizing', true, '{"status":"deflected","quote":"General Mills is committed to transparency and continues to evaluate our portfolio to provide consumers with the best value possible given current market conditions.","source":"General Mills Spokesperson, 2022","url":null}', false),
('037000291008', 'Dawn Dish Soap Original', 'P&G', 'Household', 19.4, 'fl oz', 'shrinkflation', false, null, false),
('044000021541', 'Oreo Original', 'Nabisco', 'Snacks', 13.29, 'oz', 'shrinkflation', true, '{"status":"deflected","quote":"Mondelez International regularly reviews product configurations across our portfolio to best serve consumers and retail partners.","source":"Mondelez IR Statement, 2021","url":null}', false),
('036000426137', 'Huggies Snug & Dry Size 4', 'Kimberly-Clark', 'Baby', 132, 'count', 'count-cut', true, null, false),
('054000000285', 'Scott 1000 Toilet Paper', 'Kimberly-Clark', 'Paper Goods', 1000, 'sheets', 'skimpflation', true, '{"status":"deflected","quote":"We are always looking for ways to deliver value to consumers, which may involve changes to product specifications over time.","source":"Kimberly-Clark Spokesperson, 2021","url":null}', false),
('096619144372', 'Kirkland Signature Almonds', 'Costco', 'Snacks', 48, 'oz', 'shrinkflation', false, null, false),
('043000275535', 'Stove Top Stuffing Mix', 'Kraft Heinz', 'Pantry', 6, 'oz', 'shrinkflation', false, null, false),
('070470001011', 'Yoplait Original Strawberry', 'General Mills', 'Dairy', 6, 'oz', 'skimpflation', true, null, false),
('611269991023', 'Red Bull Energy Drink', 'Red Bull', 'Beverages', 8.4, 'fl oz', 'price-hike', false, null, false)
ON CONFLICT (upc) DO NOTHING;

-- ============================================================
-- SEED: EVENTS
-- ============================================================

INSERT INTO events (upc, date, old_size, new_size, unit, pct, price_before, price_after, type, notes) VALUES
('048500205020', '2022-01-01', 64, 52, 'fl oz', 18.75, 3.99, 4.99, 'shrinkflation', 'New carton design debuted same quarter.'),
('048500205020', '2019-06-01', 89, 64, 'fl oz', 28.09, 4.49, 3.99, 'shrinkflation', 'Earlier reduction from 89oz jug to 64oz carton.'),
('052000337842', '2021-03-01', 32, 28, 'fl oz', 12.5, 1.79, 1.99, 'shrinkflation', 'Price went up too. Double whammy!'),
('037000753599', '2023-01-01', 99, 83, 'sheets', 16.16, 4.29, 4.49, 'count-cut', 'Package looked identical. Sneaky!'),
('037000753599', '2020-06-01', 110, 99, 'sheets', 10, 3.99, 4.29, 'count-cut', 'First documented reduction.'),
('048001214823', '2022-06-01', 32, 30, 'oz', 6.25, 5.49, 5.29, 'shrinkflation', 'Was 36oz before 2018. Keeps shrinking!'),
('048001214823', '2018-01-01', 36, 32, 'oz', 11.11, 4.99, 5.49, 'shrinkflation', 'First modern-era reduction.'),
('037600107556', '2021-09-01', 18, 16.3, 'oz', 9.44, 3.99, 4.19, 'downsizing', 'Deeper dent in the bottom of the jar to hide the change.'),
('025500012237', '2021-01-01', 51, 43.5, 'oz', 14.71, 11.99, 11.99, 'downsizing', 'Same price, smaller canister. Classic move.'),
('030772031674', '2022-03-01', 284, 244, 'sheets', 14.08, 18.99, 19.99, 'downsizing', 'Package grew TALLER while sheets dropped. Optical illusion!'),
('030772031674', '2019-06-01', 308, 284, 'sheets', 7.79, 16.99, 18.99, 'downsizing', 'Prior reduction.'),
('044000001803', '2023-02-01', 10, 9.1, 'oz', 9, 4.29, 4.29, 'shrinkflation', 'Box dimensions unchanged.'),
('037000805403', '2021-11-01', 72, 57, 'count', 20.83, 19.99, 21.99, 'count-cut', 'Lost 15 pods! Bag looks the same.'),
('051500280027', '2022-04-01', 18, 16, 'oz', 11.11, 3.99, 4.39, 'shrinkflation', 'Jar got a redesign and a diet.'),
('077567221827', '2022-01-01', 1.75, 1.5, 'qt', 14.29, 5.99, 6.29, 'shrinkflation', 'Third reduction in a decade!'),
('077567221827', '2018-01-01', 2, 1.75, 'qt', 12.5, 5.49, 5.99, 'shrinkflation', 'Second reduction.'),
('074570940219', '2021-06-01', 16, 14, 'fl oz', 12.5, 5.49, 5.99, 'shrinkflation', 'The "pint" is no longer a pint!'),
('036000044569', '2023-01-01', 162, 141, 'sheets', 12.96, 17.99, 18.99, 'count-cut', '21 fewer sheets per roll.'),
('021000009480', '2023-06-01', 7.5, 7.25, 'oz', 3.33, 1.79, 1.89, 'shrinkflation', 'First reduction of the blue box in decades!'),
('016000275287', '2022-01-01', 20.35, 18, 'oz', 11.55, 5.29, 5.49, 'downsizing', 'Box same height. Interior bag is smaller.'),
('037000291008', '2022-09-01', 21.6, 19.4, 'fl oz', 10, 3.79, 3.99, 'shrinkflation', 'Identical bottle silhouette.'),
('044000021541', '2021-01-01', 14.3, 13.29, 'oz', 7.06, 4.99, 5.49, 'shrinkflation', 'Fewer cookies per row.'),
('036000426137', '2022-06-01', 144, 132, 'count', 8.33, 42.99, 44.99, 'count-cut', 'Same bag, fewer diapers.'),
('054000000285', '2021-03-01', 1000, 1000, 'sheets', 18, 17.99, 19.99, 'skimpflation', 'Count stayed, but each sheet got physically smaller. 4.5in to 4.1in!'),
('028400090414', '2022-11-01', 8, 7.75, 'oz', 3.13, 4.79, 4.99, 'downsizing', 'More air, fewer chips.'),
('043000275535', '2022-01-01', 6.5, 6, 'oz', 7.69, 3.29, 3.49, 'shrinkflation', 'Servings dropped from 6 to 5.5.');

-- ============================================================
-- SEED: CONTRIBUTORS
-- ============================================================

INSERT INTO contributors (username, reports, verified, streak, level) VALUES
('shrink_detective_42', 47, 39, 21, 'Elite'),
('cart_watcher',        38, 31, 14, 'Elite'),
('grocery_vigilante',   29, 24,  9, 'Pro'),
('oz_counter',          22, 17,  6, 'Pro'),
('PackageLiesAccount',  18, 14,  4, 'Pro'),
('less_chips_more_air', 14, 10,  3, 'Scout'),
('redditor_9182',       11,  8,  2, 'Scout'),
('invisible_shrink',     8,  5,  1, 'Scout')
ON CONFLICT (username) DO NOTHING;
