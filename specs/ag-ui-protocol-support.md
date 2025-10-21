# Feature: Add AG-UI Protocol Support

## Feature Description
This feature adds AG-UI (Agent User Interaction Protocol) support to the existing Pydantic AI agent backend, enabling standardized communication with CopilotKit and other AG-UI-compatible frontends. The implementation maintains full backward compatibility with the existing custom streaming endpoint at `/api/pydantic-agent`, allowing current clients to continue working without modification while enabling new AG-UI-compatible clients to connect through a new standardized endpoint.

AG-UI is a lightweight, event-based protocol that standardizes how AI agents connect to user-facing applications. By implementing AG-UI support, this application gains:
- Interoperability with CopilotKit UI components (CopilotChat, CopilotSidebar, CopilotPopup)
- Support for frontend actions (tools defined in the UI that the agent can call)
- Shared state management between frontend and agent
- Generative UI capabilities for rendering agent state as custom components
- Access to the broader AG-UI ecosystem and tooling

## User Story
As a developer integrating AI agents into frontend applications
I want to use the AG-UI protocol with my Pydantic AI backend
So that I can leverage CopilotKit's UI components, frontend actions, and state management features while maintaining compatibility with my existing custom client implementation

## Problem Statement
Currently, the application uses a custom streaming protocol at the `/api/pydantic-agent` endpoint. While this works well for the current React frontend, it has several limitations:

1. **Vendor Lock-in**: The custom protocol ties the application to a specific frontend implementation, making it difficult to switch UI frameworks or components
2. **Limited Interoperability**: Cannot use CopilotKit's rich UI components (CopilotChat, CopilotSidebar, etc.) or other AG-UI-compatible frontends
3. **Missing Frontend Actions**: No standardized way for the agent to call tools defined in the frontend application
4. **No Shared State**: Cannot synchronize state between the agent and UI in real-time using a standard protocol
5. **Maintenance Burden**: Custom protocol requires ongoing maintenance and documentation
6. **Ecosystem Isolation**: Cannot benefit from AG-UI tooling, debugging tools, and community resources

The existing streaming endpoint must remain functional to avoid breaking the current frontend implementation during the transition period.

## Solution Statement
Implement AG-UI protocol support by adding a new endpoint at `/api/ag-ui` that exposes the Pydantic AI agent through the standardized AG-UI protocol, while keeping the existing `/api/pydantic-agent` endpoint unchanged for backward compatibility.

The solution approach:
1. **Add AG-UI Dependencies**: Install `pydantic-ai-slim[ag-ui]` package which includes the necessary AG-UI protocol encoders and Starlette request handlers
2. **Create AG-UI Endpoint**: Implement a new FastAPI endpoint using Pydantic AI's `handle_ag_ui_request()` method for Starlette-based frameworks
3. **Refactor Agent Dependencies**: Extract agent creation and dependency setup into reusable functions that both endpoints can use
4. **Implement State Management**: Use Pydantic AI's `StateDeps` pattern to support AG-UI's shared state features
5. **Frontend Actions Support**: Enable the agent to discover and call frontend-defined actions through the AG-UI protocol
6. **Maintain Backward Compatibility**: Keep existing endpoint and all its functionality unchanged
7. **Add Configuration**: Use environment variables to control AG-UI features (enable/disable, debug mode, etc.)

This dual-endpoint approach allows for gradual migration: existing clients continue using the custom endpoint while new integrations can leverage the AG-UI endpoint with all its features.

## Relevant Files
Use these files to implement the feature:

### Backend Core Files
- **`app/server/agent_api.py`** - Main FastAPI application with API endpoints. This is where we'll add the new AG-UI endpoint alongside the existing custom streaming endpoint.

- **`app/server/agent.py`** - Pydantic AI agent definition with tools and dependencies. We'll refactor this to support AG-UI's StateDeps pattern while maintaining compatibility with the existing AgentDeps.

- **`app/server/clients.py`** - Client setup functions for Supabase, OpenAI, and Mem0. May need minor updates to support AG-UI state management.

