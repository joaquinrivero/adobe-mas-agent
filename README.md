# AI Agent Application

A production-ready AI agent interface combining a modern React frontend with a FastAPI backend, featuring real-time streaming responses, conversation history, and Pydantic AI integration.

## Features

- 🤖 AI Agent with Pydantic AI framework
- 💬 Real-time streaming responses
- 📜 Conversation history management
- 🎨 Modern UI with Shadcn components
- 🔐 Supabase integration for data persistence
- 🧠 Memory management with Mem0 AI

## Prerequisites

- **Python 3.11+** (Validated with Python 3.13.1)
- **Node.js 18+** (Validated with Node.js 22.9.0)
- **uv** - Modern Python package manager (recommended)
- **Supabase account** (local or managed)
- **OpenAI API key** and/or **Anthropic API key**
- **GitHub CLI (gh)** - For AI Developer Workflows (optional)
- **Claude Code CLI** - For ADW integration (optional)

## Setup

### 1. Install Dependencies

#### Backend (Python)
```bash
cd app/server

# Create virtual environment with uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
.venv/bin/pip install -r requirements.txt

# Or use pip with virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Frontend (Node.js)
```bash
cd app/client
npm install
```

### 2. Environment Configuration

⚠️ **Important**: Carefully configure all three `.env` files with the correct values.

#### Root Environment (for ADWs)
```bash
cp .env.sample .env
# Required:
# - CLAUDE_CODE_PATH: Path to Claude Code CLI (defaults to 'claude')

# Optional:
# - E2B_API_KEY: For agent sandbox environments
# - GITHUB_PAT: GitHub Personal Access Token (if not using 'gh auth login')
# - CLOUDFLARED_TUNNEL_TOKEN: For webhook exposure
```

#### Backend Environment
```bash
cd app/server
cp .env.sample .env
# Edit .env and configure:

# LLM Configuration (Required)
LLM_PROVIDER=openai              # openai, anthropic, openrouter, or ollama
LLM_API_KEY=your-api-key-here    # Your LLM provider API key
LLM_CHOICE=gpt-4o-mini           # Model to use

# Embedding Configuration (Required for RAG)
EMBEDDING_PROVIDER=openai
EMBEDDING_API_KEY=your-api-key-here
EMBEDDING_MODEL_CHOICE=text-embedding-3-small  # NOT an API key!

# Supabase Configuration (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key-here
DATABASE_URL=postgresql://...    # Supabase Postgres connection string

# Optional
BRAVE_API_KEY=                   # For web search tool
SEARXNG_BASE_URL=                # Alternative to Brave
```

#### Frontend Environment
```bash
cd app/client
cp .env.sample .env
# Edit .env and configure:

# Supabase Configuration
VITE_SUPABASE_URL=https://your-project.supabase.co  # NOT the anon key!
VITE_SUPABASE_ANON_KEY=your-anon-key-here          # NOT the URL!

# Backend API
VITE_AGENT_ENDPOINT=http://localhost:8001/api/pydantic-agent

# Streaming
VITE_ENABLE_STREAMING=true
```

**Common Mistakes to Avoid:**
- ❌ Using API keys in `EMBEDDING_MODEL_CHOICE` (should be model name)
- ❌ Swapping `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` values
- ❌ Leaving `EMBEDDING_API_KEY` empty when using OpenAI embeddings
- ❌ Using the wrong Supabase key (service key vs anon key)

## Quick Start

Use the provided script to start both services:

```bash
./scripts/start.sh
```

Press `Ctrl+C` to stop both services.

The script will:
- Check that `.env` files exist in both `app/server/` and `app/client/`
- Start the backend on http://localhost:8001
- Start the frontend on http://localhost:5173
- Handle graceful shutdown when you exit

## Manual Start (Alternative)

### Backend
```bash
cd app/server
# .env is loaded automatically by python-dotenv
uvicorn agent_api:app --reload --port 8001
```

### Frontend
```bash
cd app/client
npm run dev
```

## Usage

1. **Start a Conversation**: Open the app and start chatting with the AI agent
2. **Stream Responses**: Watch as the AI agent responds in real-time
3. **View History**: Access your conversation history from the sidebar
4. **Manage Sessions**: Create new conversations or continue previous ones
5. **Settings**: Configure AI model preferences and other options

## Development

### Backend Commands
```bash
cd app/server

# Activate virtual environment first
source .venv/bin/activate

# Start server with hot reload
uvicorn agent_api:app --reload --port 8001

# Run tests
pytest

