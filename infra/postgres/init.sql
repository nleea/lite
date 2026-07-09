-- Enable the pgvector extension for semantic search / embeddings.
-- Runs once on database initialization.
CREATE EXTENSION IF NOT EXISTS vector;
