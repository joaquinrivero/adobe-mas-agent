# Feature: Adobe MAS Backend Tool Rendering

## Feature Description
This feature implements backend-rendered Adobe MAS (Merch At Scale) web component cards to display Adobe product pricing information directly in the chat interface. The implementation uses AG-UI's backend tool rendering capability to return HTML content from a Pydantic AI agent tool, which is then sanitized and rendered in the React frontend. The tool fetches live product data from Adobe's official Commerce API and renders it as interactive MAS component cards that match Adobe's production design system.

This feature enables users to query Adobe products (Firefly, Creative Cloud, etc.) and receive rich, interactive product cards with pricing, features, and purchase links - all rendered server-side and streamed to the client in real-time.

## User Story
As a user interacting with the AI agent
I want to ask about Adobe products and see interactive pricing cards
So that I can compare Adobe offerings, view pricing details, and access purchase links without leaving the chat interface

## Problem Statement
Currently, the AI agent can only respond to Adobe product queries with plain text. This creates several limitations:

1. **Poor Visual Experience**: Text-only responses lack the rich visual presentation needed for product information
2. **Limited Interactivity**: Users cannot directly interact with pricing information or CTAs within the chat
3. **Outdated Information**: Without API integration, product/pricing data may become stale
4. **Manual Maintenance**: Storing product data in RAG requires manual updates when Adobe changes pricing
5. **Inconsistent Branding**: Text responses don't match Adobe's visual design language
6. **CORS Limitations**: Loading MAS library from Adobe's CDN fails on localhost with CORS errors

The existing AG-UI protocol support provides the foundation for backend tool rendering, but no tools currently return rich HTML content. The MAS library already exists in `app/server/mas/dist/` but is not integrated into the application.

## Solution Statement
Implement a new `get_adobe_products` tool for the Pydantic AI agent that fetches product data from Adobe's Commerce API and renders interactive MAS component cards. The solution includes:

1. **Self-Host MAS Library**: Serve the MAS library from `http://localhost:8001/mas/mas.js` using FastAPI's StaticFiles to avoid CORS issues
2. **Adobe Commerce API Client**: Create async client to fetch live product data from Adobe's official API endpoint
3. **HTML Renderer**: Generate MAS component HTML with proper attributes, slots, and styling for responsive display
4. **Tool Implementation**: Register `get_adobe_products` tool for both standard and AG-UI agents with filtering capabilities
5. **Frontend Integration**: Update React components to detect and render tool-generated HTML with proper sanitization
6. **Security**: Whitelist MAS custom elements and attributes in DOMPurify configuration

This approach leverages the existing AG-UI infrastructure while adding Adobe-specific rendering capabilities that work seamlessly with the streaming response system.

## Relevant Files
Use these files to implement the feature:

### Backend Core Files
- **`app/server/agent_api.py`** (lines 1-489) - Main FastAPI application. Will mount StaticFiles for `/mas` directory to serve MAS library locally at `http://localhost:8001/mas/mas.js`, avoiding CORS issues with Adobe's CDN.

- **`app/server/agent.py`** (lines 1-366) - Pydantic AI agent definition. Will register `get_adobe_products` tool for both `agent` (lines 81-87) and `agui_agent` (lines 90-96) with `AgentDeps` and `AgentStateDeps` context respectively.

- **`app/server/tools.py`** (lines 1-425) - Agent tool implementations. Contains existing tools like `web_search_tool` (lines 85-107) and `retrieve_relevant_documents_tool` (lines 122-163) which serve as patterns for the new Adobe products tool.

- **`app/server/clients.py`** - HTTP client setup. The existing `http_client: AsyncClient` will be used for Adobe Commerce API requests.

### Frontend Core Files
- **`app/client/index.html`** (lines 1-27) - HTML entry point. Will add `<script>` tag to load MAS library from `http://localhost:8001/mas/mas.js` instead of Adobe's CDN.

- **`app/client/src/components/chat/MessageItem.tsx`** (lines 1-200) - Message rendering component. Currently renders markdown using ReactMarkdown (lines 75-111). Will add logic to detect `data-tool-rendered="true"` attribute and render HTML with `dangerouslySetInnerHTML` after sanitization.

- **`app/client/src/lib/utils.ts`** (lines 1-7) - Utility functions. Currently has `cn()` for className merging. Will add `sanitizeToolHTML()` function using DOMPurify to whitelist MAS custom elements.

### Data Source
- **`app/server/mas/dist/mas.js`** (429KB) - Adobe MAS web component library. Already downloaded and ready to serve. Contains custom elements: `<merch-card>`, `<merch-price>`, `<checkout-link>`.

### Configuration Files
- **`app/server/.env.sample`** - Environment template. No changes needed - uses existing `LLM_*` configuration for the agent.

- **`app/client/package.json`** - Frontend dependencies. Will add `dompurify` and `@types/dompurify` for HTML sanitization.

### New Files

#### Backend Implementation
- **`app/server/adobe_commerce_client.py`** - New file for Adobe Commerce API client with async functions to fetch product catalog from `https://www.adobe.com/mas/io/fragment?id=0d0af87d-f183-4cde-b88c-bb4729a5c3e5&api_key=wcms-commerce-ims-ro-user-milo&locale=en_US`

- **`app/server/adobe_mas_renderer.py`** - New file for MAS HTML rendering functions:
  - `render_merch_card(card_data: Dict) -> str` - Generate single card HTML
  - `render_product_comparison(cards: List[Dict], title: str) -> str` - Generate responsive grid

