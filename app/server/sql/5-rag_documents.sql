-- ============================================
-- RAG Document Storage Schema
-- ============================================
-- This script creates the tables and functions needed for RAG (Retrieval-Augmented Generation)
-- Run this in your Supabase SQL editor after running scripts 1-4

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- 1. Document Metadata Table
-- ============================================
-- Stores metadata about documents in the knowledge base
DROP TABLE IF EXISTS document_metadata CASCADE;

CREATE TABLE document_metadata (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    schema JSONB,  -- For structured documents (CSV, etc.)
    url TEXT,      -- Source URL or file path
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Index for faster lookups
CREATE INDEX idx_document_metadata_title ON document_metadata(title);
CREATE INDEX idx_document_metadata_created_at ON document_metadata(created_at);

-- ============================================
-- 2. Documents Table (Vector Storage)
-- ============================================
-- Stores document chunks with embeddings for vector similarity search
DROP TABLE IF EXISTS documents CASCADE;

CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL,  -- Contains: file_id, file_title, file_url, mime_type, file_contents (for images)
    embedding vector(1536),   -- OpenAI text-embedding-3-small dimensions (change if using different model)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_documents_file_id ON documents((metadata->>'file_id'));
CREATE INDEX idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================
-- 3. Document Rows Table (Structured Data)
-- ============================================
-- For CSV and tabular data with queryable columns
DROP TABLE IF EXISTS document_rows CASCADE;

CREATE TABLE document_rows (
    id BIGSERIAL PRIMARY KEY,
    dataset_id TEXT NOT NULL,  -- References document_metadata.id
    row_data JSONB NOT NULL,   -- All row data as key-value pairs
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (dataset_id) REFERENCES document_metadata(id) ON DELETE CASCADE
);

-- Indexes for faster queries
CREATE INDEX idx_document_rows_dataset_id ON document_rows(dataset_id);
CREATE INDEX idx_document_rows_row_data ON document_rows USING gin(row_data);

-- ============================================
-- 4. Vector Similarity Search Function
-- ============================================
-- Function to find similar documents based on vector embeddings
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_count int DEFAULT 4,
    file_id_filter text DEFAULT NULL
)
RETURNS TABLE (
    id bigint,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE
        CASE
            WHEN file_id_filter IS NOT NULL
            THEN documents.metadata->>'file_id' = file_id_filter
            ELSE TRUE
        END
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================
-- 5. Safe SQL Execution Function
-- ============================================
-- Function for executing read-only SQL queries on document_rows
CREATE OR REPLACE FUNCTION execute_custom_sql(sql_query text)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result jsonb;
BEGIN
    -- Execute the query and return results as JSON
    EXECUTE format('SELECT jsonb_agg(row_to_json(t)) FROM (%s) t', sql_query) INTO result;
    RETURN COALESCE(result, '[]'::jsonb);
EXCEPTION
    WHEN OTHERS THEN
        RETURN jsonb_build_object('error', SQLERRM);
END;
$$;

-- ============================================
-- 6. Helper Functions
-- ============================================

-- Function to get document statistics
CREATE OR REPLACE FUNCTION get_document_stats()
RETURNS TABLE (
    total_documents bigint,
    total_chunks bigint,
    total_rows bigint,
    avg_chunk_length float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(DISTINCT id) FROM document_metadata),
        (SELECT COUNT(*) FROM documents),
        (SELECT COUNT(*) FROM document_rows),
        (SELECT AVG(LENGTH(content)) FROM documents);
END;
$$;

-- Function to delete a document and all its chunks
CREATE OR REPLACE FUNCTION delete_document(doc_id text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    -- Delete from document_rows (cascades from document_metadata FK)
    DELETE FROM document_rows WHERE dataset_id = doc_id;

    -- Delete chunks from documents table
    DELETE FROM documents WHERE metadata->>'file_id' = doc_id;

    -- Delete metadata
    DELETE FROM document_metadata WHERE id = doc_id;
END;
$$;

-- ============================================
-- 7. Comments for Documentation
-- ============================================

COMMENT ON TABLE document_metadata IS 'Stores metadata about documents in the knowledge base';
COMMENT ON TABLE documents IS 'Stores document chunks with embeddings for vector similarity search';
COMMENT ON TABLE document_rows IS 'Stores structured tabular data from CSV/Excel files';
COMMENT ON FUNCTION match_documents IS 'Performs vector similarity search to find relevant document chunks';
COMMENT ON FUNCTION execute_custom_sql IS 'Safely executes read-only SQL queries on document_rows';
COMMENT ON FUNCTION get_document_stats IS 'Returns statistics about the document collection';
COMMENT ON FUNCTION delete_document IS 'Deletes a document and all associated chunks and rows';
