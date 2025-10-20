# Feature: Remove Previous Chat

## Feature Description
This feature allows users to delete individual conversations from their chat history through the user interface. Users will be able to remove unwanted or outdated conversations directly from the sidebar, providing better conversation management and privacy control. The deletion will be a soft delete by setting the `is_archived` flag to prevent accidental data loss while keeping the UI clean.

## User Story
As a user of the AI chat application
I want to remove previous chat conversations from my sidebar
So that I can manage my conversation history, remove outdated or unwanted chats, and keep my interface organized

## Problem Statement
Currently, users cannot remove conversations from their chat history in the UI. As users accumulate more conversations over time, the sidebar becomes cluttered with old or irrelevant chats that they may want to remove. Without a delete functionality, users have no way to manage their conversation history, leading to:
- Cluttered sidebar with too many conversations
- Difficulty finding recent or important conversations
- Privacy concerns with sensitive conversations that can't be removed
- Poor user experience due to lack of conversation management

## Solution Statement
Implement a soft-delete feature that allows users to archive conversations from the sidebar. When a user deletes a conversation:
1. The conversation will be marked as archived (`is_archived = true`) in the database
2. The conversation will be immediately removed from the sidebar view
3. Messages associated with the conversation will remain in the database but won't be displayed
4. If the deleted conversation was currently selected, the UI will switch to a "new chat" state
5. The operation will be optimistic with rollback on error for better UX

This approach balances user control with data preservation, allowing for potential future features like "restore archived conversations" while providing immediate feedback to users.

## Relevant Files
Use these files to implement the feature:

### Frontend Files
- **`app/client/src/components/sidebar/ChatSidebar.tsx`** - Main sidebar component that displays the conversation list. This is where we'll add the delete button UI to each conversation item.

- **`app/client/src/components/chat/ConversationManagement.tsx`** - Hook that manages conversation state and operations. We'll add the delete conversation logic here.

- **`app/client/src/lib/api.ts`** - API client functions for backend communication. We'll add a `deleteConversation` function to handle the API call.

- **`app/client/src/pages/Chat.tsx`** - Main chat page component that uses the ConversationManagement hook. May need minor updates to handle deletion state.

### Backend Files
- **`app/server/agent_api.py`** - FastAPI backend with API endpoints. We'll add a new `DELETE /api/conversations/{session_id}` endpoint.

- **`app/server/db_utils.py`** - Database utility functions. We'll add a new `archive_conversation` function to handle the database update.

### Database Files
- **`app/server/sql/3-conversations_messages.sql`** - Already has the `is_archived` boolean column, no changes needed
- **`app/server/sql/4-conversations_messages_rls.sql`** - May need to update RLS policies to filter archived conversations

### New Files
None required - all functionality will be added to existing files.

## Implementation Plan

### Phase 1: Foundation
Set up the backend infrastructure to support conversation archiving:
- Add database utility function to archive conversations
- Update conversation fetching to filter out archived conversations
- Add API endpoint for deleting/archiving conversations
- Update RLS policies if needed to exclude archived conversations

### Phase 2: Core Implementation
Implement the frontend deletion functionality:
- Add delete button UI to conversation items in the sidebar
- Implement confirmation dialog before deletion
- Add API client function to call the delete endpoint
- Implement optimistic updates with error rollback

### Phase 3: Integration
Integrate the delete functionality with existing conversation management:
- Update ConversationManagement hook to handle deletion
- Handle edge cases (deleting selected conversation, last conversation, etc.)
- Add proper error handling and user feedback
- Ensure state consistency across the application

## Step by Step Tasks

### 1. Update Database Utility Functions
- Open `app/server/db_utils.py`
- Add `archive_conversation(supabase: Client, session_id: str, user_id: str) -> bool` function
  - Updates the conversation record to set `is_archived = true`
  - Verifies that the user_id matches to prevent unauthorized deletion
  - Returns True on success, raises HTTPException on failure
- Update `fetch_conversation_history` if needed to respect archived status

### 2. Update Backend API Endpoint
- Open `app/server/agent_api.py`
- Import the new `archive_conversation` function from `db_utils`
- Add new DELETE endpoint: `@app.delete("/api/conversations/{session_id}")`
  - Use `verify_token` dependency to authenticate the user
  - Call `archive_conversation(supabase, session_id, user.get("id"))`
  - Return success response or appropriate error
  - Include proper error handling and logging

### 3. Write Backend Tests
- Open or create test file for backend API tests
- Add test for `archive_conversation` database function
  - Test successful archiving
  - Test unauthorized access (wrong user_id)
  - Test non-existent conversation
- Add test for DELETE endpoint
  - Test successful deletion with auth
  - Test unauthorized deletion
  - Test archived conversations don't appear in fetch results

### 4. Update Conversation Fetching to Filter Archived
- Open `app/server/db_utils.py`
- Update any conversation fetching queries to filter `WHERE is_archived = false`
- Ensure archived conversations are excluded from user's conversation list