- **`app/server/db_utils.py`** - Database utility functions. No changes needed, but will be used by both endpoints.

- **`app/server/prompt.py`** - Agent system prompt. No changes needed.

- **`app/server/tools.py`** - Agent tool implementations. No changes needed, works with both endpoints.

### Configuration Files
- **`app/server/requirements.txt`** - Python dependencies. We'll add `pydantic-ai-slim[ag-ui]` and any related dependencies.

- **`app/server/.env.sample`** - Environment configuration template. We'll add new AG-UI-related environment variables:
  - `AGUI_ENABLED` - Enable/disable AG-UI endpoint
  - `AGUI_DEBUG` - Enable debug logging for AG-UI events
  - `AGUI_ALLOW_FRONTEND_ACTIONS` - Enable frontend actions feature

### Documentation Files
- **`README.md`** - Project documentation. We'll add a new section explaining the AG-UI endpoint and how to use it with CopilotKit.

- **`ai_docs/ag-ui-integration.md`** - New documentation file explaining AG-UI protocol usage, frontend actions, shared state, and examples.

### Testing Files
- **`app/server/tests/test_agui_endpoint.py`** - New test file for AG-UI endpoint functionality
- **`app/server/tests/test_agent.py`** - Update existing agent tests to ensure compatibility with both dependency types

### New Files

#### Backend Implementation
- **`app/server/ag_ui_handlers.py`** - New file containing AG-UI-specific request handlers, state management, and frontend action support

- **`app/server/ag_ui_types.py`** - New file defining Pydantic models for AG-UI state and frontend actions

#### Documentation
- **`ai_docs/ag-ui-integration.md`** - Comprehensive guide for using the AG-UI endpoint with CopilotKit

- **`ai_docs/migration-guide.md`** - Guide for migrating from custom endpoint to AG-UI endpoint

#### Frontend Example (Optional)
- **`examples/copilotkit-integration/`** - Optional example directory showing how to integrate with CopilotKit UI components

## Implementation Plan

### Phase 1: Foundation
Set up the infrastructure for AG-UI protocol support:
- Install AG-UI dependencies (`pydantic-ai-slim[ag-ui]`)
- Add environment configuration for AG-UI features
- Create type definitions for AG-UI state and frontend actions
- Refactor agent dependency setup to support both custom and AG-UI patterns
- Add comprehensive logging for debugging

### Phase 2: Core Implementation
Implement the AG-UI endpoint and protocol handlers:
- Create AG-UI request handlers using Pydantic AI's `handle_ag_ui_request()` method
- Implement state management with `StateDeps` pattern
- Add support for frontend actions (tools defined in the UI)
- Create the `/api/ag-ui` endpoint in FastAPI
- Implement AG-UI event encoding and streaming
- Add proper error handling and validation

### Phase 3: Integration
Integrate AG-UI endpoint with existing infrastructure:
- Connect AG-UI handlers to existing database utilities
- Integrate with Mem0 for memory management
- Support conversation history in AG-UI format
- Add authentication and rate limiting to AG-UI endpoint
- Ensure both endpoints share common infrastructure (Supabase, OpenAI, etc.)
- Add comprehensive documentation and examples

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Install AG-UI Dependencies
- Open `app/server/requirements.txt`
- Add the following dependencies:
  ```
  pydantic-ai-slim[ag-ui]>=0.0.14
  starlette>=0.27.0
  ```
- Run `cd app/server && uv pip install -r requirements.txt` to install new dependencies
- Verify installation by running `uv pip list | grep -E "(pydantic-ai|starlette)"`

### 2. Add Environment Configuration
- Open `app/server/.env.sample`
- Add new AG-UI configuration section:
  ```
  # AG-UI Protocol Configuration
  AGUI_ENABLED=true                      # Enable/disable AG-UI endpoint
  AGUI_DEBUG=false                       # Enable debug logging for AG-UI
  AGUI_ALLOW_FRONTEND_ACTIONS=true       # Allow agent to call frontend actions
  AGUI_ENDPOINT_PATH=/api/ag-ui          # AG-UI endpoint path
  ```
