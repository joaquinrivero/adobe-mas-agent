# Migration Guide: Custom Endpoint to AG-UI

This guide helps you migrate from the custom streaming endpoint (`/api/pydantic-agent`) to the AG-UI protocol endpoint (`/api/ag-ui`).

## Why Migrate?

Moving to AG-UI provides:

- ✅ **CopilotKit Compatibility**: Use CopilotChat, CopilotSidebar, and other UI components
- ✅ **Frontend Actions**: Let agents call UI-defined functions
- ✅ **Shared State**: Bidirectional state synchronization
- ✅ **Standard Protocol**: Interoperability with AG-UI ecosystem
- ✅ **Future-Proof**: Built on standardized protocol vs custom implementation

## Backward Compatibility

**Good news**: The custom endpoint (`/api/pydantic-agent`) remains fully functional!

- Both endpoints run simultaneously
- No breaking changes to existing code
- Migrate at your own pace
- Can run A/B tests between endpoints

## Feature Comparison

| Feature | Custom Endpoint | AG-UI Endpoint |
|---------|----------------|----------------|
| **Authentication** | ✅ JWT (Supabase) | ✅ JWT (Supabase) |
| **Streaming** | ✅ Custom format | ✅ SSE (Server-Sent Events) |
| **Conversation History** | ✅ Yes | ✅ Yes |
| **Mem0 Integration** | ✅ Yes | ✅ Yes |
| **RAG Tools** | ✅ Yes | ✅ Yes |
| **Web Search** | ✅ Yes | ✅ Yes |
| **Image Analysis** | ✅ Yes | ✅ Yes |
| **File Uploads** | ✅ Yes | ⏳ Coming soon |
| **Frontend Actions** | ❌ No | ✅ Yes |
| **Shared State** | ❌ No | ✅ Yes |
| **CopilotKit UI** | ❌ No | ✅ Yes |
| **Generative UI** | ❌ No | ✅ Yes |

## Migration Steps

### Step 1: Understand Current Implementation

Your current code likely looks like this:

```typescript
// Current: Custom endpoint
const response = await fetch('/api/pydantic-agent', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: message,
    user_id: userId,
    request_id: requestId,
    session_id: sessionId,
    files: attachments
  })
});

// Custom streaming format
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { value, done } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n').filter(l => l.trim());

  for (const line of lines) {
    const data = JSON.parse(line);
    if (data.text) {
      appendMessage(data.text);
    }
  }
}
```

### Step 2: Update to AG-UI Format

```typescript
// New: AG-UI endpoint
const response = await fetch('/api/ag-ui', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    type: 'message',
    content: message,
    state: {
      session_id: sessionId,
      message_count: currentMessageCount
    }
  })
});

// AG-UI streaming format (Server-Sent Events)
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

      switch (event.type) {
        case 'text_delta':
          appendMessage(event.data.content);
          break;
        case 'state_update':
          updateState(event.data);
          break;
        case 'completion':
          onComplete();
          break;
        case 'error':
          onError(event.data.message);
          break;
      }
    }
  }
}
```

### Step 3: Update State Management

```typescript
// Before: No shared state
// State was managed entirely client-side

// After: Bidirectional state sync
interface ConversationState {
  session_id?: string;
  conversation_title?: string;
  message_count: number;
  last_updated?: string;
  user_id?: string;
}

const [state, setState] = useState<ConversationState>({
  session_id: null,
  message_count: 0
});

// State updates come from server
function handleStateUpdate(newState: ConversationState) {
  setState(newState);
  // UI automatically reflects state changes
}
```

### Step 4: Add Frontend Actions (Optional)

```typescript
// Define actions the agent can call
const frontendActions = [
  {
    name: 'show_notification',
    description: 'Display a notification to the user',
    parameters: {
      type: 'object',
      properties: {
        message: { type: 'string' },
        severity: { type: 'string', enum: ['info', 'success', 'warning', 'error'] }
      }
    }
  }
];

// Include in request
fetch('/api/ag-ui', {
  body: JSON.stringify({
    type: 'message',
    content: userMessage,
    state: state,
    frontend_actions: frontendActions  // New!
  })
});
```

## Gradual Migration Strategy

### Phase 1: Parallel Testing (Week 1)

- Keep existing frontend unchanged
- Create new AG-UI test page
- Test basic functionality
- Verify state management works
- Test frontend actions

### Phase 2: Feature Parity (Week 2)

