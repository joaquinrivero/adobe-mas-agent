"""
Adobe MAS (Merch At Scale) Web Component Renderer

This module generates HTML for Adobe MAS web components (merch-card, merch-price, checkout-link)
to display Adobe product information in rich, interactive cards.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


def render_merch_card(product: Dict[str, Any]) -> str:
    """
    Generate HTML for a single Adobe MAS merch-card component.

    Args:
        product: Product dictionary with fields like productName, price, features, etc.

    Returns:
        HTML string containing a complete merch-card with all attributes and content
    """
    try:
        # Extract product data with defaults
        product_name = product.get('productName', 'Adobe Product')
        tier = product.get('tier', '').capitalize()
        price = product.get('price', '')
        price_monthly = product.get('priceMonthly', 0)
        description = product.get('description', '')
        credits = product.get('credits', '')
        features = product.get('features', [])
        cta_text = product.get('ctaText', 'Learn more')
        cta_link = product.get('ctaLink', 'https://www.adobe.com')
        details_link = product.get('detailsLink', cta_link)
        icon = product.get('icon', '')

        # Build features list HTML
        features_html = ""
        if features:
            features_list = "\n".join([f"      <li>{feature}</li>" for feature in features[:5]])  # Limit to 5 features
            features_html = f"""
    <div slot="body-m">
      <ul class="spectrum-Body spectrum-Body--sizeM">
{features_list}
      </ul>
    </div>"""

        # Build credits/subtitle HTML
        credits_html = ""
        if credits:
            credits_html = f'\n    <div slot="body-xxs">{credits}</div>'

        # Build description HTML
        description_html = ""
        if description:
            description_html = f'\n    <div slot="body-xs">{description}</div>'

        # Build pricing HTML with merch-price component
        price_html = ""
        if price:
            # Determine badge color based on tier
            badge_color = "#EDCC2D" if tier.lower() == "pro" or tier.lower() == "premium" else "#268E6C"

            price_html = f"""
    <div slot="price">
      <merch-price
        template="price"
        data-wcs-osi="firefly-{tier.lower()}"
        data-template="price"
      >{price}</merch-price>
    </div>"""

        # Build CTA with checkout-link component
        cta_html = f"""
    <div slot="footer">
      <checkout-link
        href="{cta_link}"
        target="_blank"
        class="spectrum-Button spectrum-Button--fill spectrum-Button--accent spectrum-Button--sizeM"
      >
        <span class="spectrum-Button-label">{cta_text}</span>
      </checkout-link>
    </div>"""

        # Assemble the complete merch-card
        card_html = f"""
  <merch-card
    variant="plans"
    size="wide"
    badge-background-color="#EDCC2D"
    badge-color="#000000"
    icons="secure"
  >
    <div slot="heading-xs">{product_name}</div>{credits_html}{description_html}{features_html}{price_html}{cta_html}
  </merch-card>"""

        return card_html

    except Exception as e:
        logger.error(f"Error rendering merch card for product {product.get('id', 'unknown')}: {e}")
        # Return a fallback error card
        return f"""
  <merch-card variant="plans" size="wide">
    <div slot="heading-xs">Product Unavailable</div>
    <div slot="body-xs">Unable to display product information at this time.</div>
  </merch-card>"""


def render_product_comparison(products: List[Dict[str, Any]], title: Optional[str] = None) -> str:
    """
    Generate HTML for a grid of Adobe product cards for comparison.

    Args:
        products: List of product dictionaries to render as cards
        title: Optional title to display above the cards

    Returns:
        Complete HTML string with responsive grid layout and all product cards
    """
    try:
        if not products:
            return """
<div class="adobe-products-container">
  <div class="no-products-message">
    <p>No Adobe products found matching your query. Please try a different search.</p>
  </div>
</div>"""

        # Generate title HTML if provided
        title_html = ""
        if title:
            title_html = f"""
  <div class="products-header">
    <h2 class="products-title">{title}</h2>
  </div>"""

        # Render each product as a merch-card
        cards_html = "\n".join([render_merch_card(product) for product in products[:6]])  # Limit to 6 cards

        # Wrap cards in responsive grid container
        comparison_html = f"""
<div class="adobe-products-container" data-tool-rendered="true">
  <style>
    .adobe-products-container {{
      max-width: 1200px;
      margin: 20px auto;
      padding: 20px;
    }}
    .products-header {{
      margin-bottom: 24px;
      text-align: center;
    }}
    .products-title {{
      font-size: 28px;
      font-weight: 700;
      color: #fff;
      margin: 0;
    }}
    .products-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 24px;
      margin: 0 auto;
    }}
    @media (max-width: 768px) {{
      .products-grid {{
        grid-template-columns: 1fr;
      }}
    }}
    .no-products-message {{
      text-align: center;
      padding: 40px;
      color: #999;
    }}
  </style>{title_html}
  <div class="products-grid">
{cards_html}
  </div>
</div>"""

        return comparison_html

    except Exception as e:
        logger.error(f"Error rendering product comparison: {e}")
        return f"""
<div class="adobe-products-container">
  <div class="no-products-message">
    <p>Error displaying products. Please try again.</p>
  </div>
</div>"""


def render_search_results(products: List[Dict[str, Any]], query: str) -> str:
    """
    Render Adobe products as a search result with contextual title.

    Args:
        products: List of products to display
        query: The search query that was used

    Returns:
        HTML with title describing the search and product cards
    """
    count = len(products)
    title = f"Found {count} Adobe product{'' if count == 1 else 's'} for: {query}"
    return render_product_comparison(products, title=title)
