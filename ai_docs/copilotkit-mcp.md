# CopilotKit MCP Integration Documentation

## Overview

CopilotKit provides a Model Context Protocol (MCP) integration that enables AI agents to connect to CopilotKit applications. This includes two key components:

1. **Vibe Coding Server** - An MCP server built with Tadata that provides structured access to CopilotKit documentation and code examples
2. **CopilotKit MCP Client** - A client that enables runtime tool discovery and LLM integration with MCP servers

## What is Vibe Coding Server?

The Vibe Coding Server is an MCP server designed to make coding copilots code reliably with CopilotKit. It provides:

- **Structured Access**: Official CopilotKit docs + real code examples from repositories
- **Contextual Retrieval**: Automatically retrieves only pertinent code snippets
- **Efficiency**: Claims 66% faster integrations with fewer retries
- **Reduced Hallucinations**: Eliminates repetitive prompt instructions and API hallucinations

### Key Features

1. **Documentation Access**: Gives coding agents structured access to CopilotKit documentation
2. **Code Examples**: Provides actual code examples from CopilotKit repositories
3. **Context-Aware**: Delivers contextually relevant snippets on demand
4. **Token Efficiency**: Reduces wasted tokens by providing precise context

## What is CopilotKit MCP Client?

The CopilotKit MCP Client enables integration between LLMs and MCP servers with features including:

- **Runtime Tool Discovery**: Dynamically discovers available MCP tools
- **Tool Invocation**: Enables LLMs to invoke MCP tools alongside frontend/backend actions
- **Live Context Streaming**: Streams live context into conversations
- **UI Integration**: Provides `'McpToolCall'` for UI integration

## Quick Start

The fastest way to get started is using the scaffolding tool:

```bash
npx create-copilotkit-mcp-app
```

This command creates a preconfigured application with:
- Pre-built hooks
- UI components
- Built-in integrations (LangChain, Composio, etc.)

## Integration Paths

CopilotKit MCP supports multiple integration approaches:

### 1. Direct-to-LLM Integration

Use the MCP server to connect your LLM directly to CopilotKit.

**Documentation**: `/direct-to-llm/guides/vibe-coding-mcp`

**Use Case**: When you want to connect language models directly to CopilotKit without using an agent framework.

### 2. LangGraph Integration

Integrate MCP with LangGraph-based agentic workflows.

**Documentation**: `/langgraph/vibe-coding-mcp`

**Use Case**: For agentic workflow implementations using LangGraph.

### 3. Mastra Integration

Connect MCP to Mastra agent-based applications.

**Documentation**: `/mastra/vibe-coding-mcp`

**Use Case**: For agent-based applications built with Mastra.

## Problem Statement

Most coding copilots fail because they lack sufficient context, leading to:
- Hallucinated APIs
- Wasted tokens
- Repetitive prompting
- Slower development cycles

The Vibe Coding Server solves this by providing:
- Relevant context on demand
- Accurate code examples
- Structured documentation access
- Reduced token usage

## Architecture

The CopilotKit MCP architecture follows this pattern:

```
LLM/Agent
    ↓
CopilotKit MCP Client
    ↓
MCP Protocol
    ↓
Vibe Coding Server
    ↓
Documentation + Code Examples
```

### Components

1. **LLM/Agent**: Your AI model or agent framework (Claude, GPT-4, etc.)
2. **MCP Client**: Handles tool discovery and invocation
3. **MCP Protocol**: Standard protocol for agent-to-tool communication
4. **Vibe Coding Server**: Provides structured access to CopilotKit resources
5. **Resources**: Official docs and code examples

## Use with Claude Code

