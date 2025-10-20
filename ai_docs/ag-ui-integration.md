# AG-UI Integration Guide

## Overview

This application supports the **AG-UI (Agent User Interaction)** protocol for standardized communication with CopilotKit and other AG-UI-compatible frontends. AG-UI provides a lightweight, event-based protocol that enables:

- **Interoperability** with CopilotKit UI components (CopilotChat, CopilotSidebar, CopilotPopup)
- **Frontend Actions** - tools defined in the UI that the agent can call
- **Shared State Management** between frontend and agent
- **Generative UI** capabilities for rendering agent state as custom components
- **Standard Protocol** for broader ecosystem compatibility

## Quick Start

### Endpoint Information

**AG-UI Endpoint:** `POST /api/ag-ui`

**Authentication:** Requires JWT token from Supabase (same as custom endpoint)

**Content-Type:** `application/json`

**Response:** `text/event-stream` (Server-Sent Events)

### Basic Request Example

```bash
curl -X POST http://localhost:8001/api/ag-ui \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "content": "Hello, can you help me with my project?",
    "state": {
      "session_id": null,
      "message_count": 0
    }
  }'
```

### CopilotKit Integration Example

```typescript
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";

function App() {
  return (
    <CopilotKit
      runtimeUrl="http://localhost:8001/api/ag-ui"
      headers={{
        Authorization: `Bearer ${supabaseToken}`
      }}
    >
      <YourApp />
      <CopilotChat
        labels={{
          title: "AI Assistant",
          initial: "Hello! How can I help you today?"
        }}
      />
    </CopilotKit>
  );
}
```

## AG-UI Protocol Details

### Request Format

```typescript
interface AGUIRequest {
  type: string;              // "message" | "action_result"
  content?: string;          // User message content
  state?: ConversationState; // Shared state
  frontend_actions?: FrontendAction[]; // UI-defined actions
  metadata?: object;         // Additional metadata
}

interface ConversationState {
  session_id?: string;       // Conversation session ID
  conversation_title?: string; // Conversation title
  message_count: number;     // Number of messages
  last_updated?: string;     // Last update timestamp (ISO)
  user_id?: string;          // User ID from auth
}

interface FrontendAction {
  name: string;              // Action name
  description: string;       // What the action does
  parameters: object;        // JSON Schema for parameters
}
```

### Response Format (Server-Sent Events)

The AG-UI endpoint streams events in Server-Sent Events format:

```
data: {"type":"text_delta","data":{"content":"Hello"},"timestamp":"2025-10-20T23:45:00Z"}

data: {"type":"state_update","data":{"session_id":"abc123","message_count":2},"timestamp":"2025-10-20T23:45:01Z"}

data: {"type":"completion","data":{"session_id":"abc123"},"timestamp":"2025-10-20T23:45:02Z"}
```

#### Event Types

- **`text_delta`** - Streaming text chunks from agent response
- **`state_update`** - Updates to conversation state
- **`completion`** - Marks end of agent response
- **`error`** - Error occurred during processing

## State Management

### Shared State

The `ConversationState` is synchronized bidirectionally:

1. **Frontend → Agent**: Pass state in request
2. **Agent → Frontend**: Receive state updates via `state_update` events

```typescript
// Frontend sends state
const state = {
  session_id: "existing-session-123",
  message_count: 10
};

fetch('/api/ag-ui', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    type: 'message',
    content: 'Continue our conversation',
    state: state
  })
});
```

### State Fields

- **`session_id`**: Unique conversation identifier (auto-generated if null)
- **`conversation_title`**: Auto-generated or custom title
- **`message_count`**: Total messages in conversation
- **`last_updated`**: Last modification timestamp
- **`user_id`**: Authenticated user ID (set automatically)

## Frontend Actions

Frontend actions allow the agent to call functions defined in your UI.

### Defining Frontend Actions

```typescript
const frontendActions = [
  {
    name: "show_notification",
    description: "Display a notification to the user",
    parameters: {
      type: "object",
      properties: {
        message: {
          type: "string",
          description: "The notification message"
        },
        severity: {
          type: "string",
          enum: ["info", "success", "warning", "error"],
          description: "Notification severity level"
        }
      },
      required: ["message"]
    }
  },
  {
    name: "navigate",
    description: "Navigate to a different page",
    parameters: {
      type: "object",
      properties: {
        url: { type: "string" }
      },
      required: ["url"]
    }
  }
];

// Send actions with request
fetch('/api/ag-ui', {
  method: 'POST',
  body: JSON.stringify({
    type: 'message',
    content: 'Show me the dashboard',
    frontend_actions: frontendActions
  })
});
```