### 5. Update Frontend API Client
- Open `app/client/src/lib/api.ts`
- Add `deleteConversation(session_id: string, access_token?: string)` function
  - Makes DELETE request to `/api/conversations/{session_id}`
  - Includes Authorization header with access token
  - Handles errors appropriately
  - Returns boolean for success/failure

### 6. Update ConversationManagement Hook
- Open `app/client/src/components/chat/ConversationManagement.tsx`
- Add `handleDeleteConversation(conversationId: string)` function
  - Implements optimistic update (immediately removes from UI)
  - Calls the API to delete the conversation
  - On error, rolls back the optimistic update and shows toast error
  - On success, shows success toast
  - If deleted conversation was selected, calls `handleNewChat()` to reset to new chat state
- Export the new function from the hook

### 7. Add Delete UI to Sidebar
- Open `app/client/src/components/sidebar/ChatSidebar.tsx`
- Import Trash icon from lucide-react: `import { Trash2 } from 'lucide-react'`
- Add delete button to each conversation item in the conversation list
  - Position the trash icon on hover (right side of conversation item)
  - Use proper styling to match the existing UI theme
  - Add confirmation using AlertDialog from shadcn/ui before deletion
  - Pass `onDeleteConversation` prop to ChatSidebar component

### 8. Wire Up Delete Functionality in Chat Page
- Open `app/client/src/pages/Chat.tsx`
- Destructure `handleDeleteConversation` from `useConversationManagement` hook
- Pass `handleDeleteConversation` to ChatLayout component
- Update ChatLayout to pass it to ChatSidebar

### 9. Update ChatLayout Props
- Open `app/client/src/components/chat/ChatLayout.tsx`
- Add `onDeleteConversation` to the component props interface
- Pass the prop down to ChatSidebar component

### 10. Add Delete Confirmation Dialog
- Open `app/client/src/components/sidebar/ChatSidebar.tsx`
- Add state for managing delete confirmation dialog
- Implement AlertDialog component with:
  - Warning message about deleting the conversation
  - Cancel button
  - Confirm delete button (destructive variant)
  - Stores the conversation to delete in component state

### 11. Write Frontend Tests
- Create or update test file for ConversationManagement hook
- Test `handleDeleteConversation` function
  - Test optimistic update
  - Test error rollback
  - Test successful deletion
  - Test deleting selected conversation triggers new chat
- Add tests for ChatSidebar delete button
  - Test delete button appears on hover
  - Test confirmation dialog opens
  - Test cancel works
  - Test confirm triggers deletion

### 12. Handle Edge Cases
- Ensure deleting the currently selected conversation switches to new chat view
- Handle deletion when it's the only/last conversation
- Prevent multiple simultaneous delete operations
- Add loading state during deletion
- Ensure proper keyboard navigation with delete buttons

### 13. Add Visual Feedback
- Add loading spinner or disabled state during deletion
- Show success toast notification after deletion
- Show error toast if deletion fails
- Add smooth animation when removing conversation from list

### 14. Update RLS Policies (if needed)
- Review `app/server/sql/4-conversations_messages_rls.sql`
- Verify that RLS policies properly filter archived conversations
- If needed, update SELECT policies to exclude archived conversations
- Test that users can't access archived conversations through RLS

### 15. Run Validation Commands
- Execute all validation commands listed below to ensure feature works correctly with zero regressions
- Fix any issues that arise
- Verify the feature works end-to-end in the UI

## Testing Strategy

### Unit Tests

#### Backend Tests
- `test_archive_conversation()` - Verify conversation is marked as archived
- `test_archive_conversation_unauthorized()` - Verify user can't archive others' conversations
- `test_archive_conversation_not_found()` - Verify proper error for non-existent conversation
- `test_fetch_conversations_excludes_archived()` - Verify archived conversations don't appear
- `test_delete_endpoint_auth()` - Verify endpoint requires authentication
- `test_delete_endpoint_success()` - Verify successful deletion response

#### Frontend Tests
- `test_handleDeleteConversation_optimistic_update()` - Verify UI updates immediately
- `test_handleDeleteConversation_error_rollback()` - Verify rollback on API error
- `test_handleDeleteConversation_selected_conversation()` - Verify switching to new chat
- `test_delete_button_renders()` - Verify delete button appears in sidebar
- `test_confirmation_dialog()` - Verify confirmation before delete
- `test_delete_api_call()` - Verify correct API endpoint is called

### Integration Tests

#### End-to-End Tests
- Create a conversation, verify it appears in sidebar
- Delete the conversation, verify it disappears from sidebar
- Verify archived conversation can't be accessed by session_id
- Verify deleting selected conversation switches to new chat
- Test with multiple conversations, delete one, verify others remain
- Test error handling when backend is unavailable
- Test with slow network (verify optimistic update works)

### Edge Cases
- Deleting the currently selected/active conversation
- Deleting when only one conversation exists
- Attempting to delete the same conversation twice
- Network failure during deletion (verify rollback)
- Rapid successive delete operations
- Deleting conversation while a message is being sent
- User lacks permission to delete (different user_id)
- Conversation doesn't exist in database
- Database connection failure during deletion
- RLS policy preventing deletion
- Very long conversation titles with delete button
- Mobile/responsive view with delete buttons
- Keyboard navigation with delete functionality