#### Frontend Implementation
- **`app/client/src/lib/html-sanitizer.ts`** - New file for DOMPurify configuration to whitelist MAS custom elements (`merch-card`, `merch-price`, etc.) and required attributes (`slot`, `variant`, `data-wcs-osi`, etc.)

#### Testing
- **`app/server/tests/test_adobe_commerce_client.py`** - Tests for API client (mocked responses)
- **`app/server/tests/test_adobe_mas_renderer.py`** - Tests for HTML rendering functions
- **`app/server/tests/test_get_adobe_products_tool.py`** - Integration tests for the complete tool

#### Documentation
- **`ai_docs/adobe-mas-integration.md`** - Comprehensive guide for Adobe MAS tool usage, API details, and troubleshooting

## Implementation Plan

### Phase 1: Foundation
Set up the infrastructure for serving MAS library and fetching Adobe data:
- Install frontend dependencies (DOMPurify) for HTML sanitization
- Mount StaticFiles in FastAPI to serve MAS library from `/mas` endpoint
- Create Adobe Commerce API client with async HTTP requests
- Add HTML sanitizer configuration for MAS custom elements
- Set up logging for Adobe API requests and rendering

### Phase 2: Core Implementation
Implement the Adobe product tool and HTML rendering:
- Create MAS HTML renderer with `render_merch_card()` and `render_product_comparison()`
- Implement product filtering logic (by product line, audience type)
- Register `get_adobe_products` tool for both standard and AG-UI agents
- Parse Adobe Commerce API JSON structure (references, fields, tags)
- Generate responsive CSS grid layout for product cards
- Add error handling for API failures and missing data

### Phase 3: Integration
Integrate with frontend and existing infrastructure:
- Update `index.html` to load MAS library from local endpoint
- Modify `MessageItem.tsx` to detect and render tool HTML
- Apply sanitization with whitelisted MAS elements and attributes
- Test streaming of HTML responses through AG-UI protocol
- Validate dark theme compatibility and responsive design
- Create comprehensive tests and documentation

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Install Frontend Dependencies
- Navigate to `app/client/` directory
- Add DOMPurify for HTML sanitization:
  ```bash
  cd app/client
  npm install dompurify
  npm install --save-dev @types/dompurify
  ```
- Verify installation: `npm list dompurify`
- Update `package.json` with new dependencies

### 2. Mount MAS Static Files in FastAPI
- Open `app/server/agent_api.py`
- Add import at top (after line 18):
  ```python
  from fastapi.staticfiles import StaticFiles
  ```
- After CORS middleware setup (after line 109), add:
  ```python
  # Serve Adobe MAS library locally to avoid CORS issues
  mas_path = Path(__file__).resolve().parent / "mas" / "dist"
  app.mount("/mas", StaticFiles(directory=str(mas_path)), name="mas")
  logger.info(f"Mounted MAS library at /mas from {mas_path}")
  ```
- This serves `mas.js` at `http://localhost:8001/mas/mas.js`

### 3. Create Adobe Commerce API Client
- Create new file `app/server/adobe_commerce_client.py`
- Implement async function to fetch product catalog:
  ```python
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

      Returns nested structure with:
      - fields.cards: List of card UUIDs
      - references: Map of UUID -> card data with variant, osi, prices, etc.
      """
      try:
          response = await http_client.get(ADOBE_COMMERCE_API_URL)
          response.raise_for_status()
          data = response.json()
          logger.info(f"Fetched Adobe Commerce data: {len(data.get('references', {}))} products")
          return data
      except Exception as e:
          logger.error(f"Error fetching Adobe Commerce data: {e}")
          raise
  ```
- Add docstring explaining JSON structure (fields, references, tags)
- Handle network errors and API failures gracefully

### 4. Create MAS HTML Renderer Module
- Create new file `app/server/adobe_mas_renderer.py`
- Implement `render_merch_card()` function:
  ```python
  from typing import Dict, List, Optional
  import logging

  logger = logging.getLogger(__name__)

  def render_merch_card(card_data: Dict) -> str:
      """Generate HTML for single Adobe MAS merch-card component.

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
  ```
- Implement `render_product_comparison()` function:
  ```python
  def render_product_comparison(cards: List[Dict], title: Optional[str] = None) -> str:
      """Generate responsive grid of product cards.

      Args:
          cards: List of card data objects (max 6 displayed)
          title: Optional heading for the product grid

      Returns:
          Complete HTML with grid layout and embedded styles
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
      @media (max-width: 768px) {{
        .adobe-products-container {{
          grid-template-columns: 1fr;
          padding: 16px;
        }}
      }}
    </style>
    {title_html}
    <div class="products-grid">{cards_html}</div>
  </div>'''
  ```
- Add helper function to extract cards from API response with filtering

### 5. Implement Product Filtering Logic
- In `app/server/adobe_mas_renderer.py`, add:
  ```python
  def filter_products(
      references: Dict[str, Any],
      product_line: Optional[str] = None,
      audience_type: Optional[str] = None
  ) -> List[Dict]:
      """Filter products by tags from Adobe Commerce API.

      Args:
          references: References map from Commerce API
          product_line: Filter by product (e.g., "firefly", "creative")
          audience_type: Filter by audience (e.g., "students", "business")

      Returns:
          List of filtered card data objects
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
  ```
- Document available product lines (firefly, creative, document-cloud)
- Document available audience types (individual, students, business)

### 6. Create get_adobe_products Tool Implementation
- Open `app/server/tools.py`
- Add imports at top:
  ```python
  from adobe_commerce_client import fetch_adobe_commerce_data
  from adobe_mas_renderer import filter_products, render_product_comparison
  ```
