-- Delete legacy USDA records that used the old source_id format
-- (usda_{upc}_{fdc_id}) without a release date suffix.
-- These 877K rows were superseded by the re-run which uses
-- usda_{upc}_{fdc_id}_{release_date} format (~5.35M rows).
--
-- Old format example: usda_00012345_67890
-- New format example: usda_00012345_67890_2022-10-28

DELETE FROM raw_items
WHERE source_type = 'usda'
  AND source_id !~ '_\d{4}-\d{2}-\d{2}$';
