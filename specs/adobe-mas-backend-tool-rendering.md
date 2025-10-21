# Feature: Adobe MAS Backend Tool Rendering with AG-UI

## Feature Description
This feature implements AG-UI backend tool rendering to dynamically display Adobe product information using Adobe's Merch At Scale (MAS) web components, populated via RAG (Retrieval-Augmented Generation). The implementation enables the agent to render interactive product cards directly in the chat interface by returning HTML with MAS web components instead of plain text responses. This creates a rich, interactive shopping experience where users can query Adobe products and receive beautifully rendered cards matching Adobe's official design system.

The feature leverages the existing AG-UI protocol support to stream rendered HTML components to the frontend, where they are displayed as interactive cards showing product information, pricing, features, and call-to-action buttons. The data is retrieved dynamically from a RAG system containing Adobe product information, ensuring accuracy and allowing for flexible querying across different product lines and audience segments.

## User Story
As a user exploring Adobe products
I want to ask natural language questions about Adobe pricing and plans
So that I receive interactive, visually rich product cards that match Adobe's official design, making it easy to compare options and take action

## Problem Statement
Currently, when users ask about Adobe products, the agent returns text-based responses that lack visual hierarchy and interactivity. This creates several issues:

1. **Poor User Experience**: Text responses don't match the rich, visual experience users expect from modern e-commerce interfaces
2. **Limited Interactivity**: Users cannot click CTAs, see pricing in context, or interact with product cards
3. **Design Inconsistency**: Responses don't match Adobe's official brand and design system
4. **Information Overload**: Complex product comparisons are difficult to parse in text format
5. **No Progressive Disclosure**: All information is presented at once rather than organized into scannable cards
6. **Lack of Visual Hierarchy**: Important information (price, features, CTAs) blends into paragraphs
7. **Missing Commerce Features**: No checkout links, secure transaction badges, or direct purchase paths

To solve this, we need a way for the agent to render product information as interactive UI components that match Adobe's design system while maintaining the conversational, RAG-powered query capabilities.

## Solution Statement
Implement backend tool rendering using the AG-UI protocol to return Adobe MAS web component-based HTML instead of plain text. The solution involves:

1. **RAG System Enhancement**: Ingest and index Adobe product information (product names, tiers, pricing, features, credits, CTAs) into the existing RAG system
2. **Backend Tool Creation**: Create a `get_adobe_products` tool that queries the RAG system and returns rendered HTML containing MAS web components
3. **MAS Web Component Integration**: Load Adobe's Milo library and use `merch-card`, `merch-price`, and `checkout-link` components
4. **Frontend HTML Rendering**: Update the chat interface to safely render HTML returned by backend tools as interactive components
5. **Progressive Streaming**: Stream rendered cards progressively as the agent retrieves and processes product data
6. **Design System Compliance**: Ensure cards match Adobe's official design from creativecloud/plans.html

This approach leverages the existing AG-UI backend tool rendering pattern documented at https://dojo.ag-ui.com/langgraph/feature/backend_tool_rendering, adapting it for our Pydantic AI + FastAPI architecture.

## Relevant Files
Use these files to implement the feature:

### Backend Core Files
- **`app/server/tools.py`** - Contains agent tool implementations. We'll add the new `get_adobe_products_tool` function that queries RAG and returns rendered HTML with MAS web components.

- **`app/server/agent.py`** - Pydantic AI agent definition. We'll register the new Adobe products tool with the agent so it can be invoked during conversations.

- **`app/server/db_utils.py`** - Database utilities for querying Supabase. We'll use existing RAG functions to retrieve Adobe product data from the document store.

- **`app/server/document_ingestion.py`** - Document ingestion for RAG. We'll add logic to ingest Adobe product catalog data into the RAG system.

- **`app/server/ag_ui_handlers.py`** - AG-UI request handlers. We may need to update to properly handle HTML tool responses and ensure they're marked for safe rendering.

### Frontend Core Files
- **`app/client/src/components/chat/MessageItem.tsx`** - Message rendering component. We'll add support for rendering HTML tool responses using dangerouslySetInnerHTML with proper sanitization.

- **`app/client/src/types/database.types.ts`** - TypeScript type definitions. We'll add types for tool-rendered messages and HTML content.

