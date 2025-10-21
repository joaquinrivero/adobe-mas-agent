"""
Adobe Commerce Fragment API Client

Fetches product data from Adobe's Commerce Fragment API
with caching for performance optimization.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from httpx import AsyncClient, HTTPError
import json

logger = logging.getLogger(__name__)


class AdobeCommerceClient:
    """Client for interacting with Adobe Commerce Fragment API."""

    def __init__(self):
        """Initialize the Adobe Commerce client with configuration from environment."""
        self.fragment_id = os.getenv(
            "ADOBE_COMMERCE_FRAGMENT_ID",
            "0d0af87d-f183-4cde-b88c-bb4729a5c3e5"
        )
        self.api_key = os.getenv(
            "ADOBE_COMMERCE_API_KEY",
            "wcms-commerce-ims-ro-user-milo"
        )
        self.locale = os.getenv("ADOBE_COMMERCE_LOCALE", "en_US")
        self.base_url = "https://www.adobe.com/mas/io/fragment"

        # Simple in-memory cache with 1-hour TTL
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(hours=1)

    async def fetch_products(self) -> List[Dict[str, Any]]:
        """
        Fetch all products from the Commerce Fragment API.

        Uses caching to reduce API calls.

        Returns:
            List of product dictionaries from the API

        Raises:
            HTTPError: If the API request fails
        """
        # Check cache first
        if self._is_cache_valid():
            logger.info("Returning cached Adobe Commerce products")
            return self._cache

        # Fetch from API
        url = f"{self.base_url}/{self.fragment_id}"
        params = {
            "locale": self.locale,
            "api_key": self.api_key
        }

        try:
            async with AsyncClient(timeout=10.0) as client:
                logger.info(f"Fetching Adobe Commerce products from {url}")
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                # Extract products array from response
                # The structure may vary, so we handle different formats
                if isinstance(data, list):
                    products = data
                elif isinstance(data, dict) and "products" in data:
                    products = data["products"]
                elif isinstance(data, dict) and "data" in data:
                    products = data["data"]
                else:
                    products = [data] if data else []

                # Update cache
                self._cache = products
                self._cache_timestamp = datetime.now()

                logger.info(f"Successfully fetched {len(products)} products")
                return products

        except HTTPError as e:
            logger.error(f"Failed to fetch Adobe Commerce products: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching products: {e}")
            raise

    async def get_products_by_query(
        self,
        query: str,
        max_results: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Filter products based on a user query.

        Args:
            query: Search query string (e.g., "creative cloud", "photoshop")
            max_results: Maximum number of products to return

        Returns:
            Filtered list of products matching the query
        """
        products = await self.fetch_products()

        if not query:
            # No query, return first max_results
            return products[:max_results]

        # Simple text-based filtering
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()

        filtered = []
        for product in products:
            # Check various product fields for matches
            searchable_text = " ".join([
                str(product.get("name", "")),
                str(product.get("description", "")),
                str(product.get("productLine", "")),
                str(product.get("audience", "")),
                str(product.get("badge", "")),
            ]).lower()

            if query_lower in searchable_text:
                filtered.append(product)

            if len(filtered) >= max_results:
                break

        logger.info(f"Filtered {len(filtered)} products for query: {query}")
        return filtered

    def _is_cache_valid(self) -> bool:
        """Check if the cache is still valid."""
        if self._cache is None or self._cache_timestamp is None:
            return False

        age = datetime.now() - self._cache_timestamp
        return age < self._cache_ttl

    def clear_cache(self):
        """Clear the product cache."""
        self._cache = None
        self._cache_timestamp = None
        logger.info("Adobe Commerce cache cleared")


# Singleton instance
_client: Optional[AdobeCommerceClient] = None


def get_adobe_commerce_client() -> AdobeCommerceClient:
    """Get or create the singleton Adobe Commerce client instance."""
    global _client
    if _client is None:
        _client = AdobeCommerceClient()
    return _client
