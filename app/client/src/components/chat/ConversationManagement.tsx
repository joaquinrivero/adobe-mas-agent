
import { useState, useEffect, useCallback } from 'react';
import { fetchConversations } from '@/lib/api';
import { Conversation } from '@/types/database.types';
import { useToast } from '@/hooks/use-toast';

interface ConversationManagementProps {
  user: any;
  isMounted: React.MutableRefObject<boolean>;
}

export const useConversationManagement = ({
  user,
  isMounted
}: ConversationManagementProps) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const { toast } = useToast();
  
  // Fetch user's conversations
  const loadConversations = useCallback(async () => {
    if (!user) return [];
    
    try {
      const data = await fetchConversations(user.id);
      if (isMounted.current) {
        setConversations(data);
      }
      return data;
    } catch (err) {
      // Extract detailed error information
      const isSupabaseError = err && typeof err === 'object' && 'code' in err;
      const errorObj = err as Record<string, unknown>;

      // Build comprehensive error details for logging
      const errorDetails = {
        error: err,
        message: err instanceof Error ? err.message : 'Unknown error',
        stack: err instanceof Error ? err.stack : undefined,
        userId: user?.id,
        timestamp: new Date().toISOString(),
        errorType: err?.constructor?.name,
        // Supabase-specific error details
        ...(isSupabaseError && {
          supabaseCode: errorObj.code,
          supabaseDetails: errorObj.details,
          supabaseHint: errorObj.hint,
          supabaseMessage: errorObj.message,
        }),
      };

      // Detailed error logging to stdout
      console.error('❌ Error loading conversations:', errorDetails);

      // Log to stdout for debugging
      console.log('STDOUT ERROR:', JSON.stringify(errorDetails, null, 2));

      // Extract user-friendly error message
      let errorMessage = 'Unknown error occurred';
      if (isSupabaseError && errorObj.message) {
        errorMessage = String(errorObj.message);
      } else if (err instanceof Error && err.message) {
        errorMessage = err.message;
      }

      // Add hint if available
      if (isSupabaseError && errorObj.hint) {
        errorMessage += ` (Hint: ${String(errorObj.hint)})`;
      }

      if (isMounted.current) {
        toast({
          title: 'Error loading conversations',
          description: isSupabaseError
            ? `Database error: ${errorMessage}`
            : `Could not load your conversations: ${errorMessage}`,
          variant: 'destructive',
        });
      }
      return [];
    }
  }, [user, toast, isMounted]);

  const handleNewChat = () => {
    setSelectedConversation(null);
  };

  const handleSelectConversation = (conversation: Conversation) => {
    setSelectedConversation(conversation);
  };

  // Initial load of conversations
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  return {
    conversations,
    selectedConversation,
    setSelectedConversation,
    setConversations,
    loadConversations,
    handleNewChat,
    handleSelectConversation
  };
};
