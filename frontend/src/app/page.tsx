import React from 'react';
import ChatInterface from '../components/ChatInterface';
import useChatStore from '../store/chatStore';

export default function Home() {
  const {
    messages,
    isRecording,
    addMessage,
    setIsRecording,
    setIsLoading,
    setError,
  } = useChatStore();

  const handleSendMessage = async (content: string) => {
    try {
      setIsLoading(true);
      setError(null);

      // Add user message
      const userMessage = {
        content,
        sender: 'user',
        timestamp: new Date().toISOString(),
      };
      addMessage(userMessage);

      // Make API call to get assistant's response
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          conversation_history: messages.map((m) => m.content),
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage = {
        content: data.response,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
      };
      addMessage(assistantMessage);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartRecording = () => {
    setIsRecording(true);
    // Implement voice recording logic
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    // Implement voice recording stop logic
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <ChatInterface
        onSendMessage={handleSendMessage}
        onStartRecording={handleStartRecording}
        onStopRecording={handleStopRecording}
        messages={messages}
        isRecording={isRecording}
      />
    </main>
  );
} 