- Add new tool function after existing tools (around line 318):
  ```python
  async def get_adobe_products_tool(
      http_client: AsyncClient,
      query: str,
      product_line: Optional[str] = None,
      audience_type: Optional[str] = None,
      comparison_count: int = 3
  ) -> str:
      """Get Adobe product information and render as interactive MAS cards.

      Args:
          http_client: AsyncClient for API requests
          query: User's question about Adobe products
          product_line: Optional filter - "Firefly", "Creative Cloud", etc.
          audience_type: Optional filter - "students", "business", "all"
          comparison_count: Number of products to show (default 3, max 6)

      Returns:
          HTML with interactive Adobe product cards
      """
      try:
          # Fetch from Adobe Commerce API
          commerce_data = await fetch_adobe_commerce_data(http_client)

          # Extract and filter cards
          references = commerce_data.get('references', {})
          cards = filter_products(references, product_line, audience_type)

          # Limit to requested count
          cards = cards[:comparison_count]

          if not cards:
              return '<div>No Adobe products found matching your criteria. Try: "Firefly", "Creative Cloud"</div>'

          # Render as MAS components
          return render_product_comparison(cards, query)

      except Exception as e:
          logger.error(f"Error in get_adobe_products_tool: {e}")
          return f'<div>Error retrieving Adobe products: {str(e)}</div>'
  ```
- Add comprehensive logging for debugging

### 7. Register Tool for Standard Agent
- Open `app/server/agent.py`
- After existing tools (after line 235), add:
  ```python
  @agent.tool
  async def get_adobe_products(
      ctx: RunContext[AgentDeps],
      query: str,
      product_line: Optional[str] = None,
      audience_type: Optional[str] = None,
      comparison_count: int = 3
  ) -> str:
      """
      Get Adobe product information and display as interactive product cards.

      Use this tool when the user asks about Adobe products, pricing, plans,
      subscriptions, or wants to compare Adobe offerings. Returns rich HTML
      cards that display in the chat interface with pricing and purchase links.

      Args:
          query: User's question (e.g., "Show me Firefly pricing")
          product_line: Optional filter - "Firefly", "Creative", "Document"
          audience_type: Optional filter - "students", "business", "all"
          comparison_count: Number of products to show (default 3, max 6)

      Returns:
          HTML with interactive Adobe product cards
      """
      logger.info(f"Calling get_adobe_products tool: {query}")
      return await get_adobe_products_tool(
          ctx.deps.http_client,
          query,
          product_line,
          audience_type,
          comparison_count
      )
  ```
- Import `get_adobe_products_tool` from tools module

### 8. Register Tool for AG-UI Agent
- In `app/server/agent.py`, after AG-UI tools (after line 366), add:
  ```python
  @agui_agent.tool
  async def get_adobe_products_agui(
      ctx: RunContext[AgentStateDeps],
      query: str,
      product_line: Optional[str] = None,
      audience_type: Optional[str] = None,
      comparison_count: int = 3
  ) -> str:
      """
      Get Adobe product information and display as interactive product cards.

      Use this tool when the user asks about Adobe products, pricing, plans,
      subscriptions, or wants to compare Adobe offerings. Returns rich HTML
      cards that display in the chat interface with pricing and purchase links.

      Args:
          query: User's question (e.g., "Show me Firefly pricing")
          product_line: Optional filter - "Firefly", "Creative", "Document"
          audience_type: Optional filter - "students", "business", "all"
          comparison_count: Number of products to show (default 3, max 6)

      Returns:
          HTML with interactive Adobe product cards
      """
      logger.info(f"Calling get_adobe_products_agui tool: {query}")
      return await get_adobe_products_tool(
          ctx.deps.http_client,
          query,
          product_line,
          audience_type,
          comparison_count
      )
  ```
- Ensure both agents can use the same underlying tool implementation

### 9. Create HTML Sanitizer for Frontend
- Create new file `app/client/src/lib/html-sanitizer.ts`
- Implement DOMPurify configuration:
  ```typescript
  import DOMPurify from 'dompurify';

  /**
   * Sanitize HTML from backend tools while allowing Adobe MAS components.
   *
   * Whitelist custom elements (merch-card, merch-price) and required
   * attributes for WCS (Web Commerce System) integration.
   */
  export function sanitizeToolHTML(html: string): string {
    return DOMPurify.sanitize(html, {
      // Allow MAS web components
      ADD_TAGS: ['merch-card', 'merch-price', 'checkout-link'],

      // Allow MAS and WCS attributes
      ADD_ATTR: [
        'slot',                    // MAS slot system
        'variant',                 // Card variant (plans, special-offers)
        'size',                    // Card size (wide, super-wide)
        'badge-background-color',  // Badge styling
        'badge-color',             // Badge text color
        'data-wcs-osi',           // WCS offer selector ID
        'data-template',          // WCS template
        'data-analytics-id',      // Analytics tracking
        'is',                     // Custom element definition
        'data-tool-rendered'      // Marker for tool-rendered content
      ],

      // Allow inline styles for layout
      ALLOW_UNKNOWN_PROTOCOLS: false,

      // Keep relative URLs for local resources
      ALLOW_DATA_ATTR: false,
    });
  }
  ```
- Add JSDoc comments explaining each whitelisted element/attribute

### 10. Update index.html with MAS Script
- Open `app/client/index.html`
- After the `<div id="root"></div>` (line 21), add:
  ```html
  <!-- Adobe MAS Library (served locally to avoid CORS) -->
  <script src="http://localhost:8001/mas/mas.js" type="module" async></script>
  ```
- This loads MAS web components from local endpoint
- Add comment explaining why we self-host instead of using CDN

