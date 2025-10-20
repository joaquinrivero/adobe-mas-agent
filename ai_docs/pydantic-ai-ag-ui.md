# Pydantic AI AG-UI Integration

## Overview

Pydantic AI provides native integration with the AG-UI (Agent User Interaction) Protocol, an open standard that standardizes how frontend applications communicate with AI agents. This integration enables:

- **Streaming responses**: Real-time streaming of agent outputs
- **Frontend tools**: Tools that can be executed on the frontend
- **Shared state**: Bidirectional state synchronization between frontend and backend
- **Custom events**: Application-specific events for enhanced interactivity

## Installation

Install Pydantic AI with AG-UI support:

```bash
# Using pip
pip install 'pydantic-ai-slim[ag-ui]'

# Using uv
uv add 'pydantic-ai-slim[ag-ui]'
```

Additionally, install an ASGI server for deployment:

```bash
pip install uvicorn
```

## Three Implementation Approaches

Pydantic AI offers three methods for implementing AG-UI agents, listed from most to least flexible:

### 1. Direct Stream Handling: `run_ag_ui()`

**Use Case**: Maximum flexibility for non-Starlette frameworks (Django, Flask, etc.)

**Description**: Accepts an agent and `RunAgentInput` object, returns encoded AG-UI event streams.

**Benefits**:
- Works with any Python web framework
- Complete control over request/response handling
- Custom middleware and authentication

**Example**:

```python
from pydantic_ai import Agent
from pydantic_ai.ag_ui import run_ag_ui
from ag_ui.core import RunAgentInput

agent = Agent('openai:gpt-4o', instructions='Be helpful!')

async def handle_request(run_input: RunAgentInput):
    # Returns an async generator of encoded AG-UI events
    async for event in run_ag_ui(agent, run_input):
        yield event
```

### 2. Starlette Request Handler: `handle_ag_ui_request()`

**Use Case**: Recommended for FastAPI and other Starlette-based frameworks

**Description**: Directly processes Starlette requests and returns streaming responses.

**Benefits**:
- Simplest integration with FastAPI
- Automatic request parsing
- Built-in response streaming
- **This is what you typically want to use**

**Example**:

```python
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from pydantic_ai import Agent
from pydantic_ai.ag_ui import handle_ag_ui_request

agent = Agent('openai:gpt-4o', instructions='Be fun!')
app = FastAPI()

@app.post('/')
async def run_agent(request: Request) -> Response:
    return await handle_ag_ui_request(agent, request)
```

### 3. Standalone ASGI App: `Agent.to_ag_ui()`

**Use Case**: Simple deployments without additional web framework

**Description**: Converts an agent into a complete ASGI application.

**Benefits**:
- No additional web framework needed
- Minimal boilerplate
- Quick prototyping
- Standalone deployment

**Example**:

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', instructions='Be helpful!')
app = agent.to_ag_ui()

# Deploy with: uvicorn module_name:app
```

## State Management with StateDeps

One of the key features of AG-UI is bidirectional state synchronization. Pydantic AI implements this using `StateDeps` with Pydantic models.

### Basic State Setup

```python
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.ag_ui import StateDeps

class DocumentState(BaseModel):
    document: str = ''
    word_count: int = 0
    last_modified: str = ''

agent = Agent(
    'openai:gpt-4o',
    instructions='Help edit documents',
    deps_type=StateDeps[DocumentState],
)

# Create ASGI app with initial state
app = agent.to_ag_ui(deps=StateDeps(DocumentState()))
```

### How State Works

1. **Validation**: State from AG-UI requests (dictionaries) is automatically validated against your Pydantic model
2. **Synchronization**: State updates are synchronized between frontend and backend
3. **Type Safety**: Pydantic ensures type correctness and validation
4. **Bidirectional**: Both frontend and backend can update the state

### Accessing State in Tools

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.ag_ui import StateDeps

@agent.tool
async def update_document(
    ctx: RunContext[StateDeps[DocumentState]],
    new_content: str
) -> str:
    # Access current state
    current_state = ctx.deps.state

    # Update state
    ctx.deps.state.document = new_content
    ctx.deps.state.word_count = len(new_content.split())

    return f"Document updated with {ctx.deps.state.word_count} words"
```

## Frontend Tools

AG-UI frontend tools are seamlessly provided to the Pydantic AI agent. These tools enable rich user interfaces where the frontend can execute certain operations.

### How Frontend Tools Work

