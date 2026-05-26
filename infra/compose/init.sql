-- Basirah Corpus Database Schema
-- Stores normalized corpus records with canonical references

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main corpus table
CREATE TABLE IF NOT EXISTS corpus (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type VARCHAR(20) NOT NULL CHECK (source_type IN ('quran', 'bukhari', 'muslim')),
    reference VARCHAR(50) NOT NULL,
    text_arabic TEXT,
    text_english TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_corpus_source_type ON corpus(source_type);
CREATE INDEX IF NOT EXISTS idx_corpus_reference ON corpus(reference);
CREATE INDEX IF NOT EXISTS idx_corpus_metadata ON corpus USING GIN(metadata);
CREATE UNIQUE INDEX IF NOT EXISTS idx_corpus_source_ref ON corpus(source_type, reference);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_corpus_updated_at
    BEFORE UPDATE ON corpus
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Query logs for analytics
CREATE TABLE IF NOT EXISTS query_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question TEXT NOT NULL,
    retrieved_count INTEGER,
    response_time_ms INTEGER,
    confidence_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at DESC);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO basirah;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO basirah;
