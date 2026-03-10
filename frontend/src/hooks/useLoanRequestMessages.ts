import { useState, useCallback, useEffect } from 'react';
import { loansApi } from '@/api/loans';
import type { MessageThread } from '@/types';

interface UseLoanRequestMessagesReturn {
  thread: MessageThread | null;
  isLoading: boolean;
  error: string | null;
  fetchMessages: () => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  refreshMessages: () => Promise<void>;
}

export function useLoanRequestMessages(
  requestId: string | null
): UseLoanRequestMessagesReturn {
  const [thread, setThread] = useState<MessageThread | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMessages = useCallback(async () => {
    if (!requestId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await loansApi.getMessages(requestId);
      if (response.success && response.data) {
        setThread(response.data);
      } else {
        setError(response.message || 'Nie udało się pobrać wiadomości');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd ładowania wiadomości');
    } finally {
      setIsLoading(false);
    }
  }, [requestId]);

  const sendMessage = useCallback(async (content: string) => {
    if (!requestId || !content.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await loansApi.sendMessage(requestId, content.trim());
      if (response.success && response.data) {
        // Refresh thread to show new message
        await fetchMessages();
      } else {
        setError(response.message || 'Nie udało się wysłać wiadomości');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd wysyłania wiadomości');
    } finally {
      setIsLoading(false);
    }
  }, [requestId, fetchMessages]);

  const refreshMessages = useCallback(async () => {
    await fetchMessages();
  }, [fetchMessages]);

  // Auto-fetch when requestId changes
  useEffect(() => {
    if (requestId) {
      fetchMessages();
    } else {
      setThread(null);
    }
  }, [requestId, fetchMessages]);

  return {
    thread,
    isLoading,
    error,
    fetchMessages,
    sendMessage,
    refreshMessages
  };
}