# Add package
pip install <package>
pip freeze > requirements.txt  # Update requirements
```

### Frontend Commands
```bash
cd app/client
npm run dev                 # Start dev server
npm run build              # Build for production
npm run preview            # Preview production build
npm run lint               # Run linter
```

## Project Structure

```
.
├── app/                    # Main application
│   ├── client/             # React + TypeScript frontend with Shadcn UI
│   │   ├── src/
│   │   │   ├── components/ # UI components
│   │   │   ├── types/      # TypeScript definitions
│   │   │   └── App.tsx     # Main app component
│   │   ├── .env.sample     # Environment template
│   │   └── package.json
│   │
│   └── server/             # FastAPI backend with Pydantic AI
│       ├── agent_api.py    # Main API endpoints
│       ├── agent.py        # Pydantic AI agent definition
│       ├── tools.py        # Agent tools (RAG, web search, SQL, etc.)
│       ├── clients.py      # Client setup (Supabase, OpenAI, Mem0)
│       ├── prompt.py       # Agent system prompt
│       ├── db_utils.py     # Database utilities
│       ├── sql/            # Database schema scripts
│       ├── .env.sample     # Environment template
│       └── requirements.txt
│
├── adws/                   # AI Developer Workflows
├── scripts/                # Utility scripts (start.sh, etc.)
├── specs/                  # Feature specifications
└── ai_docs/                # AI/LLM documentation
```

## ADWs

- `uv run adws/health_check.py` - Basic health check ADW
- `uv run adws/trigger_webhook.py` - React to incoming webhook trigger (be sure to setup a tunnel and your github webhook)
- `uv run adws/trigger_cron.py` - Simple cron job trigger that checks github issues every N seconds
- `uv run adws/adw_plan_build.py` - Plan -> Build AI Developer Workflow (ADW)

## API Endpoints

### Agent Endpoints

- `POST /api/pydantic-agent` - Main agent endpoint with custom streaming (existing)
- `POST /api/ag-ui` - AG-UI protocol endpoint for CopilotKit integration (new)

### Conversation Endpoints

- `GET /api/conversations/{session_id}` - Get conversation history
- `POST /api/conversations` - Create new conversation
- `DELETE /api/pydantic-agent/conversations/{session_id}` - Archive conversation

### System Endpoints

- `GET /health` - Health check endpoint

For full API documentation, visit `http://localhost:8001/docs` when the server is running.

## AG-UI Protocol Support

This application now supports the **AG-UI (Agent User Interaction)** protocol for standardized communication with CopilotKit and other AG-UI-compatible frontends.

### Why AG-UI?

AG-UI provides:
- ✅ **CopilotKit Compatibility**: Use CopilotChat, CopilotSidebar, and other UI components
- ✅ **Frontend Actions**: Let agents call UI-defined functions
- ✅ **Shared State**: Bidirectional state synchronization
- ✅ **Standard Protocol**: Interoperability with AG-UI ecosystem

### Quick Start with AG-UI

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

### AG-UI Configuration

Configure AG-UI features in `app/server/.env`:

```env
# AG-UI Protocol Configuration
AGUI_ENABLED=true                      # Enable/disable AG-UI endpoint
AGUI_DEBUG=false                       # Enable debug logging
AGUI_ALLOW_FRONTEND_ACTIONS=true       # Allow frontend actions
AGUI_ENDPOINT_PATH=/api/ag-ui          # Endpoint path
```

### Documentation

- **[AG-UI Integration Guide](./ai_docs/ag-ui-integration.md)** - Complete guide for using the AG-UI endpoint
- **[Migration Guide](./ai_docs/migration-guide.md)** - Migrate from custom endpoint to AG-UI

### Backward Compatibility

The existing `/api/pydantic-agent` endpoint remains fully functional. Both endpoints:
- Use the same authentication (Supabase JWT)
- Share the same database and conversation history
- Access the same agent tools and capabilities
- Can be used simultaneously

Choose the endpoint that best fits your use case!

### 3. Database Setup

The application requires Supabase for data persistence. Run the SQL scripts in order:

```bash
# In your Supabase project SQL editor, run these scripts in order:
# 1. app/server/sql/1-user_profiles_requests.sql
# 2. app/server/sql/2-user_profiles_requests_rls.sql
# 3. app/server/sql/3-conversations_messages.sql
# 4. app/server/sql/4-conversations_messages_rls.sql
```

These scripts create:
- User profiles and request tracking tables
- Row Level Security (RLS) policies
- Conversations and messages tables with proper indexes

## Important Notes

### Pydantic AI Agent