- Copy to actual `.env` file: `cp app/server/.env.sample app/server/.env` (if not already done)
- Document each variable's purpose in comments

### 3. Create AG-UI Type Definitions
- Create new file `app/server/ag_ui_types.py`
- Define Pydantic models for AG-UI state:
  ```python
  from pydantic import BaseModel, Field
  from typing import Optional, Dict, Any, List

  class ConversationState(BaseModel):
      """Shared state between frontend and agent."""
      session_id: Optional[str] = Field(default=None, description="Current conversation session ID")
      conversation_title: Optional[str] = Field(default=None, description="Title of the conversation")
      message_count: int = Field(default=0, description="Number of messages in conversation")
      last_updated: Optional[str] = Field(default=None, description="Last update timestamp")

  class FrontendAction(BaseModel):
      """Definition of a frontend action that agent can call."""
      name: str = Field(..., description="Action name")
      description: str = Field(..., description="Action description")
      parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters schema")
  ```
- Add imports for AG-UI protocol types from `pydantic_ai`

### 4. Refactor Agent Dependencies for State Support
- Open `app/server/agent.py`
- Keep the existing `AgentDeps` dataclass unchanged for backward compatibility
- Create a new `AgentStateDeps` dataclass that includes ConversationState:
  ```python
  @dataclass
  class AgentStateDeps:
      """Dependencies with AG-UI state support."""
      supabase: Client
      embedding_client: AsyncOpenAI
      http_client: AsyncClient
      brave_api_key: str | None
      searxng_base_url: str | None
      memories: str
      state: ConversationState  # AG-UI shared state
  ```
- This allows the agent to work with both dependency types

### 5. Create AG-UI Request Handlers
- Create new file `app/server/ag_ui_handlers.py`
- Implement the main AG-UI handler function:
  ```python
  from fastapi import Request
  from pydantic_ai import Agent
  from ag_ui_types import ConversationState

  async def handle_ag_ui_agent_request(
      request: Request,
      agent: Agent,
      supabase: Client,
      embedding_client: AsyncOpenAI,
      http_client: AsyncClient,
      user_id: str
  ):
      """Handle AG-UI protocol requests using Pydantic AI's handle_ag_ui_request."""
      # Implementation using agent.handle_ag_ui_request()
  ```
- Add helper functions for state initialization and frontend action registration
- Implement logging and error handling

### 6. Add AG-UI Endpoint to FastAPI
- Open `app/server/agent_api.py`
- Import AG-UI handler and types:
  ```python
  from ag_ui_handlers import handle_ag_ui_agent_request
  from ag_ui_types import ConversationState
  ```
- Add new endpoint after the existing `/api/pydantic-agent` endpoint:
  ```python
  @app.post("/api/ag-ui")
  async def ag_ui_endpoint(request: Request, user: Dict[str, Any] = Depends(verify_token)):
      """AG-UI protocol endpoint for CopilotKit and other AG-UI clients."""
      # Check if AG-UI is enabled via environment variable
      if not os.getenv("AGUI_ENABLED", "true").lower() == "true":
          raise HTTPException(status_code=503, detail="AG-UI endpoint is disabled")

      # Handle the request using AG-UI protocol
      return await handle_ag_ui_agent_request(
          request=request,
          agent=agent,
          supabase=supabase,
          embedding_client=embedding_client,
          http_client=http_client,
          user_id=user.get("id")
      )
  ```

### 7. Implement State Management
- Open `app/server/ag_ui_handlers.py`
- Add state initialization from conversation history:
  ```python
  async def initialize_conversation_state(
      supabase: Client,
      session_id: Optional[str],
      user_id: str
  ) -> ConversationState:
      """Initialize AG-UI state from database."""
      # Fetch conversation metadata
      # Return ConversationState with current values
  ```
- Implement state update logic to sync changes back to database
- Add state validation and error handling