### 11. Update MessageItem Component for HTML Rendering
- Open `app/client/src/components/chat/MessageItem.tsx`
- Add import at top:
  ```typescript
  import { sanitizeToolHTML } from '@/lib/html-sanitizer';
  ```
- After `memoizedMarkdown` definition (around line 111), add detection logic:
  ```typescript
  // Check if message contains tool-rendered HTML
  const isToolRendered = useMemo(() => {
    return message.message.content?.includes('data-tool-rendered="true"');
  }, [message.message.content]);

  // Sanitize and prepare HTML if tool-rendered
  const sanitizedHTML = useMemo(() => {
    if (!isToolRendered) return null;
    return sanitizeToolHTML(message.message.content);
  }, [isToolRendered, message.message.content]);
  ```
- Update the content rendering section (around line 161):
  ```typescript
  <div className="prose prose-sm dark:prose-invert max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0 [&>p]:mb-4">
    {isToolRendered ? (
      <div
        className="tool-rendered-content"
        dangerouslySetInnerHTML={{ __html: sanitizedHTML || '' }}
      />
    ) : (
      memoizedMarkdown
    )}
  </div>
  ```
- This detects tool HTML and renders it with sanitization

### 12. Add Responsive Styles for MAS Cards
- In `app/server/adobe_mas_renderer.py`, enhance CSS in `render_product_comparison()`:
  ```css
  .adobe-products-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 24px;
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }
  .mas-title {
    grid-column: 1 / -1;
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 8px;
    color: inherit;
  }
  /* Ensure MAS cards inherit theme colors */
  merch-card {
    --merch-card-border: 1px solid var(--border);
    --merch-card-bg: var(--card);
  }
  @media (max-width: 768px) {
    .adobe-products-container {
      grid-template-columns: 1fr;
      padding: 16px;
      gap: 16px;
    }
  }
  @media (min-width: 769px) and (max-width: 1024px) {
    .adobe-products-container {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  ```
- Ensure dark theme compatibility with CSS variables

### 13. Write Backend Tests for Commerce Client
- Create `app/server/tests/test_adobe_commerce_client.py`
- Test cases:
  ```python
  import pytest
  from httpx import AsyncClient, Response
  from adobe_commerce_client import fetch_adobe_commerce_data

  @pytest.mark.asyncio
  async def test_fetch_adobe_commerce_data_success(httpx_mock):
      """Test successful API fetch."""
      # Mock response with sample data
      httpx_mock.add_response(
          url="https://www.adobe.com/mas/io/fragment*",
          json={
              "references": {
                  "uuid1": {
                      "type": "content-fragment",
                      "value": {
                          "fields": {
                              "cardTitle": "Adobe Firefly Pro"
                          }
                      }
                  }
              }
          }
      )

      async with AsyncClient() as client:
          result = await fetch_adobe_commerce_data(client)
          assert "references" in result
          assert len(result["references"]) == 1

  @pytest.mark.asyncio
  async def test_fetch_adobe_commerce_data_api_error(httpx_mock):
      """Test handling of API errors."""
      httpx_mock.add_response(
          url="https://www.adobe.com/mas/io/fragment*",
          status_code=500
      )

      async with AsyncClient() as client:
          with pytest.raises(Exception):
              await fetch_adobe_commerce_data(client)
  ```

### 14. Write Backend Tests for MAS Renderer
- Create `app/server/tests/test_adobe_mas_renderer.py`
- Test rendering functions:
  ```python
  from adobe_mas_renderer import (
      render_merch_card,
      render_product_comparison,
      filter_products
  )

  def test_render_merch_card():
      """Test single card rendering."""
      card_data = {
          "fields": {
              "variant": "plans",
              "cardTitle": "Test Product",
              "prices": {"value": "$19.99/mo"}
          }
      }
      html = render_merch_card(card_data)
      assert "<merch-card" in html
      assert 'variant="plans"' in html
      assert "Test Product" in html

  def test_render_product_comparison():
      """Test grid rendering with multiple cards."""
      cards = [{"fields": {"cardTitle": f"Product {i}"}} for i in range(3)]
      html = render_product_comparison(cards, "Test Products")
      assert 'data-tool-rendered="true"' in html
      assert "Test Products" in html
      assert html.count("<merch-card") == 3

  def test_filter_products_by_product_line():
      """Test filtering by product line."""
      references = {
          "uuid1": {
              "type": "content-fragment",
              "value": {
                  "fields": {
                      "tags": ["mas:cloud/firefly"]
                  }
              }
          },
          "uuid2": {
              "type": "content-fragment",
              "value": {
                  "fields": {
                      "tags": ["mas:cloud/creative"]
                  }
              }
          }
      }
      cards = filter_products(references, product_line="firefly")
      assert len(cards) == 1
  ```

### 15. Write Integration Tests for get_adobe_products Tool
- Create `app/server/tests/test_get_adobe_products_tool.py`
- Test complete tool flow:
  ```python
  import pytest
  from httpx import AsyncClient
  from tools import get_adobe_products_tool

  @pytest.mark.asyncio
  async def test_get_adobe_products_tool_success(httpx_mock):
      """Test successful tool execution."""
      # Mock Adobe API
      httpx_mock.add_response(
          url="https://www.adobe.com/mas/io/fragment*",
          json={
              "references": {
                  "uuid1": {
                      "type": "content-fragment",
                      "value": {
                          "fields": {
                              "cardTitle": "Firefly Pro",
                              "tags": ["mas:cloud/firefly"]
                          }
                      }
                  }
              }
          }
      )

      async with AsyncClient() as client:
          result = await get_adobe_products_tool(
              client,
              "Show me Firefly products",
              product_line="firefly"
          )
          assert 'data-tool-rendered="true"' in result
          assert "Firefly Pro" in result

  @pytest.mark.asyncio
  async def test_get_adobe_products_tool_no_results():
      """Test handling when no products match filters."""
      # Test with filters that return no results

  @pytest.mark.asyncio
  async def test_get_adobe_products_tool_api_error(httpx_mock):
      """Test error handling when API fails."""
      httpx_mock.add_response(
          url="https://www.adobe.com/mas/io/fragment*",
          status_code=500
      )

      async with AsyncClient() as client:
          result = await get_adobe_products_tool(client, "Test query")
          assert "Error retrieving" in result
  ```

