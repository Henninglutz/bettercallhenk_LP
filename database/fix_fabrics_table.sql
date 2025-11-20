-- Fix Script: Add missing columns to fabrics table
-- This script adds the fabric_code column and any other missing columns

BEGIN;

-- Check if fabric_code exists, if not add it
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'fabric_code'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN fabric_code VARCHAR(50);
        RAISE NOTICE 'Added column: fabric_code';
    END IF;
END
$$;

-- Make fabric_code UNIQUE and NOT NULL after adding data
-- (we'll add this after the first import)

-- Check and add other potentially missing columns
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'name'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN name VARCHAR(255);
        RAISE NOTICE 'Added column: name';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'composition'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN composition TEXT;
        RAISE NOTICE 'Added column: composition';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'weight'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN weight INTEGER;
        RAISE NOTICE 'Added column: weight';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'color'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN color VARCHAR(100);
        RAISE NOTICE 'Added column: color';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'pattern'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN pattern VARCHAR(100);
        RAISE NOTICE 'Added column: pattern';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'price_category'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN price_category VARCHAR(50);
        RAISE NOTICE 'Added column: price_category';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'stock_status'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN stock_status VARCHAR(50);
        RAISE NOTICE 'Added column: stock_status';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'supplier'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN supplier VARCHAR(100) DEFAULT 'Formens';
        RAISE NOTICE 'Added column: supplier';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'origin'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN origin VARCHAR(100);
        RAISE NOTICE 'Added column: origin';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'description'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN description TEXT;
        RAISE NOTICE 'Added column: description';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'care_instructions'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN care_instructions TEXT;
        RAISE NOTICE 'Added column: care_instructions';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'category'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN category VARCHAR(100);
        RAISE NOTICE 'Added column: category';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'scrape_date'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN scrape_date TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE 'Added column: scrape_date';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'fabrics' AND column_name = 'additional_metadata'
    ) THEN
        ALTER TABLE fabrics ADD COLUMN additional_metadata JSONB DEFAULT '{}'::jsonb;
        RAISE NOTICE 'Added column: additional_metadata';
    END IF;
END
$$;

COMMIT;

-- Verify the changes
\d fabrics

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'fabrics'
ORDER BY ordinal_position;
