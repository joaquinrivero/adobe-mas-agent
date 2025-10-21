"""Adobe Commerce API Client

This module provides an async HTTP client for fetching Adobe product catalog
data from the official Adobe Commerce API.
"""

from httpx import AsyncClient
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

ADOBE_COMMERCE_API_URL = (
    "https://www.adobe.com/mas/io/fragment"
    "?id=0d0af87d-f183-4cde-b88c-bb4729a5c3e5"
    "&api_key=wcms-commerce-ims-ro-user-milo"
    "&locale=en_US"
)


async def fetch_adobe_commerce_data(http_client: AsyncClient) -> Dict[str, Any]:
    """Fetch Adobe product catalog from official Commerce API.

    The API returns a nested JSON structure with:
    - fields.cards: List of card UUIDs to display
    - references: Map of UUID → card data with all content
      - type: "content-fragment" for product cards
      - value.fields: Card data (variant, osi, prices, tags, etc.)
    - tags: Used for filtering products
      - mas:cloud/{product_line} - Product line filter
      - mas:customer_segment/{audience} - Audience filter

    Args:
        http_client: AsyncClient for making HTTP requests

    Returns:
        Dict containing references, fields, and metadata

    Raises:
        Exception: If API request fails or returns invalid data

    Example response structure:
        {
            "fields": {
                "cards": ["uuid1", "uuid2", ...]
            },
            "references": {
                "uuid1": {
                    "type": "content-fragment",
                    "value": {
                        "fields": {
                            "variant": "plans",
                            "cardTitle": "Adobe Firefly Pro",
                            "prices": {"value": "<merch-price ...>"},
                            "tags": ["mas:cloud/firefly", ...]
                        }
                    }
                }
            }
        }
    """
    try:
        logger.info(f"Fetching Adobe Commerce data from {ADOBE_COMMERCE_API_URL}")
        response = await http_client.get(ADOBE_COMMERCE_API_URL, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        ref_count = len(data.get('references', {}))
        logger.info(f"Fetched Adobe Commerce data: {ref_count} products")

        return data
    except Exception as e:
        logger.error(f"Error fetching Adobe Commerce data: {e}")
        raise
