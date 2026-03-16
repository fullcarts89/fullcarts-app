-- Add image storage path column to claims
-- Stores the Supabase Storage path for permanently archived evidence images
-- Format: claim-images/{claim_id}.webp

ALTER TABLE claims ADD COLUMN IF NOT EXISTS image_storage_path TEXT;

-- Create the storage bucket (via Supabase SQL)
INSERT INTO storage.buckets (id, name, public)
VALUES ('claim-images', 'claim-images', true)
ON CONFLICT (id) DO NOTHING;

-- Allow public read access (images are evidence, not private)
CREATE POLICY "Public read access for claim images"
ON storage.objects FOR SELECT
USING (bucket_id = 'claim-images');

-- Allow service role to insert/update/delete
CREATE POLICY "Service role full access for claim images"
ON storage.objects FOR ALL
USING (bucket_id = 'claim-images')
WITH CHECK (bucket_id = 'claim-images');
