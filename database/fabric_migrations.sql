-- HENK Fabric Database Schema
-- PostgreSQL with pgvector extension for RAG functionality

-- ============================================================================
-- STEP 1: Enable Extensions
-- ============================================================================

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable uuid extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ============================================================================
-- STEP 2: Create Core Tables
-- ============================================================================

-- Table: fabrics
-- Stores core fabric information
CREATE TABLE IF NOT EXISTS fabrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fabric_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255),
    composition TEXT,
    weight INTEGER, -- grams per square meter
    color VARCHAR(100),
    pattern VARCHAR(100),
    price_category VARCHAR(50),
    stock_status VARCHAR(50),
    supplier VARCHAR(100) DEFAULT 'Formens',
    origin VARCHAR(100),
    description TEXT,
    care_instructions TEXT,
    category VARCHAR(100),

    -- Metadata
    scrape_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Additional metadata as JSONB
    additional_metadata JSONB DEFAULT '{}'::jsonb,

    -- Indexes
    CONSTRAINT valid_weight CHECK (weight IS NULL OR weight > 0)
);

-- Add comment
COMMENT ON TABLE fabrics IS 'Core fabric information scraped from Formens B2B platform';


-- Table: fabric_seasons
-- Many-to-many relationship for fabric seasons
CREATE TABLE IF NOT EXISTS fabric_seasons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fabric_id UUID NOT NULL REFERENCES fabrics(id) ON DELETE CASCADE,
    season VARCHAR(20) NOT NULL CHECK (season IN ('spring', 'summer', 'fall', 'winter')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(fabric_id, season)
);

COMMENT ON TABLE fabric_seasons IS 'Seasons suitable for each fabric';


-- Table: fabric_images
-- Stores fabric image information
CREATE TABLE IF NOT EXISTS fabric_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fabric_id UUID NOT NULL REFERENCES fabrics(id) ON DELETE CASCADE,
    image_url TEXT,
    local_path TEXT,
    image_type VARCHAR(50), -- 'primary', 'detail', 'texture', etc.
    width INTEGER,
    height INTEGER,
    file_size INTEGER, -- bytes
    format VARCHAR(10), -- 'JPEG', 'PNG', etc.

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE fabric_images IS 'Fabric images and their storage information';


-- Table: fabric_categories
-- Hierarchical fabric categories
CREATE TABLE IF NOT EXISTS fabric_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES fabric_categories(id) ON DELETE SET NULL,

    -- Occasions suitable for this category
    occasions JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE fabric_categories IS 'Hierarchical categories for organizing fabrics';

-- Insert default categories
INSERT INTO fabric_categories (name, slug, description, occasions) VALUES
    ('Ceremony Suits', 'ceremony', 'Fabrics for wedding and formal ceremonies', '["wedding", "formal_event", "gala"]'::jsonb),
    ('Business Suits', 'business', 'Professional business attire fabrics', '["business", "office", "professional"]'::jsonb),
    ('Casual Wear', 'casual', 'Smart casual and weekend fabrics', '["casual", "smart_casual", "weekend"]'::jsonb),
    ('Seasonal Collections', 'seasonal', 'Special seasonal fabric collections', '["varied"]'::jsonb)
ON CONFLICT (slug) DO NOTHING;


-- ============================================================================
-- STEP 3: RAG / Vector Search Tables
-- ============================================================================

-- Table: fabric_embeddings
-- Stores vector embeddings for RAG functionality
CREATE TABLE IF NOT EXISTS fabric_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fabric_id UUID NOT NULL REFERENCES fabrics(id) ON DELETE CASCADE,
    chunk_id VARCHAR(255) UNIQUE NOT NULL,
    chunk_type VARCHAR(50) NOT NULL CHECK (chunk_type IN ('characteristics', 'visual', 'usage', 'technical')),
    content TEXT NOT NULL,

    -- Vector embedding (OpenAI text-embedding-3-small = 1536 dimensions)
    embedding vector(1536),

    -- Chunk metadata
    embedding_metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE fabric_embeddings IS 'Vector embeddings for fabric data chunks used in RAG';


-- ============================================================================
-- STEP 4: Outfit Generation Tables
-- ============================================================================

-- Table: generated_outfits
-- Stores DALL-E generated outfit information
CREATE TABLE IF NOT EXISTS generated_outfits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    outfit_id VARCHAR(100) UNIQUE NOT NULL,

    -- Specification
    occasion VARCHAR(100) NOT NULL,
    season VARCHAR(20) NOT NULL,
    style_preferences JSONB DEFAULT '[]'::jsonb,
    color_preferences JSONB DEFAULT '[]'::jsonb,
    pattern_preferences JSONB DEFAULT '[]'::jsonb,
    additional_notes TEXT,

    -- Generation details
    dalle_prompt TEXT NOT NULL,
    revised_prompt TEXT,
    image_url TEXT,
    local_image_path TEXT,

    -- Metadata
    generation_metadata JSONB DEFAULT '{}'::jsonb,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE generated_outfits IS 'DALL-E generated outfit visualizations';