### 8. Add Frontend Actions Support
- Open `app/server/ag_ui_handlers.py`
- Implement frontend action discovery from AG-UI protocol:
  ```python
  def extract_frontend_actions(request_data: Dict[str, Any]) -> List[FrontendAction]:
      """Extract frontend actions from AG-UI request."""
      # Parse actions from request
      # Validate action schemas
      # Return list of FrontendAction objects
  ```
- Add logic to register frontend actions as agent tools dynamically
- Implement action execution handlers

### 9. Connect AG-UI to Database and Mem0
- Open `app/server/ag_ui_handlers.py`
- Add conversation history retrieval in AG-UI message format
- Integrate Mem0 memory retrieval for AG-UI requests
- Ensure message storage works with AG-UI event format
- Add conversation title generation for new AG-UI conversations

### 10. Add Comprehensive Logging
- Open `app/server/ag_ui_handlers.py`
- Add debug logging for AG-UI events when `AGUI_DEBUG=true`:
  ```python
  import logging
  logger = logging.getLogger(__name__)

  if os.getenv("AGUI_DEBUG", "false").lower() == "true":
      logger.info(f"AG-UI Request: {request_data}")
      logger.info(f"State: {state}")
      logger.info(f"Frontend Actions: {frontend_actions}")
  ```
- Log key events: request received, state initialized, actions registered, response sent

### 11. Write AG-UI Endpoint Tests
- Create `app/server/tests/test_agui_endpoint.py`
- Add test fixtures for AG-UI requests
- Test cases to implement:
  - `test_agui_endpoint_enabled()` - Verify endpoint works when enabled
  - `test_agui_endpoint_disabled()` - Verify 503 when disabled via env var
  - `test_agui_authentication()` - Verify authentication required
  - `test_agui_state_initialization()` - Verify state loads from database
  - `test_agui_frontend_actions()` - Verify frontend actions are registered
  - `test_agui_message_streaming()` - Verify AG-UI streaming format
  - `test_agui_conversation_history()` - Verify history loading works
  - `test_agui_state_updates()` - Verify state changes sync to database

### 12. Write AG-UI Handler Tests
- Update or create `app/server/tests/test_ag_ui_handlers.py`
- Test state management functions
- Test frontend action parsing and registration
- Test error handling for malformed requests
- Test logging functionality

### 13. Update Agent Tests for Compatibility
- Open `app/server/tests/test_agent.py` (if exists, create if not)
- Ensure agent works with both `AgentDeps` and `AgentStateDeps`
- Test that tools work with both dependency types
- Verify no regressions in existing agent functionality

### 14. Create AG-UI Integration Documentation
- Create `ai_docs/ag-ui-integration.md`
- Document sections:
  - **Overview**: What is AG-UI and why use it
  - **Quick Start**: Minimal example with CopilotKit
  - **Endpoint Reference**: `/api/ag-ui` endpoint details
  - **State Management**: How to use shared state
  - **Frontend Actions**: How to define and use frontend actions
  - **Authentication**: How auth works with AG-UI endpoint
  - **Examples**: Complete code examples for common use cases
  - **Troubleshooting**: Common issues and solutions

### 15. Create Migration Guide
- Create `ai_docs/migration-guide.md`
- Document migration path from custom endpoint to AG-UI
- Explain backward compatibility guarantees
- Provide comparison table of features
- Include step-by-step migration instructions
- Add code examples showing before/after

### 16. Update Main README
- Open `README.md`
- Add new section "AG-UI Protocol Support" after API Endpoints section:
  ```markdown
  ## AG-UI Protocol Support

  This application supports the AG-UI (Agent User Interaction) protocol for
  standardized communication with CopilotKit and other AG-UI-compatible frontends.

  ### Endpoints
  - `POST /api/pydantic-agent` - Custom streaming endpoint (existing, maintained for compatibility)
  - `POST /api/ag-ui` - AG-UI protocol endpoint (new, for CopilotKit integration)

  ### Quick Start with CopilotKit
  [Link to integration guide]

  ### Features
  - Frontend actions support
  - Shared state management
  - Generative UI capabilities
  - Full CopilotKit UI component support
  ```

