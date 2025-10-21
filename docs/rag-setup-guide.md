# RAG Database Setup and Document Ingestion Guide

## Overview

This guide explains how to set up the RAG (Retrieval-Augmented Generation) database and add documents to your knowledge base.

## Prerequisites

- Supabase project configured
- Environment variables set in `app/server/.env`
- pgvector extension available in your Supabase project

## Step 1: Create Database Schema

Run the SQL script to create the necessary tables and functions:

```bash
# In your Supabase SQL editor, run:
# app/server/sql/5-rag_documents.sql
```

This creates:
- `document_metadata` - Document metadata and information
- `documents` - Document chunks with vector embeddings
- `document_rows` - Structured tabular data
- `match_documents()` - Vector similarity search function
- `execute_custom_sql()` - Safe SQL execution function
- Helper functions for stats and deletion

## Step 2: Verify Database Setup

Check that the tables were created correctly:

```sql
-- In Supabase SQL editor
SELECT * FROM get_document_stats();
```

You should see:
```
total_documents | total_chunks | total_rows | avg_chunk_length
---------------+-------------+------------+-----------------
             0 |           0 |          0 |            NULL
```

## Step 3: Install Dependencies

The ingestion script requires additional dependencies:

```bash
cd app/server
pip install pandas httpx
# or
uv add pandas httpx
```

## Adding Documents to the RAG Database

### Method 1: Using the Ingestion Script (Recommended)

#### Add Text Documents

```bash
cd app/server

# Add a markdown file
python document_ingestion.py add-text "../README.md" --title "Project README"

# Add a text file with custom URL
python document_ingestion.py add-text "docs/guide.txt" \
    --title "User Guide" \
    --url "https://example.com/docs/guide"

# Add with custom ID
python document_ingestion.py add-text "api-docs.md" \
    --title "API Documentation" \
    --id "api-docs-v1"
```

#### Add Images

```bash
# Add an image with description
python document_ingestion.py add-image "diagrams/architecture.png" \
    --title "System Architecture" \
    --description "System architecture diagram showing components and data flow"

# Add screenshot
python document_ingestion.py add-image "screenshots/ui.png" \
    --title "UI Screenshot"
```

#### Add CSV Datasets

```bash
# Add CSV as structured data
python document_ingestion.py add-csv "data/sales.csv" \
    --title "Q4 Sales Data"

# The CSV will be:
# 1. Searchable via RAG (description embedded)
# 2. Queryable via SQL (rows in document_rows table)
```

#### Add Content from URLs

```bash
# Fetch and add content from web
python document_ingestion.py add-url "https://docs.example.com/api" \
    --title "API Documentation"
```

#### List Documents

```bash
# View all documents in the knowledge base
python document_ingestion.py list
```

Output:
```
Found 3 documents:

  ID: api-docs-v1
  Title: API Documentation
  URL: https://example.com/docs/api
  Created: 2025-01-20T10:30:00

  ID: 550e8400-e29b-41d4-a716-446655440000
  Title: System Architecture
  URL: file:///path/to/diagrams/architecture.png
  Created: 2025-01-20T10:25:00
  ...
```

#### Delete Documents

```bash
# Delete a document and all its chunks
python document_ingestion.py delete <document_id>
```

#### View Statistics

```bash
# Get collection stats
python document_ingestion.py stats
```

Output:
```
Document Collection Statistics:
  Total Documents: 15
  Total Chunks: 234
  Total Rows (structured data): 1,543
  Avg Chunk Length: 892 chars
```

### Method 2: Programmatic API

You can also use the ingestion class directly in your Python code:

```python
from document_ingestion import DocumentIngestion
import asyncio

async def add_my_docs():
    ingestion = DocumentIngestion()

    # Add multiple documents
    docs = [
        ('docs/intro.md', 'Introduction'),
        ('docs/api.md', 'API Reference'),
        ('docs/examples.md', 'Examples'),
    ]

    for file_path, title in docs:
        doc_id = await ingestion.add_text_document(file_path, title=title)
        print(f"Added: {title} ({doc_id})")

# Run the ingestion
asyncio.run(add_my_docs())
```

### Method 3: Direct Database Insert

For advanced users, you can insert directly via SQL:

```sql
-- 1. Insert metadata
INSERT INTO document_metadata (id, title, url)
VALUES ('my-doc-id', 'My Document', 'https://example.com/doc');

-- 2. Insert document chunks with embeddings
-- Note: You need to generate embeddings externally
INSERT INTO documents (content, embedding, metadata)
VALUES (
    'This is the document content...',
    '[0.1, 0.2, 0.3, ...]'::vector,  -- Your embedding vector
    '{"file_id": "my-doc-id", "file_title": "My Document", "file_url": "https://example.com/doc"}'::jsonb
);
```

## Configuration

### Embedding Model Settings

Your embedding model configuration in `.env`:

```bash
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=your-key-here
EMBEDDING_MODEL_CHOICE=text-embedding-3-small  # 1536 dimensions
```

### Important: Vector Dimensions

**The embedding vector dimension MUST match your database schema!**

- `text-embedding-3-small`: 1536 dimensions (default in SQL script)
- `text-embedding-3-large`: 3072 dimensions
- `nomic-embed-text` (Ollama): 768 dimensions

If using a different model, update the SQL script:

```sql
-- Change this line in 5-rag_documents.sql
embedding vector(1536),   -- Change 1536 to your model's dimensions
```