## Acceptance Criteria
1. **Delete Button Visible**: Each conversation in the sidebar displays a delete (trash) icon on hover or on mobile
2. **Confirmation Required**: Clicking delete shows a confirmation dialog before actually deleting
3. **Immediate UI Update**: After confirming deletion, the conversation immediately disappears from the sidebar (optimistic update)
4. **Backend Synchronization**: The conversation is marked as archived in the database via API call
5. **Error Handling**: If deletion fails, the conversation reappears in the sidebar with an error message
6. **Selected Conversation**: If the deleted conversation was currently selected, the UI switches to a new chat state
7. **Authorization**: Users can only delete their own conversations (enforced by backend)
8. **RLS Compliance**: Archived conversations are filtered out by RLS policies and don't appear in queries
9. **No Data Loss**: Conversations are soft-deleted (archived) not permanently deleted from database
10. **Success Feedback**: User receives success toast notification when deletion completes
11. **Multiple Deletions**: Users can delete multiple conversations sequentially without issues
12. **Responsive Design**: Delete functionality works on mobile, tablet, and desktop views
13. **Accessibility**: Delete button is keyboard accessible and screen-reader friendly
14. **No Regressions**: All existing chat functionality continues to work after implementation

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

### Backend Validation
- `cd app/server && uv run pytest` - Run all server tests including new delete conversation tests
- `cd app/server && uv run pytest -v tests/test_db_utils.py::test_archive_conversation` - Run specific archive test
- `cd app/server && uv run pytest -v tests/test_api.py::test_delete_conversation_endpoint` - Run delete endpoint test

### Frontend Validation
- `cd app/client && npm run lint` - Ensure no TypeScript or linting errors
- `cd app/client && npm run build` - Verify production build succeeds
- `cd app/client && npm test` - Run frontend unit tests (if configured)

### Integration Testing
- `./scripts/start.sh` - Start both backend and frontend
- Manually test the following scenarios in browser:
  1. Create a new conversation by sending a message
  2. Verify conversation appears in sidebar
  3. Hover over conversation and verify delete button appears
  4. Click delete button and verify confirmation dialog opens
  5. Click cancel and verify dialog closes without deleting
  6. Click delete button again and confirm deletion
  7. Verify conversation disappears from sidebar immediately
  8. Verify success toast appears
  9. Create another conversation
  10. Select the first conversation from sidebar
  11. Delete it and verify UI switches to new chat state
  12. Refresh the page and verify deleted conversation doesn't reappear
  13. Test on mobile viewport (< 768px width)
  14. Test keyboard navigation (Tab to delete button, Enter to activate)

### Database Validation
- Connect to Supabase database and run:
  ```sql
  SELECT session_id, title, is_archived, created_at FROM conversations WHERE is_archived = true;
  ```
- Verify deleted conversations are marked as archived (is_archived = true)
- Verify they are not returned in normal conversation queries

### API Validation
- Test DELETE endpoint with curl:
  ```bash
  curl -X DELETE http://localhost:8001/api/conversations/{session_id} \
    -H "Authorization: Bearer {your_token}"
  ```
- Verify 200 response for successful deletion
- Verify 401 for missing/invalid token
- Verify 404 for non-existent conversation

## Notes

### Future Enhancements
- **Restore Functionality**: Add ability to view and restore archived conversations
- **Bulk Delete**: Allow selecting multiple conversations for deletion at once
- **Permanent Delete**: Add option to permanently delete archived conversations after X days
- **Archive View**: Add separate view to see all archived conversations
- **Keyboard Shortcuts**: Add keyboard shortcut (e.g., Delete key) to delete selected conversation
- **Undo Delete**: Implement temporary undo feature with toast action button

### Technical Considerations
- **Soft Delete vs Hard Delete**: We're using soft delete (archiving) to prevent accidental data loss and enable future restore functionality
- **RLS Policies**: Ensure Row Level Security policies properly filter archived conversations to maintain security
- **Optimistic Updates**: UI updates immediately before API response for better UX, with rollback on error
- **State Management**: Need to carefully manage conversation state when deleting the currently selected conversation
- **Performance**: With many conversations, ensure delete operation doesn't cause UI lag (already optimized with optimistic updates)

### Security Notes
- Backend must verify user_id matches the conversation owner before allowing deletion
- Use Supabase RLS policies as additional security layer
- Never trust client-side validation alone
- Ensure archived conversations can't be accessed through any API endpoint

### UI/UX Notes
- Delete button should be subtle (only show on hover) to avoid cluttering the UI
- Confirmation dialog prevents accidental deletions
- Toast notifications provide clear feedback
- Switching to new chat when deleting selected conversation prevents confusion
- Animation on removal makes the action feel smooth and intentional

### Database Notes
- The `is_archived` column already exists in the schema, no migration needed
- Foreign key constraints ensure messages aren't orphaned
- Indexes already exist on user_id and session_id for performant queries
