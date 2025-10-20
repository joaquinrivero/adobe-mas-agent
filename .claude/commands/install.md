# Install & Prime

## Read
.env.sample (never read .env)
./app/server/.env.sample (never read .env)

## Read and Execute
.claude/commands/prime.md

## Run

### Pre-installation Checks
- Check if `app/server/requirements.txt` has encoding issues (spaces between characters)
- If corrupted, fix by reading the file and rewriting it properly

### Git Setup
- Remove the existing git remote: `git remote remove origin`
- Initialize a new git repository: `git init`

### Environment Files
- Run `cp .env.sample .env`
- Run `cp app/server/.env.sample app/server/.env`
- Run `cp app/client/.env.sample app/client/.env`
- Run `./scripts/copy_dot_env.sh` to copy the .env file from the tac-2 directory. Note, the tac-2 codebase may not exist, proceed either way.

### Backend Installation (Python)
- Create virtual environment: `cd app/server && uv venv`
- Install dependencies: `uv pip install -r requirements.txt`
- Verify installation: Check that uvicorn is installed in `.venv/bin/`

### Frontend Installation (Node.js)
- Install dependencies: `cd app/client && npm install`
- Verify installation: Check that `node_modules` directory exists

### Script Fixes
- Verify `scripts/start.sh` uses `.venv/bin/uvicorn` (not just `uvicorn`)
- If not, update line 54 to use `.venv/bin/uvicorn agent_api:app --reload --port 8001`

### Database Setup
- Read and apply all SQL scripts using Supabase MCP in this order:
  1. Read `app/server/sql/1-user_profiles_requests.sql` and apply with `mcp__supabase__apply_migration` (name: "user_profiles_requests")
  2. Read `app/server/sql/2-user_profiles_requests_rls.sql` and apply with `mcp__supabase__apply_migration` (name: "user_profiles_requests_rls")
  3. Read `app/server/sql/3-conversations_messages.sql` and apply with `mcp__supabase__apply_migration` (name: "conversations_messages")
  4. Read `app/server/sql/4-conversations_messages_rls.sql` and apply with `mcp__supabase__apply_migration` (name: "conversations_messages_rls")
- After all migrations complete, use `mcp__supabase__list_tables` to verify tables were created
- Use `mcp__supabase__list_migrations` to verify all migrations were applied

## Report
- Output the work you've just done in a concise bullet point list.
- Instruct the user to fill out the environment files:
  - Root level `./.env` based on `.env.sample` (for ADWs)
  - `./app/server/.env` based on `./app/server/.env.sample`
    - **IMPORTANT**: If DATABASE_URL password contains special characters like `@`, URL-encode them (e.g., `@` → `%40`)
    - Example: `postgresql://user:%40password@host:5432/db` for password "@password"
  - `./app/client/.env` based on `./app/client/.env.sample`
    - Make sure not to swap VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY values
- Report on database setup:
  - List all migrations that were successfully applied
  - List all tables that were created
  - If any migrations failed, provide clear instructions for the user to manually apply them in Supabase SQL Editor
- Mention: 'To setup your AI Agent, be sure to update the remote repo url and push to a new repo so you have access to git issues and git prs:
  ```
  git remote add origin <your-new-repo-url>
  git push -u origin main
  ```'
- Remind user to start the app with: `./scripts/start.sh`
