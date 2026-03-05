-- RPC function to update reddit_staging status from the frontend.
-- The reddit_staging table only allows writes from service_role via RLS,
-- so the anon-key frontend needs a SECURITY DEFINER function to update
-- the status column (approve / reject / dismiss) without opening the
-- entire table for public writes.

CREATE OR REPLACE FUNCTION update_staging_status(row_id uuid, new_status text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF new_status NOT IN ('promoted', 'dismissed', 'rejected') THEN
    RAISE EXCEPTION 'Invalid status: %', new_status;
  END IF;

  UPDATE reddit_staging
  SET status = new_status
  WHERE id = row_id;
END;
$$;

-- Allow anon and authenticated roles to call this function
GRANT EXECUTE ON FUNCTION update_staging_status(uuid, text) TO anon, authenticated;
