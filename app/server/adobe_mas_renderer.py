"""Adobe MAS HTML Renderer

This module provides functions to render Adobe MAS (Merch At Scale) web component
cards as HTML from Adobe Commerce API data.
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


def filter_products(
    references: Dict[str, Any],
    product_line: Optional[str] = None,
    audience_type: Optional[str] = None
) -> List[Dict]:
    """Filter products by tags from Adobe Commerce API.

    Product lines (mas:cloud/{product}):
    - firefly: Adobe Firefly products
    - creative: Creative Cloud products
    - document-cloud: Document Cloud products

    Audience types (mas:customer_segment/{audience}):
    - individual: Individual consumers
    - students: Student/teacher pricing
    - business: Business/enterprise plans

    Args:
        references: References map from Commerce API
        product_line: Filter by product (e.g., "firefly", "creative")
        audience_type: Filter by audience (e.g., "students", "business")

    Returns:
        List of filtered card data objects

    Example:
        # Get Firefly products for students
        cards = filter_products(references, "firefly", "students")
    """
    cards = []

    for ref_id, ref_data in references.items():
        # Only process content-fragment types
        if ref_data.get('type') != 'content-fragment':
            continue

        fields = ref_data.get('value', {}).get('fields', {})
        tags = fields.get('tags', [])

        # Filter by product_line if specified
        if product_line:
            tag_filter = f"mas:cloud/{product_line.lower()}"
            if tag_filter not in tags:
                continue

        # Filter by audience_type if specified
        if audience_type and audience_type != "all":
            segment_tag = f"mas:customer_segment/{audience_type.lower()}"
            if segment_tag not in tags:
                continue

        cards.append(ref_data.get('value'))

    logger.info(f"Filtered to {len(cards)} products (line={product_line}, audience={audience_type})")
    return cards


def render_merch_card(card_data: Dict) -> str:
    """Generate HTML for single Adobe MAS merch-card component.

    MAS web components use a slot-based system for content placement:
    - heading-xs: Card title/product name
    - body-xxs: Subtitle text
    - body-xs: Product description
    - footer: Call-to-action buttons

    Args:
        card_data: Card data from Adobe Commerce API with fields:
            - variant: Card style (plans, special-offers, etc.)
            - size: Card size (wide, super-wide)
            - cardTitle: Product name
            - prices: Price HTML with data-wcs-osi attributes
            - shortDescription: Product features
            - ctas: Call-to-action buttons

    Returns:
        HTML string for <merch-card> web component

    Example:
        card_html = render_merch_card({
            "fields": {
                "variant": "plans",
                "cardTitle": "Adobe Firefly Pro"
            }
        })
    """
    fields = card_data.get('fields', {})

    # Extract values with safe defaults
    variant = fields.get('variant', 'plans')
    size = fields.get('size', 'wide')
    title = fields.get('cardTitle', '')
    subtitle = fields.get('subtitle', {}).get('value', '')
    prices = fields.get('prices', {}).get('value', '')
    description = fields.get('shortDescription', {}).get('value', '')
    ctas = fields.get('ctas', {}).get('value', '')

    return f'''
<merch-card variant="{variant}"
            size="{size}"
            badge-background-color="#EDCC2D"
            badge-color="#000000">
  <div slot="heading-xs">{title}</div>
  <div slot="body-xxs">{subtitle}</div>
  {prices}
  {description}
  <div slot="footer">{ctas}</div>
</merch-card>'''


def render_product_comparison(cards: List[Dict], title: Optional[str] = None) -> str:
    """Generate responsive grid of product cards.

    Creates a responsive CSS grid layout that adapts to screen size:
    - Mobile (<768px): Single column
    - Tablet (768-1024px): Two columns
    - Desktop (>1024px): Auto-fit grid

    Args:
        cards: List of card data objects (max 6 displayed)
        title: Optional heading for the product grid

    Returns:
        Complete HTML with grid layout and embedded styles

    Example:
        html = render_product_comparison(
            cards=[card1, card2, card3],
            title="Adobe Firefly Plans"
        )
    """
    # Limit to 6 cards to prevent overwhelming the UI
    cards = cards[:6]
    cards_html = "\n".join([render_merch_card(card) for card in cards])

    title_html = f'<h2 class="mas-title">{title}</h2>' if title else ''

    return f'''
<div class="adobe-products-container" data-tool-rendered="true">
  <style>
    .adobe-products-container {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 24px;
      padding: 20px;
      max-width: 1200px;
      margin: 0 auto;
    }}
    .mas-title {{
      grid-column: 1 / -1;
      font-size: 1.5rem;
      font-weight: 600;
      margin-bottom: 8px;
      color: inherit;
    }}
    /* Ensure MAS cards inherit theme colors */
    merch-card {{
      --merch-card-border: 1px solid var(--border);
      --merch-card-bg: var(--card);
    }}
    @media (max-width: 768px) {{
      .adobe-products-container {{
        grid-template-columns: 1fr;
        padding: 16px;
        gap: 16px;
      }}
    }}
    @media (min-width: 769px) and (max-width: 1024px) {{
      .adobe-products-container {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}
  </style>
  {title_html}
  <div class="products-grid">{cards_html}</div>
</div>'''