### 17. Add Environment Variables to README
- Update README.md Environment Configuration section
- Add AG-UI configuration variables
- Explain each variable's purpose and default values
- Add example usage scenarios

### 18. Create Example CopilotKit Integration (Optional)
- Create directory `examples/copilotkit-integration/`
- Add minimal Next.js example showing:
  - CopilotKit provider setup
  - Using CopilotChat component
  - Defining frontend actions
  - Shared state usage
- Include README with setup instructions

### 19. Test Backward Compatibility
- Start the server with both endpoints enabled
- Test existing custom endpoint `/api/pydantic-agent`:
  - Verify authentication works
  - Verify message streaming works
  - Verify conversation history loads
  - Verify all existing features work unchanged
- Confirm zero regressions in existing functionality

### 20. Test AG-UI Endpoint Manually
- Install CopilotKit in a test frontend (or use curl with AG-UI format)
- Test basic message exchange via `/api/ag-ui`
- Test state synchronization
- Test frontend action registration and execution
- Verify AG-UI event format compliance
- Test with debug logging enabled

### 21. Run All Validation Commands
- Execute all validation commands listed below
- Fix any issues discovered
- Re-run tests until all pass
- Verify both endpoints work correctly

## Testing Strategy

### Unit Tests

#### AG-UI Handler Tests
- `test_initialize_conversation_state()` - Verify state loads from database correctly
- `test_state_validation()` - Verify invalid state is rejected
- `test_extract_frontend_actions()` - Verify frontend actions parse correctly
- `test_frontend_action_validation()` - Verify invalid actions are rejected
- `test_state_update_sync()` - Verify state changes sync to database

#### Endpoint Tests
- `test_agui_endpoint_authentication()` - Verify JWT authentication required
- `test_agui_endpoint_rate_limiting()` - Verify rate limits apply
- `test_agui_endpoint_enabled_flag()` - Verify env var controls endpoint availability
- `test_agui_message_format()` - Verify AG-UI event format compliance
- `test_agui_streaming()` - Verify streaming responses work correctly

#### Agent Tests
- `test_agent_with_agentdeps()` - Verify agent works with existing dependencies
- `test_agent_with_statedeps()` - Verify agent works with AG-UI state dependencies
- `test_tools_compatibility()` - Verify tools work with both dependency types
- `test_agent_prompt_consistency()` - Verify prompts consistent across both endpoints

### Integration Tests

#### Full Flow Tests
- Create conversation via AG-UI endpoint
- Send multiple messages and verify state updates
- Test frontend action execution flow
- Verify conversation history persists correctly
- Test Mem0 memory integration with AG-UI
- Verify RAG tools work through AG-UI endpoint

#### Compatibility Tests
- Run same conversation through both endpoints simultaneously
- Verify database state is consistent
- Test switching between endpoints mid-conversation
- Verify no data corruption or loss

### Edge Cases

#### AG-UI Specific
- Invalid AG-UI event format → proper error response
- Missing required state fields → defaults applied
- Frontend action with invalid parameters → validation error
- State update conflicts → last-write-wins with warning
- Very large state objects → size limits enforced
- Malformed frontend action definitions → rejected with clear error

#### Backward Compatibility
- Existing client connects to custom endpoint → works unchanged
- New client connects to custom endpoint → works as before
- Old database conversations → load correctly via AG-UI
- Missing state metadata → gracefully handle with defaults

#### Performance
- High message rate via AG-UI → handle gracefully
- Large state objects → efficient serialization
- Many frontend actions → efficient registration
- Concurrent requests to both endpoints → no conflicts

## Acceptance Criteria