### 16. Create Adobe MAS Integration Documentation
- Create `ai_docs/adobe-mas-integration.md`
- Document sections:
  - **Overview**: What is Adobe MAS and how it works
  - **Architecture**: Flow from query → API → rendering → display
  - **Adobe Commerce API**: Endpoint, authentication, response structure
  - **MAS Components**: merch-card, merch-price, checkout-link usage
  - **Tool Parameters**: product_line, audience_type, comparison_count
  - **Examples**: Sample queries and expected output
  - **Troubleshooting**: Common issues (CORS, API errors, rendering)
  - **Design Reference**: Link to adobe.com/creativecloud/plans.html

### 17. Update README with Adobe MAS Feature
- Open `README.md`
- Add new section after "AG-UI Protocol Support" (around line 303):
  ```markdown
  ## Adobe Product Integration

  The AI agent can display Adobe product pricing and information as interactive
  cards using Adobe's MAS (Merch At Scale) web components.

  ### Example Queries
  - "Show me Adobe Firefly pricing plans"
  - "Compare Creative Cloud plans for students"
  - "What Adobe products are available?"

  ### How It Works
  1. User asks about Adobe products
  2. Agent calls `get_adobe_products` tool
  3. Tool fetches live data from Adobe Commerce API
  4. Tool renders MAS component HTML
  5. Frontend displays interactive product cards

  ### Features
  - Live pricing from Adobe's official API
  - Interactive "Buy now" and "Free trial" buttons
  - Responsive grid layout (mobile, tablet, desktop)
  - Dark theme compatible
  - Streams progressively in real-time

  For detailed documentation, see [Adobe MAS Integration Guide](./ai_docs/adobe-mas-integration.md)
  ```

### 18. Run Backend Tests
- Execute test suite:
  ```bash
  cd app/server
  uv run pytest tests/test_adobe_commerce_client.py -v
  uv run pytest tests/test_adobe_mas_renderer.py -v
  uv run pytest tests/test_get_adobe_products_tool.py -v
  ```
- Verify all tests pass
- Check test coverage with `pytest --cov=adobe_commerce_client --cov=adobe_mas_renderer`

### 19. Test MAS Library Serving
- Start server: `cd app/server && uvicorn agent_api:app --reload --port 8001`
- Verify MAS endpoint: `curl http://localhost:8001/mas/mas.js`
- Should return 429KB JavaScript file
- Check logs for "Mounted MAS library at /mas"

### 20. Test Adobe Commerce API Integration
- With server running, test API client in Python REPL:
  ```python
  import asyncio
  from httpx import AsyncClient
  from adobe_commerce_client import fetch_adobe_commerce_data

  async def test():
      async with AsyncClient() as client:
          data = await fetch_adobe_commerce_data(client)
          print(f"References: {len(data.get('references', {}))}")
          return data

  asyncio.run(test())
  ```
- Verify data structure matches expected format
- Check for product cards with variant, osi, prices fields

### 21. Test Frontend HTML Rendering
- Start both server and client: `./scripts/start.sh`
- Open browser to `http://localhost:5173`
- Log in with test user
- Send query: "Show me Adobe Firefly pricing"
- Verify:
  - Agent invokes `get_adobe_products` tool (check server logs)
  - Response streams progressively
  - MAS cards render with proper styling
  - Cards are responsive (test mobile view)
  - Dark theme works correctly
  - No CORS errors in browser console

### 22. Test Product Filtering
- Test different filter combinations:
  - "Show me Firefly products" → product_line="firefly"
  - "Compare Creative Cloud plans for students" → audience_type="students"
  - "What Adobe products are available under $20?" → Parse pricing
- Verify correct products displayed for each filter

### 23. Test Error Handling
- Simulate API failure (disconnect network or modify URL)
- Verify error message displays: "Error retrieving Adobe products"
- Test with invalid filters
- Verify graceful degradation

### 24. Validate Responsive Design
- Test on different screen sizes:
  - Mobile (< 768px): Single column
  - Tablet (768-1024px): Two columns
  - Desktop (> 1024px): Auto-fit grid
- Verify cards scale appropriately
- Check spacing and gaps

### 25. Validate Dark Theme Compatibility
- Switch to dark mode in app
- Verify MAS cards respect theme colors
- Check text contrast and readability
- Ensure borders and backgrounds adapt

### 26. Run All Validation Commands
- Execute every validation command below
- Document any issues found
- Fix issues and re-test
- Confirm zero regressions in existing features

## Testing Strategy

### Unit Tests

#### Adobe Commerce Client Tests
- `test_fetch_adobe_commerce_data_success()` - Verify successful API fetch
- `test_fetch_adobe_commerce_data_api_error()` - Verify error handling for API failures
- `test_fetch_adobe_commerce_data_network_error()` - Verify network error handling
- `test_fetch_adobe_commerce_data_timeout()` - Verify timeout handling
- `test_adobe_commerce_response_structure()` - Verify expected JSON structure