- Implement all custom endpoint features in AG-UI version
- Add file upload support when available
- Test thoroughly with real users
- Gather feedback

### Phase 3: Gradual Rollout (Week 3-4)

- Deploy AG-UI version to beta users
- Monitor performance and errors
- Collect user feedback
- Fix any issues

### Phase 4: Full Migration (Week 5)

- Switch all users to AG-UI endpoint
- Keep custom endpoint available as fallback
- Monitor for regressions
- Update documentation

### Phase 5: Deprecation (Optional, Month 3+)

- Announce deprecation timeline for custom endpoint
- Provide ample notice (3-6 months)
- Ensure all clients migrated
- Finally remove custom endpoint

## Code Examples

### Example: Minimal Migration

**Before (Custom)**:
```typescript
async function sendMessage(message: string) {
  const response = await fetch('/api/pydantic-agent', {
    method: 'POST',
    body: JSON.stringify({
      query: message,
      user_id: userId,
      request_id: generateId(),
      session_id: sessionId
    })
  });

  for await (const chunk of parseCustomStream(response)) {
    displayMessage(chunk.text);
  }
}
```

**After (AG-UI)**:
```typescript
async function sendMessage(message: string) {
  const response = await fetch('/api/ag-ui', {
    method: 'POST',
    body: JSON.stringify({
      type: 'message',
      content: message,
      state: { session_id: sessionId, message_count: messages.length }
    })
  });

  for await (const event of parseAGUIStream(response)) {
    if (event.type === 'text_delta') {
      displayMessage(event.data.content);
    }
  }
}
```

### Example: Using CopilotKit

Instead of manual implementation, use CopilotKit:

```typescript
import { CopilotKit, useCopilotChat } from "@copilotkit/react";

function ChatInterface() {
  const { messages, sendMessage } = useCopilotChat();

  return (
    <CopilotKit runtimeUrl="/api/ag-ui">
      <div>
        {messages.map(msg => (
          <div key={msg.id}>{msg.content}</div>
        ))}
        <input onSubmit={(e) => sendMessage(e.target.value)} />
      </div>
    </CopilotKit>
  );
}
```

## Troubleshooting Migration

### Issue: Different Response Format

**Problem**: Code expects custom format, gets AG-UI events

**Solution**: Update parsing logic to handle SSE format (see Step 2)

### Issue: Session IDs Different

**Problem**: Existing session IDs not working

**Solution**: AG-UI uses same database schema. Session IDs are compatible.

### Issue: Missing Features

**Problem**: File uploads not available yet

**Solution**: Keep using custom endpoint for file uploads, or wait for AG-UI support

### Issue: Performance Differences

**Problem**: AG-UI seems slower/faster

**Solution**: Both use same underlying agent. Performance should be similar.

## Testing Checklist

Before going live with AG-UI:

- [ ] Authentication works (JWT token validation)
- [ ] New conversations created correctly
- [ ] Existing conversations load properly
- [ ] Message history displays correctly
- [ ] Streaming works smoothly
- [ ] State updates received and applied
- [ ] Frontend actions work (if using)
- [ ] Error handling works correctly
- [ ] Rate limiting still applies
- [ ] Mem0 memories retrieved
- [ ] RAG tools function properly
- [ ] Web search works
- [ ] Image analysis works
- [ ] Database persistence verified

## Rollback Plan

If issues arise:

1. **Immediate**: Switch frontend back to custom endpoint
2. **Short-term**: Disable AG-UI endpoint via `AGUI_ENABLED=false`
3. **Investigate**: Check logs with `AGUI_DEBUG=true`
4. **Fix**: Address issues in AG-UI implementation
5. **Re-deploy**: Test thoroughly before re-enabling

## Getting Help

- Check [AG-UI Integration Guide](./ag-ui-integration.md)
- Enable debug logging: `AGUI_DEBUG=true`
- Check server logs for errors
- Test with curl to isolate frontend issues
- File issues in repository

## Best Practices

1. **Test Thoroughly**: Don't skip testing phase
2. **Monitor Closely**: Watch logs during rollout
3. **Communicate**: Inform users of changes
4. **Have Fallback**: Keep custom endpoint available
5. **Gather Feedback**: Ask users about their experience

## Conclusion

The AG-UI endpoint provides a path to modern, standardized agent-UI communication while maintaining full backward compatibility. Take your time with migration, test thoroughly, and enjoy the benefits of the AG-UI ecosystem!
