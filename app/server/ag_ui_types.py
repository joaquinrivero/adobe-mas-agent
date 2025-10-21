"""
AG-UI Protocol Type Definitions

This module defines Pydantic models for AG-UI (Agent User Interaction) protocol
support, including shared state and frontend action definitions.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ConversationState(BaseModel):
    """
    Shared state between frontend and agent.

    This state is synchronized bidirectionally - changes from the frontend
    are reflected to the agent, and vice versa. Used by AG-UI protocol
    to maintain consistent state across the user interface and backend.
    """
    session_id: Optional[str] = Field(
        default=None,
        description="Current conversation session ID from database"
    )
    conversation_title: Optional[str] = Field(
        default=None,
        description="Title of the conversation"
    )
    message_count: int = Field(
        default=0,
        description="Number of messages in conversation"
    )
    last_updated: Optional[str] = Field(
        default=None,
        description="Last update timestamp (ISO format)"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="User ID from authentication"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "conversation_title": "Discussion about AG-UI implementation",
                "message_count": 5,
                "last_updated": "2025-10-20T23:45:00Z",
                "user_id": "user-123"
            }
        }


class FrontendAction(BaseModel):
    """
    Definition of a frontend action that the agent can call.

    Frontend actions are tools defined in the UI (not the backend) that
    the agent can invoke. Examples include showing notifications, navigating
    to different pages, or triggering UI-specific functionality.
    """
    name: str = Field(
        ...,
        description="Action name (must be unique within the session)"
    )
    description: str = Field(
        ...,
        description="Human-readable description of what this action does"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON Schema for action parameters"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "name": "show_notification",
                "description": "Display a notification to the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The notification message"
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["info", "success", "warning", "error"],
                            "description": "Notification severity level"
                        }
                    },
                    "required": ["message"]
                }
            }
        }


class AGUIRequest(BaseModel):
    """
    AG-UI protocol request structure.

    This represents the expected format of incoming AG-UI requests from
    CopilotKit or other AG-UI-compatible frontends.
    """
    type: str = Field(
        ...,
        description="Request type (e.g., 'message', 'action_result')"
    )
    content: Optional[str] = Field(
        default=None,
        description="Message content for 'message' type requests"
    )
    state: Optional[ConversationState] = Field(
        default=None,
        description="Current conversation state from frontend"
    )
    frontend_actions: Optional[List[FrontendAction]] = Field(
        default=None,
        description="List of frontend actions available for the agent to call"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional request metadata"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "type": "message",
                "content": "Hello, can you help me with my project?",
                "state": {
                    "session_id": None,
                    "conversation_title": None,
                    "message_count": 0
                },
                "frontend_actions": [
                    {
                        "name": "navigate",
                        "description": "Navigate to a different page",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        }


class AGUIEvent(BaseModel):
    """
    AG-UI protocol event structure.

    Events are streamed from the agent to the frontend. Different event types
    include text deltas, tool calls, state updates, etc.
    """
    type: str = Field(
        ...,
        description="Event type (e.g., 'text_delta', 'tool_call', 'state_update')"
    )
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data payload"
    )
    timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Event timestamp (ISO format)"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "type": "text_delta",
                "data": {
                    "content": "Here's what I found..."
                },
                "timestamp": "2025-10-20T23:45:00Z"
            }
        }