#### MAS Renderer Tests
- `test_render_merch_card()` - Verify single card HTML generation
- `test_render_merch_card_missing_fields()` - Verify safe defaults for missing data
- `test_render_product_comparison()` - Verify grid HTML with multiple cards
- `test_render_product_comparison_max_limit()` - Verify 6 card limit enforced
- `test_filter_products_by_product_line()` - Verify product line filtering
- `test_filter_products_by_audience_type()` - Verify audience filtering
- `test_filter_products_combined_filters()` - Verify multiple filter combination

#### Tool Tests
- `test_get_adobe_products_tool_success()` - Verify complete tool execution
- `test_get_adobe_products_tool_with_filters()` - Verify filtering works
- `test_get_adobe_products_tool_no_results()` - Verify empty results message
- `test_get_adobe_products_tool_api_error()` - Verify error message returned
- `test_get_adobe_products_tool_html_structure()` - Verify HTML output format

#### Frontend Tests
- `test_sanitizeToolHTML()` - Verify DOMPurify configuration
- `test_sanitize_allows_mas_elements()` - Verify MAS tags whitelisted
- `test_sanitize_allows_mas_attributes()` - Verify MAS attributes allowed
- `test_sanitize_blocks_malicious_content()` - Verify XSS prevention

### Integration Tests

#### End-to-End Flow Tests
- Start server and client
- Send "Show me Adobe Firefly pricing" query
- Verify tool invoked (check logs)
- Verify HTML response with `data-tool-rendered="true"`
- Verify MAS cards render in browser
- Verify interactive elements functional (buttons, links)

#### Agent Integration Tests
- Test tool works with standard agent (`AgentDeps`)
- Test tool works with AG-UI agent (`AgentStateDeps`)
- Verify streaming works through both endpoints
- Verify conversation history includes HTML responses

#### API Integration Tests
- Mock Adobe Commerce API with various responses
- Test with complete product catalog
- Test with partial product data
- Test with malformed API responses
- Test with slow API responses (timeout)

### Edge Cases

#### API Edge Cases
- Adobe API returns 500 error → Display error message
- Adobe API returns empty references → Display "No products found"
- Adobe API returns malformed JSON → Catch and log error
- Network timeout → Display timeout error
- API rate limiting → Handle gracefully

#### Rendering Edge Cases
- Product with missing fields → Use safe defaults
- Product with very long title → Truncate gracefully
- Product with special characters → Proper HTML escaping
- Zero products match filters → Display helpful message
- More than 6 products match → Limit to 6 with message

#### Frontend Edge Cases
- HTML without `data-tool-rendered` attribute → Render as markdown
- Malformed HTML → DOMPurify sanitizes safely
- Very large HTML response → Handle efficiently
- MAS library fails to load → Graceful degradation
- Custom elements not supported (old browser) → Fallback display

#### User Query Edge Cases
- Vague query "Adobe products" → Show general selection
- Specific query "Firefly Standard plan" → Filter precisely
- Query with typos "Show me Fiefly" → Agent should correct and call tool
- Query about pricing under specific amount → Parse and explain

## Acceptance Criteria

1. **MAS Library Self-Hosted**: MAS library served from `http://localhost:8001/mas/mas.js` with zero CORS errors
2. **Tool Registration**: `get_adobe_products` tool registered for both standard and AG-UI agents
3. **Adobe API Integration**: Tool fetches live data from Adobe Commerce API successfully
4. **Product Filtering**: Filtering by product_line and audience_type works correctly
5. **HTML Rendering**: Tool returns valid HTML with `data-tool-rendered="true"` marker
6. **Frontend Detection**: MessageItem component detects and renders tool HTML
7. **HTML Sanitization**: DOMPurify whitelists MAS elements and attributes safely
8. **Responsive Layout**: Cards display correctly on mobile (1 col), tablet (2 col), desktop (auto-fit)
9. **Dark Theme**: MAS cards respect dark theme with proper colors and contrast
10. **Interactive Elements**: "Buy now" and "Free trial" buttons functional
11. **Streaming Works**: HTML content streams progressively in real-time
12. **Error Handling**: Clear error messages when API fails or no products found
13. **Performance**: API fetch completes in < 2 seconds, rendering in < 100ms
14. **Visual Match**: Cards match Adobe's production design (reference: adobe.com/creativecloud/plans.html)
15. **Tests Passing**: All backend tests pass with >80% coverage
16. **Documentation**: Comprehensive docs with examples and troubleshooting
17. **Zero Regressions**: Existing agent features work unchanged

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

### Installation Validation
```bash
# Install frontend dependencies
cd app/client
npm install dompurify @types/dompurify
npm list dompurify
# Should show: dompurify@3.x.x

# Verify MAS library exists
ls -lh app/server/mas/dist/mas.js
# Should show: 429KB mas.js file
```

### Backend Test Validation
```bash
# Run all server tests including new Adobe tests
cd app/server && uv run pytest

# Run specific Adobe Commerce client tests
cd app/server && uv run pytest -v tests/test_adobe_commerce_client.py

# Run MAS renderer tests
cd app/server && uv run pytest -v tests/test_adobe_mas_renderer.py

# Run tool integration tests
cd app/server && uv run pytest -v tests/test_get_adobe_products_tool.py

# Check test coverage for new modules
cd app/server && uv run pytest --cov=adobe_commerce_client --cov=adobe_mas_renderer --cov-report=term-missing
```

### Server Startup Validation
```bash
# Start server and verify MAS endpoint
cd app/server && uvicorn agent_api:app --reload --port 8001 &
sleep 5

# Test health endpoint
curl http://localhost:8001/health
# Should return: {"status": "healthy", ...}

# Test MAS library endpoint
curl -I http://localhost:8001/mas/mas.js
# Should return: 200 OK with content-type: application/javascript

# Verify file size
curl http://localhost:8001/mas/mas.js | wc -c
# Should return: ~439296 bytes (429KB)
```