- **`app/client/index.html`** - Main HTML file. We'll add the Adobe Milo MAS library script to load web components globally.

- **`app/client/src/index.css`** - Global styles. We'll add any necessary CSS overrides to ensure MAS components render properly in our dark theme.

### Data Files
- **`data/adobe_products.json`** - New JSON file containing Adobe product catalog data with all product tiers, pricing, features, and metadata needed to populate MAS web components.

### Configuration Files
- **`app/server/.env.sample`** - Environment configuration. We'll add any MAS-specific configuration like API endpoints or feature flags.

### New Files

#### Backend Implementation
- **`app/server/adobe_mas_renderer.py`** - New module containing HTML rendering logic for Adobe MAS web components. Includes template functions to generate merch-cards with proper structure and data.

- **`app/server/tests/test_adobe_mas_tool.py`** - Unit tests for the Adobe products tool, testing RAG queries, HTML rendering, and component structure.

#### Data Ingestion
- **`scripts/ingest_adobe_catalog.py`** - Script to ingest Adobe product catalog into RAG system with proper chunking and metadata for semantic search.

#### Frontend Integration
- **`app/client/src/components/chat/ToolRenderedCard.tsx`** - New React component for safely rendering tool-returned HTML with proper sanitization and error handling.

- **`app/client/src/lib/html-sanitizer.ts`** - HTML sanitization utility to safely render backend-provided HTML while allowing MAS web component tags.

#### Documentation
- **`ai_docs/adobe-mas-integration.md`** - Documentation explaining the Adobe MAS integration, component usage, and data structure requirements.

## Implementation Plan

### Phase 1: Foundation
Set up the infrastructure for Adobe product data and MAS web component support:
- Create Adobe product catalog data structure with all required fields (product names, tiers, pricing, features, credits, CTAs)
- Set up data ingestion pipeline to load Adobe product information into RAG system
- Configure Adobe Milo library loading in the frontend
- Create HTML rendering templates for MAS web components
- Set up HTML sanitization infrastructure in frontend for safe rendering

### Phase 2: Core Implementation
Implement the backend tool and RAG integration:
- Create `get_adobe_products_tool` that queries RAG for product information
- Implement HTML rendering logic that populates MAS web components with RAG data
- Add progressive streaming support to stream cards as they're generated
- Register tool with Pydantic AI agent
- Implement query parsing to extract product line, audience type, and comparison parameters
- Create structured data formatting from RAG results to component properties

### Phase 3: Integration
Connect frontend and backend, ensuring proper rendering and user experience:
- Add HTML rendering support to MessageItem component with sanitization
- Create ToolRenderedCard component for displaying backend-rendered content
- Test progressive streaming of rendered cards
- Validate MAS web component functionality (interactive buttons, links, pricing)
- Ensure design matches Adobe's official creativecloud/plans.html
- Add responsive layout support for side-by-side card display
- Integrate with existing conversation flow and message history

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Create Adobe Product Catalog Data Structure
- Create `data/adobe_products.json` with comprehensive product information
- Include all Adobe product lines (Firefly, Creative Cloud, Document Cloud, etc.)
- Structure data with fields: productName, tier, icon, price, priceMonthly, description, credits, features (array), detailsLink, ctaText, audience (all/students/business)
- Add metadata for RAG indexing: product_line, category, audience_type, last_updated
- Validate JSON structure with example entries for Adobe Firefly Standard, Pro, and Premium
- Include minimum 3 product lines with 3 tiers each for comprehensive testing

### 2. Create HTML Rendering Module for MAS Components
- Create `app/server/adobe_mas_renderer.py`
- Implement `render_merch_card()` function that generates HTML for a single merch-card with proper attributes
- Create `render_product_comparison()` function that generates a grid of cards with responsive layout
- Add template functions for merch-price and checkout-link components
- Include proper data attributes for MAS components (variant="plans", size, etc.)
- Add security badge and CTA button rendering
- Implement card wrapper with proper CSS classes for layout and responsiveness
- Add error handling for missing data fields with sensible defaults

