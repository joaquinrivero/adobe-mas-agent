#!/usr/bin/env python3
"""
Document Ingestion Utility for RAG Database

This script provides utilities to add documents to the RAG knowledge base.
Supports text documents, markdown files, PDFs, images, and structured data (CSV).

Usage:
    python document_ingestion.py add-text "path/to/file.txt" --title "My Document"
    python document_ingestion.py add-csv "path/to/data.csv" --title "Sales Data"
    python document_ingestion.py add-image "path/to/image.png" --title "Diagram"
    python document_ingestion.py add-url "https://example.com/docs" --title "External Docs"
    python document_ingestion.py list
    python document_ingestion.py delete <document_id>
"""

import asyncio
import base64
import hashlib
import json
import mimetypes
import os
import sys
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

import pandas as pd
from openai import AsyncOpenAI
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DocumentIngestion:
    """Handles document ingestion into the RAG knowledge base"""

    def __init__(self):
        """Initialize clients and configuration"""
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL', ''),
            os.getenv('SUPABASE_SERVICE_KEY', '')
        )

        # Initialize embedding client
        embedding_base_url = os.getenv('EMBEDDING_BASE_URL', 'https://api.openai.com/v1')
        embedding_api_key = os.getenv('EMBEDDING_API_KEY', '')

        self.embedding_client = AsyncOpenAI(
            base_url=embedding_base_url,
            api_key=embedding_api_key
        )

        self.embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE', 'text-embedding-3-small')
        self.chunk_size = 1000  # Characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        try:
            response = await self.embedding_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            # Get chunk
            end = start + self.chunk_size
            chunk = text[start:end]

            # Try to end at a sentence boundary
            if end < text_length:
                # Look for sentence endings
                for separator in ['. ', '.\n', '! ', '?\n', '\n\n']:
                    last_sep = chunk.rfind(separator)
                    if last_sep > self.chunk_size * 0.7:  # At least 70% through
                        chunk = chunk[:last_sep + len(separator)]
                        end = start + len(chunk)
                        break

            chunks.append(chunk.strip())

            # Move start position with overlap
            start = end - self.chunk_overlap

        return [c for c in chunks if c]  # Remove empty chunks

    async def add_text_document(
        self,
        file_path: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        document_id: Optional[str] = None
    ) -> str:
        """
        Add a text document to the RAG database

        Args:
            file_path: Path to the text file
            title: Optional document title (defaults to filename)
            url: Optional source URL
            document_id: Optional custom ID (defaults to UUID)

        Returns:
            document_id of the created document
        """
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Generate document ID if not provided
        if not document_id:
            document_id = str(uuid.uuid4())

        # Use filename as title if not provided
        if not title:
            title = Path(file_path).stem

        # Use file path as URL if not provided
        if not url:
            url = f"file://{os.path.abspath(file_path)}"

        # Create metadata entry
        logger.info(f"Creating metadata for document: {title}")
        self.supabase.table('document_metadata').insert({
            'id': document_id,
            'title': title,
            'url': url,
            'schema': None
        }).execute()

        # Chunk the document
        chunks = self.chunk_text(content)
        logger.info(f"Created {len(chunks)} chunks from document")

        # Process each chunk
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)}")

            # Generate embedding
            embedding = await self.get_embedding(chunk)

            # Insert chunk with embedding
            self.supabase.table('documents').insert({
                'content': chunk,
                'embedding': embedding,
                'metadata': {
                    'file_id': document_id,
                    'file_title': title,
                    'file_url': url,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
            }).execute()

        logger.info(f"✓ Successfully added document: {title} ({document_id})")
        return document_id

    async def add_image_document(
        self,
        file_path: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        document_id: Optional[str] = None
    ) -> str:
        """
        Add an image to the RAG database

        Args:
            file_path: Path to the image file
            title: Optional image title
            description: Optional image description
            document_id: Optional custom ID

        Returns:
            document_id of the created document
        """
        # Generate document ID if not provided
        if not document_id:
            document_id = str(uuid.uuid4())

        if not title:
            title = Path(file_path).stem

        # Read and encode image
        with open(file_path, 'rb') as f:
            image_data = f.read()

        base64_image = base64.b64encode(image_data).decode('utf-8')

        # Detect mime type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'image/png'

        # Use description or title for embedding
        text_for_embedding = description or title

        # Create metadata
        self.supabase.table('document_metadata').insert({
            'id': document_id,
            'title': title,
            'url': f"file://{os.path.abspath(file_path)}",
            'schema': None
        }).execute()

        # Generate embedding for searchability
        embedding = await self.get_embedding(text_for_embedding)

        # Insert image document
        self.supabase.table('documents').insert({
            'content': description or f"Image: {title}",
            'embedding': embedding,
            'metadata': {
                'file_id': document_id,
                'file_title': title,
                'file_url': f"file://{os.path.abspath(file_path)}",
                'mime_type': mime_type,
                'file_contents': base64_image
            }
        }).execute()

        logger.info(f"✓ Successfully added image: {title} ({document_id})")
        return document_id

    async def add_csv_document(
        self,
        file_path: str,
        title: Optional[str] = None,
        document_id: Optional[str] = None
    ) -> str:
        """
        Add a CSV file to the RAG database as structured data

        Args:
            file_path: Path to the CSV file
            title: Optional dataset title
            document_id: Optional custom ID

        Returns:
            document_id of the created dataset
        """
        if not document_id:
            document_id = str(uuid.uuid4())

        if not title:
            title = Path(file_path).stem

        # Read CSV
        df = pd.read_csv(file_path)

        # Get schema
        schema = {
            col: str(dtype) for col, dtype in df.dtypes.items()
        }

        # Create metadata
        self.supabase.table('document_metadata').insert({
            'id': document_id,
            'title': title,
            'url': f"file://{os.path.abspath(file_path)}",
            'schema': schema
        }).execute()

        # Create a searchable description
        description = f"Dataset: {title}\nColumns: {', '.join(df.columns)}\nRows: {len(df)}"
        embedding = await self.get_embedding(description)

        # Add searchable document entry
        self.supabase.table('documents').insert({
            'content': description,
            'embedding': embedding,
            'metadata': {
                'file_id': document_id,
                'file_title': title,
                'file_url': f"file://{os.path.abspath(file_path)}",
                'schema': schema
            }
        }).execute()

        # Insert rows into document_rows
        logger.info(f"Inserting {len(df)} rows into document_rows")
        rows_data = []
        for _, row in df.iterrows():
            rows_data.append({
                'dataset_id': document_id,
                'row_data': row.to_dict()
            })

        # Batch insert (Supabase supports up to 1000 rows per insert)
        batch_size = 1000
        for i in range(0, len(rows_data), batch_size):
            batch = rows_data[i:i + batch_size]
            self.supabase.table('document_rows').insert(batch).execute()
            logger.info(f"Inserted batch {i//batch_size + 1}/{(len(rows_data)-1)//batch_size + 1}")

        logger.info(f"✓ Successfully added CSV dataset: {title} ({document_id})")
        return document_id

    async def add_from_url(
        self,
        url: str,
        title: Optional[str] = None,
        document_id: Optional[str] = None
    ) -> str:
        """
        Fetch content from URL and add to RAG database

        Args:
            url: URL to fetch content from
            title: Optional document title
            document_id: Optional custom ID

        Returns:
            document_id of the created document
        """
        import httpx

        if not document_id:
            document_id = str(uuid.uuid4())

        # Fetch content
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.text

        # Use URL as title if not provided
        if not title:
            title = url.split('/')[-1] or url

        # Create metadata
        self.supabase.table('document_metadata').insert({
            'id': document_id,
            'title': title,
            'url': url,
            'schema': None
        }).execute()

        # Chunk and process
        chunks = self.chunk_text(content)
        logger.info(f"Created {len(chunks)} chunks from URL content")

        for i, chunk in enumerate(chunks):
            embedding = await self.get_embedding(chunk)

            self.supabase.table('documents').insert({
                'content': chunk,
                'embedding': embedding,
                'metadata': {
                    'file_id': document_id,
                    'file_title': title,
                    'file_url': url,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
            }).execute()

        logger.info(f"✓ Successfully added content from URL: {title} ({document_id})")
        return document_id

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the knowledge base"""
        result = self.supabase.table('document_metadata') \
            .select('id, title, url, created_at') \
            .order('created_at', desc=True) \
            .execute()

        return result.data

    def delete_document(self, document_id: str) -> None:
        """Delete a document from the knowledge base"""
        self.supabase.rpc('delete_document', {'doc_id': document_id}).execute()
        logger.info(f"✓ Deleted document: {document_id}")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection"""
        result = self.supabase.rpc('get_document_stats').execute()
        return result.data[0] if result.data else {}


# CLI Interface
async def main():
    """Command-line interface for document ingestion"""
    import argparse

    parser = argparse.ArgumentParser(description='RAG Document Ingestion Utility')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Add text document
    add_text = subparsers.add_parser('add-text', help='Add a text document')
    add_text.add_argument('file_path', help='Path to text file')
    add_text.add_argument('--title', help='Document title')
    add_text.add_argument('--url', help='Source URL')
    add_text.add_argument('--id', help='Custom document ID')

    # Add image
    add_image = subparsers.add_parser('add-image', help='Add an image')
    add_image.add_argument('file_path', help='Path to image file')
    add_image.add_argument('--title', help='Image title')
    add_image.add_argument('--description', help='Image description')
    add_image.add_argument('--id', help='Custom document ID')

    # Add CSV
    add_csv = subparsers.add_parser('add-csv', help='Add a CSV dataset')
    add_csv.add_argument('file_path', help='Path to CSV file')
    add_csv.add_argument('--title', help='Dataset title')
    add_csv.add_argument('--id', help='Custom document ID')

    # Add from URL
    add_url = subparsers.add_parser('add-url', help='Add content from URL')
    add_url.add_argument('url', help='URL to fetch')
    add_url.add_argument('--title', help='Document title')
    add_url.add_argument('--id', help='Custom document ID')

    # List documents
    subparsers.add_parser('list', help='List all documents')

    # Delete document
    delete = subparsers.add_parser('delete', help='Delete a document')
    delete.add_argument('document_id', help='ID of document to delete')

    # Stats
    subparsers.add_parser('stats', help='Show document collection statistics')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ingestion = DocumentIngestion()

    try:
        if args.command == 'add-text':
            doc_id = await ingestion.add_text_document(
                args.file_path,
                title=args.title,
                url=args.url,
                document_id=args.id
            )
            print(f"Document added with ID: {doc_id}")

        elif args.command == 'add-image':
            doc_id = await ingestion.add_image_document(
                args.file_path,
                title=args.title,
                description=args.description,
                document_id=args.id
            )
            print(f"Image added with ID: {doc_id}")

        elif args.command == 'add-csv':
            doc_id = await ingestion.add_csv_document(
                args.file_path,
                title=args.title,
                document_id=args.id
            )
            print(f"CSV dataset added with ID: {doc_id}")

        elif args.command == 'add-url':
            doc_id = await ingestion.add_from_url(
                args.url,
                title=args.title,
                document_id=args.id
            )
            print(f"URL content added with ID: {doc_id}")

        elif args.command == 'list':
            docs = ingestion.list_documents()
            print(f"\nFound {len(docs)} documents:\n")
            for doc in docs:
                print(f"  ID: {doc['id']}")
                print(f"  Title: {doc['title']}")
                print(f"  URL: {doc.get('url', 'N/A')}")
                print(f"  Created: {doc['created_at']}")
                print()

        elif args.command == 'delete':
            ingestion.delete_document(args.document_id)
            print(f"Document deleted: {args.document_id}")

        elif args.command == 'stats':
            stats = ingestion.get_stats()
            print("\nDocument Collection Statistics:")
            print(f"  Total Documents: {stats.get('total_documents', 0)}")
            print(f"  Total Chunks: {stats.get('total_chunks', 0)}")
            print(f"  Total Rows (structured data): {stats.get('total_rows', 0)}")
            print(f"  Avg Chunk Length: {stats.get('avg_chunk_length', 0):.0f} chars")
            print()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
