"""
Tests for AG-UI type definitions
"""

import pytest
from datetime import datetime
from ag_ui_types import ConversationState, FrontendAction, AGUIRequest, AGUIEvent


class TestConversationState:
    """Tests for ConversationState model"""

    def test_conversation_state_defaults(self):
        """Test ConversationState with default values"""
        state = ConversationState()
        assert state.session_id is None
        assert state.conversation_title is None
        assert state.message_count == 0
        assert state.last_updated is None
        assert state.user_id is None

    def test_conversation_state_with_values(self):
        """Test ConversationState with specific values"""
        state = ConversationState(
            session_id="test-session-123",
            conversation_title="Test Conversation",
            message_count=5,
            last_updated="2025-10-20T23:45:00Z",
            user_id="user-123"
        )
        assert state.session_id == "test-session-123"
        assert state.conversation_title == "Test Conversation"
        assert state.message_count == 5
        assert state.last_updated == "2025-10-20T23:45:00Z"
        assert state.user_id == "user-123"

    def test_conversation_state_serialization(self):
        """Test ConversationState can be serialized to dict"""
        state = ConversationState(
            session_id="test-123",
            message_count=10
        )
        data = state.model_dump()
        assert isinstance(data, dict)
        assert data["session_id"] == "test-123"
        assert data["message_count"] == 10


class TestFrontendAction:
    """Tests for FrontendAction model"""

    def test_frontend_action_required_fields(self):
        """Test FrontendAction requires name and description"""
        action = FrontendAction(
            name="test_action",
            description="A test action"
        )
        assert action.name == "test_action"
        assert action.description == "A test action"
        assert action.parameters == {}

    def test_frontend_action_with_parameters(self):
        """Test FrontendAction with parameter schema"""
        action = FrontendAction(
            name="show_notification",
            description="Show a notification",
            parameters={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "severity": {"type": "string", "enum": ["info", "warning", "error"]}
                },
                "required": ["message"]
            }
        )
        assert action.name == "show_notification"
        assert "properties" in action.parameters
        assert "message" in action.parameters["properties"]

    def test_frontend_action_validation_error(self):
        """Test FrontendAction requires name and description"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            FrontendAction(name="test")  # Missing description


class TestAGUIRequest:
    """Tests for AGUIRequest model"""

    def test_agui_request_minimal(self):
        """Test AGUIRequest with minimal required fields"""
        request = AGUIRequest(type="message")
        assert request.type == "message"
        assert request.content is None
        assert request.state is None
        assert request.frontend_actions is None

    def test_agui_request_with_content_and_state(self):
        """Test AGUIRequest with content and state"""
        state = ConversationState(session_id="test-123")
        request = AGUIRequest(
            type="message",
            content="Hello, agent!",
            state=state
        )
        assert request.type == "message"
        assert request.content == "Hello, agent!"
        assert request.state.session_id == "test-123"

    def test_agui_request_with_frontend_actions(self):
        """Test AGUIRequest with frontend actions"""
        actions = [
            FrontendAction(name="action1", description="First action"),
            FrontendAction(name="action2", description="Second action")
        ]
        request = AGUIRequest(
            type="message",
            frontend_actions=actions
        )
        assert len(request.frontend_actions) == 2
        assert request.frontend_actions[0].name == "action1"


class TestAGUIEvent:
    """Tests for AGUIEvent model"""

    def test_agui_event_creation(self):
        """Test AGUIEvent creation"""
        event = AGUIEvent(
            type="text_delta",
            data={"content": "Hello"}
        )
        assert event.type == "text_delta"
        assert event.data["content"] == "Hello"
        assert event.timestamp is not None

    def test_agui_event_with_custom_timestamp(self):
        """Test AGUIEvent with custom timestamp"""
        timestamp = "2025-10-20T23:45:00Z"
        event = AGUIEvent(
            type="completion",
            data={"session_id": "test-123"},
            timestamp=timestamp
        )
        assert event.timestamp == timestamp

    def test_agui_event_serialization(self):
        """Test AGUIEvent serialization"""
        event = AGUIEvent(
            type="state_update",
            data={"message_count": 5}
        )
        data = event.model_dump()
        assert data["type"] == "state_update"
        assert data["data"]["message_count"] == 5