1. **AG-UI Endpoint Available**: New `/api/ag-ui` endpoint is accessible and responds to POST requests
2. **Authentication Required**: AG-UI endpoint requires valid JWT token, returns 401 otherwise
3. **AG-UI Format Compliance**: Responses follow AG-UI protocol event format specification
4. **Message Streaming**: Agent responses stream correctly using AG-UI events
5. **State Management**: Shared state syncs between frontend and agent via ConversationState
6. **Frontend Actions**: Frontend actions are discovered, registered, and executable by agent
7. **Conversation History**: Historical messages load correctly in AG-UI format
8. **Mem0 Integration**: Memory retrieval works with AG-UI requests
9. **Database Persistence**: Messages and state persist correctly to Supabase
10. **Backward Compatibility**: Existing `/api/pydantic-agent` endpoint works unchanged
11. **Configuration**: AG-UI features controllable via environment variables
12. **Error Handling**: Clear error messages for invalid AG-UI requests
13. **Logging**: Debug logging available when enabled via `AGUI_DEBUG=true`
14. **Documentation**: Comprehensive docs for AG-UI integration and migration
15. **Tests Passing**: All unit and integration tests pass with >80% coverage
16. **Zero Regressions**: Existing functionality unaffected by changes
17. **CopilotKit Compatible**: Works with CopilotKit UI components out of the box

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

### Installation Validation
```bash
# Verify AG-UI dependencies installed
cd app/server && uv pip list | grep -E "(pydantic-ai|starlette|ag-ui)"

# Verify version compatibility
cd app/server && python -c "import pydantic_ai; print(pydantic_ai.__version__)"
```

### Backend Test Validation
```bash
# Run all server tests including new AG-UI tests
cd app/server && uv run pytest

# Run specific AG-UI endpoint tests
cd app/server && uv run pytest -v tests/test_agui_endpoint.py

# Run AG-UI handler tests
cd app/server && uv run pytest -v tests/test_ag_ui_handlers.py

# Run agent compatibility tests
cd app/server && uv run pytest -v tests/test_agent.py

# Check test coverage
cd app/server && uv run pytest --cov=. --cov-report=term-missing
```

### Linting and Type Checking
```bash
# Run linting if configured
cd app/server && uv run ruff check . || echo "Ruff not configured"

# Type check with mypy if configured
cd app/server && uv run mypy . || echo "MyPy not configured"
```

### Server Startup Validation
```bash
# Start server and check for errors
cd app/server && uv run uvicorn agent_api:app --reload --port 8001 &
sleep 5
curl http://localhost:8001/health
# Should return: {"status": "healthy", ...}
```

### Endpoint Availability Validation
```bash
# Test health endpoint
curl http://localhost:8001/health

# Verify AG-UI endpoint exists (will fail auth, but 401 proves endpoint exists)
curl -X POST http://localhost:8001/api/ag-ui
# Should return: 401 Unauthorized (proves endpoint exists and requires auth)

# Verify existing endpoint still works
curl -X POST http://localhost:8001/api/pydantic-agent
# Should return: 401 Unauthorized (proves backward compatibility)
```

### AG-UI Protocol Validation
```bash
# Test with valid AG-UI format (requires valid JWT token)
# Replace YOUR_TOKEN with actual Supabase JWT token
curl -X POST http://localhost:8001/api/ag-ui \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "content": "Hello",
    "state": {"session_id": null}
  }'
# Should return: AG-UI formatted streaming response
```

### Environment Configuration Validation
```bash
# Test with AG-UI disabled
cd app/server
export AGUI_ENABLED=false
uv run uvicorn agent_api:app --reload --port 8002 &
sleep 5
curl -X POST http://localhost:8002/api/ag-ui
# Should return: 503 Service Unavailable

# Test with debug logging enabled
export AGUI_DEBUG=true
# Check logs for debug output
```

### Database Integration Validation
```bash
# Connect to Supabase and verify conversations table unchanged
# No schema changes needed, verify existing tables work
```

### Full Integration Test (Manual)
```bash
# Start both server and client
./scripts/start.sh

# In browser:
# 1. Navigate to http://localhost:5173
# 2. Log in with test user
# 3. Send messages via existing interface (uses custom endpoint)
# 4. Verify everything works as before (backward compatibility)

# For AG-UI testing:
# 1. Install CopilotKit in a test Next.js app
# 2. Configure it to use http://localhost:8001/api/ag-ui
# 3. Test message exchange
# 4. Test frontend actions
# 5. Test state synchronization
```

