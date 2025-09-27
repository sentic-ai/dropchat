import { useState, useCallback, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { type Message } from "@langchain/langgraph-sdk";

// Use LangGraph's Message type directly for compatibility

interface ChatResponse {
  answer: string;
  sources: string[];
  processing_steps: string[];
  error?: string;
}

interface ProjectInfo {
  project_id: string;
  project_name: string;
  description?: string;
  document_count: number;
  total_chunks: number;
  created_at: string;
  document_names: string[];
}

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  documentName: string | null;
  sendMessage: (message: string) => Promise<void>;
}

export function useCustomChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [documentName, setDocumentName] = useState<string | null>(null);
  const pathname = usePathname();

  // Extract user_hash and project_id from URL path
  const getChatParams = useCallback(() => {
    const pathParts = pathname.split('/');
    if (pathParts.length >= 4 && pathParts[1] === 'chat') {
      return {
        user_hash: pathParts[2],
        project_id: pathParts[3],
      };
    }
    return null;
  }, [pathname]);

  // Fetch project info and document name on component load
  useEffect(() => {
    const loadProjectInfo = async () => {
      const chatParams = getChatParams();
      if (!chatParams) return;

      try {
        const response = await fetch(`/api/projects/${chatParams.user_hash}/${chatParams.project_id}`);
        if (response.ok) {
          const projectInfo: ProjectInfo = await response.json();
          if (projectInfo.document_names && projectInfo.document_names.length > 0) {
            setDocumentName(projectInfo.document_names[0]); // Take first document
          }
        }
      } catch (error) {
        console.error('Failed to load project info:', error);
        // Don't set an error - this is non-critical for chat functionality
      }
    };

    loadProjectInfo();
  }, [getChatParams]);

  const sendMessage = useCallback(async (messageText: string) => {
    const chatParams = getChatParams();
    if (!chatParams) {
      setError('Invalid chat URL format');
      return;
    }

    setIsLoading(true);
    setError(null);

    // Add human message immediately (LangGraph format)
    const humanMessage: Message = {
      id: `human-${Date.now()}`,
      type: 'human',
      content: [{ type: 'text', text: messageText }],
    };

    setMessages(prev => [...prev, humanMessage]);

    try {
      // Call the backend /chat endpoint
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_hash: chatParams.user_hash,
          project_id: chatParams.project_id,
          query: messageText,
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat request failed: ${response.statusText}`);
      }

      const data: ChatResponse = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Extract document name from sources (first time only)
      if (!documentName && data.sources && data.sources.length > 0) {
        setDocumentName(data.sources[0]);
      }

      // Add AI response (LangGraph format)
      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        type: 'ai',
        content: [{ type: 'text', text: data.answer }],
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [getChatParams]);

  return {
    messages,
    isLoading,
    error,
    documentName,
    sendMessage,
  };
}