### 3. Implement Adobe Product Data Ingestion
- Create `scripts/ingest_adobe_catalog.py` script
- Read `data/adobe_products.json` and chunk products for RAG indexing
- Create document chunks with metadata: product_line, tier, audience, category
- Generate embeddings using existing embedding client
- Store in Supabase documents table with file_id="adobe-products-catalog"
- Add file metadata to document_metadata table with schema information
- Include chunking strategy that keeps product information cohesive (one chunk per product tier)
- Test ingestion with sample data before full catalog

### 4. Create RAG Query Function for Adobe Products
- Open `app/server/tools.py`
- Create `get_adobe_products_rag_query()` helper function
- Implement semantic search query construction for product queries
- Add filtering by product_line and audience_type using metadata
- Return top 3-5 most relevant products based on query
- Parse RAG results into structured product data dictionaries
- Add relevance scoring and ranking logic
- Handle edge cases: no results, partial matches, ambiguous queries

### 5. Implement Backend Tool for Adobe Products
- In `app/server/tools.py`, create `get_adobe_products_tool()` async function
- Accept parameters: query (str), product_line (optional), audience_type (optional), comparison_count (int, default 3)
- Call `get_adobe_products_rag_query()` to retrieve relevant products
- Import `adobe_mas_renderer` and call `render_product_comparison()` with RAG results
- Return rendered HTML string containing MAS web components
- Add comprehensive docstring explaining tool usage and parameters
- Implement error handling with user-friendly fallback messages
- Add logging for debugging tool invocations

### 6. Register Adobe Products Tool with Agent
- Open `app/server/agent.py`
- Import `get_adobe_products_tool` from tools module
- Register tool with agent using `@agent.tool` decorator or similar Pydantic AI pattern
- Add tool description that helps LLM understand when to invoke it (e.g., "Use this tool when user asks about Adobe products, pricing, plans, or subscriptions")
- Test tool registration by checking agent's available tools list
- Verify tool parameters are properly typed for Pydantic validation

### 7. Load Adobe Milo MAS Library in Frontend
- Open `app/client/index.html`
- Add script tag to load Adobe Milo library: `<script src="https://www.adobe.com/etc.clientlibs/globalnav/clientlibs/base/mas.js" type="module"></script>`
- Add defer/async attributes for optimal loading
- Verify library loads in browser console with no errors
- Test that web components are registered globally (check for `<merch-card>` support)
- Add fallback handling if library fails to load

### 8. Create HTML Sanitization Utility
- Create `app/client/src/lib/html-sanitizer.ts`
- Implement `sanitizeToolHTML()` function using DOMPurify or similar library
- Configure allowed tags to include MAS web components: `merch-card`, `merch-price`, `checkout-link`
- Allow necessary attributes: `variant`, `size`, `badge-background-color`, `href`, etc.
- Add URL validation for href attributes (only allow adobe.com domains)
- Export sanitization function with comprehensive JSDoc
- Add unit tests for sanitization with malicious input examples

### 9. Create ToolRenderedCard Component
- Create `app/client/src/components/chat/ToolRenderedCard.tsx`
- Accept props: htmlContent (string), messageId (string), onError (callback)
- Implement safe HTML rendering using sanitized content
- Add error boundary for catching rendering errors
- Include loading state for progressive streaming updates
- Add CSS classes for responsive grid layout (cards side-by-side on desktop, stacked on mobile)
- Test with sample MAS component HTML
- Add accessibility attributes (ARIA labels, roles)

### 10. Update MessageItem to Render Tool HTML
- Open `app/client/src/components/chat/MessageItem.tsx`
- Detect if message contains tool-rendered HTML (check message metadata or special markers)
- When HTML detected, use ToolRenderedCard component instead of markdown rendering
- Preserve existing markdown rendering for non-tool messages
- Add conditional rendering logic with proper TypeScript types
- Test with mixed messages (text + tool HTML in same conversation)
- Ensure styling consistency between text and tool-rendered messages

### 11. Update TypeScript Types for Tool Rendering
- Open `app/client/src/types/database.types.ts`
- Add `ToolRenderedContent` type with fields: htmlContent, toolName, timestamp
- Update `Message` type to optionally include toolRendered field
- Add type guards for checking if message has tool-rendered content
- Export all new types for use across components
- Ensure backward compatibility with existing message structure