### Handling Action Calls

When the agent calls a frontend action, you'll receive events indicating the tool call. Implement handlers in your frontend:

```typescript
// CopilotKit automatically handles frontend actions
<CopilotKit
  actions={[
    {
      name: "show_notification",
      description: "Display a notification",
      parameters: [
        { name: "message", type: "string" },
        { name: "severity", type: "string" }
      ],
      handler: async ({ message, severity }) => {
        toast[severity](message);
      }
    }
  ]}
>
  {/* Your app */}
</CopilotKit>
```

## Environment Configuration

Configure AG-UI features via environment variables in `.env`:

```env
# Enable/disable AG-UI endpoint (default: true)
AGUI_ENABLED=true

# Enable debug logging for AG-UI events (default: false)
# WARNING: May log sensitive data - only enable in development
AGUI_DEBUG=false

# Allow agent to call frontend-defined actions (default: true)
AGUI_ALLOW_FRONTEND_ACTIONS=true

# AG-UI endpoint path (default: /api/ag-ui)
AGUI_ENDPOINT_PATH=/api/ag-ui
```

## Authentication

AG-UI endpoint uses the same authentication as the custom endpoint:

1. **JWT Token Required**: Pass Supabase JWT in `Authorization: Bearer <token>` header
2. **User Verification**: Token is verified against Supabase auth
3. **User Context**: User ID extracted from token and used for conversation ownership

```typescript
// Get Supabase token
const { data: { session } } = await supabase.auth.getSession();
const token = session?.access_token;

// Use in request
fetch('/api/ag-ui', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## Error Handling

### Error Event Format

```json
{
  "type": "error",
  "data": {
    "message": "Error description"
  },
  "timestamp": "2025-10-20T23:45:00Z"
}
```

### Common Error Codes

- **401 Unauthorized**: Invalid or missing JWT token
- **503 Service Unavailable**: AG-UI endpoint disabled via `AGUI_ENABLED=false`
- **500 Internal Server Error**: Processing error (check logs)

## Troubleshooting

### AG-UI Endpoint Not Available

**Problem**: Getting 503 Service Unavailable

**Solution**: Check that `AGUI_ENABLED=true` in your `.env` file

### No State Updates

**Problem**: Not receiving `state_update` events

**Solution**: Ensure you're sending initial state in request and listening for SSE events

### Frontend Actions Not Working

**Problem**: Agent can't call frontend actions

**Solution**:
1. Check `AGUI_ALLOW_FRONTEND_ACTIONS=true`
2. Verify actions have valid JSON Schema in `parameters`
3. Enable `AGUI_DEBUG=true` to see action registration logs

### Authentication Failures

**Problem**: Getting 401 errors

**Solution**:
1. Verify Supabase JWT token is valid
2. Check `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in backend `.env`
3. Ensure token hasn't expired

## Debugging

Enable debug logging to see detailed AG-UI events:

```env
AGUI_DEBUG=true
```

This logs:
- Incoming AG-UI requests
- State initialization and updates
- Frontend action registration
- Event streaming details

**⚠️ WARNING**: Debug logs may contain sensitive data. Only enable in development.

## Examples

### Example 1: New Conversation

```typescript
const response = await fetch('/api/ag-ui', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    type: 'message',
    content: 'What can you help me with?',
    state: {
      session_id: null,  // New conversation
      message_count: 0
    }
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { value, done } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const event = JSON.parse(line.slice(6));
      console.log('Event:', event);
    }
  }
}
```

### Example 2: Continue Existing Conversation

```typescript
fetch('/api/ag-ui', {
  method: 'POST',
  body: JSON.stringify({
    type: 'message',
    content: 'Tell me more about that',
    state: {
      session_id: 'existing-session-abc123',
      message_count: 4
    }
  })
});
```

### Example 3: With Frontend Actions

```typescript
fetch('/api/ag-ui', {
  method: 'POST',
  body: JSON.stringify({
    type: 'message',
    content: 'Notify me when done',
    frontend_actions: [
      {
        name: 'send_notification',
        description: 'Send a browser notification',
        parameters: {
          type: 'object',
          properties: {
            title: { type: 'string' },
            body: { type: 'string' }
          }
        }
      }
    ]
  })
});
```

## Next Steps

- Read the [Migration Guide](./migration-guide.md) to transition from custom endpoint
- Explore [CopilotKit Documentation](https://docs.copilotkit.ai)
- Check out AG-UI protocol specification
- Join the AG-UI community for support