### Documentation Validation
```bash
# Verify documentation files exist and are readable
test -f ai_docs/ag-ui-integration.md && echo "AG-UI docs exist"
test -f ai_docs/migration-guide.md && echo "Migration guide exists"
grep -q "AG-UI Protocol Support" README.md && echo "README updated"
```

### Backward Compatibility Validation
```bash
# Run existing client against server
# Verify all existing features work:
# - Authentication
# - Message streaming
# - Conversation history
# - File uploads
# - Mem0 memories
# - RAG search
# - All tools

# No regressions should occur
```

## Notes

### Implementation Approach
We chose the **dual-endpoint approach** (keeping `/api/pydantic-agent` and adding `/api/ag-ui`) rather than replacing the existing endpoint because:
1. **Zero Breaking Changes**: Existing frontend continues working without modification
2. **Gradual Migration**: Teams can migrate at their own pace
3. **A/B Testing**: Can compare both protocols in production
4. **Risk Mitigation**: Can rollback to custom endpoint if AG-UI has issues
5. **Feature Parity**: Both endpoints can coexist until AG-UI proves superior

### Technical Decisions

**Why Pydantic AI's `handle_ag_ui_request()`?**
- Recommended approach for FastAPI/Starlette frameworks
- Handles protocol encoding/decoding automatically
- Provides type safety with Pydantic models
- Maintained by Pydantic AI team

**Why `StateDeps` pattern?**
- Standard way to add state to Pydantic AI agents
- Type-safe with Pydantic validation
- Easy to extend with additional state fields
- Clean separation from business logic dependencies

**Why separate `ag_ui_handlers.py` file?**
- Keeps AG-UI logic isolated for easier maintenance
- Prevents bloating `agent_api.py`
- Makes testing easier
- Follows single-responsibility principle

### Dependencies Added
- `pydantic-ai-slim[ag-ui]>=0.0.14` - Core AG-UI support from Pydantic AI
- `starlette>=0.27.0` - ASGI framework support (may already be installed via FastAPI)

### Future Enhancements
- **Frontend Migration**: Eventually migrate React frontend to use CopilotKit components and AG-UI endpoint
- **Deprecation Plan**: After migration, could deprecate custom endpoint (with long notice period)
- **Advanced Features**: Implement generative UI components for rich agent interactions
- **State Snapshots**: Save state snapshots for conversation replay/debugging
- **Frontend Action Templates**: Create reusable frontend action templates
- **AG-UI Analytics**: Track usage metrics for AG-UI endpoint
- **Performance Monitoring**: Add detailed performance metrics for AG-UI vs custom endpoint

### Security Considerations
- Both endpoints use same authentication (JWT tokens via `verify_token`)
- AG-UI endpoint respects same rate limits as custom endpoint
- Frontend actions should be validated and sanitized
- State updates must be authorized (user can only update own state)
- Enable `AGUI_DEBUG` only in development (logs may contain sensitive data)

### Performance Considerations
- AG-UI protocol has minimal overhead (event encoding is fast)
- State management adds small overhead per request
- Frontend actions registered dynamically per request (negligible cost)
- Consider caching frequently accessed state if performance becomes issue
- Both endpoints share same agent instance (no duplication)

### Compatibility Notes
- AG-UI protocol is framework-agnostic (works with any frontend)
- CopilotKit is the primary consumer but not the only one
- Custom endpoint will remain supported indefinitely
- No database schema changes required
- Existing tools and features work with both endpoints

### Development Workflow
1. Develop new features for both endpoints simultaneously
2. Test both endpoints for regressions
3. Document endpoint-specific behavior if any
4. Maintain feature parity where possible
5. Consider AG-UI as primary endpoint for new features

### Testing Philosophy
- Test both endpoints independently
- Test interactions between endpoints
- Test database consistency across endpoints
- Test backward compatibility continuously
- Aim for >80% code coverage on new code

### Documentation Strategy
- Keep AG-UI docs separate from main README initially
- Link to docs from README
- Provide migration guide for teams wanting to switch
- Include code examples for common use cases
- Document limitations and known issues
