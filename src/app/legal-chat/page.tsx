'use client';

import { useState } from 'react';
import { useAzureOpenAI } from '@/hooks/useAzureOpenAI';

export default function LegalChat() {
  const [query, setQuery] = useState('');
  const {
    response,
    error,
    loading,
    conversationContext,
    sendQuery,
    clearContext
  } = useAzureOpenAI({
    jurisdiction: 'India',
    language: 'en'
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    await sendQuery(query);
    setQuery('');
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">Legal Assistant</h1>

      {/* Chat History */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6 min-h-[400px] max-h-[600px] overflow-y-auto">
        {conversationContext.messages.map((message, index) => (
          <div
            key={index}
            className={`mb-4 ${
              message.role === 'user' ? 'text-right' : 'text-left'
            }`}
          >
            <div
              className={`inline-block p-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-gray-500">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-500 border-t-transparent" />
            Thinking...
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-100 text-red-700 rounded-lg mb-4">
            {error}
          </div>
        )}

        {response && (
          <div className="mt-4 space-y-4">
            {/* Confidence Score */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Confidence:</span>
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${response.confidence * 100}%` }}
                />
              </div>
              <span className="text-sm text-gray-500">
                {Math.round(response.confidence * 100)}%
              </span>
            </div>

            {/* Follow-up Questions */}
            {response.followUpQuestions && response.followUpQuestions.length > 0 && (
              <div className="mt-4">
                <h3 className="font-medium mb-2">Follow-up Questions:</h3>
                <div className="space-y-2">
                  {response.followUpQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setQuery(question);
                        sendQuery(question);
                      }}
                      className="block w-full text-left p-2 hover:bg-gray-100 rounded-lg text-sm text-blue-600"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Legal Disclaimer */}
            {response.legalDisclaimer && (
              <div className="mt-4 p-3 bg-yellow-50 text-yellow-800 rounded-lg text-sm">
                {response.legalDisclaimer}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask your legal question..."
          className="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50"
        >
          Send
        </button>
        <button
          type="button"
          onClick={clearContext}
          className="px-4 py-3 bg-gray-100 text-gray-600 rounded-lg font-medium hover:bg-gray-200"
        >
          Clear
        </button>
      </form>
    </div>
  );
} 