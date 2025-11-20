-- Fix for SQLAlchemy reserved 'metadata' column name
-- This script renames the 'metadata' column to 'embedding_metadata' in fabric_embeddings table
--
-- Run this on your henk_db database:
-- psql -U postgres -h localhost -p 6543 -d henk_db -f fix_metadata_column.sql

BEGIN;

-- Rename the column if it exists (old name)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabric_embeddings' AND column_name = 'metadata'
    ) THEN
        ALTER TABLE fabric_embeddings
        RENAME COLUMN metadata TO embedding_metadata;

        RAISE NOTICE 'Column renamed: metadata -> embedding_metadata';
    ELSE
        RAISE NOTICE 'Column already named embedding_metadata or does not exist';
    END IF;
END
$$;

COMMIT;

-- Verify the change
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'fabric_embeddings'
  AND column_name = 'embedding_metadata';
