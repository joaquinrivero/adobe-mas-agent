#!/usr/bin/env python3
"""
Adobe Product Catalog Ingestion Script

Ingests Adobe product catalog data from data/adobe_products.json into the RAG system
with proper chunking and metadata for semantic search.
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path to import from app/server
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'app' / 'server'))

from clients import get_agent_clients
from tools import get_embedding
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest_adobe_products():
    """
    Main ingestion function that reads the Adobe product catalog
    and stores it in Supabase with embeddings for RAG retrieval.
    """
    try:
        # Get clients
        logger.info("Initializing clients...")
        embedding_client, supabase = get_agent_clients()

        # Read the Adobe products JSON file
        catalog_path = Path(__file__).resolve().parent.parent / 'data' / 'adobe_products.json'
        logger.info(f"Reading product catalog from: {catalog_path}")

        with open(catalog_path, 'r') as f:
            catalog_data = json.load(f)

        products = catalog_data.get('products', [])
        logger.info(f"Found {len(products)} products to ingest")

        # First, add file metadata entry
        file_id = "adobe-products-catalog"
        file_metadata = {
            "id": file_id,
            "title": "Adobe Product Catalog",
            "url": "internal://adobe-products",
            "schema": {
                "id": "string",
                "productName": "string",
                "productLine": "string",
                "tier": "string",
                "audience": "array",
                "price": "string",
                "priceMonthly": "number",
                "description": "string",
                "features": "array"
            },
            "file_size": len(json.dumps(catalog_data)),
            "created_at": "2025-01-20T00:00:00Z"
        }

        # Upsert file metadata
        logger.info(f"Upserting file metadata for: {file_id}")
        supabase.table("document_metadata").upsert(file_metadata).execute()

        # Process each product as a separate document chunk
        for idx, product in enumerate(products, start=1):
            try:
                product_id = product.get('id', f'product-{idx}')
                logger.info(f"Processing product {idx}/{len(products)}: {product_id}")

                # Create comprehensive text content for embedding
                content_parts = [
                    f"Product: {product.get('productName', 'Unknown')}",
                    f"Product Line: {product.get('productLine', 'Unknown')}",
                    f"Tier: {product.get('tier', 'standard')}",
                    f"Price: {product.get('price', 'Contact sales')}",
                    f"Description: {product.get('description', '')}",
                ]

                # Add features
                features = product.get('features', [])
                if features:
                    content_parts.append("Features:")
                    content_parts.extend([f"- {feature}" for feature in features])

                # Add credits info
                if product.get('credits'):
                    content_parts.append(f"Credits: {product['credits']}")

                # Add audience
                if product.get('audience'):
                    audiences = ', '.join(product['audience'])
                    content_parts.append(f"Target Audience: {audiences}")

                # Combine all parts
                content = "\n".join(content_parts)

                # Generate embedding
                logger.info(f"  Generating embedding for {product_id}...")
                embedding = await get_embedding(content, embedding_client)

                # Create metadata for this product chunk
                chunk_metadata = {
                    "file_id": file_id,
                    "file_title": f"Adobe Product: {product.get('productName')}",
                    "file_url": product.get('detailsLink', 'https://www.adobe.com'),
                    "product_line": product.get('productLine'),
                    "tier": product.get('tier'),
                    "audience": product.get('audience', []),
                    "category": product.get('metadata', {}).get('category'),
                    "product_id": product_id,
                    "price_monthly": product.get('priceMonthly', 0)
                }

                # Store in documents table with embedding
                document_entry = {
                    "content": content,
                    "metadata": chunk_metadata,
                    "embedding": embedding
                }

                logger.info(f"  Storing in database...")
                supabase.table("documents").insert(document_entry).execute()
                logger.info(f"  ✓ Successfully ingested {product_id}")

            except Exception as e:
                logger.error(f"  ✗ Error processing product {product.get('id', idx)}: {e}")
                continue

        logger.info(f"\n✓ Successfully ingested {len(products)} Adobe products into RAG system")
        logger.info(f"File ID for queries: {file_id}")

    except Exception as e:
        logger.error(f"Fatal error during ingestion: {e}")
        raise


if __name__ == "__main__":
    logger.info("Starting Adobe product catalog ingestion...")
    asyncio.run(ingest_adobe_products())
    logger.info("Ingestion complete!")
