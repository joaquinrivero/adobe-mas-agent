#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting AI Agent Application...${NC}"

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# Check if .env files exist
if [ ! -f "$PROJECT_ROOT/app/server/.env" ]; then
    echo -e "${RED}Warning: No .env file found in app/server/.${NC}"
    echo "Please:"
    echo "  1. cd app/server"
    echo "  2. cp .env.sample .env"
    echo "  3. Edit .env and add your API keys"
    exit 1
fi

if [ ! -f "$PROJECT_ROOT/app/client/.env" ]; then
    echo -e "${RED}Warning: No .env file found in app/client/.${NC}"
    echo "Please:"
    echo "  1. cd app/client"
    echo "  2. cp .env.sample .env"
    echo "  3. Edit .env with your Supabase credentials and backend endpoint"
    exit 1
fi

# Create log files for output
BACKEND_LOG="/tmp/ai_agent_backend.log"
FRONTEND_LOG="/tmp/ai_agent_frontend.log"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"

    # Kill all child processes
    jobs -p | xargs kill 2>/dev/null || true

    # Kill tail processes
    pkill -P $$ 2>/dev/null || true

    # Wait for processes to terminate
    wait 2>/dev/null

    echo -e "${GREEN}Services stopped successfully.${NC}"
    exit 0
}

# Trap EXIT, INT, and TERM signals
trap cleanup EXIT INT TERM

# Start backend with output redirection
echo -e "${GREEN}Starting backend server...${NC}"
cd "$PROJECT_ROOT/app/server"
.venv/bin/uvicorn agent_api:app --reload --port 8001 > >(while IFS= read -r line; do echo -e "${BLUE}[BACKEND]${NC} $line"; done) 2> >(while IFS= read -r line; do echo -e "${YELLOW}[BACKEND]${NC} $line"; done >&2) &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Backend failed to start!${NC}"
    echo -e "${RED}Check the output above for errors.${NC}"
    exit 1
fi

# Start frontend with output redirection
echo -e "${GREEN}Starting frontend server...${NC}"
cd "$PROJECT_ROOT/app/client"
npm run dev > >(while IFS= read -r line; do echo -e "${BLUE}[FRONTEND]${NC} $line"; done) 2> >(while IFS= read -r line; do echo -e "${YELLOW}[FRONTEND]${NC} $line"; done >&2) &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}Frontend failed to start!${NC}"
    echo -e "${RED}Check the output above for errors.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Services started successfully!${NC}"
echo -e "${BLUE}Frontend: http://localhost:8080${NC}"
echo -e "${BLUE}Backend:  http://localhost:8001${NC}"
echo -e "${BLUE}API Docs: http://localhost:8001/docs${NC}"
echo ""
echo -e "${YELLOW}All output from both services will be displayed below:${NC}"
echo -e "${BLUE}[BACKEND]${NC} - Backend server output"
echo -e "${BLUE}[FRONTEND]${NC} - Frontend server output"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Wait for user to press Ctrl+C
wait