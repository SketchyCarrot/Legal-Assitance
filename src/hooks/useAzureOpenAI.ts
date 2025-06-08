import { useState, useCallback } from 'react';
import type { ConversationContext, LegalResponse, LegalQueryRequest } from '@/types/azure';

interface UseAzureOpenAIProps {
  initialContext?: ConversationContext;
  jurisdiction?: string;
  language?: string;
}

interface UseAzureOpenAIReturn {
  response: LegalResponse | null;
  error: string | null;
  loading: boolean;
  conversationContext: ConversationContext;
  sendQuery: (query: string) => Promise<void>;
  clearContext: () => void;
}

export function useAzureOpenAI({
  initialContext,
  jurisdiction,
  language = 'en'
}: UseAzureOpenAIProps = {}): UseAzureOpenAIReturn {
  const [response, setResponse] = useState<LegalResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [conversationContext, setConversationContext] = useState<ConversationContext>(
    initialContext || {
      messages: [],
      metadata: {
        jurisdiction,
        language
      }
    }
  );

  const sendQuery = useCallback(async (query: string) => {
    try {
      setLoading(true);
      setError(null);

      const request: LegalQueryRequest = {
        query,
        context: conversationContext,
        jurisdiction,
        language
      };

      const response = await fetch('/api/azure-openai', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': process.env.NEXT_PUBLIC_API_KEY || ''
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: LegalResponse = await response.json();
      setResponse(data);

      // Update conversation context
      setConversationContext(prev => ({
        ...prev,
        messages: [
          ...prev.messages,
          { role: 'user', content: query },
          { role: 'assistant', content: data.content }
        ]
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error in useAzureOpenAI:', err);
    } finally {
      setLoading(false);
    }
  }, [conversationContext, jurisdiction, language]);

  const clearContext = useCallback(() => {
    setConversationContext({
      messages: [],
      metadata: {
        jurisdiction,
        language
      }
    });
    setResponse(null);
    setError(null);
  }, [jurisdiction, language]);

  return {
    response,
    error,
    loading,
    conversationContext,
    sendQuery,
    clearContext
  };
} 