The AI agent is integrated directly into the backend:
- Agent definition: `app/server/agent.py`
- Agent tools: `app/server/tools.py`
- System prompt: `app/server/prompt.py`
- Client setup: `app/server/clients.py`
- Configure the agent by editing `app/server/.env`

### Database Setup

The application uses Supabase for data persistence. SQL scripts for setting up the database schema are located in `app/server/sql/`. Make sure to run these scripts in your Supabase project before starting the application.

### Security Features

- CORS configured for development (update for production)
- Environment variables for sensitive credentials
- Supabase Row Level Security (RLS) for data protection
- API key validation for agent endpoints

## Troubleshooting

### Backend Issues

**Backend won't start:**
```bash
# Check Python version (requires 3.11+, validated with 3.13.1)
python3 --version

# Verify virtual environment is activated
source app/server/.venv/bin/activate

# Check if dependencies are installed
pip list | grep -E "(fastapi|pydantic-ai|supabase)"

# Test imports
cd app/server
python3 -c "import fastapi, pydantic_ai, supabase, mem0; print('OK')"

# Check .env file exists
ls -la app/server/.env
```

**Common Backend Errors:**
- `ModuleNotFoundError`: Dependencies not installed - run `pip install -r requirements.txt`
- `EMBEDDING_MODEL_CHOICE error`: Check you used a model name (e.g., `text-embedding-3-small`), NOT an API key
- `Supabase connection error`: Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are correct
- `Database URL error`: Check `DATABASE_URL` format: `postgresql://user:password@host:port/database`

### Frontend Issues

**Frontend won't start:**
```bash
# Check Node version (requires 18+, validated with 22.9.0)
node --version

# Clear and reinstall
cd app/client
rm -rf node_modules package-lock.json
npm install

# Check .env file exists and is correct
cat app/client/.env
```

**Common Frontend Errors:**
- `VITE_SUPABASE_URL is undefined`: Check `.env` file has `VITE_SUPABASE_URL=https://...` (not the anon key!)
- `VITE_SUPABASE_ANON_KEY is undefined`: Check `.env` has the JWT token, not the URL
- `Cannot connect to backend`: Verify backend is running on port 8001 and `VITE_AGENT_ENDPOINT` is correct
- TypeScript errors: Run `npm run build` to see detailed compilation errors

### CORS Issues

**CORS errors in browser console:**
- Ensure backend is running on port 8001
- Check CORS settings in `app/server/agent_api.py`
- Verify frontend is making requests to `http://localhost:8001`
- Clear browser cache and restart both services

### Database Issues

**Database connection problems:**
```bash
# Test Supabase connection
curl -H "apikey: YOUR_ANON_KEY" https://your-project.supabase.co/rest/v1/

# Verify SQL scripts were run
# Check in Supabase SQL Editor > History
```

**Common Database Errors:**
- `relation "conversations" does not exist`: Run SQL scripts in `app/server/sql/` in order (1-4)
- `RLS policy violation`: Ensure RLS policies are created (scripts 2 and 4)
- Connection timeout: Check Supabase project status and firewall settings

### Environment Variable Issues

Run the validation script to check your setup:
```bash
# Check all environment variables and system requirements
uv run adws/health_check.py
```

**Common .env mistakes:**
- Swapped values between `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`
- Used API key in `EMBEDDING_MODEL_CHOICE` instead of model name
- Empty `EMBEDDING_API_KEY` when using OpenAI provider
- Wrong Supabase key type (service vs anon) in wrong file

## Validation Status

✅ **Application Validated: January 2025**

The application has been fully validated and tested:

- ✅ All environment files configured correctly
- ✅ Python 3.13.1 confirmed working (>= 3.11 required)
- ✅ Node.js 22.9.0 confirmed working (>= 18 required)
- ✅ Virtual environment setup tested with `uv`
- ✅ Claude Code CLI integration verified
- ✅ GitHub CLI integration verified
- ✅ All scripts and commands validated
- ✅ Requirements.txt encoding fixed
- ✅ Common configuration pitfalls documented

**Recent Fixes Applied:**
- Fixed corrupted `requirements.txt` (encoding issues)
- Corrected frontend `.env` Supabase credentials (values were swapped)
- Corrected backend `.env` embedding configuration
- Updated `scripts/stop_apps.sh` to reference correct application name
- Documented all common environment configuration mistakes

**System Verification:**
```bash
# Run the health check to verify your setup
uv run adws/health_check.py

# Check environment files
ls -la .env app/server/.env app/client/.env

# Verify Python/Node versions
python3 --version  # Should be >= 3.11
node --version     # Should be >= 18
```