### Adobe Commerce API Validation
```bash
# Test API client directly
cd app/server
python3 << 'EOF'
import asyncio
from httpx import AsyncClient
from adobe_commerce_client import fetch_adobe_commerce_data

async def test():
    async with AsyncClient() as client:
        data = await fetch_adobe_commerce_data(client)
        print(f"✓ Fetched {len(data.get('references', {}))} products")

        # Verify structure
        assert 'references' in data
        assert len(data['references']) > 0

        # Check first product
        first_ref = list(data['references'].values())[0]
        assert 'fields' in first_ref.get('value', {})
        print("✓ API response structure valid")

asyncio.run(test())
EOF
```

### Frontend Build Validation
```bash
# Build frontend to check for TypeScript errors
cd app/client
npm run build
# Should complete with: "build complete in XXXms"

# Verify no TypeScript errors
npm run type-check || echo "Add type-check script to package.json"
```

### Full Integration Test (Manual)
```bash
# Start both server and client
./scripts/start.sh

# In browser console (http://localhost:5173):
# 1. Open developer tools
# 2. Check Network tab for CORS errors (should be none)
# 3. Verify MAS library loads: http://localhost:8001/mas/mas.js (200 OK)

# Test queries in chat:
# 1. "Show me Adobe Firefly pricing plans"
#    - Verify: 3 product cards display
#    - Verify: Cards have icons, names, prices, descriptions
#    - Verify: "Buy now" buttons present
#    - Check server logs for: "Calling get_adobe_products tool"

# 2. "Compare Creative Cloud plans for students"
#    - Verify: Filtered to student products
#    - Verify: Student-specific pricing shown

# 3. "What Adobe products are available?"
#    - Verify: General product selection shown
#    - Verify: Multiple categories displayed

# Responsive design test:
# 1. Resize browser to mobile width (< 768px)
#    - Verify: Single column layout
# 2. Resize to tablet width (768-1024px)
#    - Verify: Two column layout
# 3. Resize to desktop width (> 1024px)
#    - Verify: Auto-fit grid (3+ columns)

# Dark theme test:
# 1. Toggle dark mode in app settings
#    - Verify: MAS cards adapt to dark theme
#    - Verify: Text remains readable
#    - Verify: Borders and backgrounds appropriate
```

### Error Handling Validation
```bash
# Test with Adobe API unavailable
# Modify ADOBE_COMMERCE_API_URL to invalid endpoint
# Send query: "Show me Firefly products"
# Should display: "Error retrieving Adobe products"

# Test with invalid filters
# Send query with unsupported product line
# Should display: "No Adobe products found matching your criteria"
```

### Performance Validation
```bash
# Test API response time
time curl -s "https://www.adobe.com/mas/io/fragment?id=0d0af87d-f183-4cde-b88c-bb4729a5c3e5&api_key=wcms-commerce-ims-ro-user-milo&locale=en_US" > /dev/null
# Should complete in < 2 seconds

# Test rendering performance
cd app/server
python3 << 'EOF'
import asyncio
import time
from httpx import AsyncClient
from tools import get_adobe_products_tool

async def test():
    async with AsyncClient() as client:
        start = time.time()
        html = await get_adobe_products_tool(client, "Test query")
        elapsed = time.time() - start
        print(f"Rendering took {elapsed*1000:.2f}ms")
        assert elapsed < 0.5, "Rendering too slow"
        print("✓ Performance acceptable")

asyncio.run(test())
EOF
```

### Documentation Validation
```bash
# Verify documentation files exist
test -f ai_docs/adobe-mas-integration.md && echo "✓ Adobe MAS docs exist"
grep -q "Adobe Product Integration" README.md && echo "✓ README updated"

# Check documentation completeness
grep -q "Adobe Commerce API" ai_docs/adobe-mas-integration.md && echo "✓ API docs present"
grep -q "Troubleshooting" ai_docs/adobe-mas-integration.md && echo "✓ Troubleshooting section present"
```

### Regression Testing
```bash
# Verify existing features still work

# 1. Test existing agents work
cd app/server
python3 << 'EOF'
from agent import agent, agui_agent
print(f"✓ Standard agent tools: {len(agent.tools)}")
print(f"✓ AG-UI agent tools: {len(agui_agent.tools)}")
assert len(agent.tools) > 0
assert len(agui_agent.tools) > 0
EOF

# 2. Test existing endpoints
curl -X POST http://localhost:8001/api/pydantic-agent
# Should return: 401 Unauthorized (auth required, but endpoint works)

curl -X POST http://localhost:8001/api/ag-ui
# Should return: 401 Unauthorized (auth required, but endpoint works)

# 3. Test existing tools (web search, RAG, etc.)
# Use frontend to send queries:
# - "Search the web for Python tutorials"
# - "What documents are in the knowledge base?"
# Verify these still work correctly
```

### Final Validation Checklist
```bash
# Run complete test suite
cd app/server && uv run pytest -v

# Start application
./scripts/start.sh

# Manual checks:
# ✓ MAS library loads from http://localhost:8001/mas/mas.js (no CORS)
# ✓ Query "Show me Adobe Firefly pricing" returns product cards
# ✓ Cards render with proper styling and layout
# ✓ Cards are responsive (mobile, tablet, desktop)
# ✓ Dark theme works correctly
# ✓ Interactive buttons are functional
# ✓ No console errors in browser
# ✓ Streaming works progressively
# ✓ Existing features unchanged (web search, RAG, etc.)
# ✓ Documentation complete and accurate
```