1. **Definition**: Tools are defined on the frontend using the AG-UI protocol
2. **Discovery**: Pydantic AI agent receives tool definitions from the frontend
3. **Invocation**: Agent can call frontend tools during execution
4. **Execution**: Frontend executes the tool and returns results
5. **Continuation**: Agent continues with the tool results

### Example Flow

```
User Input → Agent Processing → Agent Calls Frontend Tool
                ↑                            ↓
          Tool Result ← Frontend Executes Tool
                ↑                            ↓
          Agent Continues → Final Response
```

## Custom Events

Tools can emit AG-UI events via `ToolReturn` metadata, enabling custom application behavior and rich interactivity.

### Emitting Custom Events

```python
from ag_ui.core import CustomEvent, EventType, StateSnapshotEvent
from pydantic_ai import Agent, RunContext, ToolReturn

agent = Agent('openai:gpt-4o')

@agent.tool_plain
async def custom_events() -> ToolReturn:
    """Example tool that emits custom events"""
    return ToolReturn(
        return_value='Custom events sent',
        metadata=[
            CustomEvent(
                type=EventType.CUSTOM,
                name='progress',
                value={'step': 1, 'total': 3}
            ),
            CustomEvent(
                type=EventType.CUSTOM,
                name='progress',
                value={'step': 2, 'total': 3}
            ),
            CustomEvent(
                type=EventType.CUSTOM,
                name='completed',
                value=True
            ),
        ]
    )
```

### State Snapshot Events

```python
@agent.tool
async def update_state_tool(
    ctx: RunContext[StateDeps[DocumentState]]
) -> ToolReturn:
    # Update state
    ctx.deps.state.document = "New document content"

    # Emit state snapshot event
    return ToolReturn(
        return_value='State updated',
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=ctx.deps.state.model_dump()
            )
        ]
    )
```

### Available Event Types

From `ag_ui.core.EventType`:

- `TEXT_MESSAGE_START`, `TEXT_MESSAGE_CONTENT`, `TEXT_MESSAGE_END`
- `TOOL_CALL_START`, `TOOL_CALL_ARGS`, `TOOL_CALL_END`
- `STATE_SNAPSHOT`, `STATE_DELTA`
- `MESSAGES_SNAPSHOT`
- `CUSTOM`
- `RUN_STARTED`, `RUN_FINISHED`, `RUN_ERROR`
- `STEP_STARTED`, `STEP_FINISHED`

## Complete Example: Document Editor Agent

Here's a comprehensive example combining all features:

```python
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.ag_ui import handle_ag_ui_request, StateDeps
from ag_ui.core import CustomEvent, EventType

# Define state model
class DocumentState(BaseModel):
    document: str = ''
    word_count: int = 0
    char_count: int = 0
    version: int = 0

# Create agent with state
agent = Agent(
    'openai:gpt-4o',
    instructions='''
    You are a document editing assistant.
    Help users edit and analyze their documents.
    Track document statistics and versions.
    ''',
    deps_type=StateDeps[DocumentState],
)

# Add tools
@agent.tool
async def update_document(
    ctx: RunContext[StateDeps[DocumentState]],
    new_content: str
) -> ToolReturn:
    """Update the document content and statistics"""
    ctx.deps.state.document = new_content
    ctx.deps.state.word_count = len(new_content.split())
    ctx.deps.state.char_count = len(new_content)
    ctx.deps.state.version += 1

    return ToolReturn(
        return_value=f"Document updated to version {ctx.deps.state.version}",
        metadata=[
            CustomEvent(
                type=EventType.CUSTOM,
                name='document_updated',
                value={
                    'version': ctx.deps.state.version,
                    'word_count': ctx.deps.state.word_count,
                    'char_count': ctx.deps.state.char_count,
                }
            )
        ]
    )

@agent.tool
async def get_statistics(
    ctx: RunContext[StateDeps[DocumentState]]
) -> str:
    """Get document statistics"""
    state = ctx.deps.state
    return f"""
    Document Statistics:
    - Words: {state.word_count}
    - Characters: {state.char_count}
    - Version: {state.version}
    """

# Create FastAPI app
app = FastAPI()

@app.post('/agent')
async def run_document_agent(request: Request) -> Response:
    return await handle_ag_ui_request(
        agent,
        request,
        deps=StateDeps(DocumentState())
    )

# Run with: uvicorn module_name:app --reload
```

## Deployment

Deploy your AG-UI agent with Uvicorn:

```bash
# Development
uvicorn module_name:app --reload

# Production
uvicorn module_name:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Variables

```bash
# Set your LLM API key
export OPENAI_API_KEY=your-api-key-here

# Or for Anthropic
export ANTHROPIC_API_KEY=your-api-key-here
```

## Architecture

### Request Flow

1. **Frontend sends request**: AG-UI RunAgentInput with messages, tools, context, state
2. **Pydantic AI receives**: Converts RunAgentInput to internal types
3. **Validation**: State validated against Pydantic model
4. **Agent execution**: Agent.run() processes the request
5. **Event streaming**: Results streamed as Server-Sent Events
6. **Tool execution**: If frontend tools needed, multi-round interaction occurs
7. **State updates**: State synchronized back to frontend

### Event Streaming

Responses are streamed as Server-Sent Events (SSE):

```
data: {"type":"RUN_STARTED","threadId":"thread_123","runId":"run_456"}

data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"msg_789","delta":"Hello"}

data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"msg_789","delta":" world!"}

data: {"type":"RUN_FINISHED","threadId":"thread_123","runId":"run_456"}
```

## Integration with Frontend

### CopilotKit Integration

```typescript
import { useCopilotAgent } from '@copilotkit/react-core';

function MyComponent() {
  const { run, state } = useCopilotAgent({
    url: 'http://localhost:8000/agent',
    initialState: {
      document: '',
      word_count: 0,
      char_count: 0,
      version: 0,
    },
  });

  // Use the agent
  const handleEdit = async () => {
    await run('Edit the document to be more concise');
  };

  return (
    <div>
      <textarea value={state.document} readOnly />
      <p>Words: {state.word_count}</p>
      <button onClick={handleEdit}>Edit with AI</button>
    </div>
  );
}
```

## Advanced Features

### Dependencies Beyond State

You can include additional dependencies:

```python
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.ag_ui import StateDeps

class AppState(BaseModel):
    user_id: str = ''

class AppDeps:
    def __init__(self, state: AppState, db_connection):
        self.state = state
        self.db = db_connection

agent = Agent(
    'openai:gpt-4o',
    deps_type=AppDeps,
)

@agent.tool
async def save_to_db(ctx: RunContext[AppDeps], data: str) -> str:
    # Access both state and database
    await ctx.deps.db.save(ctx.deps.state.user_id, data)
    return "Saved to database"
```

### Error Handling

```python
from pydantic_ai import Agent
from pydantic_ai.exceptions import UserError

agent = Agent('openai:gpt-4o')

@agent.tool
async def risky_operation(value: int) -> str:
    if value < 0:
        raise UserError("Value must be positive")
    return f"Processed {value}"
```

### Streaming Control

```python
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4o',
    result_type=str,
)

# The run_ag_ui function handles streaming automatically
# You can configure streaming behavior via model settings
```

## Examples Repository

Pydantic AI includes examples in the `pydantic_ai_examples.ag_ui` directory:

- Basic FastAPI integration
- State management examples
- Custom event examples
- Frontend tool integration
- Complex multi-tool workflows

## Best Practices

1. **Use StateDeps for shared state**: Always use Pydantic models with StateDeps for type safety
2. **Emit custom events**: Provide feedback to users through custom events
3. **Handle errors gracefully**: Use UserError for user-facing errors
4. **Validate inputs**: Let Pydantic handle validation automatically
5. **Keep state minimal**: Only include what needs to be synchronized
6. **Use handle_ag_ui_request**: Recommended for FastAPI/Starlette apps
7. **Deploy with Uvicorn**: Use multiple workers for production

## Troubleshooting

### Common Issues

1. **State not updating**: Ensure you're modifying `ctx.deps.state` not creating new objects
2. **Events not streaming**: Check that response is being streamed, not awaited
3. **Tool not found**: Verify frontend tool definitions match agent expectations
4. **Type errors**: Ensure state model matches frontend state structure

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed AG-UI event information
```

## Summary

Pydantic AI's AG-UI integration provides:

- **Three flexible approaches**: From framework-agnostic to FastAPI-specific
- **Type-safe state management**: Using Pydantic models with StateDeps
- **Frontend tools**: Seamless integration with frontend-defined tools
- **Custom events**: Rich interactivity through event emission
- **Easy deployment**: Simple ASGI deployment with Uvicorn
- **Full AG-UI protocol support**: Streaming, state, tools, and events

This integration enables you to build sophisticated AI agents with rich frontend interactions while maintaining type safety and developer experience that Pydantic is known for.
