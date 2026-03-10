-- FullCarts: Featured Articles table
-- Curated news articles for the public website "In the News" section.
-- Admin reviews scraped news items and promotes them here.

CREATE TABLE featured_articles (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    raw_item_id     UUID REFERENCES raw_items(id),
    title           TEXT NOT NULL,
    summary         TEXT,
    source_url      TEXT NOT NULL,
    source_name     TEXT,
    published_at    TIMESTAMPTZ,
    image_url       TEXT,
    status          TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'featured', 'archived')),
    featured_at     TIMESTAMPTZ,
    featured_by     UUID REFERENCES auth.users(id),
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_featured_articles_status ON featured_articles (status);
CREATE INDEX idx_featured_articles_featured_at ON featured_articles (featured_at DESC)
    WHERE featured_at IS NOT NULL;
CREATE INDEX idx_featured_articles_raw_item ON featured_articles (raw_item_id)
    WHERE raw_item_id IS NOT NULL;