-- Table: outfit_fabrics
-- Many-to-many relationship between outfits and fabrics
CREATE TABLE IF NOT EXISTS outfit_fabrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    outfit_id UUID NOT NULL REFERENCES generated_outfits(id) ON DELETE CASCADE,
    fabric_id UUID NOT NULL REFERENCES fabrics(id) ON DELETE CASCADE,
    usage_type VARCHAR(50), -- 'jacket', 'trousers', 'vest', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(outfit_id, fabric_id, usage_type)
);

COMMENT ON TABLE outfit_fabrics IS 'Fabrics used in generated outfits';


-- ============================================================================
-- STEP 5: Analytics and Tracking Tables
-- ============================================================================

-- Table: fabric_recommendations
-- Track fabric recommendations made to users
CREATE TABLE IF NOT EXISTS fabric_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255),
    user_query TEXT NOT NULL,
    query_embedding vector(1536),

    -- Results
    recommended_fabrics JSONB DEFAULT '[]'::jsonb, -- Array of fabric IDs and scores

    -- Feedback
    user_feedback INTEGER CHECK (user_feedback BETWEEN 1 AND 5),
    selected_fabric_id UUID REFERENCES fabrics(id) ON DELETE SET NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE fabric_recommendations IS 'Tracking of fabric recommendations for analytics';


-- ============================================================================
-- STEP 6: Create Indexes for Performance
-- ============================================================================

-- Fabrics table indexes
CREATE INDEX IF NOT EXISTS idx_fabrics_code ON fabrics(fabric_code);
CREATE INDEX IF NOT EXISTS idx_fabrics_category ON fabrics(category);
CREATE INDEX IF NOT EXISTS idx_fabrics_composition ON fabrics(composition);
CREATE INDEX IF NOT EXISTS idx_fabrics_weight ON fabrics(weight);
CREATE INDEX IF NOT EXISTS idx_fabrics_color ON fabrics(color);
CREATE INDEX IF NOT EXISTS idx_fabrics_pattern ON fabrics(pattern);
CREATE INDEX IF NOT EXISTS idx_fabrics_supplier ON fabrics(supplier);
CREATE INDEX IF NOT EXISTS idx_fabrics_stock_status ON fabrics(stock_status);
CREATE INDEX IF NOT EXISTS idx_fabrics_created_at ON fabrics(created_at DESC);

-- GIN index for JSONB metadata search
CREATE INDEX IF NOT EXISTS idx_fabrics_metadata ON fabrics USING GIN (additional_metadata);

-- Fabric seasons indexes
CREATE INDEX IF NOT EXISTS idx_fabric_seasons_fabric ON fabric_seasons(fabric_id);
CREATE INDEX IF NOT EXISTS idx_fabric_seasons_season ON fabric_seasons(season);

-- Fabric images indexes
CREATE INDEX IF NOT EXISTS idx_fabric_images_fabric ON fabric_images(fabric_id);
CREATE INDEX IF NOT EXISTS idx_fabric_images_type ON fabric_images(image_type);

-- Fabric categories indexes
CREATE INDEX IF NOT EXISTS idx_fabric_categories_slug ON fabric_categories(slug);
CREATE INDEX IF NOT EXISTS idx_fabric_categories_parent ON fabric_categories(parent_id);

-- Fabric embeddings indexes
CREATE INDEX IF NOT EXISTS idx_fabric_embeddings_fabric ON fabric_embeddings(fabric_id);
CREATE INDEX IF NOT EXISTS idx_fabric_embeddings_chunk_type ON fabric_embeddings(chunk_type);

-- Vector similarity search index (HNSW for fast approximate nearest neighbor search)
CREATE INDEX IF NOT EXISTS idx_fabric_embeddings_vector ON fabric_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Alternative: IVFFlat index (use if HNSW not available)
-- CREATE INDEX IF NOT EXISTS idx_fabric_embeddings_vector ON fabric_embeddings
-- USING ivfflat (embedding vector_cosine_ops)
-- WITH (lists = 100);

-- GIN index for metadata
CREATE INDEX IF NOT EXISTS idx_fabric_embeddings_metadata ON fabric_embeddings USING GIN (metadata);