When using with Claude Code (Anthropic's official CLI):

1. **MCP Integration**: Claude Code supports MCP servers natively
2. **Tool Access**: Can invoke Vibe Coding Server tools for CopilotKit context
3. **Documentation Retrieval**: Access CopilotKit docs during development
4. **Code Examples**: Get relevant code snippets from CopilotKit repos

### Configuration

To use with Claude Code, configure the MCP server in your Claude Code settings:

```json
{
  "mcpServers": {
    "copilotkit-vibe": {
      "command": "npx",
      "args": ["@copilotkit/vibe-coding-server"]
    }
  }
}
```

## Benefits

### For Developers

- **Faster Integration**: 66% faster CopilotKit integrations
- **Fewer Retries**: Reduced hallucinations and errors
- **Better Context**: Contextually relevant code snippets
- **Token Efficiency**: Less wasted tokens on repetitive instructions

### For AI Agents

- **Reliable Coding**: More accurate CopilotKit implementations
- **Structured Access**: Well-organized documentation and examples
- **Runtime Discovery**: Dynamic tool availability
- **Seamless Integration**: Works alongside other MCP servers

## Features

### Vibe Coding Server Features

1. **Documentation Search**: Query CopilotKit documentation
2. **Code Example Retrieval**: Get real code examples from repos
3. **Context Filtering**: Returns only pertinent snippets
4. **Multiple Frameworks**: Supports various agent frameworks

### MCP Client Features

1. **Tool Discovery**: Automatically discovers available tools
2. **Tool Invocation**: Invokes MCP tools from LLMs
3. **Context Streaming**: Streams live context
4. **UI Components**: Built-in UI integration via `McpToolCall`

## Integration with Other Tools

CopilotKit MCP can work alongside:

- **LangChain**: For chain-based LLM applications
- **Composio**: For tool composition
- **AG-UI**: For agent-to-user interaction protocol
- **Other MCP Servers**: Can be used with multiple MCP servers simultaneously

## Resources

### Documentation

- **Official Docs**: https://docs.copilotkit.ai/vibe-coding-mcp
- **Direct-to-LLM Guide**: https://docs.copilotkit.ai/direct-to-llm/guides/vibe-coding-mcp
- **LangGraph Guide**: https://docs.copilotkit.ai/langgraph/vibe-coding-mcp
- **Mastra Guide**: https://docs.copilotkit.ai/mastra/vibe-coding-mcp

### Blog & Announcements

- **Launch Announcement**: https://webflow.copilotkit.ai/blog/announcing-copilotkit-mcp-client-vibe-coding-server

### Getting Started

```bash
# Quick scaffolding
npx create-copilotkit-mcp-app

# Install MCP client
npm install @copilotkit/mcp-client

# Install Vibe Coding Server
npm install @copilotkit/vibe-coding-server
```

## Best Practices

1. **Use Scaffolding**: Start with `create-copilotkit-mcp-app` for best setup
2. **Combine with AG-UI**: Use both MCP (tools) and AG-UI (user interaction)
3. **Multiple Servers**: Leverage multiple MCP servers for different contexts
4. **Token Optimization**: Let the Vibe Coding Server handle context retrieval
5. **Framework Choice**: Pick the integration path (Direct/LangGraph/Mastra) that fits your stack

## Common Use Cases

### 1. Building CopilotKit Applications

Use Vibe Coding Server to get accurate documentation and examples while building CopilotKit apps.

### 2. Agent Development

Integrate with LangGraph or Mastra agents to enable them to access CopilotKit context.

### 3. Claude Code Development

Use with Claude Code to get CopilotKit assistance during development sessions.

### 4. Multi-Agent Systems

Combine with other MCP servers to build comprehensive agent systems.

## Technical Specifications

### Protocol Support

- **MCP Version**: Latest Model Context Protocol specification
- **Transport**: HTTP, SSE, WebSockets (depending on implementation)
- **Authentication**: Supports API key authentication

### Performance

- **Speed Improvement**: 66% faster integrations (claimed)
- **Retry Reduction**: Fewer retries due to better context
- **Token Efficiency**: Reduced token usage through precise context

### Compatibility

- **Frameworks**: LangGraph, Mastra, Direct LLM
- **Languages**: JavaScript/TypeScript (primary), Python (via MCP client)
- **Platforms**: Node.js, browser, Edge runtime

## Troubleshooting

### Common Issues

1. **Server Not Found**: Ensure Vibe Coding Server is installed
2. **Tool Discovery Fails**: Check MCP client configuration
3. **Context Not Relevant**: Verify query formulation
4. **Authentication Errors**: Check API keys and permissions

### Debug Tips

- Enable MCP debug logging
- Verify server connectivity
- Check tool registration
- Review context retrieval queries

## Summary

CopilotKit MCP provides a powerful integration between AI agents and CopilotKit through:

1. **Vibe Coding Server**: Structured access to docs and code
2. **MCP Client**: Runtime tool discovery and invocation
3. **Multiple Integration Paths**: Support for various frameworks
4. **Claude Code Support**: Native MCP integration

This enables developers to build reliable, context-aware AI agents that can effectively work with CopilotKit applications while reducing hallucinations and improving development speed.