Then recreate the table and index.

## Chunk Configuration

You can adjust chunking behavior in `document_ingestion.py`:

```python
self.chunk_size = 1000      # Characters per chunk
self.chunk_overlap = 200    # Overlap between chunks
```

**Recommendations:**
- **Small chunks (500-800)**: Better precision, more API calls
- **Medium chunks (1000-1500)**: Balanced approach (default)
- **Large chunks (2000-3000)**: Better context, less precision

## How RAG Works in Your Application

### 1. User Asks Question

```
User: "How do I set up authentication?"
```

### 2. Agent Calls RAG Tool

```python
# In tools.py
result = await retrieve_relevant_documents_tool(
    supabase,
    embedding_client,
    "How do I set up authentication?"
)
```

### 3. Vector Search

```python
# Generate embedding for query
query_embedding = await get_embedding(query, embedding_client)

# Find similar chunks
result = supabase.rpc('match_documents', {
    'query_embedding': query_embedding,
    'match_count': 4
}).execute()
```

### 4. Agent Uses Context

The agent receives the top 4 relevant chunks and uses them to answer the question accurately.

## Best Practices

### Document Organization

1. **Use descriptive titles**: Help with search and organization
2. **Include source URLs**: Track document provenance
3. **Tag with metadata**: Use custom fields in metadata JSONB
4. **Version documents**: Use IDs with version suffixes (e.g., `api-v1`, `api-v2`)

### Chunking Strategy

1. **Respect boundaries**: Script tries to chunk at sentence boundaries
2. **Overlap for context**: 200-char overlap ensures continuity
3. **Not too small**: Avoid chunks < 200 chars
4. **Not too large**: Keep chunks < 2000 chars for best results

### Performance

1. **Batch operations**: Use batch inserts for large datasets
2. **Index maintenance**: Let Supabase maintain vector indexes
3. **Monitor costs**: Embedding generation incurs API costs
4. **Cache when possible**: Don't re-embed unchanged documents

### Security

1. **Validate inputs**: Sanitize file paths and URLs
2. **Limit file sizes**: Prevent memory issues
3. **Use service keys**: Server-side operations only
4. **RLS policies**: Add Row Level Security if needed

## Maintenance

### Updating Documents

```bash
# Delete old version
python document_ingestion.py delete old-doc-id

# Add new version
python document_ingestion.py add-text "updated-doc.md" \
    --title "Updated Document" \
    --id "new-doc-id"
```

### Bulk Import

```python
# Create a script for bulk import
from document_ingestion import DocumentIngestion
import asyncio
from pathlib import Path

async def bulk_import(directory: str):
    ingestion = DocumentIngestion()

    for file_path in Path(directory).glob('**/*.md'):
        title = file_path.stem
        doc_id = await ingestion.add_text_document(
            str(file_path),
            title=title
        )
        print(f"Added: {title}")

asyncio.run(bulk_import('docs/'))
```

### Cleanup

```sql
-- Remove all documents (use with caution!)
TRUNCATE document_metadata CASCADE;
TRUNCATE documents CASCADE;
TRUNCATE document_rows CASCADE;
```

## Troubleshooting

### Common Issues

1. **"relation 'documents' does not exist"**
   - Solution: Run `5-rag_documents.sql` in Supabase SQL editor

2. **"dimension mismatch" error**
   - Solution: Ensure vector dimensions match your embedding model
   - Check: `EMBEDDING_MODEL_CHOICE` in `.env`

3. **"No relevant documents found"**
   - Check: Documents exist (`python document_ingestion.py list`)
   - Check: Embeddings were generated properly
   - Try: Different search queries

4. **Slow vector search**
   - Solution: Ensure indexes are created (`idx_documents_embedding`)
   - Check: Vector index statistics in Supabase

5. **"Module not found: pandas"**
   - Solution: `pip install pandas` or `uv add pandas`

### Debug Tips

```python
# Test embedding generation
from document_ingestion import DocumentIngestion
import asyncio

async def test():
    ing = DocumentIngestion()
    embedding = await ing.get_embedding("test query")
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

asyncio.run(test())
```

## Example: Adding Your AI Documentation

```bash
cd app/server

# Add all AI documentation files
python document_ingestion.py add-text "../../ai_docs/anthropic_quick_start.md" \
    --title "Anthropic Quick Start"

python document_ingestion.py add-text "../../ai_docs/openai_quick_start.md" \
    --title "OpenAI Quick Start"

python document_ingestion.py add-text "../../ai_docs/ag-ui-protocol.md" \
    --title "AG-UI Protocol Documentation"

python document_ingestion.py add-text "../../ai_docs/pydantic-ai-ag-ui.md" \
    --title "Pydantic AI AG-UI Integration"

# Verify
python document_ingestion.py list
```

Now your agent can answer questions about these topics using RAG!

## Next Steps

1. **Run the SQL script**: Create the database schema
2. **Test ingestion**: Add a sample document
3. **Query the agent**: Ask questions about your documents
4. **Monitor usage**: Check embedding API costs
5. **Optimize**: Adjust chunk sizes and match counts based on results

## Summary

Your RAG system is now ready to use! You can:
- ✅ Add text documents, images, and CSV files
- ✅ Search semantically across all documents
- ✅ Query structured data with SQL
- ✅ Track document metadata and versions
- ✅ Maintain and update your knowledge base

The agent will automatically use this information to provide accurate, context-aware responses! 🎯