-- Generated outfits indexes
CREATE INDEX IF NOT EXISTS idx_outfits_outfit_id ON generated_outfits(outfit_id);
CREATE INDEX IF NOT EXISTS idx_outfits_occasion ON generated_outfits(occasion);
CREATE INDEX IF NOT EXISTS idx_outfits_season ON generated_outfits(season);
CREATE INDEX IF NOT EXISTS idx_outfits_generated_at ON generated_outfits(generated_at DESC);

-- Outfit fabrics indexes
CREATE INDEX IF NOT EXISTS idx_outfit_fabrics_outfit ON outfit_fabrics(outfit_id);
CREATE INDEX IF NOT EXISTS idx_outfit_fabrics_fabric ON outfit_fabrics(fabric_id);

-- Fabric recommendations indexes
CREATE INDEX IF NOT EXISTS idx_recommendations_session ON fabric_recommendations(session_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_created_at ON fabric_recommendations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_vector ON fabric_recommendations
USING hnsw (query_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);


-- ============================================================================
-- STEP 7: Create Views for Common Queries
-- ============================================================================

-- View: fabrics_with_details
-- Join fabrics with their seasons and images
CREATE OR REPLACE VIEW fabrics_with_details AS
SELECT
    f.*,
    ARRAY_AGG(DISTINCT fs.season) FILTER (WHERE fs.season IS NOT NULL) AS seasons,
    ARRAY_AGG(DISTINCT fi.local_path) FILTER (WHERE fi.local_path IS NOT NULL) AS image_paths,
    COUNT(DISTINCT fi.id) AS image_count
FROM fabrics f
LEFT JOIN fabric_seasons fs ON f.id = fs.fabric_id
LEFT JOIN fabric_images fi ON f.id = fi.fabric_id
GROUP BY f.id;

COMMENT ON VIEW fabrics_with_details IS 'Fabrics with aggregated seasons and images';


-- View: outfit_details
-- Join outfits with their fabrics
CREATE OR REPLACE VIEW outfit_details AS
SELECT
    o.*,
    ARRAY_AGG(DISTINCT f.fabric_code) FILTER (WHERE f.fabric_code IS NOT NULL) AS fabric_codes,
    ARRAY_AGG(DISTINCT of.usage_type) FILTER (WHERE of.usage_type IS NOT NULL) AS fabric_usages
FROM generated_outfits o
LEFT JOIN outfit_fabrics of ON o.id = of.outfit_id
LEFT JOIN fabrics f ON of.fabric_id = f.id
GROUP BY o.id;

COMMENT ON VIEW outfit_details IS 'Outfits with aggregated fabric information';


-- ============================================================================
-- STEP 8: Create Useful Functions
-- ============================================================================

-- Function: update_updated_at_column
-- Automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- Function: search_fabrics_by_vector
-- Perform vector similarity search
CREATE OR REPLACE FUNCTION search_fabrics_by_vector(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    fabric_id UUID,
    fabric_code VARCHAR,
    chunk_type VARCHAR,
    content TEXT,
    similarity float
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        fe.fabric_id,
        f.fabric_code,
        fe.chunk_type,
        fe.content,
        1 - (fe.embedding <=> query_embedding) AS similarity
    FROM fabric_embeddings fe
    JOIN fabrics f ON f.id = fe.fabric_id
    WHERE 1 - (fe.embedding <=> query_embedding) > match_threshold
    ORDER BY fe.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION search_fabrics_by_vector IS 'Search fabrics by vector similarity';


-- ============================================================================
-- STEP 9: Create Triggers
-- ============================================================================

-- Trigger: Update updated_at on fabrics
CREATE TRIGGER update_fabrics_updated_at
    BEFORE UPDATE ON fabrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Update updated_at on fabric_images
CREATE TRIGGER update_fabric_images_updated_at
    BEFORE UPDATE ON fabric_images
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Update updated_at on fabric_categories
CREATE TRIGGER update_fabric_categories_updated_at
    BEFORE UPDATE ON fabric_categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Update updated_at on fabric_embeddings
CREATE TRIGGER update_fabric_embeddings_updated_at
    BEFORE UPDATE ON fabric_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- STEP 10: Grant Permissions (adjust as needed)
-- ============================================================================

-- Example: Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO henk_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO henk_app;


-- ============================================================================
-- Migration Complete
-- ============================================================================

-- Verify installation
DO $$
BEGIN
    RAISE NOTICE 'HENK Fabric Database Schema installed successfully!';
    RAISE NOTICE 'Tables created: fabrics, fabric_seasons, fabric_images, fabric_categories, fabric_embeddings, generated_outfits, outfit_fabrics, fabric_recommendations';
    RAISE NOTICE 'Vector extension enabled: pgvector';
    RAISE NOTICE 'Indexes created for performance optimization';
    RAISE NOTICE 'Ready for fabric data ingestion and RAG queries';
END $$;
