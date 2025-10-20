"""
AG-UI Protocol Request Handlers

This module implements AG-UI (Agent User Interaction) protocol support for
Pydantic AI agents, enabling standardized communication with CopilotKit and
other AG-UI-compatible frontends.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import Request, HTTPException
from supabase import Client
from openai import AsyncOpenAI
from httpx import AsyncClient

from pydantic_ai import Agent
from ag_ui_types import ConversationState, FrontendAction, AGUIRequest
from agent import AgentStateDeps, agui_agent
from db_utils import (
    fetch_conversation_history,
    create_conversation,
    generate_session_id,
    generate_conversation_title,
    store_message
)
from clients import get_mem0_client_async

logger = logging.getLogger(__name__)


async def initialize_conversation_state(
    supabase: Client,
    session_id: Optional[str],
    user_id: str
) -> ConversationState:
    """
    Initialize AG-UI conversation state from database.

    Args:
        supabase: Supabase client
        session_id: Optional conversation session ID
        user_id: User ID from authentication

    Returns:
        ConversationState with current values from database or defaults
    """
    state = ConversationState(
        session_id=session_id,
        user_id=user_id,
        message_count=0,
        conversation_title=None,
        last_updated=datetime.utcnow().isoformat()
    )

    if session_id:
        try:
            # Fetch conversation history to get metadata
            history = await fetch_conversation_history(supabase, session_id)
            state.message_count = len(history)

            # Get conversation title from database
            result = supabase.table("conversations").select("title").eq("id", session_id).execute()
            if result.data and len(result.data) > 0:
                state.conversation_title = result.data[0].get("title")

            logger.info(f"Loaded state for session {session_id}: {state.message_count} messages")
        except Exception as e:
            logger.warning(f"Failed to load conversation state: {e}")
            # Continue with default state

    return state


async def update_conversation_state(
    supabase: Client,
    state: ConversationState
) -> None:
    """
    Sync AG-UI state changes back to database.

    Args:
        supabase: Supabase client
        state: Current conversation state
    """
    if not state.session_id:
        return

    try:
        # Update conversation metadata
        update_data = {
            "updated_at": datetime.utcnow().isoformat()
        }

        if state.conversation_title:
            update_data["title"] = state.conversation_title

        supabase.table("conversations").update(update_data).eq("id", state.session_id).execute()
        logger.info(f"Updated state for session {state.session_id}")
    except Exception as e:
        logger.error(f"Failed to update conversation state: {e}")


def extract_frontend_actions(request_data: Dict[str, Any]) -> List[FrontendAction]:
    """
    Extract and validate frontend actions from AG-UI request.

    Frontend actions are tools defined in the UI that the agent can call.

    Args:
        request_data: AG-UI request data

    Returns:
        List of validated FrontendAction objects
    """
    frontend_actions = []
    actions_data = request_data.get("frontend_actions", [])

    if not os.getenv("AGUI_ALLOW_FRONTEND_ACTIONS", "true").lower() == "true":
        logger.info("Frontend actions disabled via AGUI_ALLOW_FRONTEND_ACTIONS")
        return frontend_actions

    for action_data in actions_data:
        try:
            action = FrontendAction(**action_data)
            frontend_actions.append(action)
            logger.info(f"Registered frontend action: {action.name}")
        except Exception as e:
            logger.warning(f"Invalid frontend action: {e}")
            continue

    return frontend_actions


async def handle_ag_ui_agent_request(
    request: Request,
    agent: Agent,
    supabase: Client,
    embedding_client: AsyncOpenAI,
    http_client: AsyncClient,
    user_id: str,
    brave_api_key: Optional[str] = None,
    searxng_base_url: Optional[str] = None
):
    """
    Handle AG-UI protocol requests using Pydantic AI's handle_ag_ui_request.

    This is the main entry point for AG-UI requests from CopilotKit or other
    AG-UI-compatible frontends.

    Args:
        request: FastAPI request object
        agent: Pydantic AI agent instance (should use AgentStateDeps)
        supabase: Supabase client
        embedding_client: OpenAI client for embeddings
        http_client: HTTP client for external requests
        user_id: Authenticated user ID
        brave_api_key: Optional Brave API key for web search
        searxng_base_url: Optional SearXNG URL for web search

    Returns:
        AG-UI protocol streaming response
    """
    debug_enabled = os.getenv("AGUI_DEBUG", "false").lower() == "true"

    try:
        # Parse AG-UI request body
        request_body = await request.json()

        if debug_enabled:
            logger.info(f"AG-UI Request: {request_body}")

        # Extract conversation state
        state_data = request_body.get("state", {})
        session_id = state_data.get("session_id")

        # Initialize or load conversation state
        state = await initialize_conversation_state(supabase, session_id, user_id)

        # Create new session if needed
        if not session_id:
            session_id = generate_session_id()
            state.session_id = session_id
            await create_conversation(supabase, session_id, user_id)
            logger.info(f"Created new conversation: {session_id}")

        # Extract frontend actions
        frontend_actions = extract_frontend_actions(request_body)

        if debug_enabled and frontend_actions:
            logger.info(f"Frontend Actions: {[a.name for a in frontend_actions]}")

        # Get Mem0 memories for user
        memories = ""
        try:
            mem0_client = await get_mem0_client_async()
            if mem0_client:
                memories_list = mem0_client.search(query=request_body.get("content", ""), user_id=user_id)
                memories = "\n".join([m["memory"] for m in memories_list]) if memories_list else ""
        except Exception as e:
            logger.warning(f"Failed to retrieve memories: {e}")

        # Create agent dependencies with state
        deps = AgentStateDeps(
            supabase=supabase,
            embedding_client=embedding_client,
            http_client=http_client,
            brave_api_key=brave_api_key,
            searxng_base_url=searxng_base_url,
            memories=memories,
            state=state
        )

        # Get conversation history
        history = []
        if session_id:
            try:
                history = await fetch_conversation_history(supabase, session_id)
            except Exception as e:
                logger.warning(f"Failed to load history: {e}")

        # Store user message
        user_message = request_body.get("content", "")
        if user_message:
            await store_message(
                supabase,
                session_id,
                "user",
                user_message,
                user_id=user_id
            )

        # Use Pydantic AI's handle_ag_ui_request for protocol handling
        # Note: This is a simplified implementation. The actual AG-UI protocol
        # implementation would use agent.handle_ag_ui_request() when available.
        # For now, we'll use regular streaming and format as AG-UI events.

        async def ag_ui_stream():
            """Generate AG-UI protocol events from agent response"""
            try:
                # Run agent with dependencies
                result = agent.run(
                    user_message,
                    deps=deps,
                    message_history=history
                )

                # Stream response as AG-UI events
                assistant_message = ""
                async for event in result.stream():
                    if hasattr(event, 'content'):
                        chunk = event.content
                        assistant_message += chunk

                        # Format as AG-UI text delta event
                        ag_ui_event = {
                            "type": "text_delta",
                            "data": {"content": chunk},
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        yield f"data: {json.dumps(ag_ui_event)}\n\n"

                # Store assistant message
                await store_message(
                    supabase,
                    session_id,
                    "assistant",
                    assistant_message
                )

                # Update state
                state.message_count += 2  # User + assistant
                state.last_updated = datetime.utcnow().isoformat()
                await update_conversation_state(supabase, state)

                # Generate title if first message
                if state.message_count == 2 and not state.conversation_title:
                    try:
                        from agent_api import title_agent
                        title_result = await title_agent.run(
                            f"Generate a short, descriptive title (max 6 words) for a conversation that starts with: '{user_message}'"
                        )
                        title = title_result.data.strip()
                        state.conversation_title = title
                        supabase.table("conversations").update({"title": title}).eq("id", session_id).execute()
                    except Exception as e:
                        logger.warning(f"Failed to generate title: {e}")

                # Send final state update event
                final_event = {
                    "type": "state_update",
                    "data": state.model_dump(),
                    "timestamp": datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(final_event)}\n\n"

                # Send completion event
                completion_event = {
                    "type": "completion",
                    "data": {"session_id": session_id},
                    "timestamp": datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(completion_event)}\n\n"

            except Exception as e:
                logger.error(f"AG-UI streaming error: {e}")
                error_event = {
                    "type": "error",
                    "data": {"message": str(e)},
                    "timestamp": datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(error_event)}\n\n"

        from fastapi.responses import StreamingResponse
        import json

        return StreamingResponse(
            ag_ui_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        logger.error(f"AG-UI request error: {e}")
        raise HTTPException(status_code=500, detail=f"AG-UI request failed: {str(e)}")