## Notes

### Why Backend Tool Rendering?
Backend tool rendering provides several advantages over client-side rendering:
1. **Security**: HTML sanitization happens server-side with controlled whitelist
2. **Performance**: Rendering logic runs once on server vs. multiple times on client
3. **Consistency**: Same HTML rendered regardless of client capabilities
4. **Maintainability**: Rendering logic centralized in backend code
5. **Streaming**: HTML can stream progressively as it's generated

### Why Self-Host MAS Library?
Adobe's CDN blocks localhost with CORS policy, making development impossible without self-hosting. By serving from `http://localhost:8001/mas/mas.js`, we:
- Avoid CORS errors completely
- Maintain full control over library version
- Enable offline development
- Improve load times (local network vs. CDN)

### Adobe Commerce API Details
The API endpoint returns a complex nested structure:
- **fields.cards**: Array of card UUIDs to display
- **references**: Map of UUID → card data with all content
- **tags**: Used for filtering (mas:cloud/firefly, mas:customer_segment/students)
- **WCS attributes**: data-wcs-osi for Web Commerce System integration

### MAS Component Architecture
MAS uses web components (custom elements) with Shadow DOM:
- **merch-card**: Main card container with variant system
- **merch-price**: Price display with WCS integration
- **checkout-link**: Purchase buttons with analytics
- **Slots**: Named slots for content placement (heading-xs, body-xxs, footer)

### Product Filtering Strategy
Products are filtered using tag-based matching:
- `mas:cloud/{product}` - Product line (firefly, creative, document-cloud)
- `mas:customer_segment/{audience}` - Audience type (individual, students, business)
- Multiple filters can be combined for precise targeting

### Security Considerations
- **XSS Prevention**: DOMPurify sanitizes all HTML before rendering
- **Element Whitelist**: Only allow known MAS custom elements
- **Attribute Whitelist**: Only allow safe attributes (no onclick, onerror)
- **No External Scripts**: MAS library loaded from trusted local source
- **CSP Compatible**: Works with Content Security Policy restrictions

### Performance Optimization
- **API Caching**: Consider caching Commerce API responses (5-15 min TTL)
- **Lazy Loading**: MAS library loads async to avoid blocking page load
- **Card Limit**: Maximum 6 cards to prevent overwhelming UI
- **Progressive Rendering**: Cards stream as HTML is generated
- **Efficient Filtering**: Tag matching done in-memory after single API fetch

### Design System Alignment
MAS cards automatically match Adobe's design system:
- **Typography**: Uses Adobe Clean font family
- **Colors**: Pulls from WCS color tokens
- **Spacing**: Consistent padding and margins
- **Icons**: Adobe product icons embedded
- **Animations**: Subtle hover effects and transitions

### Browser Compatibility
MAS web components require:
- **Custom Elements v1**: Supported in all modern browsers
- **Shadow DOM v1**: Supported in all modern browsers
- **ES Modules**: Supported in all modern browsers
- **Fallback**: Consider polyfills for IE11 if needed (unlikely)

### Future Enhancements
- **Price Comparison**: Add tool parameter to highlight price differences
- **Currency Support**: Support multiple currencies via locale parameter
- **Favorites**: Allow users to save/compare specific products
- **Notifications**: Alert when prices change
- **Analytics**: Track which products users view most
- **A/B Testing**: Test different card layouts and presentations

### Known Limitations
- **Localhost Only**: Self-hosted MAS works on localhost, production needs CDN or proper CORS
- **No Real Checkout**: "Buy now" buttons open Adobe.com (can't process payments in-app)
- **API Rate Limits**: Adobe may rate limit if too many requests
- **Static Tags**: Product tags hardcoded in API response (limited filtering options)
- **No Real-Time Pricing**: Prices cached by Adobe, may not reflect instant changes

### Troubleshooting Common Issues

#### CORS Errors
- **Symptom**: Console shows "blocked by CORS policy"
- **Cause**: Loading MAS from Adobe CDN instead of local
- **Fix**: Verify `index.html` loads from `http://localhost:8001/mas/mas.js`

#### Cards Not Rendering
- **Symptom**: HTML appears as text, not components
- **Cause**: MAS library not loaded or custom elements not registered
- **Fix**: Check Network tab for `mas.js` 200 OK, check Console for errors

#### Tool Not Invoked
- **Symptom**: Agent responds with text instead of calling tool
- **Cause**: Tool description unclear or query doesn't match
- **Fix**: Ensure tool docstring mentions "Adobe products, pricing, plans"

#### API Errors
- **Symptom**: "Error retrieving Adobe products"
- **Cause**: Adobe Commerce API down or network issue
- **Fix**: Check API URL, verify network connectivity, check Adobe status page

#### Styling Issues
- **Symptom**: Cards look broken or unstyled
- **Cause**: CSS conflicts or theme incompatibility
- **Fix**: Check for CSS specificity conflicts, verify dark theme variables

### Development Workflow
1. Backend changes: Modify tool → Run tests → Restart server
2. Frontend changes: Update components → Hot reload auto-updates
3. MAS library updates: Replace `mas.js` → Hard refresh browser
4. API structure changes: Update types → Regenerate fixtures → Update tests

### Testing Philosophy
- **Unit tests** verify individual functions work correctly
- **Integration tests** verify complete flows end-to-end
- **Manual tests** verify visual appearance and UX
- **Regression tests** ensure existing features still work
- **Performance tests** ensure acceptable response times
- Aim for >80% coverage on new backend code
- Visual testing with screenshots for UI components