### 12. Add CSS Styling for MAS Components
- Open `app/client/src/index.css`
- Add CSS custom properties for MAS component theming to match dark theme
- Override MAS component default styles for background colors, text colors
- Add responsive grid styles for product cards (CSS Grid or Flexbox)
- Ensure proper spacing, borders, and shadows for cards
- Test rendering in light mode (if applicable) and adjust accordingly
- Add hover states for interactive elements (cards, buttons)
- Verify accessibility with sufficient color contrast

### 13. Implement Progressive Streaming for Tool Responses
- Open `app/server/ag_ui_handlers.py`
- Modify streaming logic to handle HTML tool responses
- Add support for partial HTML streaming (stream cards as they're generated)
- Implement chunking strategy: stream one card at a time for progressive reveal
- Test streaming with multiple product cards
- Ensure frontend properly handles partial HTML updates
- Add error recovery if streaming is interrupted

### 14. Create Adobe Product Tool Tests
- Create `app/server/tests/test_adobe_mas_tool.py`
- Test RAG query with various product queries (Firefly, Creative Cloud, students, etc.)
- Test HTML rendering generates valid MAS component markup
- Test filtering by product_line and audience_type
- Test edge cases: no matching products, invalid parameters, empty RAG results
- Test HTML output structure matches expected schema
- Verify all required MAS component attributes are present
- Test error handling and fallback messages

### 15. Test Frontend HTML Rendering
- Start development server with `npm run dev`
- Test ToolRenderedCard component with sample MAS HTML
- Verify MAS web components render correctly with proper styling
- Test interactive elements (buttons, links) are functional
- Test responsive layout on mobile, tablet, and desktop viewports
- Verify dark theme compatibility with MAS components
- Test error handling when HTML is malformed
- Validate accessibility with screen reader testing

### 16. Create Comprehensive Adobe Product Dataset
- Expand `data/adobe_products.json` with complete product catalog
- Include all major Adobe products: Creative Cloud, Document Cloud, Experience Cloud
- Add detailed feature lists, pricing for different regions (if applicable)
- Include student/teacher pricing alongside standard pricing
- Add business/enterprise plan information
- Ensure data accuracy by referencing official Adobe pricing pages
- Add metadata tags for better RAG retrieval (use cases, target audience, product category)

### 17. Run Data Ingestion Script
- Execute `uv run scripts/ingest_adobe_catalog.py`
- Verify all products are ingested into Supabase documents table
- Check embeddings are generated correctly
- Query RAG system manually to test retrieval quality
- Adjust chunking strategy if retrieval accuracy is poor
- Re-run ingestion if data structure needs changes
- Validate document_metadata entries are created

### 18. End-to-End Integration Testing
- Start full application with `./scripts/start.sh`
- Log in to the chat interface
- Test queries:
  - "Show me Adobe Firefly pricing plans"
  - "Compare Creative Cloud plans for students"
  - "What Adobe products are available for businesses?"
  - "Show me all Adobe photography tools and their prices"
- Verify cards render correctly with all elements (icon, name, price, features, CTA)
- Test streaming updates happen progressively
- Verify CTAs and links are functional
- Test conversation history persists tool-rendered messages correctly

### 19. Create Documentation
- Create `ai_docs/adobe-mas-integration.md`
- Document the architecture: RAG → Tool → MAS Components → Frontend
- Explain data structure for adobe_products.json
- Provide examples of tool invocations and expected outputs
- Document MAS component attributes and customization options
- Include troubleshooting section for common rendering issues
- Add screenshots or diagrams showing the rendered cards
- Document how to extend to other Adobe product lines

### 20. Run All Validation Commands
- Execute every validation command listed in the Validation Commands section
- Fix any failures or errors discovered
- Re-run tests until all pass with zero regressions
- Verify feature works end-to-end with production-like data
- Validate performance is acceptable (cards render within 2 seconds)
- Check memory usage and streaming efficiency

## Testing Strategy

### Unit Tests

#### Backend Tool Tests
- `test_get_adobe_products_basic_query()` - Test basic product query returns valid results
- `test_get_adobe_products_with_filters()` - Test filtering by product_line and audience_type
- `test_render_merch_card_html()` - Test HTML generation for single merch-card
- `test_render_product_comparison()` - Test multi-card grid rendering
- `test_adobe_tool_no_results()` - Test graceful handling when RAG returns no results
- `test_adobe_tool_invalid_params()` - Test validation of tool parameters
- `test_html_sanitization()` - Test HTML output is safe (no script injection)

#### RAG Query Tests
- `test_rag_query_firefly()` - Test querying for Firefly products
- `test_rag_query_creative_cloud()` - Test querying for Creative Cloud
- `test_rag_query_students()` - Test filtering by student audience
- `test_rag_query_relevance()` - Test results are ranked by relevance
- `test_rag_query_empty()` - Test handling of queries with no matches

#### Frontend Component Tests
- `test_tool_rendered_card_rendering()` - Test ToolRenderedCard renders HTML correctly
- `test_html_sanitization_frontend()` - Test sanitizer removes dangerous content
- `test_message_item_tool_detection()` - Test MessageItem detects tool HTML
- `test_mas_component_loading()` - Test MAS library loads successfully

### Integration Tests

#### Full Flow Tests
- Test complete user query → RAG → tool invocation → HTML generation → frontend rendering
- Test multiple product comparisons in single conversation
- Test switching between text responses and tool-rendered cards
- Test conversation history with tool-rendered messages loads correctly
- Test streaming updates for progressive card rendering
- Test agent correctly chooses to use tool based on query context

#### Edge Case Testing
- Query with no matching products → friendly message displayed
- Malformed product data → error handled gracefully with fallback
- MAS library fails to load → fallback to text rendering or error message
- RAG system unavailable → tool returns error with helpful message
- Very large product sets (>10 cards) → pagination or limiting applied
- Concurrent tool invocations → state management handles correctly

### Edge Cases

#### Data Quality
- Missing product fields (no price, no features) → defaults applied, card still renders
- Invalid pricing format → validation catches and formats correctly
- Broken image URLs → fallback icon displayed
- Missing CTAs → generic "Learn more" link provided

#### Frontend Rendering
- MAS components not supported in browser → polyfill or graceful degradation
- Dark theme conflicts with MAS styling → CSS overrides handle properly
- Mobile viewport → responsive layout stacks cards vertically
- Accessibility tools enabled → ARIA attributes work correctly

#### Performance
- Large HTML responses (>100KB) → chunked streaming prevents freezing
- Many cards (>20) → virtual scrolling or pagination implemented
- Slow RAG queries (>5s) → loading state shown, timeout handling
- Network interruption during streaming → partial results shown with retry option

## Acceptance Criteria

1. **Tool Registration**: `get_adobe_products` tool is registered with the agent and discoverable
2. **RAG Integration**: Tool queries RAG system and retrieves relevant Adobe product data
3. **HTML Rendering**: Tool returns valid HTML with MAS web components (merch-card, merch-price, checkout-link)
4. **Frontend Display**: Chat interface renders tool HTML as interactive product cards
5. **Card Structure**: Cards display all required elements (icon, name, price, description, features, CTA, security badge)
6. **Visual Design**: Cards match Adobe's official design from creativecloud/plans.html
7. **Responsive Layout**: Cards display side-by-side on desktop, stacked on mobile
8. **Progressive Streaming**: Cards appear progressively as data is retrieved and processed
9. **Interactivity**: All buttons, links, and CTAs are functional
10. **Data Accuracy**: Product information matches official Adobe catalog
11. **Filtering Support**: Tool correctly filters by product_line and audience_type parameters
12. **Error Handling**: Graceful fallbacks for missing data, failed queries, or rendering errors
13. **Accessibility**: Cards are accessible with screen readers and keyboard navigation
14. **Theme Compatibility**: MAS components render correctly in dark theme
15. **Conversation History**: Tool-rendered messages persist and reload correctly
16. **Performance**: Cards render within 2 seconds of query submission
17. **Security**: HTML sanitization prevents XSS and script injection
18. **Zero Regressions**: Existing chat functionality unaffected by changes

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

### Backend Tests
```bash
# Run all server tests including new Adobe MAS tool tests
cd app/server && uv run pytest

# Run specific Adobe tool tests
cd app/server && uv run pytest -v tests/test_adobe_mas_tool.py

# Test RAG query functionality
cd app/server && python -c "from tools import get_adobe_products_rag_query; import asyncio; asyncio.run(get_adobe_products_rag_query('Adobe Firefly pricing'))"

# Test HTML rendering
cd app/server && python -c "from adobe_mas_renderer import render_merch_card; print(render_merch_card({'productName': 'Test', 'price': '$9.99/mo'}))"
```

### Data Ingestion Validation
```bash
# Run Adobe product catalog ingestion
cd app/server && uv run python ../scripts/ingest_adobe_catalog.py

# Verify documents were ingested
cd app/server && python -c "from clients import get_agent_clients; client, supabase = get_agent_clients(); print(supabase.from_('document_metadata').select('*').eq('id', 'adobe-products-catalog').execute().data)"

# Test RAG retrieval
cd app/server && python -c "from tools import retrieve_relevant_documents_tool; from clients import get_agent_clients; import asyncio; client, supabase = get_agent_clients(); print(asyncio.run(retrieve_relevant_documents_tool(supabase, client, 'Adobe Firefly')))"
```

### Frontend Tests
```bash
# Start frontend dev server
cd app/client && npm run dev

# Run frontend tests (if configured)
cd app/client && npm run test || echo "No frontend tests configured yet"

# Build production bundle to check for errors
cd app/client && npm run build
```

### Integration Testing
```bash
# Start both server and client
./scripts/start.sh

# In browser, navigate to http://localhost:5173
# Test queries:
# 1. "Show me Adobe Firefly pricing plans"
# 2. "Compare Creative Cloud plans for students"
# 3. "What Adobe products are good for photographers?"

# Verify:
# - Cards render with all elements
# - Prices display correctly
# - CTAs are clickable
# - Layout is responsive
# - Dark theme looks good
```

### HTML Sanitization Validation
```bash
# Test sanitizer allows MAS components but blocks scripts
cd app/client && node -e "const {sanitizeToolHTML} = require('./src/lib/html-sanitizer'); console.log(sanitizeToolHTML('<merch-card><script>alert(1)</script></merch-card>'))"
# Should output: merch-card without script tag
```

### Performance Validation
```bash
# Test query response time
curl -X POST http://localhost:8001/api/ag-ui \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"message","content":"Show Adobe Firefly plans"}' \
  -w "Total time: %{time_total}s\n"
# Should complete in < 5 seconds
```

### Accessibility Validation
```bash
# Run accessibility audit in browser DevTools
# 1. Open http://localhost:5173
# 2. Send query for Adobe products
# 3. Open DevTools > Lighthouse
# 4. Run accessibility audit
# 5. Verify score > 90
```

### Security Validation
```bash
# Test XSS prevention
# In chat, send query that might return malicious HTML
# Verify <script> tags and dangerous attributes are stripped

# Test CSRF protection
# Verify all API requests include proper authentication tokens
```

## Notes

### Dependencies Added
- **Adobe Milo Library**: Loaded from Adobe CDN for MAS web components
- **DOMPurify** (or similar): HTML sanitization library for frontend (add via `npm install dompurify`)
- No new Python dependencies required (uses existing RAG, OpenAI, Supabase clients)

### Adobe MAS Components Used
- **merch-card**: Primary product card component with variant="plans"
- **merch-price**: Pricing display with proper formatting
- **checkout-link**: CTA buttons for purchases and sign-ups
- Additional components may be explored: mini-compare-chart, plans, product

### Data Structure Design
The Adobe product catalog follows this structure for optimal RAG retrieval:
```json
{
  "products": [
    {
      "id": "firefly-pro",
      "productName": "Adobe Firefly Pro",
      "productLine": "Firefly",
      "tier": "pro",
      "audience": ["all"],
      "icon": "https://...",
      "price": "US$19.99/mo",
      "priceMonthly": 19.99,
      "currency": "USD",
      "description": "...",
      "credits": "4,000 credits for creative AI",
      "features": ["Feature 1", "Feature 2"],
      "detailsLink": "https://www.adobe.com/...",
      "ctaText": "Select",
      "ctaLink": "https://www.adobe.com/...",
      "metadata": {
        "category": "creative-ai",
        "use_cases": ["design", "content-creation"],
        "last_updated": "2025-01-20"
      }
    }
  ]
}
```

### Technical Decisions

**Why MAS Web Components over React Components?**
- MAS components are Adobe's official design system
- Pre-built with proper styling and accessibility
- Maintained by Adobe with updates
- No need to recreate complex product cards from scratch
- Guaranteed to match adobe.com design

**Why Backend Rendering over Frontend Rendering?**
- Agent has full context from RAG query
- HTML generation happens server-side with all data available
- Progressive streaming of complete cards (not partial data + client rendering)
- Follows AG-UI backend tool rendering pattern
- Reduces frontend complexity and state management

**Why RAG over API Calls?**
- Product data is semi-static (changes infrequently)
- RAG provides semantic search for flexible queries
- No API rate limits or authentication needed
- Works offline once data is ingested
- Can combine multiple data sources easily

### Future Enhancements
- **Live Pricing Updates**: Integrate with Adobe Commerce API for real-time pricing
- **Personalization**: Show different plans based on user profile (student, business)
- **Comparison Features**: Side-by-side comparison tables with diff highlighting
- **Add to Cart**: Direct purchase flow integration
- **Product Recommendations**: "Users who viewed this also looked at..."
- **Regional Pricing**: Automatically show pricing in user's currency/region
- **A/B Testing**: Test different card layouts and CTAs for conversion optimization
- **Analytics**: Track which products users query most frequently
- **Admin Panel**: Update product catalog without re-running ingestion

### Security Considerations
- **HTML Sanitization**: Critical to prevent XSS attacks from RAG data
- **URL Validation**: Only allow adobe.com links in CTAs to prevent phishing
- **Data Integrity**: Validate product data during ingestion to prevent corruption
- **Access Control**: Ensure only authenticated users can query products
- **Rate Limiting**: Prevent abuse of expensive RAG queries

### Performance Optimization
- **Caching**: Cache frequently queried products (Firefly, Creative Cloud) in Redis
- **Lazy Loading**: Load MAS library only when needed (not on every page load)
- **Progressive Streaming**: Stream one card at a time to show results faster
- **RAG Optimization**: Tune embedding model and chunk sizes for faster retrieval
- **HTML Minification**: Minify rendered HTML to reduce payload size
- **CDN**: Serve MAS library from CDN for global performance

### Design Considerations
- Match Adobe's color palette: use Adobe red (#EB1000) for CTAs
- Ensure proper spacing and alignment for cards (16px gaps)
- Use Adobe Clean or similar font for consistency
- Maintain visual hierarchy: Price > Name > Features > CTA
- Add hover effects on cards for interactivity feedback
- Use subtle shadows and borders to separate cards
- Ensure mobile-first responsive design

### Accessibility Requirements
- All cards must have proper ARIA labels (`aria-label`, `role="article"`)
- Keyboard navigation must work (Tab to navigate between cards)
- Focus indicators must be visible on interactive elements
- Color contrast must meet WCAG AA standards (4.5:1 for text)
- Screen readers must announce all relevant information
- CTA buttons must have descriptive text (not just "Select")
- Images must have alt text

### Testing Philosophy
- Test backend and frontend independently before integration
- Use realistic product data in tests (not just minimal examples)
- Test edge cases extensively (missing data, network errors, etc.)
- Validate HTML structure with automated tools (HTML validators)
- Perform manual testing on multiple browsers and devices
- Include accessibility testing in every test cycle
- Monitor performance with real-world data volumes

### Rollout Strategy
1. **Phase 1**: Deploy with Adobe Firefly products only (3 tiers)
2. **Phase 2**: Add Creative Cloud products (Photography, Video, etc.)
3. **Phase 3**: Add Document Cloud and other product lines
4. **Phase 4**: Enable student/teacher/business audience filtering
5. **Phase 5**: Add advanced features (comparison, recommendations)

### Monitoring and Metrics
- Track tool invocation rate (how often users query Adobe products)
- Measure time-to-render for cards (target: <2s)
- Monitor RAG query accuracy (relevance of results)
- Track CTR on product CTAs (conversion funnel)
- Monitor error rates (failed queries, rendering errors)
- Collect user feedback on card usefulness
