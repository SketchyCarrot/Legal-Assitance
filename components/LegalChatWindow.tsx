'use client';

import { useState, useRef, useEffect } from 'react';
import { Message } from '@/types/chat';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function LegalChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: '### Welcome to Legal Saathi! 👋\n\nI am your AI legal assistant, specialized in Indian law. How can I assist you today?\n\n**I can help you with:**\n\n* Legal advice and guidance\n* Understanding your rights\n* Document assistance\n* Legal procedures\n* Citations from Indian law'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isMinimized, setIsMinimized] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...messages, userMessage] }),
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.message }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`fixed bottom-0 right-0 md:right-8 transition-all duration-300 ease-in-out ${isMinimized ? 'h-16' : 'h-[600px]'} w-full md:w-[400px] bg-white rounded-t-2xl shadow-2xl flex flex-col overflow-hidden border border-gray-200`}>
      {/* Header */}
      <div 
        className="bg-gradient-to-r from-blue-600 to-blue-700 p-4 flex justify-between items-center cursor-pointer"
        onClick={() => setIsMinimized(!isMinimized)}
      >
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-full flex items-center justify-center">
            <span className="text-2xl">⚖️</span>
          </div>
          <div>
            <h3 className="text-white font-semibold">Legal Saathi</h3>
            <p className="text-blue-100 text-sm">AI Legal Assistant</p>
          </div>
        </div>
        <button className="text-white hover:text-blue-200 transition-colors">
          <svg 
            className={`w-6 h-6 transform transition-transform ${isMinimized ? 'rotate-180' : ''}`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {/* Chat Content - Only show when not minimized */}
      <div className={`flex-1 flex flex-col ${isMinimized ? 'hidden' : ''}`}>
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} items-start`}
            >
              {message.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-600 to-blue-700 flex items-center justify-center mr-2 flex-shrink-0 shadow-md">
                  <span className="text-white text-sm">⚖️</span>
                </div>
              )}
              <div
                className={`max-w-[85%] p-4 rounded-2xl shadow-sm ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white ml-4'
                    : 'bg-white text-gray-800'
                }`}
              >
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                      ul: ({node, ...props}) => <ul className="list-disc ml-4 mb-2" {...props} />,
                      ol: ({node, ...props}) => <ol className="list-decimal ml-4 mb-2" {...props} />,
                      li: ({node, ...props}) => <li className="mb-1" {...props} />,
                      h1: ({node, ...props}) => <h1 className="text-lg font-bold mb-2" {...props} />,
                      h2: ({node, ...props}) => <h2 className="text-base font-bold mb-2" {...props} />,
                      h3: ({node, ...props}) => <h3 className="text-sm font-bold mb-2" {...props} />,
                      a: ({node, ...props}) => (
                        <a 
                          className={`${message.role === 'user' ? 'text-white underline' : 'text-blue-600 hover:text-blue-800'}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          {...props}
                        />
                      ),
                      code: ({node, inline, ...props}) => (
                        inline 
                          ? <code className={`px-1 py-0.5 rounded text-sm ${message.role === 'user' ? 'bg-blue-500' : 'bg-gray-200'}`} {...props} />
                          : <code className="block bg-gray-800 text-white p-2 rounded my-2 overflow-x-auto" {...props} />
                      ),
                      blockquote: ({node, ...props}) => (
                        <blockquote 
                          className={`border-l-4 pl-4 italic my-2 ${
                            message.role === 'user' 
                              ? 'border-white/30' 
                              : 'border-blue-200'
                          }`}
                          {...props}
                        />
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              </div>
              {message.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-600 to-blue-700 flex items-center justify-center ml-2 flex-shrink-0 shadow-md">
                  <span className="text-white text-sm">👤</span>
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start items-start">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-600 to-blue-700 flex items-center justify-center mr-2 flex-shrink-0 shadow-md">
                <span className="text-white text-sm">⚖️</span>
              </div>
              <div className="bg-white p-4 rounded-2xl shadow-sm">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 bg-white border-t border-gray-100">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your legal question..."
              className="flex-1 p-3 rounded-xl border border-gray-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 bg-gray-50 text-sm"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-3 rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
} 